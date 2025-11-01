"""Utility to persist automation events into the CRM."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from . import crud, schemas
from .models import ActionStatus, ActionType


class ActionLogger:
    """High-level helper used by automation agents to store activity."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def log(
        self,
        *,
        contact_id: UUID,
        action_type: ActionType,
        message: str | None = None,
        platform: str = "linkedin",
        status: ActionStatus = ActionStatus.COMPLETED,
        extra: dict[str, Any] | None = None,
    ) -> schemas.ActionResponse:
        payload = schemas.ActionCreate(
            contact_id=contact_id,
            action_type=action_type,
            action_details={
                "message": message,
                "platform": platform,
            }
            if message or platform
            else None,
            status=status,
            timestamp=datetime.utcnow(),
            metadata=extra or {},
        )
        action = crud.log_action(self._db, payload)
        return schemas.ActionResponse.model_validate(action)
