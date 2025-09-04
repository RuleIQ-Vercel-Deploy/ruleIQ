# ruleIQ Testing Procedures & Commands

**Updated**: 2025-08-15  
**Test Coverage**: 671+ tests passing

## 🎯 Overview

This document provides comprehensive testing procedures for the ruleIQ platform, covering backend, frontend, and integration testing strategies.

## 🔧 Environment Setup

### Backend Test Environment

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install test dependencies
pip install -r requirements-test.txt

# Set test environment variables
export TESTING=true
export DATABASE_URL=postgresql://test_db_url
export REDIS_URL=redis://localhost:6379/1
```

### Frontend Test Environment

```bash
cd frontend

# Install dependencies
pnpm install

# Set test environment
export NODE_ENV=test
```

## 🧪 Backend Testing

### Quick Test Commands

```bash
# Fast unit tests (2-5 minutes) - RECOMMENDED FOR PRE-COMMIT
make test-fast

# Run specific test file
pytest tests/unit/services/test_business_profile.py -v

# Run tests by marker
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m api          # API tests only
pytest -m ai           # AI service tests
pytest -m security     # Security tests
```

### Comprehensive Test Suite

```bash
# Full test suite (10-15 minutes)
make test-full

# Test with coverage report
make test-coverage

# Generate HTML coverage report
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Categories

#### 1. Unit Tests (`tests/unit/`)
Fast, isolated tests for individual components:

```bash
# Service layer tests
pytest tests/unit/services/ -v

# API router tests
pytest tests/unit/routers/ -v

# Utility function tests
pytest tests/unit/utils/ -v
```

#### 2. Integration Tests (`tests/integration/`)
Tests that verify component interactions:

```bash
# Database integration
pytest tests/integration/database/ -v

# Redis integration
pytest tests/integration/cache/ -v

# External API integration
pytest tests/integration/external/ -v
```

#### 3. API Tests (`tests/api/`)
Full API endpoint testing:

```bash
# Authentication endpoints
pytest tests/api/test_auth.py -v

# Business logic endpoints
pytest tests/api/test_business_profiles.py -v

# AI endpoints
pytest tests/api/test_ai_endpoints.py -v
```

#### 4. AI & Agent Tests
Specialized tests for AI components:

```bash
# IQ Agent tests
pytest tests/unit/services/test_iq_agent.py -v

# RAG Self-Critic tests
pytest tests/test_rag_self_critic.py -v

# AI circuit breaker tests
pytest tests/unit/services/test_circuit_breaker.py -v

# All AI tests
pytest -m ai -v
```

### Performance Testing

```bash
# Run performance benchmarks
pytest tests/performance/ --benchmark-only

# Profile slow tests
pytest --durations=10

# Memory profiling
pytest --memprof
```

### Security Testing

```bash
# Security-focused tests
pytest -m security -v

# SQL injection tests
pytest tests/security/test_sql_injection.py -v

# Authentication tests
pytest tests/security/test_authentication.py -v

# RBAC tests
pytest tests/security/test_rbac.py -v
```

## 🎨 Frontend Testing

### Unit Tests

```bash
cd frontend

# Run all unit tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Run specific test file
pnpm test -- business-profile.test.tsx

# Run tests with coverage
pnpm test:coverage
```

### Component Testing

```bash
# Test individual components
pnpm test:components

# Test with React Testing Library
pnpm test -- --testNamePattern="BusinessProfileForm"

# Debug mode
pnpm test:debug
```

### E2E Testing with Playwright

```bash
# Install Playwright browsers
pnpm exec playwright install

# Run E2E tests
pnpm test:e2e

# Run E2E tests in headed mode (see browser)
pnpm test:e2e:headed

# Run specific E2E test
pnpm test:e2e -- --grep "authentication"

# Generate E2E test report
pnpm test:e2e:report
```

### Visual Regression Testing

```bash
# Run visual tests
pnpm test:visual

# Update visual snapshots
pnpm test:visual:update

# Review visual differences
pnpm test:visual:report
```

### Theme Testing

```bash
# Test with teal theme
NEXT_PUBLIC_USE_NEW_THEME=true pnpm test

# Test theme switching
pnpm test:theme
```

## 🔄 Integration Testing

### Full Stack Integration

```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
make test-integration

# Clean up
docker-compose -f docker-compose.test.yml down
```

### API Integration Tests

```bash
# Test with real database
DATABASE_URL=postgresql://test_db pytest tests/integration/api/ -v

# Test with Redis
REDIS_URL=redis://localhost:6379/1 pytest tests/integration/cache/ -v
```

## 🤖 AI Agent Testing

### IQ Agent Testing

