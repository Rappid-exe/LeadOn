# Sales Workflow Agentic CRM

This directory hosts the Python CRM microservice and agent helpers that power the hackathon project. The service exposes a FastAPI application with SQLAlchemy models that align with the shared data contracts described in the project brief.

## Features

- Contacts, actions, campaigns, and relationship tracking tables with automatic timestamps.
- REST API for creating, searching, and bulk importing contacts.
- Aggregated overview endpoint supplying dashboard metrics for the frontend.
- Lightweight agent wrapper (`CrmPopulationAgent`) that scrapers and automations can reuse when pushing data into the CRM.

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn hackathon.crm.api:app --reload
```

The API will default to a local SQLite database (`hackathon_crm.db`). Override the `DATABASE_URL` environment variable to use PostgreSQL in production.

## Environment Variables

- `DATABASE_URL`: SQLAlchemy connection string.

## Useful Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET` | `/api/contacts` | List contacts with pagination, search, and filtering |
| `POST` | `/api/contacts` | Create or update a single contact |
| `POST` | `/api/contacts/bulk` | Bulk upsert contacts |
| `GET` | `/api/stats/overview` | Aggregated metrics for the CRM dashboard |
| `POST` | `/api/actions` | Log a LinkedIn automation action |

Use the `/health` endpoint for readiness checks.

## Production Run (containers)

- Build & run locally:
  ```bash
  docker compose up -d --build
  ```
- API: http://localhost:8000/docs
- Frontend: http://localhost:5173

**Notes**

- Gunicorn manages Uvicorn workers for multi-core.
- Use Postgres in production; run `alembic upgrade head` on deploy (the entrypoint already handles this).
- Set `DISABLE_AUTH=false` and narrow `CORS_ORIGINS`.
