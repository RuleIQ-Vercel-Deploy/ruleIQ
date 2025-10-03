# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

#### 1. **Test-First Mandate**

* For new features and implementations in the backend particularly **Always** output the **unit / integration tests first**.
* Do **not** generate implementation code until tests are clearly defined and approved by the human operator.
* All delivered code must leave the test suite ✔️ green.

#### 2. **Immaculate Code Standard**

* Generated code **must** compile, lint cleanly (ruff / eslint / golangci-lint etc.), and pass type-checking (mypy / tsc / go vet etc.) **with zero warnings**.
* If tooling reports an issue, **fix it** before returning the response.

#### 3. **Design Compliance Only**

* Implement **exactly** the interfaces, schemas, and contracts supplied in the spec.
* **No self-invented APIs, no hidden globals, no spontaneous design changes.**
* Raise a clarification question if the spec is ambiguous; never guess.

#### 4. **Strict Scope Guard**

* The PRD (or the current ticket) is the single source of truth.
* Ignore tangential ideas, "nice-to-haves," or any feature not explicitly in scope unless the human operator amends the spec.

#### 5. **Modular, Microservice-Friendly Output**

* Each component must be:
  * **Independently testable** (mock external calls).
  * **Stateless** where feasible.
  * **Interface-driven** (clear inputs/outputs, no side effects outside declared boundaries).

#### 6. **Readable & Maintainable Style**

* Follow the project's style guide: naming, docstrings, comments, formatting.
* Prefer clarity over cleverness; avoid "magic."
* Provide concise inline comments for non-obvious logic.

#### 7. **Self-Review Before Responding**

* Run an internal sanity check: logic flow, edge cases, performance hot spots.
* Include a **brief rationale** for any non-trivial algorithmic choice.

#### 8. **Error Handling Discipline**

* Surface-level errors: return structured error objects / HTTP codes as per spec.
* Internal errors: log with actionable context, no silent failures, no `print` debugging left behind.

#### 9. **Prompt Efficiency**

* Respond with **complete, final** code blocks—no incremental partials.
* Minimize chatter; deliver code + concise explanations.
* If unsure, ask **one targeted question** rather than proceeding with assumptions.

#### 10. **Escalation Protocol**

* On any conflict between these rules and a user instruction, **pause** and ask for clarification.
* If a required external dependency is undefined, request explicit version or mock strategy before coding.

#### 11. **Running Commands is Your Duty**

* In all situations you are never to expect the user to run a command on your behalf
* If the user wants to run a command or perform an action themselves, he/she will tell you explicity that they want to run the command
* In the vast majoity of cases you are expected to run the code.

---

**Non-Compliance Consequence**
Any response that violates these rules will be rejected and regenerated. Repeat offenders will be removed from the agent pool.

*End of protocol.*

## Project Overview

RuleIQ is an enterprise-grade agentic AI compliance automation platform for UK SMBs. The system uses intelligent agents that evolve from helpers to trusted advisors to autonomous partners, implementing GraphRAG-powered compliance orchestration with LangGraph workflows.

**Tech Stack:**
- **Backend**: Python 3.11.9 + FastAPI + PostgreSQL (Neon) + Neo4j (GraphRAG) + Redis
- **Frontend**: Next.js 15 + React 19 + TailwindCSS + shadcn/ui (Teal design system)
- **AI**: LangGraph multi-agent orchestration, Google Gemini, OpenAI
- **Testing**: 1884+ backend tests (pytest), 562+ frontend tests (Vitest + Playwright)

## Essential Commands

### Backend Development

```bash
# Environment activation (REQUIRED for all backend work)
source .venv/bin/activate

# Start backend server (production entrypoint)
uvicorn api.main:app --host 0.0.0.0 --port 8000

# With Doppler secrets management (recommended for production)
doppler run -- uvicorn api.main:app --host 0.0.0.0 --port 8000

# Initialize databases
python database/init_db.py           # PostgreSQL schema
python services/neo4j_service.py     # Neo4j knowledge graph
```

**Note**: `main.py` is deprecated. Always use `api.main:app` as the entrypoint.

### Frontend Development

```bash
cd frontend

# Development with Turbopack (60% faster hot reloads)
pnpm dev              # Runs on http://localhost:3000 with --turbo

# Build and production
pnpm build           # Production build
pnpm start           # Start production server
pnpm typecheck       # TypeScript validation
pnpm lint            # ESLint
pnpm format          # Prettier

# Test with teal design system
NEXT_PUBLIC_USE_NEW_THEME=true pnpm dev
```

### Testing

