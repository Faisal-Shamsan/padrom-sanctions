# Architecture

## System overview

```
Browser ──► Next.js UI   (port 3000)
                │
                │ HTTP / JSON
                ▼
           FastAPI API   (port 8000)
                │
                │ asyncpg
                ▼
          PostgreSQL 16  (port 5432)
```

The UI is a presentation layer only. All business logic lives in the API service.

## Services

### `api` — FastAPI backend
- **Async throughout** — `async def` endpoints, `async with` DB sessions via SQLAlchemy 2.0
- **Pydantic v2** for request/response validation and settings management
- **RapidFuzz** for fuzzy name matching against the loaded sanctions lists
- **Alembic** (async template) for schema migrations
- Port: **8000**

### `ui` — Next.js 15 frontend
- **App Router** — React Server Components where no interactivity is needed
- **TanStack Query v5** for server-state caching and background refetch
- **React Hook Form + Zod** for validated form inputs
- **shadcn/ui** (New York style, Slate base) for accessible UI primitives
- Port: **3000**

### `db` — PostgreSQL 16
- Single database: `padrom`
- Schema managed entirely by Alembic migrations in `api/alembic/`
- Persistent volume in Docker Compose; ephemeral in CI

## Package layout (`api/src/`)

| Package      | Responsibility                                    |
|--------------|---------------------------------------------------|
| `screening/` | POST /v1/screen/entity — core matching logic      |
| `ingestion/` | Fetch + parse EU/UN lists into the DB             |
| `audit/`     | GET /v1/audit/screenings — immutable audit trail  |

## Design decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| ORM      | SQLAlchemy 2.0 async | Native async, mature ecosystem |
| Matching | RapidFuzz | No Elasticsearch needed at PoC scale |
| State    | PostgreSQL only | No Redis, no queue — PoC simplicity |
| Deploy   | Docker Compose | No Kubernetes — appropriate for PoC |
| Frontend | Next.js 15 App Router | Modern, pairs well with shadcn/ui |

See `docs/adr/` for formal Architecture Decision Records.
