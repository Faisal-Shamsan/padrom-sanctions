# ADR 0003 — Screening Matching Strategy

**Status:** Accepted
**Date:** 2026-06-11
**Authors:** PADROM Engineering

---

## Context

Phase 3 introduces the core screening capability: given a counterparty name, determine
whether it appears on the EU Consolidated Sanctions List or the UN Security Council
Consolidated List (both ingested in Phase 2).

The matching problem has two competing forces:

- **Recall** — avoid missing a sanctioned name that appears in a slightly different form
  (transliteration variants, legal suffixes, abbreviated first names).
- **Precision** — avoid flooding human reviewers with false positives.

We also have a performance constraint: the `sanction_entry` table can hold tens of thousands
of rows. Loading the entire table into Python memory on every request is feasible at PoC
scale but wasteful; a pre-filter step keeps the Python-side comparison set small.

---

## Decision

### Two-stage retrieval

**Stage A — PostgreSQL trigram pre-filter (wide net, cheap)**

Use the `pg_trgm` extension's `similarity()` function against `primary_name` with a
threshold of `0.3`. A GIN trigram index on `primary_name` makes this an index scan.

```sql
SELECT * FROM sanction_entry
WHERE similarity(primary_name, :q) > 0.3
```

Threshold `0.3` is intentionally permissive to avoid false negatives at this stage —
precision is handled in Stage B.

Aliases are **not** checked at the SQL level. The aliases column is a `TEXT[]` array;
applying `similarity()` across each array element would require `unnest()` with lateral
joins, adding query complexity and defeating the simplicity goal. The GIN index on aliases
(added in Phase 2) is used by `@>` (containment) queries, not `similarity()`. Because
Stage B performs in-memory alias comparison, any candidate whose alias matches the query
will be returned from the Python pass even if its primary name scored below 0.3. The
trade-off is acceptable: if a sanctioned entity's primary name is entirely dissimilar to
the query but an alias matches, Stage A may miss it. At PoC scale the full list is small
enough that a secondary alias-based SQL pass could be added if this gap is measured in
production.

**Stage B — Python composite scoring (strict)**

For each candidate returned by Stage A, compute:

```
jaro  = JaroWinkler.similarity(query, candidate_name)   # 0–1
tsort = token_sort_ratio(query, candidate_name) / 100   # 0–1
composite = (jaro + tsort) / 2
```

Applied over `primary_name` and every element of `aliases`. The maximum composite score
across all names is the entry's score.

Entries with `max_score < threshold` (default `0.85`, configurable via
`settings.screening_threshold`) are discarded.

The single highest-scoring surviving entry is returned.

### RapidFuzz function selection

| Function | Rationale |
|---|---|
| `JaroWinkler.similarity` | Excellent at detecting prefix-matching transliteration variants and short name transpositions. High weight on common prefixes matches how surnames are romanised. |
| `fuzz.token_sort_ratio` | Normalises token order, handling "Ali Hassan Mohammed" vs "Mohammed Ali Hassan". Catches reordered multi-token names common in Arabic/Persian transliterations. |

Pure Levenshtein (`fuzz.ratio`) was considered but penalises long names with small edits
relative to total length; `token_sort_ratio` handles word-order variance more robustly.
`token_set_ratio` was also considered but is more permissive with substring inclusion,
raising false-positive risk.

### Composite formula

Simple arithmetic mean. This keeps the formula transparent (auditable, explainable to
regulators) and avoids the complexity of calibrating weights. Both components are bounded
[0, 1], so the composite is also [0, 1].

### Threshold: 0.85

`0.85` is set based on RapidFuzz documentation guidance for AML-adjacent use cases and
informal manual testing against common transliteration variants. It sits above the typical
"very similar" range for random name pairs (typically < 0.7) while allowing one or two
character differences in long names.

**This threshold MUST NOT be changed without a new ADR** (per CLAUDE.md rules). The value
is surfaced as `settings.screening_threshold` so it can be adjusted per deployment without
a code change, but any change must be documented.

### Result mapping

- `matched_entry is not None` → `POTENTIAL_MATCH`
- `matched_entry is None` → `NO_MATCH`

There is no `CONFIRMED_MATCH` tier. Even an exact-string hit (score = 1.0) produces
`POTENTIAL_MATCH` because:

1. False positives exist (common names, data entry errors in the sanctions list).
2. The PoC mandates human review of all potential matches before action is taken.
3. Automated confirmation without human oversight could create legal/compliance risk.

This can be revisited in a production phase once a review workflow is established.

---

## Alternatives considered

### Pure in-memory scan (no SQL pre-filter)

Load all `SanctionEntry` rows into Python on each request, score all of them.

**Rejected:** At PoC scale (~40 000 EU + ~1 000 UN entries) this is ~100 ms per request
with no caching, and the memory footprint grows with the list. The two-stage approach
keeps Stage B input under ~200 rows in typical queries.

### Pure SQL trigram scoring (no Python pass)

Use `similarity()` directly as the score and cut at 0.85 in SQL.

**Rejected:** `similarity()` only compares full strings; it cannot check aliases in an
array column without complex lateral joins. It also does not support token-order
normalisation (`token_sort_ratio` behaviour), so word-reordered names would score poorly.

### Elasticsearch / OpenSearch vector search

Pre-index names as dense vectors; use approximate nearest-neighbour search.

**Rejected:** Violates the PoC constraint (no Elasticsearch — see CLAUDE.md). Would
introduce an additional stateful service, complicating Docker Compose setup and operational
burden. Can be revisited if query volume or list size grows significantly.

### Levenshtein distance only

Use `fuzz.ratio` (Levenshtein-based) as the sole metric.

**Rejected:** Levenshtein penalises long names with small character edits too leniently
relative to length, and does not handle token-order differences (e.g. "HUSSEIN SADDAM"
vs "SADDAM HUSSEIN").

---

## Consequences

- `pg_trgm` extension must be enabled in every environment (migration adds it).
- A GIN trigram index on `sanction_entry.primary_name` is added in the same migration.
- `settings.screening_threshold` (default `0.85`) must be documented in `.env.example`.
- Alias matching happens in Python (Stage B), not SQL (Stage A). This means an entry
  whose primary name is very dissimilar to the query but has a matching alias may be missed
  by the SQL pre-filter. Acceptable at PoC scale; revisit for production.
- All screening decisions are persisted in `screening_log` for the audit trail.
