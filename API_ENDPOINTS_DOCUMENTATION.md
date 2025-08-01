# ruleIQ API Endpoints Documentation

**Generated**: 2025-08-01 09:51:50  
**Total Endpoints**: 41  
**Authentication Status**: 35 authenticated, 6 public

## Summary

| Metric | Count |
|--------|-------|
| Total Endpoints | 41 |
| Authenticated Endpoints | 35 |
| Public Endpoints | 6 |
| JWT Protected | 32 |
| Stack Auth (MIGRATION NEEDED) | 0 |
| Rate Limited | 10 |
| RBAC Protected | 0 |

## Authentication Issues

✅ No authentication issues found!

## Endpoints by File

### api/routers/ai_assessments.py

#### 🔒 `POST /api/v1/analysis`

- **Function**: `generate_analysis_stream`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user, rate_limit
- **Rate Limited**: ✅

#### 🔒 `POST /api/v1/analysis/stream`

- **Function**: `generate_analysis_stream`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user, rate_limit
- **Rate Limited**: ✅

#### 🔒 `POST /api/v1/followup`

- **Function**: `generate_analysis_stream`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user, rate_limit
- **Rate Limited**: ✅

#### 🔒 `POST /api/v1/recommendations`

- **Function**: `generate_recommendations_stream`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user, rate_limit
- **Rate Limited**: ✅

#### 🔒 `POST /api/v1/recommendations/stream`

- **Function**: `generate_recommendations_stream`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user, rate_limit
- **Rate Limited**: ✅

#### 🔒 `POST /api/v1/{framework_id}/help`

- **Function**: `generate_help_stream`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user, rate_limit
- **Rate Limited**: ✅

#### 🔒 `POST /api/v1/{framework_id}/help/stream`

- **Function**: `generate_help_stream`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user, rate_limit
- **Rate Limited**: ✅


### api/routers/ai_cost_monitoring.py

#### 🔒 `GET /api/v1/alerts`

- **Function**: `get_budget_alerts`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user

#### 🔒 `GET /api/v1/analytics/daily`

- **Function**: `get_budget_status`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user

#### 🔒 `GET /api/v1/analytics/trends`

- **Function**: `get_budget_status`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user

#### 🔒 `POST /api/v1/budget/configure`

- **Function**: `get_budget_status`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user

#### 🔒 `GET /api/v1/budget/status`

- **Function**: `get_budget_status`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user

#### 🔒 `DELETE /api/v1/cache/clear`

- **Function**: `clear_cost_cache`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user

#### 🌐 `GET /api/v1/health`

- **Function**: `cost_monitoring_health`
- **Authentication**: PUBLIC

#### 🔒 `GET /api/v1/optimization/recommendations`

- **Function**: `get_optimization_recommendations`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user

#### 🔒 `GET /api/v1/reports/monthly`

- **Function**: `cost_monitoring_health`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user

#### 🔒 `POST /api/v1/routing/select-model`

- **Function**: `select_optimal_model`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user

#### 🔒 `POST /api/v1/track`

- **Function**: `get_budget_status`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user

#### 🔒 `GET /api/v1/usage/by-service`

- **Function**: `cost_monitoring_health`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user


### api/routers/ai_cost_websocket.py

#### 🌐 `POST /api/v1/broadcast/alert`

- **Function**: `broadcast_budget_alert`
- **Authentication**: PUBLIC

#### 🌐 `POST /api/v1/broadcast/cost-spike`

- **Function**: `broadcast_cost_spike`
- **Authentication**: PUBLIC

#### 🌐 `GET /api/v1/connections/stats`

- **Function**: `get_connection_stats`
- **Authentication**: PUBLIC


### api/routers/ai_policy.py

#### 🔒 `POST /api/v1/analytics/export`

- **Function**: `export_analytics`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user

#### 🔒 `POST /api/v1/generate-policy`

- **Function**: `get_ai_metrics`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user

#### 🔒 `GET /api/v1/metrics`

- **Function**: `get_ai_metrics`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user

#### 🔒 `GET /api/v1/policy-templates`

- **Function**: `get_ai_metrics`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user

#### 🔒 `PUT /api/v1/refine-policy`

- **Function**: `get_ai_metrics`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user

#### 🔒 `POST /api/v1/validate-policy`

- **Function**: `_log_generation_metrics`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user


### api/routers/google_auth.py

#### 🌐 `GET /api/v1/login`

- **Function**: `google_login`
- **Authentication**: PUBLIC


### api/routers/performance_monitoring.py

#### 🔒 `POST /api/v1/alerts/configure`

- **Function**: `performance_monitoring_health`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user, require_permissions, require_permission

#### 🔒 `GET /api`

- **Function**: `performance_monitoring_health`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user, require_permissions, require_permission

#### 🔒 `GET /api/v1/cache`

- **Function**: `performance_monitoring_health`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user, require_permissions, require_permission

#### 🔒 `GET /api/v1/database`

- **Function**: `performance_monitoring_health`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user, require_permissions, require_permission

#### 🌐 `GET /api/v1/health`

- **Function**: `performance_monitoring_health`
- **Authentication**: PUBLIC

#### 🔒 `GET /api/v1/overview`

- **Function**: `performance_monitoring_health`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user, require_permissions, require_permission

#### 🔒 `GET /api/v1/recommendations`

- **Function**: `performance_monitoring_health`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user, require_permissions, require_permission

#### 🔒 `GET /api/v1/system`

- **Function**: `performance_monitoring_health`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user, require_permissions, require_permission

#### 🔒 `GET /api/v1/trends`

- **Function**: `performance_monitoring_health`
- **Authentication**: JWT
- **Dependencies**: get_current_active_user, require_permissions, require_permission


### api/routers/test_utils.py

#### 🔒 `DELETE /api/v1/cleanup-test-users`

- **Function**: `clear_rate_limits`
- **Authentication**: PUBLIC
- **Dependencies**: rate_limit
- **Rate Limited**: ✅

#### 🔒 `POST /api/v1/clear-rate-limits`

- **Function**: `clear_rate_limits`
- **Authentication**: PUBLIC
- **Dependencies**: rate_limit
- **Rate Limited**: ✅

#### 🔒 `POST /api/v1/create-test-user`

- **Function**: `clear_rate_limits`
- **Authentication**: PUBLIC
- **Dependencies**: rate_limit
- **Rate Limited**: ✅


