# Frontend API Client Guide

**Updated**: 2025-08-15  
**Version**: 2.0.0

## 🎯 Overview

The ruleIQ frontend API client provides a unified interface for all backend communications with automatic endpoint versioning, error handling, and type safety.

## 📍 Location

**Primary Client**: `frontend/lib/api/client.ts`

## ✨ Key Features

### 1. Automatic Endpoint Versioning

The API client automatically adds `/api/v1` prefix to endpoints that don't already include it:

```typescript
// You write:
apiClient.get('/business-profiles')

// Client sends:
GET http://localhost:8000/api/v1/business-profiles
```

### 2. Pass-Through for Versioned Endpoints

Endpoints already containing `/api` are passed through unchanged:

```typescript
// You write:
apiClient.post('/api/v1/auth/login', credentials)

// Client sends:
POST http://localhost:8000/api/v1/auth/login
```

## 🔧 Implementation Details

### Core Request Method

```typescript
private async request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  // Automatic versioning logic
  const normalizedEndpoint = endpoint.startsWith('/api') 
    ? endpoint 
    : `/api/v1${endpoint}`;
    
  const url = `${API_BASE_URL}${normalizedEndpoint}`;
  
  // ... rest of request logic
}
```

## 📚 Usage Examples

### Service Implementation

```typescript
// frontend/lib/api/business-profiles.service.ts

import { apiClient } from '@/lib/api/client';

export const businessProfileService = {
  // Clean endpoint - client adds /api/v1
  async getAll() {
    return apiClient.get('/business-profiles');
  },

  // Clean endpoint - client adds /api/v1
  async create(data: CreateBusinessProfileDto) {
    return apiClient.post('/business-profiles', data);
  },

  // Clean endpoint with parameter - client adds /api/v1
  async getById(id: string) {
    return apiClient.get(`/business-profiles/${id}`);
  },

  // Clean endpoint - client adds /api/v1
  async update(id: string, data: UpdateBusinessProfileDto) {
    return apiClient.put(`/business-profiles/${id}`, data);
  },

  // Clean endpoint - client adds /api/v1
  async delete(id: string) {
    return apiClient.delete(`/business-profiles/${id}`);
  }
};
```

### Authentication Service

```typescript
// frontend/lib/api/auth.service.ts

export const authService = {
  // Already versioned - passes through unchanged
  async login(credentials: LoginDto) {
    return apiClient.post('/api/v1/auth/login', credentials);
  },

  // Already versioned - passes through unchanged
  async signup(data: SignupDto) {
    return apiClient.post('/api/v1/auth/signup', data);
  },

  // Already versioned - passes through unchanged
  async getCurrentUser() {
    return apiClient.get('/api/v1/users/me');
  }
};
```

## 🔄 Migration Guide

### From Legacy Endpoints

If you have services using legacy patterns, update them:

```typescript
// ❌ OLD - Don't do this
apiClient.get('/api/assessments')

// ✅ NEW - Do this instead
apiClient.get('/assessments')  // Client adds /api/v1 automatically
```

### Exception: Auth Endpoints

Auth endpoints should keep their full paths for clarity:

```typescript
// ✅ Keep auth endpoints explicit
apiClient.post('/api/v1/auth/login', data)
```

## 🎯 Best Practices

### 1. Use Clean Endpoints

For non-auth endpoints, use clean paths without version:

```typescript
// ✅ Good
apiClient.get('/frameworks')
apiClient.post('/policies')
apiClient.get('/evidence')

// ❌ Avoid (unless auth)
apiClient.get('/api/v1/frameworks')
```

### 2. Consistent Service Pattern

Structure all services consistently:

```typescript
export const myService = {
  async getAll() {
    return apiClient.get('/my-resource');
  },
  
  async getById(id: string) {
    return apiClient.get(`/my-resource/${id}`);
  },
  
  async create(data: CreateDto) {
    return apiClient.post('/my-resource', data);
  },
  
  async update(id: string, data: UpdateDto) {
    return apiClient.put(`/my-resource/${id}`, data);
  },
  
  async delete(id: string) {
    return apiClient.delete(`/my-resource/${id}`);
  }
};
```

