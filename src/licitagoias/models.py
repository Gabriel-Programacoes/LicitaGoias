from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
from typing import Any


@dataclass(slots=True)
class Opportunity:
    orgao_comprador: str
    objeto: str
    data_abertura: date | None = None
    data_fechamento: date | None = None
    valor_estimado: Decimal | None = None
    link_edital: str = ""
    fonte: str = ""
    municipio: str = ""
    uf: str = "GO"
    modalidade: str = ""
    status: str = ""
    numero_processo: str = ""
    data_coleta: datetime | None = None
    hash_deduplicacao: str = ""
    link_origem: str = ""
    texto_bruto: str = ""
    pacote: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["data_abertura"] = self.data_abertura.isoformat() if self.data_abertura else ""
        payload["data_fechamento"] = self.data_fechamento.isoformat() if self.data_fechamento else ""
        payload["valor_estimado"] = str(self.valor_estimado) if self.valor_estimado is not None else ""
        payload["data_coleta"] = self.data_coleta.isoformat() if self.data_coleta else ""
        return payload

    def with_hash(self) -> "Opportunity":
        key_parts = [
            self.fonte,
            self.orgao_comprador,
            self.numero_processo,
            self.objeto,
            self.data_abertura.isoformat() if self.data_abertura else "",
            self.data_fechamento.isoformat() if self.data_fechamento else "",
            self.link_edital or self.link_origem,
        ]
        self.hash_deduplicacao = sha256("|".join(key_parts).lower().encode("utf-8")).hexdigest()
        return self
