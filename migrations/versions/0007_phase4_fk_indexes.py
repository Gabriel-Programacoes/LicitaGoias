"""Cover foreign-key lookups for phase 3 and 4 tables.

Revision ID: 0007_phase4_fk_indexes
Revises: 0006_phase4_notifications
"""
from alembic import op

revision = "0007_phase4_fk_indexes"
down_revision = "0006_phase4_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    indexes = (
        ("ix_feedback_opportunity_id", "opportunity_feedback", "opportunity_id"),
        ("ix_feedback_profile_id", "opportunity_feedback", "profile_id"),
        ("ix_feedback_user_id", "opportunity_feedback", "user_id"),
        ("ix_follows_opportunity_id", "opportunity_follows", "opportunity_id"),
        ("ix_notification_preferences_user_id", "notification_preferences", "user_id"),
        ("ix_alerts_opportunity_id", "opportunity_alerts", "opportunity_id"),
        ("ix_alerts_version_id", "opportunity_alerts", "version_id"),
        ("ix_email_outbox_user_id", "email_outbox", "user_id"),
        ("ix_unsubscribe_tokens_user_id", "email_unsubscribe_tokens", "user_id"),
    )
    for name, table, column in indexes:
        op.create_index(name, table, [column])


def downgrade() -> None:
    raise RuntimeError("Reverter índices da Fase 4 exige revisão de impacto")
