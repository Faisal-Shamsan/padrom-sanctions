# PADROM Sanctions Screening

> **PoC notice** — This is a proof-of-concept built during a 3-month internship.
> It is **not** a production-grade AML system and must not be used as one.

Screens insurance counterparties against the **EU Consolidated Sanctions List** and
the **UN Security Council Consolidated List**. Built for PADROM, Romania's natural
disaster insurance pool.

## Quick start

```bash
# 1. Copy environment files
cp api/.env.example api/.env && cp ui/.env.example ui/.env.local

# 2. Start all services (db + api + ui) with hot reload
docker compose -f compose/docker-compose.yml -f compose/docker-compose.override.yml up

# 3. Open http://localhost:3000
```

API interactive docs: http://localhost:8000/docs

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Development guide](docs/DEVELOPMENT.md)
- [Architecture Decision Records](docs/adr/)

## Project layout

```
api/      FastAPI backend + PostgreSQL
ui/       Next.js 15 frontend
compose/  Docker Compose configs
docs/     Architecture docs and ADRs
```
