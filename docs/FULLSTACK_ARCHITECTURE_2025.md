# RuleIQ Full-Stack Architecture Document
## Version 2.0 - January 2025

---

## EXECUTIVE SUMMARY

This document defines the complete full-stack architecture for RuleIQ's compliance automation platform, addressing critical security vulnerabilities, user experience gaps, and performance optimizations identified in the January 2025 audit.

**Critical Finding**: Authentication middleware is currently bypassed, creating a P0 security vulnerability that must be fixed immediately.

---

## 1. SYSTEM OVERVIEW

### 1.1 Platform Vision
RuleIQ is an AI-powered compliance automation platform designed for UK SMBs, simplifying regulatory compliance through intelligent automation, assessment workflows, and evidence management.

### 1.2 Architecture Pattern
- **Pattern**: Microservices-ready monolith with clear service boundaries
- **Approach**: Domain-driven design with vertical slice architecture
- **Scale Strategy**: Horizontal scaling with future service extraction capability

### 1.3 Technology Stack

```yaml
Frontend:
  Framework: Next.js 15.4.7
  Language: TypeScript 5.x
  Styling: Tailwind CSS + shadcn/ui
  State: Zustand + React Query
  Testing: Vitest + Playwright

Backend:
  Framework: FastAPI 0.115
  Language: Python 3.13
  ORM: SQLAlchemy 2.0 + Alembic
  Testing: pytest + pytest-asyncio

Database:
  Primary: PostgreSQL 15 (Neon)
  Cache: Redis 7
  Vector: pgvector for AI embeddings

AI/ML:
  Primary: Google Gemini 2.5 Pro/Flash
  Embeddings: text-embedding-004
  RAG: LangChain + pgvector

Infrastructure:
  Container: Docker
  Queue: Celery + Redis
  Monitoring: Prometheus + Grafana
  Logging: Structured logging with correlation IDs
```

---

## 2. SECURITY ARCHITECTURE

### 2.1 Authentication & Authorization

#### CRITICAL FIX REQUIRED
```typescript
// Current middleware.ts LINE 11 - BYPASSES ALL AUTH
export function middleware(request: NextRequest) {
  return NextResponse.next(); // REMOVE THIS - SECURITY VULNERABILITY
}
```

#### Correct Implementation
```typescript
// middleware.ts - SECURE VERSION
export async function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token');
  
  // Public routes that don't require auth
  const publicRoutes = ['/login', '/register', '/reset-password', '/api/auth/*'];
  const isPublicRoute = publicRoutes.some(route => 
    request.nextUrl.pathname.startsWith(route)
  );
  
  if (isPublicRoute) {
    return NextResponse.next();
  }
  
  // Validate JWT token
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  try {
    const payload = await verifyJWT(token.value);
    
    // Add user context to headers
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set('x-user-id', payload.userId);
    requestHeaders.set('x-user-role', payload.role);
    
    return NextResponse.next({
      request: {
        headers: requestHeaders,
      },
    });
  } catch (error) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
```

### 2.2 Security Layers

```yaml
Authentication:
  Method: JWT with refresh tokens
  Storage: HttpOnly cookies
  Rotation: 15min access / 7day refresh
  MFA: TOTP support ready

Authorization:
  Model: RBAC with permissions
  Roles: Admin, ComplianceOfficer, Auditor, User
  Middleware: Role-based route protection
  API: Permission decorators

Rate Limiting:
  Global: 1000 req/min per IP
  Auth: 5 attempts per 15min
  AI: 100 requests per hour
  Upload: 10 files per minute

CORS:
  Origins: Whitelist production domains
  Credentials: Include for auth cookies
  Headers: Strict allowed headers

Input Validation:
  Frontend: Zod schemas
  Backend: Pydantic models
  SQL: Parameterized queries only
  Files: Type/size validation

Secrets Management:
  Provider: Doppler
  Rotation: Automated 90-day
  Access: Environment-based
  Audit: Full access logs
```

---

## 3. FRONTEND ARCHITECTURE

### 3.1 Component Structure

```typescript
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Auth pages (public)
│   │   ├── login/
│   │   ├── register/
│   │   ├── reset-password/
│   │   └── onboarding/
│   ├── (dashboard)/              # Protected pages
│   │   ├── layout.tsx           # Auth wrapper
│   │   ├── page.tsx             # Dashboard
│   │   ├── policies/
│   │   ├── assessments/
│   │   ├── evidence/
│   │   ├── risks/
│   │   ├── profile/             # User management
│   │   └── settings/
│   └── api/                      # API routes
├── components/
│   ├── ui/                       # shadcn/ui components
│   ├── features/                 # Feature components
│   │   ├── auth/
│   │   ├── policies/
│   │   ├── assessments/
│   │   └── evidence/
│   ├── layouts/
│   └── shared/
├── lib/
│   ├── api/                      # API client services
│   ├── auth/                     # Auth utilities
│   ├── hooks/                    # Custom React hooks
│   ├── stores/                   # Zustand stores
│   └── utils/
└── types/
```

