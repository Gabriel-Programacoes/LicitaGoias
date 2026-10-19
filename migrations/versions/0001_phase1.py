"""Initial reliable ingestion schema.

Revision ID: 0001_phase1
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_phase1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collection_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source", sa.String(40), nullable=False),
        sa.Column("municipality_code", sa.String(20), nullable=False),
        sa.Column("uf", sa.String(2), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("segments", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("error", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "collection_progress",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("collection_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("segment", sa.String(60), nullable=False),
        sa.Column("last_page", sa.Integer(), nullable=False),
        sa.Column("total_pages", sa.Integer()),
        sa.Column("record_count", sa.Integer(), nullable=False),
        sa.Column("complete", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("run_id", "segment"),
    )
    op.create_table(
        "opportunity_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source", sa.String(40), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("identity_method", sa.String(40), nullable=False),
        sa.Column("review_required", sa.Boolean(), nullable=False),
        sa.Column("official_status", sa.String(255)),
        sa.Column("derived_state", sa.String(40), nullable=False),
        sa.Column("current_hash", sa.String(64), nullable=False),
        sa.Column("current_data", sa.JSON(), nullable=False),
        sa.Column("first_observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source", "external_id"),
    )
    op.create_index("ix_opportunity_status", "opportunity_records", ["official_status"])
    op.create_table(
        "collection_page_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("collection_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("segment", sa.String(60), nullable=False),
        sa.Column("page", sa.Integer(), nullable=False),
        sa.Column("total_pages", sa.Integer(), nullable=False),
        sa.Column("record_count", sa.Integer(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("run_id", "segment", "page"),
    )
    op.create_table(
        "opportunity_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("opportunity_id", sa.String(36), sa.ForeignKey("opportunity_records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("previous_hash", sa.String(64)),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("collection_runs.id")),
    )
    op.create_table(
        "source_snapshots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("opportunity_id", sa.String(36), sa.ForeignKey("opportunity_records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("raw_hash", sa.String(64), nullable=False),
        sa.Column("raw_data", sa.JSON(), nullable=False),
        sa.Column("first_observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("collection_runs.id")),
        sa.UniqueConstraint("opportunity_id", "raw_hash"),
    )


def downgrade() -> None:
    op.drop_table("source_snapshots")
    op.drop_table("opportunity_versions")
    op.drop_index("ix_opportunity_status", table_name="opportunity_records")
    op.drop_table("opportunity_records")
    op.drop_table("collection_page_logs")
    op.drop_table("collection_progress")
    op.drop_table("collection_runs")
