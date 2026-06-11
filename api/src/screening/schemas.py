import uuid
from datetime import datetime

from pydantic import BaseModel


class ScreeningRequest(BaseModel):
    external_id: str
    name: str


class MatchedEntry(BaseModel):
    entry_id: uuid.UUID
    primary_name: str
    source_list: str
    score: float


class ScreeningResponse(BaseModel):
    screening_id: uuid.UUID
    external_id: str
    result: str
    score: float
    matched_entry: MatchedEntry | None
    screened_at: datetime
    duration_ms: int
