from __future__ import annotations

import time
from datetime import date, timedelta
from typing import Any

import requests
from requests import RequestException

from licitagoias.collectors.base import Collector

APARECIDA_GOIANIA_IBGE = "5201405"
DEFAULT_MODALIDADE_CODES = (6, 8, 9, 5)
REQUEST_TIMEOUT_SECONDS = 20


class PNCPCollector(Collector):
    source_name = "PNCP"

    def __init__(
        self,
        base_url: str = "https://pncp.gov.br/api/consulta",
        municipio_ibge: str = APARECIDA_GOIANIA_IBGE,
        uf: str = "GO",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.municipio_ibge = municipio_ibge
        self.uf = uf
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "licitagoias/0.1 contato: coleta-publica"})

    def collect(self, start_date: date, end_date: date) -> list[dict]:
        items = self._collect_open_proposals(end_date)
        items.extend(self._collect_recent_publications(start_date, end_date))
        return [self._map_item(item) for item in self._dedupe_items(items)]

    def collect_recent(self, limit: int = 5, days_back: int = 90, end_date: date | None = None) -> list[dict]:
        end = end_date or date.today()
        start = end - timedelta(days=days_back)
        records = self.collect(start, end)
        return sorted(records, key=lambda record: record.get("data_publicacao") or "", reverse=True)[:limit]

    def _collect_open_proposals(self, end_date: date) -> list[dict[str, Any]]:
        params = {
            "dataFinal": end_date.strftime("%Y%m%d"),
            "uf": self.uf,
            "codigoMunicipioIbge": self.municipio_ibge,
            "pagina": 1,
            "tamanhoPagina": 50,
        }
        return self._get_paged("/v1/contratacoes/proposta", params, max_pages=1)

    def _collect_recent_publications(self, start_date: date, end_date: date) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for modalidade_code in DEFAULT_MODALIDADE_CODES:
            time.sleep(0.2)
            params = {
                "dataInicial": start_date.strftime("%Y%m%d"),
                "dataFinal": end_date.strftime("%Y%m%d"),
                "codigoModalidadeContratacao": modalidade_code,
                "uf": self.uf,
                "codigoMunicipioIbge": self.municipio_ibge,
                "pagina": 1,
                "tamanhoPagina": 50,
            }
            items.extend(self._get_paged("/v1/contratacoes/publicacao", params, max_pages=1, latest_page=True))
        return items

    def _get_paged(
        self,
        path: str,
        params: dict[str, Any],
        max_pages: int = 1,
        latest_page: bool = False,
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        page = 1
        while True:
            params["pagina"] = page
            try:
                response = self.session.get(f"{self.base_url}{path}", params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            except RequestException:
                return items
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After") or 1)
                time.sleep(min(retry_after, 5))
                try:
                    response = self.session.get(f"{self.base_url}{path}", params=params, timeout=REQUEST_TIMEOUT_SECONDS)
                except RequestException:
                    return items
            if response.status_code == 204:
                return items
            if response.status_code == 429:
                return items
            try:
                response.raise_for_status()
            except RequestException:
                return items
            payload = response.json()
            page_items = payload.get("data", payload if isinstance(payload, list) else [])
            items.extend(page_items)

            total_pages = int(payload.get("totalPaginas") or page)
            if latest_page and page == 1 and total_pages > 1:
                page = total_pages
                continue
            if page >= total_pages or page >= max_pages:
                return items
            page += 1

    def _dedupe_items(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        unique: dict[str, dict[str, Any]] = {}
        for item in items:
            key = item.get("numeroControlePNCP") or "|".join(
                str(item.get(field, "")) for field in ("processo", "objetoCompra", "dataPublicacaoPncp")
            )
            unique.setdefault(key, item)
        return list(unique.values())

    def _map_item(self, item: dict[str, Any]) -> dict[str, Any]:
        link = item.get("linkSistemaOrigem") or item.get("linkProcessoEletronico") or self._build_pncp_detail_url(item)
        return {
            "fonte": self.source_name,
            "orgao_comprador": item.get("orgaoEntidade", {}).get("razaoSocial") or item.get("orgaoNome"),
            "objeto": item.get("objetoCompra") or item.get("objeto"),
            "data_abertura": item.get("dataAberturaProposta") or item.get("dataPublicacaoPncp"),
            "data_fechamento": item.get("dataEncerramentoProposta") or item.get("dataPublicacaoPncp"),
            "data_publicacao": item.get("dataPublicacaoPncp"),
            "valor_estimado": item.get("valorTotalEstimado"),
            "link_edital": link,
            "link_origem": item.get("linkSistemaOrigem"),
            "municipio": item.get("unidadeOrgao", {}).get("municipioNome"),
            "uf": item.get("unidadeOrgao", {}).get("ufSigla") or "GO",
            "modalidade": item.get("modalidadeNome"),
            "status": item.get("situacaoCompraNome"),
            "numero_processo": item.get("processo"),
            "texto_bruto": str(item),
        }

    def _build_pncp_detail_url(self, item: dict[str, Any]) -> str:
        orgao = item.get("orgaoEntidade") or {}
        cnpj = orgao.get("cnpj")
        ano = item.get("anoCompra")
        sequencial = item.get("sequencialCompra")
        if not (cnpj and ano and sequencial):
            return ""
        return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}"
