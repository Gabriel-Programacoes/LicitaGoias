from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from licitagoias.api.app import get_current_user, get_db
from licitagoias.phase1_db import (
    EmailDeliveryEvent, EmailOutbox, EmailSuppression, EmailUnsubscribeToken,
    Membership, NotificationPreference, OpportunityAlert, OpportunityRecord, User, utcnow,
)

router = APIRouter(tags=["alerts", "notification-preferences"])


class PreferenceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email_enabled: bool
    digest_frequency: Literal["off", "daily", "weekly"]
    digest_hour: int = Field(ge=0, le=23)
    timezone_name: str = Field(min_length=1, max_length=80)
    critical_alerts: bool = False


class WebhookEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider_event_id: str = Field(min_length=1, max_length=255)
    message_id: str = Field(min_length=1, max_length=255)
    event_type: Literal["delivered", "bounced", "complained"]
    occurred_at: datetime | None = None


def _membership(db: Session, user: User) -> Membership:
    row = db.scalar(select(Membership).where(Membership.user_id == user.id).order_by(Membership.created_at).limit(1))
    if row is None:
        raise HTTPException(status_code=403, detail="Crie uma organização antes de configurar alertas")
    return row


def _next_digest(now: datetime, frequency: str, hour: int, zone: ZoneInfo) -> datetime | None:
    if frequency == "off":
        return None
    local = now.astimezone(zone)
    candidate = local.replace(hour=hour, minute=0, second=0, microsecond=0)
    if candidate <= local:
        from datetime import timedelta
        candidate += timedelta(days=1)
    if frequency == "weekly":
        from datetime import timedelta
        while candidate.weekday() != 0:
            candidate += timedelta(days=1)
    return candidate.astimezone(timezone.utc)


