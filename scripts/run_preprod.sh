#!/usr/bin/env bash
# Self-contained preproduction runner for RuleIQ
# Spins up API + Postgres + Redis + Neo4j + NGINX (optional) using docker-compose.preprod.yml
# Supports Doppler-injected secrets via USE_DOPPLER=1 (and DOPPLER_PROJECT / DOPPLER_CONFIG)

set -euo pipefail

# Resolve project root (this script lives in scripts/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.preprod.yml"

# Select docker compose command
if docker compose version >/dev/null 2>&1; then
  DC=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  DC=(docker-compose)
else
  echo "Error: Docker Compose is not installed. Install Docker and Docker Compose first." >&2
  exit 1
fi

# Parse args
CMD="${1:-up}"         # up | down | logs | ps | rebuild | restart | bash | health
USE_DOPPLER="${USE_DOPPLER:-}"   # if non-empty, run through doppler
DOPPLER_PROJECT="${DOPPLER_PROJECT:-ruleiq}"
DOPPLER_CONFIG="${DOPPLER_CONFIG:-stg}"  # stg by default for preprod
WAIT_HEALTH="${WAIT_HEALTH:-1}"  # 1 = wait for /health after up
HEALTH_URL="${HEALTH_URL:-http://localhost:8000/health}"

# Helper to run a compose command, optionally through doppler
run_compose() {
  if [[ -n "${USE_DOPPLER}" ]]; then
    if ! command -v doppler >/dev/null 2>&1; then
      echo "Error: Doppler CLI not found, but USE_DOPPLER=1 is set." >&2
      exit 1
    fi
    doppler run -p "${DOPPLER_PROJECT}" -c "${DOPPLER_CONFIG}" -- "${DC[@]}" -f "${COMPOSE_FILE}" "$@"
  else
    "${DC[@]}" -f "${COMPOSE_FILE}" "$@"
  fi
}

wait_for_health() {
  local url="${1:-$HEALTH_URL}"
  local timeout="${2:-60}"
  local start ts
  start="$(date +%s)"
  echo "Waiting for health at ${url} (timeout: ${timeout}s)..."
  while true; do
    if command -v curl >/dev/null 2>&1; then
      if curl -fsS "${url}" >/dev/null 2>&1; then
        echo "Service is healthy."
        return 0
      fi
    else
      # Fallback: try Python
      if python3 -c "import urllib.request; urllib.request.urlopen('${url}', timeout=2)" >/dev/null 2>&1; then
        echo "Service is healthy."
        return 0
      fi
    fi
    ts="$(date +%s)"
    if (( ts - start >= timeout )); then
      echo "Timed out waiting for health at ${url}" >&2
      return 1
    fi
    sleep 2
  done
}

case "${CMD}" in
  up)
    echo "Starting preproduction stack (compose: ${COMPOSE_FILE})..."
    run_compose up -d --build
    if [[ "${WAIT_HEALTH}" == "1" ]]; then
      wait_for_health "${HEALTH_URL}" 90 || true
    fi
    echo
    echo "Preproduction is up:"
    echo "- API:     http://localhost:8000"
    echo "- NGINX:   http://localhost:8080 (proxy to API)"
    echo "- PGSQL:   localhost:5434 (db=ruleiq_preprod, user=postgres, pass=postgres)"
    echo "- Redis:   localhost:6381"
    echo "- Neo4j:   http://localhost:7475 (neo4j/neo4jpassword)"
    echo
    echo "Logs: ${DC[*]} -f docker-compose.preprod.yml logs -f app"
    ;;

  down)
    echo "Stopping preproduction stack..."
    run_compose down
    ;;

  logs)
    run_compose logs -f app
    ;;

  ps)
    run_compose ps
    ;;

  rebuild)
    echo "Rebuilding images (no cache)..."
    run_compose build --no-cache
    ;;

  restart)
    run_compose restart app
    ;;

  bash)
    # Open a shell in the app container
    if run_compose exec app bash -lc 'echo "Opened bash in app container"' 2>/dev/null; then
      :
    else
      run_compose exec app sh -lc 'echo "Opened sh in app container"'
    fi
    ;;

  health)
    wait_for_health "${HEALTH_URL}" 60
    ;;

  *)
    cat >&2 <<EOF
Usage: $(basename "$0") [command]

Commands:
  up         Start the preproduction stack (default)
  down       Stop and remove containers
  logs       Tail app logs
  ps         Show container status
  rebuild    Rebuild images with no cache
  restart    Restart the app service
  bash       Open a shell in the app container
  health     Check /health endpoint

Environment:
  USE_DOPPLER=1           Use Doppler to inject secrets (default: off)
  DOPPLER_PROJECT=ruleiq  Doppler project (default: ruleiq)
  DOPPLER_CONFIG=stg      Doppler config (default: stg)
  WAIT_HEALTH=1           Wait for /health after up (default: 1)
  HEALTH_URL=http://localhost:8000/health

Examples:
  # Start with local defaults (self-contained)
  $(basename "$0") up

  # Start with Doppler 'stg' config
  USE_DOPPLER=1 DOPPLER_PROJECT=ruleiq DOPPLER_CONFIG=stg $(basename "$0") up

  # Stop stack
  $(basename "$0") down

  # Tail logs
  $(basename "$0") logs
EOF
    exit 1
    ;;
esac