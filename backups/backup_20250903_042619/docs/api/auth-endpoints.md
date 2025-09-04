# Authentication Endpoints Documentation

## Overview

The ruleIQ Authentication API provides secure JWT-based authentication and session management. **Stack Auth has been completely removed** as of August 2025. All authentication now uses JWT tokens with secure token refresh mechanisms.

**Base URL**: `http://localhost:8000/api/v1/auth`

## Authentication System Status

- ✅ **JWT-Only Authentication**: Complete implementation
- ❌ **Stack Auth**: Removed (August 2025)
- ✅ **Token Security**: HS256 algorithm with secure secrets
- ✅ **Session Management**: Redis-based token blacklisting
- ✅ **Rate Limiting**: Multi-tier protection

## Rate Limiting

Authentication endpoints have strict rate limiting for security:

| Endpoint | Rate Limit | Description |
|----------|------------|-------------|
| Login | 5 req/min | Prevent brute force attacks |
| Register | 5 req/min | Prevent spam registration |
| Token Refresh | 10 req/min | Normal token refresh |
| Logout | 20 req/min | Allow multiple logout attempts |
| Get User | 100 req/min | Normal API usage |

## Endpoints

### 1. User Registration

**POST** `/api/v1/auth/register`

Register a new user account and receive authentication tokens.

#### Request Body

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

#### Password Requirements
- Minimum 12 characters
- Must include uppercase, lowercase, numbers, and special characters
- Cannot be a common password

#### Response (Success - 201)

```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2025-08-01T12:00:00Z"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

#### Response (Error - 409)

```json
{
  "detail": "Email already exists"
}
```

#### Response (Error - 422)

```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must be at least 12 characters long",
      "type": "value_error"
    }
  ]
}
```

### 2. User Login

**POST** `/api/v1/auth/login`

Authenticate a user and receive access tokens.

#### Request Body

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

#### Response (Success - 200)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Response (Error - 401)

```json
{
  "detail": "Invalid credentials"
}
```

#### Response (Rate Limited - 429)

```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

### 3. Get Current User

**GET** `/api/v1/auth/me`

Retrieve information about the currently authenticated user.

#### Headers

```
Authorization: Bearer <your_access_token>
```

#### Response (Success - 200)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-08-01T12:00:00Z"
}
```

#### Response (Error - 401)

```json
{
  "detail": "Could not validate credentials"
}
```

### 4. Token Refresh

**POST** `/api/v1/auth/refresh`

Refresh an expired access token using a refresh token.

#### Request Body

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Response (Success - 200)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Response (Error - 401)

```json
{
  "detail": "Invalid refresh token"
}
```

### 5. User Logout

**POST** `/api/v1/auth/logout`

Invalidate the current user session and blacklist tokens.

#### Headers

```
Authorization: Bearer <your_access_token>
```

#### Response (Success - 200)

```json
{
  "message": "Successfully logged out"
}
```

#### Response (Error - 401)

```json
{
  "detail": "Could not validate credentials"
}
```

## Authentication Flow

### Complete User Journey

1. **Registration**: `POST /api/v1/auth/register` with user details
2. **Token Storage**: Store `access_token` and `refresh_token` securely
3. **API Requests**: Include `Authorization: Bearer <access_token>` in headers
4. **Token Refresh**: Use refresh token when access token expires (30 minutes)
5. **Logout**: `POST /api/v1/auth/logout` to invalidate tokens

### Token Lifecycle

- **Access Token**: Valid for 30 minutes
- **Refresh Token**: Valid for 7 days
- **Token Blacklisting**: Logout immediately invalidates tokens via Redis
- **Auto-refresh**: Frontend automatically refreshes tokens before expiration

## Security Features

### JWT Token Security
- **Algorithm**: HS256 with secure secret key
- **Payload**: Contains user ID and expiration time only
- **No Sensitive Data**: Passwords and sensitive information never in tokens

### Password Security
- **Hashing**: bcrypt with automatic salt generation
- **Complexity Requirements**: Enforced on registration and password changes
- **Timing Attack Protection**: Constant-time password verification

### Session Management
- **Token Blacklisting**: Redis-based invalidation on logout
- **Concurrent Sessions**: Multiple device support with individual token tracking
- **Session Timeout**: Automatic cleanup of expired tokens

### Rate Limiting
- **Authentication Endpoints**: 5 requests/minute per IP
- **General API**: 100 requests/minute per IP
- **AI Endpoints**: 20 requests/minute per user

## Error Handling

All authentication endpoints return consistent error formats:

```json
{
  "detail": "Human-readable error message",
  "timestamp": "2025-08-01T12:00:00Z"
}
```

### Common Error Scenarios

| Status Code | Error | Description |
|-------------|-------|-------------|
| 401 | `Invalid credentials` | Wrong email/password combination |
| 401 | `Could not validate credentials` | Invalid or expired access token |
| 401 | `Invalid refresh token` | Refresh token expired or invalid |
| 409 | `Email already exists` | Registration with existing email |
| 422 | `Validation Error` | Invalid input format or missing fields |
| 429 | `Rate limit exceeded` | Too many requests from IP |

## Frontend Integration

### Environment Configuration

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_JWT_EXPIRES_IN=1800
NEXT_PUBLIC_AUTH_DOMAIN=localhost
```

