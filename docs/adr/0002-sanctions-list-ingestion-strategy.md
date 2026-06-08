# ADR 0002 — Sanctions List Ingestion Strategy

**Date:** 2026-06-01
**Status:** Accepted

---

## Context

Phase 1 of the PADROM Sanctions Screening PoC requires a populated `sanction_entry` table
before any screening can take place. We need to decide how to:

1. Obtain the sanctions data (sources and transport)
2. Parse the XML payloads (library choice)
3. Persist the data (schema design and refresh strategy)
4. Trigger refreshes (scheduling vs. operator-driven)
5. Introduce the HTTP client as a production dependency

---

## Decision

### Sources

We use two official, freely-available XML feeds:

| List | URL |
|------|-----|
| EU Consolidated Sanctions List | `https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNy0wMS0wMQ==` |
| UN Security Council Consolidated List (SCSL) | `https://scsanctions.un.org/resources/xml/en/consolidated.xml` |

Both are public endpoints updated by their respective bodies. No API keys required.

### Parsing

We use Python's stdlib `xml.etree.ElementTree` exclusively. No third-party XML library
(lxml, BeautifulSoup, xmltodict) is introduced. The feed schemas are stable, the elements
we need are shallow, and `ElementTree` is sufficient for the task.

### Async HTTP fetch

`httpx.AsyncClient` with a 60-second timeout is used for downloads. `httpx` is already
present in dev dependencies for testing; this ADR records its promotion to a **production
dependency** (`[project] dependencies` in `pyproject.toml`).

### Schema — `sanction_entry` table

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | `gen_random_uuid()` server default |
| `source_list` | VARCHAR(10) | `"EU"` or `"UN"`; btree index (delete predicate) |
| `external_id` | VARCHAR(100) | `logicalId` (EU) / `DATAID` (UN) |
| `entity_type` | VARCHAR(20) | `"PERSON"` or `"ENTITY"` |
| `primary_name` | TEXT | Canonical match name; btree index (Phase 2 readiness) |
| `aliases` | ARRAY(TEXT) | GIN-indexed; all non-primary name variants |
| `raw_xml` | TEXT | Serialised source XML fragment for audit trail |
| `synced_at` | TIMESTAMPTZ | `func.now()` server default |

A `UniqueConstraint("source_list", "external_id")` prevents duplicate entries per source.

### Refresh strategy

**Full replace per list**: on each sync, all rows for a given `source_list` are deleted,
then the freshly parsed entries are bulk-inserted. Both lists are processed sequentially
(EU then UN) inside a single database transaction, committed once after both succeed.
This guarantees atomicity: a partial download failure leaves the existing data intact.

Rationale for full replace over upsert: the lists are O(thousands) of rows, the feeds
provide no incremental diff, and a full replace is simpler to audit. Performance is
acceptable for a PoC.

### Trigger mechanism

Refreshes are operator-driven via `POST /v1/ingest/sync`. No background scheduler,
cron job, or message queue is introduced. This is consistent with the PoC constraint
of avoiding Kafka, Redis, and unnecessary infrastructure.

---

## Consequences

**Positive:**
- No new XML library dependency
- Single production dependency addition (`httpx`)
- Simple, auditable refresh logic
- GIN index on `aliases` prepares the schema for Phase 2 fuzzy matching without schema changes

**Negative / accepted trade-offs:**
- Sequential full-replace means a brief window where the table has zero rows for a list
  if the operator calls sync during a live screening request (acceptable for PoC)
- No incremental/delta sync; large list downloads on every refresh (acceptable for PoC scale)
- Manual operator trigger means lists can go stale if not refreshed regularly

---

## Alternatives considered

| Alternative | Rejected because |
|-------------|-----------------|
| lxml for parsing | Additional dependency; stdlib ET is sufficient |
| `aiohttp` instead of `httpx` | `httpx` already in the project |
| Upsert (INSERT ON CONFLICT UPDATE) | More complex, unclear benefit at PoC scale |
| Background task (APScheduler / Celery) | Adds infrastructure complexity outside PoC scope |
| Storing only parsed fields (no `raw_xml`) | Loses audit trail; EU XML has rich penalty detail |
