"""Versioned alerts, notification preferences and email outbox.

Revision ID: 0006_phase4_notifications
Revises: 0005_phase3_experience
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_phase4_notifications"
down_revision = "0005_phase3_experience"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email_enabled", sa.Boolean(), nullable=False),
        sa.Column("digest_frequency", sa.String(10), nullable=False),
        sa.Column("digest_hour", sa.Integer(), nullable=False),
        sa.Column("timezone_name", sa.String(80), nullable=False),
        sa.Column("critical_alerts", sa.Boolean(), nullable=False),
        sa.Column("last_digest_at", sa.DateTime(timezone=True)),
        sa.Column("next_digest_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_notification_preference_org_user"),
        sa.CheckConstraint("digest_frequency IN ('off', 'daily', 'weekly')", name="ck_notification_digest_frequency"),
        sa.CheckConstraint("digest_hour BETWEEN 0 AND 23", name="ck_notification_digest_hour"),
    )
    op.create_index("ix_notification_preferences_due", "notification_preferences", ["digest_frequency", "next_digest_at"])
    op.create_table(
        "opportunity_alerts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("opportunity_id", sa.String(36), sa.ForeignKey("opportunity_records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_id", sa.String(36), sa.ForeignKey("opportunity_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(40), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("changes", sa.JSON(), nullable=False),
        sa.Column("idempotency_key", sa.String(64), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("organization_id", "opportunity_id", "version_id", name="uq_alert_org_opportunity_version"),
        sa.UniqueConstraint("idempotency_key", name="uq_alert_idempotency_key"),
    )
    op.create_index("ix_alerts_org_created", "opportunity_alerts", ["organization_id", "created_at"])
    op.create_table(
        "email_outbox",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("idempotency_key", sa.String(160), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("locked_until", sa.DateTime(timezone=True)),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True)),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("provider_message_id", sa.String(255)),
        sa.Column("last_error", sa.String(160)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("idempotency_key", name="uq_email_outbox_idempotency_key"),
        sa.CheckConstraint("status IN ('pending', 'processing', 'sent', 'dead', 'suppressed')", name="ck_email_outbox_status"),
    )
    op.create_index("ix_email_outbox_ready", "email_outbox", ["status", "available_at", "created_at"])
    op.create_index("ix_email_outbox_org_created", "email_outbox", ["organization_id", "created_at"])
    op.create_table(
        "email_suppressions",
        sa.Column("email", sa.String(320), primary_key=True),
        sa.Column("reason", sa.String(20), nullable=False),
        sa.Column("provider_event_id", sa.String(255), unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "email_unsubscribe_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_unsubscribe_tokens_org_user", "email_unsubscribe_tokens", ["organization_id", "user_id"])
    op.create_table(
        "email_delivery_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider_event_id", sa.String(255), nullable=False, unique=True),
        sa.Column("outbox_id", sa.String(36), sa.ForeignKey("email_outbox.id", ondelete="SET NULL")),
        sa.Column("event_type", sa.String(20), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True)),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_delivery_events_outbox", "email_delivery_events", ["outbox_id", "received_at"])

    tables = ("notification_preferences", "opportunity_alerts", "email_outbox", "email_suppressions",
              "email_unsubscribe_tokens", "email_delivery_events")
    for table in tables:
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"REVOKE ALL ON TABLE public.{table} FROM PUBLIC")
        op.execute(f"""DO $$ DECLARE client_role text; BEGIN
            FOREACH client_role IN ARRAY ARRAY['anon', 'authenticated', 'service_role'] LOOP
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = client_role) THEN
                    EXECUTE 'REVOKE ALL ON TABLE public.{table} FROM ' || quote_ident(client_role);
                END IF;
            END LOOP; END $$""")
        op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.{table} TO licitagoias_app")
        op.execute(f"CREATE POLICY licitagoias_backend_access ON public.{table} FOR ALL TO licitagoias_app USING (true) WITH CHECK (true)")


def downgrade() -> None:
    raise RuntimeError("Reverter alertas e preferências exige revisão manual dos dados e privilégios")
