from datetime import datetime

from pydantic import BaseModel


class ListSyncResult(BaseModel):
    source_list: str
    inserted: int
    duration_seconds: float


class SyncResponse(BaseModel):
    results: list[ListSyncResult]
    total_inserted: int


class ListStatus(BaseModel):
    source_list: str
    entry_count: int
    last_synced_at: datetime | None


class StatusResponse(BaseModel):
    lists: list[ListStatus]
