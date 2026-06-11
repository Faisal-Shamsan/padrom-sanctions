from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  # silently drop any env vars not declared here
    )

    database_url: str = "postgresql+asyncpg://padrom:padrom@localhost:5432/padrom"
    cors_origins: list[str] = ["http://localhost:3000"]
    debug: bool = False
    screening_threshold: float = 0.85


# Single import target throughout the codebase: `from src.config import settings`
settings = Settings()
