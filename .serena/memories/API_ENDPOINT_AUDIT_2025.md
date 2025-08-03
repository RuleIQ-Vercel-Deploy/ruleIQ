# API Endpoint Audit - Frontend vs Backend Mapping

## AUDIT METHODOLOGY
1. Extract all backend router prefixes from main.py
2. Extract all frontend API calls from service files
3. Map expected vs actual endpoints
4. Identify mismatches and fix them

## BACKEND ROUTER CONFIGURATION (main.py)

```python
# ✅ CORRECT - Using /api/v1 prefix
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(google_auth.router, prefix="/api/v1/auth", tags=["Google OAuth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(business_profiles.router, prefix="/api/v1/business-profiles", tags=["Business Profiles"])

# ❌ INCONSISTENT - Missing /v1 prefix
app.include_router(assessments.router, prefix="/api/assessments", tags=["Assessments"])
app.include_router(ai_assessments.router, prefix="/api", tags=["AI Assessment Assistant"])
app.include_router(ai_optimization.router, prefix="/api/ai", tags=["AI Optimization"])
app.include_router(frameworks.router, prefix="/api/frameworks", tags=["Compliance Frameworks"])
app.include_router(policies.router, prefix="/api/policies", tags=["Policies"])
app.include_router(implementation.router, prefix="/api/implementation", tags=["Implementation Plans"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["Evidence"])
app.include_router(evidence_collection.router, prefix="/api", tags=["Evidence Collection"])
app.include_router(compliance.router, prefix="/api/compliance", tags=["Compliance Status"])
app.include_router(readiness.router, prefix="/api/readiness", tags=["Readiness Assessment"])
app.include_router(reporting.router, prefix="/api/reports", tags=["Reports"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(foundation_evidence.router, prefix="/api", tags=["Foundation Evidence Collection"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Monitoring"])
app.include_router(security.router, prefix="/api/security", tags=["Security"])
app.include_router(chat.router, prefix="/api", tags=["AI Assistant"])
app.include_router(ai_cost_monitoring.router, prefix="/api/ai/cost", tags=["AI Cost Monitoring"])
app.include_router(ai_cost_websocket.router, prefix="/api/ai/cost", tags=["AI Cost WebSocket"])
app.include_router(ai_policy.router, prefix="/api/ai/policies", tags=["AI Policy Generation"])
app.include_router(performance_monitoring.router, prefix="/api/performance", tags=["Performance Monitoring"])
app.include_router(uk_compliance.router, prefix="/api/uk-compliance", tags=["UK Compliance"])
```

## FRONTEND API CLIENT PATTERN

The frontend API client in `frontend/lib/api/client.ts`:
- Base URL: `http://localhost:8000` (from NEXT_PUBLIC_API_URL)
- Endpoint construction: `${API_BASE_URL}${endpoint}`
- Example: `/business-profiles` becomes `http://localhost:8000/business-profiles`

## CRITICAL FINDINGS

### 🚨 MAJOR INCONSISTENCY DETECTED
The backend has mixed prefixes:
- Some routes use `/api/v1/` (auth, users, business-profiles)
- Most routes use `/api/` (assessments, frameworks, policies, etc.)
- Some routes use `/api/` with no additional prefix (ai_assessments, evidence_collection, etc.)

### 🎯 STANDARDIZATION REQUIRED
We need to decide on ONE consistent pattern:

**Option A: All routes use `/api/v1/` prefix**
- Pro: Versioned API, future-proof
- Con: Requires updating many routes

**Option B: All routes use `/api/` prefix**
- Pro: Simpler, matches current majority
- Con: No versioning

**Option C: Mixed approach (current)**
- Pro: No changes needed
- Con: Inconsistent, confusing, error-prone

## RECOMMENDED SOLUTION

**Standardize on `/api/v1/` for all routes** for these reasons:
1. Future-proof API versioning
2. Industry standard practice
3. Clear separation from other API versions
4. Consistent with auth and user endpoints (most critical)

## NEXT STEPS

1. Update all backend router prefixes to use `/api/v1/`
2. Verify frontend API calls expect `/api/v1/` pattern
3. Test all endpoints after changes
4. Update API documentation

## IMMEDIATE FIXES NEEDED

The following routers need prefix updates in main.py:
- assessments: `/api/assessments` → `/api/v1/assessments`
- frameworks: `/api/frameworks` → `/api/v1/frameworks`
- policies: `/api/policies` → `/api/v1/policies`
- implementation: `/api/implementation` → `/api/v1/implementation`
- evidence: `/api/evidence` → `/api/v1/evidence`
- compliance: `/api/compliance` → `/api/v1/compliance`
- readiness: `/api/readiness` → `/api/v1/readiness`
- reporting: `/api/reports` → `/api/v1/reports`
- integrations: `/api/integrations` → `/api/v1/integrations`
- monitoring: `/api/monitoring` → `/api/v1/monitoring`
- security: `/api/security` → `/api/v1/security`
- performance_monitoring: `/api/performance` → `/api/v1/performance`
- uk_compliance: `/api/uk-compliance` → `/api/v1/uk-compliance`

Special cases (need individual analysis):
- ai_assessments: `/api` → `/api/v1/ai-assessments`
- evidence_collection: `/api` → `/api/v1/evidence-collection`
- foundation_evidence: `/api` → `/api/v1/foundation-evidence`
- chat: `/api` → `/api/v1/chat`
- ai_optimization: `/api/ai` → `/api/v1/ai/optimization`
- ai_cost_monitoring: `/api/ai/cost` → `/api/v1/ai/cost`
- ai_policy: `/api/ai/policies` → `/api/v1/ai/policies`