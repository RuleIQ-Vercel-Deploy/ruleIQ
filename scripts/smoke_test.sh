#!/usr/bin/env bash
set -euo pipefail

# Simple smoke test for a running ruleIQ API instance (non-Docker)
# Requirements: curl, jq
# Usage:
#   BASE_URL=http://127.0.0.1:8000 USER_EMAIL=test@example.com USER_PASSWORD=Passw0rd! ./scripts/smoke_test.sh

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
USER_EMAIL="${USER_EMAIL:-test@example.com}"
USER_PASSWORD="${USER_PASSWORD:-Passw0rd!}"

echo "[smoke] Base URL: ${BASE_URL}"

function json() {
  jq -r "$1" 2>/dev/null || true
}

echo "[smoke] Health check..."
curl -fsS "${BASE_URL}/health" | jq .

echo "[smoke] Register (idempotent; may 409 if exists)..."
register_payload=$(jq -n --arg email "${USER_EMAIL}" --arg pwd "${USER_PASSWORD}" '{email:$email, password:$pwd}')
curl -fsS -X POST "${BASE_URL}/api/v1/auth/register" \
  -H "content-type: application/json" \
  -d "${register_payload}" | jq . || true

echo "[smoke] Login..."
login_payload=$(jq -n --arg email "${USER_EMAIL}" --arg pwd "${USER_PASSWORD}" '{email:$email, password:$pwd}')
login_resp=$(curl -fsS -X POST "${BASE_URL}/api/v1/auth/login" \
  -H "content-type: application/json" \
  -d "${login_payload}")

access_token=$(echo "${login_resp}" | json '.access_token')
if [[ -z "${access_token}" || "${access_token}" == "null" ]]; then
  echo "[smoke] Failed to get access token"
  echo "${login_resp}"
  exit 1
fi
echo "[smoke] Access token acquired"

echo "[smoke] /api/v1/auth/me ..."
curl -fsS -H "authorization: Bearer ${access_token}" "${BASE_URL}/api/v1/auth/me" | jq .

echo "[smoke] List assessments (expected empty initially)..."
curl -fsS -H "authorization: Bearer ${access_token}" "${BASE_URL}/api/v1/assessments" | jq .

echo "[smoke] OK"