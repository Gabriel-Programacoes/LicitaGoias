"""Give the trusted backend a dedicated PostgreSQL login role.

Revision ID: 0004_backend_role
Revises: 0003_supabase_security
"""

from alembic import op


revision = "0004_backend_role"
down_revision = "0003_supabase_security"
branch_labels = None
depends_on = None


BACKEND_TABLES = (
    "collection_runs",
    "collection_progress",
    "collection_page_logs",
    "opportunity_records",
    "opportunity_versions",
    "source_snapshots",
    "users",
    "organizations",
    "memberships",
    "audit_events",
)


def upgrade() -> None:
    # Set the password outside migrations, in a local secret store or the
    # hosting platform's environment variables.
    op.execute("CREATE ROLE licitagoias_app LOGIN")
    op.execute(
        """
        DO $$
        BEGIN
            EXECUTE 'GRANT CONNECT ON DATABASE ' || quote_ident(current_database())
                || ' TO licitagoias_app';
        END
        $$
        """
    )
    op.execute("GRANT USAGE ON SCHEMA public TO licitagoias_app")

    for table in BACKEND_TABLES:
        op.execute(f"GRANT SELECT, INSERT, UPDATE ON TABLE public.{table} TO licitagoias_app")
        # Only the backend uses this role. It validates Supabase Auth tokens
        # and checks organization membership before accessing tenant data.
        op.execute(
            f"CREATE POLICY licitagoias_backend_access ON public.{table} "
            "FOR ALL TO licitagoias_app USING (true) WITH CHECK (true)"
        )


def downgrade() -> None:
    raise RuntimeError("Reverter o papel do backend exige retirar suas credenciais e revisar acessos ativos")
