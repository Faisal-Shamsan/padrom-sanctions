# PADROM Sanctions Screening — Project Context

## Overview
Proof-of-concept microservice that screens insurance counterparties (policyholders,
claimants, brokers, suppliers, reinsurance partners) against the EU Consolidated
Sanctions List and the UN Security Council Consolidated List. Built for PADROM,
Romania's natural disaster insurance pool. **This is a PoC — not a production AML system.**

## Monorepo layout
```
padrom-sanctions/
├── api/          # FastAPI + PostgreSQL backend (Python 3.12, uv)
├── ui/           # Next.js 15 frontend (TypeScript, pnpm)
├── compose/      # Docker Compose files
├── docs/         # Architecture docs and ADRs
└── .github/      # CI workflows
```

## Tech stack
| Layer        | Choice                                               |
|--------------|------------------------------------------------------|
| Backend      | Python 3.12, FastAPI, async SQLAlchemy 2.0, asyncpg  |
| Database     | PostgreSQL 16, Alembic (async migrations)            |
| Validation   | Pydantic v2, pydantic-settings                       |
| Matching     | RapidFuzz (fuzzy name matching)                      |
| Frontend     | Next.js 15 (App Router), TypeScript, Tailwind CSS v4 |
| UI kit       | shadcn/ui (New York style, Slate base, CSS vars)     |
| Data fetch   | TanStack Query v5                                    |
| Forms        | React Hook Form + Zod                                |
| Pkg managers | uv (API), pnpm (UI)                                  |
| Containers   | Docker Compose (no Kubernetes — PoC)                 |
| CI           | GitHub Actions                                       |

## Key commands

### API (run from `api/`)
```bash
uv sync                                              # install / sync deps
uv run fastapi dev src/main.py                       # dev server on :8000 with reload
uv run pytest tests/                                 # run tests (needs Docker for testcontainers)
uv run ruff check src tests                          # lint
uv run ruff format src tests                         # format
uv run mypy src                                      # type-check
uv run alembic upgrade head                          # apply migrations
uv run alembic revision --autogenerate -m "msg"      # new migration
```

### UI (run from `ui/`)
```bash
pnpm install      # install dependencies
pnpm dev          # dev server on :3000
pnpm build        # production build
pnpm lint         # ESLint
pnpm typecheck    # tsc --noEmit
```

### Docker (run from repo root)
```bash
# Dev — hot reload on both services
docker compose -f compose/docker-compose.yml -f compose/docker-compose.override.yml up

# Add a shadcn component (from ui/)
pnpm dlx shadcn@latest add button
```

## Code conventions
- **API**: `snake_case`, strict mypy, ruff enforced, `async` everywhere
- **UI**: `camelCase` TS, strict mode, no `any`, Zod for all user-facing validation
- **Models**: Pydantic = `*Request` / `*Response`; SQLAlchemy = plain singular nouns
- **Migrations**: always `--autogenerate`; never edit a migration applied anywhere
- **Env vars**: all config via environment; never hard-code secrets or URLs
- **Error handling**: `HTTPException` with JSON body in API; user-friendly messages in UI

## IMPORTANT rules — do not break without discussion
1. **Never commit `.env` files** — use `.env.example` as the template
2. **Never change fuzzy-matching thresholds** without a new ADR in `docs/adr/`
3. **No business logic in the UI** — the UI calls the API; it never touches the DB
4. **All DB access via async session** — no sync SQLAlchemy calls
5. **PoC scope**: no Kubernetes, Redis, Elasticsearch, or Kafka — keep it simple

## Architecture decisions
See `docs/adr/` for formal records.
Any change to matching, data model, or external integrations requires an ADR first.

## Useful links
- API docs (dev): http://localhost:8000/docs
- UI (dev): http://localhost:3000
- shadcn/ui: https://ui.shadcn.com
- RapidFuzz: https://rapidfuzz.github.io/RapidFuzz/
