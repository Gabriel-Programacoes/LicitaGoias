from __future__ import annotations

import base64
import json
import os
import time
from uuid import uuid4

import pytest
from fastapi import Depends, Header, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from licitagoias.api.app import app, get_current_user, get_db
from licitagoias.api.auth import VerifiedIdentity, verify_supabase_token
from licitagoias.api.config import Settings
from licitagoias.phase1_db import AuditEvent, Base, Membership, Organization, User, session_factory


def _token(**overrides: object) -> str:
    payload = {
        "iss": "https://example.supabase.co/auth/v1",
        "aud": "authenticated",
        "role": "authenticated",
        "sub": "user-123",
        "exp": int(time.time()) + 300,
    }
    payload.update(overrides)
    part = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    return "header." + part + ".signature"


def test_supabase_identity_rejects_wrong_claims(monkeypatch: pytest.MonkeyPatch) -> None:
    class Response:
        status_code = 200

        def json(self) -> dict:
            return {"id": "user-123", "email": "a@example.com", "email_confirmed_at": "2026-10-15T10:00:00Z"}

    monkeypatch.setattr("licitagoias.api.auth.requests.get", lambda *args, **kwargs: Response())
    settings = Settings("local", "https://example.supabase.co", "public-key")
    assert verify_supabase_token(_token(), settings).email_verified
    for claims in (
        {"iss": "https://other.supabase.co/auth/v1"},
        {"aud": "anon"},
        {"role": "service_role"},
        {"sub": "another-user"},
        {"exp": int(time.time()) - 1},
    ):
        with pytest.raises(HTTPException) as error:
            verify_supabase_token(_token(**claims), settings)
        assert error.value.status_code == 401

    class RejectedResponse:
        status_code = 401

    monkeypatch.setattr("licitagoias.api.auth.requests.get", lambda *args, **kwargs: RejectedResponse())
    with pytest.raises(HTTPException) as error:
        verify_supabase_token(_token(), settings)
    assert error.value.status_code == 401


def test_authenticated_profile_is_created_and_audited(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr("licitagoias.api.app.session_factory", lambda: factory)
    monkeypatch.setattr(
        "licitagoias.api.app.get_settings",
        lambda: Settings("local", "https://example.supabase.co", "public-key"),
    )
    monkeypatch.setattr(
        "licitagoias.api.app.verify_supabase_token",
        lambda _token, _settings: VerifiedIdentity("user-123", "a@example.com", True),
    )
    client = TestClient(app)
    assert client.get("/v1/me").status_code == 401
    response = client.get("/v1/me", headers={"Authorization": "Bearer opaque-token"})
    assert response.status_code == 200
    assert response.json()["email"] == "a@example.com"
    with factory() as db:
        assert db.scalar(select(User).where(User.auth_subject == "user-123")) is not None
        assert db.scalar(select(AuditEvent).where(AuditEvent.action == "user.created")) is not None


def test_organizations_are_isolated_and_create_is_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    if os.getenv("LICITAGOIAS_DATABASE_URL"):
        factory = session_factory()
    else:
        engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        factory = sessionmaker(engine, expire_on_commit=False)
        monkeypatch.setattr("licitagoias.api.app.session_factory", lambda: factory)
    first_subject, second_subject, third_subject = str(uuid4()), str(uuid4()), str(uuid4())
    with factory.begin() as db:
        first = User(auth_subject=first_subject, email="a@example.com", email_verified=True)
        second = User(auth_subject=second_subject, email="b@example.com", email_verified=True)
        third = User(auth_subject=third_subject, email="c@example.com", email_verified=False)
        db.add_all([first, second, third])
        db.flush()
        first_id, second_id, third_id = first.id, second.id, third.id

    def fake_user(
        authorization: str | None = Header(default=None),
        db: Session = Depends(get_db),
    ) -> User:
        subject = (authorization or "").removeprefix("Bearer ")
        user = db.scalar(select(User).where(User.auth_subject == subject))
        if user is None:
            raise HTTPException(status_code=401)
        return user

    app.dependency_overrides[get_current_user] = fake_user
    client = TestClient(app)
    a = {"Authorization": f"Bearer {first_subject}"}
    b = {"Authorization": f"Bearer {second_subject}"}
    c = {"Authorization": f"Bearer {third_subject}"}
    try:
        assert client.post("/v1/organizations", json={"name": "Empresa C"}, headers=c).status_code == 403
        created = client.post("/v1/organizations", json={"name": "Empresa A"}, headers=a)
        assert created.status_code == 201
        org_a = created.json()["id"]
        repeated = client.post("/v1/organizations", json={"name": "Empresa A"}, headers=a)
        assert repeated.status_code == 200
        assert repeated.json()["id"] == org_a
        assert client.post("/v1/organizations", json={"name": "Outra"}, headers=a).status_code == 409
        assert client.post("/v1/organizations", json={"name": "Empresa B"}, headers=b).status_code == 201
        assert client.get(f"/v1/organizations/{org_a}", headers=b).status_code == 404
        assert client.patch(f"/v1/organizations/{org_a}", json={"name": "Invadida"}, headers=b).status_code == 404
        assert client.patch(f"/v1/organizations/{org_a}", json={"name": "Nova", "role": "owner"}, headers=a).status_code == 422
        updated = client.patch(f"/v1/organizations/{org_a}", json={"name": "Empresa A Nova"}, headers=a)
        assert updated.status_code == 200
        assert updated.json()["name"] == "Empresa A Nova"
        assert client.get("/v1/me", headers=a).json()["memberships"][0]["organization_id"] == org_a
    finally:
        app.dependency_overrides.clear()
        with factory.begin() as db:
            organizations = db.scalars(select(Organization.id).where(
                Organization.owner_user_id.in_([first_id, second_id])
            )).all()
            if organizations:
                db.execute(delete(AuditEvent).where(AuditEvent.organization_id.in_(organizations)))
                db.execute(delete(Membership).where(Membership.organization_id.in_(organizations)))
                db.execute(delete(Organization).where(Organization.id.in_(organizations)))
            db.execute(delete(User).where(User.id.in_([first_id, second_id, third_id])))
