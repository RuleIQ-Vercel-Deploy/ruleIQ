# RuleIQ Brownfield Architecture Document

## Introduction

This document captures the CURRENT STATE of the RuleIQ codebase, including technical debt, workarounds, and real-world patterns. It serves as a reference for AI agents working on enhancements to the compliance automation platform for UK SMBs.

### Document Scope
Comprehensive documentation of entire system including backend API, frontend application, databases, and supporting services.

### Change Log

| Date       | Version | Description                 | Author    |
|------------|---------|----------------------------|-----------|
| 2025-01-09 | 1.0     | Initial brownfield analysis | AI Agent  |

## Quick Reference - Key Files and Entry Points

### Critical Files for Understanding the System

- **Main Entry**: `main.py` - FastAPI application with lifespan management
- **Configuration**: `config/settings.py`, `.env.test`, `.env.example`
- **Core Business Logic**: `services/`, particularly `agentic_assessment.py`, `compliance_graph_initializer.py`
- **API Definitions**: `api/routers/` - All REST endpoints
- **Database Models**: `database/models/`, `models/`
- **Key Algorithms**: 
  - `services/lead_scoring_service.py` - Lead qualification
  - `services/compliance_retrieval_queries.py` - RAG implementation

## High Level Architecture

### Technical Summary

RuleIQ is an AI-powered compliance automation platform built as a microservices-ready monolith. The system uses FastAPI for the backend with async support, Next.js 14 for the frontend, and leverages multiple AI services (OpenAI, Google AI) for intelligent compliance assessments.

### Actual Tech Stack (from requirements.txt and package.json)

| Category    | Technology     | Version  | Notes                           |
|-------------|---------------|----------|----------------------------------|
| Runtime     | Python        | 3.11+    | Backend runtime                  |
| Runtime     | Node.js       | 18.17+   | Frontend runtime                 |
| Framework   | FastAPI       | 0.100.0+ | Async REST API                   |
| Framework   | Next.js       | 14.0+    | React with SSR/SSG               |
| Database    | PostgreSQL    | 13       | Docker for dev/test              |
| Database    | Neon          | Latest   | Serverless PostgreSQL for prod   |
| Database    | Redis         | 7.0+     | Caching and sessions             |
| Database    | Neo4j         | Latest   | Graph database for knowledge     |
| ORM         | SQLAlchemy    | 2.0+     | Database abstraction             |
| AI/ML       | OpenAI        | 1.0.0+   | GPT models                       |
| AI/ML       | Google AI     | 0.8.0+   | Gemini models                    |
| Task Queue  | Celery        | 5.3.0+   | Background jobs (partial setup)  |
| Auth        | JWT           | -        | Custom implementation            |

### Repository Structure Reality Check

- Type: Monorepo with separate frontend directory
- Package Manager: pip/venv for backend, pnpm for frontend
- Notable: Multiple backup directories present, migration from app/ to root structure evident

## Source Tree and Module Organization

### Project Structure (Actual)

```text
ruleIQ/
├── api/
│   ├── routers/             # 30+ endpoint modules (inconsistent patterns)
│   ├── schemas/             # Pydantic models
│   ├── dependencies/        # Auth and DB dependencies
│   └── middleware/          # Error handling, request ID
├── services/                # Business logic (mixed patterns)
│   ├── agentic_*.py         # AI services
│   ├── compliance_*.py      # Compliance logic
│   ├── monitoring/          # Database monitoring
│   └── reporting/           # Report generation
├── database/                # SQLAlchemy setup
│   ├── models/              # Some models here
│   └── db_setup.py          # Connection management
├── models/                  # MORE models here (duplication issue)
├── middleware/              # Multiple JWT implementations (v1, v2, decorators)
├── frontend/                # Next.js application
│   ├── app/                 # App router (Next.js 13+)
│   ├── components/          # React components
│   └── __tests__/           # Frontend tests
├── tests/                   # Backend tests (60% coverage)
├── scripts/                 # Security and JWT verification scripts
├── backup_*/                # Multiple backup directories (technical debt)
└── main.py                  # Entry point with complex initialization
```

### Key Modules and Their Purpose

- **User Management**: Not centralized - spread across `api/routers/users.py`, `api/routers/auth.py`, `api/routers/rbac_auth.py`
- **Authentication**: Multiple implementations - `middleware/jwt_auth.py`, `middleware/jwt_auth_v2.py`, `api/routers/auth.py`
- **Payment Processing**: `api/routers/payment.py` - Stripe integration
- **AI Assessment**: `services/agentic_assessment.py` - Core AI logic
- **Compliance Engine**: `services/compliance_graph_initializer.py` - Graph-based compliance
- **Monitoring**: `services/monitoring/database_monitor.py` - Health checks

## Data Models and APIs

### Data Models

