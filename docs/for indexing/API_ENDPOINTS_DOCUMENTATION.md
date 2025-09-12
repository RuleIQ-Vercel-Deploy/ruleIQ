# ruleIQ API Endpoints Documentation

**Updated**: 2025-08-15  
**API Version**: v1  
**Base URL**: `/api/v1`  
**Total Endpoints**: 100+  
**Authentication**: JWT + RBAC

## 🎯 API Standardization Status

✅ **COMPLETE**: All endpoints now follow the `/api/v1/` pattern

## 📋 Summary

| Category | Details |
|----------|---------|
| API Version | v1 (standardized) |
| Base Path | `/api/v1/` |
| Authentication | JWT Bearer Token |
| RBAC | Role-based permissions |
| Rate Limiting | Applied per endpoint |
| Response Format | JSON |
| Error Format | Standardized error responses |

## 🔐 Authentication

All endpoints except health/public endpoints require JWT authentication:

```
Authorization: Bearer <jwt_token>
```

## 📍 Endpoint Groups

### Authentication & Users
| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| POST | `/api/v1/auth/signup` | User registration | ❌ | 5/min |
| POST | `/api/v1/auth/login` | User login | ❌ | 5/min |
| POST | `/api/v1/auth/logout` | User logout | ✅ | - |
| POST | `/api/v1/auth/refresh` | Refresh token | ✅ | 10/min |
| POST | `/api/v1/auth/forgot-password` | Password reset request | ❌ | 3/min |
| POST | `/api/v1/auth/reset-password` | Password reset confirm | ❌ | 3/min |
| GET | `/api/v1/users/me` | Current user profile | ✅ | - |
| PUT | `/api/v1/users/me` | Update profile | ✅ | - |
| DELETE | `/api/v1/users/me` | Delete account | ✅ | - |

### Business Profiles
| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| GET | `/api/v1/business-profiles` | List profiles | ✅ | - |
| POST | `/api/v1/business-profiles` | Create profile | ✅ | - |
| GET | `/api/v1/business-profiles/{id}` | Get profile | ✅ | - |
| PUT | `/api/v1/business-profiles/{id}` | Update profile | ✅ | - |
| DELETE | `/api/v1/business-profiles/{id}` | Delete profile | ✅ | - |

### Assessments
| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| GET | `/api/v1/assessments` | List assessments | ✅ | - |
| POST | `/api/v1/assessments` | Create assessment | ✅ | - |
| GET | `/api/v1/assessments/{id}` | Get assessment | ✅ | - |
| PUT | `/api/v1/assessments/{id}` | Update assessment | ✅ | - |
| DELETE | `/api/v1/assessments/{id}` | Delete assessment | ✅ | - |
| POST | `/api/v1/assessments/{id}/submit` | Submit assessment | ✅ | - |
| GET | `/api/v1/assessments/{id}/results` | Get results | ✅ | - |

### AI-Powered Features
| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| POST | `/api/v1/ai-assessments/analysis` | AI analysis | ✅ | 20/min |
| POST | `/api/v1/ai-assessments/analysis/stream` | Streaming analysis | ✅ | 20/min |
| POST | `/api/v1/ai-assessments/recommendations` | AI recommendations | ✅ | 20/min |
| POST | `/api/v1/ai-assessments/recommendations/stream` | Streaming recommendations | ✅ | 20/min |
| POST | `/api/v1/ai-assessments/{framework_id}/help` | Framework help | ✅ | 20/min |
| POST | `/api/v1/ai-assessments/{framework_id}/help/stream` | Streaming help | ✅ | 20/min |
| POST | `/api/v1/ai-assessments/followup` | Follow-up questions | ✅ | 20/min |

### AI Optimization & Cost
| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| GET | `/api/v1/ai/optimization/performance` | Performance metrics | ✅ | - |
| GET | `/api/v1/ai/optimization/health` | System health | ✅ | - |
| POST | `/api/v1/ai/optimization/reset` | Reset circuit breaker | ✅ | - |
| GET | `/api/v1/ai/cost/analytics/daily` | Daily cost analytics | ✅ | - |
| GET | `/api/v1/ai/cost/analytics/trends` | Cost trends | ✅ | - |
| GET | `/api/v1/ai/cost/alerts` | Budget alerts | ✅ | - |
| POST | `/api/v1/ai/cost/budget/configure` | Configure budget | ✅ | - |
| WS | `/api/v1/ai/cost-websocket/ws` | Real-time cost updates | ✅ | - |

### Policies
| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| GET | `/api/v1/policies` | List policies | ✅ | - |
| POST | `/api/v1/policies` | Create policy | ✅ | - |
| GET | `/api/v1/policies/{id}` | Get policy | ✅ | - |
| PUT | `/api/v1/policies/{id}` | Update policy | ✅ | - |
| DELETE | `/api/v1/policies/{id}` | Delete policy | ✅ | - |
| POST | `/api/v1/ai/policies/generate` | AI policy generation | ✅ | 10/min |
| POST | `/api/v1/ai/policies/review` | AI policy review | ✅ | 10/min |

### Frameworks & Compliance
| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| GET | `/api/v1/frameworks` | List frameworks | ✅ | - |
| GET | `/api/v1/frameworks/{id}` | Get framework | ✅ | - |
| GET | `/api/v1/frameworks/{id}/controls` | Framework controls | ✅ | - |
| GET | `/api/v1/compliance/status` | Compliance status | ✅ | - |
| GET | `/api/v1/compliance/gaps` | Compliance gaps | ✅ | - |
| POST | `/api/v1/compliance/report` | Generate report | ✅ | 5/min |

