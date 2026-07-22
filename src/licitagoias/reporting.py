from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path

from licitagoias.classification import classify_text
from licitagoias.formatting import format_date, format_money, shorten_object
from licitagoias.models import Opportunity


PACKAGE_LABELS = {
    "obras": "Obras",
    "saude": "Saude",
    "eventos_alimentacao": "Eventos/Alimentacao",
    "tecnologia": "Tecnologia",
    "sem_pacote": "Geral",
}


@dataclass(frozen=True)
class ReportPaths:
    html: Path
    whatsapp: Path


def infer_package(opportunity: Opportunity) -> str:
    if opportunity.pacote:
        return opportunity.pacote
    return classify_text(opportunity.objeto)[0]


def deadline_label(opportunity: Opportunity, today: date | None = None) -> str:
    current = today or date.today()
    target = opportunity.data_fechamento or opportunity.data_abertura
    if target is None:
        return "Sem prazo informado"

    days = (target - current).days
    if days < 0:
        return "Prazo encerrado"
    if days == 0:
        return "Fecha hoje"
    if days == 1:
        return "Fecha amanha"
    return f"Fecha em {days} dias"


def generate_report_files(
    opportunities: list[Opportunity],
    output_dir: Path,
    title: str = "Licitacoes em Aparecida de Goiania",
    today: date | None = None,
) -> ReportPaths:
    output_dir.mkdir(parents=True, exist_ok=True)
    current = today or date.today()
    sorted_items = sorted(opportunities, key=lambda item: item.data_fechamento or item.data_abertura or date.min)

    html_path = output_dir / "relatorio_aparecida.html"
    whatsapp_path = output_dir / "whatsapp_aparecida.txt"
    html_path.write_text(render_html_report(sorted_items, title, current), encoding="utf-8")
    whatsapp_path.write_text(render_whatsapp_report(sorted_items, title, current), encoding="utf-8")
    return ReportPaths(html=html_path, whatsapp=whatsapp_path)


