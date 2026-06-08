"""
Integration tests for POST /v1/ingest/sync and GET /v1/ingest/status.

_download is mocked so tests never hit the network.
"""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from httpx import AsyncClient

# Minimal but structurally valid EU XML for mocking
EU_XML = """<?xml version="1.0" encoding="UTF-8"?>
<export>
  <sanctionEntity logicalId="EU-001">
    <entity><subjectType code="P"/></entity>
    <nameAlias wholeName="John DOE" strong="true"/>
  </sanctionEntity>
  <sanctionEntity logicalId="EU-002">
    <entity><subjectType code="E"/></entity>
    <nameAlias wholeName="ACME Corp" strong="true"/>
  </sanctionEntity>
</export>"""

# Minimal but structurally valid UN XML for mocking
UN_XML = """<?xml version="1.0" encoding="UTF-8"?>
<CONSOLIDATED_LIST>
  <INDIVIDUALS>
    <INDIVIDUAL>
      <DATAID>UN-001</DATAID>
      <FIRST_NAME>ALI</FIRST_NAME>
      <SECOND_NAME>HASSAN</SECOND_NAME>
      <THIRD_NAME></THIRD_NAME>
      <FOURTH_NAME></FOURTH_NAME>
    </INDIVIDUAL>
  </INDIVIDUALS>
  <ENTITIES>
    <ENTITY>
      <DATAID>UN-E-001</DATAID>
      <FIRST_NAME>BAD CORP</FIRST_NAME>
    </ENTITY>
  </ENTITIES>
</CONSOLIDATED_LIST>"""


@pytest.mark.asyncio
async def test_sync_returns_200_with_correct_counts(client: AsyncClient) -> None:
    with patch("src.ingestion.service._download", new_callable=AsyncMock) as mock_dl:
        mock_dl.side_effect = [EU_XML, UN_XML]
        response = await client.post("/v1/ingest/sync")

    assert response.status_code == 200
    body = response.json()
    assert body["total_inserted"] == 4  # 2 EU + 2 UN

    results_by_list = {r["source_list"]: r for r in body["results"]}
    assert results_by_list["EU"]["inserted"] == 2
    assert results_by_list["UN"]["inserted"] == 2


@pytest.mark.asyncio
async def test_sync_is_idempotent(client: AsyncClient) -> None:
    with patch("src.ingestion.service._download", new_callable=AsyncMock) as mock_dl:
        mock_dl.side_effect = [EU_XML, UN_XML, EU_XML, UN_XML]
        await client.post("/v1/ingest/sync")
        response = await client.post("/v1/ingest/sync")

    assert response.status_code == 200
    body = response.json()
    # Second sync should yield same counts (full replace)
    assert body["total_inserted"] == 4


@pytest.mark.asyncio
async def test_status_shows_both_lists_after_sync(client: AsyncClient) -> None:
    with patch("src.ingestion.service._download", new_callable=AsyncMock) as mock_dl:
        mock_dl.side_effect = [EU_XML, UN_XML]
        await client.post("/v1/ingest/sync")

    response = await client.get("/v1/ingest/status")
    assert response.status_code == 200
    body = response.json()

    source_lists = {lst["source_list"] for lst in body["lists"]}
    assert "EU" in source_lists
    assert "UN" in source_lists

    for lst in body["lists"]:
        assert lst["entry_count"] > 0
        assert lst["last_synced_at"] is not None


@pytest.mark.asyncio
async def test_sync_returns_502_on_download_failure(client: AsyncClient) -> None:
    with patch("src.ingestion.service._download", new_callable=AsyncMock) as mock_dl:
        mock_dl.side_effect = httpx.ConnectError("connection refused")
        response = await client.post("/v1/ingest/sync")

    assert response.status_code == 502
