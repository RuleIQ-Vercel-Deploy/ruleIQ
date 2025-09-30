# Coverage Baseline Report

**Generated**: 2025-09-30 08:39:24
**Project**: RuleIQ Compliance Automation Platform
**Purpose**: Establish test coverage baseline for quality gate enforcement

---

## Executive Summary

### Overall Project Coverage

| Metric | Coverage | Target | Status |
|--------|----------|--------|--------|
| **Combined Project** | 3.13% | 80% | 🔴 Critical |
| **Backend (Python)** | 3.13% | 80% | 🔴 Critical |
| **Frontend (TypeScript)** | 0.00% | 80% | 🔴 Critical |

### Key Findings

- 🔴 **Critical**: Overall coverage is below 50% - urgent action required

- Current baseline established as of 2025-09-30 08:39:24
- Coverage data collected from pytest-cov (backend) and vitest (frontend)
- Quality gates will enforce maintenance of this baseline

---

## Backend Coverage (Python)

### Overall Backend Metrics

| Type | Coverage | Status |
|------|----------|--------|
| **Line Coverage** | 3.13% | ⚠️ |
| **Branch Coverage** | 0.00% | ⚠️ |

### Per-Module Breakdown

| Module | Line Coverage | Branch Coverage | Status |
|--------|--------------|-----------------|--------|
| `models` | 100.00% | 100.00% | 🟢 |
| `.` | 7.83% | 0.00% | 🔴 |
| `agents` | 0.00% | 0.00% | 🔴 |
| `ai` | 0.00% | 0.00% | 🔴 |
| `ai.evaluation` | 0.00% | 0.00% | 🔴 |
| `ai.evaluation.golden_datasets` | 0.00% | 0.00% | 🔴 |
| `ai.evaluation.infrastructure` | 0.00% | 0.00% | 🔴 |
| `ai.evaluation.metrics` | 0.00% | 0.00% | 🔴 |
| `ai.evaluation.schemas` | 0.00% | 0.00% | 🔴 |
| `ai.evaluation.tools` | 0.00% | 0.00% | 🔴 |
| `automation` | 0.00% | 0.00% | 🔴 |
| `caching` | 0.00% | 0.00% | 🔴 |
| `clients` | 0.00% | 0.00% | 🔴 |
| `integrations` | 0.00% | 0.00% | 🔴 |
| `integrations.base` | 0.00% | 100.00% | 🔴 |
| `knowledge_graph` | 0.00% | 0.00% | 🔴 |
| `monitoring` | 0.00% | 0.00% | 🔴 |
| `realtime` | 0.00% | 0.00% | 🔴 |
| `reporting` | 0.00% | 0.00% | 🔴 |
| `schemas` | 0.00% | 0.00% | 🔴 |
| `services` | 0.00% | 0.00% | 🔴 |

### Top 10 Most Covered Files

| File | Coverage | Status |
|------|----------|--------|
| `api/context.py` | 100.00% | ✅ |
| `api/integrations/__init__.py` | 100.00% | ✅ |
| `api/integrations/base/__init__.py` | 100.00% | ✅ |
| `database/__init__.py` | 100.00% | ✅ |
| `database/assessment_lead.py` | 100.00% | ✅ |
| `database/assessment_question.py` | 100.00% | ✅ |
| `database/assessment_session.py` | 100.00% | ✅ |
| `database/business_profile.py` | 100.00% | ✅ |
| `database/chat_conversation.py` | 100.00% | ✅ |
| `database/chat_message.py` | 100.00% | ✅ |

### Top 10 Least Covered Files (Priority for Improvement)

| File | Coverage | Priority |
|------|----------|----------|
| `database/db_setup.py` | 19.25% | 🔴 High |
| `database/ai_question_bank.py` | 37.37% | 🟡 Medium |
| `database/lead_scoring_event.py` | 46.91% | 🟡 Medium |
| `database/conversion_event.py` | 54.46% | 🟡 Medium |
| `database/freemium_assessment_session.py` | 68.83% | 🟡 Medium |
| `database/evidence_item.py` | 94.34% | 🟡 Medium |
| `database/report_schedule.py` | 95.65% | 🟡 Medium |
| `database/compliance_framework.py` | 97.30% | 🟡 Medium |
| `database/generated_policy.py` | 97.37% | 🟡 Medium |
| `api/context.py` | 100.00% | 🟡 Medium |

### Critical Uncovered Paths

⚠️  **These files handle sensitive operations and require immediate coverage:**

