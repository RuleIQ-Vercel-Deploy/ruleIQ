# RuleIQ - AI-Powered Compliance Automation Platform

[![CI Pipeline](https://github.com/OmarA1-Bakri/ruleIQ/actions/workflows/ci.yml/badge.svg)](https://github.com/OmarA1-Bakri/ruleIQ/actions/workflows/ci.yml)
[![Test Suite](https://github.com/OmarA1-Bakri/ruleIQ/actions/workflows/test-optimized.yml/badge.svg)](https://github.com/OmarA1-Bakri/ruleIQ/actions/workflows/test-optimized.yml)
[![SonarQube Analysis](https://github.com/OmarA1-Bakri/ruleIQ/actions/workflows/sonarqube.yml/badge.svg)](https://github.com/OmarA1-Bakri/ruleIQ/actions/workflows/sonarqube.yml)
[![Security Scan](https://github.com/OmarA1-Bakri/ruleIQ/actions/workflows/security.yml/badge.svg)](https://github.com/OmarA1-Bakri/ruleIQ/actions/workflows/security.yml)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ruleiq&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ruleiq)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ruleiq&metric=coverage)](https://sonarcloud.io/summary/new_code?id=ruleiq)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=ruleiq&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=ruleiq)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=ruleiq&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=ruleiq)

## Overview

RuleIQ is an AI-powered compliance automation platform designed for UK SMBs to streamline regulatory compliance, automate assessment workflows, and provide intelligent compliance guidance through advanced AI systems.

## 🚀 Quick Start

### Prerequisites
- Python 3.11.9
- Node.js 22.14.0
- PostgreSQL 15+
- Redis 7+
- Neo4j (optional for graph features)

### Development Setup

```bash
# Clone repository
git clone https://github.com/OmarA1-Bakri/ruleIQ.git
cd ruleIQ

# Backend setup
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Install additional dependencies (post-critical-fixes)
pip install pyotp freezegun aiofiles docker pydantic_ai graphiti_core

# Environment configuration
cp .env.example .env
# Edit .env with your configuration

# Run backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (in new terminal)
cd frontend
npm install
npm run dev
```

### Testing

```bash
# Run all tests (2,550 tests)
pytest

# Run with coverage
pytest --cov=api --cov=services --cov-report=html

# Run specific test categories
pytest tests/api/          # API tests
pytest tests/integration/  # Integration tests
pytest tests/unit/         # Unit tests
```

## 🏗️ Architecture

### Backend Stack
- **Framework**: FastAPI + Uvicorn
- **Database**: PostgreSQL (Neon) + Neo4j + Redis
- **AI Services**: OpenAI, Google AI, Anthropic, LangChain
- **Task Queue**: Celery with Redis broker
- **Security**: JWT + RBAC, Doppler secrets management

### Frontend Stack  
- **Framework**: Next.js 15 + React 19
- **Styling**: TailwindCSS + shadcn/ui
- **Authentication**: Stack Auth integration
- **State**: React Context + hooks
- **Testing**: Vitest + Playwright

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions (23 comprehensive workflows)
- **Monitoring**: Sentry + SonarCloud + custom metrics
- **Deployment**: Multi-stage production builds

## 📊 Project Status

### Build & Test Status
- ✅ **Import Errors**: 0 (down from 32 critical blockers)
- ✅ **Test Collection**: 2,550 tests successfully collected  
- ✅ **Build System**: Backend & frontend builds operational
- ✅ **Dependencies**: All critical packages installed

### Quality Metrics (SonarCloud)
- 🔴 **Test Coverage**: 0% (Target: 80%)
- 🔴 **Security Rating**: E (16 vulnerabilities)  
- 🔴 **Reliability Rating**: E (358 bugs)
- 🟡 **Code Duplication**: 5.9% (Target: <3%)

### Deployment Readiness
- ✅ **Staging**: Ready for immediate deployment
- ⚠️ **Production**: Requires security fixes and test coverage
- ✅ **CI/CD**: 23 comprehensive workflows operational

## 🔧 Development

### Environment Variables
See `.env.example` for comprehensive configuration including:
- Database URLs (PostgreSQL, Redis, Neo4j)
- AI service API keys (OpenAI, Google, Anthropic)
- UK compliance APIs (Companies House, ICO, FCA)
- Security settings (JWT, CORS, headers)
- Monitoring (Sentry, alerting webhooks)

### Code Quality
```bash
# Linting
ruff check .
ruff format .

# Type checking  
mypy api/

# Security scanning
bandit -r api/ services/
```

## 🛡️ Security

### Current Security Features
- JWT authentication with configurable algorithms
- RBAC (Role-Based Access Control)
- Security headers middleware
- CSP violation reporting
- Input validation (in progress)
- Rate limiting (configured)

### Security Improvements Needed
- 16 security vulnerabilities to address
- 369 security hotspots for review
- Enhanced input validation implementation
- SQL injection prevention hardening

## 🧪 Testing Strategy

### Test Structure
- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-service workflow testing  
- **API Tests**: Endpoint validation and security
- **Performance Tests**: Load testing and optimization
- **Security Tests**: Vulnerability and penetration testing

### Running Tests
```bash
# Quick test run
pytest -x --ff

# Full test suite with coverage
pytest --cov=api --cov=services --cov-report=html --maxfail=5

# Specific test categories
pytest tests/api/test_auth_endpoints.py      # Authentication tests
pytest tests/integration/                   # Integration workflows
pytest tests/security/                      # Security validation
```

## 📈 Monitoring & Observability

### Integrated Services
- **Application Monitoring**: Sentry error tracking
- **Code Quality**: SonarCloud continuous analysis
- **Performance**: Custom metrics collection  
- **Security**: Automated vulnerability scanning
- **Infrastructure**: Health checks and alerting

### Key Metrics Tracked
- API response times and error rates
- Database query performance
- Memory and CPU utilization
- Authentication success/failure rates
- Compliance assessment accuracy

## 🚀 Deployment

### Quick Deploy Commands
```bash
# Build containers
docker-compose build

# Start all services  
docker-compose up -d

# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Health check
curl http://localhost:8000/health
```

### Deployment Environments
- **Development**: `docker-compose.yml`
- **Staging**: `docker-compose.staging.yml`
- **Production**: `docker-compose.prod.yml`
- **Freemium**: `docker-compose.freemium.yml`

## 📚 Documentation

- `CLAUDE.md` - Development guidelines and conventions
- `SERENA.md` - AI coding assistant integration
- `AUDIT_PHASE3_INFRASTRUCTURE.md` - Infrastructure analysis
- `CRITICAL_FIXES.md` - Deployment blocker resolution
- `.github/workflows/` - 23 CI/CD workflow configurations

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Install dependencies and run tests
4. Make changes following code quality guidelines
5. Run full test suite: `pytest`
6. Create Pull Request with description

### Code Quality Requirements
- All tests must pass (2,550 tests)
- Code coverage above 80% for new features
- Security scan must pass
- Type hints required for Python functions
- ESLint/Prettier compliance for TypeScript

## 📞 Support

### Issues & Questions
- **Bug Reports**: Use GitHub Issues with bug template
- **Feature Requests**: Use GitHub Issues with feature template  
- **Security Issues**: Email security@ruleiq.com (private)
- **General Questions**: GitHub Discussions

### Development Support  
- **Code Analysis**: Integrated Serena MCP for intelligent code assistance
- **Task Management**: Archon MCP for project coordination
- **Quality Gates**: Automated SonarCloud analysis
- **Security**: Automated vulnerability scanning and reporting

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Last Updated**: September 5, 2025  
**Version**: 1.0.0  
**Build Status**: ✅ Operational (2,550 tests collected, 0 import errors)  
**Security Status**: ⚠️ 16 vulnerabilities pending resolution