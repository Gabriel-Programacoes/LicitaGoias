from __future__ import annotations

from datetime import date

import pytest
from fastapi import Depends, Header, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from licitagoias.api.app import app, get_current_user, get_db
from licitagoias.phase1_db import (
    Base, Membership, NotificationPreference, OpportunityAlert, OpportunityFeedback,
    OpportunityFollow, OpportunityRecord, OpportunityVersion, Organization,
    SourceSnapshot, User,
)
from licitagoias.phase1_ingestion import save_record


@pytest.fixture
def db_factory():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)


def test_ingestion_is_idempotent_and_versions_observed_change(db_factory):
    raw = {"numeroControlePNCP": "12345678000199-1-000001/2026"}
    record = {
        "external_id": raw["numeroControlePNCP"], "orgao_cnpj": "12345678000199",
        "ano_compra": "2026", "unidade_codigo": "1", "objeto": "Computadores",
        "status": "Recebendo propostas", "data_fechamento": "2026-11-01",
    }
    with db_factory.begin() as db:
        save_record(db, "PNCP", raw, record, None)
    with db_factory.begin() as db:
        save_record(db, "PNCP", raw, record, None)
    with db_factory() as db:
        opportunity = db.scalar(select(OpportunityRecord))
        assert db.scalar(select(func.count()).select_from(OpportunityRecord)) == 1
        assert db.scalar(select(func.count()).select_from(OpportunityVersion)) == 1
        assert db.scalar(select(func.count()).select_from(SourceSnapshot)) == 1
        baseline = opportunity.current_hash

    with db_factory.begin() as db:
        user = User(auth_subject="test-subject", email="test@example.com", email_verified=True)
        db.add(user)
        db.flush()
        org = Organization(owner_user_id=user.id, name="Empresa teste")
        db.add(org)
        db.flush()
        db.add(Membership(user_id=user.id, organization_id=org.id, role="owner"))
        opportunity = db.scalar(select(OpportunityRecord))
        db.add(OpportunityFollow(organization_id=org.id, opportunity_id=opportunity.id, baseline_hash=baseline))

    changed_raw = {**raw, "situacaoCompraNome": "Suspensa"}
    changed_record = {**record, "status": "Suspensa"}
    with db_factory.begin() as db:
        save_record(db, "PNCP", changed_raw, changed_record, None)
    with db_factory() as db:
        versions = db.scalars(select(OpportunityVersion).order_by(OpportunityVersion.observed_at)).all()
        alert = db.scalar(select(OpportunityAlert))
        assert len(versions) == 2
        assert versions[1].previous_hash == versions[0].content_hash
        assert alert is not None
        assert alert.event_type == "opportunity_suspended"
        assert alert.severity == "critical"
        assert alert.changes["status"]["before"] == "Recebendo propostas"
        assert alert.changes["status"]["after"] == "Suspensa"
        assert db.scalar(select(func.count()).select_from(SourceSnapshot)) == 2


def test_pncp_collector_walks_declared_pages(monkeypatch):
    from licitagoias.collectors.pncp import CollectionPage, PNCPCollector

    collector = PNCPCollector()
    responses = iter([
        {"data": [{"numeroControlePNCP": "one"}], "totalPaginas": 2},
        {"data": [{"numeroControlePNCP": "two"}], "totalPaginas": 2},
    ])

    class Response:
        status_code = 200

        def json(self):
            return next(responses)

        def raise_for_status(self):
            return None

    monkeypatch.setattr(collector, "_request", lambda *args, **kwargs: Response())
    pages = list(collector.iter_pages("publicacao:6", date(2026, 10, 1), date(2026, 10, 15)))
    assert [page.page for page in pages] == [1, 2]
    assert [page.records[0]["numeroControlePNCP"] for page in pages] == ["one", "two"]


def test_phase3_profiles_follows_and_feedback_are_organization_scoped(db_factory, monkeypatch):
    with db_factory.begin() as db:
        user_a = User(auth_subject="subject-a", email="a@example.com", email_verified=True)
        user_b = User(auth_subject="subject-b", email="b@example.com", email_verified=True)
        db.add_all([user_a, user_b])
        db.flush()
        org_a = Organization(owner_user_id=user_a.id, name="Empresa A")
        org_b = Organization(owner_user_id=user_b.id, name="Empresa B")
        db.add_all([org_a, org_b])
        db.flush()
        db.add_all([
            Membership(user_id=user_a.id, organization_id=org_a.id, role="owner"),
            Membership(user_id=user_b.id, organization_id=org_b.id, role="owner"),
        ])
        opportunity = OpportunityRecord(
            source="PNCP", external_id="official-1", identity_method="official",
            review_required=False, official_status="Recebendo propostas", derived_state="unknown",
            current_hash="a" * 64,
            current_data={"objeto": "Aquisição de computadores", "municipio": "Goiânia",
                          "data_abertura": {"iso": "2026-11-01"}},
        )
        db.add(opportunity)

    def test_db():
        with db_factory() as db:
            yield db

    def test_user(authorization: str | None = Header(default=None), db: Session = Depends(test_db)):
        subject = (authorization or "").removeprefix("Bearer ")
        user = db.scalar(select(User).where(User.auth_subject == subject))
        if user is None:
            raise HTTPException(status_code=401)
        return user

    app.dependency_overrides[get_db] = test_db
    app.dependency_overrides[get_current_user] = test_user
    client = TestClient(app)
    a, b = {"Authorization": "Bearer subject-a"}, {"Authorization": "Bearer subject-b"}
    try:
        catalog = client.get("/v1/catalog", headers=a)
        assert catalog.status_code == 200
        assert catalog.json()["product_service_catalog"] == "CATMAT/CATSER"
        invalid = client.post("/v1/interest-profiles", headers=a, json={
            "name": "Item livre", "product_service_ids": ["termo-inventado"],
        })
        assert invalid.status_code == 422
        monkeypatch.setattr("licitagoias.api.phase3.resolve_item_ids", lambda ids: {item_id: "Computador portátil" for item_id in ids})
        created = client.post("/v1/interest-profiles", headers=a, json={
            "name": "Informática", "product_service_ids": ["catmat:12345"],
        })
        assert created.status_code == 201
        assert created.json()["product_service_labels"]["catmat:12345"] == "Computador portátil"
        assert len(client.get("/v1/interest-profiles", headers=a).json()) == 1
        assert client.get("/v1/interest-profiles", headers=b).json() == []

        follow = client.post("/v1/follows", headers=a, json={"opportunity_id": client.get(
            "/v1/opportunities", headers=a
        ).json()["items"][0]["id"]})
        assert follow.status_code == 201
        assert client.post("/v1/follows", headers=a, json={"opportunity_id": follow.json()["opportunity_id"]}).status_code == 200
        assert client.get("/v1/follows", headers=b).json() == []
        assert client.delete(f"/v1/follows/{follow.json()['opportunity_id']}", headers=b).status_code == 404

        feedback = client.post(
            f"/v1/opportunities/{follow.json()['opportunity_id']}/feedback", headers=a,
            json={"relevance": "relevant", "profile_id": created.json()["id"]},
        )
        assert feedback.status_code == 201
        assert client.get("/v1/feedback", headers=b).json() == []
    finally:
        app.dependency_overrides.clear()
