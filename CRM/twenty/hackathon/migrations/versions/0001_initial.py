"""Initial schema for hackathon CRM service."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

UUID_TYPE = getattr(sa, "Uuid", None)
if UUID_TYPE is None:
    UUID_TYPE = postgresql.UUID(as_uuid=True)

relationship_stage_enum = sa.Enum(
    "new_lead",
    "contacted",
    "engaged",
    "customer",
    "inactive",
    name="relationshipstage",
    native_enum=False,
)
action_type_enum = sa.Enum(
    "post_liked",
    "comment_posted",
    "skill_endorsed",
    "connection_request_sent",
    "message_sent",
    "profile_viewed",
    name="actiontype",
    native_enum=False,
)
action_status_enum = sa.Enum(
    "pending",
    "completed",
    "failed",
    name="actionstatus",
    native_enum=False,
)


def upgrade() -> None:
    relationship_stage_enum.create(op.get_bind(), checkfirst=True)
    action_type_enum.create(op.get_bind(), checkfirst=True)
    action_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "campaigns",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column("user_prompt", sa.Text(), nullable=False),
        sa.Column("target_tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "contacts",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("linkedin_url", sa.String(length=500), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("relationship_stage", relationship_stage_enum, nullable=False, server_default="new_lead"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("last_interaction_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("campaign_id", UUID_TYPE, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("linkedin_url", name="uq_contacts_linkedin_url"),
        sa.UniqueConstraint("email", name="uq_contacts_email"),
    )
    op.create_index("ix_contacts_created_at", "contacts", ["created_at"])
    op.create_index("ix_contacts_company", "contacts", ["company"])
    op.create_index("ix_contacts_relationship_stage", "contacts", ["relationship_stage"])

    op.create_table(
        "actions",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column("contact_id", UUID_TYPE, nullable=False),
        sa.Column("action_type", action_type_enum, nullable=False),
        sa.Column("action_details", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("status", action_status_enum, nullable=False, server_default="pending"),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_actions_timestamp", "actions", ["timestamp"])
    op.create_index("ix_actions_action_type", "actions", ["action_type"])

    op.create_table(
        "relationships",
        sa.Column("contact_id", UUID_TYPE, nullable=False),
        sa.Column("relationship_stage", relationship_stage_enum, nullable=False, server_default="new_lead"),
        sa.Column("last_interaction", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_action_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("contact_id"),
    )
    op.create_index("ix_relationships_stage", "relationships", ["relationship_stage"])


def downgrade() -> None:
    op.drop_index("ix_relationships_stage", table_name="relationships")
    op.drop_table("relationships")

    op.drop_index("ix_actions_action_type", table_name="actions")
    op.drop_index("ix_actions_timestamp", table_name="actions")
    op.drop_table("actions")

    op.drop_index("ix_contacts_relationship_stage", table_name="contacts")
    op.drop_index("ix_contacts_company", table_name="contacts")
    op.drop_index("ix_contacts_created_at", table_name="contacts")
    op.drop_table("contacts")

    op.drop_table("campaigns")

    action_status_enum.drop(op.get_bind(), checkfirst=True)
    action_type_enum.drop(op.get_bind(), checkfirst=True)
    relationship_stage_enum.drop(op.get_bind(), checkfirst=True)
