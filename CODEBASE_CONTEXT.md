# ComplianceGPT Codebase Context Specification

## Project Overview
ComplianceGPT is an AI-powered compliance automation platform targeting UK SMBs. The system provides end-to-end compliance management including scoping, policy generation, implementation planning, evidence collection, and readiness assessment.

## Technology Stack

### Core Framework
- **Web Framework**: FastAPI with uvicorn server
- **Language**: Python 3.13+
- **Architecture**: Service-oriented with clear separation of concerns

### Data Layer
- **Database**: PostgreSQL with SQLAlchemy ORM 2.0+
- **Migrations**: Alembic for database schema management
- **Connection**: psycopg2-binary driver

### AI/ML Integration
- **Primary AI**: Google Generative AI (Gemini 2.5 Flash Preview)
- **Fallback**: OpenAI GPT models (optional)
- **Token Management**: tiktoken for token counting

### Infrastructure
- **Containerization**: Docker with docker-compose
- **Task Queue**: Celery with Redis backend
- **Caching**: Redis for session management and caching
- **Monitoring**: Prometheus metrics, optional Sentry integration

### Security & Authentication
- **JWT**: python-jose for token handling
- **Password Hashing**: passlib with bcrypt
- **CORS**: Configurable origins
- **Rate Limiting**: Custom middleware implementation

## Directory Structure & Components

### `/api/` - API Layer
**FastAPI-based REST API with comprehensive endpoint coverage**

```
api/
├── routers/           # Endpoint definitions grouped by domain
│   ├── auth.py            # Authentication & authorization
│   ├── users.py           # User management
│   ├── business_profiles.py # Business profile management
│   ├── assessments.py     # Compliance assessments
│   ├── frameworks.py      # Compliance framework data
│   ├── policies.py        # Policy generation & management
│   ├── implementation.py  # Implementation plan management
│   ├── evidence.py        # Evidence item CRUD operations
│   ├── readiness.py       # Readiness scoring & gap analysis
│   ├── reporting.py       # Report generation & scheduling
│   ├── integrations.py    # External service integrations
│   └── chat.py            # AI assistant chat interface
├── schemas/           # Pydantic models for request/response validation
│   ├── base.py            # Base schema classes
│   ├── models.py          # Core business model schemas
│   ├── chat.py            # Chat and AI interaction schemas
│   └── reporting.py       # Report-specific schemas
├── middleware/        # HTTP middleware components
│   ├── error_handler.py   # Global error handling
│   ├── rate_limiter.py    # API rate limiting
│   └── security_headers.py # Security header injection
├── dependencies/      # FastAPI dependency injection
│   └── auth.py            # Authentication dependencies
├── integrations/      # External service integration logic
│   ├── base/              # Base integration classes
│   ├── google_workspace_integration.py # Google Workspace
│   └── oauth_config.py    # OAuth configuration
└── utils/             # API utility functions
    ├── circuit_breaker.py # Circuit breaker pattern
    ├── retry.py           # Retry mechanisms
    └── validators.py      # Custom validation logic
```

### `/database/` - Data Model Layer
**SQLAlchemy models representing the domain entities**

```
database/
├── db_setup.py        # Database connection & session management
├── init_db.py         # Database initialization script
├── user.py            # User account model
├── business_profile.py # Business profile & settings
├── assessment_session.py # Compliance assessment sessions
├── compliance_framework.py # Framework definitions
├── evidence_item.py   # Evidence collection & storage
├── generated_policy.py # AI-generated policy documents
├── implementation_plan.py # Implementation plan tracking
├── readiness_assesment.py # Readiness score calculations
├── chat_conversation.py # AI chat conversation history
└── chat_message.py    # Individual chat messages
```

### `/services/` - Business Logic Layer
**Core business logic separated from API concerns**

