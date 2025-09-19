# Secret Handling Guardrails

This document explains the day-to-day guardrails that keep `the-bmad-experiment` free from
credential leaks after the cleanup.

## Local Development
- Install pre-commit once by running `pip install pre-commit && pre-commit install`.
- Commit workflows automatically run `scripts/ci/scan_secrets.py`. You can run it on demand via
  `python3 scripts/ci/scan_secrets.py`.
- Store real secrets in Doppler, environment managers, or local `.env` files that are **never**
  committed. Use the provided templates (`env.template`, `env.comprehensive.template`) with
  placeholder values only.
- Replace any static tokens in tests/fixtures with obvious placeholders (e.g., `mock-access`,
  `dummy-refresh`). If a test genuinely requires a long-lived credential, fetch it from the runtime
  environment inside the test setup instead of hard coding it.

## CI Expectations
- The GitHub Actions workflow executes the same scanner early in the job to prevent accidental
  leaks from reaching deploy stages.
- Failing scans must be remediated by redacting the value or documenting intentional placeholders
  in the scanner.

## Responding to Findings
1. Investigate the file/location reported by the scanner.
2. If the value is a real secret, rotate it immediately (see `SECRET_ROTATION_PLAN.md`) and replace
   it with a placeholder.
3. If the finding is a false positive, do one of the following:
   - Shorten the placeholder so it looks less like a credential (`mock-access` instead of
     `mock-access-token-123`).
   - Update the scanner heuristics only when the placeholder pattern is expected to recur across the
     repository.
4. Re-run `python3 scripts/ci/scan_secrets.py` to confirm a clean result before committing.

## Future Remediation & History Rewrite
- After all rotations are complete, use the forthcoming `scripts/tools/purge_secrets.sh` (or the
  documented `git filter-repo` commands) to rewrite history and excise leaked blobs before
  force-pushing `the-bmad-experiment`.
- Capture the new secret material in Doppler/infra managers and share updates with downstream teams.

_Last updated: $(date +%Y-%m-%d)_
