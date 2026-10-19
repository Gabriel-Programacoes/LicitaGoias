"""Restrict the domain tables exposed by Supabase's public schema.

Revision ID: 0003_supabase_security
Revises: 0002_phase2
"""

from alembic import op


revision = "0003_supabase_security"
down_revision = "0002_phase2"
branch_labels = None
depends_on = None


DOMAIN_TABLES = (
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
    "alembic_version",
)


def upgrade() -> None:
    for table in DOMAIN_TABLES:
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")

    # These roles exist on Supabase but are absent from the plain PostgreSQL
    # instance used by local development and CI.
    op.execute(
        """
        DO $$
        DECLARE
            client_role text;
            table_name text;
        BEGIN
            FOREACH client_role IN ARRAY ARRAY['anon', 'authenticated', 'service_role'] LOOP
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = client_role) THEN
                    FOREACH table_name IN ARRAY ARRAY[
                        'collection_runs', 'collection_progress', 'collection_page_logs',
                        'opportunity_records', 'opportunity_versions', 'source_snapshots',
                        'users', 'organizations', 'memberships', 'audit_events',
                        'alembic_version'
                    ] LOOP
                        EXECUTE 'REVOKE ALL ON TABLE public.' || quote_ident(table_name)
                            || ' FROM ' || quote_ident(client_role);
                    END LOOP;
                END IF;
            END LOOP;
        END
        $$
        """
    )

    op.create_index("ix_opportunity_versions_opportunity_id", "opportunity_versions", ["opportunity_id"])
    op.create_index("ix_opportunity_versions_run_id", "opportunity_versions", ["run_id"])
    op.create_index("ix_source_snapshots_run_id", "source_snapshots", ["run_id"])
    op.create_index("ix_memberships_organization_id", "memberships", ["organization_id"])
    op.create_index("ix_audit_events_actor_user_id", "audit_events", ["actor_user_id"])
    op.create_index("ix_audit_events_organization_id", "audit_events", ["organization_id"])


def downgrade() -> None:
    raise RuntimeError("Reverter a proteção RLS exige revisão manual dos privilégios de acesso")
