# ruleIQ Project: Test Failure Resolution Checklist

## Priority 1: Database Model Issues (6-8 hours)
*Fixes 44 tests including the 5 Business Services failures*

- [ ] **1.1. Fix SQLAlchemy Relationship Configuration**
  - File: `database/models.py`
  - Action: Add missing `questions` relationship to `AssessmentSession` model
  - Implementation:
    ```python
    # Add association table if not present
    assessment_questions_association = Table(
        'assessment_questions_association',
        Base.metadata,
        Column('session_id', Integer, ForeignKey('assessment_sessions.id')),
        Column('question_id', Integer, ForeignKey('assessment_questions.id'))
    )
    
    # Add relationship to AssessmentSession class
    questions = relationship("AssessmentQuestion", 
                            secondary=assessment_questions_association)
    ```
  - Validation: Run `pytest tests/models/test_assessment_session.py -v`

- [ ] **1.2. Add Missing User Model Attribute**
  - File: `database/models.py`
  - Action: Ensure User model is properly defined and imported
  - Implementation: Verify User model has all required fields and relationships
  - Validation: Run `pytest tests/services/test_business_services.py -v`

- [ ] **1.3. Create Database Migration**
  - File: `alembic/versions/xxxx_add_questions_relationship.py`
  - Action: Generate migration for relationship changes
  - Command: `alembic revision --autogenerate -m "add_questions_relationship"`
  - Validation: Inspect migration file for correct changes

- [ ] **1.4. Apply Database Migration**
  - Command: `alembic upgrade head`
  - Validation: Verify database schema with `psql` or database tool

- [ ] **1.5. Update Database Connection Handling**
  - File: `database/db.py`
  - Action: Improve connection pool settings and add retry logic
  - Implementation:
    ```python
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,
        pool_pre_ping=True,
        connect_args={
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
    )
    ```
  - Validation: Run database connection tests

## Priority 2: Missing AI Service Methods (4-5 hours)
*Fixes 15+ tests including AI Optimization Endpoints failures*

- [ ] **2.1. Implement Missing AI Assistant Methods**
  - File: `services/ai/assistant.py`
  - Action: Add `generate_followup_questions()` and `get_question_help()` methods
  - Implementation:
    ```python
    @staticmethod
    async def generate_followup_questions(question_text, framework_id, business_context):
        # Implementation here
        
    @staticmethod
    async def get_question_help(question_id, question_text, framework_id, user_context):
        # Implementation here
    ```
  - Validation: Run `pytest tests/services/test_ai_services.py -v`

- [ ] **2.2. Create AI Optimization Endpoints**
  - File: `routes/ai/optimization.py` (create if not exists)
  - Action: Create new router with required endpoints
  - Implementation:
    ```python
    @router.post("/model-selection")
    async def model_selection(request: ModelSelectionRequest):
        # Implementation
        
    @router.get("/model-health")
    async def model_health_check():
        # Implementation
        
    @router.get("/performance-metrics")
    async def performance_metrics():
        # Implementation
    ```
  - Validation: Run `pytest tests/api/test_ai_optimization.py -v`

- [ ] **2.3. Register AI Optimization Router**
  - File: `main.py`
  - Action: Include the new router in the FastAPI app
  - Implementation: `app.include_router(optimization.router)`
  - Validation: Verify endpoints with Swagger UI

- [ ] **2.4. Implement AI Performance Metrics**
  - File: `services/ai/metrics.py` (create if not exists)
  - Action: Create metrics collection and reporting
  - Implementation: Add methods to track response times, token usage, etc.
  - Validation: Run `pytest tests/services/test_ai_performance.py -v`

## Priority 3: Security & Rate Limiting (3-4 hours)
*Fixes 9 tests including Security & Authorization failures*

- [ ] **3.1. Implement Rate Limiting Middleware**
  - File: `middleware/rate_limiting.py` (create if not exists)
  - Action: Create middleware for API rate limiting
  - Implementation:
    ```python
    class RateLimitingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            # Rate limiting logic
    ```
  - Validation: Run `pytest tests/security/test_rate_limiting.py -v`

- [ ] **3.2. Add Rate Limiting to FastAPI App**
  - File: `main.py`
  - Action: Register the rate limiting middleware
  - Implementation: `app.add_middleware(RateLimitingMiddleware, ...)`
  - Validation: Verify rate limiting with concurrent requests

- [ ] **3.3. Implement Role-Based Access Control**
  - File: `auth/rbac.py` (create if not exists)
  - Action: Create RBAC system with permission checks
  - Implementation:
    ```python
    class RBACPermission:
        def __init__(self, allowed_roles):
            self.allowed_roles = allowed_roles
        
        def __call__(self, current_user = Depends(get_current_user)):
            # Permission check logic
    ```
  - Validation: Run `pytest tests/security/test_rbac.py -v`

- [ ] **3.4. Apply RBAC to Protected Routes**
  - Files: Various route files
  - Action: Add RBAC dependency to protected endpoints
  - Implementation: `@router.get("/admin", dependencies=[Depends(admin_only)])`
  - Validation: Test access with different user roles

- [ ] **3.5. Fix Session Management Security**
  - File: `auth/session.py`
  - Action: Improve session validation and expiration
  - Implementation: Add proper token validation and expiration checks
  - Validation: Run `pytest tests/security/test_session_management.py -v`

## Priority 4: Performance Optimization (4-5 hours)
*Fixes 8 tests including API Performance failures*

