#!/usr/bin/env bash
# Remove historical secrets from Git using git-filter-repo.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${REPO_ROOT}" ]]; then
  echo "❌ This script must be run inside a Git repository." >&2
  exit 1
fi

cd "${REPO_ROOT}"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "❌ Working tree is dirty. Commit or stash changes before rewriting history." >&2
  exit 1
fi

if ! command -v git-filter-repo >/dev/null 2>&1 && ! command -v git filter-repo >/dev/null 2>&1; then
  cat >&2 <<'MSG'
❌ git-filter-repo is required.
Install via:
  pip install git-filter-repo
or
  brew install git-filter-repo (macOS)
MSG
  exit 1
fi

if [[ "${ALLOW_HISTORY_REWRITE:-}" != "true" ]]; then
  cat >&2 <<'MSG'
⚠️  History rewrite is destructive.
Set ALLOW_HISTORY_REWRITE=true to acknowledge you have backups and rotated secrets.
Example:
  ALLOW_HISTORY_REWRITE=true scripts/tools/purge_secrets.sh
MSG
  exit 1
fi

BACKUP_REF="rewrite-backup-$(date +%Y%m%d-%H%M%S)"
BACKUP_BRANCH="refs/backup/${BACKUP_REF}"

echo "📦 Creating safety tag ${BACKUP_REF}..."
git update-ref "${BACKUP_BRANCH}" HEAD

tmpfile="$(mktemp)"
trap 'rm -f "${tmpfile}"' EXIT

cat > "${tmpfile}" <<'EOF_REPLACEMENTS'
# Each block is original text, newline, replacement, newline.
# Neon Database URL credentials
postgresql+asyncpg://neondb_owner:npg_s0JhnfGNy3Ze@ep-sweet-truth-a89at3wo-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require
postgresql+asyncpg://<redacted-neon-url>

postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require
postgresql://<redacted-neon-url>

# Stack Auth keys
5771eac7-350a-43b0-9fe2-0ca6a0b8ea17
<redacted-stack-project-id>

pck_bga2tny5stehdhyay71bj4pmzstfar6gpvh8n63q63c00
<redacted-stack-client-key>

ssk_0wkry6dwy3z0a8gwhjcxywwzcqzb1nbzp1gknfpn7bh60
<redacted-stack-server-key>

ssk_sy6z4a4h84hca9mybvf8wzn5td696wjsvydkpbnh52400
<redacted-stack-server-key>

# JWT/Fernet secrets
nTDlGluRj39drsQ+IczE7pFw0okljEY/tKsLa+mB3d8=
<redacted-jwt-secret>

dev-secret-key-change-for-production
<redacted-secret-key>

dev-32-character-encryption-key
<redacted-encryption-key>

PiuMdniC0TBtnLTactkEi7TZSpQq_PA_tkg5olwDQbM=
<redacted-fernet-key>

# OpenAI / Google AI keys from env files and Postman collections
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
<redacted-openai-key>

AIzaSyAp13qdjwpFbqi85X2uK5K2exj7tX6I5eE
<redacted-google-api-key>

# Sample JWT tokens
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MWIxOTMwZC05YzI0LTQwZWItYmE3Ny02YzViNTA4YjNiNDEiLCJleHAiOjE3NTU5NDAxNDgsInR5cGUiOiJhY2Nlc3MiLCJpYXQiOjE3NTU5MzgzNDh9.iAoqj2FrDDW0-ckb6A74I_KKetm87MCH6astHxxk2aI
<redacted-jwt-token>

eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIn0.signature
<redacted-jwt-token>

# Google API references in manifests
sk-management-framework
sk-management-framework-redacted
EOF_REPLACEMENTS

echo "🧹 Running git-filter-repo..."
if command -v git-filter-repo >/dev/null 2>&1; then
  FILTER_REPO="git-filter-repo"
else
  FILTER_REPO="git filter-repo"
fi

${FILTER_REPO} --force --replace-text "${tmpfile}"

echo "✅ History rewrite complete. Backup ref stored at ${BACKUP_BRANCH}."
echo "Next steps:"
echo "  1. Verify: git log --stat --since=1.month"
echo "  2. Force push once satisfied: git push origin --force --all && git push origin --force --tags"
echo "  3. Coordinate with team to reclone repositories."