```
services/
├── assessment_service.py  # Compliance assessment logic
├── business_service.py    # Business profile management
├── evidence_service.py    # Evidence collection & validation
├── framework_service.py   # Framework data management
├── implementation_service.py # Implementation plan logic
├── policy_service.py      # Policy generation & management
├── readiness_service.py   # Readiness scoring algorithms
├── ai/                    # AI-powered services
│   ├── assistant.py           # Main AI assistant logic
│   ├── context_manager.py     # Conversation context management
│   └── prompt_templates.py    # Structured AI prompts
├── automation/            # Evidence automation services
│   ├── evidence_processor.py  # Evidence processing pipeline
│   ├── duplicate_detector.py  # Duplicate evidence detection
│   └── quality_scorer.py      # Evidence quality assessment
└── reporting/             # Report generation services
    ├── report_generator.py    # Core report generation
    ├── pdf_generator.py       # PDF-specific generation
    ├── template_manager.py    # Report template management
    └── report_scheduler.py    # Automated report scheduling
```

### `/workers/` - Background Task Processing
**Celery-based asynchronous task execution**

```
workers/
├── evidence_tasks.py      # Evidence collection & processing tasks
├── compliance_tasks.py    # Compliance scoring & monitoring tasks
├── notification_tasks.py  # Email & notification tasks
└── reporting_tasks.py     # Report generation & distribution tasks
```

### `/config/` - Configuration Management
**Application configuration and settings**

```
config/
├── settings.py        # Application settings with environment support
├── ai_config.py       # AI service configuration
├── logging_config.py  # Logging setup and configuration
└── log_config.yaml    # Structured logging configuration
```

### `/tests/` - Testing Framework
**Comprehensive testing covering all application layers**

```
tests/
├── conftest.py        # Pytest configuration and fixtures
├── test_services.py   # Service layer unit tests
├── test_security.py   # Security testing
├── test_performance.py # Performance benchmarks
├── test_integration.py # API integration tests
├── test_e2e_workflows.py # End-to-end workflow tests
├── test_ai_ethics.py  # AI behavior validation
├── test_compliance_accuracy.py # Compliance logic validation
├── test_usability.py  # User experience testing
├── integration/       # Integration test suites
│   └── test_evidence_flow.py # End-to-end evidence workflows
└── load/             # Load testing configurations
    └── locustfile.py     # Multi-user load testing scenarios
```

### `/scripts/` - Operational Scripts
**Deployment, migration, and operational utilities**

```
scripts/
├── deploy.py          # Deployment readiness checker
└── migrate_evidence.py # Database migration utilities
```

### `/monitoring/` - Observability
**Monitoring and alerting configuration**

```
monitoring/
├── prometheus.yml     # Prometheus scraping configuration
└── alert_rules.yml    # Alerting rules and thresholds
```

## Core Domain Models

### Primary Entities

#### 1. **User** (`database/user.py`)
- Authentication and authorization
- Role-based access control
- Profile management

#### 2. **BusinessProfile** (`database/business_profile.py`)
- Company information and settings
- Industry classification
- Compliance framework selection
- Integration configuration

#### 3. **ComplianceFramework** (`database/compliance_framework.py`)
- Framework definitions (ISO27001, SOC2, GDPR, etc.)
- Control mappings and requirements
- Assessment criteria

#### 4. **EvidenceItem** (`database/evidence_item.py`)
- Manual and automated evidence collection
- Framework mapping and categorization
- Quality scoring and validation
- Integration source tracking

#### 5. **AssessmentSession** (`database/assessment_session.py`)
- Compliance assessment workflows
- Progress tracking
- Results and recommendations

#### 6. **GeneratedPolicy** (`database/generated_policy.py`)
- AI-generated policy documents
- Customization and versioning
- Framework alignment

#### 7. **ImplementationPlan** (`database/implementation_plan.py`)
- Step-by-step implementation guidance
- Timeline and resource planning
- Progress tracking

#### 8. **ReadinessAssessment** (`database/readiness_assesment.py`)
- Compliance readiness scoring
- Gap analysis and recommendations
- Historical tracking

### AI-Powered Entities

#### 9. **ChatConversation** (`database/chat_conversation.py`)
- AI assistant conversation management
- Context preservation
- User interaction history

#### 10. **ChatMessage** (`database/chat_message.py`)
- Individual messages in conversations
- Role-based message handling (user/assistant)
- Metadata for analysis