def render_whatsapp_report(opportunities: list[Opportunity], title: str, today: date | None = None) -> str:
    current = today or date.today()
    lines = [f"{title} - {format_date(current)}", ""]
    for index, opportunity in enumerate(opportunities, start=1):
        close_date = opportunity.data_fechamento or opportunity.data_abertura
        package = PACKAGE_LABELS.get(infer_package(opportunity), "Geral")
        lines.extend(
            [
                f"{index}. {shorten_object(opportunity.objeto, 220)}",
                f"Valor: {format_money(opportunity.valor_estimado)}",
                f"Data: {format_date(close_date)} ({deadline_label(opportunity, current)})",
                f"Orgao: {opportunity.orgao_comprador}",
                f"Pacote: {package}",
                f"Link: {opportunity.link_edital or opportunity.link_origem}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def render_html_report(opportunities: list[Opportunity], title: str, today: date | None = None) -> str:
    current = today or date.today()
    package_counts = Counter(infer_package(opportunity) for opportunity in opportunities)
    total_value = sum((opportunity.valor_estimado for opportunity in opportunities if opportunity.valor_estimado), start=0)

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #182026;
      --muted: #62707d;
      --line: #d7dde3;
      --paper: #f7f8f6;
      --panel: #ffffff;
      --accent: #0f766e;
      --warn: #b45309;
      --good: #2563eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
    }}
    main {{
      max-width: 1160px;
      margin: 0 auto;
      padding: 28px 18px 40px;
    }}
    header {{
      display: grid;
      gap: 10px;
      margin-bottom: 22px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 18px;
    }}
    h1 {{
      margin: 0;
      font-size: 30px;
      letter-spacing: 0;
    }}
    .meta {{
      color: var(--muted);
      font-size: 14px;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin: 20px 0 22px;
    }}
    .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
    }}
    .metric strong {{
      display: block;
      margin-top: 5px;
      font-size: 22px;
    }}
    .package-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 18px;
    }}
    .chip {{
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--panel);
      padding: 7px 10px;
      font-size: 13px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    article {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      display: grid;
      gap: 12px;
    }}
    .topline {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
    }}
    .badge {{
      flex: 0 0 auto;
      border-radius: 999px;
      padding: 5px 8px;
      background: #e6f4f1;
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
    }}
    h2 {{
      margin: 0;
      font-size: 17px;
      letter-spacing: 0;
    }}
    dl {{
      display: grid;
      grid-template-columns: 110px 1fr;
      gap: 6px 10px;
      margin: 0;
      font-size: 14px;
    }}
    dt {{ color: var(--muted); }}
    dd {{ margin: 0; }}
    a {{ color: var(--good); overflow-wrap: anywhere; }}
    .deadline {{
      color: var(--warn);
      font-weight: 700;
    }}
    .whatsapp {{
      margin-top: 24px;
      background: #eef6ff;
      border: 1px solid #bdd7ff;
      border-radius: 8px;
      padding: 14px;
      color: #1f3554;
      font-size: 14px;
    }}
    @media (max-width: 760px) {{
      main {{ padding: 18px 12px 28px; }}
      h1 {{ font-size: 24px; }}
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .grid {{ grid-template-columns: 1fr; }}
      dl {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>{escape(title)}</h1>
      <div class="meta">Atualizado em {escape(format_date(current))} - Fonte: PNCP / Aparecida de Goiania</div>
    </header>
    {render_summary(opportunities, package_counts, total_value)}
    {render_package_chips(package_counts)}
    <section class="grid" aria-label="Oportunidades">
      {"".join(render_opportunity_card(opportunity, current) for opportunity in opportunities)}
    </section>
    <section class="whatsapp">
      Arquivo pronto para envio manual: <strong>whatsapp_aparecida.txt</strong>
    </section>
  </main>
</body>
</html>
"""


def render_summary(opportunities: list[Opportunity], package_counts: Counter, total_value: int) -> str:
    with_value = sum(1 for opportunity in opportunities if opportunity.valor_estimado is not None)
    return f"""
    <section class="summary" aria-label="Resumo">
      <div class="metric"><span>Oportunidades</span><strong>{len(opportunities)}</strong></div>
      <div class="metric"><span>Valor mapeado</span><strong>{escape(format_money(total_value))}</strong></div>
      <div class="metric"><span>Com valor</span><strong>{with_value}</strong></div>
      <div class="metric"><span>Pacotes</span><strong>{len(package_counts)}</strong></div>
    </section>
"""


def render_package_chips(package_counts: Counter) -> str:
    chips = []
    for package, count in sorted(package_counts.items(), key=lambda item: PACKAGE_LABELS.get(item[0], item[0])):
        label = PACKAGE_LABELS.get(package, "Geral")
        chips.append(f'<span class="chip">{escape(label)}: {count}</span>')
    return f'<section class="package-row" aria-label="Pacotes">{"".join(chips)}</section>'


def render_opportunity_card(opportunity: Opportunity, today: date) -> str:
    close_date = opportunity.data_fechamento or opportunity.data_abertura
    link = opportunity.link_edital or opportunity.link_origem
    package = PACKAGE_LABELS.get(infer_package(opportunity), "Geral")
    return f"""
      <article>
        <div class="topline">
          <h2>{escape(shorten_object(opportunity.objeto, 220))}</h2>
          <span class="badge">{escape(package)}</span>
        </div>
        <dl>
          <dt>Valor</dt><dd>{escape(format_money(opportunity.valor_estimado))}</dd>
          <dt>Data</dt><dd>{escape(format_date(close_date))} <span class="deadline">{escape(deadline_label(opportunity, today))}</span></dd>
          <dt>Orgao</dt><dd>{escape(opportunity.orgao_comprador)}</dd>
          <dt>Modalidade</dt><dd>{escape(opportunity.modalidade or "Nao informada")}</dd>
          <dt>Link</dt><dd><a href="{escape(link)}">{escape(link)}</a></dd>
        </dl>
      </article>
"""
