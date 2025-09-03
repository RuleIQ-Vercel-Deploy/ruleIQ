# API Context

## Purpose & Responsibility

The API layer provides the REST interface for the ruleIQ compliance automation platform. It implements secure, performant endpoints for authentication, business profile management, compliance assessments, AI services, evidence collection, and reporting.

## Architecture Overview

### **API Design Pattern**
- **Pattern**: RESTful API with OpenAPI specification generation
- **Approach**: Router-based organization with middleware layers
- **Framework**: FastAPI with automatic validation and documentation

### **API Structure**
```
Base URL: /api/v1
Authentication: JWT Bearer tokens with refresh mechanism
Documentation: Auto-generated OpenAPI/Swagger at /docs
Rate Limiting: Tiered limits by endpoint category
Content-Type: application/json (primary), multipart/form-data (uploads)
```

## Dependencies

### **Incoming Dependencies**
- **Frontend Application**: Primary consumer for all UI interactions
- **Mobile Applications**: Future mobile app integration
- **Third-party Integrations**: Webhook endpoints for external services
- **Monitoring Systems**: Health check and metrics endpoints
- **Admin Tools**: Administrative interface and reporting

### **Outgoing Dependencies**
- **Database Layer**: PostgreSQL for data persistence
- **AI Services**: Google Gemini integration for intelligent features
- **File Storage**: Document and evidence storage systems
- **Authentication Service**: JWT token validation and user management
- **Background Tasks**: Celery workers for async processing
- **Cache Layer**: Redis for session and response caching

## Key Interfaces

### **API Router Organization**

#### **Authentication & Users** (`/api/auth/*`, `/api/users/*`)
```python
POST /api/auth/register          # User registration
POST /api/auth/login            # User authentication
POST /api/auth/token            # OAuth2-compatible token endpoint
POST /api/auth/refresh          # Token refresh
POST /api/auth/logout           # Session termination
GET  /api/users/me              # Current user profile
PUT  /api/users/me              # Update user profile
```

#### **Business Profiles** (`/api/business-profiles/*`)
```python
POST /api/business-profiles/    # Create/update business profile
GET  /api/business-profiles/    # Get user's business profile
PUT  /api/business-profiles/{id} # Update specific profile
DELETE /api/business-profiles/{id} # Delete profile
```

#### **Assessments** (`/api/assessments/*`)
```python
GET  /api/assessments/          # List user assessments
POST /api/assessments/          # Create new assessment
GET  /api/assessments/{id}      # Get assessment details
PUT  /api/assessments/{id}      # Update assessment
DELETE /api/assessments/{id}    # Delete assessment
POST /api/assessments/quick     # Quick compliance recommendations
```

#### **AI Services** (`/api/ai/*`)
```python
# Assessment AI endpoints
POST /api/ai/assessments/{framework_id}/help
POST /api/ai/assessments/followup
POST /api/ai/assessments/analysis
POST /api/ai/assessments/analysis/stream
POST /api/ai/assessments/recommendations
POST /api/ai/assessments/recommendations/stream

# AI health and monitoring
GET  /api/ai/health
GET  /api/ai/circuit-breaker/status
POST /api/ai/circuit-breaker/reset
GET  /api/ai/models/{model_name}/health
GET  /api/ai/rate-limit-stats
POST /api/ai/feedback
GET  /api/ai/metrics
```

#### **Evidence Management** (`/api/evidence/*`)
```python
GET  /api/evidence/            # List evidence items
POST /api/evidence/            # Create evidence item
GET  /api/evidence/{id}        # Get evidence details
PUT  /api/evidence/{id}        # Update evidence
DELETE /api/evidence/{id}      # Delete evidence
POST /api/evidence/upload      # File upload
GET  /api/evidence/search      # Search evidence
```

#### **Policy Generation** (`/api/policies/*`)
```python
GET  /api/policies/            # List generated policies
POST /api/policies/generate    # Generate new policy
GET  /api/policies/{id}        # Get policy details
PUT  /api/policies/{id}        # Update policy
DELETE /api/policies/{id}      # Delete policy
GET  /api/policies/{id}/download # Download policy document
```

