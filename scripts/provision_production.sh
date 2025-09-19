#!/usr/bin/env bash
set -euo pipefail

# Idempotent provisioning script for non-Docker production deploys.
# Supports two modes:
#   1) Env-file mode (default): /etc/ruleiq/ruleiq.env
#   2) Doppler mode (set PROVISION_WITH_DOPPLER=true): /etc/doppler/ruleiq.env + doppler-run
#
# - Creates a system user
# - Installs/updates a Python venv
# - Syncs app code to /opt/ruleiq/app
# - Installs dependencies
# - Installs a systemd service and starts it

APP_USER=${APP_USER:-ruleiq}
APP_GROUP=${APP_GROUP:-ruleiq}
APP_DIR=${APP_DIR:-/opt/ruleiq/app}
VENV_DIR=${VENV_DIR:-/opt/ruleiq/venv}
ENV_DIR=${ENV_DIR:-/etc/ruleiq}
DOPPLER_DIR=${DOPPLER_DIR:-/etc/doppler}
PROVISION_WITH_DOPPLER=${PROVISION_WITH_DOPPLER:-false}

echo "[provision] Creating system user/group: ${APP_USER}"
if ! id -u "${APP_USER}" >/dev/null 2>&1; then
  sudo useradd --system --create-home --shell /bin/false "${APP_USER}"
fi

echo "[provision] Creating directories"
sudo mkdir -p "${APP_DIR}" "${VENV_DIR}" "${ENV_DIR}" "${DOPPLER_DIR}" /var/log/ruleiq
sudo chown -R "${APP_USER}:${APP_GROUP}" "$(dirname "${APP_DIR}")" "${ENV_DIR}" "${DOPPLER_DIR}" /var/log/ruleiq

echo "[provision] Syncing repository to ${APP_DIR}"
if command -v rsync >/dev/null 2>&1; then
  sudo rsync -a --delete --exclude=".git" --exclude="__pycache__" ./ "${APP_DIR}/"
else
  # Fallback copy (no delete)
  sudo cp -rT ./ "${APP_DIR}/"
fi
sudo chown -R "${APP_USER}:${APP_GROUP}" "${APP_DIR}"

echo "[provision] Ensuring Python venv at ${VENV_DIR}"
if [ ! -f "${VENV_DIR}/bin/activate" ]; then
  sudo -u "${APP_USER}" python3 -m venv "${VENV_DIR}"
fi

echo "[provision] Installing/upgrading pip and dependencies"
sudo -u "${APP_USER}" "${VENV_DIR}/bin/pip" install --upgrade pip wheel setuptools
sudo -u "${APP_USER}" "${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt"

if [ "${PROVISION_WITH_DOPPLER}" = "true" ]; then
  echo "[provision] Doppler mode enabled"
  if ! command -v doppler >/dev/null 2>&1; then
    echo "[provision] ERROR: doppler CLI not found. Install with:"
    echo "  curl -Ls https://cli.doppler.com/install.sh | sh"
    exit 1
  fi

  # Seed doppler env file if missing
  if [ ! -f "${DOPPLER_DIR}/ruleiq.env" ]; then
    echo "[provision] Creating ${DOPPLER_DIR}/ruleiq.env (DOPPLER_PROJECT, DOPPLER_CONFIG, DOPPLER_TOKEN)"
    sudo tee "${DOPPLER_DIR}/ruleiq.env" >/dev/null <<'EOF'
# Doppler systemd environment
# Set your Doppler Project, Config, and Service Token
DOPPLER_PROJECT=
DOPPLER_CONFIG=prd
DOPPLER_TOKEN=
EOF
    sudo chown "${APP_USER}:${APP_GROUP}" "${DOPPLER_DIR}/ruleiq.env"
    echo "IMPORTANT: Edit ${DOPPLER_DIR}/ruleiq.env and set DOPPLER_PROJECT and DOPPLER_TOKEN"
  fi

  SYSTEMD_UNIT=/etc/systemd/system/ruleiq-api.service
  echo "[provision] Installing Doppler-backed systemd unit ${SYSTEMD_UNIT}"
  sudo cp "${APP_DIR}/deployment/systemd/ruleiq-api.doppler.service" "${SYSTEMD_UNIT}"
else
  # Env-file mode
  # Seed environment file if missing
  if [ ! -f "${ENV_DIR}/ruleiq.env" ]; then
    echo "[provision] Seeding ${ENV_DIR}/ruleiq.env from env.production.template"
    sudo cp "${APP_DIR}/env.production.template" "${ENV_DIR}/ruleiq.env"
    sudo chown "${APP_USER}:${APP_GROUP}" "${ENV_DIR}/ruleiq.env"
    echo "IMPORTANT: Edit ${ENV_DIR}/ruleiq.env and set DATABASE_URL, JWT_SECRET_KEY, REDIS_PASSWORD, FERNET_KEY"
  fi

  SYSTEMD_UNIT=/etc/systemd/system/ruleiq-api.service
  echo "[provision] Installing systemd unit ${SYSTEMD_UNIT}"
  sudo cp "${APP_DIR}/deployment/systemd/ruleiq-api.service" "${SYSTEMD_UNIT}"
fi

sudo systemctl daemon-reload
sudo systemctl enable ruleiq-api

echo "[provision] Starting service: ruleiq-api"
sudo systemctl restart ruleiq-api
sudo systemctl status --no-pager ruleiq-api || true

echo "[provision] Done. Tail logs with: journalctl -u ruleiq-api -f"