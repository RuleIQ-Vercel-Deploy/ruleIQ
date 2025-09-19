# Deployment Checklist (Backend API) — Non‑Docker, Production

This checklist covers a host-based, systemd-managed deployment. Two supported modes:

- Env-file mode (default): systemd loads `/etc/ruleiq/ruleiq.env`
- Doppler mode (recommended): systemd runs the API under `doppler run`, injecting secrets from Doppler

See also: docs/doppler_setup.md

## 1) Provision the host

Clone the repository on your server and run:

```bash
# Env-file mode (default)
sudo ./scripts/provision_production.sh

# Doppler mode (secrets injected at runtime)
PROVISION_WITH_DOPPLER=true sudo ./scripts/provision_production.sh
```

What this does:
- Creates/updates `/opt/ruleiq/venv` (Python 3.11 venv)
- Syncs code to `/opt/ruleiq/app`
- Installs Python dependencies
- Installs systemd unit:
  - Env-file mode: deployment/systemd/ruleiq-api.service
  - Doppler mode:   deployment/systemd/ruleiq-api.doppler.service (aliased to ruleiq-api.service)

## 2) Configure environment

- Env-file mode:
  - Edit `/etc/ruleiq/ruleiq.env` (seeded from `env.production.template`)
  - Set at least:
    - DATABASE_URL=postgresql://user:pass@host:5432/dbname
    - JWT_SECRET_KEY=your-32+-char-secret
    - REDIS_PASSWORD=strongpassword
    - FERNET_KEY=base64 key (generate with Fernet)
    - ENVIRONMENT=production
    - ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

- Doppler mode:
  - Install Doppler CLI (see docs/doppler_setup.md)
  - Edit `/etc/doppler/ruleiq.env` and set:
    - DOPPLER_PROJECT=your-project
    - DOPPLER_CONFIG=prd
    - DOPPLER_TOKEN=dp.st.your_service_token

## 3) Start and verify

```bash
sudo systemctl daemon-reload
sudo systemctl restart ruleiq-api
journalctl -u ruleiq-api -f
```

Verify health:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/v1/health
```

Run the smoke test (requires jq):

```bash
BASE_URL=http://127.0.0.1:8000 USER_EMAIL=you@example.com USER_PASSWORD='Passw0rd!' ./scripts/smoke_test.sh
```

Notes:
- The service applies Alembic migrations before startup.
- Optional routers are safely included; startup won’t fail if some aren’t ready.

## 4) Put Nginx in front (HTTPS)

Use the sample config and adjust `server_name` and TLS paths:

```bash
sudo cp deployment/nginx/ruleiq.conf /etc/nginx/sites-available/ruleiq.conf
sudo ln -s /etc/nginx/sites-available/ruleiq.conf /etc/nginx/sites-enabled/ruleiq.conf
sudo nginx -t && sudo systemctl reload nginx
```

## 5) Common issues

- Migrations failing:
  - Check `DATABASE_URL` and network access
  - Re-run: `sudo -u ruleiq /opt/ruleiq/venv/bin/alembic upgrade head` (Env-file mode)
  - Doppler: `doppler run --project=$DOPPLER_PROJECT --config=$DOPPLER_CONFIG --token=$DOPPLER_TOKEN -- /opt/ruleiq/venv/bin/alembic upgrade head`

- CORS errors:
  - Set `ALLOWED_ORIGINS` (comma-separated) in env/Doppler

- Redis auth:
  - Ensure `REDIS_PASSWORD` is set (if you use Redis). If `REDIS_URL` is unset, the app defaults to localhost in non-Docker mode.

## 6) Optional: Celery workers (non-Docker)

- Start workers manually to test:
  ```bash
  /opt/ruleiq/venv/bin/celery -A celery_app worker -l info -Q evidence,compliance,notifications,reports
  ```
- You can add a systemd unit later similar to the API service (with or without Doppler).

## 7) Production hardening

- Rotate JWT secret and DB credentials regularly
- Enable Sentry DSN
- Set `FORCE_HTTPS=true` and `SECURE_COOKIES=true` behind TLS
- Access logs and error logs are emitted by Gunicorn; aggregate with your log stack