The project has **MODEL DUPLICATION ISSUE**:
- Models in `database/models/` - Some SQLAlchemy models
- Models in `models/` - Additional models including feature flags
- No clear separation of concerns

Key models referenced:
- **User Model**: Location unclear (likely in `database/models/`)
- **Assessment Models**: Multiple assessment-related routers suggest complex model
- **Business Profile**: `api/routers/business_profiles.py`
- **Framework Models**: `api/routers/frameworks.py`

### API Specifications

- **OpenAPI Spec**: Auto-generated by FastAPI at `/docs`
- **Postman Collection**: Not found
- **Manual Endpoints**: 30+ routers in `api/routers/` including:
  - Standard CRUD operations
  - AI-powered endpoints (`ai_assessments`, `ai_optimization`, `ai_policy`)
  - UK-specific compliance (`uk_compliance`)
  - WebSocket support (`ai_cost_websocket`)

## Technical Debt and Known Issues

### Critical Technical Debt

1. **Multiple JWT Implementations**: `jwt_auth.py`, `jwt_auth_v2.py`, `jwt_decorators.py` - unclear which is primary
2. **Model Duplication**: Models split between `database/models/` and `models/` directories
3. **Backup Directories**: Multiple `backup_*` directories in root (should be git-ignored)
4. **Inconsistent Auth Patterns**: Three different auth routers (`auth`, `rbac_auth`, `google_auth`)
5. **Database Connection Management**: Multiple connection patterns in use
6. **Missing Migrations**: Alembic directory exists but migration strategy unclear
7. **Test Database Configuration**: Hardcoded PostgreSQL on port 5433, credentials in plain text

### Workarounds and Gotchas

- **Test Environment**: Must use Docker PostgreSQL on port 5433 with `postgres:postgres` credentials
- **Production Secrets**: Stored in Doppler, not in `.env` files
- **Module Import**: Must use `main:app` not `app.main:app` when running uvicorn
- **Database Initialization**: Complex lifespan management in `main.py` with multiple try/except blocks
- **Frontend State**: Multiple background processes running (check with `ps aux | grep uvicorn`)
- **Environment Variables**: Test environment requires explicit `TESTING=true` flag

## Integration Points and External Dependencies

### External Services

| Service        | Purpose            | Integration Type | Key Files                        |
|----------------|-------------------|------------------|----------------------------------|
| OpenAI         | GPT models        | REST API         | `services/agentic_assessment.py` |
| Google AI      | Gemini models     | SDK              | Multiple AI service files        |
| Stripe         | Payments          | SDK              | `api/routers/payment.py`         |
| Neo4j          | Graph database    | Driver           | `services/neo4j_service.py`      |
| SendGrid       | Email (planned)   | -                | Not implemented                  |
| Doppler        | Secrets mgmt      | CLI              | Production only                  |
| Neon           | Serverless DB     | PostgreSQL       | Production only                  |

### Internal Integration Points

- **Frontend Communication**: REST API on port 8000, CORS enabled for localhost:3000
- **Background Jobs**: Celery configured but not fully implemented
- **WebSocket**: Cost monitoring via WebSocket endpoint
- **Cache Layer**: Redis configured but usage patterns unclear
- **Graph Database**: Neo4j for compliance knowledge graph

## Development and Deployment

### Local Development Setup

1. **Backend Setup** (what actually works):
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start Docker services
docker-compose up -d  # PostgreSQL on 5433, Redis on 6379

# Run migrations (if they exist)
alembic upgrade head

# Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Frontend Setup**:
```bash
cd frontend
pnpm install
pnpm dev  # Runs on port 3000
```

3. **Known Setup Issues**:
   - Port 8000 often already in use (kill existing process)
   - Database connection fails if Docker not running
   - Test credentials differ from production

### Build and Deployment Process

- **Build Command**: Not clearly defined, appears to be containerized
- **Deployment**: Docker-based, configs in `deployment/` and `docker/`
- **Environments**: Development (local), Testing (Docker), Production (Neon + cloud)

## Testing Reality

### Current Test Coverage

- **Backend Tests**: ~60% coverage (per comments in code)
- **Integration Tests**: Present in `tests/integration/`
  - `test_api_endpoints.py`
  - `test_auth_flow.py`
  - `test_jwt_coverage.py`
  - `test_feature_flags.py`
- **Frontend Tests**: Minimal, some in `frontend/__tests__/`
- **E2E Tests**: None found

### Running Tests

```bash
# Backend tests
pytest tests/

# With coverage
pytest --cov=. tests/

# Frontend tests
cd frontend && pnpm test
```

### Test Environment Issues

- Test database on port 5433 vs production on standard 5432
- Test environment variables in `.env.test` but not all services respect them
- No clear test data seeding strategy

## Security Considerations

### Current Security Implementation

