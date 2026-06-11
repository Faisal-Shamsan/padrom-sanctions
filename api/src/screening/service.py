"""
Screening service: orchestrates the two-stage matcher, persists the log,
and returns a ScreeningResponse.
"""

import time

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.ingestion.models import SanctionEntry
from src.screening import matcher
from src.screening.models import MatchResult, ScreeningLog
from src.screening.schemas import MatchedEntry, ScreeningRequest, ScreeningResponse


async def screen(session: AsyncSession, body: ScreeningRequest) -> ScreeningResponse:
    t0 = time.monotonic()

    norm_name = matcher.normalise(body.name)

    # Stage A: DB trigram pre-filter (wide net)
    stmt = (
        select(SanctionEntry)
        .where(text("similarity(primary_name, :q) > 0.3"))
        .params(q=norm_name)
    )
    candidates = list((await session.execute(stmt)).scalars().all())

    # Stage B: Python composite scoring (strict)
    from src.config import settings  # local import avoids circular at module level

    entry, score = matcher.find_top_match(
        norm_name, candidates, threshold=settings.screening_threshold
    )

    result = MatchResult.POTENTIAL_MATCH if entry is not None else MatchResult.NO_MATCH
    duration_ms = int((time.monotonic() - t0) * 1000)

    log = ScreeningLog(
        external_id=body.external_id,
        queried_name=body.name,
        result=result,
        score=score,
        matched_entry_id=entry.id if entry is not None else None,
        duration_ms=duration_ms,
    )
    session.add(log)
    await session.commit()

    matched_entry: MatchedEntry | None = None
    if entry is not None:
        matched_entry = MatchedEntry(
            entry_id=entry.id,
            primary_name=entry.primary_name,
            source_list=entry.source_list,
            score=score,
        )

    return ScreeningResponse(
        screening_id=log.id,
        external_id=body.external_id,
        result=result.value,
        score=score,
        matched_entry=matched_entry,
        screened_at=log.screened_at,
        duration_ms=duration_ms,
    )
