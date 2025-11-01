"""Database access helpers for the Hackathon CRM service."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime
from typing import Iterable
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas


def _normalize_tags(tags: Iterable[str] | None) -> list[str]:
    if not tags:
        return []
    return sorted({tag.strip().lower() for tag in tags if tag.strip()})


def _resolve_contact_match(
    db: Session,
    *,
    linkedin_url: str | None,
    email: str | None,
) -> models.Contact | None:
    linkedin_match: models.Contact | None = None
    email_match: models.Contact | None = None

    if linkedin_url:
        linkedin_match = (
            db.execute(select(models.Contact).where(models.Contact.linkedin_url == linkedin_url))
            .scalars()
            .first()
        )

    if email:
        email_match = (
            db.execute(select(models.Contact).where(models.Contact.email == email))
            .scalars()
            .first()
        )

    if linkedin_match and email_match and linkedin_match.id != email_match.id:
        raise ValueError("conflict: email/linkedin resolve to different contacts")

    return linkedin_match or email_match


def _apply_contact_update(
    existing: models.Contact, contact_in: schemas.ContactCreate | schemas.ContactUpdate
) -> None:
    update_data = contact_in.model_dump(exclude_unset=True)
    tags = update_data.pop("tags", None)
    if tags is not None:
        existing.tags = _normalize_tags(tags)

    for field, value in update_data.items():
        if value is not None and hasattr(existing, field):
            setattr(existing, field, value)

    existing.updated_at = datetime.utcnow()


def _apply_contact_filters(
    query: Select[tuple[models.Contact]],
    *,
    search: str | None = None,
    company: str | None = None,
    relationship_stage: models.RelationshipStage | None = None,
) -> Select[tuple[models.Contact]]:
    if search:
        like = f"%{search.lower()}%"
        query = query.where(
            func.lower(models.Contact.name).like(like)
            | func.lower(models.Contact.company).like(like)
            | func.lower(models.Contact.title).like(like)
        )
    if company:
        query = query.where(func.lower(models.Contact.company) == company.lower())
    if relationship_stage:
        query = query.where(models.Contact.relationship_stage == relationship_stage)
    return query


def list_contacts(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    search: str | None = None,
    tags: list[str] | None = None,
    company: str | None = None,
    relationship_stage: models.RelationshipStage | None = None,
) -> tuple[list[models.Contact], int]:
    query = select(models.Contact).where(models.Contact.is_archived.is_(False))
    query = _apply_contact_filters(
        query,
        search=search,
        company=company,
        relationship_stage=relationship_stage,
    )
    records = db.execute(query.order_by(models.Contact.created_at.desc())).scalars().all()

    if tags:
        normalized_tags = {tag.strip().lower() for tag in tags if tag.strip()}
        records = [
            record
            for record in records
            if normalized_tags.issubset(set(record.tags or []))
        ]

    total = len(records)
    contacts = records[skip : skip + limit]
    return contacts, total


def get_contact(db: Session, contact_id: UUID) -> models.Contact | None:
    return db.get(models.Contact, contact_id)


def create_or_update_contact(
    db: Session,
    contact_in: schemas.ContactCreate,
) -> models.Contact:
    try:
        existing = _resolve_contact_match(
            db,
            linkedin_url=contact_in.linkedin_url,
            email=contact_in.email,
        )
    except ValueError as exc:
        raise ValueError(str(exc)) from exc

    if existing:
        _apply_contact_update(existing, contact_in)
        if existing.relationship:
            existing.relationship.relationship_stage = existing.relationship_stage
        else:
            existing.relationship = models.Relationship(
                contact_id=existing.id,
                relationship_stage=existing.relationship_stage,
            )
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    contact = models.Contact(
        **contact_in.model_dump(exclude={"tags"}),
        tags=_normalize_tags(contact_in.tags),
    )
    contact.relationship = models.Relationship(
        contact_id=contact.id,
        relationship_stage=contact.relationship_stage,
    )
    db.add(contact)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        try:
            existing = _resolve_contact_match(
                db,
                linkedin_url=contact_in.linkedin_url,
                email=contact_in.email,
            )
        except ValueError as conflict_exc:
            raise ValueError(str(conflict_exc)) from conflict_exc

        if existing:
            _apply_contact_update(existing, contact_in)
            if existing.relationship:
                existing.relationship.relationship_stage = existing.relationship_stage
            else:
                existing.relationship = models.Relationship(
                    contact_id=existing.id,
                    relationship_stage=existing.relationship_stage,
                )
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

        raise

    db.refresh(contact)
    return contact


def update_contact(
    db: Session,
    contact_id: UUID,
    contact_in: schemas.ContactUpdate,
) -> models.Contact:
    contact = get_contact(db, contact_id)
    if not contact:
        raise ValueError("Contact not found")

    _apply_contact_update(contact, contact_in)

    if contact.relationship:
        contact.relationship.relationship_stage = contact.relationship_stage
        contact.relationship.last_interaction = contact.last_interaction_at
    else:
        contact.relationship = models.Relationship(
            contact_id=contact.id,
            relationship_stage=contact.relationship_stage,
        )

    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def archive_contact(db: Session, contact_id: UUID) -> models.Contact:
    contact = get_contact(db, contact_id)
    if not contact:
        raise ValueError("Contact not found")
    contact.is_archived = True
    contact.archived_at = datetime.utcnow()
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def log_action(db: Session, action_in: schemas.ActionCreate) -> models.Action:
    timestamp = action_in.timestamp or datetime.utcnow()
    payload = action_in.model_dump(exclude={"timestamp"}, exclude_none=True)
    payload.setdefault("action_details", {})
    payload.setdefault("metadata", {})
    action = models.Action(
        **payload,
        timestamp=timestamp,
    )
    db.add(action)

    if contact := db.get(models.Contact, action.contact_id):
        contact.last_interaction_at = timestamp
        if contact.relationship:
            contact.relationship.last_interaction = timestamp
        db.add(contact)

    db.commit()
    db.refresh(action)
    return action


def list_actions(
    db: Session,
    *,
    contact_id: UUID | None = None,
    limit: int = 100,
) -> list[models.Action]:
    query = select(models.Action)
    if contact_id:
        query = query.where(models.Action.contact_id == contact_id)
    return (
        db.execute(query.order_by(models.Action.timestamp.desc()).limit(limit)).scalars().all()
    )


def create_campaign(db: Session, campaign_in: schemas.CampaignCreate) -> models.Campaign:
    campaign = models.Campaign(
        **campaign_in.model_dump(exclude={"target_tags"}),
        target_tags=_normalize_tags(campaign_in.target_tags),
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


def list_campaigns(db: Session) -> list[models.Campaign]:
    return db.execute(select(models.Campaign).order_by(models.Campaign.created_at.desc())).scalars().all()


def get_overview(db: Session) -> schemas.CrmOverview:
    total_contacts = db.execute(
        select(func.count()).select_from(models.Contact).where(models.Contact.is_archived.is_(False))
    ).scalar_one()
    active_campaigns = db.execute(
        select(func.count()).select_from(models.Campaign).where(models.Campaign.completed_at.is_(None))
    ).scalar_one()

    stage_counts_raw = (
        db.execute(
            select(models.Contact.relationship_stage, func.count())
            .where(models.Contact.is_archived.is_(False))
            .group_by(models.Contact.relationship_stage)
        )
        .all()
    )
    stage_counts: dict[str, int] = {
        stage.value if isinstance(stage, models.RelationshipStage) else stage: count
        for stage, count in stage_counts_raw
    }

    tag_counter: Counter[str] = Counter()
    all_tags = db.execute(select(models.Contact.tags)).scalars().all()
    for tag_list in all_tags:
        if isinstance(tag_list, list):
            tag_counter.update(tag_list)

    recent_actions = list_actions(db, limit=10)

    daily_action_rows = (
        db.execute(
            select(func.date(models.Action.timestamp), func.count())
            .group_by(func.date(models.Action.timestamp))
            .order_by(func.date(models.Action.timestamp).desc())
            .limit(14)
        )
        .all()
    )
    daily_action_counts = [
        {"date": row[0].isoformat() if isinstance(row[0], (date, datetime)) else row[0], "count": row[1]}
        for row in daily_action_rows
    ]

    return schemas.CrmOverview(
        total_contacts=total_contacts,
        active_campaigns=active_campaigns,
        relationship_stage_counts=stage_counts,
        tag_counts=dict(tag_counter),
        daily_action_counts=daily_action_counts,
        recent_actions=[schemas.ActionResponse.model_validate(action) for action in recent_actions],
    )
