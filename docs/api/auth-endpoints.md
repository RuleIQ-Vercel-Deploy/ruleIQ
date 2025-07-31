# Authentication Endpoints Documentation

## Overview

The ruleIQ Authentication API provides secure user authentication and session management using JWT tokens. All API endpoints require authentication via Bearer tokens.

**Base URL**: `http://localhost:8000/api/auth`

## Rate Limiting

Authentication endpoints have strict rate limiting for security:

| Endpoint | Rate Limit | Description |
|----------|------------|-------------|
| Login | 5 req/min | Prevent brute force attacks |
| Register | 5 req/min | Prevent spam registration |
| Token Refresh | 10 req/min | Normal token refresh |
| Logout | 20 req/min | Allow multiple logout attempts |

## Endpoints

### 1. User Login

**POST** `/api/auth/token`

Authenticate a user and receive access tokens.

#### Request Body (Form-encoded)

```
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=your_password
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
  "detail": "Incorrect email or password"
}
```

#### Response (Rate Limited - 429)

```json
{
  "detail": "Too many login attempts. Please try again later."
}
```

### 2. User Registration

**POST** `/api/auth/register`

Register a new user account.

#### Request Body

```json
{
  "email": "user@example.com",
  "password": "secure_password_123",
  "full_name": "John Doe",
  "company_name": "Acme Corp",
  "role": "admin"
}
```

#### Response (Success - 201)

```json
{
  "message": "User registered successfully",
  "user_id": "user_12345"
}
```

#### Response (Error - 400)

```json
{
  "detail": "Email already registered"
}
```

### 3. Token Refresh

**POST** `/api/auth/refresh`

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

### 4. User Logout

**POST** `/api/auth/logout`

Invalidate the current user session and tokens.

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

### 5. Get Current User

**GET** `/api/auth/me`

Retrieve information about the currently authenticated user.

#### Headers

```
Authorization: Bearer <your_access_token>
```

#### Response (Success - 200)

```json
{
  "id": "user_12345",
  "email": "user@example.com",
  "full_name": "John Doe",
  "company_name": "Acme Corp",
  "role": "admin",
  "created_at": "2025-01-15T10:30:00Z",
  "last_login": "2025-01-15T14:22:00Z"
}
```

## Authentication Flow

### Standard Login Flow

1. **POST** `/api/auth/token` with credentials
2. Store `access_token` and `refresh_token` securely
3. Include `Authorization: Bearer <access_token>` in all API requests
4. When access token expires (8 hours), use refresh token to get new tokens
5. If refresh token expires, redirect user to login

### Token Lifecycle

- **Access Token**: Valid for 8 hours
- **Refresh Token**: Valid for 30 days
- **Auto-refresh**: Frontend automatically refreshes tokens before expiration

## Error Handling

All authentication endpoints return consistent error formats:

```json
{
  "detail": "Human-readable error message",
  "error_code": "AUTH_ERROR_CODE",
  "timestamp": "2025-01-15T14:22:00Z"
}
```

### Common Error Codes

- `INVALID_CREDENTIALS`: Wrong email/password
- `TOKEN_EXPIRED`: Access token has expired
- `TOKEN_INVALID`: Malformed or invalid token
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `USER_NOT_FOUND`: User account doesn't exist
- `EMAIL_ALREADY_EXISTS`: Registration with existing email

## Security Features

- **JWT Tokens**: Secure token-based authentication
- **Rate Limiting**: Prevent brute force attacks
- **Token Rotation**: Refresh tokens are rotated on use
- **Session Tracking**: Server-side session management
- **Secure Storage**: Tokens stored with encryption

## Frontend Integration

### Environment Configuration

```typescript
// .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### API Client Setup

```typescript
// lib/api/client.ts
const client = axios.create({
  baseURL: `${env.NEXT_PUBLIC_API_URL}/api`,
  timeout: 30000,
});
```

### Authentication Service

```typescript
// lib/api/auth.service.ts
const login = async (email: string, password: string) => {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);
  
  const response = await axios.post(
    `${env.NEXT_PUBLIC_API_URL}/api/auth/token`, 
    formData,
    {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }
  );
  
  return response.data;
};
```

## Testing

### cURL Examples

**Login:**
```bash
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=your_password"
```

**Get Current User:**
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer <your_access_token>"
```

**Refresh Token:**
```bash
curl -X POST "http://localhost:8000/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your_refresh_token"}'
```

---

*Last Updated: 2025-07-29*  
*API Version: 2.0*