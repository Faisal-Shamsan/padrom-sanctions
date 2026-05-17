from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

# echo=True logs every SQL statement — useful in dev, noisy in prod
engine = create_async_engine(settings.database_url, echo=settings.debug)

# expire_on_commit=False keeps model instances usable after commit
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async DB session per request."""
    async with AsyncSessionLocal() as session:
        yield session
