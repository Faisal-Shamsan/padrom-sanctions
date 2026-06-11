import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.base import Base


class SanctionEntry(Base):
    __tablename__ = "sanction_entry"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    source_list: Mapped[str] = mapped_column(index=True)
    external_id: Mapped[str] = mapped_column()
    entity_type: Mapped[str] = mapped_column()
    primary_name: Mapped[str] = mapped_column(Text, index=True)
    aliases: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    raw_xml: Mapped[str] = mapped_column(Text)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("source_list", "external_id"),
        Index("ix_sanction_entry_aliases_gin", "aliases", postgresql_using="gin"),
    )
