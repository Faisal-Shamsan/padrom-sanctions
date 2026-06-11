"""Integration tests for POST /v1/screen/entity."""

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.ingestion.models import SanctionEntry
from src.screening.models import MatchResult, ScreeningLog


@pytest_asyncio.fixture
async def sanctioned_entry(db_session: AsyncSession) -> SanctionEntry:
    """Seed a single SanctionEntry for matching tests."""
    entry = SanctionEntry(
        source_list="EU",
        external_id="EU-TEST-001",
        entity_type="P",
        primary_name="Viktor Bout",
        aliases=["Victor Bout", "Viktor Anatolyevich Bout"],
        raw_xml="<test/>",
    )
    db_session.add(entry)
    await db_session.flush()
    return entry


@pytest.mark.asyncio
async def test_screen_matching_name_returns_potential_match(
    client: AsyncClient,
    sanctioned_entry: SanctionEntry,
    db_session: AsyncSession,
) -> None:
    response = await client.post(
        "/v1/screen/entity",
        json={"external_id": "CPTY-001", "name": "Viktor Bout"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == MatchResult.POTENTIAL_MATCH.value
    assert data["score"] == 1.0
    assert data["matched_entry"] is not None
    assert data["matched_entry"]["entry_id"] == str(sanctioned_entry.id)
    assert data["external_id"] == "CPTY-001"
    assert data["duration_ms"] >= 0


@pytest.mark.asyncio
async def test_screen_unrelated_name_returns_no_match(
    client: AsyncClient,
    sanctioned_entry: SanctionEntry,
    db_session: AsyncSession,
) -> None:
    response = await client.post(
        "/v1/screen/entity",
        json={"external_id": "CPTY-002", "name": "John Smith"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == MatchResult.NO_MATCH.value
    assert data["matched_entry"] is None
    assert data["score"] == 0.0


@pytest.mark.asyncio
async def test_potential_match_persists_screening_log(
    client: AsyncClient,
    sanctioned_entry: SanctionEntry,
    db_session: AsyncSession,
) -> None:
    response = await client.post(
        "/v1/screen/entity",
        json={"external_id": "CPTY-003", "name": "Viktor Bout"},
    )
    assert response.status_code == 200
    screening_id = uuid.UUID(response.json()["screening_id"])

    log = await db_session.get(ScreeningLog, screening_id)
    assert log is not None
    assert log.result == MatchResult.POTENTIAL_MATCH
    assert log.queried_name == "Viktor Bout"
    assert log.matched_entry_id == sanctioned_entry.id
    assert log.score == 1.0


@pytest.mark.asyncio
async def test_no_match_persists_screening_log(
    client: AsyncClient,
    sanctioned_entry: SanctionEntry,
    db_session: AsyncSession,
) -> None:
    response = await client.post(
        "/v1/screen/entity",
        json={"external_id": "CPTY-004", "name": "John Smith"},
    )
    assert response.status_code == 200
    screening_id = uuid.UUID(response.json()["screening_id"])

    log = await db_session.get(ScreeningLog, screening_id)
    assert log is not None
    assert log.result == MatchResult.NO_MATCH
    assert log.matched_entry_id is None
    assert log.score == 0.0


@pytest.mark.asyncio
async def test_screen_alias_match(
    client: AsyncClient,
    sanctioned_entry: SanctionEntry,
    db_session: AsyncSession,
) -> None:
    response = await client.post(
        "/v1/screen/entity",
        json={"external_id": "CPTY-005", "name": "Victor Bout"},
    )
    assert response.status_code == 200
    data = response.json()
    # Alias exact match → POTENTIAL_MATCH with score 1.0
    assert data["result"] == MatchResult.POTENTIAL_MATCH.value
    assert data["score"] == 1.0
