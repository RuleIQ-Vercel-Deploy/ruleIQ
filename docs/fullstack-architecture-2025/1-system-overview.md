# 1. SYSTEM OVERVIEW

## 1.1 Platform Vision
RuleIQ is an AI-powered compliance automation platform designed for UK SMBs, simplifying regulatory compliance through intelligent automation, assessment workflows, and evidence management.

## 1.2 Architecture Pattern
- **Pattern**: Microservices-ready monolith with clear service boundaries
- **Approach**: Domain-driven design with vertical slice architecture
- **Scale Strategy**: Horizontal scaling with future service extraction capability

## 1.3 Technology Stack

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
