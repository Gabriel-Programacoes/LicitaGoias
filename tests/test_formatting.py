from datetime import date
from decimal import Decimal

from licitagoias.formatting import format_date, format_money, format_opportunity_line, shorten_object
from licitagoias.models import Opportunity


def test_format_money_brazilian() -> None:
    assert format_money(Decimal("49979.82")) == "R$ 49.979,82"
    assert format_money(None) == "Valor nao informado"


def test_format_date_brazilian() -> None:
    assert format_date(date(2026, 7, 10)) == "10/07/2026"
    assert format_date(None) == "Data nao informada"


def test_format_opportunity_line() -> None:
    opportunity = Opportunity(
        orgao_comprador="Municipio de Aparecida de Goiania",
        objeto="Aquisicao de herbicida",
        data_fechamento=date(2026, 7, 10),
        valor_estimado=Decimal("49979.82"),
        link_edital="https://example.test",
    )

    assert format_opportunity_line(opportunity) == "Aquisicao de herbicida + R$ 49.979,82 + 10/07/2026"


def test_shorten_object() -> None:
    assert shorten_object("A" * 200, max_length=12) == "AAAAAAAAA..."
