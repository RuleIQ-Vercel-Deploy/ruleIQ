# JWT Authentication Implementation

## Overview

RuleIQ API uses JSON Web Token (JWT) authentication to secure API endpoints. This implementation provides:
- Token-based authentication with access and refresh tokens
- Token blacklisting for secure logout
- Rate limiting on authentication endpoints
- Automatic token expiry warnings
- Comprehensive security headers

## Protected Routes (20% Coverage Achieved)

The following critical API routes are protected with JWT authentication:

### User Management
- `/api/v1/users/*` - All user profile and management endpoints

### Administrative
- `/api/v1/admin/*` - Admin dashboard and user management
- `/api/v1/api/admin/*` - Administrative API operations

### Data Export
- `/api/v1/reports/export/*` - Report generation and export
- `/api/v1/evidence/export/*` - Evidence export functionality
- `/api/v1/audit-export/*` - Audit log exports

### Configuration & Settings
- `/api/v1/settings/*` - Application settings
- `/api/v1/business-profiles/*` - Business profile management

### Financial & Billing
- `/api/v1/payments/*` - Payment processing and billing

### API Management
- `/api/v1/api-keys/*` - API key creation and management
- `/api/v1/webhooks/*` - Webhook configuration

### Security & Secrets
- `/api/v1/secrets/*` - Secrets vault access

### Compliance & Assessments
- `/api/v1/assessments/*` - Assessment creation and management
- `/api/v1/compliance/*` - Compliance status and reports
- `/api/v1/policies/*` - Policy management

### AI Services
- `/api/v1/ai/*` - AI-powered features
- `/api/v1/iq-agent/*` - IQ Agent interactions
- `/api/v1/agentic-rag/*` - Agentic RAG operations

### Integrations & Monitoring
- `/api/v1/integrations/*` - Third-party integrations
- `/api/v1/dashboard/*` - Dashboard data
- `/api/v1/monitoring/*` - System monitoring
- `/api/v1/security/*` - Security operations
- `/api/v1/performance/*` - Performance metrics

## Authentication Flow

### 1. User Registration
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

Response:
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "is_active": true,
    "created_at": "2025-01-03T00:00:00Z"
  },
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer"
  }
}
```

### 2. User Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### 3. Using Protected Endpoints
```http
GET /api/v1/users/profile
Authorization: Bearer eyJ...

Response:
{
  "id": "uuid",
  "email": "user@example.com",
  "roles": ["business_user"],
  "permissions": ["view_profile", "edit_profile"]
}
```

### 4. Token Refresh
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### 5. Logout
```http
POST /api/v1/auth/logout
Authorization: Bearer eyJ...

Response:
{
  "message": "Logged out successfully"
}
```

## Token Configuration

### Access Tokens
- **Expiration**: 30 minutes (configurable via `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Algorithm**: HS256
- **Claims**: `sub` (user ID), `email`, `type` (access), `exp`, `iat`

### Refresh Tokens
- **Expiration**: 30 days (configurable via `JWT_REFRESH_TOKEN_EXPIRE_DAYS`)
- **Algorithm**: HS256
- **Claims**: `sub` (user ID), `type` (refresh), `exp`, `iat`

## Security Features

### 1. Token Blacklisting
- Tokens are blacklisted on logout
- Blacklisted tokens are stored in Redis with TTL
- All user tokens can be blacklisted for security events
- Blacklist statistics tracked for monitoring

### 2. Rate Limiting
- **Authentication endpoints**: 5 requests/minute
- **General API endpoints**: 100 requests/minute
- **AI endpoints**: 3-20 requests/minute (tiered)

### 3. Security Headers
All responses include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`

### 4. Token Expiry Warnings
When tokens are near expiry (< 5 minutes):
- `X-Token-Expires-In: <seconds>`
- `X-Token-Refresh-Recommended: true`

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```
**Causes**: Missing token, expired token, invalid token, blacklisted token

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```
**Causes**: Valid token but lacks required permissions

### 429 Too Many Requests
```json
{
  "detail": "Too many authentication attempts. Please try again later."
}
```
**Causes**: Rate limit exceeded

## Implementation Details

### Middleware Stack
1. **CORS Middleware** - Handle cross-origin requests
2. **RequestID Middleware** - Track requests
3. **RBAC Middleware** - Role-based access control
4. **Rate Limit Middleware** - Request throttling
5. **JWT Auth Middleware** - Token validation (NEW)
6. **Security Middleware** - Additional security checks

### JWT Middleware Features
- Public path detection (no auth required)
- Critical path enforcement (strict auth)
- Token validation with blacklist checking
- Rate limiting for auth endpoints
- Security event logging
- Token expiry monitoring

### Token Storage
- **Access tokens**: Sent to client, not stored server-side
- **Refresh tokens**: Sent to client, tracked for rotation
- **Blacklisted tokens**: Stored in Redis with TTL
- **Session data**: Stored in Redis for active sessions

## Testing

### Running JWT Tests
```bash
# Run all JWT authentication tests
pytest tests/test_jwt_authentication.py -v

