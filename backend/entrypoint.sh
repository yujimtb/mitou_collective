#!/bin/sh
set -eu

echo "Running database migrations..."
alembic upgrade head

if [ "${SEED_ON_STARTUP:-false}" = "true" ]; then
  echo "Seeding demo dataset..."
  python manage.py seed
fi

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
