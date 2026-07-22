from __future__ import annotations

from datetime import date
from decimal import Decimal

from licitagoias.cleaning import parse_brazilian_date
from licitagoias.models import Opportunity

MAX_OBJECT_LENGTH = 180


def format_money(value: Decimal | None) -> str:
    if value is None:
        return "Valor nao informado"
    formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def format_date(value: date | None) -> str:
    if value is None:
        return "Data nao informada"
    return value.strftime("%d/%m/%Y")


def format_opportunity_line(opportunity: Opportunity) -> str:
    date_value = opportunity.data_fechamento or opportunity.data_abertura
    return f"{shorten_object(opportunity.objeto)} + {format_money(opportunity.valor_estimado)} + {format_date(date_value)}"


def format_raw_recent_line(record: dict) -> str:
    date_value = parse_brazilian_date(record.get("data_fechamento") or record.get("data_abertura"))
    value = record.get("valor_estimado")
    money = Decimal(str(value)) if value not in (None, "") else None
    return f"{shorten_object(record.get('objeto', ''))} + {format_money(money)} + {format_date(date_value)}"


def shorten_object(value: str, max_length: int = MAX_OBJECT_LENGTH) -> str:
    text = "".join(char if char.isprintable() else " " for char in str(value))
    text = " ".join(text.split())
    if len(text) <= max_length:
        return text
    return f"{text[: max_length - 3].rstrip()}..."
