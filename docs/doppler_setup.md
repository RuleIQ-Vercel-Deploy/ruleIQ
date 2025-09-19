# Doppler Integration (Production)

This project supports Doppler for secrets management in both CI and production.

Two supported deployment modes:
- Env-file mode (default): systemd loads /etc/ruleiq/ruleiq.env
- Doppler mode (recommended): systemd runs the API under doppler run, loading secrets from your Doppler project/config

## 1) Install Doppler CLI

On your server:
```bash
curl -Ls https://cli.doppler.com/install.sh | sudo sh
doppler --version
```

## 2) Create a Doppler Service Token

From the Doppler dashboard:
- Create a Service Token with read access to your production config.
- Note the token value (we'll store it locally in an env file readable by systemd).

## 3) Provision with Doppler

Use the provisioning script with Doppler mode:

```bash
PROVISION_WITH_DOPPLER=true sudo ./scripts/provision_production.sh
```

This will:
- Ensure /opt/ruleiq/app and /opt/ruleiq/venv exist and are set up
- Create /etc/doppler/ruleiq.env if missing:
  - DOPPLER_PROJECT=
  - DOPPLER_CONFIG=prd
  - DOPPLER_TOKEN=
- Install the Doppler-backed systemd unit:
  - /etc/systemd/system/ruleiq-api.service (based on deployment/systemd/ruleiq-api.doppler.service)
- Enable and start the service

Edit /etc/doppler/ruleiq.env:

```
DOPPLER_PROJECT=your-project
DOPPLER_CONFIG=prd
DOPPLER_TOKEN=dp.st.your_service_token
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl restart ruleiq-api
journalctl -u ruleiq-api -f
```

## 4) How it works

The Doppler systemd unit runs:
- `doppler run --project=$DOPPLER_PROJECT --config=$DOPPLER_CONFIG --token=$DOPPLER_TOKEN -- alembic upgrade head`
- `doppler run --project=$DOPPLER_PROJECT --config=$DOPPLER_CONFIG --token=$DOPPLER_TOKEN -- gunicorn ... main:app`

All environment variables expected by the app (DATABASE_URL, JWT_SECRET_KEY, REDIS_URL, GOOGLE_API_KEY, FERNET_KEY, etc.) must be defined in Doppler.

## 5) Health and Smoke Test

- Verify health:
  ```bash
  curl http://127.0.0.1:8000/health
  ```
- Smoke test:
  ```bash
  BASE_URL=http://127.0.0.1:8000 USER_EMAIL=you@example.com USER_PASSWORD='Passw0rd!' ./scripts/smoke_test.sh
  ```

## 6) CI and GitHub Actions

The repo already integrates Doppler in CI workflows as needed. For further integration:
- Store Doppler tokens as GitHub secrets
- Use dopplerhq/cli-action in workflows

## 7) Security Notes

- Keep /etc/doppler/ruleiq.env readable only by the system user/group:
  ```bash
  sudo chown ruleiq:ruleiq /etc/doppler/ruleiq.env
  sudo chmod 600 /etc/doppler/ruleiq.env
  ```
- Do not commit secrets to the repository; Doppler injects them at runtime.

For help configuring Doppler projects/configs or mapping variables to app settings, ask and I can tailor the setup.