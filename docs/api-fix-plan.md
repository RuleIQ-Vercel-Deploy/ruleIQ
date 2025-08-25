# API Connection Fix Implementation Plan

## Summary
- **Total Missing Endpoints**: 99
- **Services Affected**: 18
- **Backend Endpoints to Create**: 99

## Implementation by Router

### evidence.py (9 endpoints)
**File**: `api/routers/evidence.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| GET | `evidence` | evidence.service |
| GET | `evidence/{id}` | evidence.service |
| POST | `evidence` | evidence.service |
| PATCH | `evidence/{id}` | evidence.service |
| POST | `evidence/{id}/automation` | evidence.service |
| GET | `evidence/dashboard/{frameworkId}` | evidence.service |
| POST | `evidence/{id}/classify` | evidence.service |
| GET | `evidence/requirements/{frameworkId}` | evidence.service |
| GET | `evidence/{id}/quality` | evidence.service |

### compliance.py (8 endpoints)
**File**: `api/routers/compliance.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| GET | `compliance/status/{frameworkId}` | compliance.service |
| POST | `compliance/tasks` | compliance.service |
| PATCH | `compliance/tasks/{taskId}` | compliance.service |
| POST | `compliance/risks` | compliance.service |
| PATCH | `compliance/risks/{riskId}` | compliance.service |
| GET | `compliance/timeline` | compliance.service |
| GET | `compliance/dashboard` | compliance.service |
| POST | `compliance/certificate/generate` | compliance.service |

### policies.py (8 endpoints)
**File**: `api/routers/policies.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| GET | `policies` | policies.service |
| GET | `policies/{id}` | policies.service |
| PATCH | `policies/{id}/status` | policies.service |
| PUT | `policies/{id}/approve` | policies.service |
| POST | `policies/{id}/regenerate-section` | policies.service |
| GET | `policies/templates` | policies.service |
| POST | `policies/{id}/clone` | policies.service |
| GET | `policies/{id}/versions` | policies.service |

### frameworks.py (7 endpoints)
**File**: `api/routers/frameworks.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| GET | `frameworks` | frameworks.service |
| GET | `frameworks/{id}` | frameworks.service |
| GET | `frameworks/{frameworkId}/controls` | frameworks.service |
| GET | `frameworks/{frameworkId}/implementation-guide` | frameworks.service |
| GET | `frameworks/{frameworkId}/compliance-status` | frameworks.service |
| POST | `frameworks/compare` | frameworks.service |
| GET | `frameworks/{frameworkId}/maturity-assessment` | frameworks.service |

### integrations.py (7 endpoints)
**File**: `api/routers/integrations.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| GET | `integrations` | integrations.service |
| GET | `integrations/connected` | integrations.service |
| POST | `integrations/{integrationId}/test` | integrations.service |
| GET | `integrations/{integrationId}/sync-history` | integrations.service |
| POST | `integrations/{integrationId}/webhooks` | integrations.service |
| GET | `integrations/{integrationId}/logs` | integrations.service |
| POST | `integrations/oauth/callback` | integrations.service |

### monitoring.py (7 endpoints)
**File**: `api/routers/monitoring.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| GET | `monitoring/database/status` | monitoring.service |
| PATCH | `monitoring/alerts/{alertId}/resolve` | monitoring.service |
| GET | `monitoring/metrics` | monitoring.service |
| GET | `monitoring/api-performance` | monitoring.service |
| GET | `monitoring/error-logs` | monitoring.service |
| GET | `monitoring/health` | monitoring.service |
| GET | `monitoring/audit-logs` | monitoring.service |

### payment.py (7 endpoints)
**File**: `api/routers/payment.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| POST | `payments/subscription/cancel` | payment.service |
| POST | `payments/subscription/reactivate` | payment.service |
| POST | `payments/payment-methods` | payment.service |
| GET | `payments/invoices` | payment.service |
| GET | `payments/invoices/upcoming` | payment.service |
| POST | `payments/coupons/apply` | payment.service |
| GET | `payments/subscription/limits` | payment.service |

### assessments.py (6 endpoints)
**File**: `api/routers/assessments.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| GET | `assessments` | assessments.service |
| GET | `assessments/{id}` | assessments.service |
| POST | `assessments` | assessments.service |
| PATCH | `assessments/{id}` | assessments.service |
| POST | `assessments/{id}/complete` | assessments.service |
| GET | `assessments/{id}/results` | assessments.service |

