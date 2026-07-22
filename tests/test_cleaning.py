from decimal import Decimal

from licitagoias.cleaning import curate_opportunities, normalize_records, parse_brazilian_date, parse_brazilian_money


def test_parse_brazilian_date() -> None:
    assert parse_brazilian_date("31/07/2026").isoformat() == "2026-07-31"
    assert parse_brazilian_date("2026-07-31").isoformat() == "2026-07-31"
    assert parse_brazilian_date("") is None


def test_parse_brazilian_money() -> None:
    assert parse_brazilian_money("R$ 1.234.567,89") == Decimal("1234567.89")
    assert parse_brazilian_money("2500.50") == Decimal("2500.50")
    assert parse_brazilian_money("") is None


def test_curate_removes_cancelled_missing_link_and_duplicates() -> None:
    records = [
        {
            "orgao_comprador": "Secretaria de Saude",
            "objeto": "Aquisicao de medicamentos",
            "status": "Aberta",
            "link_edital": "https://example.test/1",
            "numero_processo": "1",
        },
        {
            "orgao_comprador": "Secretaria de Saude",
            "objeto": "Aquisicao de medicamentos",
            "status": "Aberta",
            "link_edital": "https://example.test/1",
            "numero_processo": "1",
        },
        {
            "orgao_comprador": "Secretaria de Obras",
            "objeto": "Reforma de escola",
            "status": "Suspensa",
            "link_edital": "https://example.test/2",
        },
        {
            "orgao_comprador": "Secretaria de Tecnologia",
            "objeto": "Computadores",
            "status": "Aberta",
        },
    ]

    curated = curate_opportunities(normalize_records(records))

    assert len(curated) == 1
    assert curated[0].objeto == "Aquisicao de medicamentos"
