from __future__ import annotations

import os
from functools import lru_cache
from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid4())


class Base(DeclarativeBase):
    pass


class CollectionRun(Base):
    __tablename__ = "collection_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    source: Mapped[str] = mapped_column(String(40), nullable=False)
    municipality_code: Mapped[str | None] = mapped_column(String(20))
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    segments: Mapped[list] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="running")
    error: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class CollectionProgress(Base):
    __tablename__ = "collection_progress"
    __table_args__ = (UniqueConstraint("run_id", "segment"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    run_id: Mapped[str] = mapped_column(ForeignKey("collection_runs.id", ondelete="CASCADE"), nullable=False)
    segment: Mapped[str] = mapped_column(String(60), nullable=False)
    last_page: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_pages: Mapped[int | None] = mapped_column(Integer)
    record_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    complete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class CollectionPageLog(Base):
    __tablename__ = "collection_page_logs"
    __table_args__ = (UniqueConstraint("run_id", "segment", "page"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    run_id: Mapped[str] = mapped_column(ForeignKey("collection_runs.id", ondelete="CASCADE"), nullable=False)
    segment: Mapped[str] = mapped_column(String(60), nullable=False)
    page: Mapped[int] = mapped_column(Integer, nullable=False)
    total_pages: Mapped[int] = mapped_column(Integer, nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class OpportunityRecord(Base):
    __tablename__ = "opportunity_records"
    __table_args__ = (
        UniqueConstraint("source", "external_id"),
        Index("ix_opportunity_status", "official_status"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    source: Mapped[str] = mapped_column(String(40), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    identity_method: Mapped[str] = mapped_column(String(40), nullable=False)
    review_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    official_status: Mapped[str | None] = mapped_column(String(255))
    derived_state: Mapped[str] = mapped_column(String(40), nullable=False, default="unknown")
    current_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    current_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    first_observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    last_observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class OpportunityVersion(Base):
    __tablename__ = "opportunity_versions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunity_records.id", ondelete="CASCADE"), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    previous_hash: Mapped[str | None] = mapped_column(String(64))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    run_id: Mapped[str | None] = mapped_column(ForeignKey("collection_runs.id"))


class SourceSnapshot(Base):
    __tablename__ = "source_snapshots"
    __table_args__ = (UniqueConstraint("opportunity_id", "raw_hash"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunity_records.id", ondelete="CASCADE"), nullable=False)
    raw_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    first_observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    last_observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    run_id: Mapped[str | None] = mapped_column(ForeignKey("collection_runs.id"))


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    auth_subject: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "organization_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    actor_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"))
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class InterestProfile(Base):
    __tablename__ = "interest_profiles"
    __table_args__ = (Index("ix_interest_profiles_organization_id", "organization_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    positive_terms: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    synonyms: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    negative_terms: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    municipalities: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    statuses: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    modality_codes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    opportunity_category_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    deadline_days: Mapped[int | None] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class OpportunityFollow(Base):
    __tablename__ = "opportunity_follows"
    __table_args__ = (
        UniqueConstraint("organization_id", "opportunity_id", name="uq_follow_organization_opportunity"),
        Index("ix_follows_organization_created", "organization_id", "created_at"),
        Index("ix_follows_opportunity_id", "opportunity_id"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunity_records.id", ondelete="CASCADE"), nullable=False)
    baseline_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class OpportunityFeedback(Base):
    __tablename__ = "opportunity_feedback"
    __table_args__ = (
        Index("ix_feedback_organization_created", "organization_id", "created_at"),
        Index("ix_feedback_opportunity_id", "opportunity_id"),
        Index("ix_feedback_profile_id", "profile_id"),
        Index("ix_feedback_user_id", "user_id"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunity_records.id", ondelete="CASCADE"), nullable=False)
    profile_id: Mapped[str | None] = mapped_column(ForeignKey("interest_profiles.id", ondelete="SET NULL"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    relevance: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(40))
    comment: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_notification_preference_org_user"),
        Index("ix_notification_preferences_due", "digest_frequency", "next_digest_at"),
        Index("ix_notification_preferences_user_id", "user_id"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    email_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    digest_frequency: Mapped[str] = mapped_column(String(10), nullable=False, default="off")
    digest_hour: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    timezone_name: Mapped[str] = mapped_column(String(80), nullable=False, default="America/Sao_Paulo")
    critical_alerts: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_digest_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_digest_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class OpportunityAlert(Base):
    __tablename__ = "opportunity_alerts"
    __table_args__ = (
        UniqueConstraint("organization_id", "opportunity_id", "version_id", name="uq_alert_org_opportunity_version"),
        UniqueConstraint("idempotency_key", name="uq_alert_idempotency_key"),
        Index("ix_alerts_org_created", "organization_id", "created_at"),
        Index("ix_alerts_opportunity_id", "opportunity_id"),
        Index("ix_alerts_version_id", "version_id"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunity_records.id", ondelete="CASCADE"), nullable=False)
    version_id: Mapped[str] = mapped_column(ForeignKey("opportunity_versions.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    changes: Mapped[dict] = mapped_column(JSON, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(64), nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class EmailOutbox(Base):
    __tablename__ = "email_outbox"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_email_outbox_idempotency_key"),
        Index("ix_email_outbox_ready", "status", "available_at", "created_at"),
        Index("ix_email_outbox_org_created", "organization_id", "created_at"),
        Index("ix_email_outbox_user_id", "user_id"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(160), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    provider_message_id: Mapped[str | None] = mapped_column(String(255))
    last_error: Mapped[str | None] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class EmailSuppression(Base):
    __tablename__ = "email_suppressions"
    email: Mapped[str] = mapped_column(String(320), primary_key=True)
    reason: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_event_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class EmailUnsubscribeToken(Base):
    __tablename__ = "email_unsubscribe_tokens"
    __table_args__ = (
        Index("ix_unsubscribe_tokens_org_user", "organization_id", "user_id"),
        Index("ix_unsubscribe_tokens_user_id", "user_id"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class EmailDeliveryEvent(Base):
    __tablename__ = "email_delivery_events"
    __table_args__ = (Index("ix_delivery_events_outbox", "outbox_id", "received_at"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    provider_event_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    outbox_id: Mapped[str | None] = mapped_column(ForeignKey("email_outbox.id", ondelete="SET NULL"))
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


def database_url() -> str:
    value = os.getenv("LICITAGOIAS_DATABASE_URL")
    if not value:
        raise RuntimeError("Defina LICITAGOIAS_DATABASE_URL com uma URL postgresql+psycopg://")
    if not value.startswith("postgresql+psycopg://"):
        raise ValueError("A Fase 1 requer PostgreSQL com driver psycopg")
    return value


@lru_cache(maxsize=4)
def _factory(url: str):
    engine = create_engine(url, pool_pre_ping=True)
    return sessionmaker(engine, expire_on_commit=False)


def session_factory():
    return _factory(database_url())
