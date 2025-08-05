# Feature Development Workflow

Implement production-ready features using specialized agents with comprehensive quality assurance.

## Overview

This workflow orchestrates multiple specialized agents to implement complete features from design to deployment, ensuring consistency, quality, and production readiness at each stage.

## Workflow Steps

### 1. **Requirements Analysis & Planning**
   - Use Task tool with subagent_type="business-analyst"
   - Prompt: "Analyze requirements for: $ARGUMENTS. Define user stories, acceptance criteria, success metrics, and business value. Include risk assessment and implementation complexity."
   - Output: Requirements document with clear specifications

### 2. **Architecture & API Design**
   - Use Task tool with subagent_type="backend-architect" 
   - Prompt: "Design scalable architecture for: $ARGUMENTS. Include RESTful API endpoints, database schema, service boundaries, error handling, rate limiting, and security considerations. Use requirements from step 1: [requirements]"
   - Output: API specification, database migrations, service architecture

### 3. **Frontend Architecture & Design**
   - Use Task tool with subagent_type="frontend-architect"
   - Prompt: "Design frontend architecture for: $ARGUMENTS. Create component hierarchy, state management strategy, API integration patterns, and UI/UX specifications. Use backend design from step 2: [API spec]"
   - Output: Component structure, design system alignment, user flow

### 4. **Security Review**
   - Use Task tool with subagent_type="security-auditor"
   - Prompt: "Conduct security review for: $ARGUMENTS. Analyze authentication, authorization, data validation, encryption, and potential vulnerabilities. Review architecture from steps 2-3: [architecture details]"
   - Output: Security recommendations, threat model, compliance checklist

### 5. **Backend Implementation**
   - Use Task tool with subagent_type="backend-architect"
   - Prompt: "Implement backend services for: $ARGUMENTS. Follow the approved architecture from step 2: [API design] and security requirements from step 4: [security specs]. Include database models, API endpoints, business logic, and error handling."
   - Output: Complete backend implementation

### 6. **Frontend Implementation**
   - Use Task tool with subagent_type="frontend-developer"
   - Prompt: "Implement frontend components for: $ARGUMENTS. Use approved design from step 3: [frontend architecture] and integrate with backend APIs from step 5: [API endpoints]. Ensure accessibility and responsive design."
   - Output: Complete frontend implementation

### 7. **Comprehensive Testing**
   - Use Task tool with subagent_type="test-engineer"
   - Prompt: "Create comprehensive test suite for: $ARGUMENTS. Cover backend APIs from step 5: [endpoints] and frontend components from step 6: [components]. Include unit, integration, e2e, security, and performance tests. Target 85%+ coverage."
   - Output: Complete test suite with coverage report

### 8. **Performance Optimization**
   - Use Task tool with subagent_type="performance-optimizer"
   - Prompt: "Optimize performance for: $ARGUMENTS. Analyze backend services from step 5: [implementation] and frontend from step 6: [components]. Target <200ms API response times and optimize bundle sizes, database queries, and caching strategies."
   - Output: Performance optimizations and benchmarks

### 9. **Code Review & Quality Assurance**
   - Use Task tool with subagent_type="code-reviewer"
   - Prompt: "Conduct comprehensive code review for: $ARGUMENTS. Review implementation from steps 5-6: [code], tests from step 7: [test suite], and optimizations from step 8: [performance]. Ensure code quality, maintainability, and adherence to standards."
   - Output: Code review report with recommendations

### 10. **Documentation & Deployment**
   - Use Task tool with subagent_type="docs-architect"
   - Prompt: "Create comprehensive documentation for: $ARGUMENTS. Document API endpoints, component usage, deployment procedures, and operational runbooks. Include the complete implementation: [all previous outputs]"
   - Use Task tool with subagent_type="deployment-engineer"
   - Prompt: "Prepare production deployment for: $ARGUMENTS. Create CI/CD pipeline, containerization, monitoring, rollback procedures, and health checks for the complete feature: [implementation details]"
   - Output: Documentation, deployment pipeline, monitoring setup

## Quality Gates

Each step must pass quality gates before proceeding:
- ✅ Requirements clearly defined with acceptance criteria
- ✅ Architecture reviewed and approved
- ✅ Security vulnerabilities addressed
- ✅ Code passes all tests (85%+ coverage)
- ✅ Performance meets targets (<200ms API, optimized frontend)
- ✅ Code review approved
- ✅ Documentation complete
- ✅ Deployment pipeline tested

## Integration Points

- **Database**: Ensure migrations are reversible and tested
- **APIs**: Validate OpenAPI specs and contract testing
- **Frontend**: Verify design system compliance and accessibility
- **Security**: Confirm RBAC integration and audit logging
- **Monitoring**: Set up alerts and performance tracking

## Rollback Strategy

- Database migration rollback procedures
- Feature flag configuration for gradual rollout
- Blue/green deployment for zero-downtime updates
- Monitoring and alerting for early issue detection

## Success Criteria

- ✅ All tests passing with 85%+ coverage
- ✅ Performance benchmarks met
- ✅ Security audit passed
- ✅ Production deployment successful
- ✅ User acceptance criteria satisfied
- ✅ Documentation complete and accessible

---

**Feature Description:** $ARGUMENTS

**Usage:** Replace $ARGUMENTS with detailed feature requirements and execute each step sequentially, ensuring quality gates are met before proceeding.
