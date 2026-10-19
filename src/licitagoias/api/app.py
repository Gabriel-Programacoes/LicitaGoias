from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request, Response, Security, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from licitagoias.api.auth import VerifiedIdentity, verify_supabase_token
from licitagoias.api.config import get_settings
from licitagoias.phase1_db import AuditEvent, Membership, Organization, User, session_factory, utcnow

bearer = HTTPBearer(auto_error=False)


class OrganizationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=2, max_length=160)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if len(value) < 2:
            raise ValueError("Nome deve ter ao menos dois caracteres")
        return value


class OrganizationOutput(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: datetime


class MembershipOutput(BaseModel):
    organization_id: str
    role: str


class MeOutput(BaseModel):
    id: str
    email: str
    email_verified: bool
    memberships: list[MembershipOutput]


def get_db() -> Iterator[Session]:
    try:
        factory = session_factory()
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=503, detail="Serviço indisponível") from exc
    with factory() as session:
        yield session


def get_verified_identity(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer),
) -> VerifiedIdentity:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Credencial ausente", headers={"WWW-Authenticate": "Bearer"})
    try:
        settings = get_settings()
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=503, detail="Autenticação indisponível") from exc
    return verify_supabase_token(credentials.credentials, settings)


def get_current_user(
    identity: VerifiedIdentity = Depends(get_verified_identity),
    db: Session = Depends(get_db),
) -> User:
    user = db.scalar(select(User).where(User.auth_subject == identity.subject))
    if user is None:
        user = User(
            auth_subject=identity.subject,
            email=identity.email,
            email_verified=identity.email_verified,
        )
        db.add(user)
        try:
            db.flush()
            db.add(AuditEvent(
                actor_user_id=user.id, organization_id=None,
                action="user.created", details={"email_verified": user.email_verified},
            ))
            db.commit()
        except IntegrityError:
            db.rollback()
            user = db.scalar(select(User).where(User.auth_subject == identity.subject))
            if user is None:
                raise
    elif user.email != identity.email or user.email_verified != identity.email_verified:
        changed_fields = []
        if user.email != identity.email:
            changed_fields.append("email")
        if user.email_verified != identity.email_verified:
            changed_fields.append("email_verified")
        user.email = identity.email
        user.email_verified = identity.email_verified
        user.updated_at = utcnow()
        db.add(AuditEvent(
            actor_user_id=user.id, organization_id=None,
            action="user.profile_synced", details={"changed_fields": changed_fields},
        ))
        db.commit()
    return user


def organization_for_user(db: Session, user: User, organization_id: str) -> tuple[Organization, Membership]:
    row = db.execute(
        select(Organization, Membership)
        .join(Membership, Membership.organization_id == Organization.id)
        .where(Organization.id == organization_id, Membership.user_id == user.id)
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Organização não encontrada")
    return row[0], row[1]


def as_organization(org: Organization) -> OrganizationOutput:
    return OrganizationOutput(
        id=org.id, name=org.name, created_at=org.created_at, updated_at=org.updated_at
    )


app = FastAPI(
    title="LicitaGoias API",
    version="0.2.0",
    description="API do LicitaGoias: identidade, oportunidades e acompanhamento.",
)

@app.get("/v1/health", tags=["operation"])
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        get_settings()
        db.execute(text("SELECT 1"))
    except (SQLAlchemyError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=503, detail="Serviço indisponível") from exc
    return {"status": "ok"}


@app.get("/v1/me", response_model=MeOutput, responses={401: {"description": "Credencial inválida"}}, tags=["identity"])
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MeOutput:
    memberships = db.scalars(select(Membership).where(Membership.user_id == user.id)).all()
    return MeOutput(
        id=user.id,
        email=user.email,
        email_verified=user.email_verified,
        memberships=[
            MembershipOutput(organization_id=item.organization_id, role=item.role)
            for item in memberships
        ],
    )


@app.post(
    "/v1/organizations",
    response_model=OrganizationOutput,
    status_code=201,
    responses={401: {"description": "Credencial inválida"}, 403: {"description": "E-mail não confirmado"}, 409: {"description": "Organização já criada"}},
    tags=["organizations"],
)
def create_organization(
    payload: OrganizationInput,
    response: Response,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationOutput:
    if not user.email_verified:
        raise HTTPException(status_code=403, detail="Confirme seu e-mail antes de criar a organização")
    existing = db.scalar(select(Organization).where(Organization.owner_user_id == user.id))
    if existing is not None:
        if existing.name == payload.name:
            response.status_code = 200
            return as_organization(existing)
        raise HTTPException(status_code=409, detail="Organização inicial já criada")
    org = Organization(owner_user_id=user.id, name=payload.name)
    db.add(org)
    try:
        db.flush()
        db.add(Membership(user_id=user.id, organization_id=org.id, role="owner"))
        db.add(AuditEvent(
            actor_user_id=user.id, organization_id=org.id,
            action="organization.created", details={"name": org.name},
        ))
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(select(Organization).where(Organization.owner_user_id == user.id))
        if existing is not None and existing.name == payload.name:
            response.status_code = 200
            return as_organization(existing)
        raise HTTPException(status_code=409, detail="Organização inicial já criada")
    return as_organization(org)


@app.get(
    "/v1/organizations/{organization_id}",
    response_model=OrganizationOutput,
    responses={401: {"description": "Credencial inválida"}, 404: {"description": "Organização não encontrada"}},
    tags=["organizations"],
)
def get_organization(
    organization_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationOutput:
    org, _membership = organization_for_user(db, user, str(organization_id))
    return as_organization(org)


@app.patch(
    "/v1/organizations/{organization_id}",
    response_model=OrganizationOutput,
    responses={401: {"description": "Credencial inválida"}, 403: {"description": "Sem permissão"}, 404: {"description": "Organização não encontrada"}},
    tags=["organizations"],
)
def update_organization(
    organization_id: UUID,
    payload: OrganizationInput,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationOutput:
    org, membership = organization_for_user(db, user, str(organization_id))
    if membership.role != "owner":
        raise HTTPException(status_code=403, detail="Sem permissão para alterar a organização")
    if org.name != payload.name:
        previous = org.name
        org.name = payload.name
        org.updated_at = utcnow()
        db.add(AuditEvent(
            actor_user_id=user.id,
            organization_id=org.id,
            action="organization.renamed",
            details={"previous_name": previous, "name": org.name},
        ))
        db.commit()
    return as_organization(org)


from licitagoias.api.phase3 import router as phase3_router
from licitagoias.api.notifications import router as notifications_router

app.include_router(phase3_router)
app.include_router(notifications_router)

_static_dir = Path(__file__).with_name("static")
_fonts_dir = Path(__file__).resolve().parents[3] / "public" / "fonts"
app.mount("/assets", StaticFiles(directory=_static_dir), name="assets")
app.mount("/fonts", StaticFiles(directory=_fonts_dir), name="fonts")


@app.get("/app", include_in_schema=False)
def web_app():
    return FileResponse(_static_dir / "index.html")


@app.get("/unsubscribe", include_in_schema=False)
def unsubscribe_page():
    return FileResponse(_static_dir / "unsubscribe.html")


@app.get("/v1/client-config", include_in_schema=False)
def client_config() -> dict[str, str]:
    settings = get_settings()
    return {"supabase_url": settings.supabase_url, "publishable_key": settings.publishable_key}


@app.middleware("http")
async def web_security_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path in {"/app", "/unsubscribe"} or request.url.path.startswith("/assets/"):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; connect-src 'self' https://*.supabase.co; "
            "object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
