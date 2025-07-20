# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ruleIQ is an AI-powered compliance automation platform for UK SMBs. It's a full-stack application built with:
- **Backend**: FastAPI (Python) with PostgreSQL, Redis, Celery
- **Frontend**: Next.js 15 (React) with TypeScript, TanStack Query, Zustand
- **AI Services**: Google Gemini integration with multi-model strategy

## Development Commands

### Backend (Python/FastAPI)

```bash
# Activate virtual environment
source /home/omar/Documents/ruleIQ/.venv/bin/activate

# Start backend server
python main.py  # Runs on http://localhost:8000
# Alternative: uvicorn main:app --reload  # Development with auto-reload
# Production: uvicorn main:app --host 0.0.0.0 --port 8000

# Run backend tests
make test-fast        # Quick unit tests (2-5 min)
make test-integration # Integration tests (5-10 min)
make test-full        # Complete test suite
make test-ci          # CI-optimized execution

# Single test execution
python -m pytest tests/test_specific.py -v

# Test with specific markers
pytest -m unit          # Unit tests only
pytest -m api           # API tests only
pytest -m security      # Security tests only

# Linting and formatting
ruff check .           # Linting
ruff format .          # Formatting
ruff check --fix .     # Auto-fix linting issues

# Database migrations
alembic upgrade head   # Apply migrations
alembic revision --autogenerate -m "description"  # Create new migration
alembic downgrade -1   # Rollback one migration

# Database utilities
python database/init_db.py  # Initialize database
```

### Frontend (Next.js/React)

```bash
cd frontend

# Install dependencies (pnpm required)
pnpm install

# Development
pnpm dev              # Runs on http://localhost:3000

# Production build
pnpm build            # Build for production
pnpm start            # Start production server

# Testing
pnpm test             # Run tests with vitest
pnpm test:coverage    # With coverage report
pnpm test:e2e         # End-to-end tests with Playwright
pnpm test:visual      # Visual regression tests

# Code quality
pnpm lint             # ESLint
pnpm typecheck        # TypeScript checking
pnpm format           # Prettier formatting
```

### Docker Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app
docker-compose logs -f celery_worker

# Rebuild after changes
docker-compose down && docker-compose up --build
```

## Architecture Overview

### Backend Structure

```
api/
├── routers/          # FastAPI route handlers
│   ├── ai_assessments.py    # AI-powered assessments
│   ├── auth.py              # JWT authentication
│   └── business_profiles.py # Business profile management
├── middleware/       # Request/response processing
│   ├── rate_limiter.py      # Rate limiting
│   └── security_headers.py  # Security headers
└── dependencies/     # Dependency injection

services/
├── ai/              # AI service modules
│   ├── circuit_breaker.py   # Fault tolerance
│   ├── fallback_system.py   # Graceful degradation
│   └── performance_optimizer.py # Cost optimization
└── assessment_service.py     # Business logic

database/
├── models.py        # SQLAlchemy models
└── db_setup.py      # Database configuration
```

### Frontend Structure

```
frontend/
├── app/             # Next.js app router pages
│   ├── (auth)/      # Authentication pages
│   ├── (dashboard)/ # Protected dashboard pages
│   └── api/         # API routes
├── components/      # React components
│   ├── ui/          # Base UI components (shadcn/ui)
│   └── features/    # Feature-specific components
├── lib/
│   ├── api/         # API service clients
│   ├── stores/      # Zustand state management
│   └── tanstack-query/ # React Query hooks
└── types/           # TypeScript definitions
```

### Key Architectural Patterns

1. **AI Services**: Circuit breaker pattern with fallback mechanisms
2. **Authentication**: JWT with secure Web Crypto API storage
3. **State Management**: Zustand stores + TanStack Query for server state
4. **Database**: PostgreSQL with SQLAlchemy ORM, Redis for caching
5. **Background Tasks**: Celery with Redis broker for async processing
6. **Security**: Rate limiting, CORS, input validation, OWASP compliance

## Current Development Context

The project is 98% production-ready with:
- 671+ backend tests passing
- Enterprise-grade security (8.5/10 score)
- Sub-200ms API response times
- 40-60% AI cost optimization achieved

### Active Areas

1. **AI Optimization**: Multi-model strategy for cost reduction
2. **Database**: Column name mappings for legacy truncation issues
3. **Frontend**: Design system migration with new color palette

### Known Issues

1. **Database Column Names**: Some columns truncated (handled via mappers)
   - `handles_persona` → `handles_personal_data`
   - `processes_payme` → `processes_payments`
   - Solution: Field mappers in `frontend/lib/api/business-profile/field-mapper.ts`

## Testing Strategy

- **Unit Tests**: Fast, isolated component testing
- **Integration Tests**: API endpoints, database operations
- **E2E Tests**: Complete user workflows with Playwright
- **AI Tests**: Accuracy validation, circuit breaker testing
- **Performance Tests**: Load testing, response time validation

Run tests in parallel chunks for optimal performance:
```bash
make test-groups-parallel  # Run all test groups in parallel
```

## Environment Variables

Key environment variables (see `.env.template`):
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `GOOGLE_API_KEY`: Google Gemini API key
- `JWT_SECRET_KEY`: JWT signing key (generate with `python generate_jwt_secret.py`)
- `ALLOWED_ORIGINS`: CORS allowed origins

## MCP Integration

The project integrates with Serena MCP Server for enhanced code intelligence:
- Semantic code analysis and symbol-level operations
- Multi-language support (Python, TypeScript)
- Context-aware assistance

## Security Considerations

- All API endpoints have input validation and rate limiting
- JWT tokens stored with AES-GCM encryption in frontend
- OWASP Top 10 compliance verified
- Regular security audits (see `scripts/security_audit.py`)

## Common Development Workflows

### Adding a New API Endpoint

1. Create router in `api/routers/`
2. Add service logic in `services/`
3. Define schemas in `api/schemas/`
4. Add tests in `tests/test_*.py`
5. Update API documentation

### Adding a New Frontend Page

1. Create page in `frontend/app/(dashboard)/` or appropriate route group
2. Add API service client in `frontend/lib/api/`
3. Create Zustand store if needed in `frontend/lib/stores/`
4. Add TanStack Query hooks in `frontend/lib/tanstack-query/hooks/`
5. Write tests in `frontend/tests/`

### Working with AI Services

- AI services use circuit breaker pattern for reliability
- Fallback responses configured for all AI endpoints
- Cost optimization through caching and model selection
- See `services/ai/` for implementation details

## Important Notes

1. **Database Column Naming**: Some columns are truncated due to legacy issues. Always use field mappers when working with:
   - Business profiles
   - Assessment sessions
   - Any table with truncated column names

2. **Testing**: Always run relevant tests before committing:
   ```bash
   # Backend
   make test-fast  # Quick check
   
   # Frontend
   cd frontend && pnpm test
   ```

3. **Environment Variables**: Never commit `.env` files. Use `.env.template` as reference.

4. **API Rate Limiting**: Default limits are:
   - General endpoints: 100 requests/minute
   - AI endpoints: 20 requests/minute
   - Authentication: 5 requests/minute

5. **Frontend State Management**:
   - Use Zustand for client state
   - Use TanStack Query for server state
   - Don't mix the two patterns

6. **Code Style**:
   - Python: Follow PEP 8, enforced by ruff
   - TypeScript: Follow project ESLint rules
   - Use descriptive variable names
   - Comment complex logic