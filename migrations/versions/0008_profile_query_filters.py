"""Add profile modality filters and allow statewide PNCP collection.

Revision ID: 0008_profile_query_filters
Revises: 0007_phase4_fk_indexes
"""
from alembic import op
import sqlalchemy as sa


revision = "0008_profile_query_filters"
down_revision = "0007_phase4_fk_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "interest_profiles",
        sa.Column("modality_codes", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )
    op.alter_column("collection_runs", "municipality_code", existing_type=sa.String(length=20), nullable=True)


def downgrade() -> None:
    op.execute("UPDATE collection_runs SET municipality_code = 'ALL' WHERE municipality_code IS NULL")
    op.alter_column("collection_runs", "municipality_code", existing_type=sa.String(length=20), nullable=False)
    op.drop_column("interest_profiles", "modality_codes")