- [ ] **4.1. Implement AI Response Caching**
  - File: `services/ai/caching.py` (create if not exists)
  - Action: Create caching system for AI responses
  - Implementation:
    ```python
    class AIResponseCache:
        @staticmethod
        def get_cached_response(prefix, **kwargs):
            # Cache retrieval logic
            
        @staticmethod
        def cache_response(response, prefix, **kwargs):
            # Cache storage logic
    ```
  - Validation: Run `pytest tests/performance/test_ai_performance.py -v`

- [ ] **4.2. Optimize Database Queries**
  - File: `database/optimized_queries.py` (create if not exists)
  - Action: Create optimized query functions
  - Implementation: Replace ORM with optimized SQL queries for critical paths
  - Validation: Run `pytest tests/performance/test_database_performance.py -v`

- [ ] **4.3. Implement Circuit Breaker for AI Services**
  - File: `services/ai/circuit_breaker.py` (create if not exists)
  - Action: Create circuit breaker pattern implementation
  - Implementation:
    ```python
    class AICircuitBreaker:
        def __init__(self):
            self.failure_count = 0
            self.state = "CLOSED"
            
        async def execute(self, func, *args, **kwargs):
            # Circuit breaker logic
    ```
  - Validation: Run `pytest tests/performance/test_circuit_breaker.py -v`

- [ ] **4.4. Add Memory Usage Optimization for Streaming**
  - File: `services/ai/streaming.py`
  - Action: Optimize memory usage in streaming responses
  - Implementation: Use generators and proper cleanup
  - Validation: Run `pytest tests/performance/test_memory_usage.py -v`

## Priority 5: AsyncClient Configuration (1-2 hours)
*Fixes 6 AsyncClient errors*

- [ ] **5.1. Fix AsyncClient Configuration in Tests**
  - File: `tests/conftest.py`
  - Action: Update AsyncClient fixture
  - Implementation:
    ```python
    @pytest.fixture
    async def async_client():
        async with AsyncClient(base_url="http://test") as ac:
            yield ac
    ```
  - Validation: Run tests with AsyncClient dependency

- [ ] **5.2. Update Test Cases Using AsyncClient**
  - Files: Various test files using AsyncClient
  - Action: Ensure proper usage of AsyncClient
  - Implementation: Check for correct parameter usage
  - Validation: Run affected tests

## Priority 6: Evidence Flow Integration (1-2 hours)
*Fixes 1 Evidence Flow Integration failure*

- [ ] **6.1. Fix Business Profile to Evidence Workflow**
  - File: `routes/evidence.py`
  - Action: Fix validation or processing in evidence creation
  - Implementation: Check request validation and error handling
  - Validation: Run `pytest tests/integration/test_evidence_flow.py -v`

- [ ] **6.2. Add Evidence Metadata Field**
  - File: `database/models.py`
  - Action: Add metadata field to EvidenceItem model
  - Implementation:
    ```python
    metadata = Column(JSON, default=dict)
    ```
  - Validation: Verify model changes with test data

## Priority 7: Dashboard Information and Feedback (2-3 hours)
*Fixes 3 Usability failures*

- [ ] **7.1. Implement Dashboard Information Hierarchy**
  - File: `frontend/components/dashboard/InformationHierarchy.tsx`
  - Action: Create component with required information sections
  - Implementation: Add compliance status, action items, and metrics
  - Validation: Run `pytest tests/frontend/test_dashboard.py -v`

- [ ] **7.2. Add Action Feedback and Confirmation**
  - File: `frontend/components/common/Feedback.tsx`
  - Action: Create feedback component for user actions
  - Implementation: Add toast notifications and confirmation dialogs
  - Validation: Run `pytest tests/frontend/test_feedback.py -v`

- [ ] **7.3. Implement Workflow Guidance**
  - File: `frontend/components/dashboard/NextSteps.tsx`
  - Action: Create component for next steps guidance
  - Implementation: Add clear next steps based on user progress
  - Validation: Run `pytest tests/frontend/test_workflow.py -v`

## Validation Plan

1. **Incremental Testing**
   - [ ] After each major fix, run related test groups
   - [ ] Track progress with test counts (passed/failed)

2. **Full Test Suite**
   - [ ] Run complete test suite after all fixes
   - [ ] Verify 100% pass rate: `pytest -v`

3. **Performance Verification**
   - [ ] Run performance tests with timing
   - [ ] Verify all thresholds are met

4. **Security Validation**
   - [ ] Verify rate limiting with load testing
   - [ ] Test RBAC with different user roles

## Dependencies Between Fixes

1. Database model fixes must be completed first (Priority 1)
2. AI service methods should be implemented before optimization (Priority 2 before 4)
3. AsyncClient configuration should be fixed early to enable proper testing (Priority 5)
4. Rate limiting and security can be implemented in parallel with other fixes

## Estimated Timeline

- **Priority 1 (Database)**: 6-8 hours
- **Priority 2 (AI Services)**: 4-5 hours
- **Priority 3 (Security)**: 3-4 hours
- **Priority 4 (Performance)**: 4-5 hours
- **Priority 5 (AsyncClient)**: 1-2 hours
- **Priority 6 (Evidence Flow)**: 1-2 hours
- **Priority 7 (Dashboard)**: 2-3 hours

**Total Estimated Time**: 21-29 hours

**Note**: Some tasks can be worked on in parallel by different team members to reduce total time.