1. **Multiple JWT implementations** causing confusion
2. **Security verification scripts** suggest past security issues:
   - `scripts/verify_auth_security.py`
   - `scripts/verify_sec001_fix.py`
   - `scripts/jwt_coverage_audit.py`
3. **Feature flags** for gradual rollout (`services/feature_flag_service.py`)
4. **Enhanced security middleware** but unclear if active

### Security Debt

- JWT implementation fragmentation
- Plain text test credentials
- No clear API rate limiting
- Missing OWASP compliance checks

## Performance Bottlenecks

### Identified Issues

1. **Database Monitoring**: 30-second interval polling in lifespan
2. **Synchronous Operations**: Some services not fully async
3. **No Connection Pooling**: Database connections not optimized
4. **Frontend Bundle**: No optimization strategy evident
5. **Cache Underutilization**: Redis configured but barely used

## Migration and Refactoring Needs

### Urgent Refactoring

1. **Consolidate JWT Implementation**: Remove v1, standardize on v2
2. **Unify Model Location**: Move all models to `database/models/`
3. **Remove Backup Directories**: Clean up `backup_*` folders
4. **Standardize Auth Flow**: Single auth router and strategy
5. **Complete Celery Integration**: Background tasks half-implemented

### Long-term Improvements

1. **Microservices Extraction**: AI services prime candidate
2. **GraphQL Layer**: For complex compliance queries
3. **Event Sourcing**: For audit trail
4. **CQRS Pattern**: Separate read/write for compliance data
5. **Service Mesh**: For production scaling

## Development Patterns and Conventions

### Current Patterns (Inconsistent)

- **Repository Pattern**: Attempted in `database/repositories/` but not widespread
- **Service Layer**: Present but mixed with business logic in routers
- **Dependency Injection**: FastAPI's `Depends` used inconsistently
- **Error Handling**: Global middleware but also local try/catch
- **Validation**: Pydantic schemas but not everywhere

### Anti-patterns Present

- **God Objects**: `main.py` doing too much initialization
- **Duplicate Code**: Multiple JWT implementations
- **Callback Hell**: Some async code using callbacks
- **Hard-coded Values**: Test database configuration
- **Mixed Concerns**: Business logic in routers

## Monitoring and Observability

### Current Implementation

- **Database Monitor**: Custom implementation with 30s polling
- **Health Checks**: `/api/v1/monitoring/health`
- **Logging**: Python logging configured
- **Metrics**: Prometheus setup attempted
- **Error Tracking**: Sentry mentioned but not configured

## Known Bugs and Workarounds

1. **Port Conflicts**: Backend often fails to start due to port 8000 in use
2. **Database Connections**: Connection refused errors if Docker not running
3. **Module Import**: Must use correct module path for uvicorn
4. **Frontend Hot Reload**: Sometimes requires manual refresh
5. **Test Isolation**: Tests may fail if run in parallel

## Useful Commands and Scripts

### Frequently Used Commands

```bash
# Check running processes
ps aux | grep uvicorn
ps aux | grep "pnpm dev"

# Kill stuck processes
pkill -f uvicorn
pkill -f "pnpm dev"

# Docker management
docker ps  # Check running containers
docker-compose restart ruleiq-test-postgres

# Database access
docker exec -it ruleiq-test-postgres psql -U postgres -d compliance_test

# Quick backend restart
pkill -f uvicorn && uvicorn main:app --reload

# Check logs
docker-compose logs -f
```

### Debugging and Troubleshooting

- **Backend Logs**: Check console output from uvicorn
- **Frontend Logs**: Browser console and terminal running pnpm dev
- **Database Issues**: Check Docker container status
- **API Testing**: Use FastAPI's built-in `/docs` endpoint

## Critical Integration Constraints

### Must Maintain Compatibility

1. **JWT Token Format**: Existing tokens in production
2. **Database Schema**: No breaking changes without migration
3. **API Contracts**: Frontend depends on current endpoints
4. **Stripe Integration**: Payment flow cannot break
5. **Neon Connection**: Production database configuration

### Cannot Modify (Legacy)

1. **Test Database Port**: Must remain 5433
2. **Frontend Port**: Must remain 3000
3. **API Port**: Must remain 8000
4. **Redis Ports**: 6379 for cache, 6380 for testing

## Appendix - Environment Variables

### Critical Environment Variables

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/compliance_test
TESTING=true  # Required for test environment

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Services
OPENAI_API_KEY=<required>
GOOGLE_AI_API_KEY=<required>

# Security
JWT_SECRET_KEY=<minimum 32 characters>

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production Differences

- Credentials in Doppler, not env files
- Neon database instead of Docker PostgreSQL
- Different ports and hostnames
- SSL/TLS enabled
- Rate limiting active

---

**Note**: This document reflects the actual state as of January 2025. The codebase shows signs of rapid development with technical debt accumulation. Priority should be given to consolidating authentication, cleaning up model duplication, and establishing clear architectural boundaries before adding new features.