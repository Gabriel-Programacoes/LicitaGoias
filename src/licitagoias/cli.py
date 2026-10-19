from __future__ import annotations

import argparse
import logging
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy import select

from licitagoias.collectors.pncp import DEFAULT_MODALIDADE_CODES, PNCPCollector
from licitagoias.formatting import format_opportunity_line
from licitagoias.phase1_db import CollectionProgress, CollectionRun, OpportunityRecord, OpportunityVersion, session_factory
from licitagoias.phase1_ingestion import import_legacy, sync_pncp
from licitagoias.pipeline import collect_recent_aparecida, generate_recent_aparecida_report, process_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="licitagoias")
    subparsers = parser.add_subparsers(dest="command", required=True)

    process = subparsers.add_parser("process", help="Processa um CSV bruto e exporta planilhas curadas.")
    process.add_argument("--input", required=True, type=Path, help="Caminho do CSV bruto.")
    process.add_argument("--output-dir", required=True, type=Path, help="Diretorio de saida.")

    recent = subparsers.add_parser("recent-aparecida", help="Lista licitacoes recentes de Aparecida de Goiania.")
    recent.add_argument("--limit", type=int, default=5, help="Quantidade de oportunidades.")
    recent.add_argument("--days-back", type=int, default=90, help="Janela de busca em dias.")

    report = subparsers.add_parser("report-aparecida", help="Gera relatorio HTML e texto para WhatsApp.")
    report.add_argument("--limit", type=int, default=12, help="Quantidade de oportunidades.")
    report.add_argument("--days-back", type=int, default=90, help="Janela de busca em dias.")
    report.add_argument("--output-dir", type=Path, default=Path("data/reports"), help="Diretorio de saida.")

    sync = subparsers.add_parser("sync-pncp", help="Coleta PNCP e grava no PostgreSQL.")
    sync.add_argument("--municipio-ibge", default=None, help="Código IBGE; sem este filtro, coleta todo o estado selecionado.")
    sync.add_argument("--uf", default="GO")
    sync.add_argument("--start", type=date.fromisoformat, default=date.today() - timedelta(days=30))
    sync.add_argument("--end", type=date.fromisoformat, default=date.today())
    sync.add_argument("--modalidades", default=",".join(map(str, DEFAULT_MODALIDADE_CODES)), help="Códigos PNCP separados por vírgula.")
    sync.add_argument("--resume-run", help="ID da execucao parcial a retomar com os mesmos parametros.")

    runs = subparsers.add_parser("collection-runs", help="Lista execucoes e progresso de coleta.")
    runs.add_argument("--limit", type=int, default=20)

    history = subparsers.add_parser("opportunity-history", help="Exibe versoes de um identificador de fonte.")
    history.add_argument("--source", default="PNCP")
    history.add_argument("--external-id", required=True)

    legacy = subparsers.add_parser("import-legacy-sqlite", help="Importa uma base SQLite antiga em modo somente leitura.")
    legacy.add_argument("--input", required=True, type=Path)
    return parser


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    args = build_parser().parse_args()
    if args.command == "process":
        written = process_csv(args.input, args.output_dir)
        for path in written:
            print(path)
    elif args.command == "recent-aparecida":
        opportunities = collect_recent_aparecida(limit=args.limit, days_back=args.days_back)
        if not opportunities:
            print("Nenhuma oportunidade encontrada para Aparecida de Goiania na janela informada.")
            return
        for opportunity in opportunities:
            print(format_opportunity_line(opportunity))
    elif args.command == "report-aparecida":
        paths = generate_recent_aparecida_report(
            limit=args.limit,
            days_back=args.days_back,
            output_dir=args.output_dir,
        )
        print(paths.html)
        print(paths.whatsapp)
    elif args.command == "sync-pncp":
        modalidades = tuple(int(value.strip()) for value in args.modalidades.split(",") if value.strip())
        collector = PNCPCollector(municipio_ibge=args.municipio_ibge, uf=args.uf, modalidades=modalidades)
        run = sync_pncp(collector, args.start, args.end, args.resume_run)
        print(f"{run.id} {run.status}")
    elif args.command == "collection-runs":
        with session_factory()() as session:
            runs = session.scalars(select(CollectionRun).order_by(CollectionRun.started_at.desc()).limit(args.limit)).all()
            for run in runs:
                progress = session.scalars(select(CollectionProgress).where(CollectionProgress.run_id == run.id)).all()
                parts = ", ".join(f"{item.segment}:{item.last_page}/{item.total_pages or '?'}" for item in progress)
                scope = run.municipality_code or f"todo {run.uf}"
                print(f"{run.id} {run.status} {scope} {run.start_date}..{run.end_date} {parts} {run.error or ''}")
    elif args.command == "opportunity-history":
        with session_factory()() as session:
            record = session.scalar(select(OpportunityRecord).where(
                OpportunityRecord.source == args.source, OpportunityRecord.external_id == args.external_id
            ))
            if record is None:
                raise SystemExit("Oportunidade não encontrada")
            print(f"{record.id} {record.identity_method} review={record.review_required}")
            versions = session.scalars(select(OpportunityVersion).where(
                OpportunityVersion.opportunity_id == record.id
            ).order_by(OpportunityVersion.observed_at, OpportunityVersion.id)).all()
            for version in versions:
                print(f"{version.observed_at} {version.previous_hash or '-'} -> {version.content_hash} {version.data}")
    elif args.command == "import-legacy-sqlite":
        print(import_legacy(args.input))


if __name__ == "__main__":
    main()
