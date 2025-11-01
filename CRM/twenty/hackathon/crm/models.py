"""Database models for the Hackathon CRM service."""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class RelationshipStage(str, enum.Enum):
    """Lifecycle stage for a CRM contact."""

    NEW_LEAD = "new_lead"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    CUSTOMER = "customer"
    INACTIVE = "inactive"


class ActionType(str, enum.Enum):
    """Actions that can be performed during nurturing."""

    POST_LIKED = "post_liked"
    COMMENT_POSTED = "comment_posted"
    SKILL_ENDORSED = "skill_endorsed"
    CONNECTION_REQUEST_SENT = "connection_request_sent"
    MESSAGE_SENT = "message_sent"
    PROFILE_VIEWED = "profile_viewed"


class ActionStatus(str, enum.Enum):
    """Possible execution status for automation actions."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


TagsColumn = JSON().with_variant(JSONB, "postgresql")


class Contact(Base):
    """Contact enriched by the scraping agents."""

    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tags: Mapped[list[str]] = mapped_column(TagsColumn, default=list, nullable=False)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    relationship_stage: Mapped[RelationshipStage] = mapped_column(
        Enum(RelationshipStage),
        default=RelationshipStage.NEW_LEAD,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_interaction_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    campaign: Mapped["Campaign" | None] = relationship("Campaign", back_populates="contacts")
    actions: Mapped[list["Action"]] = relationship(
        "Action",
        back_populates="contact",
        cascade="all, delete-orphan",
    )
    relationship: Mapped["Relationship" | None] = relationship(
        "Relationship",
        uselist=False,
        back_populates="contact",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_contacts_created_at", "created_at"),
        Index("ix_contacts_company", "company"),
        Index("ix_contacts_relationship_stage", "relationship_stage"),
        Index("ix_contacts_email", "email"),
        UniqueConstraint("linkedin_url", name="uq_contacts_linkedin_url"),
        UniqueConstraint("email", name="uq_contacts_email"),
    )


class Campaign(Base):
    """Lead generation campaigns initiated from user prompts."""

    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    target_tags: Mapped[list[str]] = mapped_column(TagsColumn, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    contacts: Mapped[list[Contact]] = relationship("Contact", back_populates="campaign")


class Action(Base):
    """Interaction executed on behalf of the user."""

    __tablename__ = "actions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    contact_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False
    )
    action_type: Mapped[ActionType] = mapped_column(Enum(ActionType), nullable=False)
    action_details: Mapped[dict | None] = mapped_column(TagsColumn, default=dict, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    status: Mapped[ActionStatus] = mapped_column(
        Enum(ActionStatus), default=ActionStatus.PENDING, nullable=False
    )
    metadata: Mapped[dict | None] = mapped_column(TagsColumn, default=dict, nullable=False)
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    contact: Mapped[Contact] = relationship("Contact", back_populates="actions")

    __table_args__ = (
        Index("ix_actions_timestamp", "timestamp"),
        Index("ix_actions_action_type", "action_type"),
    )


class Relationship(Base):
    """Tracks relationship metadata for a contact."""

    __tablename__ = "relationships"

    contact_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    relationship_stage: Mapped[RelationshipStage] = mapped_column(
        Enum(RelationshipStage),
        default=RelationshipStage.NEW_LEAD,
        nullable=False,
    )
    last_interaction: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_action_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    contact: Mapped[Contact] = relationship("Contact", back_populates="relationship")

    __table_args__ = (
        Index("ix_relationships_stage", "relationship_stage"),
    )