**Backend (1884+ tests):**
```bash
# Independent test groups (recommended, fastest)
make test-groups-parallel    # All groups in parallel (~20 min)
make test-group-unit         # Unit tests (2-3 min)
make test-group-ai           # AI core tests (3-4 min)
make test-group-api          # Basic API tests (4-5 min)

# Legacy modes
make test-fast               # Fast unit tests
make test-full               # Complete suite
make test-ai                 # AI and compliance tests
make test-security           # Security tests

# Single test file
pytest tests/path/to/test_file.py -v
```

**Frontend:**
```bash
cd frontend
pnpm test                    # Unit tests (Vitest)
pnpm test:coverage           # With coverage
pnpm test:e2e                # E2E tests (Playwright)
pnpm test:visual             # Visual regression
```

**Agentic Systems:**
```bash
# RAG Self-Critic testing
python services/rag_self_critic.py quick-check --query "GDPR query"
python services/rag_self_critic.py fact-check --query "ISO 27001 requirements"
```

### Code Quality

```bash
# Backend
ruff check .                 # Linting
ruff format .                # Formatting

# Frontend
cd frontend
pnpm lint                    # ESLint
pnpm format                  # Prettier
pnpm typecheck               # TypeScript checks
```

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Frontend (Next.js 15)                  │
│  App Router │ Zustand │ TanStack Query │ Teal Theme    │
└────────────────────────┬────────────────────────────────┘
                         │ REST API + WebSocket
┌────────────────────────┴────────────────────────────────┐
│              Agentic Intelligence Layer                 │
│  IQ Agent │ GraphRAG │ RAG Self-Critic │ LangGraph     │
│  PPALE Loop: Perceive→Plan→Act→Learn→Remember          │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                Backend (FastAPI)                        │
│  56+ Routers │ 140+ Services │ JWT Auth │ RBAC         │
└────────────────────────┬────────────────────────────────┘
                         │
     ┌───────────────────┼───────────────────┐
     │                   │                   │
