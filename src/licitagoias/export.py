from __future__ import annotations

from pathlib import Path

import pandas as pd

from licitagoias.models import Opportunity

EXPORT_COLUMNS = [
    "pacote",
    "orgao_comprador",
    "objeto",
    "data_abertura",
    "data_fechamento",
    "valor_estimado",
    "link_edital",
    "fonte",
    "municipio",
    "status",
    "numero_processo",
    "link_origem",
]


def opportunities_to_dataframe(opportunities: list[Opportunity]) -> pd.DataFrame:
    rows = [opportunity.to_dict() for opportunity in opportunities]
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=EXPORT_COLUMNS)
    return df.reindex(columns=EXPORT_COLUMNS)


def export_package_files(opportunities: list[Opportunity], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    df = opportunities_to_dataframe(opportunities)
    written: list[Path] = []

    all_csv = output_dir / "oportunidades_curadas.csv"
    all_xlsx = output_dir / "oportunidades_curadas.xlsx"
    df.to_csv(all_csv, index=False, encoding="utf-8-sig")
    df.to_excel(all_xlsx, index=False)
    written.extend([all_csv, all_xlsx])

    if df.empty:
        return written

    for package in sorted(df["pacote"].dropna().unique()):
        package_df = df[df["pacote"] == package]
        csv_path = output_dir / f"pacote_{package}.csv"
        xlsx_path = output_dir / f"pacote_{package}.xlsx"
        package_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        package_df.to_excel(xlsx_path, index=False)
        written.extend([csv_path, xlsx_path])

    return written
