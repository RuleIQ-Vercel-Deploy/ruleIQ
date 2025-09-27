# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**ruleIQ** is an enterprise-grade agentic AI compliance automation platform designed specifically for UK Small and Medium Businesses (SMBs). Unlike traditional compliance tools, ruleIQ implements intelligent agents that build ongoing relationships with users, evolving from helpers to trusted advisors to autonomous partners.

### Core Features

- **🤖 IQ Agent** - GraphRAG-powered compliance orchestrator with PPALE intelligence loop
- **🔍 RAG Self-Critic** - Automated fact-checking and response validation system
- **🕸️ LangGraph Workflows** - Multi-agent orchestration with state persistence
- **🧠 Memory Systems** - Conversation, knowledge graph, and pattern memory
- **📊 Trust Gradient** - Three-level progression: Helper → Advisor → Partner
- **🎯 Predictive Intelligence** - Proactive compliance monitoring and risk alerts

## Essential Commands

### Quick Start
```bash
# Start all services (recommended)
./start.sh

# Start backend only
uvicorn api.main:app --reload --port 8000

# Start frontend with Turbopack (faster)
cd frontend && pnpm dev:turbo

# Start workers
celery -A api.workers worker --loglevel=info
```

### Development Environment Setup
```bash
# Python backend setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend && pnpm install

# Database setup
alembic upgrade head
python scripts/seed_database.py

# Neo4j knowledge graph setup
python services/neo4j_service.py
```

### Testing Commands (1884+ Tests)
```bash
# Fast unit tests (2-5 minutes)
make test-fast

# Complete test suite with agentic systems
make test-full

# Test groups (recommended approach)
make test-groups                 # All 6 groups sequentially
make test-groups-parallel       # All 6 groups in parallel (fastest)

# Specific test groups
make test-group-unit            # Unit tests (2-3 min)
make test-group-ai              # AI core tests (3-4 min)
make test-group-api             # Basic API tests (4-5 min)
make test-group-endpoints       # AI endpoints (5-6 min)
make test-group-advanced        # Advanced features (3-4 min)
make test-group-e2e             # End-to-end tests (6-8 min)

# Frontend testing
cd frontend
pnpm test                       # Unit tests with Vitest
pnpm test:e2e                   # E2E tests with Playwright
pnpm test:coverage              # Coverage reports
```

### Code Quality
```bash
# Python linting and formatting
ruff check .                    # Linting
ruff format .                   # Formatting

# Frontend quality checks
cd frontend
pnpm lint                       # ESLint
pnpm typecheck                  # TypeScript checking
pnpm format                     # Prettier formatting
```

### Database Operations
```bash
# PostgreSQL migrations
alembic upgrade head            # Apply migrations
alembic revision --autogenerate -m "description"  # Create migration

# Neo4j knowledge graph
python services/compliance_graph_initializer.py   # Initialize compliance graph
python services/neo4j_service.py                  # Manage Neo4j operations
```

### Docker Operations
```bash
# Full stack with Docker Compose
docker-compose up -d            # Start all services
docker-compose logs -f backend  # View backend logs
docker-compose logs -f iq_agent # View IQ Agent logs
docker-compose down             # Stop all services

# Individual service builds
docker build -t ruleiq-backend .
docker build -f Dockerfile.freemium -t ruleiq-freemium .
```

## Architecture Overview

ruleIQ follows a **microservices architecture with agentic AI orchestration**:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway    │    │   IQ Agent      │
│  (Next.js 15)   │◄──►│   (FastAPI)      │◄──►│  (LangGraph)    │
│   + Turbopack   │    │   + Routers      │    │  + GraphRAG     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                ┌─────────────────────────────────────────┐
                │          Service Layer                  │
                │  • Agentic Assessment & RAG             │
                │  • Compliance Graph Initializer         │
                │  • Memory Manager & Retrieval           │
                │  • Performance Monitor & Security       │
                └─────────────────────────────────────────┘
                                 │
                                 ▼
                ┌─────────────────────────────────────────┐
                │        Data & Storage Layer             │
                │  • PostgreSQL (Primary DB + Sessions)   │
                │  • Neo4j (Knowledge Graph - 20+ nodes)  │
                │  • Redis (Caching + Rate Limiting)      │
                │  • Vector Store (Embeddings)            │
                └─────────────────────────────────────────┘
