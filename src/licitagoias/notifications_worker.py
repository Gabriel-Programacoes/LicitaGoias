from __future__ import annotations

import hashlib
import html
import logging
import os
import secrets
import smtplib
import ssl
import time
from datetime import timedelta, timezone
from email.message import EmailMessage
from email.utils import formataddr
from urllib.parse import quote
from zoneinfo import ZoneInfo

from sqlalchemy import select

from licitagoias.phase1_db import (
    EmailOutbox, EmailSuppression, EmailUnsubscribeToken, Membership,
    NotificationPreference, OpportunityAlert, OpportunityRecord, User,
    session_factory, utcnow,
)

logger = logging.getLogger("licitagoias.notifications")
MAX_ATTEMPTS = 8


def _materialize(session) -> None:
    now = utcnow()
    prefs = session.scalars(select(NotificationPreference).where(
        NotificationPreference.email_enabled.is_(True)
    )).all()
    for pref in prefs:
        user = session.get(User, pref.user_id)
        if not user or not user.email_verified or session.get(EmailSuppression, user.email.strip().casefold()):
            continue
        if pref.critical_alerts:
            alerts = session.scalars(select(OpportunityAlert).where(
                OpportunityAlert.organization_id == pref.organization_id,
                OpportunityAlert.severity == "critical",
                OpportunityAlert.created_at > (pref.last_digest_at or pref.created_at),
            )).all()
            for alert in alerts:
                key = f"alert:{pref.id}:{alert.id}"
                if session.scalar(select(EmailOutbox.id).where(EmailOutbox.idempotency_key == key)):
                    continue
                session.add(EmailOutbox(
                    organization_id=pref.organization_id, user_id=pref.user_id,
                    category="alert", idempotency_key=key,
                    payload={"alert_id": alert.id}, status="pending", available_at=now,
                ))
        if pref.digest_frequency == "off" or not pref.next_digest_at or pref.next_digest_at > now:
            continue
        alerts = session.scalars(select(OpportunityAlert).where(
            OpportunityAlert.organization_id == pref.organization_id,
            OpportunityAlert.created_at > (pref.last_digest_at or pref.created_at),
            OpportunityAlert.created_at <= pref.next_digest_at,
            *([OpportunityAlert.severity != "critical"] if pref.critical_alerts else []),
        ).order_by(OpportunityAlert.created_at, OpportunityAlert.id).limit(500)).all()
        if alerts:
            window = pref.next_digest_at.isoformat()
            key = f"digest:{pref.id}:{window}"
            if not session.scalar(select(EmailOutbox.id).where(EmailOutbox.idempotency_key == key)):
                session.add(EmailOutbox(
                    organization_id=pref.organization_id, user_id=pref.user_id,
                    category="digest", idempotency_key=key,
                    payload={"alert_ids": [alert.id for alert in alerts]}, status="pending", available_at=now,
                ))
        pref.last_digest_at = pref.next_digest_at
        local = now.astimezone(ZoneInfo(pref.timezone_name))
        if pref.digest_frequency == "daily":
            candidate = local.replace(hour=pref.digest_hour, minute=0, second=0, microsecond=0)
            if candidate <= local:
                candidate += timedelta(days=1)
        else:
            candidate = local.replace(hour=pref.digest_hour, minute=0, second=0, microsecond=0)
            if candidate <= local:
                candidate += timedelta(days=1)
            while candidate.weekday() != 0:
                candidate += timedelta(days=1)
        pref.next_digest_at = candidate.astimezone(timezone.utc)
        pref.updated_at = now


def _email_enabled() -> bool:
    return (os.getenv("LICITAGOIAS_EMAIL_ENABLED", "false").lower() == "true"
            and os.getenv("LICITAGOIAS_EMAIL_DOMAIN_VERIFIED", "false").lower() == "true")


def _claim(factory) -> str | None:
    with factory.begin() as session:
        now = utcnow()
        row = session.scalar(select(EmailOutbox).where(
            ((EmailOutbox.status == "pending") & (EmailOutbox.available_at <= now)) |
            ((EmailOutbox.status == "processing") & (EmailOutbox.locked_until < now))
        ).order_by(EmailOutbox.available_at, EmailOutbox.created_at).with_for_update(skip_locked=True).limit(1))
        if row is None:
            return None
        row.status = "processing"
        row.locked_until = now + timedelta(minutes=5)
        row.attempt_count += 1
        row.last_attempt_at = now
        return row.id


