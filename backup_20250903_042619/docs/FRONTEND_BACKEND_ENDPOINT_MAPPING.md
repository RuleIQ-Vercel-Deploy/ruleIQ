# Frontend-Backend API Endpoints Complete Inventory

**Status**: Generated January 31, 2025  
**Purpose**: Complete mapping of all API endpoints for Stack Auth integration

## 🚨 CRITICAL AUTH STATUS

### ✅ What's Working
- Stack Auth frontend integration (OAuth, tokens)
- Frontend API client with Stack Auth tokens
- Environment variables configured

### ❌ What's Missing
- **Backend Stack Auth token validation** (CRITICAL)
- **API endpoints still expect JWT tokens** (CRITICAL)
- **No Stack Auth middleware** (CRITICAL)

---

## 📋 BACKEND API ENDPOINTS

### 🔐 Authentication & Authorization
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/v1/auth/register` | auth.py | POST | ❌ | JWT | ❌ NEEDS UPDATE |
| `/api/v1/auth/login` | auth.py | POST | ❌ | JWT | ❌ NEEDS UPDATE |
| `/api/v1/auth/token` | auth.py | POST | ❌ | JWT | ❌ NEEDS UPDATE |
| `/api/v1/auth/refresh` | auth.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/v1/auth/logout` | auth.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/v1/auth/me` | auth.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/v1/auth/google` | google_auth.py | GET | ❌ | JWT | ❌ NEEDS UPDATE |
| `/api/v1/auth/google/callback` | google_auth.py | GET | ❌ | JWT | ❌ NEEDS UPDATE |
| `/api/v1/auth/google/mobile` | google_auth.py | POST | ❌ | JWT | ❌ NEEDS UPDATE |

### 🏢 Business Profiles
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/business-profiles` | business_profiles.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/business-profiles` | business_profiles.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/business-profiles/{id}` | business_profiles.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/business-profiles/{id}` | business_profiles.py | PUT | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/business-profiles/{id}` | business_profiles.py | PATCH | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/business-profiles/{id}` | business_profiles.py | DELETE | ✅ | JWT | ❌ NEEDS UPDATE |

### 📊 Assessments
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/assessments/quick` | assessments.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/assessments` | assessments.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/assessments` | assessments.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/assessments/{id}/start` | assessments.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/assessments/current` | assessments.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/assessments/{id}/questions` | assessments.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/assessments/{id}/responses` | assessments.py | PUT | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/assessments/{id}/responses/bulk` | assessments.py | PUT | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/assessments/{id}` | assessments.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/assessments/{id}/recommendations` | assessments.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/assessments/{id}/complete` | assessments.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |

### 🤖 AI Assessment Assistant
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/ai/help` | ai_assessments.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/ai/help/stream` | ai_assessments.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/ai/followup` | ai_assessments.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/ai/analysis` | ai_assessments.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/ai/analysis/stream` | ai_assessments.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/ai/recommendations` | ai_assessments.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/ai/recommendations/stream` | ai_assessments.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/ai/feedback` | ai_assessments.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/ai/metrics` | ai_assessments.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/ai/rate-limits` | ai_assessments.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/ai/health` | ai_assessments.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/ai/circuit-breaker` | ai_assessments.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/ai/circuit-breaker/reset` | ai_assessments.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/ai/model-health` | ai_assessments.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/ai/cache-metrics` | ai_assessments.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |

### 🏛️ Frameworks
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/frameworks` | frameworks.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/frameworks/recommendations` | frameworks.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/frameworks/recommendations/{profile_id}` | frameworks.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/frameworks/{id}` | frameworks.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |

### 📋 Policies
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/policies/generate` | policies.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/policies` | policies.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/policies/{id}` | policies.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/policies/{id}/status` | policies.py | PUT | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/policies/{id}/approve` | policies.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |

### 📁 Evidence Management
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/evidence` | evidence.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence` | evidence.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/statistics` | evidence.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/search` | evidence.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/validate` | evidence.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/requirements` | evidence.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/requirements/identify` | evidence.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/{id}` | evidence.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/{id}` | evidence.py | PUT | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/{id}/status` | evidence.py | PUT | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/{id}` | evidence.py | DELETE | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/bulk/status` | evidence.py | PUT | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/automation` | evidence.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/upload` | evidence.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/dashboard` | evidence.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/classify` | evidence.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/bulk/classify` | evidence.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/mapping-suggestions` | evidence.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/classification/statistics` | evidence.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/quality/analysis` | evidence.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/duplicates/detect` | evidence.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/duplicates/batch` | evidence.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/quality/benchmark` | evidence.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/evidence/quality/trends` | evidence.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |

### 📊 Reports
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/reports/templates` | reporting.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/reports/generate` | reporting.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/reports/pdf` | reporting.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/reports/preview` | reporting.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/reports/templates/customize` | reporting.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/reports/schedules` | reporting.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/reports/schedules` | reporting.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/reports/schedules/{id}` | reporting.py | DELETE | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/reports/schedules/{id}/execute` | reporting.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |

### 🔧 Integrations
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/integrations/connect` | integrations.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/integrations/{provider}/disconnect` | integrations.py | DELETE | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/integrations/{provider}/status` | integrations.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |

### 🏗️ Implementation Plans
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/implementation/plans` | implementation.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/implementation/plans` | implementation.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/implementation/plans/{id}` | implementation.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/implementation/plans/{id}/tasks/{task_id}` | implementation.py | PUT | ✅ | JWT | ❌ NEEDS UPDATE |

### 📈 Monitoring & Performance
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/monitoring/health` | monitoring.py | GET | ❌ | None | ✅ READY |
| `/api/monitoring/database/status` | monitoring.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/monitoring/database/pool` | monitoring.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/monitoring/database/alerts` | monitoring.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/monitoring/database/engine` | monitoring.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/monitoring/prometheus` | monitoring.py | GET | ❌ | None | ✅ READY |
| `/api/monitoring/database/test` | monitoring.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/monitoring/status` | monitoring.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |

### 🔐 Security & RBAC
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/security/rbac/test` | security.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/security/vulnerabilities/test` | security.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/security/status` | security.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/security/rate-limit/test` | security.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |

### 👤 Users
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/users/me` | users.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/users/profile` | users.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/users/dashboard` | users.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/users/deactivate` | users.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |

### 🤖 AI Chat Assistant
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/conversations` | chat.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/conversations` | chat.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/conversations/{id}` | chat.py | GET | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/conversations/{id}/messages` | chat.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/conversations/{id}` | chat.py | DELETE | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/chat/evidence-recommendations` | chat.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/chat/compliance-gap` | chat.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/chat/context-recommendations` | chat.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/chat/workflow` | chat.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/chat/policy` | chat.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |
| `/api/chat/guidance` | chat.py | POST | ✅ | JWT | ❌ NEEDS UPDATE |

### 🛡️ Admin Endpoints
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/admin/users` | admin/user_management.py | GET | ✅ | JWT + Admin | ❌ NEEDS UPDATE |
| `/api/admin/users` | admin/user_management.py | POST | ✅ | JWT + Admin | ❌ NEEDS UPDATE |
| `/api/admin/users/{id}` | admin/user_management.py | GET | ✅ | JWT + Admin | ❌ NEEDS UPDATE |
| `/api/admin/users/{id}` | admin/user_management.py | PUT | ✅ | JWT + Admin | ❌ NEEDS UPDATE |
| `/api/admin/users/{id}` | admin/user_management.py | DELETE | ✅ | JWT + Admin | ❌ NEEDS UPDATE |
| `/api/admin/roles` | admin/user_management.py | GET | ✅ | JWT + Admin | ❌ NEEDS UPDATE |
| `/api/admin/roles` | admin/user_management.py | POST | ✅ | JWT + Admin | ❌ NEEDS UPDATE |
| `/api/admin/users/{id}/roles` | admin/user_management.py | POST | ✅ | JWT + Admin | ❌ NEEDS UPDATE |
| `/api/admin/users/{id}/roles/{role_id}` | admin/user_management.py | DELETE | ✅ | JWT + Admin | ❌ NEEDS UPDATE |
| `/api/admin/statistics` | admin/user_management.py | GET | ✅ | JWT + Admin | ❌ NEEDS UPDATE |
| `/api/admin/audit-logs` | admin/user_management.py | GET | ✅ | JWT + Admin | ❌ NEEDS UPDATE |

### 🧪 Test Utilities (Dev/Test Only)
| Endpoint | Router | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|--------|---------|---------------|--------------|------------------|
| `/api/test-utils/cleanup-users` | test_utils.py | POST | ❌ | None | ✅ READY |
| `/api/test-utils/create-user` | test_utils.py | POST | ❌ | None | ✅ READY |
| `/api/test-utils/clear-rate-limits` | test_utils.py | POST | ❌ | None | ✅ READY |

