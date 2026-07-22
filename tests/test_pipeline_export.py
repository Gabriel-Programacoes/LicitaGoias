from pathlib import Path

from licitagoias.pipeline import process_records


def test_process_records_exports_files(tmp_path: Path) -> None:
    written = process_records(
        [
            {
                "orgao_comprador": "Secretaria de Obras",
                "objeto": "Reforma de escola municipal",
                "data_abertura": "10/07/2026",
                "valor_estimado": "R$ 100.000,00",
                "link_edital": "https://example.test/edital",
                "status": "Aberta",
            }
        ],
        tmp_path,
    )

    names = {path.name for path in written}
    assert "oportunidades_curadas.csv" in names
    assert "pacote_obras.csv" in names
    assert (tmp_path / "pacote_obras.xlsx").exists()
