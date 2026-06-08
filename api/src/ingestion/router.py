import xml.etree.ElementTree as ET

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.ingestion import service
from src.ingestion.schemas import StatusResponse, SyncResponse

router = APIRouter(tags=["ingestion"])


@router.post("/sync", response_model=SyncResponse)
async def sync(session: AsyncSession = Depends(get_db)) -> SyncResponse:  # noqa: B008
    """Trigger a full refresh of the EU and UN sanctions lists."""
    try:
        return await service.run_full_sync(session)
    except (httpx.HTTPError, ET.ParseError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/status", response_model=StatusResponse)
async def status(session: AsyncSession = Depends(get_db)) -> StatusResponse:  # noqa: B008
    """Return entry counts and last-sync timestamps per list."""
    return await service.get_status(session)
