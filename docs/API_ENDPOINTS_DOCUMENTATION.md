# ruleIQ API Endpoints Documentation

## Overview

This document provides comprehensive documentation for all ruleIQ API endpoints. The API follows RESTful principles with a consistent `/api/v1/` versioning pattern.

**Base URL**: `http://localhost:8000` (Development) | `https://api.ruleiq.com` (Production)
**API Version**: v1
**Authentication**: JWT Bearer Token
**API Documentation**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

## Table of Contents

1. [Authentication & Authorization](#authentication--authorization)
2. [Business Profiles](#business-profiles)
3. [AI Services](#ai-services)
4. [Assessments](#assessments)
5. [Compliance Frameworks](#compliance-frameworks)
6. [IQ Agent](#iq-agent)
7. [Monitoring & Health](#monitoring--health)
8. [Security](#security)

## Authentication & Authorization

### Overview
JWT-based authentication with role-based access control (RBAC). Tokens expire after 30 minutes with 7-day refresh tokens.

### Endpoints

#### Register User
```http
POST /api/v1/auth/register
```
Creates a new user account with automatic `business_user` role assignment.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "company_name": "Acme Corp"
}
```

**Response:** `201 Created`
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "role": "business_user",
  "created_at": "2025-01-19T10:00:00Z"
}
```

#### Login
```http
POST /api/v1/auth/token
```
Authenticates user and returns JWT tokens.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Get Current User
```http
GET /api/v1/auth/me
```
Returns authenticated user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "business_user",
  "permissions": ["read", "write"]
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
```
Exchanges refresh token for new access token.

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ...",
  "expires_in": 1800
}
```

#### Logout
```http
POST /api/v1/auth/logout
```
Invalidates current tokens (adds to Redis blacklist).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

### Rate Limiting
- Authentication endpoints: 5 requests/minute
- Password reset: 3 requests/hour
- General API: 100 requests/minute

## Business Profiles

### Overview
Manages company information and business profiles for compliance assessments.

### Endpoints

#### Get Business Profile
```http
GET /api/v1/business-profiles/{profile_id}
```

**Response:** `200 OK`
```json
{
  "profile_id": "uuid",
  "company_name": "Acme Corp",
  "industry": "Technology",
  "employee_count": 150,
  "annual_revenue": "10M-50M",
  "compliance_frameworks": ["ISO27001", "GDPR"],
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-19T00:00:00Z"
}
```

#### Update Business Profile
```http
PUT /api/v1/business-profiles/{profile_id}
```

**Request Body:**
```json
{
  "industry": "FinTech",
  "employee_count": 200,
  "compliance_frameworks": ["ISO27001", "GDPR", "PCI-DSS"]
}
```

**Response:** `200 OK`

#### List Business Profiles
```http
GET /api/v1/business-profiles
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `industry`: Filter by industry
- `framework`: Filter by compliance framework

**Response:** `200 OK`
```json
{
  "profiles": [...],
  "total": 45,
  "page": 1,
  "pages": 3
}
```

## AI Services

### Overview
AI-powered assessment and compliance assistance services with circuit breaker protection and intelligent fallbacks.

### AI Assessment Assistant

#### Get AI Help
```http
POST /api/v1/ai-assessments/help
```
Provides intelligent assistance for assessment questions.

**Request Body:**
```json
{
  "question_id": "q123",
  "question_text": "What is your data retention policy?",
  "framework_id": "gdpr",
  "section_id": "data_protection",
  "user_context": {
    "business_profile": {
      "industry": "Technology",
      "employee_count": 150
    },
    "current_answers": {
      "q122": "We process customer data for service delivery"
    }
  }
}
```

**Response:** `200 OK`
```json
{
  "guidance": "Based on GDPR requirements for technology companies...",
  "confidence_score": 0.92,
  "related_topics": ["Article 5", "Data minimization"],
  "follow_up_suggestions": [
    "Define specific retention periods per data category",
    "Document legal basis for retention"
  ],
  "source_references": ["GDPR Article 5(1)(e)", "ICO Guidance"]
}
```

#### Stream Assessment Analysis
```http
POST /api/v1/ai-assessments/analyze/stream
```
Streams AI analysis results for real-time updates.

**Request Body:**
```json
{
  "assessment_id": "uuid",
  "framework": "iso27001",
  "responses": {...}
}
```

**Response:** `200 OK` (Server-Sent Events)
```
data: {"type": "progress", "message": "Analyzing controls...", "progress": 0.3}
data: {"type": "gap", "gap": {...}, "progress": 0.5}
data: {"type": "recommendation", "recommendation": {...}, "progress": 0.8}
data: {"type": "complete", "summary": {...}, "progress": 1.0}
```

#### Get AI Recommendations
```http
POST /api/v1/ai-assessments/recommendations
```
Generates personalized compliance recommendations.

**Request Body:**
```json
{
  "assessment_id": "uuid",
  "gaps": [...],
  "priority": "high",
  "timeframe": "3_months"
}
```

**Response:** `200 OK`
```json
{
  "recommendations": [
    {
      "id": "rec_001",
      "title": "Implement Access Control Policy",
      "priority": "high",
      "effort": "medium",
      "impact": "high",
      "description": "...",
      "action_items": [...],
      "resources": [...],
      "estimated_time": "2-4 weeks"
    }
  ],
  "roadmap": {
    "immediate": [...],
    "short_term": [...],
    "long_term": [...]
  }
}
```

### Rate Limiting
- AI Help: 20 requests/minute
- Streaming Analysis: 3 concurrent streams
- Recommendations: 10 requests/minute

### Error Handling
AI services implement circuit breaker pattern:
- Opens after 3 consecutive failures
- Half-open after 30 seconds
- Provides fallback responses when circuit is open

## Assessments

### Overview
Manages compliance assessments and questionnaires.

### Endpoints

#### Create Assessment
```http
POST /api/v1/assessments
```

**Request Body:**
```json
{
  "framework_id": "iso27001",
  "business_profile_id": "uuid",
  "name": "Q1 2025 ISO Assessment"
}
```

**Response:** `201 Created`
```json
{
  "assessment_id": "uuid",
  "status": "in_progress",
  "created_at": "2025-01-19T00:00:00Z"
}
```

#### Submit Assessment Response
```http
POST /api/v1/assessments/{assessment_id}/responses
```

**Request Body:**
```json
{
  "question_id": "q123",
  "response": "Yes",
  "evidence": ["policy_doc.pdf"],
  "notes": "Implemented in Q4 2024"
}
```

**Response:** `200 OK`

#### Get Assessment Results
```http
GET /api/v1/assessments/{assessment_id}/results
```

**Response:** `200 OK`
```json
{
  "assessment_id": "uuid",
  "completion_rate": 0.85,
  "compliance_score": 72,
  "gaps": [...],
  "recommendations": [...],
  "next_steps": [...]
}
```

## Compliance Frameworks

### Overview
Provides framework-specific requirements and guidance.

### Endpoints

#### List Frameworks
```http
GET /api/v1/frameworks
```

**Response:** `200 OK`
```json
{
  "frameworks": [
    {
      "id": "gdpr",
      "name": "General Data Protection Regulation",
      "version": "2016/679",
      "categories": ["data_protection", "privacy"]
    },
    {
      "id": "iso27001",
      "name": "ISO/IEC 27001:2022",
      "version": "2022",
      "categories": ["information_security", "risk_management"]
    }
  ]
}
```

#### Get Framework Details
```http
GET /api/v1/frameworks/{framework_id}
```

**Response:** `200 OK`
```json
{
  "id": "iso27001",
  "name": "ISO/IEC 27001:2022",
  "controls": [...],
  "requirements": [...],
  "assessment_methodology": {...}
}
```

## IQ Agent

### Overview
Intelligent compliance assistant powered by GraphRAG and LangGraph workflows.

### Endpoints

#### Start Conversation
```http
POST /api/v1/chat/start
```

**Request Body:**
```json
{
  "context": "compliance_assessment",
  "business_profile_id": "uuid"
}
```

**Response:** `200 OK`
```json
{
  "session_id": "uuid",
  "welcome_message": "Hello! I'm your compliance assistant...",
  "suggested_topics": ["GDPR compliance", "ISO 27001 certification"]
}
```

#### Send Message
```http
POST /api/v1/chat/message
```

**Request Body:**
```json
{
  "session_id": "uuid",
  "message": "What are the GDPR requirements for data retention?",
  "attachments": []
}
```

**Response:** `200 OK`
```json
{
  "response": "Under GDPR, data retention must follow...",
  "confidence": 0.94,
  "sources": ["GDPR Article 5", "ICO Guidance"],
  "follow_up_questions": [...],
  "action_items": []
}
```

#### Get Chat History
```http
GET /api/v1/chat/history/{session_id}
```

**Response:** `200 OK`
```json
{
  "session_id": "uuid",
  "messages": [...],
  "summary": "Discussion covered GDPR retention requirements...",
  "action_items": [...]
}
```

## Monitoring & Health

### Overview
System health monitoring and performance metrics.

### Endpoints

#### Health Check
```http
GET /health
```

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2025-01-19T10:00:00Z",
  "version": "1.0.0"
}
```

#### Detailed Health Status
```http
GET /api/v1/health/detailed
```

**Response:** `200 OK`
```json
{
  "api": "healthy",
  "database": "healthy",
  "redis": "healthy",
  "ai_services": {
    "gemini": "healthy",
    "openai": "degraded",
    "anthropic": "healthy"
  },
  "neo4j": "healthy",
  "uptime": 432000,
  "response_time_ms": 45
}
```

#### Metrics
```http
GET /api/v1/monitoring/metrics
```

**Response:** `200 OK`
```json
{
  "requests_per_minute": 145,
  "average_response_time_ms": 78,
  "error_rate": 0.002,
  "active_users": 34,
  "ai_tokens_used_today": 45000,
  "cache_hit_rate": 0.84
}
```

## Security

### Overview
Security testing and validation endpoints.

### Endpoints

#### CSP Report
```http
POST /api/v1/security/csp-report
```
Content Security Policy violation reporting endpoint.

**Request Body:**
```json
{
  "csp-report": {
    "document-uri": "https://app.ruleiq.com",
    "violated-directive": "script-src",
    "blocked-uri": "https://evil.com/script.js"
  }
}
```

**Response:** `204 No Content`

#### Security Headers Test
```http
GET /api/v1/security/headers-test
```

**Response:** `200 OK`
```json
{
  "headers_present": [
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Strict-Transport-Security"
  ],
  "missing_headers": [],
  "score": "A+"
}
```

## Error Responses

All endpoints follow consistent error response format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  },
  "request_id": "req_123abc",
  "timestamp": "2025-01-19T10:00:00Z"
}
```

### Common Error Codes
- `AUTHENTICATION_REQUIRED`: Missing or invalid token
- `PERMISSION_DENIED`: Insufficient permissions
- `VALIDATION_ERROR`: Request validation failed
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `SERVICE_UNAVAILABLE`: Temporary service issue
- `INTERNAL_ERROR`: Server error

## Pagination

Endpoints returning lists support pagination:

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `sort`: Sort field
- `order`: Sort order (asc/desc)

**Response Headers:**
- `X-Total-Count`: Total number of items
- `X-Page-Count`: Total number of pages
- `Link`: RFC 5988 pagination links

## Webhooks

Configure webhooks for real-time events:

```http
POST /api/v1/webhooks
```

**Supported Events:**
- `assessment.completed`
- `compliance.score.changed`
- `evidence.approved`
- `risk.identified`
- `framework.updated`

## SDK & Client Libraries

Official client libraries available:
- **JavaScript/TypeScript**: `@ruleiq/client`
- **Python**: `ruleiq-python`
- **Go**: `github.com/ruleiq/go-client`

## Support

For API support and questions:
- Documentation: https://docs.ruleiq.com
- API Status: https://status.ruleiq.com
- Support: api-support@ruleiq.com