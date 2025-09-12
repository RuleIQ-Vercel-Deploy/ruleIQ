# RuleIQ Source Tree Structure

## Overview
This document provides a comprehensive map of the RuleIQ codebase structure, explaining the purpose of each directory and key files. The project follows a modular architecture with clear separation between backend API, frontend application, and supporting services.

## Root Directory Structure

```
ruleIQ/
├── .bmad-core/               # BMad project management configuration
├── .github/                  # GitHub Actions workflows and templates
├── alembic/                  # Database migration files
├── api/                      # FastAPI backend application
├── backup_*/                 # Backup directories (git-ignored)
├── config/                   # Application configuration
├── database/                 # Database models and setup
├── deployment/               # Deployment configurations
├── docker/                   # Docker-related files
├── docs/                     # Project documentation
├── frontend/                 # Next.js React application
├── middleware/               # FastAPI middleware components
├── models/                   # Additional data models
├── monitoring/               # Monitoring configurations
├── scripts/                  # Utility and maintenance scripts
├── services/                 # Business logic services
├── tests/                    # Backend test suite
├── .env.example              # Environment variables template
├── .env.test                 # Test environment configuration
├── docker-compose.yml        # Docker services configuration
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## Backend Structure

### `/api` - FastAPI Application Core

```
api/
├── dependencies/             # Dependency injection
│   ├── auth.py              # Authentication dependencies
│   ├── database.py          # Database session management
│   └── services.py          # Service layer dependencies
├── middleware/               # API middleware
│   ├── error_handler.py     # Global error handling
│   └── security.py          # Security middleware
├── routers/                  # API endpoints
│   ├── admin.py             # Admin endpoints
│   ├── assessments.py       # Compliance assessments
│   ├── auth.py              # Authentication endpoints
│   ├── business_profiles.py # Business profile management
│   ├── compliance.py        # Compliance status
│   ├── frameworks.py        # Compliance frameworks
│   ├── monitoring.py        # Health monitoring
│   ├── payment.py           # Payment processing
│   ├── policies.py          # Policy management
│   ├── reports.py           # Report generation
│   └── users.py             # User management
├── schemas/                  # Pydantic models
│   ├── assessment.py        # Assessment schemas
│   ├── auth.py              # Authentication schemas
│   ├── compliance.py        # Compliance schemas
│   └── user.py              # User schemas
├── utils/                    # Utility functions
│   ├── validation.py        # Input validation
│   └── formatting.py        # Response formatting
└── request_id_middleware.py # Request tracking
```

### `/database` - Data Layer

```
database/
├── __init__.py              # Database exports
├── db_setup.py              # Database initialization
├── models/                  # SQLAlchemy models
│   ├── assessment.py        # Assessment model
│   ├── business_profile.py # Business profile model
│   ├── framework.py         # Framework model
│   ├── policy.py            # Policy model
│   └── user.py              # User model
├── repositories/            # Data access layer
│   ├── base.py              # Base repository
│   └── assessment_repo.py   # Assessment repository
└── migrations/              # Alembic migrations
```

### `/services` - Business Logic

```
services/
├── agentic_assessment.py    # AI-powered assessments
├── agentic_integration.py   # AI service integration
├── compliance_graph_initializer.py # Graph database setup
├── compliance_memory_manager.py # Compliance memory management
├── compliance_retrieval_queries.py # RAG queries
├── feature_flag_service.py  # Feature flag management
├── framework_service.py     # Framework operations
├── lead_scoring_service.py  # Lead scoring algorithm
├── monitoring/               # Monitoring services
│   ├── __init__.py
│   └── database_monitor.py  # Database health monitoring
├── neo4j_service.py         # Graph database service
├── policy_service.py        # Policy management
├── reporting/               # Report generation
│   ├── pdf_generator.py    # PDF report generation
│   └── report_scheduler.py # Scheduled reports
├── security_alerts.py       # Security monitoring
└── session_manager.py       # Session management
```

### `/middleware` - Request Processing

```
middleware/
├── degradation.py           # Graceful degradation
├── jwt_auth.py              # JWT authentication
├── jwt_auth_v2.py           # Enhanced JWT auth
├── jwt_decorators.py        # Auth decorators
├── security_headers.py      # Security headers
├── security_middleware.py   # Core security
└── security_middleware_enhanced.py # Enhanced security
```

### `/config` - Configuration Management

```
config/
├── __init__.py              # Config exports
├── cache.py                 # Redis cache configuration
├── celery.py                # Celery task queue config
├── feature_flags.py         # Feature flag configuration
├── logging_config.py        # Logging configuration
├── security.py              # Security settings
└── settings.py              # Application settings
```

## Frontend Structure

### `/frontend` - Next.js Application

```
frontend/
├── app/                     # Next.js 13+ app directory
│   ├── (auth)/              # Authentication routes
│   │   ├── login/
│   │   ├── register/
│   │   └── reset-password/
│   ├── (dashboard)/         # Dashboard routes
│   │   ├── assessments/
│   │   ├── compliance/
│   │   ├── policies/
│   │   └── reports/
│   ├── api/                 # API routes
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Home page
├── components/              # React components
│   ├── auth/                # Authentication components
│   ├── compliance/          # Compliance components
│   ├── dashboard/           # Dashboard components
│   ├── layout/              # Layout components
│   ├── magicui/             # Animation components
│   ├── payment/             # Payment components
│   └── ui/                  # Reusable UI components
├── hooks/                   # Custom React hooks
│   ├── useAuth.ts           # Authentication hook
│   ├── useCompliance.ts     # Compliance data hook
│   └── useDebounce.ts       # Debounce hook
├── lib/                     # Utility libraries
│   ├── api.ts               # API client
│   ├── constants.ts         # App constants
│   └── utils.ts             # Helper functions
├── public/                  # Static assets
│   ├── images/
│   └── fonts/
├── styles/                  # Global styles
│   └── globals.css          # Global CSS
├── types/                   # TypeScript definitions
│   ├── api.types.ts         # API types
│   └── components.types.ts  # Component types
├── __tests__/               # Test files
├── next.config.js           # Next.js configuration
├── package.json             # Dependencies
├── tailwind.config.ts       # Tailwind configuration
└── tsconfig.json            # TypeScript configuration
```

## Testing Structure

### `/tests` - Backend Tests

```
tests/
├── unit/                    # Unit tests
│   ├── services/            # Service tests
│   ├── models/              # Model tests
│   └── utils/               # Utility tests
├── integration/             # Integration tests
│   ├── test_api_endpoints.py
│   ├── test_auth_flow.py
│   ├── test_jwt_coverage.py
│   └── test_transactions.py
├── fixtures/                # Test fixtures
│   ├── assessment_data.py
│   └── user_data.py
├── conftest.py              # Pytest configuration
└── test_*.py                # Test files
```

### `/frontend/__tests__` - Frontend Tests

```
frontend/__tests__/
├── components/              # Component tests
├── hooks/                   # Hook tests
├── integration/             # Integration tests
├── pages/                   # Page tests
└── utils/                   # Utility tests
```

## Documentation Structure

### `/docs` - Project Documentation

```
docs/
├── architecture/            # Architecture documentation
│   ├── coding-standards.md # Coding conventions
│   ├── tech-stack.md        # Technology choices
│   └── source-tree.md       # This document
├── api/                     # API documentation
│   ├── openapi.yaml         # OpenAPI specification
│   └── postman/             # Postman collections
├── qa/                      # QA documentation
├── stories/                 # Development stories
├── AI_*.md                  # AI agent documentation
├── DATABASE_*.md            # Database documentation
├── FEATURE_*.md             # Feature documentation
└── prd/                     # Product requirements
```

## Scripts and Utilities

### `/scripts` - Maintenance Scripts

```
scripts/
├── apply_jwt_coverage.py    # JWT implementation
├── jwt_coverage_audit.py    # Security audit
├── test_auth_api.py         # API testing
├── test_feature_flags.py    # Feature flag testing
├── verify_auth_security.py  # Security verification
└── verify_sec001_fix.py     # Security fix verification
```

## Docker Configuration

### `/docker` - Container Definitions

```
docker/
├── Dockerfile.backend       # Backend container
├── Dockerfile.frontend      # Frontend container
└── docker-compose.override.yml # Local overrides
```

## Key Configuration Files

### Root Configuration Files

| File | Purpose |
|------|---------|
| `.env.example` | Environment variables template |
| `.env.test` | Test environment configuration |
| `.gitignore` | Git ignore patterns |
| `.pre-commit-config.yaml` | Pre-commit hooks |
| `docker-compose.yml` | Docker services |
| `docker-compose.monitoring.yml` | Monitoring stack |
| `requirements.txt` | Python dependencies |
| `main.py` | FastAPI entry point |

### Frontend Configuration Files

| File | Purpose |
|------|---------|
| `package.json` | Node dependencies |
| `next.config.js` | Next.js configuration |
| `tailwind.config.ts` | Tailwind CSS config |
| `tsconfig.json` | TypeScript config |
| `.eslintrc.json` | ESLint rules |
| `.prettierrc` | Prettier formatting |

## Environment-Specific Files

### Development Environment
- `.env.development` - Development variables
- `docker-compose.override.yml` - Local Docker overrides
- `.vscode/` - VS Code settings

### Test Environment
- `.env.test` - Test variables
- `test.db` - SQLite test database
- `coverage/` - Coverage reports

### Production Environment
- `.env.production` - Production variables (via Doppler)
- `deployment/` - Deployment configurations
- `monitoring/` - Production monitoring

## Generated Files and Directories

### Build Artifacts
```
frontend/.next/              # Next.js build output
frontend/out/                # Static export
dist/                        # Distribution files
build/                       # Build output
```

### Cache and Temporary
```
__pycache__/                 # Python bytecode
.pytest_cache/               # Pytest cache
.coverage                    # Coverage data
node_modules/                # Node dependencies
.venv/                       # Python virtual environment
```

## Module Dependencies

### Core Dependencies Flow
```
main.py
  └── api/routers/*
      └── services/*
          └── database/models/*
              └── database/db_setup

frontend/app/*
  └── components/*
      └── lib/api
          └── services/api
```

### Service Layer Dependencies
```
services/
  ├── agentic_assessment
  │   └── openai, langchain
  ├── compliance_graph_initializer
  │   └── neo4j
  ├── framework_service
  │   └── database/repositories
  └── reporting/
      └── reportlab, python-docx
```

## Key Entry Points

### Backend Entry Points
- `main.py` - FastAPI application
- `celery_worker.py` - Background tasks
- `alembic/` - Database migrations

### Frontend Entry Points
- `app/layout.tsx` - Root layout
- `app/page.tsx` - Home page
- `middleware.ts` - Edge middleware

### Testing Entry Points
- `pytest` - Backend tests
- `npm test` - Frontend tests
- `playwright` - E2E tests

## Naming Conventions

### File Naming
- Python files: `snake_case.py`
- TypeScript files: `camelCase.ts` or `PascalCase.tsx`
- Test files: `test_*.py` or `*.test.ts`
- Config files: `lowercase.config.ext`

### Directory Naming
- Python packages: `snake_case/`
- React components: `PascalCase/`
- Routes: `kebab-case/`
- Resources: `plural_names/`

## Import Paths

### Python Imports
```python
# Absolute imports from root
from api.routers import auth
from database.models import User
from services.compliance_service import ComplianceService

# Relative imports within module
from .schemas import UserSchema
from ..utils import validate_input
```

### TypeScript Imports
```typescript
// Absolute imports with aliases
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/lib/api';

// Relative imports
import { Header } from './Header';
import type { User } from '../types';
```

## Development Workflow

### Adding New Features
1. Create feature branch
2. Add route in `api/routers/`
3. Implement service in `services/`
4. Add model if needed in `database/models/`
5. Create frontend components in `components/`
6. Add tests in `tests/` and `__tests__/`
7. Update documentation

### Common Tasks
- **Add API endpoint**: `api/routers/` → `services/` → `database/`
- **Add UI component**: `components/` → `hooks/` → `lib/api`
- **Add background task**: `services/` → `celery_tasks.py`
- **Add database table**: `database/models/` → `alembic revision`

## Maintenance Notes

### Regular Updates
- Dependencies: Monthly security updates
- Documentation: Update with each feature
- Tests: Maintain 80% coverage minimum
- Migrations: Test rollback procedures

### Code Organization Rules
1. Keep files under 500 lines
2. One component per file
3. Group related functionality
4. Clear module boundaries
5. Consistent naming patterns

## Technical Debt Areas

### Known Issues
- Legacy payment module in `services/legacy/`
- Callback-based code in older services
- Some missing TypeScript types
- Incomplete test coverage in `frontend/components/payment/`

### Planned Refactoring
- Migrate to full async/await
- Complete TypeScript coverage
- Implement service mesh pattern
- Add comprehensive E2E tests