## Key Integration Points

### 1. **Authentication Flow**
```
Client Request → FastAPI Middleware → JWT Validation → 
Database User Lookup → Service Authorization → Business Logic
```

### 2. **Evidence Collection Pipeline**
```
Integration Trigger → Celery Task Queue → OAuth Authentication →
Data Collection → Evidence Processing → Quality Scoring →
Database Storage → Notification
```

### 3. **AI Assistant Workflow**
```
User Message → Context Gathering → Intent Classification →
AI Processing (Gemini) → Response Generation → 
Context Updates → Response Delivery
```

### 4. **Report Generation Pipeline**
```
Report Request → Data Collection → Template Processing →
PDF Generation → Storage → Email Distribution (optional)
```

## API Endpoint Structure

### Authentication & User Management
- `POST /api/auth/login` - User authentication
- `POST /api/auth/register` - User registration
- `GET /api/users/profile` - User profile retrieval

### Business Operations
- `POST /api/business-profiles` - Create business profile
- `GET /api/frameworks` - Available compliance frameworks
- `POST /api/assessments` - Start compliance assessment
- `GET /api/readiness/{profile_id}` - Readiness scoring

### Evidence Management
- `GET /api/evidence` - List evidence items
- `POST /api/evidence` - Create evidence item
- `GET /api/evidence/stats` - Evidence statistics

### Policy & Implementation
- `POST /api/policies/generate` - AI policy generation
- `GET /api/implementation/{profile_id}` - Implementation plans

### Reporting
- `POST /api/reports/generate` - Generate reports
- `POST /api/reports/schedules` - Schedule automated reports
- `GET /api/reports/download/{report_id}` - Download reports

### Integrations
- `GET /api/integrations` - Available integrations
- `POST /api/integrations/{type}/connect` - Connect integration
- `POST /api/integrations/collect/{profile_id}` - Trigger collection

### AI Assistant
- `POST /api/chat/conversations` - Start conversation
- `POST /api/chat/conversations/{id}/messages` - Send message
- `GET /api/chat/conversations/{id}` - Get conversation history

## Background Task Organization

### Evidence Queue (`workers/evidence_tasks.py`)
- **Daily Evidence Collection**: Automated data gathering from integrations
- **Evidence Processing**: Quality scoring and duplicate detection
- **Expiry Monitoring**: Track and notify about expiring evidence
- **Integration Status Sync**: Monitor integration health

### Compliance Queue (`workers/compliance_tasks.py`)
- **Compliance Score Updates**: Recalculate readiness scores
- **Gap Analysis**: Identify compliance gaps
- **Framework Updates**: Process framework definition changes

### Reporting Queue (`workers/reporting_tasks.py`)
- **Scheduled Report Generation**: Automated report creation
- **Report Distribution**: Email delivery of reports
- **Report Cleanup**: Archive and cleanup old reports

### Notification Queue (`workers/notification_tasks.py`)
- **Email Notifications**: General notification delivery
- **Alert Processing**: Critical alert handling
- **Reminder System**: Automated reminders for actions

## Development Patterns & Conventions

### 1. **Service Layer Pattern**
All business logic is encapsulated in service classes with clear interfaces:
```python
# Example service structure
class EvidenceService:
    def __init__(self, db: Session):
        self.db = db
    
    @authenticated
    def create_evidence(self, user_id: UUID, evidence_data: EvidenceCreate) -> EvidenceItem:
        # Business logic here
        pass
```

### 2. **Dependency Injection**
FastAPI dependency injection for database sessions, authentication, and services:
```python
# API endpoint with dependencies
@router.post("/evidence")
async def create_evidence(
    evidence_data: EvidenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = EvidenceService(db)
    return service.create_evidence(current_user.id, evidence_data)
```

### 3. **Error Handling Strategy**
Centralized error handling with custom exceptions and HTTP status mapping:
```python
# Custom exceptions
class ComplianceGPTException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
```

### 4. **Async/Await Pattern**
Consistent use of async operations for I/O-bound tasks:
```python
# AI service async operations
async def process_message(self, message: str) -> tuple[str, dict]:
    context = await self.context_manager.get_conversation_context(...)
    response = await self._call_ai_service(message, context)
    return response
```

