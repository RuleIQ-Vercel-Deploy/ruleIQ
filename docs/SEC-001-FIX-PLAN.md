# SEC-001: Authentication Middleware Bypass - Critical Fix Plan

## Problem Statement
The authentication middleware can be bypassed, creating a critical security vulnerability that blocks 14 dependent tasks.

## Root Cause
The middleware is not properly validating JWT tokens and has bypass conditions that can be exploited.

## Fix Implementation (4 hours)

### Hour 1: Analysis & Testing
```python
# 1. Identify the bypass in api/middleware/auth.py
# Current vulnerable code likely has:
if not request.path.startswith('/api/protected'):
    return None  # VULNERABILITY: Skip auth

# 2. Write failing test to demonstrate bypass
def test_auth_middleware_bypass():
    response = client.get('/api/users/profile', headers={})
    assert response.status_code == 401  # Should fail without auth
```

### Hour 2: Implement Fix
```python
# Fixed middleware pattern
from functools import wraps
from flask import request, jsonify
import jwt

EXEMPT_PATHS = ['/api/auth/login', '/api/auth/register', '/api/health']

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if path is explicitly exempt
        if request.path in EXEMPT_PATHS:
            return f(*args, **kwargs)
        
        # All other paths require authentication
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function
```

### Hour 3: Integration Testing
```python
# Comprehensive test suite
class TestAuthMiddleware:
    def test_protected_routes_require_auth(self):
        """Ensure all protected routes enforce authentication"""
        protected_routes = [
            '/api/users/profile',
            '/api/assessments/create',
            '/api/policies/generate',
            '/api/evidence/upload'
        ]
        for route in protected_routes:
            response = client.get(route)
            assert response.status_code == 401
    
    def test_exempt_routes_accessible(self):
        """Ensure public routes remain accessible"""
        public_routes = ['/api/health', '/api/auth/login']
        for route in public_routes:
            response = client.get(route)
            assert response.status_code != 401
```

### Hour 4: Deployment & Verification
1. Deploy to staging environment
2. Run full regression test suite
3. Verify no existing functionality broken
4. Update documentation
5. Notify team of unblocking

## Validation Checklist
- [ ] All protected routes return 401 without valid JWT
- [ ] Valid JWT tokens work correctly
- [ ] Exempt routes remain accessible
- [ ] No regression in existing authenticated flows
- [ ] Performance impact < 10ms per request
- [ ] Error messages don't leak sensitive information

## Rollback Plan
If issues discovered post-deployment:
1. Revert to previous middleware version
2. Add feature flag: `AUTH_MIDDLEWARE_V2_ENABLED`
3. Gradual rollout with monitoring

## Success Metrics
- 0 authentication bypasses in security scan
- 100% of protected endpoints requiring auth
- No increase in false positive auth failures
- Unblocks 14 dependent tasks (94 hours of work)