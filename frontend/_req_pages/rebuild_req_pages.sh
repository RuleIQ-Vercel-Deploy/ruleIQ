#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(dirname "$0")/..
cd "$ROOT_DIR"

PNPM_BIN=${PNPM:-pnpm}
REQ_DIR="_req_pages"
REPORT_DIR="$REQ_DIR/reports"
SCREEN_DIR="$REQ_DIR/screenshots"
WIREFRAME_DIR="$REQ_DIR/wireframes"
INDEX_MD="$REQ_DIR/INDEX.md"
INDEX_JSON="$REQ_DIR/req_index.json"
STYLE_RULES="_index_ops/quality_gate/style_rules.json"

mkdir -p "$REPORT_DIR" "$SCREEN_DIR" "$WIREFRAME_DIR"

# Validate requirements.json is an array with required fields
node - <<'NODE'
const fs=require('fs');
const p='_req_pages/requirements.json';
const data=JSON.parse(fs.readFileSync(p,'utf8'));
if(!Array.isArray(data)) { console.error('requirements.json must be an array'); process.exit(1); }
for(const r of data){
  for(const k of ['key','title','status','priority','owner','notes']){
    if(!(k in r)) { console.error(`Missing field ${k} in requirement ${JSON.stringify(r)}`); process.exit(1); }
  }
}
NODE

# For this run, focus on single requirement
KEY=$(node -e "const d=require('./_req_pages/requirements.json'); console.log(d[0].key)")
TITLE=$(node -e "const d=require('./_req_pages/requirements.json'); console.log(d[0].title)")

# Conformance check: ensure style rules exist
[ -f "$STYLE_RULES" ] || { echo "Missing $STYLE_RULES"; exit 1; }

# Page-level conformance (static scan of kept components)
node _index_ops/quality_gate/lint-components.mjs || { echo "Component lint FAIL"; exit 1; }

# Placeholder page-level report (extend with actual page scan once scaffolded)
cat > "$REPORT_DIR/$KEY.md" <<EOF
# Conformance Report – $TITLE

Status: PASS (components static scan)
Notes: Page scaffold pending; using PASS components only is enforced by gate.
EOF

cat > "$REPORT_DIR/$KEY.json" <<EOF
{ "key": "$KEY", "status": "PASS", "notes": ["Components static scan passed or warned only."] }
EOF

# Update index files
cat > "$INDEX_MD" <<EOF
# Requirements Index

- $TITLE (/requirements/$KEY)
EOF

cat > "$INDEX_JSON" <<EOF
[
  {
    "key": "$KEY",
    "route": "/requirements/$KEY",
    "title": "$TITLE",
    "last_commit_iso": "",
    "screenshot": "$SCREEN_DIR/$KEY.png",
    "wireframe": "$WIREFRAME_DIR/$KEY.png",
    "conformance": { "status": "PASS", "notes": ["Components static scan only in this pass."] }
  }
]
EOF

echo "Rebuild complete (scaffold-only). See $REQ_DIR."