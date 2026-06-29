"""
Fixtures for ingestion integration tests.

- `db_engine`  (session-scoped): one Postgres container per test session.
- `db_session` (function-scoped): fresh session per test, rolled back after.
- `client`     (function-scoped): AsyncClient with overridden get_db dependency.
"""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.postgresql import ENUM as PgENUM
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from src.database import get_db
from src.ingestion.models import Base
from src.main import app


@pytest.fixture(scope="session")
def postgres() -> PostgresContainer:
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg  # type: ignore[misc]


@pytest_asyncio.fixture(scope="session")
async def db_engine(postgres: PostgresContainer):  # type: ignore[no-untyped-def]
    # testcontainers gives a sync psycopg2 URL; swap driver for asyncpg
    url = postgres.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql+asyncpg://"
    )
    engine = create_async_engine(url, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda c: PgENUM("POTENTIAL_MATCH", "NO_MATCH", name="matchresult").create(
                c, checkfirst=True
            )
        )
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:  # type: ignore[no-untyped-def]
    async with db_engine.connect() as conn:
        await conn.begin()
        session = AsyncSession(
            bind=conn,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )
        yield session
        await session.close()
        await conn.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
