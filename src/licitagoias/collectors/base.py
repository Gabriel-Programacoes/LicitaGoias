from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date


class Collector(ABC):
    source_name: str

    @abstractmethod
    def collect(self, start_date: date, end_date: date) -> list[dict]:
        """Retorna registros brutos para normalizacao posterior."""
