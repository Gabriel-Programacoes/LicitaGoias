from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import re
from zoneinfo import ZoneInfo
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import and_, cast, func, or_, select, Text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from licitagoias.api.app import get_current_user, get_db, organization_for_user
from licitagoias.catalog import (
    DEADLINE_OPTIONS, MODALITIES, MUNICIPALITIES, OPPORTUNITY_CATEGORIES, STATUSES,
    catalog_response,
)
from licitagoias.cleaning import strip_accents
from licitagoias.phase1_db import (
    CollectionRun, InterestProfile, OpportunityFeedback, OpportunityFollow,
    Membership, OpportunityRecord, OpportunityVersion, User, utcnow,
)

router = APIRouter(tags=["opportunities", "interest-profiles", "feedback", "follows"])
RULESET_VERSION = "rules-v2"
MAX_PAGE_SIZE = 100
_ACCENTED_SEARCH_CHARS = "áàâãäåæçéèêëíìîïñóòôõöøúùûüýÿ"
_PLAIN_SEARCH_CHARS = "aaaaaaac" + "eeee" + "iiii" + "n" + "oooooo" + "uuuu" + "yy"


def _normalized(value: Any) -> str:
    return strip_accents(str(value or "").casefold())


def _contains_phrase(text: str, phrase: str) -> bool:
    normalized = _normalized(phrase).strip()
    return bool(normalized) and re.search(
        rf"(?<![a-z0-9]){re.escape(normalized)}(?![a-z0-9])", text
    ) is not None


def _ilike_fragment(value: str) -> str:
    return value.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class ProfileInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=2, max_length=120)
    # Empty means a broad profile without opportunity-category narrowing.
    opportunity_category_ids: list[str] = Field(default_factory=list, max_length=20)
    municipality_codes: list[str] = Field(default_factory=list, max_length=10)
    status_codes: list[str] = Field(default_factory=list, max_length=10)
    modality_codes: list[str] = Field(default_factory=list, max_length=14)
    deadline_days: int | None = Field(default=None, ge=0, le=365)
    active: bool = True

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if len(value) < 2:
            raise ValueError("Nome deve ter ao menos dois caracteres")
        return value

    @field_validator("opportunity_category_ids")
    @classmethod
    def validate_opportunity_categories(cls, value: list[str]) -> list[str]:
        value = list(dict.fromkeys(value))
        if set(value) - OPPORTUNITY_CATEGORIES.keys():
            raise ValueError("Selecione uma categoria de licitação disponível")
        return value

    @field_validator("municipality_codes")
    @classmethod
    def validate_municipalities(cls, value: list[str]) -> list[str]:
        value = list(dict.fromkeys(value))
        if set(value) - MUNICIPALITIES.keys():
            raise ValueError("Selecione um município disponível")
        return value

    @field_validator("status_codes")
    @classmethod
    def validate_statuses(cls, value: list[str]) -> list[str]:
        value = list(dict.fromkeys(value))
        if set(value) - STATUSES.keys():
            raise ValueError("Selecione uma situação disponível")
        return value

    @field_validator("modality_codes")
    @classmethod
    def validate_modalities(cls, value: list[str]) -> list[str]:
        value = list(dict.fromkeys(value))
        if set(value) - MODALITIES.keys():
            raise ValueError("Selecione uma modalidade disponível")
        return value

    @field_validator("deadline_days")
    @classmethod
    def validate_deadline_option(cls, value: int | None) -> int | None:
        if value not in DEADLINE_OPTIONS:
            raise ValueError("Selecione um prazo disponível")
        return value

class ProfileOutput(BaseModel):
    id: str
    organization_id: str
    name: str
    opportunity_category_ids: list[str]
    municipality_codes: list[str]
    status_codes: list[str]
    modality_codes: list[str]
    deadline_days: int | None
    active: bool
    legacy_options: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class FeedbackInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    relevance: str = Field(pattern="^(relevant|not_relevant)$")
    reason: str | None = Field(default=None, pattern="^(wrong_product|location|deadline|status|other)$")
    comment: str | None = Field(default=None, max_length=1000)
    profile_id: UUID | None = None


class OpportunityOutput(BaseModel):
    id: str
    source: str
    external_id: str
    identity_method: str
    review_required: bool
    official_status: str | None
    derived_state: str
    data: dict[str, Any]
    first_observed_at: datetime
    last_observed_at: datetime
    match: dict[str, Any] | None = None
    followed: bool = False


class FollowInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    opportunity_id: UUID


def _profile_output(row: InterestProfile) -> ProfileOutput:
    municipality_codes = []
    for value in row.municipalities:
        code = value if value in MUNICIPALITIES else next((key for key, option in MUNICIPALITIES.items()
                    if _normalized(value) in {_normalized(option["name"]), *(_normalized(term) for term in option["terms"])}), None)
        if code and code not in municipality_codes:
            municipality_codes.append(code)
    status_codes = []
    for value in row.statuses:
        code = value if value in STATUSES else next((key for key, option in STATUSES.items()
                    if _normalized(value) in {_normalized(option["name"]), *(_normalized(term) for term in option["terms"])}), None)
        if code and code not in status_codes:
            status_codes.append(code)
    legacy = []
    if row.positive_terms or row.negative_terms:
        legacy.append("Critérios antigos de produto ou serviço")
    if len(municipality_codes) < len(row.municipalities):
        mapped_names = {MUNICIPALITIES[code]["name"] for code in municipality_codes}
        old = [value for value in row.municipalities if value not in MUNICIPALITIES
               and not any(_normalized(value) == _normalized(name) for name in mapped_names)]
        if old:
            legacy.append("Municípios antigos: " + ", ".join(old))
    if len(status_codes) < len(row.statuses):
        recognized_values = {STATUSES[code]["name"] for code in status_codes}
        old = [value for value in row.statuses if value not in STATUSES
               and not any(_normalized(value) == _normalized(name) for name in recognized_values)]
        if old:
            legacy.append("Situações antigas: " + ", ".join(old))
    if row.deadline_days is not None and row.deadline_days not in DEADLINE_OPTIONS:
        legacy.append(f"Prazo antigo: até {row.deadline_days} dias")
    return ProfileOutput(
        id=row.id, organization_id=row.organization_id, name=row.name,
        opportunity_category_ids=list(row.opportunity_category_ids or []),
        municipality_codes=municipality_codes, status_codes=status_codes,
        modality_codes=list(row.modality_codes or []),
        deadline_days=row.deadline_days if row.deadline_days in DEADLINE_OPTIONS else None,
        active=row.active, legacy_options=legacy,
        created_at=row.created_at, updated_at=row.updated_at,
    )


def _profile_values(payload: ProfileInput) -> dict[str, Any]:
    return {
        "name": payload.name,
        "opportunity_category_ids": payload.opportunity_category_ids,
        "positive_terms": [],
        "synonyms": {},
        "negative_terms": [],
        "municipalities": payload.municipality_codes,
        "statuses": payload.status_codes,
        "modality_codes": payload.modality_codes,
        "deadline_days": payload.deadline_days,
        "active": payload.active,
    }


def _opportunity_category_text(data: dict[str, Any]) -> str:
    # Category matching uses only the notice's published object-level text.
    keys = ("objeto", "informacao_complementar")
    return _normalized(" ".join(str(data.get(key) or "") for key in keys))


