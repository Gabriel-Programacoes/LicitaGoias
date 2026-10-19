from __future__ import annotations

import base64
import binascii
import json
import time
from dataclasses import dataclass

import requests
from fastapi import HTTPException, status

from licitagoias.api.config import Settings


@dataclass(frozen=True)
class VerifiedIdentity:
    subject: str
    email: str
    email_verified: bool


def _reject() -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credencial inválida",
                         headers={"WWW-Authenticate": "Bearer"})


def _claims(token: str) -> dict:
    try:
        chunks = token.split(".")
        if len(chunks) != 3 or len(token) > 16384:
            raise ValueError("formato")
        payload = base64.urlsafe_b64decode(chunks[1] + "=" * (-len(chunks[1]) % 4))
        result = json.loads(payload)
        if not isinstance(result, dict):
            raise ValueError("payload")
        return result
    except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
        raise _reject() from exc


def verify_supabase_token(token: str, settings: Settings) -> VerifiedIdentity:
    # O endpoint /user valida a assinatura no próprio projeto Supabase.
    claims = _claims(token)
    try:
        response = requests.get(
            settings.user_url,
            headers={"apikey": settings.publishable_key, "Authorization": f"Bearer {token}"},
            timeout=8,
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=503, detail="Autenticação indisponível") from exc
    if response.status_code in {400, 401, 403}:
        raise _reject()
    if response.status_code != 200:
        raise HTTPException(status_code=503, detail="Autenticação indisponível")
    try:
        user = response.json()
    except ValueError as exc:
        raise HTTPException(status_code=503, detail="Autenticação indisponível") from exc
    if not isinstance(user, dict):
        raise HTTPException(status_code=503, detail="Autenticação indisponível")

    audience = claims.get("aud")
    if isinstance(audience, str):
        audience = [audience]
    expiry = claims.get("exp")
    subject = claims.get("sub")
    if (
        claims.get("iss") != settings.issuer
        or not isinstance(audience, list) or "authenticated" not in audience
        or claims.get("role") != "authenticated"
        or isinstance(expiry, bool) or not isinstance(expiry, (int, float)) or expiry <= time.time()
        or not isinstance(subject, str) or not subject or subject != user.get("id")
        or user.get("is_anonymous") is True
    ):
        raise _reject()
    email = user.get("email")
    if not isinstance(email, str) or not email.strip():
        raise _reject()
    return VerifiedIdentity(
        subject=subject,
        email=email.strip().lower(),
        email_verified=bool(user.get("email_confirmed_at")),
    )
