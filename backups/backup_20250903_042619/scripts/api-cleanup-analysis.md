# API Cleanup Analysis - ruleIQ

## Current State
- **Total Endpoints**: 99 (all connecting successfully)
- **Status**: 100% connectivity achieved (was 11.4%)
- **Issues Found**: Duplicates, inconsistent naming, redundant routers

## 1. DUPLICATE ROUTERS
### Reports vs Reporting
- **reports.py**: Active, included in main.py
- **reporting.py**: NOT included in main.py, redundant
- **Action**: DELETE reporting.py (duplicate functionality)

## 2. ROUTERS WITH PROBLEMATIC PREFIX DEFINITIONS

### Routers with Double-Prefixing (FIXED)
These routers define prefix in APIRouter() AND get another prefix in main.py:
- ❌ **performance_monitoring.py**: Has `prefix="/performance"` in router + `/api/v1/performance` in main.py
- ❌ **uk_compliance.py**: Has `prefix="/api/v1/compliance"` in router + `/api/v1/uk-compliance` in main.py  
- ❌ **rbac_auth.py**: Has `prefix="/api/v1/auth"` in router + registered without prefix
- ❌ **ai_cost_monitoring.py**: Has `prefix="/api/v1/ai/cost"` in router + same prefix in main.py
- ❌ **ai_cost_websocket.py**: Has `prefix="/api/v1/ai/cost/ws"` in router + `/api/v1/ai/cost-websocket` in main.py
- ❌ **ai_policy.py**: Has `prefix="/policies"` in router + `/api/v1/ai/policies` in main.py
- ❌ **agentic_rag.py**: Has `prefix="/agentic-rag"` in router + `/api/v1` in main.py
- ❌ **google_auth.py**: Has `prefix="/google"` in router + `/api/v1/auth` in main.py

### Clean Routers (No prefix in APIRouter)
These correctly use APIRouter() without prefix:
- ✅ monitoring.py
- ✅ auth.py
- ✅ evidence_collection.py
- ✅ readiness.py
- ✅ frameworks.py
- ✅ assessments.py
- ✅ business_profiles.py
- ✅ reports.py
- ✅ policies.py
- ✅ payment.py
- ✅ integrations.py
- ✅ dashboard.py
- ✅ evidence.py
- ✅ compliance.py
- ✅ users.py
- ✅ foundation_evidence.py
- ✅ ai_optimization.py
- ✅ implementation.py
- ✅ security.py

## 3. COMMENTED OUT / DISABLED ROUTERS
- **agentic_assessments.py**: Commented out in main.py (line 245)
- **Action**: Either DELETE or properly integrate

## 4. NAMING INCONSISTENCIES
### Hyphenated vs Underscore
- Most use hyphens: `business-profiles`, `evidence-collection`, `uk-compliance`
- Some use underscores in code but hyphens in URLs

### Recommendations:
1. Standardize on hyphens for all URL paths
2. Keep underscores in Python file names
3. Maintain consistent mapping

## 5. ENDPOINT DUPLICATES & CONFLICTS

### Chat vs AI Assessments
Both have similar chat/conversation endpoints:
- chat.py: `/api/v1/chat/conversations`
- ai_assessments.py has chat-like functions

### Monitoring vs Performance Monitoring
- monitoring.py: System monitoring, database, health
- performance_monitoring.py: Performance metrics, optimization
- **Keep both**: Different purposes

## CLEANUP ACTIONS

### Phase 1: Remove Duplicates
1. DELETE `api/routers/reporting.py` (replaced by reports.py)
2. DELETE or FIX `api/routers/agentic_assessments.py` (commented out)

### Phase 2: Fix Double-Prefixing
Remove prefix from APIRouter() in these files:
1. performance_monitoring.py
2. uk_compliance.py  
3. rbac_auth.py
4. ai_cost_monitoring.py
5. ai_cost_websocket.py
6. ai_policy.py
7. agentic_rag.py
8. google_auth.py

### Phase 3: Consolidate Similar Endpoints
1. Review chat.py vs ai_assessments.py for overlaps
2. Ensure clear separation of concerns

### Phase 4: Documentation
1. Create API map showing all 99 endpoints
2. Document purpose of each router
3. Create naming convention guide

## FINAL STATE GOAL
- ~95 clean, non-duplicate endpoints
- Consistent naming (all hyphens in URLs)
- No double-prefixing
- Clear separation of concerns
- 100% frontend-backend connectivity maintained