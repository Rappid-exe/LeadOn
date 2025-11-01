#!/usr/bin/env bash
set -euo pipefail

# Default to Postgres URL; allow SQLite for local override
: "${DATABASE_URL:=postgresql+psycopg://user:pass@db:5432/sales_crm}"
export DATABASE_URL

# Auth must be enabled in production
: "${DISABLE_AUTH:=false}"
export DISABLE_AUTH

# Run migrations
alembic -c /app/hackathon/alembic.ini upgrade head

# Start Gunicorn with Uvicorn workers (1 per CPU as a sane default)
exec gunicorn hackathon.crm.api:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers "${GUNICORN_WORKERS:-1}" \
  --bind 0.0.0.0:8000 \
  --timeout "${GUNICORN_TIMEOUT:-60}"
