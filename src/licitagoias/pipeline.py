from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from licitagoias.classification import classify_opportunities
from licitagoias.cleaning import curate_opportunities, normalize_records
from licitagoias.collectors.pncp import APARECIDA_GOIANIA_IBGE, PNCPCollector
from licitagoias.export import export_package_files
from licitagoias.models import Opportunity
from licitagoias.reporting import ReportPaths, generate_report_files


def process_records(records: list[dict], output_dir: Path) -> list[Path]:
    normalized = normalize_records(records)
    curated = curate_opportunities(normalized)
    classified = classify_opportunities(curated)
    return export_package_files(classified, output_dir)


def process_csv(input_path: Path, output_dir: Path) -> list[Path]:
    df = pd.read_csv(input_path)
    records = df.fillna("").to_dict(orient="records")
    return process_records(records, output_dir)


def collect_recent_aparecida(limit: int = 5, days_back: int = 90) -> list[Opportunity]:
    records = PNCPCollector(municipio_ibge=APARECIDA_GOIANIA_IBGE).collect_recent(
        limit=max(limit * 4, 10), days_back=days_back
    )
    normalized = normalize_records(records)
    curated = curate_opportunities(normalized)
    return sorted(curated, key=lambda item: item.data_fechamento or item.data_abertura or date.min, reverse=True)[:limit]


def generate_recent_aparecida_report(limit: int, days_back: int, output_dir: Path) -> ReportPaths:
    opportunities = collect_recent_aparecida(limit=limit, days_back=days_back)
    return generate_report_files(opportunities, output_dir)