def explain_match(profile: InterestProfile, row: OpportunityRecord) -> dict[str, Any]:
    data = row.current_data
    text_value = _opportunity_category_text(data)
    selected_categories = [OPPORTUNITY_CATEGORIES[category_id]
                           for category_id in profile.opportunity_category_ids
                           if category_id in OPPORTUNITY_CATEGORIES]
    matched_categories = [category["name"] for category in selected_categories
                          if any(_contains_phrase(text_value, term) for term in category["terms"])]
    stale_item_criteria = bool(profile.positive_terms or profile.negative_terms)
    reasons: list[str] = []
    exclusions: list[str] = []
    if stale_item_criteria:
        exclusions.append("Perfil precisa ser atualizado para categorias de licitação")
    if not selected_categories:
        reasons.append("Busca ampla: nenhuma categoria selecionada")
    elif matched_categories:
        reasons.append("Categoria: " + ", ".join(matched_categories))
    else:
        exclusions.append("Categoria de licitação fora do perfil")
    if profile.municipalities:
        municipality = _normalized(data.get("municipio"))
        allowed = []
        for value in profile.municipalities:
            option = MUNICIPALITIES.get(value)
            if option:
                allowed.extend(_normalized(term) for term in option["terms"])
            else:
                allowed.append(_normalized(value))
        if municipality not in allowed:
            exclusions.append("Município fora do perfil")
        else:
            reasons.append(f"Município: {data.get('municipio')}")
    if profile.statuses:
        state = _normalized(data.get("status") or row.official_status)
        matches_status = False
        today_sp = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
        def source_date(field: str) -> date | None:
            value = data.get(field)
            value = value.get("iso") if isinstance(value, dict) else value
            try:
                return date.fromisoformat(str(value)[:10])
            except (ValueError, TypeError):
                return None

        opening_date = source_date("data_abertura")
        closing_date = source_date("data_fechamento")
        for value in profile.statuses:
            option = STATUSES.get(value)
            terms = option["terms"] if option else (value,)
            textual_match = any(_normalized(term) in state for term in terms)
            if value == "open":
                excluded_state = any(term in state for term in ("suspens", "cancel", "revog", "anulad"))
                receiving_proposals = (
                    opening_date is not None and closing_date is not None
                    and opening_date <= today_sp <= closing_date
                    and not excluded_state
                )
                textual_match = textual_match or receiving_proposals
            matches_status = matches_status or textual_match
        if not matches_status:
            exclusions.append("Situação fora do perfil")
        else:
            reasons.append(f"Situação: {data.get('status') or row.official_status}")
    if profile.modality_codes:
        modality_code = str(data.get("modalidade_codigo") or "")
        modality_name = re.sub(r"[^a-z0-9]+", " ", _normalized(data.get("modalidade"))).strip()
        selected_modalities = [MODALITIES[code] for code in profile.modality_codes if code in MODALITIES]
        matches_modality = modality_code in profile.modality_codes
        if not modality_code and modality_name:
            matches_modality = any(
                re.sub(r"[^a-z0-9]+", " ", _normalized(option["name"])).strip() == modality_name
                for option in selected_modalities
            )
        if not matches_modality:
            exclusions.append("Modalidade fora do perfil")
        else:
            matched_label = next((MODALITIES[code]["name"] for code in profile.modality_codes
                                  if code in MODALITIES and modality_code == code), None)
            reasons.append(f"Modalidade: {data.get('modalidade') or matched_label or 'selecionada no perfil'}")
    deadline_iso = ((data.get("data_abertura") or {}).get("iso")
                    if isinstance(data.get("data_abertura"), dict)
                    else data.get("data_abertura"))
    if profile.deadline_days is not None:
        try:
            today_sp = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
            remaining = (date.fromisoformat(str(deadline_iso)[:10]) - today_sp).days
            if remaining < 0 or remaining > profile.deadline_days:
                exclusions.append("Prazo fora do limite configurado")
            else:
                reasons.append(f"Prazo em {remaining} dia(s)")
        except (ValueError, TypeError):
            exclusions.append("Prazo desconhecido; perfil exige limite de prazo")
    included = (not selected_categories or bool(matched_categories)) and not stale_item_criteria and not exclusions and profile.active
    return {
        "included": included,
        "score": len(matched_categories),
        "reasons": reasons,
        "exclusions": exclusions,
        "ruleset_version": RULESET_VERSION,
    }


def _coverage(db: Session) -> dict[str, Any]:
    latest = db.scalar(select(CollectionRun).where(CollectionRun.source == "PNCP")
                       .order_by(CollectionRun.started_at.desc(), CollectionRun.id.desc()).limit(1))
    now = datetime.now(timezone.utc)
    if latest is None:
        return {"state": "unavailable", "last_run_at": None, "message": "Nenhuma coleta registrada"}
    observed_at = latest.finished_at or latest.started_at
    age = now - observed_at.replace(tzinfo=timezone.utc) if observed_at.tzinfo is None else now - observed_at
    state = "stale" if age > timedelta(hours=24) else latest.status
    return {
        "state": state, "last_run_at": observed_at,
        "run_status": latest.status, "source": latest.source,
        "municipality_code": latest.municipality_code, "uf": latest.uf,
        "message": "Atualização com mais de 24 horas" if state == "stale" else None,
    }


def _as_opportunity(row: OpportunityRecord, profile: InterestProfile | None = None,
                    followed: bool = False) -> dict[str, Any]:
    return {
        "id": row.id, "source": row.source, "external_id": row.external_id,
        "identity_method": row.identity_method, "review_required": row.review_required,
        "official_status": row.official_status, "derived_state": row.derived_state,
        "data": row.current_data, "first_observed_at": row.first_observed_at,
        "last_observed_at": row.last_observed_at,
        "match": explain_match(profile, row) if profile is not None else None,
        "followed": followed,
    }