```bash
# Quick fact-check (2-5 seconds)
python services/rag_self_critic.py quick-check --query "GDPR applies to UK businesses"

# Comprehensive fact-check (10-30 seconds)
python services/rag_self_critic.py fact-check --query "ISO 27001 requirements"

# Self-critique analysis (15-45 seconds)
python services/rag_self_critic.py critique --query "Complex compliance scenario"

# Test agent memory
pytest tests/unit/services/test_compliance_memory_manager.py -v

# Test GraphRAG integration
pytest tests/integration/test_graphrag.py -v
```

### LangGraph Workflow Testing

```bash
# Test workflow orchestration
pytest tests/unit/services/test_langgraph_workflows.py -v

# Test state persistence
pytest tests/integration/test_workflow_state.py -v
```

## 📊 Test Coverage Requirements

### Minimum Coverage Targets

| Component | Target | Current |
|-----------|--------|---------|
| API Routes | 90% | 92% ✅ |
| Services | 85% | 87% ✅ |
| Utils | 95% | 96% ✅ |
| AI Services | 80% | 82% ✅ |
| Frontend Components | 80% | 78% ⚠️ |
| E2E Critical Paths | 100% | 100% ✅ |

### Generating Coverage Reports

```bash
# Backend coverage
make test-coverage
# Report available at: htmlcov/index.html

# Frontend coverage
cd frontend && pnpm test:coverage
# Report available at: coverage/lcov-report/index.html
```

## 🚦 CI/CD Testing

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### GitHub Actions Workflow

```yaml
# Automatically runs on PR
- Backend unit tests
- Frontend unit tests
- Linting & formatting
- Type checking
- Security scanning
```

## 🐛 Debugging Tests

### Backend Debugging

```bash
# Run with pytest debugger
pytest tests/unit/test_file.py --pdb

# Verbose output
pytest -vvv tests/unit/test_file.py

# Show print statements
pytest -s tests/unit/test_file.py

# Show local variables on failure
pytest -l tests/unit/test_file.py
```

### Frontend Debugging

```bash
# Debug in VS Code
pnpm test:debug

# Console output
pnpm test -- --verbose

# Interactive watch mode
pnpm test:watch
```

## 📝 Writing New Tests

### Backend Test Template

```python
# tests/unit/services/test_new_service.py
import pytest
from unittest.mock import Mock, patch

class TestNewService:
    """Test suite for NewService"""
    
    @pytest.fixture
    def service(self):
        """Create service instance"""
        return NewService()
    
    @pytest.mark.unit
    async def test_method_success(self, service):
        """Test successful execution"""
        # Arrange
        mock_dependency = Mock()
        
        # Act
        result = await service.method(mock_dependency)
        
        # Assert
        assert result.success is True
        mock_dependency.called_once_with(expected_args)
```

### Frontend Test Template

```typescript
// tests/components/NewComponent.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { NewComponent } from '@/components/NewComponent';

describe('NewComponent', () => {
  it('should render correctly', () => {
    render(<NewComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
  
  it('should handle user interaction', async () => {
    render(<NewComponent />);
    const button = screen.getByRole('button');
    
    fireEvent.click(button);
    
    expect(await screen.findByText('Updated Text')).toBeInTheDocument();
  });
});
```

## 🔍 Troubleshooting

### Common Test Issues

#### Pytest Collection Errors

```bash
# Clear pytest cache
pytest --cache-clear

# Check for import errors
python -c "import tests.unit.services.test_file"

# Run with minimal settings
pytest tests/unit/ --tb=short
```

#### Database Connection Issues

```bash
# Use test database
export DATABASE_URL=sqlite:///test.db
pytest tests/unit/ -v

# Reset test database
python database/init_test_db.py
```

#### Frontend Test Failures

```bash
# Clear Jest cache
pnpm test -- --clearCache

# Update snapshots
pnpm test -- -u

# Check Node version
node --version  # Should be 18+
```

## 📚 Best Practices

1. **Run tests before committing**: `make test-fast`
2. **Write tests for new features**: TDD approach
3. **Keep tests fast**: Mock external dependencies
4. **Use descriptive test names**: `test_should_create_user_when_valid_data`
5. **Test edge cases**: Null values, empty strings, large datasets
6. **Maintain test isolation**: Each test should be independent
7. **Use fixtures**: Reuse common test setup
8. **Assert specific outcomes**: Avoid broad assertions

## 🔗 Related Documentation

- [Development Setup](../README.md#-quick-start)
- [API Documentation](./API_ENDPOINTS_DOCUMENTATION.md)
- [CI/CD Pipeline](./.github/workflows/test.yml)

---

*Last Updated: 2025-08-15*  
*Total Tests: 671+*  
*Test Framework: pytest (backend), Jest/Playwright (frontend)*