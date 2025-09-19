# Deployment Checklist (Backend API)

This document outlines a minimal, reliable process to deploy the backend API using Docker Compose.

## 1) Prepare Environment

Copy the production template and fill in required secrets:

```bash
cp env.production.template .env.prod
```

Required values:
- DATABASE_URL (PostgreSQL, e.g., postgresql://user:pass@host:5432/dbname)
- JWT_SECRET_KEY (>=32 chars)
- REDIS_PASSWORD (strong password used by Redis in docker-compose)
- FERNET_KEY (base64 key; generate: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`)

Optional:
- GOOGLE_API_KEY (only if AI features are enabled)
- SENTRY_DSN (if using Sentry)
- REDIS_URL (leave empty to let compose default to redis://:${REDIS_PASSWORD}@redis:6379/0)

## 2) Smoke-test with HTTP-only Nginx (no TLS)

```bash
docker compose -f docker-compose.prod.http.yml --env-file .env.prod up -d app redis nginx
```

Verify:
```bash
curl http://localhost/health
curl http://localhost/api/v1/health
docker compose -f docker-compose.prod.http.yml logs -f app nginx
```

Notes:
- The container entrypoint waits for the database, applies Alembic migrations, and then starts Uvicorn.
- If your database is external (e.g., Neon), ensure its firewall allows the server IP.

## 3) Switch to TLS (HTTPS) when ready

Place TLS certs:
- `./ssl/cert.pem`
- `./ssl/key.pem`

Start TLS stack:
```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

Verify:
```bash
curl -k https://localhost/health
curl -k https://localhost/api/v1/health
docker compose -f docker-compose.prod.yml logs -f app nginx
```

## 4) Optional: Start Celery workers (when tasks are needed)

Services are under the `celery` profile so they won't start by default.

```bash
docker compose -f docker-compose.prod.http.yml --env-file .env.prod --profile celery up -d celery_worker celery_beat
```

Sanity check:
```bash
# returns "pong"
docker compose -f docker-compose.prod.http.yml exec app python -c "from celery_app import ping; r=ping.delay(); print(r.get(timeout=10))"
```

## 5) Health and Logs

- Health endpoints:
  - `/health`
  - `/api/v1/health`
  - `/api/v1/health/detailed`
- Logs:
  - `docker compose logs -f app`
  - `docker compose logs -f nginx`

## 6) Common Issues

- Migrations failing:
  - Check `DATABASE_URL` and network access to database.
  - Re-run: `docker compose exec app alembic upgrade head`

- Redis auth:
  - Ensure `REDIS_PASSWORD` is set; compose defaults REDIS_URLs using that password.

- Router import issues:
  - Optional routers are included via a safe loader; the API will still start. Check logs for any skipped routers.

## 7) Production Hardening (later)

- Rotate JWT secret and DB creds regularly.
- Move secrets to a secret manager (AWS SM or similar).
- Enable Sentry and metrics.
- Put Nginx behind a managed LB with automatic cert renewal.