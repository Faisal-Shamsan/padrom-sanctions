"""add sanction_entry table

Revision ID: 1a1a7ae4ec60
Revises:
Create Date: 2026-06-01 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "1a1a7ae4ec60"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sanction_entry",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("source_list", sa.String(length=10), nullable=False),
        sa.Column("external_id", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=20), nullable=False),
        sa.Column("primary_name", sa.Text(), nullable=False),
        sa.Column("aliases", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("raw_xml", sa.Text(), nullable=False),
        sa.Column(
            "synced_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_list", "external_id"),
    )
    op.create_index(
        "ix_sanction_entry_source_list",
        "sanction_entry",
        ["source_list"],
    )
    op.create_index(
        "ix_sanction_entry_primary_name",
        "sanction_entry",
        ["primary_name"],
    )
    op.create_index(
        "ix_sanction_entry_aliases_gin",
        "sanction_entry",
        ["aliases"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_sanction_entry_aliases_gin", table_name="sanction_entry")
    op.drop_index("ix_sanction_entry_primary_name", table_name="sanction_entry")
    op.drop_index("ix_sanction_entry_source_list", table_name="sanction_entry")
    op.drop_table("sanction_entry")
