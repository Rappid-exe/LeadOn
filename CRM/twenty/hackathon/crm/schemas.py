"""Pydantic schemas for the Hackathon CRM service."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .models import ActionStatus, ActionType, RelationshipStage


class ContactBase(BaseModel):
    name: str
    title: str | None = None
    company: str | None = None
    email: str | None = None
    linkedin_url: str | None = Field(default=None, max_length=500)
    phone: str | None = None
    tags: list[str] = Field(default_factory=list)
    source: str | None = None
    relationship_stage: RelationshipStage = RelationshipStage.NEW_LEAD
    notes: str | None = None
    campaign_id: UUID | None = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    email: str | None = None
    linkedin_url: str | None = Field(default=None, max_length=500)
    phone: str | None = None
    tags: list[str] | None = None
    source: str | None = None
    relationship_stage: RelationshipStage | None = None
    notes: str | None = None
    campaign_id: UUID | None = None
    is_archived: bool | None = None


class ContactResponse(ContactBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_archived: bool
    archived_at: datetime | None = None
    last_interaction_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedContacts(BaseModel):
    total: int
    items: list[ContactResponse]


class BulkUpsertResult(BaseModel):
    success: bool
    contact: ContactResponse | None = None
    error: str | None = None
    detail: str | None = None
    payload: ContactCreate | None = None


class ActionBase(BaseModel):
    contact_id: UUID
    action_type: ActionType
    action_details: dict[str, Any] | None = None
    status: ActionStatus = ActionStatus.PENDING
    timestamp: datetime | None = None
    metadata: dict[str, Any] | None = None
    scheduled_for: datetime | None = None


class ActionCreate(ActionBase):
    pass


class ActionResponse(ActionBase):
    id: UUID
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class CampaignBase(BaseModel):
    user_prompt: str
    target_tags: list[str] = Field(default_factory=list)


class CampaignCreate(CampaignBase):
    pass


class CampaignResponse(CampaignBase):
    id: UUID
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class RelationshipBase(BaseModel):
    relationship_stage: RelationshipStage
    last_interaction: datetime | None = None
    next_action_date: date | None = None
    notes: str | None = None


class RelationshipResponse(RelationshipBase):
    contact_id: UUID

    model_config = ConfigDict(from_attributes=True)


class CrmOverview(BaseModel):
    total_contacts: int
    active_campaigns: int
    relationship_stage_counts: dict[str, int]
    tag_counts: dict[str, int]
    daily_action_counts: list[dict[str, Any]]
    recent_actions: list[ActionResponse]
