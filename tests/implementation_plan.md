# Test Coverage Implementation Plan - P3 Task

## Objective
Transform ruleIQ's test coverage from 0% to 80% within 5 days (by January 8, 2025).

## Current State (January 3, 2025)
- **Test Infrastructure**: ✅ Fixed - 1,884 tests collectable
- **Current Coverage**: 0% (no tests passing)
- **Target Coverage**: 80% overall, 90% critical business logic

## Priority Areas & Schedule

### Day 1 (Jan 3): Core Business Logic - Services Layer
**Target: 25% coverage**

#### AI Services (`/services/ai/`) - HIGHEST PRIORITY
- [ ] `assistant.py` - Main AI assistant orchestration
- [ ] `tools.py` - Tool registry and execution
- [ ] `assessment_tools.py` - Assessment AI tools
- [ ] `evidence_tools.py` - Evidence validation tools
- [ ] `regulation_tools.py` - Regulatory mapping tools
- [ ] `context_manager.py` - Context management
- [ ] `safety_manager.py` - Content safety validation
- [ ] `circuit_breaker.py` - Fault tolerance

#### Compliance Services (`/services/compliance/`)
- [ ] `compliance_service.py` - Core compliance logic
- [ ] `assessment_service.py` - Assessment processing
- [ ] `framework_service.py` - Framework management
- [ ] `scoring_service.py` - Compliance scoring

#### Security Services (`/services/security/`)
- [ ] `auth_service.py` - Authentication logic
- [ ] `rbac_service.py` - Role-based access control
- [ ] `encryption_service.py` - Data encryption
- [ ] `jwt_service.py` - JWT token management

### Day 2 (Jan 4): API Integration Tests
**Target: 45% coverage**

#### Authentication Endpoints
- [ ] `/api/v1/auth/login` - User login
- [ ] `/api/v1/auth/register` - User registration
- [ ] `/api/v1/auth/token` - Token refresh
- [ ] `/api/v1/auth/google` - Google OAuth

#### Core Business Endpoints
- [ ] `/api/v1/assessments/*` - Assessment CRUD
- [ ] `/api/v1/frameworks/*` - Framework operations
- [ ] `/api/v1/policies/*` - Policy generation
- [ ] `/api/v1/evidence/*` - Evidence management
- [ ] `/api/v1/compliance/*` - Compliance status

#### AI Endpoints
- [ ] `/api/v1/ai/assess` - AI assessment
- [ ] `/api/v1/ai/chat` - Chat interface
- [ ] `/api/v1/ai/policies` - AI policy generation

### Day 3 (Jan 5): Database & Models
**Target: 60% coverage**

#### Database Models
- [ ] User model and operations
- [ ] BusinessProfile model
- [ ] Assessment model
- [ ] Framework model
- [ ] Policy model
- [ ] Evidence model

#### Database Operations
- [ ] Transaction handling
- [ ] Query optimization
- [ ] Connection pooling
- [ ] Migration tests

### Day 4 (Jan 6): Frontend & Integration
**Target: 70% coverage**

#### React Components
- [ ] Authentication components
- [ ] Dashboard components
- [ ] Assessment forms
- [ ] Policy viewers
- [ ] Evidence upload

#### State Management
- [ ] Redux/Context API tests
- [ ] API integration tests
- [ ] WebSocket tests

### Day 5 (Jan 7): Gap Analysis & Final Push
**Target: 80%+ coverage**

- [ ] Identify coverage gaps
- [ ] Add missing critical tests
- [ ] Performance tests
- [ ] Security tests
- [ ] Edge cases
- [ ] Error handling

## Test Categories & Markers

### Unit Tests (`@pytest.mark.unit`)
- Isolated function/method tests
- Mock all dependencies
- Fast execution (<100ms)

### Integration Tests (`@pytest.mark.integration`)
- API endpoint tests with TestClient
- Database integration with test DB
- Service-to-service communication

### End-to-End Tests (`@pytest.mark.e2e`)
- Complete user workflows
- Real database transactions
- Full authentication flow

### Performance Tests (`@pytest.mark.performance`)
- Response time validation
- Load testing
- Memory usage

## Technical Implementation

### Test Structure
```python
# Example test structure
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
async def test_ai_assistant_classify_intent():
    """Test AI assistant intent classification"""
    # Arrange
    assistant = ComplianceAssistant(db=Mock())
    
    # Act
    result = await assistant.classify_intent("How do I comply with GDPR?")
    
    # Assert
    assert result['intent'] == 'compliance_guidance'
    assert result['confidence'] > 0.8
```

### Coverage Configuration
```bash
# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term-missing

# Focus on specific module
pytest tests/services/ai --cov=services/ai --cov-report=term

# Run in parallel for speed
pytest -n auto --cov=.
```

### Mock Strategy
1. **External Services**: Mock all (OpenAI, Google, AWS, etc.)
2. **Database**: Use test database on port 5433
3. **Redis**: Use fakeredis
4. **File Storage**: Use tmp_path fixture

## Success Metrics
- [ ] 80%+ overall code coverage
- [ ] 90%+ coverage on critical paths
- [ ] Zero failing tests
- [ ] All tests run in <5 minutes
- [ ] Coverage integrated with CI/CD
- [ ] SonarCloud quality gate passes

## Risk Mitigation
- **Flaky Tests**: Add retry mechanism
- **Slow Tests**: Use parallel execution
- **External Dependencies**: Mock everything
- **Database State**: Clean between tests
- **Coverage Gaps**: Focus on business logic first

## Daily Progress Tracking
- Day 1 End: 25% coverage, services tested
- Day 2 End: 45% coverage, API tested
- Day 3 End: 60% coverage, DB tested
- Day 4 End: 70% coverage, frontend tested
- Day 5 End: 80%+ coverage, gaps filled

## Next Steps
1. Start with highest priority AI services
2. Create reusable test fixtures
3. Implement mock factories
4. Run coverage report hourly
5. Update this plan with actual progress