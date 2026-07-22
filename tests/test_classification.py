from licitagoias.classification import classify_text


def test_classify_packages() -> None:
    assert classify_text("Aquisicao de cimento para pavimentacao") == ["obras"]
    assert classify_text("Compra de medicamentos e luvas hospitalares") == ["saude"]
    assert classify_text("Contratacao de buffet e locacao de tendas") == ["eventos_alimentacao"]
    assert classify_text("Aquisicao de notebooks e toners") == ["tecnologia"]


def test_classify_without_match() -> None:
    assert classify_text("Servico administrativo generico") == ["sem_pacote"]
