# ruleIQ Repository Map
Generated: 2025-01-09
Total Files: 1,467 | Directories: 53 | Lines of Code: ~200,000+

## Directory Structure

```
ruleIQ/
├── api/                    # [60+ files] FastAPI routes and schemas
│   ├── routers/           # API endpoints (many .jwt-backup files)
│   └── schemas/           # Pydantic models for validation
├── services/              # [40+ files] Business logic layer
│   ├── ai/               # AI service implementations
│   ├── compliance/       # Compliance engines
│   └── iq_agent.py      # Core IQ Agent (1200+ lines)
├── langgraph_agent/       # [30+ files] LangGraph workflow system
│   ├── graph/            # Graph definitions
│   ├── nodes/            # Workflow nodes
│   └── models/           # State models
├── database/              # [20+ files] Database models
│   ├── models/           # SQLAlchemy models
│   └── migrations/       # Alembic migrations
├── frontend/              # [70+ files] Next.js application
│   ├── app/              # App router pages
│   ├── components/       # React components
│   └── lib/              # Utilities
├── tests/                 # [150+ files] Test suites
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── ai/               # AI accuracy tests
├── scripts/               # [20+ files] Utility scripts
├── workers/               # [10+ files] Background tasks
├── config/                # [10+ files] Configuration
├── docker/                # [5+ files] Containerization
└── docs/                  # [30+ files] Documentation

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Databases**: PostgreSQL (Neon) + Neo4j (Graph)
- **AI/ML**: LangGraph, OpenAI GPT-4, Mistral
- **Background**: Celery → LangGraph migration
- **Testing**: Pytest (87% coverage)

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **UI**: TailwindCSS + shadcn/ui
- **State**: React Context + Hooks
- **Auth**: JWT (undergoing changes)

### Infrastructure
- **Containers**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Logging via Python logging
- **Deployment**: Cloud-ready architecture

## Key Components

### 1. IQ Agent System
- **Location**: `services/iq_agent.py`
- **Purpose**: Autonomous compliance orchestration
- **Architecture**: LangGraph 6-node workflow
- **Features**: Dual DB access, memory management, risk assessment

### 2. Master Integration Graph
- **Location**: `langgraph_agent/graph/master_integration_graph.py`
- **Purpose**: 4-phase compliance processing pipeline
- **Nodes**: 9 processing nodes with error handling
- **Integration**: RAG, Celery migration, state management

### 3. Neo4j Compliance Graph
- **Location**: `services/neo4j_service.py`
- **Purpose**: Knowledge graph for regulations
- **Schema**: Regulation → Requirement → Control
- **Coverage**: UK/EU/US jurisdictions

### 4. Business Profile System
- **Location**: `database/business_profile.py`
- **Purpose**: Company compliance context
- **Features**: Evidence management, assessment tracking

## Important Patterns

### API Structure
```
api/routers/{resource}.py → services/{resource}_service.py → database/models/{resource}.py
```

### LangGraph Workflow
```
StateGraph → add_node() → add_edge() → compile() → execute()
```

### Dual Database Pattern
```
PostgreSQL: Business data, users, evidence
Neo4j: Compliance graph, regulations, relationships
```

## Technical Debt

1. **JWT Backup Files**: 60+ .jwt-backup files indicating auth system changes
2. **Celery Migration**: Ongoing transition to LangGraph
3. **Test Flakiness**: Some integration tests are unstable
4. **Routing Inconsistency**: Mix of old and new patterns

## Entry Points

- **API**: `main.py` - FastAPI application
- **Frontend**: `frontend/app/page.tsx` - Next.js home
- **IQ Agent**: `services/iq_agent.py` - AI orchestrator
- **Graph**: `langgraph_agent/graph/master_integration_graph.py`