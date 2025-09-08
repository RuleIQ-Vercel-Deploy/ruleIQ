# JWT Authentication Environment Configuration

**Status**: ✅ Stack Auth Removed - JWT Only  
**Updated**: 2025-08-01  
**Migration**: Complete

## Overview

ruleIQ now uses **JWT-only authentication** after successful removal of Stack Auth. This document outlines the required environment variables and configuration for the JWT authentication system.

## Backend Environment Variables

### Required JWT Configuration

```bash
# JWT Authentication
JWT_SECRET_KEY=your-super-secure-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Database (Required for user storage)
DATABASE_URL=postgresql://user:password@host:port/database

# Redis (Required for token blacklisting)
REDIS_URL=redis://localhost:6379/0
```

### Optional Security Configuration

```bash
# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
MAX_CONCURRENT_REQUESTS=10

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Environment
ENVIRONMENT=production
DEBUG=false
```

## Frontend Environment Variables

### Required JWT Configuration

```bash
# API Connection
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000

# JWT Configuration
NEXT_PUBLIC_AUTH_DOMAIN=localhost
NEXT_PUBLIC_JWT_EXPIRES_IN=1800

# Environment
NEXT_PUBLIC_ENV=production
```

### Optional Frontend Configuration

```bash
# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_SENTRY=false
NEXT_PUBLIC_ENABLE_MOCK_DATA=false

# Analytics
NEXT_PUBLIC_VERCEL_ANALYTICS_ID=your-analytics-id
```

## JWT Secret Key Generation

**CRITICAL**: Generate a secure JWT secret key for production:

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use the provided script
python generate_jwt_secret.py
```

## Authentication Flow

### 1. User Registration
```
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "User Name"
}

Response:
{
  "user": { "id": "...", "email": "...", "is_active": true },
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer"
  }
}
```

### 2. User Login
```
POST /api/v1/auth/login
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

### 3. Protected Endpoint Access
```
GET /api/v1/auth/me
Headers: {
  "Authorization": "Bearer eyJ..."
}

Response:
{
  "id": "user-uuid",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2025-08-01T12:00:00Z"
}
```

### 4. Token Refresh
```
POST /api/v1/auth/refresh
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
```
POST /api/v1/auth/logout
Headers: {
  "Authorization": "Bearer eyJ..."
}

Response:
{
  "message": "Successfully logged out"
}
```

## Security Features

### Token Security
- **Access Token Expiry**: 30 minutes (configurable)
- **Refresh Token Expiry**: 7 days (configurable)
- **Token Blacklisting**: Logout invalidates tokens
- **Secure Algorithm**: HS256 with strong secret

### Password Security
- **Minimum Length**: 12 characters
- **Complexity**: Must include uppercase, lowercase, numbers, special chars
- **Hashing**: bcrypt with salt rounds
- **Timing Attack Protection**: Constant-time comparison

### Rate Limiting
- **Authentication Endpoints**: 5 requests/minute
- **General Endpoints**: 100 requests/minute
- **AI Endpoints**: 20 requests/minute

## Database Requirements

### User Table Schema
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Redis Requirements
- **Token Blacklist**: Stores invalidated tokens
- **Session Management**: Tracks active sessions
- **Rate Limiting**: Stores request counts

## Migration from Stack Auth

### ✅ Completed Steps
1. **Backend Migration**: All routers updated to use JWT
2. **Frontend Migration**: Auth store and API clients updated
3. **Dependency Removal**: Stack Auth packages removed
4. **Environment Cleanup**: Stack Auth variables removed
5. **Testing**: Authentication flow verified

### 🗑️ Removed Stack Auth Variables
```bash
# These variables are NO LONGER NEEDED:
# STACK_PROJECT_ID
# STACK_PUBLISHABLE_CLIENT_KEY
# STACK_SECRET_SERVER_KEY
# STACK_INTERNAL_PROJECT_KEYS
# NEXT_PUBLIC_STACK_PROJECT_ID
# NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY
```

## Production Deployment Checklist

### Backend
- [ ] Set strong `JWT_SECRET_KEY`
- [ ] Configure production `DATABASE_URL`
- [ ] Set up Redis for token blacklisting
- [ ] Enable rate limiting
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure CORS origins
- [ ] Set up SSL/TLS

### Frontend
- [ ] Set production `NEXT_PUBLIC_API_URL`
- [ ] Configure `NEXT_PUBLIC_AUTH_DOMAIN`
- [ ] Set `NEXT_PUBLIC_ENV=production`
- [ ] Disable debug features
- [ ] Configure analytics (optional)

### Security
- [ ] Use HTTPS in production
- [ ] Secure JWT secret storage
- [ ] Configure proper CORS
- [ ] Enable security headers
- [ ] Set up monitoring

## Troubleshooting

### Common Issues

**401 Unauthorized on protected endpoints**
- Check if token is included in Authorization header
- Verify token format: `Bearer <token>`
- Ensure token hasn't expired
- Check if user is active

**Token refresh fails**
- Verify refresh token is valid
- Check if refresh token has expired
- Ensure user account is still active

**Login fails with correct credentials**
- Check password complexity requirements
- Verify user account is active
- Check rate limiting status

### Debug Commands

```bash
# Test authentication endpoints
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPassword123!"}'

# Test protected endpoint
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Check API health
curl http://localhost:8000/health
```

## Support

For authentication issues:
1. Check this documentation
2. Verify environment variables
3. Test with provided curl commands
4. Check application logs
5. Contact development team

---

**Migration Status**: ✅ Complete  
**Authentication System**: JWT Only  
**Stack Auth**: ❌ Removed  
**Production Ready**: ✅ Yes