#### **Chat & Real-time** (`/api/chat/*`)
```python
GET  /api/chat/conversations   # List conversations
POST /api/chat/conversations   # Create conversation
GET  /api/chat/conversations/{id} # Get conversation details
POST /api/chat/conversations/{id}/messages # Send message
WS   /api/chat/ws/{id}         # WebSocket connection
```

### **API Middleware Stack**

#### **Security Middleware**
```python
SecurityHeadersMiddleware       # CORS, CSP, HSTS headers
CORSMiddleware                 # Cross-origin request handling
AuthenticationMiddleware       # JWT token validation
AuthorizationMiddleware        # Role-based access control
```

#### **Performance Middleware**
```python
RateLimitingMiddleware         # Request rate limiting
CachingMiddleware             # Response caching
CompressionMiddleware         # Response compression
RequestTimeoutMiddleware      # Request timeout handling
```

#### **Monitoring Middleware**
```python
RequestLoggingMiddleware      # Request/response logging
ErrorHandlingMiddleware       # Structured error responses
MetricsMiddleware            # Performance metrics collection
RequestIdMiddleware          # Request correlation tracking
```

### **Rate Limiting Configuration**

#### **Tiered Rate Limits**
```python
RATE_LIMITS = {
    'auth': {
        'login': '5/minute',          # Login attempts
        'register': '3/minute',       # Registration attempts
        'refresh': '10/minute'        # Token refresh
    },
    'api': {
        'standard': '100/minute',     # Standard API calls
        'upload': '10/minute',        # File uploads
        'search': '50/minute'         # Search operations
    },
    'ai': {
        'help': '10/minute',          # AI question help
        'followup': '5/minute',       # Follow-up generation
        'analysis': '3/minute',       # Assessment analysis
        'recommendations': '3/minute', # Recommendations
        'chat': '30/minute'           # Chat messages
    }
}
```

#### **Burst Allowances**
```python
BURST_ALLOWANCES = {
    'ai_help': 2,                # Allow 2 additional requests
    'ai_followup': 1,            # Allow 1 additional request
    'ai_analysis': 1,            # Allow 1 additional request
    'standard_api': 20           # Allow 20 additional requests
}
```

## Implementation Context

### **Request/Response Patterns**

#### **Standard Response Format**
```python
# Success Response
{
    "data": { ... },             # Response payload
    "message": "Success",        # Human-readable message
    "status": 200,              # HTTP status code
    "timestamp": "2025-01-07T...", # ISO timestamp
    "request_id": "req_123..."   # Request correlation ID
}

# Error Response
{
    "detail": "Error message",   # Error description
    "error_code": "VALIDATION_ERROR", # Machine-readable error code
    "status": 400,              # HTTP status code
    "timestamp": "2025-01-07T...", # ISO timestamp
    "request_id": "req_123...",  # Request correlation ID
    "validation_errors": [...]   # Field-specific errors (if applicable)
}

# Paginated Response
{
    "items": [...],             # Data items
    "total": 100,              # Total item count
    "page": 1,                 # Current page number
    "size": 20,                # Items per page
    "has_next": true,          # Has next page
    "has_prev": false,         # Has previous page
    "request_id": "req_123..."
}
```

#### **File Upload Response**
```python
# File Upload Success
{
    "file_id": "file_123...",   # Unique file identifier
    "filename": "document.pdf", # Original filename
    "file_size": 1048576,      # File size in bytes
    "file_type": "application/pdf", # MIME type
    "storage_path": "/evidence/...", # Storage location
    "upload_timestamp": "2025-01-07T...",
    "request_id": "req_123..."
}
```

### **Authentication & Authorization**

