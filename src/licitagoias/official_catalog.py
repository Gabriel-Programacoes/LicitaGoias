"""Acesso paginado ao CATMAT/CATSER oficial do Compras.gov.br."""
from __future__ import annotations

from functools import lru_cache
from time import monotonic
from typing import Any

import requests

BASE_URL = "https://dadosabertos.compras.gov.br"
_STEPS = {
    ("material", "group"): ("modulo-material/1_consultarGrupoMaterial", None, "codigoGrupo", "nomeGrupo"),
    ("material", "class"): ("modulo-material/2_consultarClasseMaterial", "codigoGrupo", "codigoClasse", "nomeClasse"),
    ("material", "pdm"): ("modulo-material/3_consultarPdmMaterial", "codigoClasse", "codigoPdm", "nomePdm"),
    ("material", "item"): ("modulo-material/4_consultarItemMaterial", "codigoPdm", "codigoItem", "descricaoItem"),
    ("service", "section"): ("modulo-servico/1_consultarSecaoServico", None, "codigoSecao", "nomeSecao"),
    ("service", "division"): ("modulo-servico/2_consultarDivisaoServico", "codigoSecao", "codigoDivisao", "nomeDivisao"),
    ("service", "group"): ("modulo-servico/3_consultarGrupoServico", "codigoDivisao", "codigoGrupo", "nomeGrupo"),
    ("service", "class"): ("modulo-servico/4_consultarClasseServico", "codigoGrupo", "codigoClasse", "nomeClasse"),
    ("service", "subclass"): ("modulo-servico/5_consultarSubClasseServico", "codigoClasse", "codigoSubclasse", "nomeSubclasse"),
    ("service", "item"): ("modulo-servico/6_consultarItemServico", "codigoSubclasse", "codigoServico", "nomeServico"),
}


class CatalogUnavailable(RuntimeError):
    pass


_CACHE_TTL_SECONDS = 3600
_cached_at = 0.0


@lru_cache(maxsize=512)
def _cached_rows(kind: str, level: str, parent_code: str | None, cache_generation: int) -> tuple[dict[str, Any], ...]:
    try:
        path, parent_param, code_key, name_key = _STEPS[(kind, level)]
    except KeyError as exc:
        raise ValueError("Etapa do catálogo inválida") from exc
    if parent_param and not parent_code:
        raise ValueError("Selecione a categoria anterior")
    params: dict[str, Any] = {"pagina": 1}
    if parent_param:
        params[parent_param] = parent_code
    if level == "item":
        params["tamanhoPagina"] = 500
    results: list[dict[str, Any]] = []
    try:
        with requests.Session() as session:
            while True:
                response = session.get(f"{BASE_URL}/{path}", params=params, timeout=(5, 25))
                response.raise_for_status()
                payload = response.json()
                results.extend(payload.get("resultado", []))
                total_pages = int(payload.get("totalPaginas") or 1)
                if params["pagina"] >= total_pages:
                    break
                if params["pagina"] >= 200:
                    raise CatalogUnavailable("A consulta oficial excedeu o limite de páginas")
                params["pagina"] += 1
    except (requests.RequestException, ValueError, TypeError) as exc:
        raise CatalogUnavailable("O catálogo oficial do Compras.gov.br está temporariamente indisponível") from exc
    status_key = {"group":"statusGrupo", "class":"statusClasse", "pdm":"statusPdm", "item":"statusItem",
                  "section":"statusSecao", "division":"statusDivisao", "subclass":"statusSubclasse"}.get(
                      level, "statusServico")
    return tuple({
        "code": str(row.get(code_key, "")),
        "name": str(row.get(name_key, "")).strip(),
        "active": row.get(status_key, row.get("statusGrupo", True)),
    } for row in results if row.get(code_key) is not None and row.get(name_key))


def catalog_nodes(kind: str, level: str, parent_code: str | None = None) -> list[dict[str, Any]]:
    global _cached_at
    if monotonic() - _cached_at > _CACHE_TTL_SECONDS:
        _cached_rows.cache_clear()
        _cached_at = monotonic()
    rows = _cached_rows(kind, level, parent_code, int(_cached_at))
    prefix = "catmat" if kind == "material" else "catser"
    return [{"id": f"{prefix}:{row['code']}", "code": row["code"], "name": row["name"],
             "active": row["active"] is True or str(row["active"]).lower() in {"true", "1"}}
            for row in rows]


def resolve_item_ids(ids: list[str]) -> dict[str, str]:
    """Validate selected item identifiers against official code lookup endpoints."""
    resolved: dict[str, str] = {}
    for item_id in ids:
        prefix, code = item_id.split(":", 1)
        kind = "material" if prefix == "catmat" else "service"
        endpoint, _, code_key, name_key = _STEPS[(kind, "item")]
        query_key = "codigoItem" if kind == "material" else "codigoServico"
        try:
            response = requests.get(f"{BASE_URL}/{endpoint}", params={query_key: code, "pagina": 1, "tamanhoPagina": 500}, timeout=(5, 25))
            response.raise_for_status()
            rows = response.json().get("resultado", [])
        except (requests.RequestException, ValueError, TypeError) as exc:
            raise CatalogUnavailable("Não foi possível validar os itens no catálogo oficial") from exc
        match = next((row for row in rows if str(row.get(code_key)) == code and row.get(name_key)), None)
        if match is None:
            raise ValueError(f"O item {item_id} não existe no catálogo oficial")
        resolved[item_id] = str(match[name_key]).strip()
    return resolved


def clear_catalog_cache() -> None:
    global _cached_at
    _cached_rows.cache_clear()
    _cached_at = monotonic()
