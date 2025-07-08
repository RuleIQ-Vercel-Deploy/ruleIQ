# ruleIQ Context Documentation

## Overview

This directory contains comprehensive context documentation for the ruleIQ compliance automation platform. The documentation provides deep architectural understanding, component relationships, and implementation context for all major platform areas.

## Context Documentation Structure

### **Core Context Documents**

#### **[CONTEXT_SPECIFICATION.md](./CONTEXT_SPECIFICATION.md)**
Master specification defining context management standards, documentation formats, and maintenance protocols for the entire platform.

#### **[ARCHITECTURE_CONTEXT.md](./ARCHITECTURE_CONTEXT.md)**
High-level system architecture overview including technology stack, design patterns, development status, and architectural decisions.

### **Component-Specific Context**

#### **[AI_SERVICES_CONTEXT.md](./AI_SERVICES_CONTEXT.md)**
Comprehensive documentation of AI services including Google Gemini integration, multi-model strategy, circuit breaker patterns, and the current Week 1 Day 3 optimization project.

#### **[DATABASE_CONTEXT.md](./DATABASE_CONTEXT.md)** ⚠️ **CRITICAL ISSUES**
Database schema documentation highlighting critical column naming issues, missing constraints, and required migrations for production readiness.

#### **[FRONTEND_CONTEXT.md](./FRONTEND_CONTEXT.md)** ⚠️ **SECURITY ISSUES**
Frontend architecture including React/Next.js implementation, component organization, state management, and critical security vulnerabilities requiring immediate attention.

#### **[API_CONTEXT.md](./API_CONTEXT.md)**
REST API documentation covering endpoint organization, authentication, rate limiting, request/response patterns, and security considerations.

#### **[TESTING_CONTEXT.md](./TESTING_CONTEXT.md)**
Comprehensive testing infrastructure including backend/frontend test suites, AI accuracy validation, performance testing, and security testing strategies.

## Quick Reference

### **Project Status Overview**
- **Overall Readiness**: 95% production ready
- **Backend**: ✅ Production ready (597 tests, ~98% passing)
- **Frontend**: ✅ Business profile complete, assessment workflow in progress
- **Database**: ❌ Critical schema issues requiring fixes
- **AI Services**: 🔄 Week 1 Day 3 optimization in progress
- **Security**: ⚠️ Critical vulnerabilities requiring immediate attention

### **Critical Issues Requiring Immediate Action**

#### **🔴 CRITICAL - Database Schema (Must Fix Before Production)**
```sql
-- Column name truncation breaking ORM relationships
ALTER TABLE business_profiles RENAME COLUMN handles_persona TO handles_personal_data;
ALTER TABLE business_profiles RENAME COLUMN processes_payme TO processes_payments;
ALTER TABLE assessment_sessions RENAME COLUMN business_profil TO business_profile_id;
```
**Impact**: Database operations failing, API field mapping complexity  
**Files**: `database/business_profile.py`, `api/routers/business_profiles.py`  
**Timeline**: Week 1 - Highest Priority

#### **🔴 CRITICAL - Frontend Security (Authentication Vulnerability)**
```typescript
// VULNERABLE: Unencrypted tokens in localStorage
localStorage.setItem("ruleiq_auth_token", tokens.access_token);

// REQUIRED: Secure token storage
// 1. HTTP-only cookies for refresh tokens
// 2. Memory-only access tokens
// 3. Token encryption for localStorage fallback
```
**Impact**: XSS attacks can steal authentication tokens  
**Files**: `frontend/lib/stores/auth.store.ts`  
**Timeline**: Week 1 - Security Risk

#### **🔴 CRITICAL - API Input Validation**
```python
# DANGEROUS: Dynamic attribute setting without validation
for field, value in update_data.items():
    setattr(item, field, value)  # No validation or sanitization

# REQUIRED: Whitelist validation
ALLOWED_FIELDS = {'title', 'description', 'status'}
validated_data = {k: sanitize(v) for k, v in data.items() if k in ALLOWED_FIELDS}
```
**Impact**: Potential injection attacks and data integrity issues  
**Files**: `services/evidence_service.py`  
**Timeline**: Week 1 - Security Risk

