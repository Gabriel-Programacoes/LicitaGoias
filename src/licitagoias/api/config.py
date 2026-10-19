from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from urllib.parse import urlparse


@dataclass(frozen=True)
class Settings:
    environment: str
    supabase_url: str
    publishable_key: str

    @property
    def issuer(self) -> str:
        return f"{self.supabase_url}/auth/v1"

    @property
    def user_url(self) -> str:
        return f"{self.issuer}/user"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    environment = os.getenv("LICITAGOIAS_ENV", "local").strip().lower()
    if environment not in {"local", "staging", "production"}:
        raise RuntimeError("LICITAGOIAS_ENV deve ser local, staging ou production")
    url = os.getenv("LICITAGOIAS_SUPABASE_URL", "").strip().rstrip("/")
    key = os.getenv("LICITAGOIAS_SUPABASE_PUBLISHABLE_KEY", "").strip()
    parsed = urlparse(url)
    if not parsed.hostname or parsed.path or parsed.query or parsed.fragment:
        raise RuntimeError("Configure LICITAGOIAS_SUPABASE_URL com a origem do projeto")
    local_host = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not (environment == "local" and local_host and parsed.scheme == "http"):
        raise RuntimeError("Supabase Auth requer HTTPS fora do ambiente local")
    if not key:
        raise RuntimeError("Configure LICITAGOIAS_SUPABASE_PUBLISHABLE_KEY")
    return Settings(environment=environment, supabase_url=url, publishable_key=key)
