Write an Architecture Decision Record for the following change: $ARGUMENTS

## When an ADR is required

An ADR **must** be written (and linked in the PR description) before merging any change that:

1. Alters fuzzy-matching thresholds or the matching algorithm (RapidFuzz scorer, token ratios, cutoff scores)
2. Introduces or removes an external dependency or third-party integration
3. Changes the database schema in a non-trivial way (beyond adding plain CRUD columns)
4. Alters the API contract between the UI and the API service (new fields, renamed fields, status codes)
5. Deviates from the PoC constraints (no Kubernetes, Redis, Elasticsearch, or Kafka)

If none of these apply, no ADR is needed — skip this skill.

## File naming convention

```
docs/adr/NNNN-kebab-title.md
```

- `NNNN` = next sequential number (check `docs/adr/` for the highest existing number and increment)
- Use lowercase kebab-case for the title slug
- Example: `docs/adr/0003-use-token-set-ratio-for-entity-matching.md`

## Required sections and format

```markdown
# ADR NNNN: <Title>

**Date:** YYYY-MM-DD
**Status:** Proposed   ← use Proposed until merged; change to Accepted in the same PR

## Context

<Explain the situation, the problem, and why a decision is needed.
Include the compliance/regulatory stakes for PADROM where relevant.>

## Decision

<State the decision clearly and unambiguously.
Include concrete values (e.g. threshold = 85) where applicable.>

## Consequences

<List the trade-offs, follow-up work, and any risks introduced.
Note any previously accepted ADR that this supersedes, and link it.>
```

## Immutability rule

Once an ADR is merged with **Status: Accepted** it is **never edited**.
To reverse or replace a decision:
1. Write a new ADR with **Status: Proposed**
2. Add a line to the new ADR: `Supersedes: ADR NNNN`
3. Update the old ADR's status line to `Superseded by ADR MMMM` (this one edit is allowed)

## Checklist before opening the PR

- [ ] New file created at `docs/adr/NNNN-<slug>.md`
- [ ] Status set to `Proposed` (will be changed to `Accepted` when merged)
- [ ] ADR number linked in the PR description
- [ ] If superseding an old ADR, old file updated with `Superseded by ADR NNNN`
