"""High level agent used by scrapers to persist contacts into the CRM service."""

from __future__ import annotations

import logging
from typing import Iterable

import httpx

from ..crm import schemas

logger = logging.getLogger(__name__)


class CrmPopulationAgent:
    """Helper class wrapping the CRM HTTP API for ingestion pipelines."""

    def __init__(self, base_url: str = "http://localhost:8000/api") -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self._base_url, timeout=10.0)

    def upsert_contacts(self, contacts: Iterable[schemas.ContactCreate]) -> list[schemas.ContactResponse]:
        """Send a batch of contacts to the CRM service using the bulk endpoint."""

        payload = [contact.model_dump() for contact in contacts]
        if not payload:
            return []
        logger.debug("Sending %s contacts to CRM", len(payload))
        response = self._client.post("contacts/bulk", json=payload)
        response.raise_for_status()
        data = response.json()
        return [schemas.ContactResponse.model_validate(item) for item in data]

    def log_action(self, action: schemas.ActionCreate) -> schemas.ActionResponse:
        """Persist an automation action for traceability."""

        response = self._client.post("actions", json=action.model_dump())
        response.raise_for_status()
        return schemas.ActionResponse.model_validate(response.json())

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "CrmPopulationAgent":  # pragma: no cover - context manager sugar
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - context manager sugar
        self.close()
