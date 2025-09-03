# Stack Auth Migration Plan

## Overview
Migrate 826 authentication touchpoints across 25 router files from JWT to Stack Auth with 100% accuracy.

## Migration Schema

### 1. User Object Schema Changes

#### Old JWT User Model (SQLAlchemy)
```python
class User:
    id: UUID
    email: str
    username: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
```

#### New Stack Auth User Dict
```python
{
    "id": "stack_user_id_string",
    "primaryEmail": "user@example.com",
    "email": "user@example.com",  # fallback
    "displayName": "John Doe",
    "profilePictureUrl": "https://...",
    "roles": [
        {"id": "role_id", "name": "admin"}
    ],
    "metadata": {},
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z"
}
```

### 2. Import Migration Schema

| Old Import | New Import |
|------------|------------|
| `from api.dependencies.auth import get_current_active_user` | `from api.dependencies.stack_auth import get_current_stack_user` |
| `from api.dependencies.auth import get_current_user` | `from api.dependencies.stack_auth import get_current_stack_user` |
| `from database import User` | Remove if only used for typing |
| `from database.models import User` | Remove if only used for typing |

### 3. Function Signature Schema

| Old Pattern | New Pattern |
|-------------|-------------|
| `current_user: User = Depends(get_current_active_user)` | `current_user: dict = Depends(get_current_stack_user)` |
| `user: User = Depends(get_current_user)` | `user: dict = Depends(get_current_stack_user)` |

### 4. Attribute Access Schema

| Old Access | New Access | Notes |
|------------|------------|-------|
| `user.id` | `user["id"]` | Direct dict access |
| `user.email` | `user.get("primaryEmail", user.get("email", ""))` | Fallback handling |
| `user.username` | `user.get("displayName", "")` | Different field name |
| `user.is_active` | `user.get("isActive", True)` | May need custom logic |
| `user.is_superuser` | Check roles: `any(r["name"] == "admin" for r in user.get("roles", []))` | Role-based |

## Phase-by-Phase Migration Plan

### Phase 1: Core User Endpoints (Day 1)
**Files: 3 | Changes: 31 | Risk: Low**

1. **api/routers/users.py** (23 changes)
   - User profile endpoints
   - Dashboard endpoint
   - Critical for user experience

2. **main.py** (1 change)
   - Dashboard endpoint already updated
   - Verify it's working

3. **api/routers/business_profiles.py** (8 changes)
   - Core business data
   - Directly tied to users

**Validation:**
- [ ] Dry run shows expected changes
- [ ] Unit tests pass
- [ ] Manual testing with Postman
- [ ] Frontend integration test

### Phase 2: Assessment & AI Endpoints (Day 2)
**Files: 5 | Changes: 178 | Risk: Medium**

1. **api/routers/ai_assessments.py** (68 changes)
2. **api/routers/assessments.py** (Not in list, check manually)
3. **api/routers/ai_optimization.py** (25 changes)
4. **api/routers/agentic_assessments.py** (9 changes)
5. **api/routers/agentic_rag.py** (13 changes)

**Validation:**
- [ ] Dry run for each file
- [ ] AI service integration tests
- [ ] Performance benchmarks
- [ ] Error handling verification

### Phase 3: Evidence & Compliance (Day 3)
**Files: 6 | Changes: 269 | Risk: High**

1. **api/routers/evidence.py** (117 changes)
2. **api/routers/evidence_collection.py** (25 changes)
3. **api/routers/foundation_evidence.py** (63 changes)
4. **api/routers/compliance.py** (19 changes)
5. **api/routers/policies.py** (29 changes)
6. **api/routers/implementation.py** (17 changes)

**Validation:**
- [ ] Database transaction tests
- [ ] File upload/download tests
- [ ] Compliance calculation accuracy
- [ ] Policy generation tests

### Phase 4: Chat & Communication (Day 4)
**Files: 3 | Changes: 174 | Risk: Medium**

1. **api/routers/chat.py** (149 changes) - Largest file!
2. **api/routers/ai_cost_monitoring.py** (24 changes)
3. **api/routers/ai_cost_websocket.py** (1 change)

**Special Considerations:**
- WebSocket authentication needs custom handling
- Real-time features require connection state management

