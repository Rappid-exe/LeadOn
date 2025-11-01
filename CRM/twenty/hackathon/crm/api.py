"""FastAPI application exposing the CRM capabilities for the hackathon project."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, engine, get_db

logger = logging.getLogger(__name__)

app = FastAPI(title="Sales Workflow Agentic CRM", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    logger.info("CRM database tables ensured")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/contacts", response_model=schemas.PaginatedContacts)
def list_contacts(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    search: str | None = None,
    company: str | None = None,
    tags: list[str] | None = Query(default=None),
    relationship_stage: models.RelationshipStage | None = Query(default=None),
) -> schemas.PaginatedContacts:
    contacts, total = crud.list_contacts(
        db,
        skip=skip,
        limit=limit,
        search=search,
        company=company,
        tags=tags,
        relationship_stage=relationship_stage,
    )
    return schemas.PaginatedContacts(
        total=total,
        items=[schemas.ContactResponse.model_validate(contact) for contact in contacts],
    )


@app.post(
    "/api/contacts",
    response_model=schemas.ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contact(
    contact_in: schemas.ContactCreate,
    db: Session = Depends(get_db),
) -> schemas.ContactResponse:
    try:
        contact = crud.create_or_update_contact(db, contact_in)
    except ValueError as exc:
        message = str(exc)
        if message.startswith("conflict"):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from exc
    return schemas.ContactResponse.model_validate(contact)


@app.get("/api/contacts/{contact_id}", response_model=schemas.ContactResponse)
def get_contact(contact_id: UUID, db: Session = Depends(get_db)) -> schemas.ContactResponse:
    if contact := crud.get_contact(db, contact_id):
        return schemas.ContactResponse.model_validate(contact)
    raise HTTPException(status_code=404, detail="Contact not found")


@app.put("/api/contacts/{contact_id}", response_model=schemas.ContactResponse)
def update_contact(
    contact_id: UUID,
    contact_in: schemas.ContactUpdate,
    db: Session = Depends(get_db),
) -> schemas.ContactResponse:
    try:
        contact = crud.update_contact(db, contact_id, contact_in)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return schemas.ContactResponse.model_validate(contact)


@app.delete("/api/contacts/{contact_id}", response_model=schemas.ContactResponse)
def archive_contact(contact_id: UUID, db: Session = Depends(get_db)) -> schemas.ContactResponse:
    try:
        contact = crud.archive_contact(db, contact_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return schemas.ContactResponse.model_validate(contact)


@app.post(
    "/api/contacts/bulk",
    response_model=list[schemas.BulkUpsertResult],
    status_code=status.HTTP_207_MULTI_STATUS,
)
def bulk_upsert_contacts(
    contacts_in: list[schemas.ContactCreate],
    db: Session = Depends(get_db),
) -> list[schemas.BulkUpsertResult]:
    results: list[schemas.BulkUpsertResult] = []
    for payload in contacts_in:
        try:
            contact = crud.create_or_update_contact(db, payload)
        except ValueError as exc:
            message = str(exc)
            if message.startswith("conflict"):
                results.append(
                    schemas.BulkUpsertResult(
                        success=False,
                        error="conflict",
                        detail=message,
                        payload=payload,
                    )
                )
                continue
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from exc
        results.append(
            schemas.BulkUpsertResult(
                success=True,
                contact=schemas.ContactResponse.model_validate(contact),
            )
        )
    return results


@app.get("/api/contacts/{contact_id}/actions", response_model=list[schemas.ActionResponse])
def list_contact_actions(
    contact_id: UUID,
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[schemas.ActionResponse]:
    actions = crud.list_actions(db, contact_id=contact_id, limit=limit)
    return [schemas.ActionResponse.model_validate(action) for action in actions]


@app.post(
    "/api/actions",
    response_model=schemas.ActionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_action(
    action_in: schemas.ActionCreate,
    db: Session = Depends(get_db),
) -> schemas.ActionResponse:
    action = crud.log_action(db, action_in)
    return schemas.ActionResponse.model_validate(action)


@app.get("/api/actions", response_model=list[schemas.ActionResponse])
def list_actions(
    db: Session = Depends(get_db),
    contact_id: UUID | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[schemas.ActionResponse]:
    actions = crud.list_actions(db, contact_id=contact_id, limit=limit)
    return [schemas.ActionResponse.model_validate(action) for action in actions]


@app.post(
    "/api/campaigns",
    response_model=schemas.CampaignResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_campaign(
    campaign_in: schemas.CampaignCreate,
    db: Session = Depends(get_db),
) -> schemas.CampaignResponse:
    campaign = crud.create_campaign(db, campaign_in)
    return schemas.CampaignResponse.model_validate(campaign)


@app.get("/api/campaigns", response_model=list[schemas.CampaignResponse])
def list_campaigns(db: Session = Depends(get_db)) -> list[schemas.CampaignResponse]:
    campaigns = crud.list_campaigns(db)
    return [schemas.CampaignResponse.model_validate(campaign) for campaign in campaigns]


@app.get("/api/stats/overview", response_model=schemas.CrmOverview)
def get_overview(db: Session = Depends(get_db)) -> schemas.CrmOverview:
    return crud.get_overview(db)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # type: ignore[override]
    if isinstance(exc, HTTPException):
        raise exc
    logger.exception("Unhandled error while processing %s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Unexpected server error"},
    )