### 3.2 State Management

```typescript
// stores/auth.store.ts
interface AuthStore {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginDto) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

// stores/compliance.store.ts
interface ComplianceStore {
  policies: Policy[];
  assessments: Assessment[];
  currentFramework: Framework | null;
  complianceScore: number;
  fetchDashboardData: () => Promise<void>;
}
```

### 3.3 Performance Optimizations

```typescript
// Dynamic imports for code splitting
const PolicyEditor = dynamic(() => import('@/components/features/policies/PolicyEditor'), {
  loading: () => <PolicyEditorSkeleton />,
  ssr: false,
});

// Image optimization
const OptimizedImage = ({ src, alt, ...props }) => (
  <Image
    src={src}
    alt={alt}
    placeholder="blur"
    blurDataURL={generateBlurDataURL(src)}
    loading="lazy"
    {...props}
  />
);

// Virtual scrolling for large lists
const VirtualPolicyList = ({ policies }) => (
  <VirtualList
    height={600}
    itemCount={policies.length}
    itemSize={120}
    width="100%"
  >
    {({ index, style }) => (
      <div style={style}>
        <PolicyCard policy={policies[index]} />
      </div>
    )}
  </VirtualList>
);
```

### 3.4 Accessibility Compliance

```yaml
WCAG 2.1 AA Requirements:
  Color Contrast:
    Text: 4.5:1 minimum
    Large Text: 3:1 minimum
    Interactive: 3:1 minimum
    Fix: Update teal-300 to #14B8A6

  Keyboard Navigation:
    Skip Links: Add to layout
    Focus Trap: Modal implementation
    Tab Order: Logical flow
    Shortcuts: Document all

  ARIA Implementation:
    Landmarks: Proper regions
    Labels: All interactive elements
    Live Regions: Status updates
    Descriptions: Complex interactions

  Screen Reader:
    Alt Text: All images
    Headings: Proper hierarchy
    Tables: Headers and captions
    Forms: Associated labels
```

---

## 4. BACKEND ARCHITECTURE

### 4.1 Service Layer Architecture

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

### 4.2 API Design

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

### 4.3 Database Schema

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

## 5. AI/ML ARCHITECTURE

### 5.1 AI Service Layer

```python
class AIService:
    def __init__(self):
        self.llm = GeminiClient()
        self.embeddings = EmbeddingService()
        self.rag = RAGPipeline()
        self.circuit_breaker = CircuitBreaker()
    
    @with_circuit_breaker
    async def generate_policy(
        self,
        framework: str,
        context: dict
    ) -> PolicyContent:
        # RAG-enhanced generation
        relevant_docs = await self.rag.retrieve(framework)
        
        prompt = self.build_prompt(
            framework=framework,
            context=context,
            examples=relevant_docs
        )
        
        response = await self.llm.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=8000
        )
        
        return self.parse_policy(response)
```

### 5.2 RAG Pipeline

```yaml
RAG Architecture:
  Embeddings:
    Model: text-embedding-004
    Dimensions: 768
    Storage: pgvector
    
  Retrieval:
    Method: Hybrid (semantic + keyword)
    Reranking: Cross-encoder
    Chunks: 512 tokens with 128 overlap
    
  Generation:
    Model: Gemini 2.5 Pro
    Context: 32K tokens
    Temperature: 0.3 for factual
    
  Quality:
    Hallucination: Fact verification
    Relevance: Cosine similarity > 0.7
    Citations: Source tracking
```

---

## 6. INFRASTRUCTURE

### 6.1 Deployment Architecture

```yaml
Production:
  Platform: AWS/GCP/Azure
  Containers: Docker + Kubernetes
  Database: Managed PostgreSQL
  Cache: Managed Redis
  CDN: CloudFlare
  
Scaling:
  Frontend:
    Strategy: Horizontal auto-scaling
    Min: 2 instances
    Max: 10 instances
    Metric: CPU > 70%
    
  Backend:
    Strategy: Horizontal + vertical
    Min: 3 instances
    Max: 20 instances
    Metric: Request latency
    
  Database:
    Read Replicas: 2
    Connection Pool: 100
    Backup: Daily + point-in-time
    
Monitoring:
  APM: Datadog/New Relic
  Logs: ELK Stack
  Metrics: Prometheus + Grafana
  Alerts: PagerDuty integration
```

### 6.2 CI/CD Pipeline

```yaml
Pipeline:
  Trigger: Push to main/develop
  
  Stages:
    - Lint:
        Frontend: ESLint + Prettier
        Backend: Ruff + Black
        
    - Test:
        Unit: 80% coverage minimum
        Integration: API contract tests
        E2E: Critical user journeys
        
    - Build:
        Docker: Multi-stage builds
        Optimization: Tree shaking
        
    - Security:
        SAST: SonarQube
        Dependencies: Snyk
        Secrets: GitLeaks
        
    - Deploy:
        Strategy: Blue-Green
        Rollback: Automatic on errors
        Health: Readiness probes
```

---

## 7. IMPLEMENTATION ROADMAP

