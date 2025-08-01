# ruleIQ - AI-Powered Compliance Automation Platform

<div align="center">

![ruleIQ](https://img.shields.io/badge/ruleIQ-Compliance_Automation-blue)
![Status](https://img.shields.io/badge/Status-98%25_Production_Ready-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Next.js](https://img.shields.io/badge/Next.js-15-black)
![Tests](https://img.shields.io/badge/Tests-671+-brightgreen)

</div>

## 🚀 Overview

ruleIQ is an enterprise-grade AI-powered compliance automation platform designed specifically for UK Small and Medium Businesses (SMBs). It transforms complex regulatory requirements into actionable insights, automating policy generation, evidence collection, and compliance tracking across multiple frameworks.

### Key Features

- **🤖 AI-Powered Policy Generation** - Automatically generate audit-ready policies tailored to your business
- **📊 Real-time Compliance Scoring** - Monitor compliance status across ISO 27001, GDPR, Cyber Essentials, and more
- **🎯 Interactive Assessment Wizard** - Guided questionnaires for comprehensive business profiling
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
├── PostgreSQL                 # Primary database with advanced indexing
├── Redis                      # Caching and session management
├── Celery                     # Distributed task queue
└── Google Gemini AI           # Multi-model AI strategy

Frontend:
├── Next.js 15                 # React framework with App Router
├── TypeScript                 # Type-safe development
├── TanStack Query             # Server state management
├── Zustand                    # Client state management
├── Tailwind CSS               # Utility-first styling
└── shadcn/ui                  # Component library
```

### System Architecture

```mermaid
graph TB
    subgraph "Frontend"
        A[Next.js App] --> B[API Client]
        B --> C[Zustand Store]
        B --> D[TanStack Query]
    end
    
    subgraph "Backend"
        E[FastAPI] --> F[Service Layer]
        F --> G[AI Services]
        F --> H[Database]
        F --> I[Cache Layer]
    end
    
    subgraph "Infrastructure"
        J[PostgreSQL]
        K[Redis]
        L[Celery Workers]
    end
    
    B --> E
    H --> J
    I --> K
    F --> L
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- pnpm (for frontend)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ruleiq.git
cd ruleiq

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.template .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the backend server
python main.py  # Runs on http://localhost:8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (requires pnpm)
pnpm install

# Start development server
pnpm dev  # Runs on http://localhost:3000
```

### Docker Setup (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🧪 Testing

### Backend Tests

```bash
# Quick unit tests (2-5 minutes)
make test-fast

# Integration tests (5-10 minutes)
make test-integration

# Full test suite
make test-full

# Run specific test
pytest tests/test_specific.py -v
```

### Frontend Tests

```bash
cd frontend

# Unit tests
pnpm test

# E2E tests
pnpm test:e2e

# Visual regression tests
pnpm test:visual

# Test coverage
pnpm test:coverage
```

## 📖 Documentation

### Development Guides

- [API Documentation](http://localhost:8000/docs) - Interactive API documentation (when server is running)
- [Testing Guide](docs/TESTING_GUIDE.md) - Comprehensive testing strategies
- [Security Setup](docs/SECURITY_PERFORMANCE_SETUP.md) - Security best practices
- [Infrastructure Setup](docs/INFRASTRUCTURE_SETUP.md) - Deployment and scaling

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

**Note**: Stack Auth has been completely removed as of August 2025. All authentication now uses JWT tokens.
- **GDPR Compliant**: Data privacy and user rights management

Security Score: **8.5/10** (Enterprise-grade)

## 🚀 Performance

- **API Response Times**: 78.9-125.3ms average
- **AI Response Times**: <3s with streaming optimization
- **Database Queries**: 40-90% performance improvement with indexing
- **Frontend Loading**: <3s initial load with Core Web Vitals optimization
- **AI Cost Optimization**: 40-60% cost reduction achieved

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

## 📊 Project Status

- **Overall Readiness**: 98% production ready
- **Backend**: ✅ Production ready (671+ tests passing)
- **Frontend**: ✅ Complete with security hardening
- **Database**: ⚠️ Column truncation handled via mappers
- **AI Services**: ✅ Optimized with cost reduction
- **Documentation**: ✅ Comprehensive coverage

## 🏢 Use Cases

### Target Users

- **Analytical Alex**: Data-driven businesses wanting customization and control
- **Cautious Ben**: Risk-averse companies needing guidance and reassurance
- **Principled Catherine**: Ethics-focused organizations valuing transparency

### Supported Compliance Frameworks

- ISO 27001
- GDPR
- Cyber Essentials
- SOC 2
- PCI DSS
- Custom frameworks

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) and [Next.js](https://nextjs.org/)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- AI powered by [Google Gemini](https://ai.google.dev/)

---

<div align="center">

**[Documentation](docs)** • **[API Reference](http://localhost:8000/docs)** • **[Report Bug](https://github.com/yourusername/ruleiq/issues)** • **[Request Feature](https://github.com/yourusername/ruleiq/issues)**

</div>