#### **JWT Token Structure**
```python
# Access Token Payload
{
    "sub": "user_uuid",         # User identifier
    "email": "user@example.com", # User email
    "is_active": true,          # Account status
    "is_superuser": false,      # Admin privileges
    "exp": 1704649200,         # Expiration timestamp
    "iat": 1704645600,         # Issued at timestamp
    "jti": "token_uuid"        # Token identifier
}

# Refresh Token Payload (longer-lived)
{
    "sub": "user_uuid",
    "type": "refresh",          # Token type
    "exp": 1707237600,         # 30-day expiration
    "iat": 1704645600,
    "jti": "refresh_uuid"
}
```

#### **Authorization Patterns**
```python
# Route-level authorization
@router.get("/admin/metrics")
async def admin_metrics(
    current_user: User = Depends(require_admin)
):
    # Admin-only endpoint

# Resource-level authorization
@router.get("/evidence/{evidence_id}")
async def get_evidence(
    evidence_id: UUID,
    current_user: User = Depends(get_current_user)
):
    # Verify user owns the evidence
    if evidence.user_id != current_user.id:
        raise HTTPException(403, "Access denied")
```

### **Input Validation & Security**

#### **Pydantic Request Models**
```python
class BusinessProfileCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    industry: str = Field(..., min_length=1, max_length=100)
    employee_count: int = Field(..., gt=0, le=10000)
    handles_personal_data: bool
    processes_payments: bool
    
    @field_validator('company_name')
    @classmethod
    def validate_company_name(cls, v):
        # Custom validation logic
        if not re.match(r'^[a-zA-Z0-9\s\-&.]+$', v):
            raise ValueError('Invalid company name format')
        return v.strip()
```

#### **Security Validation** ⚠️
```python
# CURRENT ISSUE: Dynamic attribute setting without validation
# services/evidence_service.py:346-353
for field, value in update_data.items():
    if hasattr(item, field):
        setattr(item, field, value)  # UNSAFE - no validation

# REQUIRED FIX: Whitelist allowed fields
ALLOWED_UPDATE_FIELDS = {'title', 'description', 'status', 'notes'}

def validate_update_data(update_data: Dict[str, Any]) -> Dict[str, Any]:
    validated = {}
    for field, value in update_data.items():
        if field not in ALLOWED_UPDATE_FIELDS:
            raise ValidationError(f"Field '{field}' is not allowed")
        validated[field] = sanitize_input(value)
    return validated
```

### **Error Handling Patterns**

#### **Exception Hierarchy**
```python
class APIException(Exception):
    """Base API exception"""
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "Internal server error"

class ValidationException(APIException):
    status_code = 400
    error_code = "VALIDATION_ERROR"

class AuthenticationException(APIException):
    status_code = 401
    error_code = "AUTHENTICATION_ERROR"

class AuthorizationException(APIException):
    status_code = 403
    error_code = "AUTHORIZATION_ERROR"

class NotFoundException(APIException):
    status_code = 404
    error_code = "NOT_FOUND"
```

#### **Global Error Handler**
```python
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "status": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(request.state, 'request_id', None)
        }
    )
```

### **Performance Optimization**

#### **Database Query Optimization**
```python
# Efficient pagination with cursor-based approach
async def paginate_evidence(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 20,
    cursor: Optional[str] = None
) -> PaginatedResponse:
    query = select(EvidenceItem).where(
        EvidenceItem.user_id == user_id
    ).order_by(EvidenceItem.created_at.desc())
    
    if cursor:
        query = query.where(EvidenceItem.created_at < decode_cursor(cursor))
    
    items = await db.execute(query.limit(limit + 1))
    # ... pagination logic
```

#### **Response Caching**
```python
@cache(expire=300)  # 5-minute cache
async def get_dashboard_data(user_id: UUID) -> DashboardData:
    # Expensive dashboard data aggregation
    return await aggregate_dashboard_metrics(user_id)
```

## Change Impact Analysis

### **Risk Factors**

#### **High-Risk Areas**
1. **Authentication Changes**: Token format or validation modifications
2. **Breaking API Changes**: Request/response schema modifications
3. **Rate Limiting Changes**: Could affect user experience
4. **Database Schema Changes**: Requiring API contract updates
5. **AI Integration Changes**: Model response format changes

