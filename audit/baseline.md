# ruleIQ PHASE 1 — Inventory & Baseline

Generated: 2025-08-29T00:00:00Z
Repo: OmarA1-Bakri/ruleIQ

## System Map

```mermaid
flowchart TB
  subgraph Frontend [Next.js (frontend/)]
    FE[App Router + TypeScript]
    APIClient[API Client <frontend/lib/api/>]
    State[Zustand Stores]
    Query[TanStack Query]
    FE --> APIClient
    APIClient --> Query
    APIClient --> State
  end

  subgraph Backend [FastAPI (api/ routers)]
    Routers[api/routers/*]
    Services[services/*]
    Auth[JWT + RBAC]
    Errors[utils/error_handlers.py]
    Routers --> Services
    Routers --> Auth
    Routers --> Errors
  end

  subgraph DataStores
    PG[(PostgreSQL)]
    Neo4j[(Neo4j)]
    Redis[(Redis)]
  end

  subgraph AI [AI Services]
    IQ[services/ai/*]
    Circuit[circuit_breaker.py]
    Safety[safety_manager.py]
    IQ --> Circuit
    IQ --> Safety
  end

  FE --> Backend
  Backend --> PG
  Backend --> Neo4j
  Backend --> Redis
  Backend --> AI

  classDef boundary stroke:#f66,stroke-width:2px,stroke-dasharray: 3 3;
  class Backend,DataStores boundary;
```

Trust boundaries:
- Internet ↔ Frontend (browser)
- Frontend ↔ Backend (API, TLS)
- Backend ↔ DataStores (network ACLs)
- Backend ↔ External AI APIs (egress with API keys)

Third-party integrations:
- Google Gemini / OpenAI (AI models)
- Neon PostgreSQL (managed Postgres)
- Redis (cache/session)

## Environment Versions

- Node: pending
- PNPM: pending
- NPM: pending
- Python: pending
- Pip: pending

Tools:
- ruff: pending
- mypy/pyright: pending
- bandit: pending
- pip-audit/safety: pending
- eslint: pending
- tsc: pending
- trivy (fs/config): pending
- dockle: pending
- gitleaks: pending
- cyclonedx-bom: pending
- cyclonedx-npm: pending

## Scan Summary (to be populated)

- Python dependency audit: see logs
- Node audit: see logs
- Static analysis (Python): see logs
- Lint/type (Node): see logs
- Secrets scan: see logs
- Container/FS scan: see logs

## Artifacts

- Logs: /audit/logs/
- SBOMs: /audit/sbom/
- This baseline: /audit/baseline.md

## Notes

- Phase 1 is non-destructive. No migrations or app changes.
- Missing tools will be noted and proposed for CI in Phase 5.

RuleIQ Audit Baseline - 2025-08-29T13:46:57+00:00
Environment:
- Node: v22.12.0
- PNPM: 9.15.1
- Python: Python 3.12.8
- Pip: pip 24.3.1 from /home/ubuntu/.pyenv/versions/3.12.8/lib/python3.12/site-packages/pip (python 3.12)

Scans started at 2025-08-29T13:46:58+00:00