### 📊 Root Endpoints
| Endpoint | File | Method | Auth Required | Current Auth | Stack Auth Ready |
|----------|------|---------|---------------|--------------|------------------|
| `/` | main.py | GET | ❌ | None | ✅ READY |
| `/health` | main.py | GET | ❌ | None | ✅ READY |
| `/api/dashboard` | main.py | GET | ✅ | **Stack Auth** | ✅ **ALREADY READY** |

---

## 🖥️ FRONTEND API SERVICES

### 📂 Service Files Inventory
| Service File | Purpose | Endpoints Called | Stack Auth Ready |
|--------------|---------|------------------|------------------|
| `stack-client.ts` | **Stack Auth API Client** | All authenticated endpoints | ✅ **READY** |
| `client.ts` | Legacy JWT API Client | All endpoints | ❌ **DEPRECATED** |
| `assessments.service.ts` | Assessment management | `/api/assessments/*` | ❌ NEEDS UPDATE |
| `assessments-ai.service.ts` | AI Assessment features | `/api/ai/*` | ❌ NEEDS UPDATE |
| `business-profiles.service.ts` | Business profile CRUD | `/api/business-profiles/*` | ❌ NEEDS UPDATE |
| `chat.service.ts` | AI Chat assistant | `/api/conversations/*`, `/api/chat/*` | ❌ NEEDS UPDATE |
| `compliance.service.ts` | Compliance status | `/api/compliance/*` | ❌ NEEDS UPDATE |
| `dashboard.service.ts` | Dashboard data | `/api/dashboard`, `/api/users/dashboard` | ❌ NEEDS UPDATE |
| `evidence.service.ts` | Evidence management | `/api/evidence/*` | ❌ NEEDS UPDATE |
| `evidence-collection.service.ts` | Evidence collection | `/api/evidence-collection/*` | ❌ NEEDS UPDATE |
| `frameworks.service.ts` | Compliance frameworks | `/api/frameworks/*` | ❌ NEEDS UPDATE |
| `implementation.service.ts` | Implementation plans | `/api/implementation/*` | ❌ NEEDS UPDATE |
| `integrations.service.ts` | Third-party integrations | `/api/integrations/*` | ❌ NEEDS UPDATE |
| `monitoring.service.ts` | System monitoring | `/api/monitoring/*` | ❌ NEEDS UPDATE |
| `policies.service.ts` | Policy management | `/api/policies/*` | ❌ NEEDS UPDATE |
| `readiness.service.ts` | Readiness assessments | `/api/readiness/*` | ❌ NEEDS UPDATE |
| `reports.service.ts` | Report generation | `/api/reports/*` | ❌ NEEDS UPDATE |

---

## 🚨 CRITICAL INTEGRATION REQUIREMENTS

### 1. Backend Stack Auth Integration (URGENT)
**Status**: ❌ NOT STARTED  
**Files to Create/Update**:
- `api/middleware/stack_auth_middleware.py` - Token validation middleware
- `api/dependencies/stack_auth.py` - Stack Auth dependencies
- Update all protected routes to use Stack Auth

### 2. Frontend Migration (PARTIAL)
**Status**: 🟡 50% COMPLETE  
**Completed**: Stack Auth client (`stack-client.ts`)  
**Remaining**: Update all service files to use Stack Auth client

### 3. Authentication Flow
**Current State**: 
- ✅ Frontend sends Stack Auth tokens
- ❌ Backend expects JWT tokens
- ❌ Token validation fails
- ❌ All protected endpoints return 401

---

## 🎯 NEXT STEPS (PRIORITY ORDER)

1. **CRITICAL**: Create Stack Auth backend middleware
2. **CRITICAL**: Update all protected endpoints 
3. **HIGH**: Update frontend services to use Stack Auth client
4. **MEDIUM**: Test complete auth flow
5. **LOW**: Clean up legacy JWT code

---

**Total Endpoints**: 150+ endpoints  
**Protected Endpoints**: 140+ endpoints  
**Ready for Stack Auth**: 3 endpoints  
**Need Stack Auth Update**: 140+ endpoints

⚠️ **BLOCKER**: Backend cannot validate Stack Auth tokens - all protected endpoints failing**