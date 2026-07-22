from __future__ import annotations

import sqlite3
from pathlib import Path

from licitagoias.models import Opportunity


SCHEMA = """
CREATE TABLE IF NOT EXISTS opportunities (
  hash_deduplicacao TEXT PRIMARY KEY,
  orgao_comprador TEXT NOT NULL,
  objeto TEXT NOT NULL,
  data_abertura TEXT,
  data_fechamento TEXT,
  valor_estimado TEXT,
  link_edital TEXT,
  fonte TEXT,
  municipio TEXT,
  uf TEXT,
  modalidade TEXT,
  status TEXT,
  numero_processo TEXT,
  data_coleta TEXT,
  link_origem TEXT,
  texto_bruto TEXT
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute(SCHEMA)
    return connection


def upsert_opportunities(connection: sqlite3.Connection, opportunities: list[Opportunity]) -> int:
    rows = [opportunity.to_dict() for opportunity in opportunities]
    if not rows:
        return 0

    connection.executemany(
        """
        INSERT OR REPLACE INTO opportunities (
          hash_deduplicacao, orgao_comprador, objeto, data_abertura, data_fechamento,
          valor_estimado, link_edital, fonte, municipio, uf, modalidade, status,
          numero_processo, data_coleta, link_origem, texto_bruto
        ) VALUES (
          :hash_deduplicacao, :orgao_comprador, :objeto, :data_abertura, :data_fechamento,
          :valor_estimado, :link_edital, :fonte, :municipio, :uf, :modalidade, :status,
          :numero_processo, :data_coleta, :link_origem, :texto_bruto
        )
        """,
        rows,
    )
    connection.commit()
    return len(rows)
