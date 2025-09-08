# Security Hardening Implementation Plan

## 🔴 CRITICAL Priority Fixes (Immediate)

### 1. Hardcoded Neo4j Credentials
**Files Affected**: 7 files with `neo4j_password = 'ruleiq123'`

**Strategic Fix**:
```python
# BEFORE (INSECURE):
neo4j_password = 'ruleiq123'

# AFTER (SECURE):
import os
from config.settings import get_settings

settings = get_settings()
neo4j_password = settings.neo4j_password  # From Doppler
```

### 2. SQL Injection Vulnerability
**File**: `database/performance_indexes.py`

**Strategic Fix**:
```python
# BEFORE (VULNERABLE):
await db.execute(text(f'ANALYZE {table};'))

# AFTER (SECURE):
from sqlalchemy import text
await db.execute(text('ANALYZE :table').bindparams(table=table))
```

### 3. Empty Password Hash
**File**: `api/routers/google_auth.py`

**Strategic Fix**:
```python
# BEFORE (INSECURE):
hashed_password=''

# AFTER (SECURE):
import secrets
import hashlib
random_password = secrets.token_urlsafe(32)
hashed_password = hashlib.sha256(random_password.encode()).hexdigest()
```

## 🟡 HIGH Priority Fixes (Today)

### 4. Authorization Middleware
Create comprehensive authorization checks:
```python
# middleware/authorization_middleware.py
from fastapi import HTTPException, Depends
from typing import Optional

async def check_resource_access(
    user_id: str,
    resource_id: str,
    resource_type: str,
    action: str
) -> bool:
    """Verify user has permission to access resource"""
    # Implement RBAC/ABAC logic
    pass
```

### 5. Input Validation Layer
Implement Pydantic validation for all inputs:
```python
# schemas/validation.py
from pydantic import BaseModel, validator
import re

class SecureInput(BaseModel):
    user_input: str
    
    @validator('user_input')
    def sanitize_input(cls, v):
        # Remove potential injection patterns
        v = re.sub(r'[<>\"\'%;()&+]', '', v)
        return v[:1000]  # Limit length
```

## 📋 Implementation Checklist

### Phase 1: Critical Fixes (0-2 hours)
- [ ] Replace hardcoded Neo4j passwords
- [ ] Fix SQL injection vulnerabilities
- [ ] Fix empty password hashes
- [ ] Create Doppler configuration file

### Phase 2: High Priority (2-4 hours)
- [ ] Implement authorization middleware
- [ ] Add input validation layer
- [ ] Strengthen JWT configuration
- [ ] Add security headers

### Phase 3: Medium Priority (4-8 hours)
- [ ] Implement rate limiting
- [ ] Add security event logging
- [ ] Create security test suite
- [ ] Document security practices

## 🛠️ Implementation Commands

```bash
# 1. Set up Doppler secrets
doppler secrets set NEO4J_PASSWORD --project ruleiq --config dev

# 2. Run security scan
pip install bandit safety
bandit -r . -f json -o bandit_report.json
safety check --json

# 3. Test security fixes
pytest tests/security/ -v

# 4. Verify OWASP compliance
python scripts/verify_owasp_compliance.py
```

## 📊 Success Metrics

- **Before**: Security Rating E (126 vulnerabilities)
- **Target**: Security Rating B or better
- **Critical Issues**: 0 (from 8)
- **High Issues**: <5 (from 15)
- **OWASP Compliance**: 8/10 categories passing

## 🚀 Execution Strategy

1. **Fix Critical Issues First** (Claude implements)
2. **Test Each Fix** (Automated tests)
3. **Deploy Incrementally** (One fix at a time)
4. **Monitor Security Metrics** (SonarCloud)
5. **Document Changes** (Security changelog)

---

**Ready for implementation with your approval!**