### 3. Type Safety

Always use TypeScript interfaces for request/response:

```typescript
interface BusinessProfile {
  id: string;
  company_name: string;
  // ... other fields
}

interface CreateBusinessProfileDto {
  company_name: string;
  // ... other fields
}

// Type-safe service methods
async getAll(): Promise<BusinessProfile[]> {
  return apiClient.get<BusinessProfile[]>('/business-profiles');
}

async create(data: CreateBusinessProfileDto): Promise<BusinessProfile> {
  return apiClient.post<BusinessProfile>('/business-profiles', data);
}
```

## 🔍 How It Works

### Request Flow

1. **Service calls client** with clean endpoint
2. **Client checks** if endpoint starts with `/api`
3. **If NO**: Prepends `/api/v1` to the endpoint
4. **If YES**: Uses endpoint as-is
5. **Constructs full URL** with base URL
6. **Sends request** with auth headers
7. **Handles response** with error checking

### Example Flow

```
Service: apiClient.get('/assessments')
         ↓
Client: endpoint = '/assessments'
        ↓
Check: Does NOT start with '/api'
       ↓
Transform: '/api/v1/assessments'
          ↓
Full URL: 'http://localhost:8000/api/v1/assessments'
         ↓
Request: GET with Authorization header
```

## 🛠️ Configuration

### Environment Variables

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Client Configuration

```typescript
// frontend/lib/api/client.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  // ... implementation
}

export const apiClient = new APIClient();
```

## 🐛 Troubleshooting

### Common Issues

#### 404 Not Found Errors

**Problem**: Getting "APIError: Not Found" 

**Solution**: Ensure you're using clean endpoints:
```typescript
// ❌ Wrong
apiClient.get('/api/business-profiles')  // Results in /api/v1/api/business-profiles

// ✅ Correct
apiClient.get('/business-profiles')  // Results in /api/v1/business-profiles
```

#### Authentication Failures

**Problem**: 401 Unauthorized errors

**Solution**: Ensure token is being included:
```typescript
// Check token exists
const token = localStorage.getItem('access_token');
if (!token) {
  // Redirect to login
}
```

#### CORS Errors

**Problem**: CORS policy blocking requests

**Solution**: Ensure backend allows frontend origin:
```python
# backend main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    # ... other settings
)
```

## 📊 Endpoint Reference

### Pattern Mapping

| Service Call | Actual Request |
|--------------|----------------|
| `/business-profiles` | `/api/v1/business-profiles` |
| `/assessments` | `/api/v1/assessments` |
| `/frameworks` | `/api/v1/frameworks` |
| `/policies` | `/api/v1/policies` |
| `/api/v1/auth/login` | `/api/v1/auth/login` |
| `/api/v1/users/me` | `/api/v1/users/me` |

## 🔒 Security Considerations

1. **Token Storage**: Access tokens stored in localStorage
2. **Token Refresh**: Automatic refresh on 401 responses
3. **Request Signing**: All requests include Authorization header
4. **Error Sanitization**: Sensitive data removed from error logs

## 📈 Performance

- **Request Caching**: TanStack Query handles caching
- **Retry Logic**: Automatic retry on network failures
- **Request Deduplication**: Prevents duplicate concurrent requests
- **Optimistic Updates**: UI updates before server confirmation

## 🔗 Related Documentation

- [API Endpoints Documentation](./API_ENDPOINTS_DOCUMENTATION.md)
- [Frontend Architecture](../frontend/FRONTEND_DESIGN_COMPLIANCE_PLAN.md)
- [Authentication Flow](./AUTHENTICATION_FLOW_DOCUMENTATION.md)

---

*Last Updated: 2025-08-15*  
*Client Version: 2.0.0*  
*API Version: 1.0.0*