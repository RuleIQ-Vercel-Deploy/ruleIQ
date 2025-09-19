# Repository Guidelines

## Project Structure & Module Organization
- `api/`, `app/`, `core/`, `services/`, and `middleware/` hold the Python FastAPI backend; shared settings live under `config/` and `database/`.
- `frontend/` contains the Next.js + TypeScript client with Storybook stories under `frontend/stories/` and component tests in `frontend/tests/`.
- `tests/` is the canonical Python test suite; Postman and Newman artefacts sit in `api/`.
- Automation lives in `scripts/` (`scripts/ci/scan_secrets.py`, `scripts/run_tests_chunked.py`) and security/process docs in `docs/`.
- Experimental services such as graph visualisation are isolated in `visualization-backend/`.

## Build, Test, and Development Commands
- Backend: `python -m venv .venv && pip install -r requirements.txt` then `uvicorn main:app --reload`.
- Frontend: `pnpm install` at repo root, then `pnpm --filter frontend dev` for local dev and `pnpm --filter frontend build` for production bundles.
- Secret guardrail: `python3 scripts/ci/scan_secrets.py` must return “No secrets detected” before commits.
- Python tests: `make test-groups` for the full suite or `pytest tests/unit/` for a focused run.
- Frontend tests: `pnpm --filter frontend test` (unit), `pnpm --filter frontend test:e2e` (Playwright), `pnpm --filter frontend lint` and `pnpm --filter frontend typecheck` before PRs.

## Coding Style & Naming Conventions
- Python: 4-space indentation, type hints required, and `ruff` enforces imports/formatting (`ruff.toml`). Prefer descriptive snake_case for modules/functions and PascalCase for classes.
- Frontend: follow ESLint + Prettier defaults (`pnpm --filter frontend lint:fix`, `pnpm --filter frontend format`). Components sit in PascalCase files (`MyComponent.tsx`); hooks use `useSomething` naming.
- JSON/YAML config values should remain placeholder-based—never commit live secrets.

## Testing Guidelines
- Pytest discovers `test_*.py`; mark long-running suites with `@pytest.mark.slow` so `make test-fast` stays lean. Coverage gate is 70% (`make test-coverage`).
- Vitest looks for `*.test.ts(x)` under `frontend/tests/`; E2E specs belong in `frontend/tests/e2e/`. Keep snapshots in the same directory as the component they verify.
- Record the test group or command you executed in the PR description.

## Security & Configuration Tips
- Keep `.env*` files untracked; use `env.template` or `env.comprehensive.template` for placeholders and load real values via Doppler/CI secrets.
- Run `pre-commit run --all-files` before pushing; it executes the secret scanner and formatting hooks locally.
- Avoid expanding CORS, CSP, or OAuth callback surfaces without updating `docs/security/` and the relevant tests.

## Commit & Pull Request Guidelines
- Use Conventional Commit prefixes (`feat:`, `fix:`, `chore:`). Reference ticket IDs when available (e.g., `feat(auth-123): add PKCE verifier`).
- PRs should include: summary, verification commands (`make test-groups`, `pnpm test`), security considerations, and UI screenshots for visual changes.
- Request review from the owning squad; re-run the secret scanner and lint/typecheck pipelines after addressing feedback.