# Run specific test classes
pytest tests/test_jwt_authentication.py::TestJWTTokenGeneration -v
pytest tests/test_jwt_authentication.py::TestTokenBlacklist -v
pytest tests/test_jwt_authentication.py::TestJWTMiddleware -v
pytest tests/test_jwt_authentication.py::TestProtectedRoutes -v
```

### Test Coverage
- Token generation and validation
- Token blacklisting operations
- Protected route access control
- Rate limiting functionality
- Token refresh flow
- Security headers validation

## Configuration

### Environment Variables
```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-minimum-32-characters
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Rate Limiting
AUTH_RATE_LIMIT_PER_MINUTE=5
RATE_LIMIT_PER_MINUTE=100

# Redis (for blacklist)
REDIS_URL=redis://localhost:6379/0
```

### Settings via Doppler
```bash
# Access JWT settings
doppler secrets get JWT_SECRET_KEY --plain
doppler secrets get JWT_ACCESS_TOKEN_EXPIRE_MINUTES --plain
```

## Monitoring & Alerts

### Metrics Tracked
- Authentication attempts (success/failure)
- Token blacklist operations
- Rate limit violations
- Token expiry warnings issued
- Average token lifetime

### Security Alerts
- Multiple failed login attempts
- Suspicious blacklist patterns
- Rate limit violations
- Token reuse after logout

## Best Practices

### For Developers
1. **Never log tokens** - Avoid logging JWT tokens in any form
2. **Use HTTPS** - Always use HTTPS in production
3. **Rotate secrets** - Regularly rotate JWT secret keys
4. **Monitor expiry** - Handle token expiry gracefully in clients
5. **Implement refresh** - Use refresh tokens to maintain sessions

### For API Consumers
1. **Store securely** - Store tokens in secure storage (not localStorage)
2. **Include in headers** - Send as `Authorization: Bearer <token>`
3. **Handle expiry** - Refresh tokens before expiry
4. **Logout properly** - Call logout endpoint to blacklist tokens
5. **Monitor headers** - Check for expiry warning headers

## Troubleshooting

### Common Issues

#### "Authentication required" on protected endpoint
- Ensure token is included in Authorization header
- Check token hasn't expired
- Verify token isn't blacklisted

#### "Invalid or expired token"
- Token may be expired (check `exp` claim)
- Token may be malformed
- Wrong secret key or algorithm

#### "Too many authentication attempts"
- Rate limit exceeded
- Wait before retrying
- Check for automated retry loops

## Migration Guide

### For Existing Endpoints
Endpoints are automatically protected based on path patterns. No code changes required for:
- Existing user endpoints
- Admin endpoints
- Export endpoints
- AI service endpoints

### For New Endpoints
New endpoints under protected path patterns are automatically secured. For custom protection:
```python
from api.dependencies.auth import get_current_active_user

@router.get("/custom-endpoint")
async def custom_endpoint(user: User = Depends(get_current_active_user)):
    # Endpoint logic here
    pass
```

## Security Compliance

### Standards Met
- **OWASP Top 10** - Protection against common vulnerabilities
- **GDPR** - Token-based authentication supports user privacy
- **UK Data Protection** - Secure authentication for UK businesses
- **PCI DSS** - Secure token handling for payment endpoints

### Security Features
- ✅ Token expiration
- ✅ Token blacklisting
- ✅ Rate limiting
- ✅ Secure algorithms (HS256/RS256)
- ✅ Security headers
- ✅ Audit logging
- ✅ Session management
- ✅ Multi-factor authentication ready

## Support

For issues or questions about JWT authentication:
1. Check the error response details
2. Review this documentation
3. Check test examples in `tests/test_jwt_authentication.py`
4. Contact the security team for sensitive issues