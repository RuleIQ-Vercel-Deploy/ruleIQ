# 2. SECURITY ARCHITECTURE

## 2.1 Authentication & Authorization

### CRITICAL FIX REQUIRED
```typescript
// Current middleware.ts LINE 11 - BYPASSES ALL AUTH
export function middleware(request: NextRequest) {
  return NextResponse.next(); // REMOVE THIS - SECURITY VULNERABILITY
}
```

### Correct Implementation
```typescript
// middleware.ts - SECURE VERSION
export async function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token');
  
  // Public routes that don't require auth
  const publicRoutes = ['/login', '/register', '/reset-password', '/api/auth/*'];
  const isPublicRoute = publicRoutes.some(route => 
    request.nextUrl.pathname.startsWith(route)
  );
  
  if (isPublicRoute) {
    return NextResponse.next();
  }
  
  // Validate JWT token
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  try {
    const payload = await verifyJWT(token.value);
    
    // Add user context to headers
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set('x-user-id', payload.userId);
    requestHeaders.set('x-user-role', payload.role);
    
    return NextResponse.next({
      request: {
        headers: requestHeaders,
      },
    });
  } catch (error) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
```

## 2.2 Security Layers

```yaml
Authentication:
  Method: JWT with refresh tokens
  Storage: HttpOnly cookies
  Rotation: 15min access / 7day refresh
  MFA: TOTP support ready

Authorization:
  Model: RBAC with permissions
  Roles: Admin, ComplianceOfficer, Auditor, User
  Middleware: Role-based route protection
  API: Permission decorators

Rate Limiting:
  Global: 1000 req/min per IP
  Auth: 5 attempts per 15min
  AI: 100 requests per hour
  Upload: 10 files per minute

CORS:
  Origins: Whitelist production domains
  Credentials: Include for auth cookies
  Headers: Strict allowed headers

Input Validation:
  Frontend: Zod schemas
  Backend: Pydantic models
  SQL: Parameterized queries only
  Files: Type/size validation

Secrets Management:
  Provider: Doppler
  Rotation: Automated 90-day
  Access: Environment-based
  Audit: Full access logs
```

---
