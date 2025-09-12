# SEC-005: Complete JWT Coverage Extension Handoff

## Task Overview
**Priority**: P2.1 (Critical Path)
**Time Allocation**: 12 hours
**Dependencies**: None (can start immediately)
**Owner**: Backend Specialist Agent

## Current State
- 40% of API routes have JWT v2 middleware (from SEC-001 fix)
- Remaining 60% routes are unprotected or using legacy auth
- Feature flag system available for gradual rollout

## Objective
Extend JWT authentication middleware to cover 100% of API routes requiring authentication.

## Implementation Plan

### Phase 1: Route Inventory (2 hours)
1. Scan all routes in `api/routers/`
2. Identify routes missing JWT middleware
3. Categorize by priority:
   - Critical: User data, admin functions
   - High: Business logic, assessments
   - Medium: Reports, analytics
   - Low: Public endpoints (keep unauthenticated)

### Phase 2: Middleware Application (6 hours)
1. Apply JWT middleware systematically:
   ```python
   from middleware.jwt_auth_v2 import JWTMiddleware
   
   @router.get("/protected-route")
   @JWTMiddleware.require_auth
   async def protected_endpoint(user: CurrentUser = Depends(get_current_user)):
       # Route logic
   ```

2. Routes to update:
   - `/api/v1/assessments/*` - All assessment endpoints
   - `/api/v1/compliance/*` - Compliance checking
   - `/api/v1/evidence/*` - Evidence management
   - `/api/v1/policies/*` - Policy management
   - `/api/v1/admin/*` - Admin functions
   - `/api/v1/reports/*` - Report generation

### Phase 3: Testing (3 hours)
1. Run integration tests for each protected route
2. Verify token validation
3. Test unauthorized access returns 401
4. Test token expiration handling
5. Verify refresh token flow

### Phase 4: Feature Flag Rollout (1 hour)
1. Create feature flag: `jwt_full_coverage`
2. Implement gradual rollout:
   - 10% initial deployment
   - Monitor for 30 minutes
   - 50% if no issues
   - 100% after validation

## Files to Modify
- `api/routers/assessments.py`
- `api/routers/compliance.py`
- `api/routers/evidence.py`
- `api/routers/policies.py`
- `api/routers/admin/*.py`
- `api/routers/reports.py`
- `tests/integration/test_jwt_coverage.py`

## Success Criteria
- [ ] 100% of non-public routes have JWT middleware
- [ ] All integration tests pass
- [ ] No authentication bypass vulnerabilities
- [ ] Feature flag controls rollout
- [ ] Performance impact < 10ms per request
- [ ] Monitoring shows successful auth rate > 99%

## Rollback Plan
If issues detected:
1. Disable feature flag immediately
2. Routes revert to previous auth state
3. Investigation and fix
4. Re-attempt with updated approach

## Monitoring
Track via Prometheus/Grafana:
- Authentication success rate
- Token validation latency
- Failed auth attempts
- Route coverage percentage

## Agent Instructions
1. Start by reading current JWT middleware implementation
2. Scan all routes for coverage gaps
3. Apply middleware systematically
4. Test each change incrementally
5. Use feature flags for safe deployment
6. Report progress to orchestrator