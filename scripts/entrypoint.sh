#!/bin/sh
set -eu

echo "[entrypoint] Environment: ${ENVIRONMENT:-unknown}"
echo "[entrypoint] Waiting for database..."
python -u scripts/wait_for_db.py

echo "[entrypoint] Running migrations..."
if ! alembic upgrade head; then
  echo "[entrypoint] Alembic migration failed"
  exit 1
fi

echo "[entrypoint] Starting Uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000