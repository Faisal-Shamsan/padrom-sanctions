# ADR 0001: Record Architecture Decisions

**Date:** 2026-05-13
**Status:** Accepted

## Context

During this PoC internship we will make decisions about technology choices,
fuzzy-matching thresholds, data models, and external integrations. These
decisions should be recorded so that future contributors understand *why* a
choice was made, not just *what* was chosen.

Without this practice, thresholds and design choices drift silently and become
impossible to audit — a particular risk for a sanctions-screening system where
wrong matches have compliance implications.

## Decision

We will use Architecture Decision Records (ADRs) stored in `docs/adr/` for any
decision that:

- Affects fuzzy-matching thresholds or matching algorithms
- Introduces a new external dependency or integration
- Changes the database schema in a non-trivial way (beyond CRUD columns)
- Alters the API contract between the UI and the API service
- Deviates from the "no Kubernetes / no Redis / no Kafka" PoC constraints

ADRs are numbered sequentially (`NNNN-short-title.md`) and use the format:
**Context → Decision → Consequences**.

## Consequences

- Any PR that changes matching thresholds without a corresponding ADR will be
  blocked at review.
- ADRs are immutable once accepted. To reverse a decision, write a new ADR that
  supersedes the previous one and link them.
- This adds a small writing overhead but prevents silent drift in parameters that
  have compliance implications.
