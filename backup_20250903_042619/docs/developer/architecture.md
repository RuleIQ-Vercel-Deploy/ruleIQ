# ruleIQ Architecture Context

## Purpose & Responsibility

The ruleIQ platform is an AI-powered compliance automation system designed for UK SMBs. It simplifies complex regulatory compliance through intelligent automation, assessment workflows, and evidence management.

## Architecture Overview

### **System Design Pattern**
- **Pattern**: Microservices-ready monolith with clear service boundaries
- **Approach**: Domain-driven design with separation of concerns
- **Scale**: Designed for horizontal scaling and future service extraction

### **Technology Stack**
```
Frontend: Next.js 15 + TypeScript + Tailwind CSS + shadcn/ui
Backend: FastAPI + Python 3.13 + SQLAlchemy + Alembic
Database: PostgreSQL 15 + Redis 7
AI: Google Gemini 2.5 Pro/Flash with circuit breaker patterns
Infrastructure: Docker + Celery + Prometheus monitoring
Testing: pytest (597 tests) + Vitest (159 tests) + Playwright E2E
Dev Tools: Serena MCP Server (IDE Assistant integration)
```

## Dependencies

### **Incoming Dependencies**
- **Frontend Client Applications**: Web browser-based compliance management interface
- **External Compliance APIs**: Regulatory framework data and updates
- **Third-party Integrations**: Google Workspace, Slack, Microsoft 365
- **Audit Systems**: External compliance reporting and audit trail consumers

### **Outgoing Dependencies**
- **Google AI Services**: Gemini 2.5 Pro/Flash for content generation and analysis
- **PostgreSQL Database**: Primary data persistence layer
- **Redis Cache**: Session management and response caching
- **File Storage**: Document and evidence storage system
- **Email Services**: Notification and communication systems

## Key Interfaces

### **Public APIs**
- **REST API**: `/api/v1/*` endpoints for all frontend interactions
- **WebSocket API**: `/api/chat/ws/{id}` for real-time AI assistance
- **Authentication**: JWT-based with refresh token support
- **Rate Limiting**: Tiered rate limits for different endpoint categories

### **Internal Interfaces**
- **Service Layer**: Business logic services with dependency injection
- **Data Layer**: SQLAlchemy ORM with async/sync dual support
- **AI Integration**: ComplianceAssistant service with circuit breaker
- **Background Tasks**: Celery workers for async processing

## Implementation Context

### **Current Development Status**
- **Backend**: ✅ Production Ready (597 tests, ~98% passing)
- **Frontend**: ✅ Business Profile Complete (159 tests, 100% passing for core features)
- **AI Integration**: 🔄 Week 1 Day 3 - Advanced optimization in progress
- **Database**: ⚠️ Schema issues identified requiring fixes
- **Overall Readiness**: 95% production ready

### **Technology Choices**

#### **Backend Framework: FastAPI**
- **Reasoning**: High performance, automatic OpenAPI generation, excellent async support
- **Benefits**: Type safety, dependency injection, built-in validation
- **Trade-offs**: Newer ecosystem compared to Django/Flask

#### **Frontend Framework: Next.js 15**
- **Reasoning**: App Router for modern React patterns, excellent SSR/SSG capabilities
- **Benefits**: Performance optimization, built-in TypeScript support, production-ready
- **Trade-offs**: Rapid release cycle requires maintenance overhead

#### **Database: PostgreSQL + Redis**
- **PostgreSQL**: ACID compliance for transactional data, excellent JSON support
- **Redis**: High-performance caching and session management
- **Benefits**: Proven scalability, comprehensive feature set
- **Trade-offs**: More complex setup than single-database solutions

#### **AI Integration: Google Gemini**
- **Reasoning**: State-of-the-art language model with function calling capabilities
- **Benefits**: Cost-effective, high-quality responses, comprehensive API
- **Trade-offs**: Vendor lock-in, external service dependency

### **Code Organization**

