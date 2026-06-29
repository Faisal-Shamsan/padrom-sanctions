"""add screening_log table

Revision ID: a3f2b1c8d9e0
Revises: 1a1a7ae4ec60
Create Date: 2026-06-11 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a3f2b1c8d9e0"
down_revision: Union[str, None] = "1a1a7ae4ec60"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable trigram extension (idempotent; may already exist on shared clusters)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # GIN trigram index on sanction_entry.primary_name for similarity() queries
    op.create_index(
        "ix_sanction_entry_primary_name_trgm",
        "sanction_entry",
        ["primary_name"],
        postgresql_using="gin",
        postgresql_ops={"primary_name": "gin_trgm_ops"},
    )

    # screening_log table
    op.create_table(
        "screening_log",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("external_id", sa.Text(), nullable=False),
        sa.Column("queried_name", sa.Text(), nullable=False),
        sa.Column(
            "result",
            postgresql.ENUM("POTENTIAL_MATCH", "NO_MATCH", name="matchresult", create_type=True),
            nullable=False,
        ),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column(
            "matched_entry_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sanction_entry.id"),
            nullable=True,
        ),
        sa.Column(
            "screened_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_screening_log_matched_entry_id",
        "screening_log",
        ["matched_entry_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_screening_log_matched_entry_id", table_name="screening_log")
    op.drop_table("screening_log")

    matchresult = postgresql.ENUM(
        "POTENTIAL_MATCH", "NO_MATCH", name="matchresult", create_type=False
    )
    matchresult.drop(op.get_bind(), checkfirst=True)

    op.drop_index(
        "ix_sanction_entry_primary_name_trgm", table_name="sanction_entry"
    )
    # pg_trgm extension is not dropped — it is system-level and may be shared
