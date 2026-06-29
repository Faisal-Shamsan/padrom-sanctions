from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.screening import service
from src.screening.schemas import HistoryResponse, ScreeningRequest, ScreeningResponse

router = APIRouter(tags=["screening"])


@router.post("/entity", response_model=ScreeningResponse)
async def screen_entity(
    body: ScreeningRequest,
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> ScreeningResponse:
    """Screen a counterparty name against the loaded sanctions lists."""
    return await service.screen(session, body)


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> HistoryResponse:
    """Paginated audit log of screening results."""
    return await service.get_history(session, page, page_size)
