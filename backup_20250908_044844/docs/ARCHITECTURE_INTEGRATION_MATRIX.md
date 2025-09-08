# RuleIQ Agentic Integration Point Matrix

## Service ↔ Service Integration Points

| Source Service | Target Service | Integration Type | Data Flow | Trust Level Required | Risk Level |
|----------------|----------------|------------------|-----------|---------------------|------------|
| **Agent Orchestrator** | Trust Manager | Synchronous API | Trust level queries/updates | N/A | Low |
| **Trust Manager** | Session Manager | Event-driven | Trust progression events | N/A | Medium |
| **Session Manager** | Context Storage | Async writes | User interaction history | 0+ | Low |
| **RAG System** | Self-Critic | Pipeline | Response validation | 1+ | High |
| **Self-Critic** | Agent Orchestrator | Callback | Confidence scores | 1+ | Medium |
| **Smart Evidence Collector** | RAG System | Batch processing | Evidence classification | 2+ | Medium |
| **Compliance Monitor** | Agent Orchestrator | Event-driven | Regulatory change alerts | 2+ | High |
| **Policy Generator** | Trust Manager | Permission check | Auto-update authorization | 3 | High |

## API ↔ UI Integration Points

| Frontend Component | Backend Endpoint | Method | Trust Level | Real-time | Caching |
|-------------------|------------------|--------|-------------|-----------|---------|
| **Conversational UI** | `/api/v1/agents/chat` | WebSocket | 0+ | Yes | Session |
| **Trust Dashboard** | `/api/v1/trust/status` | GET | 0+ | Yes | 30s |
| **Agent Settings** | `/api/v1/agents/config` | PUT | 1+ | No | None |
| **Compliance Monitor** | `/api/v1/compliance/stream` | SSE | 2+ | Yes | None |
| **Policy Manager** | `/api/v1/policies/auto` | POST | 3 | No | None |
| **Evidence Collector** | `/api/v1/evidence/smart` | POST | 2+ | No | 5min |
| **Assessment Flow** | `/api/v1/assessments/conversational` | WebSocket | 0+ | Yes | Session |

## External Service Dependencies

| External Service | Purpose | Criticality | Fallback Strategy | SLA Requirement |
|-----------------|---------|-------------|-------------------|-----------------|
| **Google AI API** | Primary AI model | Critical | Circuit breaker → Local model | 99.9% |
| **Neon PostgreSQL** | Primary database | Critical | Read replicas | 99.95% |
| **Redis Cluster** | Session/cache | High | Local cache fallback | 99.5% |
| **Regulatory APIs** | Compliance updates | Medium | Cached responses | 95% |
| **Notification Services** | User alerts | Low | Email fallback | 90% |

## Data Synchronization Points

| Data Type | Primary Store | Secondary Store | Sync Method | Consistency Model |
|-----------|---------------|-----------------|-------------|-------------------|
| **User Context** | PostgreSQL | Redis | Event-driven | Eventually consistent |
| **Trust Levels** | PostgreSQL | Redis | Synchronous | Strong consistency |
| **Agent Sessions** | Redis | PostgreSQL | Async batch | Eventually consistent |
| **Compliance Data** | PostgreSQL | Vector Store | Pipeline | Eventually consistent |
| **Policy Documents** | PostgreSQL | File Storage | Event-driven | Strong consistency |

## Security Integration Points

| Component | Authentication | Authorization | Data Encryption | Audit Logging |
|-----------|----------------|---------------|-----------------|---------------|
| **Agent Orchestrator** | JWT validation | RBAC + Trust level | TLS 1.3 | All actions |
| **Trust Manager** | Service token | Internal ACL | AES-256 | Trust changes |
| **RAG System** | API key | Rate limiting | At rest + transit | Query logs |
| **Self-Critic** | Internal auth | Validation only | Transit only | Validation results |
| **External APIs** | OAuth 2.0 | Scoped tokens | Provider TLS | API calls |

## Performance Integration Requirements

| Integration Point | Latency Target | Throughput Target | Monitoring | Alerting |
|-------------------|----------------|-------------------|------------|----------|
| **Agent ↔ RAG** | <200ms | 100 req/s | Response time | >500ms |
| **UI ↔ Agent** | <100ms | 50 concurrent | WebSocket health | Connection drops |
| **Trust ↔ Session** | <50ms | 200 req/s | Cache hit rate | <80% hit rate |
| **DB ↔ Cache** | <10ms | 1000 req/s | Query performance | >100ms queries |
| **External APIs** | <2s | 10 req/s | Circuit breaker | 3 failures |

## Error Handling & Resilience

| Failure Scenario | Detection Method | Recovery Strategy | User Impact | Recovery Time |
|------------------|------------------|-------------------|-------------|---------------|
| **AI API failure** | Circuit breaker | Fallback model | Degraded responses | <30s |
| **Database failure** | Health check | Read replica | Read-only mode | <60s |
| **Cache failure** | Connection timeout | Direct DB queries | Slower responses | <10s |
| **Agent crash** | Process monitor | Auto-restart | Session recovery | <15s |
| **Trust corruption** | Validation check | Reset to level 0 | Trust rebuild | Immediate |

## Deployment Dependencies

| Component | Deployment Order | Dependencies | Health Check | Rollback Trigger |
|-----------|------------------|--------------|--------------|------------------|
| **Database migrations** | 1 | None | Schema validation | Migration failure |
| **Core API services** | 2 | Database | /health endpoint | 3 failed checks |
| **Agent orchestrator** | 3 | Core API | Agent creation test | Service unavailable |
| **RAG system** | 4 | Vector store | Query test | Response failure |
| **Frontend** | 5 | All backend | Page load test | Build failure |

## Monitoring & Observability

| Integration Layer | Metrics | Logs | Traces | Alerts |
|-------------------|---------|------|--------|--------|
| **API Gateway** | Request rate, latency | Access logs | Request traces | Rate limits |
| **Agent Layer** | Trust progression, session duration | Agent decisions | User journeys | Trust failures |
| **AI Services** | Model performance, costs | AI responses | AI call chains | High costs |
| **Data Layer** | Query performance, cache hits | Data changes | DB transactions | Slow queries |
| **External** | API availability, response times | API errors | External calls | Service outages |