def _owned_profile(db: Session, user: User, profile_id: UUID) -> InterestProfile:
    row = db.scalar(select(InterestProfile).where(InterestProfile.id == str(profile_id)))
    if row is None:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    organization_for_user(db, user, row.organization_id)
    return row


@router.get("/v1/catalog")
def get_catalog(user: User = Depends(get_current_user)):
    """Categorias de oportunidade e filtros estruturados de perfil."""
    return catalog_response()


@router.get("/v1/interest-profiles", response_model=list[ProfileOutput])
def list_profiles(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    organization_ids = select(InterestProfile.organization_id).join(
        Membership,
        Membership.organization_id == InterestProfile.organization_id,
    ).where(Membership.user_id == user.id)
    return [_profile_output(row) for row in db.scalars(select(InterestProfile).where(
        InterestProfile.organization_id.in_(organization_ids)).order_by(InterestProfile.created_at, InterestProfile.id)).all()]


@router.post("/v1/interest-profiles", response_model=ProfileOutput, status_code=201)
def create_profile(payload: ProfileInput, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = db.execute(select(Membership)
                            .where(Membership.user_id == user.id)).scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=403, detail="Crie uma organização antes do perfil")
    row = InterestProfile(organization_id=membership.organization_id,
                          **_profile_values(payload))
    db.add(row)
    db.commit()
    db.refresh(row)
    return _profile_output(row)


@router.patch("/v1/interest-profiles/{profile_id}", response_model=ProfileOutput)
def update_profile(profile_id: UUID, payload: ProfileInput, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = _owned_profile(db, user, profile_id)
    for key, value in _profile_values(payload).items():
        setattr(row, key, value)
    row.updated_at = utcnow()
    db.commit()
    db.refresh(row)
    return _profile_output(row)


@router.delete("/v1/interest-profiles/{profile_id}", status_code=204)
def delete_profile(profile_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = _owned_profile(db, user, profile_id)
    db.delete(row)
    db.commit()
    return Response(status_code=204)


@router.get("/v1/opportunities")
def search_opportunities(
    q: str | None = Query(default=None, max_length=200), municipality: str | None = Query(default=None, max_length=100),
    status_filter: str | None = Query(default=None, alias="status", max_length=100),
    opening_from: date | None = None, opening_to: date | None = None,
    page: int = Query(default=1, ge=1), page_size: int = Query(default=30, ge=1, le=MAX_PAGE_SIZE),
    profile_id: UUID | None = None, view: str = Query(default="matched", pattern="^(matched|all)$"),
    user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    profile = _owned_profile(db, user, profile_id) if profile_id else None
    query = select(OpportunityRecord)
    if profile and view == "matched":
        # Push exact structured facets into PostgreSQL before applying the full
        # deterministic matcher; this keeps large tenant feeds from scanning
        # every collected opportunity in Python.
        if profile.modality_codes:
            modality_code = OpportunityRecord.current_data["modalidade_codigo"].as_string()
            code_match = modality_code.in_(profile.modality_codes)
            # Preserve older normalized rows without a modality code; the
            # matcher below checks their official modality label.
            query = query.where(or_(code_match, modality_code.is_(None)))
    if q:
        # Search each word independently so order and accents do not matter
        # (e.g. "manutencao computadores" matches "Computadores — manutenção").
        # Translating in SQL avoids requiring the optional PostgreSQL unaccent
        # extension on hosted Supabase projects.
        search_fields = [
            func.translate(
                func.lower(OpportunityRecord.current_data[key].as_string()),
                _ACCENTED_SEARCH_CHARS + _ACCENTED_SEARCH_CHARS.upper(),
                _PLAIN_SEARCH_CHARS + _PLAIN_SEARCH_CHARS,
            )
            for key in (
                "objeto", "informacao_complementar", "orgao_comprador", "municipio",
                "modalidade", "status", "numero_processo",
            )
        ]
        search_fields.extend([
            func.translate(
                func.lower(value),
                _ACCENTED_SEARCH_CHARS + _ACCENTED_SEARCH_CHARS.upper(),
                _PLAIN_SEARCH_CHARS + _PLAIN_SEARCH_CHARS,
            )
            for value in (OpportunityRecord.external_id, OpportunityRecord.official_status)
        ])
        terms = [_normalized(term) for term in re.findall(r"[\w]+", q, flags=re.UNICODE)]
        terms = [term for term in terms if term]
        if terms:
            query = query.where(and_(*[
                or_(*[
                    field.ilike(f"%{_ilike_fragment(term)}%", escape="\\")
                    for field in search_fields
                ])
                for term in terms
            ]))
    if municipality:
        query = query.where(OpportunityRecord.current_data["municipio"].as_string().ilike(
            f"%{_ilike_fragment(municipality)}%", escape="\\"))
    if status_filter:
        category = STATUSES.get(status_filter)
        if category:
            query = query.where(or_(*[
                OpportunityRecord.official_status.ilike(
                    f"%{_ilike_fragment(term)}%", escape="\\"
                ) for term in category["terms"]
            ]))
        else:
            query = query.where(OpportunityRecord.official_status.ilike(
                f"%{_ilike_fragment(status_filter)}%", escape="\\"))
    ordered = query.order_by(OpportunityRecord.last_observed_at.desc(), OpportunityRecord.id)
    if profile is None and not (opening_from or opening_to):
        total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
        rows = db.scalars(ordered.offset((page - 1) * page_size).limit(page_size)).all()
    else:
        def opening(row: OpportunityRecord):
            field = row.current_data.get("data_abertura")
            value = field.get("iso") if isinstance(field, dict) else field
            try:
                return date.fromisoformat(str(value)[:10])
            except (ValueError, TypeError):
                return None
        total = 0
        matched_total = 0
        excluded_total = 0
        rows = []
        start_at, end_at = (page - 1) * page_size, page * page_size
        for row in db.scalars(ordered.execution_options(yield_per=500)):
            opened = opening(row)
            if opening_from and (opened is None or opened < opening_from):
                continue
            if opening_to and (opened is None or opened > opening_to):
                continue
            classification = explain_match(profile, row) if profile else None
            included = classification["included"] if classification else True
            if included:
                matched_total += 1
            else:
                excluded_total += 1
            if profile and view == "matched" and not included:
                continue
            if start_at <= total < end_at:
                rows.append(row)
            total += 1
    items = rows
    if profile is None:
        matched_total = total
        excluded_total = 0
    followed_ids = set()
    if items:
        organization_ids = select(Membership.organization_id).where(
            Membership.user_id == user.id
        )
        followed_ids = set(db.scalars(select(OpportunityFollow.opportunity_id).where(
            OpportunityFollow.organization_id.in_(organization_ids),
            OpportunityFollow.opportunity_id.in_([row.id for row in items]),
        )).all())
    coverage = _coverage(db)
    return {
        "items": [_as_opportunity(row, profile, followed=row.id in followed_ids) for row in items],
        "page": page, "page_size": page_size, "total": total,
        "matched_total": matched_total, "excluded_total": excluded_total,
        "pages": (total + page_size - 1) // page_size,
        "coverage": coverage, "partial": bool(coverage.get("state") in {"partial", "failed", "stale", "unavailable"}),
    }


@router.get("/v1/opportunities/{opportunity_id}", response_model=OpportunityOutput)
def get_opportunity(opportunity_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.get(OpportunityRecord, str(opportunity_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Oportunidade não encontrada")
    org_ids = select(Membership.organization_id).where(
        Membership.user_id == user.id)
    followed = db.scalar(select(OpportunityFollow.id).where(
        OpportunityFollow.opportunity_id == row.id, OpportunityFollow.organization_id.in_(org_ids)).limit(1)) is not None
    return _as_opportunity(row, followed=followed)


@router.get("/v1/opportunities/{opportunity_id}/changes")
def opportunity_changes(opportunity_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.get(OpportunityRecord, str(opportunity_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Oportunidade não encontrada")
    versions = db.scalars(select(OpportunityVersion).where(
        OpportunityVersion.opportunity_id == row.id).order_by(OpportunityVersion.observed_at, OpportunityVersion.id)).all()
    follow = db.scalar(select(OpportunityFollow).where(
        OpportunityFollow.opportunity_id == row.id,
        OpportunityFollow.organization_id.in_(select(Membership.organization_id)
                                              .where(Membership.user_id == user.id))).limit(1))
    changes = []
    include = follow is None
    previous = None
    for version in versions:
        if follow and version.content_hash == follow.baseline_hash:
            include, previous = True, version.data
            continue
        if not include:
            previous = version.data
            continue
        if previous is not None:
            keys = sorted(set(previous) | set(version.data))
            diff = {key: {"before": previous.get(key), "after": version.data.get(key)}
                    for key in keys if previous.get(key) != version.data.get(key)}
            changes.append({"version_id": version.id, "observed_at": version.observed_at, "changes": diff})
        previous = version.data
    return {"opportunity_id": row.id, "first_observed_at": row.first_observed_at,
            "followed_at": follow.created_at if follow else None, "items": changes}


@router.get("/v1/feed")
def feed(profile_id: UUID = Query(...), page: int = Query(1, ge=1), page_size: int = Query(30, ge=1, le=MAX_PAGE_SIZE),
         view: str = Query(default="matched", pattern="^(matched|all)$"),
         user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return search_opportunities(None, None, None, None, None, page, page_size, profile_id, view, user, db)


@router.get("/v1/follows")
def list_follows(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_ids = select(Membership.organization_id).where(
        Membership.user_id == user.id)
    rows = db.execute(select(OpportunityFollow, OpportunityRecord).join(
        OpportunityRecord, OpportunityRecord.id == OpportunityFollow.opportunity_id)
        .where(OpportunityFollow.organization_id.in_(org_ids))
        .order_by(OpportunityFollow.created_at.desc(), OpportunityFollow.id)).all()
    return [{"id": follow.id, "created_at": follow.created_at, "baseline_hash": follow.baseline_hash,
             "opportunity": _as_opportunity(opportunity, followed=True)} for follow, opportunity in rows]


@router.post("/v1/follows", status_code=201)
def create_follow(payload: FollowInput, response: Response, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = db.execute(select(Membership)
                            .where(Membership.user_id == user.id)).scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=403, detail="Organização não encontrada")
    opportunity = db.get(OpportunityRecord, str(payload.opportunity_id))
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Oportunidade não encontrada")
    row = db.scalar(select(OpportunityFollow).where(
        OpportunityFollow.organization_id == membership.organization_id,
        OpportunityFollow.opportunity_id == opportunity.id))
    if row is not None:
        response.status_code = 200
        return {"id": row.id, "created_at": row.created_at, "opportunity_id": row.opportunity_id}
    row = OpportunityFollow(organization_id=membership.organization_id, opportunity_id=opportunity.id,
                            baseline_hash=opportunity.current_hash)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        row = db.scalar(select(OpportunityFollow).where(
            OpportunityFollow.organization_id == membership.organization_id,
            OpportunityFollow.opportunity_id == opportunity.id))
        if row is None:
            raise
        response.status_code = 200
    db.refresh(row)
    return {"id": row.id, "created_at": row.created_at, "opportunity_id": row.opportunity_id}


@router.delete("/v1/follows/{opportunity_id}", status_code=204)
def delete_follow(opportunity_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_ids = select(Membership.organization_id).where(
        Membership.user_id == user.id)
    row = db.scalar(select(OpportunityFollow).where(
        OpportunityFollow.opportunity_id == str(opportunity_id), OpportunityFollow.organization_id.in_(org_ids)))
    if row is None:
        raise HTTPException(status_code=404, detail="Acompanhamento não encontrado")
    db.delete(row)
    db.commit()
    return Response(status_code=204)


@router.post("/v1/opportunities/{opportunity_id}/feedback", status_code=201)
def create_feedback(opportunity_id: UUID, payload: FeedbackInput, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = db.execute(select(Membership)
                            .where(Membership.user_id == user.id)).scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=403, detail="Organização não encontrada")
    if db.get(OpportunityRecord, str(opportunity_id)) is None:
        raise HTTPException(status_code=404, detail="Oportunidade não encontrada")
    if payload.profile_id:
        _owned_profile(db, user, payload.profile_id)
    row = OpportunityFeedback(organization_id=membership.organization_id, opportunity_id=str(opportunity_id),
                              profile_id=str(payload.profile_id) if payload.profile_id else None,
                              user_id=user.id, relevance=payload.relevance, reason=payload.reason,
                              comment=payload.comment.strip() if payload.comment else None)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "opportunity_id": row.opportunity_id, "relevance": row.relevance,
            "reason": row.reason, "comment": row.comment, "created_at": row.created_at}


@router.get("/v1/feedback")
def list_feedback(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_ids = select(Membership.organization_id).where(
        Membership.user_id == user.id)
    rows = db.scalars(select(OpportunityFeedback).where(OpportunityFeedback.organization_id.in_(org_ids))
                       .order_by(OpportunityFeedback.created_at.desc(), OpportunityFeedback.id).limit(200)).all()
    return [{"id": row.id, "opportunity_id": row.opportunity_id, "profile_id": row.profile_id,
             "relevance": row.relevance, "reason": row.reason, "comment": row.comment,
             "created_at": row.created_at} for row in rows]
