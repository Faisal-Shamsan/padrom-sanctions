# Development Guide

## Prerequisites

| Tool | Install |
|------|---------|
| Python 3.12+ | `pyenv install 3.12` or system package |
| uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js 20+ | https://nodejs.org or `nvm install 20` |
| pnpm | `npm i -g pnpm` or `corepack enable pnpm` |
| Docker Desktop | https://docs.docker.com/desktop/ |

## First-time setup

```bash
git clone https://github.com/Faisal-Shamsan/padrom-sanctions.git
cd padrom-sanctions

# API
cd api
cp .env.example .env
uv sync                  # creates .venv and installs all deps

# UI
cd ../ui
cp .env.example .env.local
pnpm install
```

## Running locally (all services via Docker)

```bash
# From repo root — hot reload on both api and ui
docker compose -f compose/docker-compose.yml \
               -f compose/docker-compose.override.yml up
```

Open http://localhost:3000 (UI) and http://localhost:8000/docs (API).

## Running services individually (no Docker)

Start the DB container first:
```bash
docker compose -f compose/docker-compose.yml up db
```

Then in separate terminals:
```bash
# API
cd api && uv run fastapi dev src/main.py   # hot reload on :8000

# UI
cd ui && pnpm dev                          # hot reload on :3000
```

## Running tests

```bash
cd api
uv run pytest tests/ -v
```

Tests use **testcontainers** — Docker must be running. No separate Postgres needed.

## Linting & formatting

```bash
# API
cd api
uv run ruff check src tests      # lint
uv run ruff format src tests     # auto-format
uv run mypy src                  # strict type check

# UI
cd ui
pnpm lint                        # ESLint
pnpm typecheck                   # tsc --noEmit
```

## Database migrations

```bash
cd api

# Apply all pending migrations
uv run alembic upgrade head

# Create a migration after editing SQLAlchemy models
uv run alembic revision --autogenerate -m "add entity table"

# Roll back one step
uv run alembic downgrade -1
```

## Adding a shadcn/ui component

```bash
cd ui
pnpm dlx shadcn@latest add button
```

Components are added to `ui/components/ui/` and can be imported as `@/components/ui/button`.

## Environment variables

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `DATABASE_URL` | api | `postgresql+asyncpg://padrom:padrom@localhost:5432/padrom` | asyncpg DSN |
| `CORS_ORIGINS` | api | `["http://localhost:3000"]` | Allowed origins (JSON list) |
| `DEBUG` | api | `false` | Enable SQLAlchemy query echo |
| `NEXT_PUBLIC_API_URL` | ui | `http://localhost:8000` | API base URL (baked into bundle) |
