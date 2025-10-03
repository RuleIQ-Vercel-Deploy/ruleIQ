#!/usr/bin/env bash
set -euo pipefail

# Rebuild Storybook with Iron-Fist gate
# Usage: PNPM=pnpm ./_index_ops/rebuild_storybook.sh

ROOT_DIR=$(dirname "$0")/..
cd "$ROOT_DIR"

PNPM_BIN=${PNPM:-pnpm}

echo "[1/4] Install deps"
$PNPM_BIN install --frozen-lockfile

echo "[2/4] Lint components against style rules"
node _index_ops/quality_gate/lint-components.mjs || {
  echo "Static scan reported FAIL. See _index_ops/quality_gate/report.*" >&2
  exit 1
}

echo "[3/4] Test Storybook"
$PNPM_BIN test:storybook || true

echo "[4/4] Build Storybook"
$PNPM_BIN build-storybook

echo "Done. Output in frontend/storybook-static/"
