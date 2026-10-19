"""Add opportunity-level category criteria to interest profiles.

Revision ID: 0009_opportunity_categories
Revises: 0008_profile_query_filters
"""
from alembic import op
import sqlalchemy as sa


revision = "0009_opportunity_categories"
down_revision = "0008_profile_query_filters"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "interest_profiles",
        sa.Column("opportunity_category_ids", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )


def downgrade() -> None:
    op.drop_column("interest_profiles", "opportunity_category_ids")