- `api/auth.py` - 0.00% coverage
- `api/integrations/oauth_config.py` - 0.00% coverage
- `api/schemas/compliance.py` - 0.00% coverage
- `services/ai/assessment_tools.py` - 0.00% coverage
- `services/ai/compliance_ingestion_pipeline.py` - 0.00% coverage
- `services/ai/compliance_query_engine.py` - 0.00% coverage
- `services/ai/evaluation/schemas/compliance_scenario.py` - 0.00% coverage
- `services/assessment_agent.py` - 0.00% coverage
- `services/assessment_service.py` - 0.00% coverage
- `services/auth_service.py` - 0.00% coverage
- `services/compliance_graph_initializer.py` - 0.00% coverage
- `services/compliance_loader.py` - 0.00% coverage
- `services/compliance_memory_manager.py` - 0.00% coverage
- `services/compliance_retrieval_queries.py` - 0.00% coverage
- `services/security_alerts.py` - 0.00% coverage

---

## Frontend Coverage (TypeScript/React)

### Overall Frontend Metrics

| Type | Coverage | Status |
|------|----------|--------|
| **Line Coverage** | 0.00% | ⚠️ |
| **Branch Coverage** | 0.00% | ⚠️ |
| **Function Coverage** | 0.00% | ⚠️ |
| **Statement Coverage** | 0.00% | ⚠️ |


---

## Coverage Trends

### Historical Data

This is the initial baseline. Future reports will show trends over time.

### Coverage Improvement Targets

| Timeframe | Backend Target | Frontend Target | Combined Target |
|-----------|---------------|-----------------|-----------------|
| **Current** | 3.13% | 0.00% | 3.13% |
| **3 Months** | 18.13% | 15.00% | 18.13% |
| **6 Months** | 33.13% | 30.00% | 33.13% |
| **12 Months** | 80% | 80% | 80% |

### Planned Initiatives

1. **Q1 2025**: Focus on critical path coverage (authentication, payments, compliance)
2. **Q2 2025**: Increase integration test coverage
3. **Q3 2025**: Add E2E test coverage for core user flows
4. **Q4 2025**: Achieve 80% coverage target

---

## Quality Gates

### Current Thresholds (Enforced in CI/CD)

- **Backend Minimum**: 3.13% (current baseline)
- **Frontend Minimum**: 0.00% (current baseline)
- **PR Requirement**: No coverage decrease >2% without justification

### Exceptions

Modules below baseline require explicit approval for coverage decreases:
- All modules currently below 50% coverage
- Critical security and compliance modules

---

## Recommendations

### Quick Wins (High Impact, Low Effort)


**Backend:**
- `api/clients/__init__.py` (4 statements) - Small file, easy to test
- `api/integrations/oauth_config.py` (28 statements) - Small file, easy to test
- `api/request_id_middleware.py` (16 statements) - Small file, easy to test
- `api/schemas/__init__.py` (2 statements) - Small file, easy to test
- `api/schemas/base.py` (43 statements) - Small file, easy to test


### High-Priority Modules

1. **Authentication & Security**: Critical for system security
2. **Payment Processing**: Financial transaction integrity
3. **Compliance Logic**: Core business functionality
4. **API Endpoints**: User-facing functionality

### Testing Strategy Improvements

1. **Increase Unit Test Coverage**: Focus on business logic and utilities
2. **Add Integration Tests**: Test component interactions
3. **Expand E2E Tests**: Cover critical user workflows
4. **Mock External Services**: Improve test reliability and speed

### Tooling Enhancements

1. **Coverage Badges**: Add to README for visibility
2. **Coverage Trends**: Track historical data
3. **SonarCloud Integration**: Fix path mapping for accurate reporting
4. **Automated Alerts**: Notify team of coverage drops

---

## Appendix

### Viewing Coverage Reports

**Backend (HTML):**
```bash
open htmlcov/index.html
```

**Frontend (HTML):**
```bash
open frontend/coverage/index.html
```

### Running Coverage Locally

**Backend:**
```bash
pytest --cov=services --cov=api --cov=core --cov=utils --cov=models \
       --cov-report=html --cov-report=xml --cov-branch
```

**Frontend:**
```bash
cd frontend && pnpm test:coverage
```

### CI/CD Workflows

- Backend Tests: `.github/workflows/backend-tests.yml`
- Frontend Tests: `.github/workflows/frontend-tests.yml`
- Coverage Report: `.github/workflows/coverage-report.yml`

### Troubleshooting

**Coverage not generating:**
1. Ensure all dependencies installed (`pytest-cov`, `@vitest/coverage-v8`)
2. Check test execution completes successfully
3. Verify configuration files (`.coveragerc`, `vitest.config.ts`)

**Coverage shows 0% in SonarCloud:**
1. Check path mapping in `sonar-project.properties`
2. Verify coverage file formats (XML for backend, LCOV for frontend)
3. Ensure source paths match between coverage report and SonarCloud config

---

**Last Updated**: {timestamp}
**Next Review**: Quarterly or after major feature releases