```

### Project Structure

```
ruleIQ/
├── api/                        # FastAPI backend with routers
│   ├── routers/               # API endpoint definitions
│   └── main.py                # FastAPI app entry point
├── services/                  # 18+ microservice modules
│   ├── iq_agent.py           # Core IQ Agent with GraphRAG
│   ├── agentic_rag.py        # RAG system with self-critique
│   ├── agentic_assessment.py # Conversational assessments
│   ├── compliance_memory_manager.py  # Memory systems
│   ├── neo4j_service.py      # Knowledge graph operations
│   └── langgraph_workflows/  # Multi-agent orchestration
├── langgraph_agent/          # LangGraph agent implementation
│   ├── agents/               # Specialized agent nodes
│   ├── core/                 # Core models and constants
│   ├── graph/                # Workflow graph definitions
│   └── services/             # Agent-specific services
├── frontend/                 # Next.js 15 + Turbopack app
│   ├── src/                  # React components and pages
│   ├── stories/              # Storybook component stories
│   └── tests/                # Frontend test suites
├── database/                 # Database schemas and migrations
├── tests/                    # Comprehensive Python test suite (1884+ tests)
├── config/                   # Configuration management
├── scripts/                  # Automation and CI/CD scripts
└── docs/                     # Project documentation
```

## Agentic Intelligence Architecture

### IQ Agent - Core Intelligence Loop (PPALE)

The IQ Agent implements the **PPALE** intelligence loop:

1. **PERCEIVE** - Query compliance posture from Neo4j knowledge graph
2. **PLAN** - Risk-weighted prioritization with enforcement precedent analysis  
3. **ACT** - Execute compliance controls and update graph
4. **LEARN** - Pattern recognition and effectiveness analysis
5. **REMEMBER** - Memory consolidation and knowledge building

### GraphRAG Implementation

```python
# IQ Agent leverages Neo4j GraphRAG for compliance intelligence
from services.iq_agent import IQComplianceAgent
from services.neo4j_service import Neo4jGraphRAGService

# Core architecture
agent = IQComplianceAgent(
    neo4j_service=Neo4jGraphRAGService(),
    llm_model='gpt-4'
)

# Knowledge graph with 20+ node types:
# - Regulations, Controls, Frameworks
# - Risk Assessments, Evidence, Patterns  
# - User Interactions, Memory Traces
```

### RAG Self-Critic System

```python
# Automated fact-checking with 85%+ confidence thresholds
from services.rag_self_critic import RAGSelfCritic

critic = RAGSelfCritic()
validated_response = await critic.fact_check_with_sources(
    query="GDPR Article 33 breach notification requirements",
    confidence_threshold=0.85
)
```

### Trust Gradient Progression

- **Level 1: Transparent Helper** (Current) - Shows reasoning, asks confirmation
- **Level 2: Trusted Advisor** (6 months) - Makes confident suggestions, learns preferences  
- **Level 3: Autonomous Partner** (12 months) - Takes initiative, prevents issues

## Tech Stack & Datastores

### Backend Stack
```python
# Core Framework
FastAPI                 # High-performance async API framework
uvicorn                # ASGI server
pydantic               # Data validation and serialization

# AI & ML
openai                 # GPT-4 integration
langchain             # LLM orchestration framework  
langgraph             # Multi-agent workflows
chromadb              # Vector database for embeddings

# Databases
sqlalchemy            # PostgreSQL ORM
psycopg               # PostgreSQL adapter
neo4j                 # Knowledge graph database
redis                 # Caching and session management

