from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Iterator

import requests
from requests import RequestException

from licitagoias.collectors.base import Collector

APARECIDA_GOIANIA_IBGE = "5201405"
DEFAULT_MODALIDADE_CODES = tuple(range(1, 15))
REQUEST_TIMEOUT_SECONDS = 20
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CollectionPage:
    segment: str
    page: int
    total_pages: int
    records: list[dict[str, Any]]


class CollectionError(RuntimeError):
    def __init__(self, segment: str, page: int, reason: str):
        self.segment = segment
        self.page = page
        super().__init__(f"{segment}, página {page}: {reason}")


class PNCPCollector(Collector):
    source_name = "PNCP"

    def __init__(
        self,
        base_url: str = "https://pncp.gov.br/api/consulta",
        municipio_ibge: str | None = None,
        uf: str = "GO",
        modalidades: tuple[int, ...] = DEFAULT_MODALIDADE_CODES,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.municipio_ibge = municipio_ibge
        self.uf = uf
        self.modalidades = modalidades
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "licitagoias/0.1 contato: coleta-publica"})

    def collect(self, start_date: date, end_date: date) -> list[dict]:
        unique: dict[str, dict] = {}
        for segment in self.segments():
            for page in self.iter_pages(segment, start_date, end_date):
                for raw in page.records:
                    key = raw.get("numeroControlePNCP") or repr(raw)
                    unique[str(key)] = self.map_item(raw)
        return list(unique.values())

    def collect_recent(self, limit: int = 5, days_back: int = 90, end_date: date | None = None) -> list[dict]:
        end = end_date or date.today()
        records = self.collect(end - timedelta(days=days_back), end)
        return sorted(records, key=lambda record: record.get("data_publicacao") or "", reverse=True)[:limit]

    def segments(self) -> tuple[str, ...]:
        return ("proposta", *(f"publicacao:{code}" for code in self.modalidades))

    def iter_pages(
        self, segment: str, start_date: date, end_date: date, start_page: int = 1
    ) -> Iterator[CollectionPage]:
        if start_page < 1 or start_date > end_date:
            raise ValueError("Página ou janela de datas inválida")
        params: dict[str, Any] = {
            "dataFinal": end_date.strftime("%Y%m%d"),
            "uf": self.uf,
            "tamanhoPagina": 50,
        }
        if self.municipio_ibge:
            params["codigoMunicipioIbge"] = self.municipio_ibge
        if segment == "proposta":
            path = "/v1/contratacoes/proposta"
        elif segment.startswith("publicacao:") and segment.split(":", 1)[1].isdigit() and int(segment.split(":", 1)[1]) in self.modalidades:
            path = "/v1/contratacoes/publicacao"
            params["dataInicial"] = start_date.strftime("%Y%m%d")
            params["codigoModalidadeContratacao"] = int(segment.split(":", 1)[1])
        else:
            raise ValueError(f"Segmento desconhecido: {segment}")

        page_number = start_page
        while True:
            params["pagina"] = page_number
            response = self._request(path, params, segment, page_number)
            if response.status_code == 204:
                if page_number != 1:
                    raise CollectionError(segment, page_number, "204 antes do fim da paginação")
                yield CollectionPage(segment, page_number, 1, [])
                return
            try:
                payload = response.json()
            except ValueError as exc:
                raise CollectionError(segment, page_number, "JSON inválido") from exc
            if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
                raise CollectionError(segment, page_number, "formato inesperado")
            try:
                total_pages = int(payload["totalPaginas"])
            except (KeyError, ValueError, TypeError) as exc:
                raise CollectionError(segment, page_number, "totalPaginas inválido") from exc
            if total_pages < page_number or total_pages < 1 or not all(isinstance(row, dict) for row in payload["data"]):
                raise CollectionError(segment, page_number, "paginação ou registros inválidos")
            logger.info("pncp_page segment=%s page=%s total=%s count=%s", segment, page_number, total_pages, len(payload["data"]))
            yield CollectionPage(segment, page_number, total_pages, payload["data"])
            if page_number >= total_pages:
                return
            page_number += 1

    def _request(self, path: str, params: dict[str, Any], segment: str, page: int) -> requests.Response:
        for attempt in range(4):
            try:
                response = self.session.get(f"{self.base_url}{path}", params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            except RequestException as exc:
                if attempt == 3:
                    raise CollectionError(segment, page, f"falha de rede: {type(exc).__name__}") from exc
                time.sleep(2 ** attempt)
                continue
            if response.status_code == 429 or 500 <= response.status_code < 600:
                if attempt == 3:
                    raise CollectionError(segment, page, f"HTTP {response.status_code}")
                retry_after = response.headers.get("Retry-After", "")
                delay = int(retry_after) if retry_after.isdigit() else 2 ** attempt
                time.sleep(min(delay, 30))
                continue
            if response.status_code != 204:
                try:
                    response.raise_for_status()
                except RequestException as exc:
                    raise CollectionError(segment, page, f"HTTP {response.status_code}") from exc
            return response
        raise AssertionError("limite de tentativas inalcançável")

    def map_item(self, item: dict[str, Any]) -> dict[str, Any]:
        orgao = item.get("orgaoEntidade") or {}
        unidade = item.get("unidadeOrgao") or {}
        link = item.get("linkSistemaOrigem") or item.get("linkProcessoEletronico") or self._build_pncp_detail_url(item)
        return {
            "fonte": self.source_name,
            "external_id": item.get("numeroControlePNCP"),
            "orgao_cnpj": orgao.get("cnpj"),
            "ano_compra": item.get("anoCompra"),
            "unidade_codigo": unidade.get("codigoUnidade"),
            "orgao_comprador": orgao.get("razaoSocial") or item.get("orgaoNome"),
            "objeto": item.get("objetoCompra") or item.get("objeto"),
            "informacao_complementar": item.get("informacaoComplementar") or item.get("informacaoComplementarCompra"),
            "data_abertura": item.get("dataAberturaProposta"),
            "data_fechamento": item.get("dataEncerramentoProposta"),
            "data_publicacao": item.get("dataPublicacaoPncp"),
            "valor_estimado": item.get("valorTotalEstimado"),
            "link_edital": link,
            "link_origem": item.get("linkSistemaOrigem"),
            "municipio": unidade.get("municipioNome"),
            "uf": unidade.get("ufSigla") or self.uf,
            "modalidade": item.get("modalidadeNome"),
            "modalidade_codigo": item.get("codigoModalidadeContratacao"),
            "status": item.get("situacaoCompraNome"),
            "numero_processo": item.get("processo"),
            "texto_bruto": "",
        }

    def _build_pncp_detail_url(self, item: dict[str, Any]) -> str:
        orgao = item.get("orgaoEntidade") or {}
        cnpj = orgao.get("cnpj")
        ano = item.get("anoCompra")
        sequencial = item.get("sequencialCompra")
        if not (cnpj and ano and sequencial):
            return ""
        return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}"