#### **Breaking Change Potential**
1. **Request/Response Models**: Pydantic schema changes
2. **Authentication Flow**: JWT structure or validation changes
3. **Error Response Format**: Error handling modifications
4. **File Upload Process**: Upload endpoint or response changes
5. **WebSocket Protocol**: Real-time communication changes

### **Testing Requirements**

#### **API Contract Testing**
- **OpenAPI Validation**: Ensure responses match OpenAPI specification
- **Schema Validation**: Request/response schema compliance
- **Authentication Testing**: Token validation and authorization
- **Rate Limiting Testing**: Rate limit enforcement and recovery
- **Error Scenario Testing**: Comprehensive error response validation

#### **Performance Testing**
- **Load Testing**: Concurrent request handling under load
- **Stress Testing**: API behavior under extreme load
- **Response Time Testing**: SLA compliance measurement
- **Rate Limiting Testing**: Limit enforcement and burst handling
- **Database Performance**: Query optimization validation

#### **Security Testing**
- **Input Validation**: SQL injection and XSS prevention
- **Authentication Testing**: Token security and session management
- **Authorization Testing**: Access control boundary validation
- **File Upload Security**: Malicious file upload prevention
- **API Abuse Testing**: Rate limiting and DDoS protection

## Current Status

### **Production Readiness Assessment**
- **API Design**: ✅ Well-designed RESTful interface with OpenAPI
- **Authentication**: ✅ Secure JWT implementation with refresh tokens
- **Rate Limiting**: ✅ Comprehensive tiered rate limiting
- **Error Handling**: ✅ Structured error responses with correlation IDs
- **Performance**: ✅ Optimized with caching and database optimization
- **Security Issues**: ⚠️ Input validation gaps need addressing

### **Current API Metrics**
- **Endpoints**: 25+ endpoints across 12 routers
- **Test Coverage**: 597 backend tests covering all endpoints
- **Response Times**: <500ms for standard operations
- **Rate Limits**: Tiered limits with burst allowances
- **Documentation**: Auto-generated OpenAPI specification

### **Known Issues & Technical Debt**

#### **Critical Security Issues**
1. **Input Validation**: Dynamic attribute setting without validation
2. **Error Information Leakage**: Internal details exposed in error messages
3. **Session Security**: Excessive session timeout durations
4. **File Upload Validation**: Insufficient file type and content validation

#### **Performance Optimizations Needed**
1. **Database Queries**: N+1 query problems in pagination
2. **Response Caching**: Inconsistent caching strategies
3. **Connection Pooling**: Pool optimization for high concurrency
4. **Background Tasks**: Async processing optimization

### **Required Actions Before Production**

#### **Phase 1: Security Hardening (Week 1)**
1. **Fix input validation vulnerabilities** - Whitelist allowed fields
2. **Sanitize error messages** - Remove internal details from responses
3. **Optimize session management** - Reduce session timeouts
4. **Enhance file upload security** - Add content validation

#### **Phase 2: Performance Optimization (Week 2)**
1. **Optimize database queries** - Fix N+1 problems
2. **Implement consistent caching** - Standardize cache strategies
3. **Optimize connection pooling** - Tune for production load
4. **Add comprehensive monitoring** - API metrics and alerting

#### **Phase 3: Documentation & Testing (Week 3)**
1. **Complete OpenAPI documentation** - Ensure all endpoints documented
2. **Add integration tests** - End-to-end API workflow testing
3. **Performance benchmarking** - Establish baseline metrics
4. **Security audit** - Comprehensive penetration testing

---

**Document Metadata**
- Created: 2025-01-07
- Version: 1.0.0
- Authors: AI Assistant
- Review Status: Initial Draft
- Next Review: 2025-01-10
- Dependencies: ARCHITECTURE_CONTEXT.md, DATABASE_CONTEXT.md
- Change Impact: Medium - well-designed with identified security issues
- Related Files: api/routers/*, api/middleware/*, api/schemas/*