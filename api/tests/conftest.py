"""
Shared pytest fixtures.

Design notes:
- `postgres` is session-scoped: one container for the whole test run (fast).
- `client` is function-scoped: fresh AsyncClient per test (no state bleed).
- The health endpoint doesn't touch the DB, so `client` works without `postgres`.
  DB-dependent tests should request both fixtures.
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from testcontainers.postgres import PostgresContainer

from src.main import app


@pytest.fixture(scope="session")
def postgres() -> PostgresContainer:
    """Start a throwaway Postgres 16 container shared across the test session."""
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg  # type: ignore[misc]


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client wired directly to the FastAPI ASGI app (no network)."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
