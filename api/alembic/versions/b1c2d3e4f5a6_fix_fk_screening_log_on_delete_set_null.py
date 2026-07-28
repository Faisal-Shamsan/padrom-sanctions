"""fix fk screening_log matched_entry_id on delete set null

Revision ID: b1c2d3e4f5a6
Revises: a3f2b1c8d9e0
Create Date: 2026-07-28 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, None] = "a3f2b1c8d9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the existing FK (no delete rule) and re-add with ON DELETE SET NULL.
    # The column is already nullable, so this is safe: when a sanction_entry row
    # is deleted during re-sync, matched_entry_id becomes NULL instead of blocking
    # the delete with a ForeignKeyViolationError.
    op.drop_constraint(
        "screening_log_matched_entry_id_fkey",
        "screening_log",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "screening_log_matched_entry_id_fkey",
        "screening_log",
        "sanction_entry",
        ["matched_entry_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "screening_log_matched_entry_id_fkey",
        "screening_log",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "screening_log_matched_entry_id_fkey",
        "screening_log",
        "sanction_entry",
        ["matched_entry_id"],
        ["id"],
    )