### readiness.py (6 endpoints)
**File**: `api/routers/readiness.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| GET | `readiness/{businessProfileId}` | readiness.service |
| GET | `readiness/gaps/{businessProfileId}` | readiness.service |
| POST | `readiness/roadmap` | readiness.service |
| POST | `readiness/quick-assessment` | readiness.service |
| GET | `readiness/trends/{businessProfileId}` | readiness.service |
| GET | `readiness/benchmarks` | readiness.service |

### reports.py (6 endpoints)
**File**: `api/routers/reports.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| GET | `reports/history` | reports.service |
| GET | `reports/{id}` | reports.service |
| POST | `reports/schedule` | reports.service |
| GET | `reports/scheduled` | reports.service |
| POST | `reports/preview` | reports.service |
| GET | `reports/analytics` | reports.service |

### business_profiles.py (5 endpoints)
**File**: `api/routers/business_profiles.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| GET | `business-profiles` | business-profiles.service |
| GET | `business-profiles/{id}` | business-profiles.service |
| POST | `business-profiles` | business-profiles.service |
| PUT | `business-profiles/{id}` | business-profiles.service |
| GET | `business-profiles/{id}/compliance` | business-profiles.service |

### dashboard.py (5 endpoints)
**File**: `api/routers/dashboard.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| GET | `dashboard` | dashboard.service |
| GET | `dashboard/widgets` | dashboard.service |
| GET | `dashboard/notifications` | dashboard.service |
| GET | `dashboard/quick-actions` | dashboard.service |
| GET | `dashboard/recommendations` | dashboard.service |

### foundation_evidence.py (5 endpoints)
**File**: `api/routers/foundation_evidence.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| POST | `foundation/evidence/aws/configure` | foundation-evidence.service |
| POST | `foundation/evidence/okta/configure` | foundation-evidence.service |
| POST | `foundation/evidence/google/configure` | foundation-evidence.service |
| POST | `foundation/evidence/microsoft/configure` | foundation-evidence.service |
| GET | `foundation/evidence/health` | foundation-evidence.service |

### ai_assessments.py (4 endpoints)
**File**: `api/routers/ai_assessments.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| POST | `ai/self-review` | ai-self-review.service |
| POST | `ai/quick-confidence-check` | ai-self-review.service |
| POST | `ai/assessments/followup` | assessments-ai.service |
| GET | `ai/assessments/metrics` | assessments-ai.service |

### chat.py (4 endpoints)
**File**: `api/routers/chat.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| GET | `chat/conversations/{id}` | chat.service |
| POST | `chat/compliance-gap-analysis` | chat.service |
| GET | `chat/smart-compliance-guidance` | chat.service |
| DELETE | `chat/cache/clear?pattern={encodeURIComponent(pattern)}` | chat.service |

### implementation.py (4 endpoints)
**File**: `api/routers/implementation.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| GET | `implementation/plans/{planId}` | implementation.service |
| GET | `implementation/recommendations` | implementation.service |
| GET | `implementation/resources/{frameworkId}` | implementation.service |
| GET | `implementation/plans/{planId}/analytics` | implementation.service |

### evidence_collection.py (1 endpoints)
**File**: `api/routers/evidence_collection.py`

| Method | Path | Frontend Service |
|--------|------|-----------------|
| GET | `evidence-collection/plans` | evidence-collection.service |

## Frontend Services Breakdown

### ai-self-review.service (2 endpoints)
- POST `/ai/self-review`
- POST `/ai/quick-confidence-check`

### assessments-ai.service (2 endpoints)
- POST `/ai/assessments/followup`
- GET `/ai/assessments/metrics`

### assessments.service (6 endpoints)
- GET `/assessments`
- GET `/assessments/${id}`
- POST `/assessments`
- PATCH `/assessments/${id}`
- POST `/assessments/${id}/complete`
- GET `/assessments/${id}/results`

### business-profiles.service (5 endpoints)
- GET `/business-profiles`
- GET `/business-profiles/${id}`
- POST `/business-profiles`
- PUT `/business-profiles/${id}`
- GET `/business-profiles/${id}/compliance`