### Phase 5: Monitoring & Reporting (Day 5)
**Files: 4 | Changes: 140 | Risk: Low**

1. **api/routers/monitoring.py** (26 changes)
2. **api/routers/performance_monitoring.py** (46 changes)
3. **api/routers/reporting.py** (47 changes)
4. **api/routers/readiness.py** (21 changes)

### Phase 6: Admin & Security (Day 6)
**Files: 6 | Changes: 92 | Risk: High**

1. **api/routers/rbac_auth.py** (25 changes)
2. **api/routers/security.py** (21 changes)
3. **api/routers/integrations.py** (39 changes)
4. **api/routers/frameworks.py** (1 change)
5. **api/routers/uk_compliance.py** (4 changes)
6. **api/routers/ai_policy.py** (6 changes)

**Special Considerations:**
- RBAC integration with Stack Auth roles
- Permission mapping required
- Admin role verification

## Pre-Migration Checklist

### 1. Environment Setup
- [ ] Stack Auth credentials in .env
- [ ] Test Stack Auth connection
- [ ] Backup database
- [ ] Create rollback branch

### 2. Testing Infrastructure
- [ ] Update test fixtures for Stack Auth users
- [ ] Create Stack Auth test tokens
- [ ] Mock Stack Auth responses for unit tests
- [ ] Update integration test auth headers

### 3. Monitoring Setup
- [ ] Error tracking for auth failures
- [ ] Metrics for auth performance
- [ ] Alerts for high failure rates
- [ ] Rollback triggers defined

## Migration Execution Schema

### For Each File:

1. **Pre-Migration Dry Run**
   ```bash
   python scripts/migrate_stack_auth_single.py --file api/routers/users.py --dry-run
   ```

2. **Review Changes**
   - Verify import changes
   - Check type annotations
   - Validate attribute access
   - Confirm no logic changes

3. **Create Backup**
   ```bash
   cp api/routers/users.py api/routers/users.py.jwt-backup
   ```

4. **Execute Migration**
   ```bash
   python scripts/migrate_stack_auth_single.py --file api/routers/users.py --execute
   ```

5. **Run Tests**
   ```bash
   pytest tests/test_users.py -v
   ```

6. **Manual Verification**
   - Test with valid Stack Auth token
   - Test with invalid token (should 401)
   - Test with no token (should 401)
   - Verify user data mapping

7. **Commit**
   ```bash
   git add api/routers/users.py
   git commit -m "feat: migrate users router to Stack Auth"
   ```

## Rollback Plan

### Immediate Rollback (per file)
```bash
cp api/routers/users.py.jwt-backup api/routers/users.py
```

### Full Rollback
```bash
git checkout jwt-auth-backup
```

## Success Criteria

### Per-File Success
- [ ] All tests pass
- [ ] No 500 errors in logs
- [ ] Auth success rate > 95%
- [ ] Response time < 200ms

### Overall Success
- [ ] All 826 changes applied
- [ ] Zero authentication bypass vulnerabilities
- [ ] Frontend fully functional
- [ ] No user complaints
- [ ] Performance maintained or improved

## Risk Mitigation

### High-Risk Areas
1. **User ID Type Mismatch**
   - JWT uses UUID, Stack uses string
   - Solution: Ensure string conversion in DB queries

2. **Email Field Name**
   - JWT uses `email`, Stack uses `primaryEmail`
   - Solution: Fallback handling in place

3. **Permission System**
   - JWT uses `is_superuser`, Stack uses roles
   - Solution: Role mapping function

4. **WebSocket Auth**
   - Different auth flow than REST
   - Solution: Custom WebSocket auth handler

## Post-Migration Tasks

1. **Remove JWT Dependencies**
   - Remove python-jose
   - Remove passlib
   - Remove JWT middleware

2. **Update Documentation**
   - API documentation
   - Developer guides
   - Deployment instructions

3. **Security Audit**
   - Penetration testing
   - Auth flow review
   - Token security verification

## Emergency Contacts

- Stack Auth Support: support@stack-auth.com
- DevOps Lead: [Contact]
- Security Team: [Contact]

---

**Remember**: ALWAYS dry run before execution. This is not optional.