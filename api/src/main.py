from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings

app = FastAPI(
    title="PADROM Sanctions Screening API",
    version="0.1.0",
    description="PoC — screens insurance counterparties against EU/UN sanctions lists.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Future routers will be included here, e.g.:
# app.include_router(screening.router, prefix="/v1/screen")
# app.include_router(ingestion.router, prefix="/v1/ingest")


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    """Liveness probe — returns 200 as long as the process is running."""
    return {"status": "ok"}
