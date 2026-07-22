from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd

from licitagoias.models import Opportunity

CANCELLED_STATUS_TERMS = {
    "cancelada",
    "cancelado",
    "suspensa",
    "suspenso",
    "revogada",
    "revogado",
    "anulada",
    "anulado",
    "fracassada",
    "fracassado",
    "deserta",
    "deserto",
}


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def clean_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def parse_brazilian_date(value: Any) -> date | None:
    text = clean_text(value)
    if not text:
        return None

    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y"):
        try:
            return datetime.strptime(text[:10], fmt).date()
        except ValueError:
            continue
    return None


def parse_brazilian_money(value: Any) -> Decimal | None:
    text = clean_text(value)
    if not text:
        return None

    text = re.sub(r"[^\d,.-]", "", text)
    if not text:
        return None

    if "," in text:
        text = text.replace(".", "").replace(",", ".")

    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def is_cancelled_status(status: Any) -> bool:
    normalized = strip_accents(clean_text(status).lower())
    return any(term in normalized for term in CANCELLED_STATUS_TERMS)


def normalize_record(record: dict[str, Any]) -> Opportunity:
    opportunity = Opportunity(
        orgao_comprador=clean_text(record.get("orgao_comprador") or record.get("orgao") or record.get("unidade")),
        objeto=clean_text(record.get("objeto") or record.get("descricao")),
        data_abertura=parse_brazilian_date(record.get("data_abertura") or record.get("abertura")),
        data_fechamento=parse_brazilian_date(record.get("data_fechamento") or record.get("fechamento")),
        valor_estimado=parse_brazilian_money(record.get("valor_estimado") or record.get("valor")),
        link_edital=clean_text(record.get("link_edital") or record.get("edital")),
        fonte=clean_text(record.get("fonte")),
        municipio=clean_text(record.get("municipio")),
        uf=clean_text(record.get("uf")) or "GO",
        modalidade=clean_text(record.get("modalidade")),
        status=clean_text(record.get("status")),
        numero_processo=clean_text(record.get("numero_processo") or record.get("processo")),
        data_coleta=datetime.utcnow(),
        link_origem=clean_text(record.get("link_origem") or record.get("url")),
        texto_bruto=clean_text(record.get("texto_bruto")),
    )
    return opportunity.with_hash()


def normalize_records(records: Iterable[dict[str, Any]]) -> list[Opportunity]:
    return [normalize_record(record) for record in records]


def curate_opportunities(opportunities: Iterable[Opportunity]) -> list[Opportunity]:
    unique: dict[str, Opportunity] = {}
    for opportunity in opportunities:
        if is_cancelled_status(opportunity.status):
            continue
        if not (opportunity.link_edital or opportunity.link_origem):
            continue
        if not opportunity.orgao_comprador or not opportunity.objeto:
            continue
        unique.setdefault(opportunity.hash_deduplicacao, opportunity)
    return list(unique.values())
