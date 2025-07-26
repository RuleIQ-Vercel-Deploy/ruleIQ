# Backend Development - Condensed Reference (July 2025)

## Project Status
- **Production Readiness**: 98% complete
- **Tests**: 671+ passing
- **Security Score**: 8.5/10
- **Performance**: <200ms API response times
- **AI Cost Optimization**: 40-60% achieved

## Tech Stack
- **API**: FastAPI (Python) on http://localhost:8000
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis
- **Background**: Celery with Redis broker
- **AI**: Google Gemini (primary) + OpenAI (fallback)

## Critical Development Commands
```bash
# Environment
source /home/omar/Documents/ruleIQ/.venv/bin/activate

# Backend Server
python main.py  # or: uvicorn main:app --reload

# Testing
make test-fast        # Quick unit tests (2-5 min)
make test-integration # Integration tests (5-10 min)
ruff check . && ruff format .  # Linting/formatting

# Database
alembic upgrade head  # Apply migrations
python database/init_db.py  # Initialize database
```

## Key Features Implementation

### 1. AI Policy Generation (COMPLETED)
- **Service**: `services/ai/policy_generator.py`
- **Endpoints**: `/api/v1/ai/generate-policy`, `/api/v1/ai/refine-policy`
- **Features**: Circuit breaker, dual providers, template fallback
- **Rate Limit**: 20 req/min

### 2. RBAC System (COMPLETED)
- **Database**: 7 RBAC tables (roles, permissions, user_roles, etc.)
- **Service**: `services/rbac_service.py`
- **Middleware**: Automatic API route protection
- **Default Roles**: 5 roles, 21 permissions
- **Audit**: Complete logging for compliance

### 3. Infrastructure Fixes (2025)
**Celery Workers**:
- Rate limiting: Evidence (5/m), Compliance (3/m), Notifications (20/m)
- Exponential backoff with jitter
- Safe autodiscovery with error handling

**Database**:
- Column truncation mappers: `handles_persona` → `handles_personal_data`
- Neon database integration ready

## API Architecture
```
api/
├── routers/          # Endpoints (ai_assessments, auth, business_profiles)
├── middleware/       # Rate limiting, security headers, RBAC
└── dependencies/     # JWT auth, RBAC auth

services/
├── ai/              # Circuit breaker, fallback, optimizer
└── assessment_service.py
```

## Rate Limiting
- General: 100 req/min
- AI endpoints: 20 req/min  
- Authentication: 5 req/min

## Security Features
- JWT with AES-GCM encryption
- OWASP Top 10 compliance
- Input validation on all endpoints
- Comprehensive audit logging

## Known Issues & Solutions
1. **Column Truncation**: Use field mappers in `frontend/lib/api/business-profile/field-mapper.ts`
2. **Circular Imports**: Lazy imports in Celery workers
3. **API Overload**: Comprehensive rate limiting implemented

## Testing Strategy
```bash
# Run specific test markers
pytest -m unit
pytest -m api
pytest -m security

# Parallel test execution
make test-groups-parallel
```

## Environment Variables (see .env.template)
- DATABASE_URL, REDIS_URL
- GOOGLE_API_KEY
- JWT_SECRET_KEY (generate with `python generate_jwt_secret.py`)
- ALLOWED_ORIGINS

## References
- Agent Protocol: ALWAYS_READ_FIRST memory
- Full docs: project_overview, tech_stack memories
- Implementation details: ai_*, rbac_*, celery_worker_fixes_2025 memories