# Background Processing
celery                # Distributed task queue
```

### Frontend Stack
```bash
# Core Framework
Next.js 15            # React framework with App Router
Turbopack             # Ultra-fast bundler (60% faster than Webpack)
TypeScript            # Type-safe development

# State Management  
@tanstack/react-query # Server state management
zustand               # Client state management

# UI Framework
@radix-ui/*          # Accessible component primitives
tailwindcss          # Utility-first styling
framer-motion        # Animation library

# Data Visualization
@nivo/*              # Chart library
recharts             # Additional charting
victory              # Statistical visualizations
```

### Database Architecture

#### PostgreSQL (Primary Database)
- **Tables**: 15+ core tables with optimized indexing
- **Features**: JSONB support, full-text search, audit trails
- **Performance**: 40-90% improvement with advanced indexing

#### Neo4j (Knowledge Graph)
- **Nodes**: 20+ types (Regulations, Controls, Frameworks, Users, Assessments)
- **Relationships**: Complex compliance mappings and dependencies
- **Usage**: GraphRAG queries, pattern recognition, memory systems

#### Redis (Caching Layer)
- **Session Management**: JWT token storage and validation
- **Rate Limiting**: Multi-tier protection (auth, general, AI endpoints)
- **Circuit Breaker**: API failure protection with fallback responses

## Development Workflow

### Environment Configuration

Required environment variables:
```bash
# Database URLs
DATABASE_URL=postgresql://user:pass@localhost/ruleiq_dev
NEO4J_URI=neo4j+s://your-instance.neo4j.io
REDIS_URL=redis://localhost:6379

# AI Services
OPENAI_API_KEY=your_openai_key
GOOGLE_AI_API_KEY=your_gemini_key

# Security
JWT_SECRET_KEY=your_jwt_secret
SESSION_SECRET=your_session_secret

# Optional: Secrets Management
DOPPLER_PROJECT=ruleiq
DOPPLER_CONFIG=dev
```

### Hot Reloading

- **Backend**: `uvicorn api.main:app --reload` for automatic Python reloading
- **Frontend**: `pnpm dev:turbo` for ultra-fast Turbopack HMR (~200ms reloads)
- **Workers**: `celery -A api.workers worker --loglevel=info --reload`

### Code Quality Gates

```bash
# Pre-commit hooks (automatically run)
pre-commit install
pre-commit run --all-files

# Manual quality checks
make lint-check               # Python and TypeScript linting
make format-check            # Code formatting verification
make security-scan           # Security vulnerability scanning
make type-check              # TypeScript type checking
```

## Testing & CI Infrastructure

### Test Organization (1884+ Tests)

#### Backend Tests
```bash
# Test groups provide optimal parallelization
make test-group-unit         # 600+ unit tests (2-3 min)
make test-group-ai           # 400+ AI core tests (3-4 min) 
make test-group-api          # 300+ API tests (4-5 min)
make test-group-endpoints    # 250+ AI endpoint tests (5-6 min)
make test-group-advanced     # 200+ advanced feature tests (3-4 min)
make test-group-e2e          # 134+ end-to-end tests (6-8 min)

# Specialized test categories
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests
pytest -m ai                # AI/ML specific tests
pytest -m slow              # Long-running tests
pytest -m security          # Security tests
```

#### Frontend Tests
```bash
cd frontend

# Unit tests with Vitest
pnpm test                   # Run all unit tests
pnpm test:watch             # Watch mode for development
pnpm test:coverage          # Generate coverage reports

# E2E tests with Playwright  
pnpm test:e2e               # End-to-end tests
pnpm test:e2e:ui            # Visual test runner
pnpm test:e2e:headed        # Run with browser UI

# Visual regression tests
pnpm test:visual            # Component snapshots
pnpm test:accessibility     # A11y compliance tests
```

### Continuous Integration

#### GitHub Actions Workflows
- **CI Pipeline**: Automated testing on PR/push
- **Security Scanning**: SonarCloud integration  
- **Docker Builds**: Multi-stage container builds
- **Blue-Green Deployments**: Zero-downtime production deployments

#### Quality Gates
- **Code Coverage**: Minimum 70% threshold
- **Security Score**: 8.5/10 enterprise-grade
- **Performance**: <200ms SLO for API endpoints
- **Accessibility**: WCAG 2.2 AA compliance

## Deployment Architecture

### Docker Compose (Development)
```bash
# Start full development stack
docker-compose up -d

# Individual services
docker-compose up -d backend    # FastAPI backend
docker-compose up -d frontend   # Next.js frontend  
docker-compose up -d redis      # Redis cache
docker-compose up -d neo4j      # Neo4j knowledge graph
```

### Production Deployment (Cloud Run)
```bash
# Build and deploy
gcloud builds submit --config cloudbuild.yaml

# Monitor deployment
gcloud run services list --region=europe-west2
gcloud logging read "resource.type=cloud_run_revision"
```

### Environment-Specific Configurations
- **Development**: `docker-compose.yml` + `.env`
- **Staging**: `docker-compose.preprod.yml` 
- **Production**: `docker-compose.prod.yml` + Doppler secrets
- **CI Testing**: `docker-compose.ci.yml`

## Governance & Best Practices

### Code Standards (from CLAUDE.md)

#### Python Standards
- **Indentation**: 4 spaces (enforced by ruff)
- **Type Hints**: Required for all functions
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Imports**: Organized and formatted by ruff

#### Frontend Standards  
- **Components**: PascalCase files (`MyComponent.tsx`)
- **Hooks**: Use `useSomething` naming convention
- **Linting**: ESLint + Prettier enforced
- **Type Safety**: Full TypeScript coverage required

### Security Requirements
- **Secrets**: Never commit secrets; use `.env.template` for placeholders
- **Authentication**: JWT-only with HS256 algorithm (Stack Auth removed)
- **Rate Limiting**: Multi-tier protection implemented
- **Input Validation**: Comprehensive whitelist-based validation
- **OWASP Compliance**: Regular security audits

### Pull Request Process
- **Conventional Commits**: Use `feat:`, `fix:`, `chore:` prefixes
- **Testing**: Include verification commands in PR description
- **Security**: Run secret scanner before pushing
- **Review**: Request review from appropriate domain experts
- **Documentation**: Update relevant docs for architectural changes

### Priority Gates (STRICTLY ENFORCED)
- **P0 Must Complete Before P1**: No P1 work until ALL P0 tasks pass
- **Sequential Gating**: Each priority level blocks the next
- **Timeframes**: P0 (24h max), P1 (48h max), P2 (1 week max)

### AI Safety & Trust Gradient
- **RAG Self-Critic**: 85%+ confidence threshold for AI responses
- **Evidence Requirements**: Minimum 3 independent sources for major claims
- **Verification**: Primary sources required (legislation.gov.uk, EUR-Lex)
- **Transparency**: Show reasoning and confidence levels to users

## Performance Metrics

### Response Times
- **API Endpoints**: 78.9-125.3ms average (<200ms SLO)
- **IQ Agent Quick Check**: ~2-5 seconds  
- **Standard AI Queries**: ~10-30 seconds with streaming
- **Complex Analysis**: ~15-45 seconds
- **Database Queries**: 40-90% improvement with indexing

### Frontend Performance
- **Initial Load**: <3s with Turbopack optimization
- **Hot Reloads**: ~200ms (60% faster with Turbopack)
- **Core Web Vitals**: All metrics in green
- **Bundle Size**: Optimized with tree shaking and code splitting

### Cost Optimization
- **AI Costs**: 40-60% reduction through intelligent caching
- **Database**: Query optimization with proper indexing
- **Redis**: Circuit breaker pattern prevents API overuse

This architecture represents a production-ready foundation with clear paths for completing AI integration and scaling to enterprise requirements.