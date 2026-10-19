from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from licitagoias.cleaning import strip_accents
from licitagoias.collectors.pncp import PNCPCollector
from licitagoias.phase1_db import (
    CollectionPageLog, CollectionProgress, CollectionRun, OpportunityRecord, OpportunityVersion,
    OpportunityAlert, OpportunityFollow, SourceSnapshot, session_factory, utcnow,
)

logger = logging.getLogger(__name__)


def digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def date_field(value: Any) -> dict[str, Any]:
    if value is None or value == "":
        return {"raw": None, "iso": None, "precision": None, "timezone_known": False}
    raw = str(value).strip()
    parsed: date | datetime
    try:
        if "T" in raw or " " in raw:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            precision = "datetime"
        else:
            parsed = date.fromisoformat(raw)
            precision = "date"
    except ValueError:
        return {"raw": raw, "iso": None, "precision": "invalid", "timezone_known": False}
    return {
        "raw": raw,
        "iso": parsed.isoformat(),
        "precision": precision,
        "timezone_known": isinstance(parsed, datetime) and parsed.tzinfo is not None,
    }


def normalized_data(record: dict[str, Any]) -> dict[str, Any]:
    value = record.get("valor_estimado")
    try:
        money = str(Decimal(str(value))) if value is not None and str(value).strip() else None
    except InvalidOperation:
        money = None
    fields = (
        "orgao_comprador", "objeto", "informacao_complementar", "link_edital", "link_origem", "municipio",
        "uf", "modalidade", "modalidade_codigo", "status", "numero_processo", "external_id",
    )
    data = {key: record.get(key) for key in fields}
    data["data_publicacao"] = date_field(record.get("data_publicacao"))
    data["data_abertura"] = date_field(record.get("data_abertura"))
    data["data_fechamento"] = date_field(record.get("data_fechamento"))
    data["valor_estimado"] = {"raw": value, "decimal": money, "natureza": "total_estimado" if money else "desconhecido"}
    return data


def identity(record: dict[str, Any], raw: dict[str, Any]) -> tuple[str, str, bool]:
    official = str(record.get("external_id") or "").strip()
    if official:
        return official, "official", False
    parts = [
        str(record.get("orgao_cnpj") or "").strip(),
        str(record.get("numero_processo") or "").strip(),
        str(record.get("ano_compra") or "").strip(),
        str(record.get("unidade_codigo") or "").strip(),
    ]
    if all(parts):
        return "fallback:" + digest(parts), "orgao_processo_ano_unidade", True
    return "unresolved:" + digest(raw), "raw_hash", True


def derived_state(status: str | None) -> str:
    value = strip_accents((status or "").lower())
    if "suspens" in value:
        return "suspended"
    if any(term in value for term in ("cancel", "revog", "anulad", "fracassad", "desert")):
        return "closed"
    return "unknown"


def save_record(session: Session, source: str, raw: dict, record: dict, run_id: str | None) -> None:
    external_id, method, review = identity(record, raw)
    if source == "legacy_sqlite":
        method, review = "legacy_hash", True
    data = normalized_data(record)
    content_hash = digest(data)
    raw_hash = digest(raw)
    now = utcnow()
    opportunity = session.scalar(select(OpportunityRecord).where(
        OpportunityRecord.source == source, OpportunityRecord.external_id == external_id
    ))
    if opportunity is None:
        opportunity = OpportunityRecord(
            source=source, external_id=external_id, identity_method=method,
            review_required=review, official_status=record.get("status"),
            derived_state=derived_state(record.get("status")),
            current_hash=content_hash, current_data=data,
            first_observed_at=now, last_observed_at=now,
        )
        session.add(opportunity)
        session.flush()
        session.add(OpportunityVersion(
            opportunity_id=opportunity.id, content_hash=content_hash,
            data=data, previous_hash=None, observed_at=now, run_id=run_id,
        ))
    else:
        if opportunity.current_hash != content_hash:
            previous_data = opportunity.current_data
            version = OpportunityVersion(
                opportunity_id=opportunity.id, content_hash=content_hash,
                data=data, previous_hash=opportunity.current_hash,
                observed_at=now, run_id=run_id,
            )
            session.add(version)
            session.flush()
            if version.previous_hash is not None:
                follows = session.scalars(select(OpportunityFollow).where(
                    OpportunityFollow.opportunity_id == opportunity.id
                )).all()
                keys = sorted(set(previous_data) | set(data))
                changes = {key: {"before": previous_data.get(key), "after": data.get(key)}
                           for key in keys if previous_data.get(key) != data.get(key)}
                if follows and changes:
                    changed_fields = set(changes)
                    severity = "critical" if changed_fields & {"status", "data_fechamento"} else "informational"
                    if "status" in changed_fields:
                        status_text = strip_accents(str(record.get("status") or "").casefold())
                        event_type = ("opportunity_suspended" if "suspens" in status_text else
                                      "opportunity_closed" if any(word in status_text for word in ("cancel", "revog", "anulad", "fracassad", "desert"))
                                      else "status_changed")
                    else:
                        event_type = "deadline_changed" if "data_fechamento" in changed_fields else "opportunity_updated"
                    for follow in follows:
                        key = digest([follow.organization_id, opportunity.id, version.id])
                        session.add(OpportunityAlert(
                            organization_id=follow.organization_id, opportunity_id=opportunity.id,
                            version_id=version.id, event_type=event_type, severity=severity,
                            changes=changes, idempotency_key=key,
                        ))
            opportunity.current_hash = content_hash
            opportunity.current_data = data
        opportunity.official_status = record.get("status")
        opportunity.derived_state = derived_state(record.get("status"))
        opportunity.last_observed_at = now
    snapshot = session.scalar(select(SourceSnapshot).where(
        SourceSnapshot.opportunity_id == opportunity.id, SourceSnapshot.raw_hash == raw_hash
    ))
    if snapshot is None:
        session.add(SourceSnapshot(
            opportunity_id=opportunity.id, raw_hash=raw_hash,
            raw_data=raw, first_observed_at=now, last_observed_at=now, run_id=run_id,
        ))
    else:
        snapshot.last_observed_at = now