#### **Backend Structure**
```
/api/                    # API layer (routers, middleware, schemas)
├── routers/             # 19 endpoint routers
├── middleware/          # Security, rate limiting, error handling
├── dependencies/        # Auth and database dependencies
└── schemas/             # Pydantic request/response models

/services/               # Business logic layer
├── ai/                  # 25+ AI service modules
├── automation/          # Quality scoring and evidence processing
├── reporting/           # PDF generation and scheduling
└── monitoring/          # Health checks and metrics

/database/               # Data persistence layer
├── models.py            # SQLAlchemy model definitions
├── migrations/          # Alembic database migrations
└── [entity].py         # Individual model files

/config/                 # Configuration management
├── settings.py          # Environment-based configuration
├── ai_config.py         # AI model configuration
└── logging_config.py    # Structured logging setup
```

#### **Frontend Structure**
```
/app/                    # Next.js App Router
├── (auth)/              # Authentication pages
├── (dashboard)/         # Protected application pages
└── (public)/            # Marketing and public pages

/components/             # React component library
├── ui/                  # Base shadcn/ui components (90+ components)
├── features/            # Feature-specific components
├── assessments/         # Assessment workflow components
├── dashboard/           # Dashboard widgets and charts
└── shared/              # Reusable utility components

/lib/                    # Frontend utilities and services
├── api/                 # API client and service layer
├── stores/              # Zustand state management
├── hooks/               # Custom React hooks
├── validations/         # Zod validation schemas
└── utils/               # Utility functions and helpers
```

### **Testing Strategy**

#### **Backend Testing (597 tests)**
- **Unit Tests**: Service layer and utility functions
- **Integration Tests**: API endpoints with database
- **Performance Tests**: Load testing with Locust
- **Security Tests**: Authentication and authorization
- **AI Tests**: Model accuracy and compliance validation

#### **Frontend Testing (159 tests)**
- **Component Tests**: React component behavior
- **Integration Tests**: User flow validation
- **E2E Tests**: Complete user journeys with Playwright
- **Accessibility Tests**: WCAG compliance validation
- **Performance Tests**: Core Web Vitals monitoring

## Change Impact Analysis

### **Risk Factors**

#### **High-Risk Components**
1. **AI Service Integration**: External dependency with potential for service disruption
2. **Database Schema**: Column naming issues affecting ORM relationships
3. **Authentication System**: Security-critical component requiring careful changes
4. **Business Profile Service**: Core entity with widespread dependencies

#### **Breaking Change Potential**
1. **API Contract Changes**: Frontend-backend interface modifications
2. **Database Schema Changes**: Migration complexity and data integrity
3. **AI Model Changes**: Response format or behavior modifications
4. **Authentication Changes**: Token format or validation logic updates

#### **Rollback Considerations**
1. **Database Migrations**: Must be reversible with data preservation
2. **AI Model Updates**: Fallback to previous model versions
3. **Frontend Deployments**: Static asset rollback capabilities
4. **Configuration Changes**: Environment variable rollback procedures

### **Testing Requirements**

#### **Integration Test Coverage**
- **Critical Path**: User authentication → Business profile → Assessment workflow
- **AI Integration**: Timeout handling, fallback mechanisms, error scenarios
- **Database Operations**: Transaction integrity, concurrent access, migration testing
- **API Contracts**: Request/response validation, error handling, rate limiting

#### **Performance Test Scenarios**
- **Load Testing**: Concurrent user scenarios up to 1000 simultaneous users
- **AI Response Times**: Sub-3-second response time requirements
- **Database Performance**: Query optimization and index effectiveness
- **Frontend Performance**: Core Web Vitals within target thresholds

#### **Security Validation Needs**
- **Authentication Testing**: JWT token validation, refresh mechanisms, session security
- **Input Validation**: SQL injection, XSS prevention, file upload security
- **API Security**: Rate limiting effectiveness, authorization boundary testing
- **Data Protection**: Encryption at rest and in transit validation

## Development Tools Integration

### **Serena MCP Server**
The project integrates with Serena MCP Server for enhanced IDE assistance and development workflows.

#### **Configuration**
- **Context**: ide-assistant
- **Project Path**: Automatically set to current project directory
- **Integration**: Claude MCP protocol for advanced code assistance

#### **Features**
- Real-time code analysis and suggestions
- Context-aware development assistance
- Project-specific knowledge integration
- Enhanced debugging capabilities