### Phase 1: Security Foundation (Week 1)
```yaml
Day 1-2:
  - Fix authentication middleware
  - Implement JWT validation
  - Add rate limiting
  
Day 3-4:
  - Deploy auth pages (login/register/reset)
  - Test auth flows end-to-end
  
Day 5:
  - Security audit
  - Penetration testing
```

### Phase 2: User Experience (Week 2)
```yaml
Day 1-2:
  - User profile page
  - Team management UI
  
Day 3-4:
  - Onboarding wizard
  - Error boundaries
  
Day 5:
  - Accessibility fixes
  - Performance optimization
```

### Phase 3: Feature Enhancement (Week 3)
```yaml
Day 1-2:
  - Policy editor improvements
  - Assessment workflow optimization
  
Day 3-4:
  - Evidence management upgrade
  - Reporting enhancements
  
Day 5:
  - Integration testing
  - Production deployment
```

---

## 8. SHARDABLE TASKS

### 8.1 Security Tasks [PRIORITY: P0]
```yaml
SEC-001:
  Title: Fix authentication middleware bypass
  Effort: 4 hours
  Dependencies: None
  
SEC-002:
  Title: Implement JWT validation
  Effort: 8 hours
  Dependencies: SEC-001
  
SEC-003:
  Title: Add rate limiting middleware
  Effort: 6 hours
  Dependencies: SEC-001
  
SEC-004:
  Title: Implement CORS configuration
  Effort: 2 hours
  Dependencies: SEC-001
```

### 8.2 Frontend Tasks [PRIORITY: P1]
```yaml
FE-001:
  Title: Create user profile page
  Effort: 8 hours
  Dependencies: SEC-002
  
FE-002:
  Title: Build team management UI
  Effort: 12 hours
  Dependencies: FE-001
  
FE-003:
  Title: Implement onboarding wizard
  Effort: 16 hours
  Dependencies: SEC-002
  
FE-004:
  Title: Add global error boundaries
  Effort: 6 hours
  Dependencies: None
  
FE-005:
  Title: Fix accessibility violations
  Effort: 8 hours
  Dependencies: None
```

### 8.3 Backend Tasks [PRIORITY: P1]
```yaml
BE-001:
  Title: Create user profile endpoints
  Effort: 6 hours
  Dependencies: SEC-002
  
BE-002:
  Title: Build team management API
  Effort: 10 hours
  Dependencies: BE-001
  
BE-003:
  Title: Implement onboarding API
  Effort: 8 hours
  Dependencies: SEC-002
  
BE-004:
  Title: Add comprehensive logging
  Effort: 6 hours
  Dependencies: None
```

### 8.4 Performance Tasks [PRIORITY: P2]
```yaml
PERF-001:
  Title: Implement code splitting
  Effort: 8 hours
  Dependencies: None
  
PERF-002:
  Title: Add image optimization
  Effort: 4 hours
  Dependencies: None
  
PERF-003:
  Title: Implement virtual scrolling
  Effort: 6 hours
  Dependencies: None
  
PERF-004:
  Title: Add Redis caching layer
  Effort: 10 hours
  Dependencies: None
```

---

## 9. SUCCESS METRICS

### 9.1 Security Metrics
- Zero authentication bypasses
- < 0.1% unauthorized access attempts
- 100% HTTPS coverage
- < 5s token refresh time

### 9.2 Performance Metrics
- LCP < 2.5s
- FID < 100ms
- CLS < 0.1
- API response < 200ms p95
- 99.9% uptime

### 9.3 User Experience Metrics
- Onboarding completion > 80%
- User activation rate > 60%
- Feature adoption > 40%
- Support tickets < 5% MAU

### 9.4 Business Metrics
- Customer acquisition cost < £100
- Monthly churn < 5%
- NPS score > 50
- Revenue per user > £50/month

---

## 10. RISK MITIGATION

### 10.1 Technical Risks
```yaml
Risk: Authentication bypass exploitation
Mitigation: Immediate fix + security audit

Risk: Data breach via SQL injection
Mitigation: Parameterized queries + input validation

Risk: AI hallucination in compliance content
Mitigation: RAG + fact verification + human review

Risk: Performance degradation at scale
Mitigation: Caching + CDN + horizontal scaling
```

### 10.2 Business Risks
```yaml
Risk: Regulatory non-compliance
Mitigation: Legal review + automated compliance checks

Risk: Customer data loss
Mitigation: Daily backups + disaster recovery plan

Risk: Vendor lock-in (Gemini)
Mitigation: Abstraction layer + alternative providers

Risk: Team knowledge silos
Mitigation: Documentation + pair programming + rotation
```

---

## APPENDICES

### A. API Documentation
See: `/docs/api/README.md`

### B. Database Migrations
See: `/alembic/versions/`

### C. Security Policies
See: `/docs/security/policies.md`

### D. Deployment Guides
See: `/docs/deployment/`

---

**Document Status**: READY FOR SHARDING
**Last Updated**: January 2025
**Next Review**: February 2025
**Owner**: Architecture Team