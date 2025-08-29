# Audit Phase 1 — Inventory & Baseline (work in progress)

Branch: devin/1756476145-phase1-baseline
PR: https://github.com/OmarA1-Bakri/ruleIQ/pull/40
Generated: 2025-08-29T14:05:10Z

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

Third-party integrations (docs):
- Google Gemini / OpenAI (AI models)
- Neon PostgreSQL (managed Postgres)
- Redis (cache/session)

## Environment & Tool Versions

Environment detected:
- Node: v22.12.0
- PNPM: 9.15.1
- Python: Python 3.12.8
- Pip: pip 24.3.1

Tool availability on this VM:
- ruff: missing
- mypy: missing
- pyright: missing
- bandit: missing
- pip-audit: missing
- safety: missing
- eslint: missing
- tsc: available via npx
- trivy: missing
- gitleaks: missing
- cyclonedx-bom: missing
- cyclonedx-npm: available via npx
- dockle: missing

Note: Missing tools will be proposed for CI in Phase 5; local install can be performed if approved.

## Scan Status

Initiated non-destructive scans; artifacts will be written under /audit/logs and /audit/sbom as tools become available.

- Python dependency export: audit/logs/requirements.freeze.txt (present)
- Python vulnerability audit: pending (pip-audit/safety missing)
- Python static analysis: pending (ruff/mypy/bandit missing)
- Frontend audits:
  - Install: attempted with pnpm (see logs when available)
  - npm/pnpm audit: pending
  - ESLint: pending (eslint missing)
  - Typecheck: pending (tsc via npx; will capture on run)
- Secrets (gitleaks): pending (missing)
- Trivy FS/config: pending (missing)
- Dockle: best-effort (requires Docker + dockle)
- SBOMs:
  - Python: pending (cyclonedx-bom missing)
  - Node: pending (will use npx @cyclonedx/cyclonedx-npm)

## Artifacts

- Logs: /audit/logs/
- SBOMs: /audit/sbom/
- This baseline: /audit/baseline.md

## Notes

- Phase 1 is non-destructive; no app code changes or migrations.
- This file will be updated as logs and SBOMs are generated.
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

Environment/tool versions (2025-08-29T14:04:23+00:00):
v22.12.0
9.15.1
10.8.3
Python 3.12.8
pip 24.3.1 from /home/ubuntu/repos/ruleIQ/.venv/lib/python3.12/site-packages/pip (python 3.12)
ruff: missing
mypy: missing
pyright: missing
bandit: missing
pip-audit: missing
safety: missing
eslint: missing
Need to install the following packages:
tsc@2.0.4
Ok to proceed? (y) 


[41m                                                                               [0m
[41m[37m                This is not the tsc command you are looking for                [0m
[41m                                                                               [0m

To get access to the TypeScript compiler, [34mtsc[0m, from the command line either:

- Use [1mnpm install typescript[0m to first add TypeScript to your project [1mbefore[0m using npx
- Use [1myarn[0m to avoid accidentally running code from un-installed packages
tsc: missing
trivy: missing
gitleaks: missing
cyclonedx-bom: missing
4.0.0
dockle: missing

Logs generated (2025-08-29T14:12:22+00:00):
bandit.log
eslint.log
gitleaks.log
mypy.log
npm-audit.log
pip-audit.log
pnpm-audit.log
pyright.log
requirements.freeze.txt
ruff.log
safety.log
sbom-node.log
sbom-python.log
trivy-config.log
trivy-fs.log
tsc.log

SBOMs generated:

Unavailable tools on this VM: trivy, gitleaks, dockle (apt packages not found). Will propose CI additions in Phase 5.
SBOMs now:
