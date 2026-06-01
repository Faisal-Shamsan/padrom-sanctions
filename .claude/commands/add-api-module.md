Scaffold a new API feature module for: $ARGUMENTS

## Module layout

Every feature module lives under `api/src/<module_name>/` and contains exactly these four files:

```
api/src/<module_name>/
├── __init__.py      # empty or re-export router
├── router.py        # FastAPI APIRouter — HTTP layer only
├── service.py       # business logic — no FastAPI imports
├── models.py        # SQLAlchemy ORM models
└── schemas.py       # Pydantic request/response schemas
```

## Naming conventions

**Pydantic schemas** (`schemas.py`):
- Request bodies: class name ends in `Request` (e.g. `ScreenEntityRequest`)
- Responses: class name ends in `Response` (e.g. `ScreenEntityResponse`)
- Use `snake_case` field names to match JSON keys

**SQLAlchemy models** (`models.py`):
- Plain singular nouns — no `Model` suffix (e.g. `Screening`, `SanctionEntry`)
- `snake_case` column names
- Always inherit from `Base` imported from `src.database`
- All DB access must go through the async session — never use sync calls

**Router** (`router.py`):
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_session

router = APIRouter(tags=["<module_name>"])

@router.post("/entity", response_model=YourResponse)
async def your_endpoint(
    payload: YourRequest,
    session: AsyncSession = Depends(get_session),
) -> YourResponse:
    return await service.do_something(session, payload)
```

## Registering the router in `main.py`

After creating `router.py`, add one line to `api/src/main.py`:

```python
from src.<module_name> import router as <module_name>_router
app.include_router(<module_name>_router, prefix="/v1/<module_name>")
```

## Settings and config

Import settings from the central config — never read env vars directly:

```python
from src.config import settings

# Use settings.database_url, settings.cors_origins, etc.
```

## Error handling

Use `HTTPException` with a string `detail` field. The UI's `request<T>()` helper
reads `body.detail` to surface user-friendly error messages:

```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="No screening record found for the given ID.",
)
```

## Tests

- Test files go in `api/tests/` mirroring the module path
- `asyncio_mode = "auto"` is set in `pyproject.toml` — do **not** add `@pytest.mark.asyncio`
- Use `httpx.AsyncClient` with `app` for endpoint tests
- Use testcontainers (PostgreSQL) for any test that touches the DB

---

## When you add or change a SQLAlchemy model — migration steps

**Always use `--autogenerate`. Never write migration SQL by hand.**

1. Make your changes to `models.py`
2. Ensure `Base.metadata` is imported in `alembic/env.py` (so autogenerate detects the model)
3. Ensure `.env` is present so `alembic/env.py` can read `settings.database_url`
4. Generate the migration:
   ```bash
   cd api/
   uv run alembic revision --autogenerate -m "short description of change"
   ```
5. Review the generated file in `alembic/versions/` — check it looks correct
6. Apply the migration:
   ```bash
   uv run alembic upgrade head
   ```

**Critical rules:**
- Never edit a migration file that has already been applied anywhere (dev, CI, staging)
- `NullPool` in `alembic/env.py` prevents connection reuse during migrations — do not remove it
- If a model is new, `Base.metadata` must be imported before autogenerate will detect it
- An ADR is required if the schema change is non-trivial (see `/adr` skill)

## Checklist

- [ ] Four files created under `api/src/<module_name>/`
- [ ] Pydantic schemas follow `*Request` / `*Response` naming
- [ ] SQLAlchemy models use plain singular nouns and async session only
- [ ] Router registered in `main.py` with `/v1/<module_name>` prefix
- [ ] Config read via `settings`, not raw `os.environ`
- [ ] Migration generated and applied if any model was added or changed
- [ ] `uv run ruff check src tests` passes
- [ ] `uv run mypy src` passes