## Configuration Management

### Environment-Based Configuration
Settings are managed through environment variables with sensible defaults:

```python
# config/settings.py
class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    google_api_key: Optional[str] = None
    secret_key: str
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
```

### AI Service Configuration
Centralized AI model configuration with fallback options:

```python
# config/ai_config.py
AI_CONFIG = {
    "google": {
        "model": "gemini-2.5-flash-preview-05-20",
        "temperature": 0.1,
        "max_tokens": 8192
    }
}
```

## Security Implementation

### 1. **Authentication & Authorization**
- JWT-based authentication with secure token handling
- Role-based access control (RBAC)
- OAuth integration for external services

### 2. **Data Protection**
- Input validation with Pydantic models
- SQL injection protection through SQLAlchemy
- XSS protection with proper sanitization
- CORS configuration for frontend integration

### 3. **API Security**
- Rate limiting to prevent abuse
- Security headers for protection
- Request size limits
- Secure error messages (no sensitive data exposure)

## Testing Strategy

### 1. **Unit Testing**
- Service layer unit tests with mocked dependencies
- Database model testing with test fixtures
- AI service testing with mocked responses

### 2. **Integration Testing**
- API endpoint testing with test database
- End-to-end workflow validation
- External service integration testing

### 3. **Load Testing**
- Multi-user scenario simulation with Locust
- Performance benchmarking
- Scalability validation

### 4. **Security Testing**
- Authentication and authorization testing
- Input validation testing
- Security vulnerability scanning

## Deployment & Operations

### 1. **Container Strategy**
- Docker-based development and production deployment
- Multi-service orchestration with Docker Compose
- Health checks and monitoring

### 2. **Database Management**
- Alembic-based schema migrations
- Connection pooling and optimization
- Backup and recovery procedures

### 3. **Monitoring & Observability**
- Prometheus metrics collection
- Structured logging with JSON format
- Alert rules for critical conditions
- Performance tracking and optimization

### 4. **Background Processing**
- Celery worker scaling and monitoring
- Queue management and prioritization
- Task failure handling and retry logic

## External Dependencies & Integrations

### Required Services
- **PostgreSQL 15+**: Primary database
- **Redis 7+**: Cache and message broker
- **Google AI API**: Primary AI service

### Optional Services
- **OpenAI API**: Secondary AI service
- **SMTP Server**: Email notifications
- **Prometheus**: Monitoring and metrics

### External Integrations
- **Google Workspace**: Evidence collection via OAuth
- **Microsoft 365**: Planned integration
- **Generic OAuth**: Framework for additional integrations

## Development Workflow

### 1. **Local Development Setup**
```bash
# Environment setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database setup
alembic upgrade head

# Start services
docker-compose up -d redis db
uvicorn main:app --reload

# Start workers
./start_workers.sh
```

### 2. **Testing Workflow**
```bash
# Run all tests
pytest

# Load testing
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Deployment readiness
python scripts/deploy.py --health-check
```

### 3. **Database Migrations**
```bash
# Create migration
alembic revision --autogenerate -m "Add new feature"

# Apply migration
alembic upgrade head
```

## Future Roadmap Considerations

### Planned Enhancements
1. **Multi-Framework Support**: Expanded compliance framework coverage
2. **Advanced AI Features**: More sophisticated AI analysis and recommendations
3. **Integration Expansion**: Additional cloud platform integrations
4. **Mobile Support**: Mobile-optimized interfaces
5. **Advanced Analytics**: Compliance trend analysis and predictive insights

### Scalability Considerations
1. **Microservice Evolution**: Potential transition to microservices architecture
2. **Database Sharding**: Horizontal scaling for large deployments
3. **CDN Integration**: Global content delivery optimization
4. **Caching Strategy**: Advanced caching for improved performance

---

This codebase context specification provides a comprehensive understanding of the ComplianceGPT project structure, components, and operational patterns. It serves as the definitive reference for development, maintenance, and future enhancements.