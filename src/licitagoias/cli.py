from __future__ import annotations

import argparse
from pathlib import Path

from licitagoias.formatting import format_opportunity_line
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
    return parser


def main() -> None:
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


if __name__ == "__main__":
    main()
