# ruleIQ API Documentation

## Overview
This document provides comprehensive documentation for the ruleIQ Compliance Automation API, containing 235+ endpoints across 40+ functional categories.

**Base URL**: `http://localhost:8000` (Development) | `https://api.ruleiq.com` (Production)  
**API Version**: v2.0.0  
**Authentication**: JWT Bearer Token  
**OpenAPI Docs**: `/docs` | `/redoc`

## Authentication & Security

### Authentication Flow
1. **Register**: `POST /api/v1/auth/register` - Create account with auto business_user role
2. **Login**: `POST /api/v1/auth/token` - Get JWT access token
3. **Refresh**: `POST /api/v1/auth/refresh` - Refresh expired token
4. **Use Token**: Include `Authorization: Bearer <token>` header in requests

### Rate Limiting
- **General Endpoints**: 100 requests/minute
- **AI Endpoints**: 3-20 requests/minute (tiered by complexity)
- **Authentication**: 5 requests/minute

### RBAC Permissions
The API implements Role-Based Access Control with the following roles:
- `business_user`: Standard business user access
- `admin`: Administrative privileges
- `super_admin`: Full system access

## Core API Categories

### 🔐 Authentication & Authorization (6 endpoints)
**Base Path**: `/api/v1/auth`
- User registration, login, token management
- Role-based access control
- Password reset and account management

### 🏢 Business Profiles (6 endpoints) 
**Base Path**: `/api/v1/business-profiles`
- Company information management
- Industry classification and business details
- Profile validation and completion tracking

### 🧠 AI Assessment Assistant (8 endpoints)
**Base Path**: `/api/v1/ai-assessments`
- Intelligent compliance analysis
- Streaming assessment results
- AI-powered recommendations and help
- Circuit breaker protection for reliability

### 📋 Assessments (4 endpoints)
**Base Path**: `/api/v1/assessments`
- Compliance questionnaire management
- Assessment creation and submission
- Results tracking and analysis

### 🏛️ Compliance Frameworks (4 endpoints)
**Base Path**: `/api/v1/frameworks`
- GDPR, UK GDPR, Companies House, Employment Law
- Framework-specific requirements
- Regulatory updates and guidance

### 🆓 Freemium Assessment (6 endpoints)
**Base Path**: `/api/v1/freemium`
- Public compliance health checks
- No authentication required
- Email capture for lead generation
- Basic compliance scoring

### 🤖 IQ Agent (4 endpoints)
**Base Path**: `/api/v1/chat`
- Intelligent Compliance Agent with Neo4j integration
- Context-aware compliance assistance
- Multi-turn conversations
- Document analysis and recommendations

### 📊 Monitoring & Health (5 endpoints)
**Base Paths**: `/health`, `/api/v1/health`, `/api/v1/monitoring`
- System health checks with database monitoring
- Performance metrics and alerts
- Uptime and service availability

### 🔐 Secrets Vault (4 endpoints)
**Base Path**: `/api/v1/secrets`
- Secure credential management
- Encrypted secret storage
- Access control and audit logging

### 🔒 Security Testing (4 endpoints)
**Base Path**: `/api/v1/security`
- Security validation endpoints
- Penetration testing utilities
- Vulnerability assessment tools

## Advanced Features

### AI Services Architecture
The API implements sophisticated AI services with:
- **Circuit Breaker Pattern**: Prevents cascade failures
- **Fallback Responses**: Ensures service availability
- **Model Selection**: Dynamic model routing based on task complexity
- **Streaming Support**: Real-time response delivery
- **Rate Limiting**: Prevents AI service overload

### Database Integration
- **Primary Database**: Neon PostgreSQL (cloud-hosted)
- **Caching Layer**: Redis for performance optimization
- **Graph Database**: Neo4j for IQ Agent knowledge management
- **Field Mapping**: Handles legacy column name truncation

### Error Handling
- **Standardized Responses**: Consistent error format across all endpoints
- **HTTP Status Codes**: Proper status code usage
- **Detailed Messages**: Meaningful error descriptions
- **Request ID Tracking**: Unique request identifiers for debugging

## Testing with Postman

### Import Collection
1. Download `ruleiq_postman_collection.json`
2. Import into Postman
3. Set up environment variables:
   - `base_url`: `http://localhost:8000`
   - `jwt_token`: Your authentication token
   - `user_id`: Your user ID
   - `business_profile_id`: Your business profile ID

### Authentication Setup
The collection includes automatic token management:
- Pre-request scripts handle token validation
- Automatic token refresh when expired
- Collection-level authentication configuration

### Testing Workflows
1. **Registration Flow**: Register → Login → Get Profile
2. **Assessment Flow**: Create Assessment → Submit Responses → Get Results
3. **AI Analysis Flow**: Upload Evidence → Request Analysis → Stream Results
4. **Freemium Flow**: Public Health Check → Email Capture → Basic Report

## API Response Format

### Success Response
```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation successful",
  "request_id": "uuid-string"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { /* additional error context */ }
  },
  "request_id": "uuid-string"
}
```

### Pagination Response
```json
{
  "success": true,
  "data": {
    "items": [ /* array of items */ ],
    "total": 100,
    "page": 1,
    "per_page": 20,
    "total_pages": 5
  }
}
```

## Development Guidelines

### Request Headers
```
Content-Type: application/json
Authorization: Bearer <jwt_token>
X-Request-ID: <optional-uuid>
```

### File Upload Headers
```
Content-Type: multipart/form-data
Authorization: Bearer <jwt_token>
```

### Streaming Endpoints
For AI streaming responses:
```
Accept: text/event-stream
Authorization: Bearer <jwt_token>
```

## Production Considerations

### Performance
- API responses target <200ms average
- Database connection pooling enabled
- Redis caching for frequently accessed data
- CDN integration for static assets

### Security
- JWT tokens with AES-GCM encryption
- CORS configuration for allowed origins
- Request ID middleware for tracing
- Security headers middleware
- Input validation on all endpoints

### Monitoring
- Health check endpoints with database monitoring
- Performance metrics collection
- Error tracking and alerting
- Uptime monitoring integration

## Support & Resources

- **Interactive Documentation**: `/docs` (Swagger UI)
- **Alternative Documentation**: `/redoc` (ReDoc)
- **API Status**: Production-ready (98% complete, 671+ tests)
- **Support Email**: api-support@ruleiq.com
- **Documentation**: https://docs.ruleiq.com

---

**Generated**: 2025-08-22  
**API Version**: v2.0.0  
**Total Endpoints**: 235+  
**Categories**: 40+