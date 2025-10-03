# _req_pages – Requirements Pages System

This folder contains artifacts for requirement-specific pages built strictly from vetted PASS components.

Prerequisites
- Node 18+, pnpm
- Storybook and quality gate set up under `frontend/.storybook` and `_index_ops/quality_gate`

How to add a requirement
1. Append an object to `requirements.json` (key, title, status, priority, owner, notes[])
2. Run the rebuild script (see below) to scaffold/update the page and reports

Conformance
- The page must use only tokenized styles per `_index_ops/quality_gate/style_rules.json`
- Lint script must report PASS/WARN only (no FAIL)
- Dark mode context; WCAG AA focus states

Outputs per requirement
- `wireframes/<key>.png|svg` (if Excalidraw MCP available)
- `reports/<key>.json|md`
- `screenshots/<key>.png` (Playwright, 1440×900 DPR=1)
- Index entries in `INDEX.md` and `req_index.json`

Rebuild script (idempotent)
- `./_req_pages/rebuild_req_pages.sh`
  - Validates JSON schema
  - Ensures/updates Next route scaffold (or React Router fallback)
  - Runs conformance check and screenshot
  - Updates index files
  - Exits non-zero on any FAIL
