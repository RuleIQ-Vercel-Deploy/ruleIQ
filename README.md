# ruleIQ - AI-Powered Compliance Automation Platform

<div align="center">

![ruleIQ](https://img.shields.io/badge/ruleIQ-Compliance_Automation-2C7A7B)
![Status](https://img.shields.io/badge/Status-Production_Ready-green)
![License](https://img.shields.io/badge/License-Proprietary-lightgrey)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Next.js](https://img.shields.io/badge/Next.js-15_+_Turbopack-black)
![Tests](https://img.shields.io/badge/Tests-1884+-brightgreen)
![AI Agents](https://img.shields.io/badge/AI_Agents-IQ_Agent_+_RAG-2C7A7B)

[![CI Pipeline](https://github.com/yourusername/ruleiq/workflows/CI%20Pipeline/badge.svg)](https://github.com/yourusername/ruleiq/actions/workflows/ci.yml)
[![Security Scan](https://github.com/yourusername/ruleiq/workflows/Security%20and%20Dependency%20Scanning/badge.svg)](https://github.com/yourusername/ruleiq/actions/workflows/security.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ruliq-compliance-platform&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ruliq-compliance-platform)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ruliq-compliance-platform&metric=coverage)](https://sonarcloud.io/summary/new_code?id=ruliq-compliance-platform)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=ruliq-compliance-platform&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=ruliq-compliance-platform)

</div>

## 🚀 Overview

ruleIQ is an enterprise-grade **agentic AI compliance automation platform** designed specifically for UK Small and Medium Businesses (SMBs). Unlike traditional compliance tools, ruleIQ implements intelligent agents that build ongoing relationships with users, evolving from helpers to trusted advisors to autonomous partners.

### 🤖 Agentic Intelligence Features

- **🧠 IQ Agent** - GraphRAG-powered compliance orchestrator with PPALE intelligence loop
- **🔍 RAG Self-Critic** - Automated fact-checking and response validation system
- **🕸️ LangGraph Workflows** - Multi-agent orchestration with state persistence
- **🧠 Memory Systems** - Conversation, knowledge graph, and pattern memory
- **📊 Trust Gradient** - Three-level progression: Helper → Advisor → Partner
- **🎯 Predictive Intelligence** - Proactive compliance monitoring and risk alerts

### Key Features

- **🤖 AI-Powered Policy Generation** - Automatically generate audit-ready policies tailored to your business
- **📊 Real-time Compliance Scoring** - Monitor compliance status across ISO 27001, GDPR, Cyber Essentials, and more
- **🎯 Conversational Assessments** - AI-driven replacement for traditional forms with follow-up intelligence
- **📁 Evidence Management** - Streamlined collection and approval workflows with automated validation
- **📈 Executive Dashboards** - Visual reports, strategic roadmaps, and actionable insights
- **☁️ Cloud Integration** - Automated evidence collection from AWS, Office 365, Google Workspace, GitHub
- **♿ Accessibility First** - WCAG 2.2 AA compliant interface ensuring inclusivity
- **📱 Mobile Responsive** - Optimized for all devices with progressive web app capabilities

## 🏗️ Architecture

### Tech Stack

```
Backend:
├── FastAPI (Python 3.8+)      # High-performance async API framework
├── PostgreSQL (Neon Cloud)    # Primary database with advanced indexing
├── Neo4j                       # GraphRAG knowledge base (20+ node types)
├── Redis                       # Caching and session management
├── Celery                      # Distributed task queue
├── LangGraph                   # Multi-agent orchestration framework
└── Google Gemini AI           # Multi-model AI strategy

Frontend:
├── Next.js 15 + Turbopack     # React framework with App Router & Turbopack bundler
├── TypeScript                 # Type-safe development
├── TanStack Query             # Server state management
├── Zustand                    # Client state management
├── Tailwind CSS (Teal Theme)  # Utility-first styling with teal design system
└── shadcn/ui                  # Component library
```

### Agentic System Architecture

```mermaid
graph TB
    subgraph "Frontend"
        A[Next.js + Turbopack] --> B[API Client]
        B --> C[Zustand Store]
        B --> D[TanStack Query]
    end
    
    subgraph "Agentic Layer"
        E[IQ Agent] --> F[GraphRAG Engine]
        E --> G[RAG Self-Critic]
        E --> H[LangGraph Workflow]
        F --> I[Neo4j Knowledge Base]
        H --> J[PostgreSQL State]
    end
    
    subgraph "Backend Services"
        K[FastAPI Router] --> L[Service Layer]
        L --> M[Memory Manager]
        L --> N[Pattern Recognition]
        L --> O[Trust Tracker]
    end
    
    subgraph "Infrastructure"
        P[Neon PostgreSQL]
        Q[Redis Cache]
        R[Celery Workers]
    end
    
    B --> K
    E --> L
    J --> P
    N --> Q
    L --> R
```

## 📅 Recent Updates (January 2025)

### ✅ CI/CD Infrastructure Complete
- GitHub Actions workflows for CI/CD
- Automated testing on PR/push
- SonarCloud integration for code quality
- Docker build and security scanning
- Blue-green deployments for production
- Emergency rollback capabilities

### ✅ API Standardization Complete
- All endpoints now follow consistent `/api/v1/` pattern
- Frontend API client automatically handles versioning
- Resolved all "APIError: Not Found" issues
- [Full API Documentation](docs/API_ENDPOINTS_DOCUMENTATION.md) updated

### 🎨 Teal Design System Migration (65% Complete)
- Marketing page fully migrated to teal theme
- Dashboard components using new design tokens
- Legacy purple/cyan colors being phased out

### 🔐 Authentication System
- JWT-only authentication (Stack Auth removed)
- Bulletproof security with token blacklisting
- RBAC middleware for granular permissions

### 🤖 AI Agent Enhancements
- IQ Agent with GraphRAG knowledge base
- RAG Self-Critic for hallucination prevention
- LangGraph multi-agent orchestration

## 🧠 Agentic Intelligence

### IQ Agent - Core Intelligence Loop (PPALE)

1. **PERCEIVE** - Query compliance posture from Neo4j knowledge graph
2. **PLAN** - Risk-weighted prioritization with enforcement precedent analysis
3. **ACT** - Execute compliance controls and update graph
4. **LEARN** - Pattern recognition and effectiveness analysis
5. **REMEMBER** - Memory consolidation and knowledge building

### Trust Gradient Implementation

#### Level 1: Transparent Helper (Current)
- Shows all reasoning and confidence levels
- Asks for confirmation before actions
- Explains decisions with transparent logic

#### Level 2: Trusted Advisor (6 months)
- Makes confident suggestions based on patterns
- Learns user preferences over time
- Predicts compliance needs proactively

#### Level 3: Autonomous Partner (12 months)
- Takes initiative with high-confidence actions
- Manages workflows autonomously
- Prevents issues before they occur

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL 13+ (or Neon cloud)
- Neo4j 5.0+ (for GraphRAG)
- Redis 6+
- pnpm (for frontend)

### One-Command Start

```bash
# Clone and start everything
git clone https://github.com/yourusername/ruleiq.git
cd ruleiq

# Make the script executable (first time only)
chmod +x ./start

# Start full development environment
./start
```

Prerequisites:
- Python 3.11+ available as python3
- Node.js 18+ with pnpm (recommended via Corepack)
  - If pnpm is not installed, run: corepack enable && corepack prepare pnpm@latest --activate

The start script will:
- Create a Python virtual environment if missing
- Install backend dependencies on first run
- Install frontend dependencies with pnpm using the existing lockfile
- Start both backend (http://localhost:8000) and frontend (http://localhost:3000)

### Manual Setup

#### Backend Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (auto-detects missing packages)
pip install -r requirements.txt

# Set up environment variables
# 🔐 SECRETS MANAGEMENT (PRODUCTION-READY)
# Option 1: Doppler (Recommended for production)
doppler run -- python main.py    # All secrets auto-injected from Doppler

# Option 2: Local development with .env
cp .env.template .env
# Edit .env with your configuration including:
# - DATABASE_URL (Neon PostgreSQL)
# - NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
# - GOOGLE_AI_API_KEY (for Gemini AI)
# - REDIS_URL
# - JWT_SECRET_KEY

# Initialize databases
python database/init_db.py      # PostgreSQL schema
python services/neo4j_service.py  # Neo4j knowledge graph

# Start the backend server
python main.py  # Runs on http://localhost:8000
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
pnpm install

# Start development server with Turbopack (faster builds)
pnpm dev  # Runs on http://localhost:3000 with --turbo flag
```

### Docker Setup (Production)

```bash
# Start all services including Neo4j
docker-compose up -d

# View logs
docker-compose logs -f iq_agent  # IQ Agent logs
docker-compose logs -f backend   # FastAPI logs
docker-compose logs -f frontend  # Next.js logs

# Stop services
docker-compose down
```

## 📡 API Documentation

### API Standardization
All API endpoints now follow a consistent `/api/v1/` pattern:
- **Base URL**: `http://localhost:8000/api/v1/`
- **Documentation**: `http://localhost:8000/docs`
- **Frontend Integration**: Automatic endpoint normalization in API client

See [API Documentation](docs/API_ENDPOINTS_DOCUMENTATION.md) for complete endpoint reference.

## 🧪 Testing

### Backend Tests (1884+ passing)

```bash
# Quick unit tests (2-5 minutes)
make test-fast

# AI agent tests
pytest -m ai -v

# RAG system tests
pytest tests/test_rag_self_critic.py -v

# Integration tests (5-10 minutes)
make test-integration

# Full test suite including agentic systems
make test-full

# Test specific component
pytest tests/unit/services/test_iq_agent.py -v
```

### Frontend Tests

```bash
cd frontend

# Unit tests
pnpm test

# Test with new teal theme
NEXT_PUBLIC_USE_NEW_THEME=true pnpm test

# E2E tests with Playwright
pnpm test:e2e

# Visual regression tests
pnpm test:visual

# Test coverage
pnpm test:coverage
```

### Agentic System Testing

```bash
# Quick IQ Agent fact-check (2-5 seconds)
python services/rag_self_critic.py quick-check --query "GDPR applies to UK businesses"

# Comprehensive fact-check (10-30 seconds)
python services/rag_self_critic.py fact-check --query "ISO 27001 certification requirements"

# Self-critique analysis (15-45 seconds)
python services/rag_self_critic.py critique --query "Complex compliance scenario"
```

## 📖 Documentation

### Core Documentation

- [**Agentic Systems Overview**](frontend/AGENTIC_SYSTEMS_OVERVIEW.md) - Complete guide to IQ Agent, RAG Self-Critic, and LangGraph workflows
- [API Documentation](http://localhost:8000/docs) - Interactive API documentation
- [Testing Guide](docs/TESTING_GUIDE.md) - Comprehensive testing strategies
- [Security Setup](docs/SECURITY_PERFORMANCE_SETUP.md) - Security best practices

### Frontend Documentation

- [**Frontend Design Plan**](frontend/FRONTEND_DESIGN_COMPLIANCE_PLAN.md) - Teal design system migration
- [Frontend Context](docs/context/FRONTEND_CONTEXT.md) - UI/UX architecture
- [Design System Guide](frontend/design_framework.md) - Component library and patterns(docs/INFRASTRUCTURE_SETUP.md) - Deployment and scaling

### Architecture Documentation

- [Architecture Context](docs/context/ARCHITECTURE_CONTEXT.md) - System design and patterns
- [API Context](docs/context/API_CONTEXT.md) - API design and endpoints
- [Database Context](docs/context/DATABASE_CONTEXT.md) - Schema and optimization
- [Frontend Context](docs/context/FRONTEND_CONTEXT.md) - UI/UX architecture
- [AI Services Context](docs/context/AI_SERVICES_CONTEXT.md) - AI integration details

## 🔐 Security

ruleIQ implements enterprise-grade security measures:

- **Authentication**: JWT-only system with HS256 algorithm (Stack Auth removed)
  - 30-minute access tokens with 7-day refresh tokens
  - bcrypt password hashing with automatic salt generation
  - Redis-based token blacklisting for secure logout
- **Authorization**: Role-based access control (RBAC) with granular permissions
- **Encryption**: AES-GCM for sensitive data, TLS 1.3 for transport
- **Input Validation**: Comprehensive whitelist-based validation on all endpoints
- **Rate Limiting**: Multi-tier protection (5/min auth, 100/min general, 20/min AI)
- **OWASP Compliance**: Regular security audits and penetration testing

### Authentication Endpoints

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/logout` - Secure logout

### IQ Agent Endpoints

- `POST /api/v1/iq/query` - Process compliance query with agent
- `GET /api/v1/iq/memory/retrieve` - Get contextual memories
- `POST /api/v1/iq/memory/store` - Store interaction memory
- `GET /api/v1/iq/health` - Agent system health check

**Note**: Stack Auth has been completely removed as of August 2025. All authentication now uses JWT tokens.
- **GDPR Compliant**: Data privacy and user rights management
- **AI Safety**: RAG Self-Critic prevents hallucinations with 85%+ confidence thresholds

Security Score: **8.5/10** (Enterprise-grade)

## 🚀 Performance

### Response Times
- **API Endpoints**: 78.9-125.3ms average (<200ms SLO)
- **IQ Agent Quick Check**: ~2-5 seconds
- **Standard AI Queries**: ~10-30 seconds with streaming
- **Complex Analysis**: ~15-45 seconds
- **Database Queries**: 40-90% performance improvement with indexing

### Frontend Performance
- **Initial Load**: <3s with Turbopack optimization
- **Hot Reloads**: ~200ms (60% faster with Turbopack)
- **Core Web Vitals**: All metrics in green
- **Teal Theme Bundle**: <5% size increase over legacy theme

### AI Cost Optimization
- **40-60% cost reduction** through intelligent caching
- Circuit breaker pattern prevents API overuse
- Fallback responses for system resilience

## 🎨 Design System

### Teal Theme Migration (65% Complete)

```css
/* Primary Teal Palette */
--teal-600: #2C7A7B;   /* PRIMARY BRAND */
--teal-700: #285E61;   /* Hover states */
--teal-50: #E6FFFA;    /* Light backgrounds */
--teal-300: #4FD1C5;   /* Bright accents */
```

### Migration Status
- ✅ Foundation established with design tokens
- ✅ Core components (buttons, navigation, forms)
- 🔄 Color migration (removing purple/cyan legacy)
- 📋 Advanced UI patterns (loading states, modals)
- 📋 Visual regression testing

### Theme Testing
```bash
# Test with new teal theme
NEXT_PUBLIC_USE_NEW_THEME=true pnpm dev
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Quality

```bash
# Backend
ruff check .       # Linting
ruff format .      # Formatting

# Frontend
pnpm lint          # ESLint
pnpm format        # Prettier
pnpm typecheck     # TypeScript
```

## 📊 Project Status (January 2025)

### Overall Readiness: 98% Production Ready

- **Backend**: ✅ Production ready (1884+ tests passing, <200ms SLO)
- **Frontend**: ✅ Complete with Turbopack + teal design system
- **Agentic Systems**: ✅ IQ Agent, RAG Self-Critic, LangGraph deployed
- **CI/CD**: ✅ Complete GitHub Actions pipelines with SonarCloud
- **Database**: ⚠️ Column truncation handled via field mappers
- **AI Services**: ✅ Optimized with 40-60% cost reduction
- **Documentation**: ✅ Comprehensive coverage including agentic systems
- **Security**: ✅ 8.5/10 enterprise-grade (OWASP compliant)

### Recent Achievements

- ✅ **CI/CD Infrastructure** - Complete GitHub Actions with blue-green deployment
- ✅ **Test Infrastructure** - 1884+ tests with full coverage reporting
- ✅ **Agentic Transformation Complete** - Full IQ Agent deployment with GraphRAG
- ✅ **RAG Self-Critic Integration** - Automated fact-checking with 85%+ confidence
- ✅ **Turbopack Integration** - 60% faster development builds
- ✅ **Teal Design System** - Modern, accessible UI with 65% migration complete
- ✅ **Memory Systems** - Conversation, knowledge graph, and pattern memory
- ✅ **Trust Gradient Implementation** - Helper → Advisor → Partner progression

### Active Development

- 🔄 **Conversational Assessments** - Replacing forms with AI conversations
- 🔄 **Predictive Intelligence** - Proactive compliance monitoring
- 🔄 **Advanced Pattern Recognition** - Learning from user interactions
- 🔄 **Full Teal Migration** - Completing design system transition

## 🏢 Use Cases

### Target Users

- **Analytical Alex**: Data-driven businesses wanting AI-powered insights and control
- **Cautious Ben**: Risk-averse companies needing AI guidance and reassurance
- **Principled Catherine**: Ethics-focused organizations valuing AI transparency

### Supported Compliance Frameworks

- ISO 27001 (with AI gap analysis)
- GDPR (with automated assessment)
- Cyber Essentials (with evidence automation)
- SOC 2 (with control mapping)
- PCI DSS (with risk scoring)
- Custom frameworks (with AI adaptation)

### Agentic Capabilities

- **Autonomous Policy Updates** - IQ Agent maintains policies based on regulatory changes
- **Predictive Risk Alerts** - Proactive identification of compliance gaps
- **Intelligent Evidence Collection** - Automated gathering from integrated systems
- **Contextual Recommendations** - Personalized guidance based on business patterns
- **Continuous Learning** - System improves with every user interaction

## 📝 License

This software is proprietary and provided under a restrictive license. All rights reserved.  
You may evaluate and test internally, but production or commercial use requires a separate commercial agreement.  
See the full terms in the [LICENSE](LICENSE) file. For licensing inquiries, contact legal@ruleiq.com.  
Additional details and CI publication guard instructions: [docs/licensing.md](docs/licensing.md).

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) and [Next.js](https://nextjs.org/)
- Agentic intelligence powered by [LangGraph](https://langchain-ai.github.io/langgraph/)
- GraphRAG implementation using [Neo4j](https://neo4j.com/)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- AI powered by [Google Gemini](https://ai.google.dev/)(https://ai.google.dev/)

---

<div align="center">

**[Documentation](docs)** • **[Agentic Overview](frontend/AGENTIC_SYSTEMS_OVERVIEW.md)** • **[API Reference](http://localhost:8000/docs)** • **[Report Bug](https://github.com/yourusername/ruleiq/issues)** • **[Request Feature](https://github.com/yourusername/ruleiq/issues)**

*"We're not just adding AI features to existing tools. We're fundamentally reimagining compliance management as an ongoing partnership between humans and intelligent agents."*

</div>