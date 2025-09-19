# Secret Rotation Plan (the-bmad-experiment)

The following repository artifacts previously contained production or staging credentials. New values must be provisioned before merging this branch and force-pushing the cleaned history.

## Credentials to Rotate

| Secret | Where it was exposed | Owner | Rotation Notes |
| --- | --- | --- | --- |
| Neon `DATABASE_URL` | `env.template`, `env.comprehensive.template`, `alembic.ini`, test fixtures | Platform / DBA | Issue new connection string, revoke old user, update Doppler / infrastructure secrets. |
| Stack Auth project + keys | `env.template`, `env.comprehensive.template`, `frontend/.env.local` | Identity Platform | Create new Stack project keys; update Doppler and Vercel. |
| JWT signing secret | `env.template`, `env.comprehensive.template` | Backend | Generate new 32-byte secret, rotate refresh tokens. |
| Fernet encryption key | `env.template`, `env.comprehensive.template` | Backend | Re-encrypt stored payloads once new key deployed. |
| OpenAI API key | `env.template`, `env.comprehensive.template`, Postman environments | AI Platform | Create new key, revoke exposed key. |
| Google AI API key | `env.comprehensive.template`, Postman environments | AI Platform | Regenerate key, update service accounts. |
| Sample JWT token | `api/basic_results.json` | QA | Generate fresh token when needed; do not commit real tokens. |

## Required Follow-up

1. **Credential rotation** – execute the rotations above and capture the updated values in Doppler / secret managers. Avoid committing secrets; rely on runtime injection.
2. **History rewrite** – after rotations, run the provided script (`scripts/tools/purge_secrets.sh`, to be added) or the documented `git filter-repo` commands to remove leaked blobs from Git history, then force-push `the-bmad-experiment`.
3. **Communication** – notify downstream teams (QA, integrations) about rotated credentials to avoid service interruptions.
4. **Validation** – run the new secret scanner locally and in CI to ensure the repository is free of leaked values before merging.

_Last updated: $(date +%Y-%m-%d)_