### UK-Specific Compliance
| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| GET | `/api/v1/uk-compliance/frameworks` | UK frameworks | ✅ | - |
| GET | `/api/v1/uk-compliance/requirements` | UK requirements | ✅ | - |
| POST | `/api/v1/uk-compliance/assess` | UK assessment | ✅ | - |
| GET | `/api/v1/uk-compliance/gdpr` | GDPR compliance | ✅ | - |
| GET | `/api/v1/uk-compliance/cyber-essentials` | Cyber Essentials | ✅ | - |

### Evidence Management
| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| GET | `/api/v1/evidence` | List evidence | ✅ | - |
| POST | `/api/v1/evidence` | Upload evidence | ✅ | - |
| GET | `/api/v1/evidence/{id}` | Get evidence | ✅ | - |
| PUT | `/api/v1/evidence/{id}` | Update evidence | ✅ | - |
| DELETE | `/api/v1/evidence/{id}` | Delete evidence | ✅ | - |
| POST | `/api/v1/evidence-collection/configure` | Configure collection | ✅ | - |
| POST | `/api/v1/evidence-collection/start` | Start collection | ✅ | - |
| GET | `/api/v1/foundation-evidence` | Foundation evidence | ✅ | - |

### Implementation & Readiness
| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| GET | `/api/v1/implementation/plan` | Implementation plan | ✅ | - |
| POST | `/api/v1/implementation/start` | Start implementation | ✅ | - |
| GET | `/api/v1/implementation/progress` | Progress tracking | ✅ | - |
| GET | `/api/v1/readiness/score` | Readiness score | ✅ | - |
| GET | `/api/v1/readiness/gaps` | Readiness gaps | ✅ | - |

### Reporting & Analytics
| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| GET | `/api/v1/reports` | List reports | ✅ | - |
| POST | `/api/v1/reports/generate` | Generate report | ✅ | 5/min |
| GET | `/api/v1/reports/{id}` | Get report | ✅ | - |
| GET | `/api/v1/reports/{id}/download` | Download report | ✅ | - |

### Integrations
| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| GET | `/api/v1/integrations` | List integrations | ✅ | - |
| POST | `/api/v1/integrations/connect` | Connect integration | ✅ | - |
| DELETE | `/api/v1/integrations/{id}` | Disconnect | ✅ | - |
| POST | `/api/v1/integrations/sync` | Sync data | ✅ | 10/min |

### Monitoring & Health
| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| GET | `/api/v1/monitoring/metrics` | System metrics | ✅ | - |
| GET | `/api/v1/monitoring/health` | Health check | ❌ | - |
| GET | `/api/v1/performance/metrics` | Performance metrics | ✅ | - |
| GET | `/api/v1/security/audit-log` | Audit log | ✅ | - |
| GET | `/api/v1/security/threats` | Threat detection | ✅ | - |

### Chat & Support
| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| POST | `/api/v1/chat/message` | Send message | ✅ | 30/min |
| GET | `/api/v1/chat/history` | Chat history | ✅ | - |
| WS | `/api/v1/chat/ws` | WebSocket chat | ✅ | - |

## 🔄 Frontend API Client Integration

The frontend API client (`frontend/lib/api/client.ts`) automatically handles endpoint normalization:

```typescript
// Frontend service calls can use clean paths:
apiClient.get('/business-profiles')  // → GET /api/v1/business-profiles
apiClient.post('/assessments')       // → POST /api/v1/assessments

// Already versioned paths pass through:
apiClient.post('/api/v1/auth/login') // → POST /api/v1/auth/login
```

## 📝 Response Format

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details
    }
  }
}
```

## 🚦 Rate Limiting

Rate limits are applied per endpoint and per user:

| Category | Limit | Window |
|----------|-------|--------|
| Authentication | 5 requests | 1 minute |
| AI Operations | 20 requests | 1 minute |
| General API | 100 requests | 1 minute |
| Report Generation | 5 requests | 1 minute |

## 🔒 RBAC Permissions

Role-based access control is enforced on all protected endpoints:

| Role | Permissions |
|------|------------|
| `admin` | Full access to all endpoints |
| `user` | Access to own resources |
| `viewer` | Read-only access |
| `guest` | Limited public endpoints only |

## 🛠️ Development & Testing

### Local Development
```bash
# Backend API
http://localhost:8000/api/v1/

# API Documentation
http://localhost:8000/docs

# Frontend
http://localhost:3000
```

### Testing Endpoints
```bash
# Health check (no auth required)
curl http://localhost:8000/api/v1/monitoring/health

# Authenticated request
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/users/me
```

## 📚 Migration Notes

### From Legacy Endpoints
If migrating from legacy endpoints, update your API calls:

| Old Pattern | New Pattern |
|-------------|-------------|
| `/api/assessments` | `/api/v1/assessments` |
| `/api/frameworks` | `/api/v1/frameworks` |
| `/api/policies` | `/api/v1/policies` |

The frontend API client handles this automatically, but direct API calls should use the new pattern.

## 🔍 Monitoring & Debugging

### API Logs
- All API requests are logged with correlation IDs
- Rate limit violations are logged with user context
- Authentication failures trigger security alerts

### Performance Metrics
- Average response time: <200ms target
- 99th percentile: <500ms
- Error rate: <1%

## 📞 Support

For API issues or questions:
- Check API documentation at `/docs`
- Review error responses for debugging hints
- Contact support with correlation ID from error response

---

*Last Updated: 2025-08-15*  
*API Version: 1.0.0*  
*Documentation Version: 2.0.0*