def _render(session, row: EmailOutbox, user: User, base_url: str) -> EmailMessage:
    ids = row.payload.get("alert_ids", []) if row.category == "digest" else [row.payload.get("alert_id")]
    alerts = session.scalars(select(OpportunityAlert).where(
        OpportunityAlert.id.in_([item for item in ids if item])
    )).all()
    # Only currently enabled email preferences can produce a message.
    pref = session.scalar(select(NotificationPreference).where(
        NotificationPreference.organization_id == row.organization_id,
        NotificationPreference.user_id == user.id,
    ))
    if not pref or not pref.email_enabled or not user.email_verified:
        raise PermissionError("notifications_disabled")
    if row.category == "alert" and (not pref.critical_alerts or any(a.severity != "critical" for a in alerts)):
        raise PermissionError("alert_preference_disabled")
    items = []
    for alert in alerts:
        opportunity = session.get(OpportunityRecord, alert.opportunity_id)
        if not opportunity:
            continue
        title = html.escape(str(opportunity.current_data.get("objeto") or "Oportunidade"))
        source_url = opportunity.current_data.get("link_origem") or opportunity.current_data.get("link_edital")
        source_link = ""
        if isinstance(source_url, str) and source_url.startswith("https://"):
            source_link = f" · <a href=\"{html.escape(source_url, quote=True)}\">fonte oficial</a>"
        items.append(f"<li><strong>{title}</strong> — {html.escape(alert.event_type)}{source_link}</li>")
    if not items:
        raise PermissionError("no_alerts")
    token = secrets.token_urlsafe(32)
    session.add(EmailUnsubscribeToken(
        token_hash=hashlib.sha256(token.encode()).hexdigest(),
        organization_id=row.organization_id, user_id=user.id,
        expires_at=utcnow() + timedelta(days=30),
    ))
    link = base_url.rstrip("/") + "/unsubscribe?token=" + quote(token)
    message = EmailMessage()
    message["Subject"] = "LicitaGoias: atualizações de oportunidades" if row.category == "digest" else "LicitaGoias: alteração em oportunidade acompanhada"
    sender = os.environ["LICITAGOIAS_EMAIL_FROM"].strip()
    message["From"] = formataddr((os.getenv("LICITAGOIAS_EMAIL_FROM_NAME", "LicitaGoias"), sender))
    message["To"] = user.email
    domain = sender.rsplit("@", 1)[-1] if "@" in sender else "invalid.local"
    message["Message-ID"] = f"<{hashlib.sha256(row.idempotency_key.encode()).hexdigest()}@{domain}>"
    app_link = html.escape(base_url.rstrip("/") + "/app#alerts", quote=True)
    message.set_content("Há atualizações em oportunidades acompanhadas. Acesse o LicitaGoias para ver os detalhes. Confira sempre o edital e a situação no portal oficial.")
    message.add_alternative(
        "<html><body><h1>Atualizações de oportunidades</h1><ul>" + "".join(items) +
        f"</ul><p><a href=\"{app_link}\">Ver meus alertas no LicitaGoias</a></p>"
        f"<p>Confirme sempre o edital e a situação no portal oficial. <a href=\"{html.escape(link, quote=True)}\">Cancelar notificações por e-mail</a></p></body></html>",
        subtype="html",
    )
    return message


def _smtp_send(message: EmailMessage) -> None:
    host = os.getenv("LICITAGOIAS_EMAIL_HOST", "").strip()
    port = int(os.getenv("LICITAGOIAS_EMAIL_PORT", "587"))
    if not host or not os.getenv("LICITAGOIAS_EMAIL_FROM", "").strip():
        raise RuntimeError("smtp_configuration_missing")
    context = ssl.create_default_context()
    with smtplib.SMTP(host, port, timeout=20) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.ehlo()
        username = os.getenv("LICITAGOIAS_EMAIL_USERNAME", "")
        password = os.getenv("LICITAGOIAS_EMAIL_PASSWORD", "")
        if username:
            smtp.login(username, password)
        smtp.send_message(message)


def process_one(factory) -> bool:
    if not _email_enabled():
        return False
    row_id = _claim(factory)
    if not row_id:
        return False
    try:
        with factory.begin() as session:
            row = session.get(EmailOutbox, row_id)
            user = session.get(User, row.user_id)
            address = user.email.strip().casefold() if user else ""
            if not user or session.get(EmailSuppression, address):
                row.status, row.last_error, row.locked_until = "suppressed", "recipient_suppressed", None
                return True
            message = _render(session, row, user, os.getenv("LICITAGOIAS_APP_BASE_URL", "http://127.0.0.1:8000"))
            message_id = message["Message-ID"]
        _smtp_send(message)
        with factory.begin() as session:
            row = session.get(EmailOutbox, row_id)
            row.status, row.sent_at, row.provider_message_id = "sent", utcnow(), message_id
            row.locked_until = None
        return True
    except PermissionError as exc:
        with factory.begin() as session:
            row = session.get(EmailOutbox, row_id)
            row.status, row.last_error, row.locked_until = "suppressed", str(exc)[:160], None
        return True
    except Exception as exc:
        # Keep server responses, addresses, and message bodies out of persistent logs.
        with factory.begin() as session:
            row = session.get(EmailOutbox, row_id)
            if row.attempt_count >= MAX_ATTEMPTS:
                row.status = "dead"
            else:
                row.status = "pending"
                row.available_at = utcnow() + timedelta(seconds=min(3600, 30 * (2 ** (row.attempt_count - 1))))
            row.last_error = type(exc).__name__[:160]
            row.locked_until = None
        logger.warning("email_delivery_failed outbox=%s error_type=%s", row_id, type(exc).__name__)
        return True


def run_worker(once: bool = False) -> None:
    factory = session_factory()
    while True:
        with factory.begin() as session:
            _materialize(session)
        did_work = process_one(factory)
        if once:
            return
        if not did_work:
            time.sleep(max(1, int(os.getenv("LICITAGOIAS_EMAIL_POLL_SECONDS", "30"))))


def main() -> None:
    import argparse
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    parser = argparse.ArgumentParser(description="Worker de notificações do LicitaGoias")
    parser.add_argument("--once", action="store_true", help="Executa um ciclo e encerra")
    args = parser.parse_args()
    run_worker(once=args.once)


if __name__ == "__main__":
    main()
