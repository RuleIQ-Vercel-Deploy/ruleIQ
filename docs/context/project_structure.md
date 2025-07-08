# Project Structure Analysis

## Directory Overview

The ruleIQ project is a comprehensive AI-powered compliance automation platform with both backend (Python/FastAPI) and frontend (Next.js/TypeScript) components.

### Backend Structure (`./`)
```
├── api/                     # FastAPI routers and endpoints
│   ├── routers/            # API route handlers (14 modules)
│   ├── schemas/            # Pydantic models for API
│   ├── middleware/         # Custom middleware (rate limiting, security)
│   └── dependencies/       # Dependency injection
├── services/               # Business logic layer
│   ├── ai/                # AI optimization services (25+ modules)
│   ├── automation/        # Evidence processing automation
│   ├── monitoring/        # Database and performance monitoring
│   └── reporting/         # PDF and report generation
├── database/              # SQLAlchemy models and migrations
├── config/                # Application configuration
├── utils/                 # Input validation and utilities
├── workers/               # Celery background tasks
└── tests/                 # Comprehensive test suite (671 tests)
```

### Frontend Structure (`./frontend/`)
```
├── app/                   # Next.js App Router pages
│   ├── (auth)/           # Authentication pages
│   ├── (dashboard)/      # Main application pages
│   └── (public)/         # Public marketing pages
├── components/           # React components
│   ├── ui/               # shadcn/ui base components (50+ components)
│   ├── features/         # Feature-specific components
│   ├── assessments/      # Assessment workflow components
│   ├── dashboard/        # Dashboard widgets and charts
│   └── shared/           # Reusable components
├── lib/                  # Libraries and utilities
│   ├── api/              # API client services (15+ services)
│   ├── stores/           # Zustand state management
│   ├── validations/      # Zod validation schemas
│   └── utils/            # Utility functions
├── tests/                # Frontend test suite
│   ├── e2e/              # Playwright end-to-end tests
│   ├── components/       # Component unit tests
│   └── integration/      # Integration tests
└── types/                # TypeScript type definitions
```

## File Count Summary
- **Total Files**: 27,819
- **Python Files**: 10,505 (backend logic, tests, scripts)
- **TypeScript Files**: 14,668 (frontend components, services, tests)
- **Markdown Files**: 1,872 (documentation, guides, specifications)

## Key Components

### Backend Services
- **AI Services**: 25 modules implementing Google Gemini integration with multi-model strategy
- **Assessment Engine**: Core compliance assessment logic
- **Evidence Management**: Automated evidence collection and processing
- **Security**: Input validation, rate limiting, authentication
- **Reporting**: PDF generation and scheduled reports

### Frontend Features
- **Assessment Wizard**: Multi-step compliance assessment workflow
- **Dashboard**: Real-time compliance metrics and widgets
- **Evidence Management**: File upload, categorization, and tracking
- **AI Integration**: Streaming responses, guidance, and recommendations
- **Team Management**: Role-based access control and collaboration

### Infrastructure
- **Database**: PostgreSQL with Alembic migrations
- **Caching**: Redis-based caching system
- **Background Tasks**: Celery workers for async processing
- **Testing**: 671+ backend tests, comprehensive frontend test suite
- **Deployment**: Docker containers with CI/CD pipelines

## Notable Files and Directories

### Critical Backend Files
- `main.py` - FastAPI application entry point
- `services/ai/assistant.py` - Core AI compliance assistant
- `api/routers/ai_assessments.py` - AI-powered assessment endpoints
- `utils/input_validation.py` - Security validation framework
- `database/` - Complete database schema with 8 migrations

### Critical Frontend Files
- `app/layout.tsx` - Root application layout
- `components/assessments/AssessmentWizard.tsx` - Main assessment flow
- `lib/stores/auth.store.ts` - Authentication state management
- `lib/utils/secure-storage.ts` - Secure token storage implementation
- `middleware.ts` - Next.js middleware for routing and security

### Configuration and Deployment
- `docker-compose.yml` - Multi-service deployment configuration
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies and scripts
- `.github/workflows/` - CI/CD pipeline definitions
- `alembic/versions/` - Database migration history

This structure represents a mature, production-ready application with comprehensive testing, security measures, and modern development practices.