┌────┴─────┐      ┌─────┴──────┐     ┌─────┴──────┐
│PostgreSQL│      │   Neo4j    │     │   Redis    │
│  (Neon)  │      │ (GraphRAG) │     │  (Cache)   │
└──────────┘      └────────────┘     └────────────┘
```

### Key Directory Structure

**Backend:**
- `api/routers/` - 56+ FastAPI endpoints (all follow `/api/v1/` pattern)
- `services/` - 140+ business logic services, AI integrations
  - `services/ai/assistant.py` - **CRITICAL**: 4,031 lines (needs refactoring)
  - `services/ai/compliance_ingestion_pipeline.py`
  - `services/neo4j_service.py`
- `database/` - SQLAlchemy models, Alembic migrations
- `langgraph_agent/` - LangGraph multi-agent workflows
- `middleware/` - Auth, rate limiting, security headers
- `models/` - Pydantic request/response schemas
- `tests/` - 234 Python test files

**Frontend:**
- `frontend/app/` - Next.js 15 App Router pages
- `frontend/components/` - 200+ React components (shadcn/ui based)
- `frontend/lib/` - API clients, Zustand stores, utilities
- `frontend/tests/` - 562 test files (Vitest + Playwright)

### Critical Files to Understand

1. **`api/main.py`** - FastAPI application entrypoint with middleware stack
2. **`services/ai/assistant.py`** - AI orchestration (WARNING: 4,031 lines, scheduled for refactoring)
3. **`frontend/lib/api/client.ts`** - API client with automatic `/api/v1/` normalization
4. **`config/settings.py`** - Configuration management
5. **`database/models/`** - SQLAlchemy ORM models

### API Architecture

**All endpoints follow `/api/v1/` pattern:**
- Authentication: `/api/v1/auth/*`
- IQ Agent: `/api/v1/iq/*`
- Assessments: `/api/v1/assessments/*`
- Compliance: `/api/v1/compliance/*`
- Evidence: `/api/v1/evidence/*`

**Frontend API client automatically normalizes endpoints** - no manual versioning needed.

### Agentic Intelligence (IQ Agent)

**PPALE Intelligence Loop:**
1. **PERCEIVE** - Query compliance posture from Neo4j
2. **PLAN** - Risk-weighted prioritization
3. **ACT** - Execute compliance controls
4. **LEARN** - Pattern recognition
5. **REMEMBER** - Memory consolidation

**Trust Gradient Levels:**
- Level 1: Transparent Helper (current) - Shows reasoning, asks confirmation
- Level 2: Trusted Advisor (6 months) - Makes confident suggestions
- Level 3: Autonomous Partner (12 months) - Takes initiative autonomously

### State Management

**Backend:**
- PostgreSQL: Persistent data, user accounts, assessments
- Neo4j: Knowledge graph (20+ node types), compliance relationships
- Redis: Sessions, JWT blacklist, rate limiting, caching

**Frontend:**
- TanStack Query: Server state management
- Zustand: Client state management
- React Hook Form: Form state
- LocalStorage: Persisted queries

## Security & Authentication

**JWT-Only Authentication** (Stack Auth removed August 2025):
- 30-minute access tokens, 7-day refresh tokens
- bcrypt password hashing with auto-salt
- Redis-based token blacklisting
- RBAC middleware for granular permissions

**Rate Limiting:**
- 5/min for auth endpoints
- 100/min for general endpoints
- 20/min for AI endpoints

**IMPORTANT**: Never commit secrets. Use Doppler for production or `.env` for local development.

## Critical Issues & Known Debt

### P0 - Must Fix Before Deployment

1. **Hardcoded Passwords** - SECURITY RISK in:
   - `services/neo4j_service.py` (Line ~15): `'ruleiq123'`
   - `services/ai/compliance_ingestion_pipeline.py`: `'password'`
   - `services/ai/evaluation/tools/ingestion_fixed.py`: `'ruleiq123'`
   - **FIX**: Remove defaults, require environment variables, fail if not set

2. **assistant.py God Object** (4,031 lines):
   - Violates Single Responsibility Principle severely
   - Difficult to test and maintain
   - Scheduled for refactoring into 8-10 focused modules

### High Priority

- Test coverage needs verification (run `pytest --cov`)
- 458 TODO comments need systematic review
- Multiple `.jwt-backup` files need cleanup
- Large files (>1,000 lines) need refactoring

## Design System (Teal Theme Migration - 65% Complete)

**Primary Teal Palette:**
```css
--teal-600: #2C7A7B;   /* PRIMARY BRAND */
--teal-700: #285E61;   /* Hover states */
--teal-50: #E6FFFA;    /* Light backgrounds */
--teal-300: #4FD1C5;   /* Bright accents */
```

**Legacy purple/cyan colors being phased out** - use teal tokens for new components.

## Database Schema

**PostgreSQL Tables:**
- `users`, `business_profiles`, `frameworks`, `controls`
- `assessments`, `evidence`, `audit_logs`
- `api_keys`, `subscriptions`

**Neo4j Graph:**
- Nodes: Frameworks, Controls, Requirements, Evidence, Businesses
- Relationships: REQUIRES, MAPPED_TO, SATISFIES, REFERENCES

## Development Workflow Best Practices

1. **Always activate virtualenv**: `source .venv/bin/activate`
2. **Use Doppler for secrets**: `doppler run -- <command>`
3. **Run tests before committing**: `make test-fast` (backend), `pnpm test` (frontend)
4. **Follow API versioning**: All endpoints must use `/api/v1/` prefix
5. **Use teal design tokens**: No new purple/cyan color codes
6. **Never commit to main**: Use feature branches and PRs
7. **Update tests with changes**: Coverage gates are enforced

## Performance SLOs

- API endpoints: <200ms (p95)
- IQ Agent quick check: 2-5 seconds
- Standard AI queries: 10-30 seconds
- Frontend initial load: <3s
- Hot reloads: ~200ms (with Turbopack)

## Project Status (January 2025)

- **Overall**: 98% Production Ready
- **Backend**: ✅ 1884+ tests passing
- **Frontend**: ✅ Complete with Turbopack + teal design
- **Agentic Systems**: ✅ IQ Agent, RAG Self-Critic, LangGraph deployed
- **CI/CD**: ✅ GitHub Actions with SonarCloud
- **Security**: 8.5/10 (enterprise-grade)

## When Things Go Wrong

**Backend won't start:**
- Check virtualenv is activated
- Verify DATABASE_URL in `.env`
- Check Neo4j and Redis are running
- Review logs: `tail -f logs/app.log`

**Frontend build fails:**
- Run `pnpm install` to sync dependencies
- Check Node.js version (requires 18+)
- Clear `.next` cache: `rm -rf .next`

**Tests failing:**
- Ensure databases are accessible
- Check test fixtures are up to date
- Run single test to isolate: `pytest tests/path/to/test.py::test_name -v`

**Database connection issues:**
- Verify connection string format
- Check network access to Neon PostgreSQL
- Review connection pool settings in `config/settings.py`

## Useful Documentation Links

- API Documentation: `http://localhost:8000/docs` (when running)
- Agentic Systems: `frontend/AGENTIC_SYSTEMS_OVERVIEW.md`
- API Endpoints: `docs/API_ENDPOINTS_DOCUMENTATION.md`
- Testing Guide: `docs/TESTING_GUIDE.md`
- Frontend Design Plan: `frontend/FRONTEND_DESIGN_COMPLIANCE_PLAN.md`

## Priority Gates (Task Management)

- **P0 Must Complete Before P1**: No P1 work until ALL P0 tasks pass
- **Sequential Gating**: Each priority level blocks the next
- **Timeframes**: P0 (24h max), P1 (48h max), P2 (1 week max)
- **Quality Standards**: All tasks must pass acceptance criteria, tests must pass