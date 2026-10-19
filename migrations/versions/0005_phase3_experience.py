"""Interest profiles, feedback and opportunity follows.

Revision ID: 0005_phase3_experience
Revises: 0004_backend_role
"""
from alembic import op
import sqlalchemy as sa


revision = "0005_phase3_experience"
down_revision = "0004_backend_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "interest_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("positive_terms", sa.JSON(), nullable=False),
        sa.Column("synonyms", sa.JSON(), nullable=False),
        sa.Column("negative_terms", sa.JSON(), nullable=False),
        sa.Column("municipalities", sa.JSON(), nullable=False),
        sa.Column("statuses", sa.JSON(), nullable=False),
        sa.Column("deadline_days", sa.Integer()),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_interest_profiles_organization_id", "interest_profiles", ["organization_id"])
    op.create_table(
        "opportunity_follows",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("opportunity_id", sa.String(36), sa.ForeignKey("opportunity_records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("baseline_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("organization_id", "opportunity_id", name="uq_follow_organization_opportunity"),
    )
    op.create_index("ix_follows_organization_created", "opportunity_follows", ["organization_id", "created_at"])
    op.create_table(
        "opportunity_feedback",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("opportunity_id", sa.String(36), sa.ForeignKey("opportunity_records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("profile_id", sa.String(36), sa.ForeignKey("interest_profiles.id", ondelete="SET NULL")),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("relevance", sa.String(20), nullable=False),
        sa.Column("reason", sa.String(40)),
        sa.Column("comment", sa.String(1000)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_feedback_organization_created", "opportunity_feedback", ["organization_id", "created_at"])

    for table in ("interest_profiles", "opportunity_follows", "opportunity_feedback"):
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"REVOKE ALL ON TABLE public.{table} FROM PUBLIC")
        op.execute(f"""
            DO $$
            DECLARE client_role text;
            BEGIN
                FOREACH client_role IN ARRAY ARRAY['anon', 'authenticated', 'service_role'] LOOP
                    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = client_role) THEN
                        EXECUTE 'REVOKE ALL ON TABLE public.{table} FROM ' || quote_ident(client_role);
                    END IF;
                END LOOP;
            END
            $$
        """)
        op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.{table} TO licitagoias_app")
        op.execute(
            f"CREATE POLICY licitagoias_backend_access ON public.{table} "
            "FOR ALL TO licitagoias_app USING (true) WITH CHECK (true)"
        )


def downgrade() -> None:
    raise RuntimeError("Reverter dados da Fase 3 exige revisão manual dos privilégios")
