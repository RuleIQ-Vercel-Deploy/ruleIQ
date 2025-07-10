# ruleIQ Project Overview

## Purpose
ruleIQ is a comprehensive AI-powered compliance automation platform designed specifically for UK Small and Medium Businesses (SMBs). The system guides businesses through compliance scoping, generates audit-ready policies, creates implementation plans, tracks evidence collection, and provides continuous readiness assessments.

## Key Features
- **AI-Powered Policy Generation** - Automatically generate comprehensive, audit-ready policies
- **Real-time Compliance Scoring** - Monitor compliance status across multiple frameworks
- **Interactive Assessment Wizard** - Guided questionnaires for business profiling
- **Evidence Management** - Streamlined collection and approval workflows
- **Executive Dashboards** - Visual reports and strategic roadmaps
- **Cloud Integration** - Automated evidence collection from AWS, Office 365, GitHub
- **Accessibility First** - WCAG 2.2 AA compliant interface
- **Mobile Responsive** - Optimized for all devices

## Target Users
- **Alex (Analytical)**: Data-driven, wants customization and control
- **Ben (Cautious)**: Risk-averse, needs guidance and reassurance  
- **Catherine (Principled)**: Ethics-focused, values transparency and audit trails

## Architecture
- **Backend**: FastAPI (Python) with PostgreSQL database
- **Frontend**: Next.js 15 with TypeScript (separate codebase)
- **AI Integration**: OpenAI GPT-4 and Google Generative AI
- **Task Queue**: Celery with Redis
- **Testing**: 716+ tests across multiple types
- **Monitoring**: Prometheus + Grafana
- **Containerization**: Docker + Docker Compose