### **Architecture Strengths**

#### **✅ Excellent Foundations**
- **Modern Tech Stack**: FastAPI + Next.js 15 + PostgreSQL + Redis
- **Comprehensive AI Integration**: 25+ AI modules with circuit breaker patterns
- **Testing Excellence**: 756 total tests (597 backend + 159 frontend)
- **Performance Optimization**: Caching, indexing, connection pooling
- **Security Infrastructure**: JWT auth, rate limiting, CORS protection

#### **✅ Advanced Features**
- **AI Optimization Project**: Multi-model strategy targeting 40-60% cost reduction
- **Real-time Capabilities**: WebSocket chat, streaming AI responses
- **Component Architecture**: 90+ reusable UI components with shadcn/ui
- **State Management**: Zustand + TanStack Query for optimal performance
- **Production Infrastructure**: Docker, Celery workers, monitoring

### **Development Context**

#### **Current Focus: Week 1 Day 3 - AI SDK Optimization**
**Project**: Google Gen AI SDK Comprehensive Optimization (40+ hours)  
**Goals**: 
- 40-60% cost reduction through intelligent model selection
- 80% latency improvement via streaming and optimization
- Enhanced reliability with advanced circuit breaker patterns

**Implementation Areas**:
- 🔄 Multi-model strategy (Gemini 2.5 Pro/Flash/Light, Gemma 3)
- 🔄 Streaming responses for real-time user feedback
- 🔄 Function calling for structured AI interactions
- 🔄 Advanced caching with context awareness

#### **6-Week Production Roadmap**
- **Week 1**: AI Integration Completion (Days 1-5) - 🔄 IN PROGRESS
- **Week 2**: Advanced Features & Analytics
- **Week 3**: User Experience & Performance
- **Week 4**: Testing & Quality Assurance
- **Week 5**: Security & Compliance
- **Week 6**: Production Deployment

### **Quality Metrics**

#### **Test Coverage Summary**
```
Total Tests: 756
├── Backend: 597 tests (~98% passing)
│   ├── Unit Tests: 450+ (service layer, models)
│   ├── Integration Tests: 100+ (API, database)
│   └── AI Tests: 47 (accuracy, circuit breaker)
└── Frontend: 159 tests
    ├── Component Tests: 65 (UI components)
    ├── Store Tests: 22 (100% passing)
    ├── E2E Tests: 28 (user journeys)
    └── Integration Tests: 38 (user flows)
```

#### **Performance Benchmarks**
- **API Response Times**: <500ms for standard operations
- **AI Response Times**: 15-30s (optimizing to <3s with streaming)
- **Database Queries**: Optimized with comprehensive indexing
- **Frontend Loading**: <3s target with optimization in progress

#### **Security Assessment**
- **Backend Security**: 7/10 (rate limiting, auth, some input validation gaps)
- **Frontend Security**: 5/10 (authentication vulnerabilities, missing CSRF)
- **Database Security**: 6/10 (good design, missing constraints)
- **Overall Security**: 6/10 - requires immediate attention to critical issues

## Context Usage Guidelines

### **For New Developers**
1. **Start with**: [ARCHITECTURE_CONTEXT.md](./ARCHITECTURE_CONTEXT.md) for system overview
2. **Then review**: Component-specific context for your work area
3. **Reference**: [TESTING_CONTEXT.md](./TESTING_CONTEXT.md) for testing strategies
4. **Follow**: [CONTEXT_SPECIFICATION.md](./CONTEXT_SPECIFICATION.md) for documentation standards

### **For Architecture Decisions**
1. **Review**: Related context documents for impact analysis
2. **Update**: Affected context documentation with changes
3. **Validate**: Changes against context quality metrics
4. **Document**: Architecture Decision Records (ADRs) in context

