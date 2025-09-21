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
# Neon Database URL credentials - EXAMPLE ONLY
# Replace these with actual patterns from your git history scan
postgresql+asyncpg://[USERNAME]:[PASSWORD]@[HOST]/[DATABASE]
postgresql+asyncpg://<redacted-neon-url>

postgresql://[USERNAME]:[PASSWORD]@[HOST]/[DATABASE]
postgresql://<redacted-neon-url>

# Stack Auth keys - EXAMPLE PATTERNS
# UUID pattern for project IDs
[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}
<redacted-stack-project-id>

# Client key pattern
pck_[a-z0-9]{40}
<redacted-stack-client-key>

# Server key patterns
ssk_[a-z0-9]{40}
<redacted-stack-server-key>

ssk_[a-z0-9]{40}
<redacted-stack-server-key>

# JWT/Fernet secrets - EXAMPLE PATTERNS
# Base64 encoded secret pattern
[A-Za-z0-9+/]{40,}=
<redacted-jwt-secret>

dev-secret-key-change-for-production
<redacted-secret-key>

dev-32-character-encryption-key
<redacted-encryption-key>

# Fernet key pattern
[A-Za-z0-9_-]{43}=
<redacted-fernet-key>

# OpenAI / Google AI keys - EXAMPLE PATTERNS
# OpenAI API key pattern
sk-proj-[A-Za-z0-9_-]{100,}
<redacted-openai-key>

# Google API key pattern
AIzaSy[A-Za-z0-9_-]{33}
<redacted-google-api-key>

# JWT token patterns
# JWT pattern (header.payload.signature)
eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+
<redacted-jwt-token>

eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+
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
