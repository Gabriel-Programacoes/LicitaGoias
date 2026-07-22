from datetime import date
from decimal import Decimal

from licitagoias.models import Opportunity
from licitagoias.reporting import deadline_label, render_html_report, render_whatsapp_report


def test_deadline_label() -> None:
    opportunity = Opportunity(
        orgao_comprador="Municipio",
        objeto="Aquisicao de medicamentos",
        data_fechamento=date(2026, 7, 12),
        link_edital="https://example.test",
    )

    assert deadline_label(opportunity, date(2026, 7, 10)) == "Fecha em 2 dias"


def test_render_reports_include_product_fields() -> None:
    opportunity = Opportunity(
        orgao_comprador="Municipio de Aparecida de Goiania",
        objeto="Aquisicao de medicamentos",
        data_fechamento=date(2026, 7, 12),
        valor_estimado=Decimal("1000.50"),
        link_edital="https://example.test",
        modalidade="Pregao",
    )

    html = render_html_report([opportunity], "Relatorio", date(2026, 7, 10))
    whatsapp = render_whatsapp_report([opportunity], "Relatorio", date(2026, 7, 10))

    assert "Aquisicao de medicamentos" in html
    assert "R$ 1.000,50" in html
    assert "Pacote:" in whatsapp
    assert "Link: https://example.test" in whatsapp