#### **Initialization**
The Serena MCP server is initialized automatically when starting development sessions through the project initialization script (`scripts/init_dev_environment.sh`).

## Current Status

### **Development Phase: Week 1 Day 3 - AI Integration Optimization**

#### **Completed Work**
- ✅ Phase 1.5: AI Recommendations (AI service integration complete)
- ✅ Phase 2.1: Backend AI Endpoints (real endpoint integration)
- ✅ Core Infrastructure: Backend API, database, authentication
- ✅ Business Logic: Business profile management, evidence collection
- ✅ Frontend Foundation: Dashboard, authentication, business profile wizard

#### **Current Work: AI SDK Optimization (40+ hours)**
- 🔄 Multi-model strategy implementation (Gemini 2.5 Pro/Flash/Light, Gemma 3)
- 🔄 Streaming implementation for real-time responses
- 🔄 Function calling for structured AI interactions
- 🔄 Advanced caching and performance optimization
- 🔄 Enhanced error handling and resilience

#### **Known Issues & Technical Debt**

##### **Critical Issues**
1. **Database Column Naming**: Truncated column names breaking ORM relationships
   - Files: `database/business_profile.py`, `api/routers/business_profiles.py`
   - Impact: Requires field mapping workarounds
   - Priority: Critical - affects data integrity

2. **Frontend Authentication Security**: Tokens stored in localStorage without encryption
   - Files: `frontend/lib/stores/auth.store.ts`
   - Impact: XSS vulnerability
   - Priority: Critical - security risk

3. **API Input Validation**: Dynamic attribute setting without proper validation
   - Files: `services/evidence_service.py`
   - Impact: Potential injection attacks
   - Priority: High - security risk

##### **High Priority Issues**
1. **TypeScript Build Errors**: 26+ TypeScript errors ignored during build
   - Files: Various frontend components
   - Impact: Type safety compromised
   - Priority: High - code quality

2. **Database Performance**: N+1 query problems in pagination
   - Files: `services/evidence_service.py`
   - Impact: Performance degradation
   - Priority: High - scalability

3. **Error Handling Consistency**: Mixed error handling patterns across services
   - Files: Multiple service files
   - Impact: Debugging difficulty
   - Priority: Medium - maintainability

#### **Planned Improvements**

##### **Week 1 Completion (Days 4-5)**
- Phase 3.1: Conversational Assessment Mode
- Phase 3.2: Smart Adaptation
- Phase 3.3: Real-time Scoring

##### **Week 2-6 Roadmap**
- Advanced Features & Analytics
- User Experience & Performance optimization
- Testing & Quality Assurance
- Security & Compliance hardening
- Production Deployment preparation

## Context Dependencies

### **Related Documentation**
- **[AI_CONTEXT.md](../../AI_CONTEXT.md)**: Detailed AI optimization project context
- **[HANDOVER.md](../../HANDOVER.md)**: Project status and development history
- **[PROJECT_TASKS.md](../../PROJECT_TASKS.md)**: Detailed task tracking and progress
- **[CLAUDE.md](../../CLAUDE.md)**: Development guidelines and specifications
- **[Frontend Knowledge Graph](../../frontend/ruleIQ-knowledge-graph.md)**: Comprehensive dependency mapping

### **Architecture Decision Records**
- **ADR-001**: FastAPI selection for backend framework
- **ADR-002**: Next.js App Router adoption for frontend
- **ADR-003**: PostgreSQL + Redis dual database strategy
- **ADR-004**: Google Gemini AI integration approach
- **ADR-005**: JWT authentication implementation
- **ADR-006**: Microservices-ready monolith architecture

### **API Specifications**
- **OpenAPI Spec**: Auto-generated from FastAPI endpoints
- **Frontend API**: TypeScript interfaces and service definitions
- **WebSocket API**: Real-time chat and streaming response specifications

---

**Document Metadata**
- Created: 2025-01-07
- Version: 1.0.0
- Authors: AI Assistant
- Review Status: Initial Draft
- Next Review: 2025-01-14
- Dependencies: HANDOVER.md, AI_CONTEXT.md, PROJECT_TASKS.md
- Change Impact: High - foundational architecture documentation