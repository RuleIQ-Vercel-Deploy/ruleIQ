# 4. BACKEND ARCHITECTURE

## 4.1 Service Layer Architecture

```python
# services/architecture.py
from typing import Protocol

class ComplianceService(Protocol):
    """Domain service interface for compliance operations"""
    
    async def generate_policy(
        self, 
        framework_id: str, 
        company_context: dict
    ) -> Policy: ...
    
    async def assess_compliance(
        self,
        framework_id: str,
        evidence: List[Evidence]
    ) -> ComplianceScore: ...
    
    async def generate_report(
        self,
        assessment_id: str,
        format: ReportFormat
    ) -> bytes: ...

# Dependency injection
class ServiceContainer:
    def __init__(self):
        self.compliance = ComplianceServiceImpl()
        self.ai = AIService()
        self.auth = AuthService()
        self.notification = NotificationService()
```

## 4.2 API Design

```yaml
API Structure:
  Version: /api/v1
  Format: RESTful + WebSocket
  Documentation: OpenAPI 3.0
  Response: Consistent envelope

Endpoints:
  Auth:
    POST   /auth/login
    POST   /auth/register
    POST   /auth/refresh
    POST   /auth/logout
    POST   /auth/reset-password
    POST   /auth/verify-email
    
  Policies:
    GET    /policies
    POST   /policies/generate
    GET    /policies/{id}
    PUT    /policies/{id}
    DELETE /policies/{id}
    POST   /policies/{id}/export
    
  Assessments:
    GET    /assessments
    POST   /assessments
    GET    /assessments/{id}
    PUT    /assessments/{id}/submit
    GET    /assessments/{id}/report
    
  Evidence:
    GET    /evidence
    POST   /evidence/upload
    GET    /evidence/{id}
    DELETE /evidence/{id}
    POST   /evidence/{id}/map
    
  AI Chat:
    WS     /chat/ws/{session_id}
    POST   /chat/message
    GET    /chat/history/{session_id}
```

## 4.3 Database Schema

```sql
-- Core entities with proper naming conventions
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    company_id UUID REFERENCES companies(company_id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE policies (
    policy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(company_id),
    framework_id UUID REFERENCES frameworks(framework_id),
    title VARCHAR(500) NOT NULL,
    content JSONB NOT NULL,
    status VARCHAR(50) NOT NULL,
    version INTEGER DEFAULT 1,
    effective_date DATE,
    review_date DATE,
    owner_id UUID REFERENCES users(user_id),
    approver_id UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_policies_company ON policies(company_id);
CREATE INDEX idx_policies_status ON policies(status);
CREATE INDEX idx_policies_dates ON policies(effective_date, review_date);
```

---
