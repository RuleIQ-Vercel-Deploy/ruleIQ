# RuleIQ Project Architecture - September 2025

## Directory Structure Overview

### Core Backend Directories

#### `/alembic` - Database Migrations
- **Purpose**: Database schema version control
- **Key Files**: 15+ migration files
- **Recent**: RBAC tables, Google OAuth fields, API key tables, freemium tables
- **Pattern**: Timestamp-based versioning with merge heads

#### `/api` - API Layer
- **Total Files**: 95+ Python files
- **Structure**:
  - `/routers` (40+ endpoints): auth, compliance, ai_assessments, freemium, iq_agent, etc.
  - `/middleware` (10+ files): RBAC, rate limiting, security headers, cost tracking
  - `/schemas` (10+ files): Pydantic models for validation
  - `/dependencies` (6 files): Auth, database, file handling
  - `/clients` (5 files): External API integrations (Google, Microsoft, AWS, Okta)
  - `/integrations`: OAuth configurations, Xero, Google Workspace

#### `/services` - Business Logic Layer
- **Total Files**: 140+ Python files
- **Key Services**:
  - `/ai` (70+ files): Circuit breaker, fallback systems, evaluation framework
  - `/compliance`: UK compliance engine, GraphRAG research
  - `/security`: Authentication, authorization, encryption, audit logging
  - `/automation`: Evidence processing, quality scoring
  - `/reporting`: PDF generation, templates, scheduling
  - `/knowledge_graph`: Neo4j integration models
  - `/agents`: PydanticAI framework integration

#### `/database` - Data Models & Setup
- **Total Files**: 35+ Python files
- **Models**: User, BusinessProfile, Assessment, Evidence, Policy, etc.
- **Features**: Redis client, performance indexes, RBAC models
- **Services**: Integration service layer

#### `/langgraph_agent` - LangGraph Integration
- **Total Files**: 50+ Python files
- **Structure**:
  - `/graph`: State management, error handling, master integration
  - `/nodes`: Compliance, evidence, reporting, RAG nodes
  - `/agents`: RAG system, tool manager, memory manager
  - `/services`: AI service, compliance analyzer, evidence collector
  - `/core`: Neo4j service, constants, models

#### `/workers` - Background Tasks
- Celery workers for async processing
- Task scheduling and queue management

#### `/tests` - Test Suite
- **Total Files**: 180+ test files
- **Coverage Areas**:
  - Unit tests in `/unit`
  - Integration tests in `/integration`
  - Performance tests in `/performance`
  - Security tests in `/security`
  - E2E tests in `/e2e`
  - Monitoring tests in `/monitoring`

### Frontend Structure

#### `/frontend` - Next.js Application
- **Framework**: Next.js 15 with App Router
- **Component Library**: shadcn/ui + custom components
- **State Management**: Zustand stores + TanStack Query
- **Key Directories**:
  - `/app`: Next.js app router pages
  - `/components`: UI components (magicui, payment, ui)
  - `/lib`: API clients, utilities, stores
  - `/hooks`: Custom React hooks
  - `/types`: TypeScript definitions
  - `/scripts`: QA and fix automation scripts

### Supporting Directories

#### `/config` - Configuration Files
- Environment configurations
- Service configurations

#### `/monitoring` - Observability
- Metrics collection
- Health monitoring

#### `/utils` - Shared Utilities
- Common helper functions
- Shared constants

#### `/vectorstores` - Vector Database
- Embedding storage for RAG

#### `/data` - Static Data
- Reference data
- Configuration data

#### `/uploads` - File Storage
- User uploads
- Generated documents

## Architecture Patterns

### Backend Architecture
- **Pattern**: Service-Oriented Architecture (SOA)
- **API Design**: RESTful with FastAPI
- **Authentication**: JWT + RBAC middleware
- **Database**: PostgreSQL (Neon) + Redis cache
- **Background Jobs**: Celery + Redis queue
- **AI Integration**: LangGraph + circuit breaker pattern

### Frontend Architecture
- **Pattern**: Component-based with atomic design
- **Routing**: File-based with Next.js App Router
- **Styling**: TailwindCSS + CSS modules
- **Data Fetching**: TanStack Query with caching
- **State**: Zustand for client, server state via Query

### AI/ML Architecture
- **RAG System**: LangGraph nodes with Neo4j knowledge graph
- **Fallback**: Circuit breaker with graceful degradation
- **Evaluation**: Golden datasets with custom metrics
- **Cost Management**: Token tracking and optimization

### Security Architecture
- **Authentication**: Multi-layer JWT + OAuth
- **Authorization**: RBAC with granular permissions
- **Encryption**: AES-GCM for sensitive data
- **Rate Limiting**: Tiered limits by endpoint type
- **Audit**: Comprehensive logging system

## Key Integration Points
1. **LangGraph**: Central orchestration for AI workflows
2. **Neo4j**: Knowledge graph for compliance data
3. **Redis**: Caching and queue management
4. **Neon PostgreSQL**: Primary data store
5. **External APIs**: Google, Microsoft, AWS, Okta integrations