def sync_pncp(
    collector: PNCPCollector, start_date: date, end_date: date, resume_run_id: str | None = None
) -> CollectionRun:
    if start_date > end_date:
        raise ValueError("Janela de datas inválida")
    factory = session_factory()
    with factory.begin() as session:
        if resume_run_id:
            run = session.get(CollectionRun, resume_run_id)
            if run is None or run.source != "PNCP":
                raise ValueError("Execução PNCP não encontrada")
            if (run.municipality_code, run.uf, run.start_date, run.end_date, run.segments) != (
                collector.municipio_ibge, collector.uf, start_date, end_date, list(collector.segments())
            ):
                raise ValueError("Parâmetros diferentes da execução original")
            if run.status == "complete":
                return run
            run.status, run.error, run.finished_at = "running", None, None
        else:
            run = CollectionRun(
                source="PNCP", municipality_code=collector.municipio_ibge,
                uf=collector.uf, start_date=start_date, end_date=end_date,
                segments=list(collector.segments()), status="running",
            )
            session.add(run)
            session.flush()
        run_id = run.id

    try:
        for segment in collector.segments():
            with factory.begin() as session:
                progress = session.scalar(select(CollectionProgress).where(
                    CollectionProgress.run_id == run_id, CollectionProgress.segment == segment
                ))
                if progress is None:
                    progress = CollectionProgress(run_id=run_id, segment=segment, last_page=0, record_count=0, complete=False)
                    session.add(progress)
                    session.flush()
                start_page = progress.last_page + 1
                complete = progress.complete
            if complete:
                continue
            for page in collector.iter_pages(segment, start_date, end_date, start_page):
                with factory.begin() as session:
                    progress = session.scalar(select(CollectionProgress).where(
                        CollectionProgress.run_id == run_id, CollectionProgress.segment == segment
                    ).with_for_update())
                    if page.page <= progress.last_page:
                        continue
                    for raw in page.records:
                        save_record(session, "PNCP", raw, collector.map_item(raw), run_id)
                    session.add(CollectionPageLog(
                        run_id=run_id, segment=segment, page=page.page,
                        total_pages=page.total_pages, record_count=len(page.records), observed_at=utcnow(),
                    ))
                    progress.last_page = page.page
                    progress.total_pages = page.total_pages
                    progress.record_count += len(page.records)
                    progress.complete = page.page == page.total_pages
                logger.info("collection_page run=%s segment=%s page=%s count=%s", run_id, segment, page.page, len(page.records))
        with factory.begin() as session:
            run = session.get(CollectionRun, run_id)
            run.status, run.finished_at = "complete", utcnow()
            return run
    except Exception as exc:
        logger.exception("collection_failed run=%s", run_id)
        with factory.begin() as session:
            run = session.get(CollectionRun, run_id)
            completed = session.scalar(select(func.count()).select_from(CollectionProgress).where(
                CollectionProgress.run_id == run_id, CollectionProgress.last_page > 0
            ))
            run.status = "partial" if completed else "failed"
            run.error = str(exc)[:2000]
            run.finished_at = utcnow()
        raise


def import_legacy(db_path: Path) -> dict[str, int]:
    source_path = db_path.resolve()
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    source = sqlite3.connect(source_path.as_uri() + "?mode=ro", uri=True)
    source.row_factory = sqlite3.Row
    factory = session_factory()
    counts = {"read": 0, "imported": 0, "conflicts": 0}
    try:
        for row in source.execute("SELECT * FROM opportunities"):
            counts["read"] += 1
            raw = dict(row)
            legacy_hash = raw.get("hash_deduplicacao")
            if not legacy_hash:
                counts["conflicts"] += 1
                continue
            record = dict(raw)
            record["external_id"] = "sqlite:" + str(legacy_hash)
            with factory.begin() as session:
                existing = session.scalar(select(OpportunityRecord).where(
                    OpportunityRecord.source == "legacy_sqlite",
                    OpportunityRecord.external_id == record["external_id"],
                ))
                if existing:
                    if existing.current_hash != digest(normalized_data(record)):
                        counts["conflicts"] += 1
                    continue
                save_record(session, "legacy_sqlite", raw, record, None)
                counts["imported"] += 1
    finally:
        source.close()
    return counts
