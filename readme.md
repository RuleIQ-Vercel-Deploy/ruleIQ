# ruleIQ - AI Compliance Automated

<div align="center">

![ruleIQ Logo](frontend/public/placeholder-logo.svg)

**AI-powered compliance automation platform for UK SMBs**

[![Build Status](https://github.com/OmarA1-Bakri/Experiment/workflows/CI/badge.svg)](https://github.com/OmarA1-Bakri/Experiment/actions)
[![Test Coverage](https://img.shields.io/badge/coverage-80%25-green.svg)](./frontend/coverage)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

</div>

## 🎯 Overview

ruleIQ is a comprehensive AI-powered compliance automation platform designed specifically for UK Small and Medium Businesses (SMBs). The system guides businesses through compliance scoping, generates audit-ready policies, creates implementation plans, tracks evidence collection, and provides continuous readiness assessments.

### ✨ Key Features

- **🤖 AI-Powered Policy Generation** - Automatically generate comprehensive, audit-ready policies
- **📊 Real-time Compliance Scoring** - Monitor compliance status across multiple frameworks
- **📋 Interactive Assessment Wizard** - Guided questionnaires for business profiling
- **📁 Evidence Management** - Streamlined collection and approval workflows
- **📈 Executive Dashboards** - Visual reports and strategic roadmaps
- **🔗 Cloud Integration** - Automated evidence collection from AWS, Office 365, GitHub
- **♿ Accessibility First** - WCAG 2.2 AA compliant interface
- **📱 Mobile Responsive** - Optimized for all devices

## 🏗️ Architecture

### Technology Stack

#### Frontend
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod validation
- **Animations**: Framer Motion
- **Testing**: Vitest + Playwright + jest-axe

#### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Authentication**: JWT with refresh tokens
- **AI Integration**: OpenAI GPT-4
- **Task Queue**: Celery with Redis
- **Monitoring**: Prometheus + Grafana

#### Infrastructure
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Deployment**: Production-ready with health checks
- **Monitoring**: Comprehensive logging and metrics

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and pnpm
- **Python** 3.11+
- **PostgreSQL** 14+
- **Redis** 6+
- **Docker** (optional)
- **Serena MCP Server** (optional, for enhanced IDE assistance)

### Development Setup

#### Quick Start with Initialization Script

For a complete development environment setup including all services and Serena MCP integration:

```bash
# Clone the repository
git clone https://github.com/OmarA1-Bakri/Experiment.git
cd ruleIQ

# Run the initialization script
./scripts/init_dev_environment.sh
```

This script will:
- ✅ Check prerequisites
- ✅ Set up Python virtual environment
- ✅ Install all dependencies
- ✅ Start Docker services (PostgreSQL, Redis)
- ✅ Run database migrations
- ✅ Initialize Serena MCP Server for IDE assistance
- ✅ Run context change detection

To stop all services:
```bash
./scripts/stop_dev_environment.sh
```

#### Manual Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/OmarA1-Bakri/Experiment.git
   cd ruleIQ
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Setup database
   python scripts/init_db.py

   # Start backend
   uvicorn main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend

   # Install dependencies
   pnpm install

   # Start development server
   pnpm dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Docker Setup (Alternative)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🧪 Testing

ruleIQ features a comprehensive testing infrastructure with **100+ tests** across multiple testing types:

### Test Types & Coverage

- **✅ Unit Tests** - Component and service testing (80%+ coverage)
- **✅ Integration Tests** - API and workflow testing
- **✅ E2E Tests** - Complete user journey testing with Playwright
- **✅ Accessibility Tests** - WCAG 2.2 AA compliance with jest-axe
- **✅ Performance Tests** - Core Web Vitals and bundle size monitoring
- **✅ Visual Regression Tests** - Pixel-perfect UI consistency

### Running Tests

```bash
cd frontend

# Run all tests
pnpm test:all

# Unit tests with coverage
pnpm test:coverage

# E2E tests (all browsers)
pnpm test:e2e

# Accessibility tests
pnpm test:accessibility

# Performance tests
pnpm test:performance

# Visual regression tests
pnpm test:visual

# Bundle analysis
pnpm analyze:bundle
```

### Test Results Dashboard

- **Test Coverage**: 80%+ (statements, branches, functions)
- **E2E Coverage**: All critical user journeys
- **Accessibility**: WCAG 2.2 AA compliant
- **Performance**: Core Web Vitals within thresholds
- **Bundle Size**: <800KB total, <300KB first load

## 🎨 Core User Flows

### 1. 🚀 Onboarding & Business Assessment
- User registration with email verification
- Guided multi-step business profile wizard
- Industry-specific questionnaire
- Automated framework recommendations with scoring

### 2. 📝 Policy Generation
- Framework selection (GDPR, ISO 27001, SOC 2, etc.)
- AI-powered policy generation tailored to business
- Comprehensive policies, procedures, and tool recommendations
- Export capabilities (PDF, Word, HTML)

### 3. 📋 Control Implementation Planning
- Step-by-step implementation roadmaps
- Phase-based timelines with effort estimates
- Budget projections and resource allocation
- Role assignments and clear action items

### 4. 📁 Evidence Collection Management
- Interactive compliance checklists
- Automated evidence collection from cloud tools
- Upload and categorization workflows
- Approval processes with audit trails

### 5. 📊 Readiness Assessment & Monitoring
- Real-time compliance scoring across domains
- Gap analysis with prioritized recommendations
- Executive dashboards with visual reports
- Continuous monitoring and alerts

## 🔧 Development

### Project Structure

```
ruleIQ/
├── frontend/                 # Next.js frontend application
│   ├── app/                 # App Router pages and layouts
│   ├── components/          # React components
│   ├── lib/                 # Utilities and configurations
│   ├── tests/               # Comprehensive test suite
│   └── types/               # TypeScript definitions
├── api/                     # FastAPI backend
├── database/                # Database models and migrations
├── services/                # Business logic services
├── tests/                   # Backend tests
├── workers/                 # Background task workers
└── docs/                    # Documentation
```

### Code Quality

- **TypeScript**: Strict type checking enabled
- **ESLint**: Comprehensive linting rules
- **Prettier**: Consistent code formatting
- **Husky**: Pre-commit hooks for quality gates
- **Conventional Commits**: Standardized commit messages

### Performance Standards

- **Core Web Vitals**: LCP <2.5s, FID <100ms, CLS <0.1
- **Bundle Size**: <800KB total JavaScript
- **Accessibility**: WCAG 2.2 AA compliance
- **Test Coverage**: 80%+ across all modules

## 📚 Documentation

- **[Testing Guide](./frontend/tests/README.md)** - Comprehensive testing documentation
- **[Accessibility Guide](./frontend/tests/accessibility/MANUAL_TESTING_GUIDE.md)** - WCAG compliance procedures
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs
- **[Deployment Guide](./DEPLOYMENT.md)** - Production deployment instructions
- **[Contributing Guide](./CONTRIBUTING.md)** - Development guidelines

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   # Copy environment template
   cp .env.example .env

   # Configure production variables
   nano .env
   ```

2. **Build and Deploy**
   ```bash
   # Build frontend
   cd frontend && pnpm build

   # Deploy with Docker
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Health Checks**
   ```bash
   # Verify services
   curl http://localhost:3000/health
   curl http://localhost:8000/health
   ```

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/ruleiq
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# AI Integration
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details.

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** with tests
4. **Run the test suite** (`pnpm test:all`)
5. **Commit your changes** (`git commit -m 'feat: add amazing feature'`)
6. **Push to the branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Code Standards

- Follow TypeScript best practices
- Write comprehensive tests for new features
- Ensure accessibility compliance
- Maintain performance budgets
- Update documentation as needed

## 📊 Project Status

### Current Version: v1.0.0-beta

- ✅ **Frontend**: Production-ready with comprehensive testing
- ✅ **Backend**: Core API functionality complete
- ✅ **Testing**: 100+ tests across all types
- ✅ **Accessibility**: WCAG 2.2 AA compliant
- ✅ **Performance**: Optimized for Core Web Vitals
- ✅ **Documentation**: Comprehensive guides available


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check our comprehensive guides
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join our GitHub Discussions
- **Email**: support@ruleiq.com

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 integration
- **Vercel** for Next.js framework
- **shadcn/ui** for component library
- **Playwright** for E2E testing
- **The open-source community** for amazing tools and libraries

---

<div align="center">

**Built with ❤️ for UK SMBs**

[Website](https://ruleiq.com) • [Documentation](./docs) • [API](http://localhost:8000/docs) • [Support](mailto:support@ruleiq.com)

</div>
