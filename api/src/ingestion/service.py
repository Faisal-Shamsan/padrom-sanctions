import time
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass, field

import httpx
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ingestion.models import SanctionEntry
from src.ingestion.schemas import (
    ListStatus,
    ListSyncResult,
    StatusResponse,
    SyncResponse,
)

EU_URL = (
    "https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/"
    "content?token=dG9rZW4tMjAxNw"
)
UN_URL = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"


@dataclass
class _ParsedEntry:
    source_list: str
    external_id: str
    entity_type: str
    primary_name: str
    aliases: list[str] = field(default_factory=list)
    raw_xml: str = ""


def _ns_tag(tag: str, ns: str) -> str:
    """Wrap tag with namespace prefix if namespace is non-empty."""
    return f"{{{ns}}}{tag}" if ns else tag


def _parse_eu_xml(xml_text: str) -> list[_ParsedEntry]:
    root = ET.fromstring(xml_text)
    ns = root.tag.split("}")[0].lstrip("{") if "}" in root.tag else ""

    entries: list[_ParsedEntry] = []

    for entity in root.iter(_ns_tag("sanctionEntity", ns)):
        logical_id = entity.get("logicalId", "")
        if not logical_id:
            continue

        subject_type_el = entity.find(f".//{_ns_tag('subjectType', ns)}")
        code = subject_type_el.get("code", "") if subject_type_el is not None else ""
        entity_type = "PERSON" if code == "P" else "ENTITY"

        primary_name: str | None = None
        aliases: list[str] = []

        for name_alias in entity.iter(_ns_tag("nameAlias", ns)):
            whole_name = name_alias.get("wholeName", "").strip()
            first_name = name_alias.get("firstName", "").strip()
            last_name = name_alias.get("lastName", "").strip()

            name = whole_name or " ".join(p for p in [first_name, last_name] if p)
            if not name:
                continue

            if name_alias.get("strong") == "true":
                primary_name = name
            else:
                aliases.append(name)

        if primary_name is None:
            if aliases:
                primary_name = aliases.pop(0)
            else:
                continue

        raw_xml = ET.tostring(entity, encoding="unicode")
        entries.append(
            _ParsedEntry(
                source_list="EU",
                external_id=logical_id,
                entity_type=entity_type,
                primary_name=primary_name,
                aliases=aliases,
                raw_xml=raw_xml,
            )
        )

    return entries


def _parse_un_xml(xml_text: str) -> list[_ParsedEntry]:
    root = ET.fromstring(xml_text)
    entries: list[_ParsedEntry] = []

    for individual in root.iter("INDIVIDUAL"):
        dataid = individual.findtext("DATAID", "").strip()
        if not dataid:
            continue

        parts = [
            individual.findtext("FIRST_NAME", "").strip(),
            individual.findtext("SECOND_NAME", "").strip(),
            individual.findtext("THIRD_NAME", "").strip(),
            individual.findtext("FOURTH_NAME", "").strip(),
        ]
        primary_name = " ".join(p for p in parts if p)
        if not primary_name:
            continue

        aliases: list[str] = []
        for alias_el in individual.iter("INDIVIDUAL_ALIAS"):
            quality = alias_el.findtext("QUALITY", "").strip()
            alias_name = alias_el.findtext("ALIAS_NAME", "").strip()
            if quality == "Good quality" and alias_name:
                aliases.append(alias_name)

        raw_xml = ET.tostring(individual, encoding="unicode")
        entries.append(
            _ParsedEntry(
                source_list="UN",
                external_id=dataid,
                entity_type="PERSON",
                primary_name=primary_name,
                aliases=aliases,
                raw_xml=raw_xml,
            )
        )

    for entity_el in root.iter("ENTITY"):
        dataid = entity_el.findtext("DATAID", "").strip()
        if not dataid:
            continue

        primary_name = entity_el.findtext("FIRST_NAME", "").strip()
        if not primary_name:
            continue

        aliases = []
        for alias_el in entity_el.iter("ENTITY_ALIAS"):
            quality = alias_el.findtext("QUALITY", "").strip()
            alias_name = alias_el.findtext("ALIAS_NAME", "").strip()
            if quality == "Good quality" and alias_name:
                aliases.append(alias_name)

        raw_xml = ET.tostring(entity_el, encoding="unicode")
        entries.append(
            _ParsedEntry(
                source_list="UN",
                external_id=dataid,
                entity_type="ENTITY",
                primary_name=primary_name,
                aliases=aliases,
                raw_xml=raw_xml,
            )
        )

    return entries


async def _download(url: str) -> str:
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


async def _sync_one_list(
    session: AsyncSession,
    source_list: str,
    url: str,
    parser: Callable[[str], list[_ParsedEntry]],
) -> ListSyncResult:
    t0 = time.monotonic()
    xml_text = await _download(url)
    parsed = parser(xml_text)

    await session.execute(
        delete(SanctionEntry).where(SanctionEntry.source_list == source_list)
    )

    session.add_all(
        [
            SanctionEntry(
                source_list=entry.source_list,
                external_id=entry.external_id,
                entity_type=entry.entity_type,
                primary_name=entry.primary_name,
                aliases=entry.aliases,
                raw_xml=entry.raw_xml,
            )
            for entry in parsed
        ]
    )
    await session.flush()

    duration = time.monotonic() - t0
    return ListSyncResult(
        source_list=source_list,
        inserted=len(parsed),
        duration_seconds=round(duration, 3),
    )


async def run_full_sync(session: AsyncSession) -> SyncResponse:
    eu_result = await _sync_one_list(session, "EU", EU_URL, _parse_eu_xml)
    un_result = await _sync_one_list(session, "UN", UN_URL, _parse_un_xml)
    await session.commit()

    results = [eu_result, un_result]
    return SyncResponse(
        results=results,
        total_inserted=sum(r.inserted for r in results),
    )


async def get_status(session: AsyncSession) -> StatusResponse:
    stmt = select(
        SanctionEntry.source_list,
        func.count().label("entry_count"),
        func.max(SanctionEntry.synced_at).label("last_synced_at"),
    ).group_by(SanctionEntry.source_list)

    result = await session.execute(stmt)
    rows = result.all()

    lists = [
        ListStatus(
            source_list=row.source_list,
            entry_count=row.entry_count,
            last_synced_at=row.last_synced_at,
        )
        for row in rows
    ]
    return StatusResponse(lists=lists)