@router.get("/v1/notification-preferences")
def get_preferences(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = _membership(db, user)
    row = db.scalar(select(NotificationPreference).where(
        NotificationPreference.organization_id == membership.organization_id,
        NotificationPreference.user_id == user.id,
    ))
    if row is None:
        return {"email_enabled": False, "digest_frequency": "off", "digest_hour": 8,
                "timezone_name": "America/Sao_Paulo", "critical_alerts": False}
    return {key: getattr(row, key) for key in ("email_enabled", "digest_frequency", "digest_hour", "timezone_name", "critical_alerts")}


@router.put("/v1/notification-preferences")
def put_preferences(payload: PreferenceInput, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = _membership(db, user)
    if payload.email_enabled and not user.email_verified:
        raise HTTPException(status_code=403, detail="Confirme seu e-mail antes de ativar notificações")
    try:
        zone = ZoneInfo(payload.timezone_name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Fuso horário inválido") from exc
    suppressed = db.get(EmailSuppression, user.email.strip().casefold())
    if payload.email_enabled and suppressed:
        raise HTTPException(status_code=409, detail="Este endereço está bloqueado para envio")
    now = utcnow()
    row = db.scalar(select(NotificationPreference).where(
        NotificationPreference.organization_id == membership.organization_id,
        NotificationPreference.user_id == user.id,
    ))
    values = payload.model_dump()
    if row is None:
        row = NotificationPreference(organization_id=membership.organization_id, user_id=user.id, **values)
        db.add(row)
    else:
        for key, value in values.items():
            setattr(row, key, value)
    row.last_digest_at = now
    row.next_digest_at = _next_digest(now, payload.digest_frequency, payload.digest_hour, zone) if payload.email_enabled else None
    row.updated_at = now
    db.commit()
    return {**values, "next_digest_at": row.next_digest_at}


@router.get("/v1/alerts")
def list_alerts(unread_only: bool = Query(False), limit: int = Query(50, ge=1, le=100),
                user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = _membership(db, user)
    query = select(OpportunityAlert, OpportunityRecord).join(
        OpportunityRecord, OpportunityRecord.id == OpportunityAlert.opportunity_id
    ).where(OpportunityAlert.organization_id == membership.organization_id)
    if unread_only:
        query = query.where(OpportunityAlert.read_at.is_(None))
    rows = db.execute(query.order_by(OpportunityAlert.created_at.desc(), OpportunityAlert.id).limit(limit)).all()
    return [{"id": alert.id, "event_type": alert.event_type, "severity": alert.severity,
             "changes": alert.changes, "created_at": alert.created_at, "read_at": alert.read_at,
             "opportunity": {"id": opportunity.id, "data": opportunity.current_data}}
            for alert, opportunity in rows]


@router.get("/v1/notifications/status")
def notification_status(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = _membership(db, user)
    counts = dict(db.execute(select(EmailOutbox.status, func.count(EmailOutbox.id)).where(
        EmailOutbox.organization_id == membership.organization_id
    ).group_by(EmailOutbox.status)).all())
    latest = db.scalar(select(func.max(EmailOutbox.sent_at)).where(
        EmailOutbox.organization_id == membership.organization_id
    ))
    return {"queue": {key: counts.get(key, 0) for key in ("pending", "processing", "sent", "dead", "suppressed")},
            "last_sent_at": latest, "email_transport_enabled": (
                os.getenv("LICITAGOIAS_EMAIL_ENABLED", "false").lower() == "true" and
                os.getenv("LICITAGOIAS_EMAIL_DOMAIN_VERIFIED", "false").lower() == "true"
            )}


@router.post("/v1/alerts/{alert_id}/read")
def mark_alert_read(alert_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = _membership(db, user)
    alert = db.scalar(select(OpportunityAlert).where(
        OpportunityAlert.id == str(alert_id), OpportunityAlert.organization_id == membership.organization_id
    ))
    if alert is None:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    if alert.read_at is None:
        alert.read_at = utcnow()
        db.commit()
    return {"id": alert.id, "read_at": alert.read_at}


@router.post("/v1/email/unsubscribe")
def unsubscribe(payload: dict[str, str], db: Session = Depends(get_db)):
    token = payload.get("token", "")
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    now = utcnow()
    row = db.scalar(select(EmailUnsubscribeToken).where(
        EmailUnsubscribeToken.token_hash == token_hash,
        EmailUnsubscribeToken.expires_at > now,
        EmailUnsubscribeToken.consumed_at.is_(None),
    )) if len(token) <= 200 else None
    if row:
        pref = db.scalar(select(NotificationPreference).where(
            NotificationPreference.organization_id == row.organization_id,
            NotificationPreference.user_id == row.user_id,
        ))
        if pref:
            pref.email_enabled = False
            pref.digest_frequency = "off"
            pref.critical_alerts = False
            pref.next_digest_at = None
            pref.updated_at = now
        tokens = db.scalars(select(EmailUnsubscribeToken).where(
            EmailUnsubscribeToken.organization_id == row.organization_id,
            EmailUnsubscribeToken.user_id == row.user_id,
            EmailUnsubscribeToken.consumed_at.is_(None),
        )).all()
        for item in tokens:
            item.consumed_at = now
        db.commit()
    return {"status": "processed", "message": "Se o link era válido, suas notificações foram desativadas."}


@router.post("/v1/email/webhook")
async def mail_webhook(request: Request, payload: WebhookEvent, x_licitagoias_signature: str | None = Header(default=None),
                 db: Session = Depends(get_db)):
    secret = os.getenv("LICITAGOIAS_MAIL_WEBHOOK_SECRET", "")
    if not secret:
        raise HTTPException(status_code=503, detail="Webhook de entrega desativado")
    raw_body = await request.body()
    expected = "sha256=" + hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    if not x_licitagoias_signature or not hmac.compare_digest(expected, x_licitagoias_signature):
        raise HTTPException(status_code=401, detail="Assinatura inválida")
    outbox = db.scalar(select(EmailOutbox).where(EmailOutbox.provider_message_id == payload.message_id))
    event = EmailDeliveryEvent(provider_event_id=payload.provider_event_id,
                               outbox_id=outbox.id if outbox else None,
                               event_type=payload.event_type, occurred_at=payload.occurred_at)
    db.add(event)
    if outbox and payload.event_type in {"bounced", "complained"}:
        user = db.get(User, outbox.user_id)
        if user:
            address = user.email.strip().casefold()
            if db.get(EmailSuppression, address) is None:
                db.add(EmailSuppression(email=address, reason=payload.event_type,
                                        provider_event_id=payload.provider_event_id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
    return {"status": "accepted"}