### chat.service (4 endpoints)
- GET `/chat/conversations/${id}`
- POST `/chat/compliance-gap-analysis`
- GET `/chat/smart-compliance-guidance`
- DELETE `/chat/cache/clear?pattern=${encodeURIComponent(pattern)}`

### compliance.service (8 endpoints)
- GET `/compliance/status/${frameworkId}`
- POST `/compliance/tasks`
- PATCH `/compliance/tasks/${taskId}`
- POST `/compliance/risks`
- PATCH `/compliance/risks/${riskId}`
- GET `/compliance/timeline`
- GET `/compliance/dashboard`
- POST `/compliance/certificate/generate`

### dashboard.service (5 endpoints)
- GET `/dashboard`
- GET `/dashboard/widgets`
- GET `/dashboard/notifications`
- GET `/dashboard/quick-actions`
- GET `/dashboard/recommendations`

### evidence-collection.service (1 endpoints)
- GET `/evidence-collection/plans`

### evidence.service (9 endpoints)
- GET `/evidence`
- GET `/evidence/${id}`
- POST `/evidence`
- PATCH `/evidence/${id}`
- POST `/evidence/${id}/automation`
- GET `/evidence/dashboard/${frameworkId}`
- POST `/evidence/${id}/classify`
- GET `/evidence/requirements/${frameworkId}`
- GET `/evidence/${id}/quality`

### foundation-evidence.service (5 endpoints)
- POST `/foundation/evidence/aws/configure`
- POST `/foundation/evidence/okta/configure`
- POST `/foundation/evidence/google/configure`
- POST `/foundation/evidence/microsoft/configure`
- GET `/foundation/evidence/health`

### frameworks.service (7 endpoints)
- GET `/frameworks`
- GET `/frameworks/${id}`
- GET `/frameworks/${frameworkId}/controls`
- GET `/frameworks/${frameworkId}/implementation-guide`
- GET `/frameworks/${frameworkId}/compliance-status`
- POST `/frameworks/compare`
- GET `/frameworks/${frameworkId}/maturity-assessment`

### implementation.service (4 endpoints)
- GET `/implementation/plans/${planId}`
- GET `/implementation/recommendations`
- GET `/implementation/resources/${frameworkId}`
- GET `/implementation/plans/${planId}/analytics`

### integrations.service (7 endpoints)
- GET `/integrations`
- GET `/integrations/connected`
- POST `/integrations/${integrationId}/test`
- GET `/integrations/${integrationId}/sync-history`
- POST `/integrations/${integrationId}/webhooks`
- GET `/integrations/${integrationId}/logs`
- POST `/integrations/oauth/callback`

### monitoring.service (7 endpoints)
- GET `/monitoring/database/status`
- PATCH `/monitoring/alerts/${alertId}/resolve`
- GET `/monitoring/metrics`
- GET `/monitoring/api-performance`
- GET `/monitoring/error-logs`
- GET `/monitoring/health`
- GET `/monitoring/audit-logs`

### payment.service (7 endpoints)
- POST `/payments/subscription/cancel`
- POST `/payments/subscription/reactivate`
- POST `/payments/payment-methods`
- GET `/payments/invoices`
- GET `/payments/invoices/upcoming`
- POST `/payments/coupons/apply`
- GET `/payments/subscription/limits`

### policies.service (8 endpoints)
- GET `/policies`
- GET `/policies/${id}`
- PATCH `/policies/${id}/status`
- PUT `/policies/${id}/approve`
- POST `/policies/${id}/regenerate-section`
- GET `/policies/templates`
- POST `/policies/${id}/clone`
- GET `/policies/${id}/versions`

### readiness.service (6 endpoints)
- GET `/readiness/${businessProfileId}`
- GET `/readiness/gaps/${businessProfileId}`
- POST `/readiness/roadmap`
- POST `/readiness/quick-assessment`
- GET `/readiness/trends/${businessProfileId}`
- GET `/readiness/benchmarks`

### reports.service (6 endpoints)
- GET `/reports/history`
- GET `/reports/${id}`
- POST `/reports/schedule`
- GET `/reports/scheduled`
- POST `/reports/preview`
- GET `/reports/analytics`