### Authentication Store (Zustand)

```typescript
// lib/stores/auth.store.ts
interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  checkAuthStatus: () => Promise<void>;
}
```

### API Client with JWT

```typescript
// lib/api/client.ts
class APIClient {
  private async getAuthHeaders(): Promise<HeadersInit> {
    const { tokens, refreshToken } = useAuthStore.getState();
    
    if (!tokens?.access_token) {
      throw new APIError('No authentication token available', 401);
    }
    
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${tokens.access_token}`,
    };
  }
}
```

### Route Protection

```typescript
// app/(dashboard)/layout.tsx
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, checkAuthStatus } = useAuthStore();

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  if (!isAuthenticated) {
    redirect('/login');
  }

  return <SidebarProvider>{children}</SidebarProvider>;
}
```

## Testing

### Manual Testing with cURL

**Register a new user:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

**Get current user:**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Refresh token:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

**Logout:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Automated Testing

```bash
# Run authentication tests
pytest tests/security/test_authentication.py -v

# Run integration tests
pytest tests/integration/test_jwt_auth_integration.py -v

# Run all auth-related tests
pytest -k "auth" -v
```

## Migration Notes

### From Stack Auth (Completed August 2025)

**What was removed:**
- `@stackframe/stack` package dependency
- Stack Auth middleware and dependencies
- Stack Auth environment variables
- Stack Auth API endpoints

**What was added:**
- Complete JWT authentication system
- Token refresh mechanism
- Redis-based token blacklisting
- Enhanced security features

**Migration impact:**
- All existing users need to re-register (one-time migration)
- Frontend authentication flows updated
- API client authentication updated
- Environment variables updated

## Production Deployment

### Environment Variables

```bash
# Required for JWT authentication
JWT_SECRET_KEY=your-super-secure-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Database for user storage
DATABASE_URL=postgresql://user:password@host:port/database

# Redis for token blacklisting
REDIS_URL=redis://localhost:6379/0

# Security
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### Security Checklist

- [ ] Generate strong JWT secret key (32+ characters)
- [ ] Configure HTTPS for all communications
- [ ] Set proper CORS origins
- [ ] Enable rate limiting
- [ ] Configure Redis for token blacklisting
- [ ] Set up monitoring and logging
- [ ] Regular security audits

---

**Last Updated**: August 1, 2025  
**API Version**: 2.0  
**Authentication System**: JWT-Only (Stack Auth Removed)  
**Status**: Production Ready