### **For Production Deployment**
1. **Verify**: All critical issues resolved (database, security, TypeScript)
2. **Validate**: Test coverage and performance benchmarks met
3. **Review**: Security assessment and penetration testing complete
4. **Confirm**: Context documentation updated for production configuration

## Context Maintenance

### **Update Frequency**
- **Active Development Areas**: Weekly updates (currently AI services)
- **Stable Components**: Monthly reviews
- **Critical Issues**: Immediate updates as issues are resolved
- **Architecture Changes**: Update within 48 hours of implementation

### **Quality Validation**
- **Accuracy**: Context matches implementation (validated in reviews)
- **Completeness**: All major components documented
- **Freshness**: Last update timestamps tracked
- **Usability**: Developer feedback incorporated

### **Change Impact Tracking**
- **High Impact**: Database schema, authentication, API contracts
- **Medium Impact**: Component architecture, testing infrastructure
- **Low Impact**: Documentation updates, minor optimizations

## Automated Monitoring

A context monitoring system (`scripts/context_monitor.py`) automatically detects changes that affect context documentation:

- **Change Detection**: File-based monitoring with hash tracking
- **Impact Analysis**: Categorizes changes by impact level
- **Report Generation**: Creates actionable change reports
- **Change Log Updates**: Maintains historical context changes

## Development Tools Integration

### Serena MCP Server

The project integrates with Serena MCP Server - a powerful coding agent toolkit that provides semantic code understanding through Language Server Protocol (LSP) integration.

#### **Core Capabilities**
- **Semantic Code Analysis**: Symbol-level code understanding rather than text-based approaches
- **Multi-Language Support**: Python, TypeScript/JavaScript, Java, C#, Rust, Go, Ruby, C++, PHP
- **Intelligent Code Operations**: `find_symbol`, `replace_symbol_body`, `search_for_pattern`, and more
- **Context-Aware Assistance**: Configurable behavior for different environments

#### **Integration Architecture**
- **Installation Path**: `/home/omar/serena/`
- **Primary Mode**: MCP Server for Claude Desktop integration
- **Context Mode**: `ide-assistant` for project-specific development assistance
- **Configuration**: Four-layer hierarchy (global config, CLI args, project settings, runtime modes)

#### **Essential Commands** (when working with Serena)
```bash
# Dependency management and task orchestration (uv + poe)
uv run poe lint        # Linting (only allowed command)
uv run poe format      # Code formatting (only allowed command) 
uv run poe type-check  # Type checking (only allowed command)
uv run poe test [args] # Testing (preferred method)

# Manual Serena startup for ruleIQ project
cd /home/omar/serena
# Start Serena MCP server with ruleIQ context
python -m serena.mcp --context ide-assistant --project /home/omar/Documents/ruleIQ
```

#### **Development Workflow Enhancement**
- **Semantic Code Editing**: Precise symbol-level modifications vs text manipulation
- **Cross-Language Analysis**: Unified approach across different programming languages
- **Project Context Awareness**: Deep understanding of ruleIQ architecture and patterns
- **Real-time Code Intelligence**: LSP-powered code analysis and suggestions

#### **ruleIQ-Specific Benefits**
- **Full-Stack Understanding**: Semantic analysis of both Python backend and TypeScript frontend
- **Database Schema Intelligence**: Understanding of SQLAlchemy models and relationships
- **AI Service Analysis**: Deep comprehension of the 25+ AI service modules
- **Architecture Compliance**: Ensures changes align with established patterns and context

## Document Metadata

- **Created**: 2025-01-07
- **Version**: 1.0.0
- **Authors**: AI Assistant
- **Review Status**: Initial Draft
- **Next Review**: 2025-01-14
- **Context Coverage**: Complete for all major platform areas
- **Critical Issues**: 3 critical issues identified requiring immediate attention
- **Quality Score**: B+ (Good architecture, critical execution issues)