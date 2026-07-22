from __future__ import annotations

from collections.abc import Iterable

from licitagoias.cleaning import strip_accents
from licitagoias.models import Opportunity

PACKAGE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "obras": (
        "asfalto",
        "pavimentacao",
        "cimento",
        "concreto",
        "reforma",
        "escola",
        "ponte",
        "drenagem",
        "maquinario",
        "construcao",
        "engenharia",
    ),
    "saude": (
        "medicamento",
        "hospitalar",
        "epi",
        "luva",
        "mascara",
        "ambulancia",
        "exame",
        "odontologico",
        "insumo",
    ),
    "eventos_alimentacao": (
        "merenda",
        "generos alimenticios",
        "alimento",
        "buffet",
        "coffee break",
        "tenda",
        "som",
        "palco",
        "iluminacao",
        "evento",
    ),
    "tecnologia": (
        "computador",
        "notebook",
        "impressora",
        "toner",
        "cartucho",
        "rede",
        "internet",
        "firewall",
        "software",
        "camera",
        "servidor",
    ),
}


def classify_text(text: str) -> list[str]:
    normalized = strip_accents(text.lower())
    packages = []
    for package, keywords in PACKAGE_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            packages.append(package)
    return packages or ["sem_pacote"]


def classify_opportunities(opportunities: Iterable[Opportunity]) -> list[Opportunity]:
    classified: list[Opportunity] = []
    for opportunity in opportunities:
        packages = classify_text(f"{opportunity.objeto} {opportunity.texto_bruto}")
        for package in packages:
            clone = Opportunity(**opportunity.to_dict())
            clone.data_abertura = opportunity.data_abertura
            clone.data_fechamento = opportunity.data_fechamento
            clone.valor_estimado = opportunity.valor_estimado
            clone.data_coleta = opportunity.data_coleta
            clone.pacote = package
            classified.append(clone)
    return classified
