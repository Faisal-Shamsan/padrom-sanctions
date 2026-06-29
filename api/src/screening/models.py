import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import ENUM as PgENUM
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.base import Base


class MatchResult(StrEnum):
    POTENTIAL_MATCH = "POTENTIAL_MATCH"
    NO_MATCH = "NO_MATCH"


class ScreeningLog(Base):
    __tablename__ = "screening_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    external_id: Mapped[str] = mapped_column(Text, nullable=False)
    queried_name: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[MatchResult] = mapped_column(
        PgENUM("POTENTIAL_MATCH", "NO_MATCH", name="matchresult", create_type=False),
        nullable=False,
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    matched_entry_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sanction_entry.id"),
        nullable=True,
        index=True,
    )
    screened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
