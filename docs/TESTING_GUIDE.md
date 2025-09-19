# ruleIQ Testing Guide

## Overview

This guide covers the comprehensive testing infrastructure for the ruleIQ platform, including unit tests, integration tests, performance tests, and end-to-end testing strategies.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Organization](#test-organization)
3. [Test Execution Modes](#test-execution-modes)
4. [Test Groups](#test-groups)
5. [Writing Tests](#writing-tests)
6. [CI/CD Integration](#cicd-integration)
7. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

```bash
# Activate virtual environment
source /home/omar/Documents/ruleIQ/.venv/bin/activate

# Install test dependencies
make install-test-deps
```

### Running Tests

```bash
# Quick unit tests (2-5 minutes)
make test-fast

# Full test suite
make test-full

# Specific test group
make test-group-unit
```

## Test Organization

### Directory Structure

```
tests/
├── unit/                 # Unit tests for individual components
│   ├── services/        # Service layer tests
│   ├── models/         # Database model tests
│   └── utils/          # Utility function tests
├── integration/         # Integration tests
│   ├── api/            # API endpoint tests
│   ├── database/       # Database integration tests
│   └── external/       # External service tests
├── performance/        # Performance and benchmark tests
├── e2e/               # End-to-end workflow tests
├── fixtures/          # Test data and fixtures
└── conftest.py        # Pytest configuration
```

### Test Markers

Tests are organized with pytest markers for selective execution:

```python
@pytest.mark.unit          # Fast unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.performance   # Performance tests
@pytest.mark.ai           # AI service tests
@pytest.mark.compliance   # Compliance engine tests
@pytest.mark.security     # Security tests
@pytest.mark.e2e          # End-to-end tests
@pytest.mark.slow         # Slow-running tests
```

## Test Execution Modes

### Makefile Commands

The project includes a comprehensive Makefile with optimized test execution:

#### Fast Testing Modes

```bash
# Unit tests only (2-3 minutes)
make test-fast

# Quick test groups
make test-quick-groups
```

#### Comprehensive Testing

```bash
# Full test suite with optimization
make test-full

# All test groups sequentially
make test-groups

# All test groups in parallel (fastest)
make test-groups-parallel
```

#### Specialized Testing

```bash
# AI and compliance tests
make test-ai

# Security and authentication tests
make test-security

# Performance benchmarks
make test-performance

# End-to-end workflows
make test-e2e
```

### Chunked Test Execution

The `scripts/run_tests_chunked.py` script provides intelligent test chunking:

```bash
# Run with specific mode
python scripts/run_tests_chunked.py --mode fast

# List available modes
python scripts/run_tests_chunked.py --list-modes
```

Available modes:
- `fast`: Unit tests only (high parallelism)
- `integration`: Integration tests (medium parallelism)
- `performance`: Performance tests (sequential)
- `ai`: AI and compliance tests
- `security`: Security and auth tests
- `e2e`: End-to-end tests
- `full`: Complete test suite
- `ci`: CI-optimized execution

## Test Groups

### Independent Test Groups

The project implements 6 independent test groups for better organization:

#### Group 1: Unit Tests (2-3 minutes)
```bash
make test-group-unit
```
- Core business logic
- Utility functions
- Model validation
- Service layer logic

#### Group 2: AI Core Tests (3-4 minutes)
```bash
make test-group-ai
```
- LLM service integration
- AI assessment logic
- RAG self-critic
- Circuit breaker patterns

#### Group 3: Basic API Tests (4-5 minutes)
```bash
make test-group-api
```
- Endpoint validation
- Request/response formats
- Authentication flows
- Rate limiting

#### Group 4: AI Endpoints Tests (5-6 minutes)
```bash
make test-group-endpoints
```
- AI assessment endpoints
- Streaming responses
- Compliance AI integration
- IQ Agent API

#### Group 5: Advanced Features (3-4 minutes)
```bash
make test-group-advanced
```
- Complex workflows
- Integration scenarios
- Compliance engine
- GraphRAG integration

#### Group 6: End-to-End Tests (6-8 minutes)
```bash
make test-group-e2e
```
- Complete user journeys
- Multi-step workflows
- System integration
- Production scenarios

### Running Test Groups

```bash
# List all test groups
make test-groups-list

# Run all groups sequentially (~25 minutes)
make test-groups

# Run all groups in parallel (~8 minutes)
make test-groups-parallel

# Run core groups only
make test-core-groups
```

## Writing Tests

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, patch
from services.ai_service import AIAssessmentService

class TestAIAssessmentService:
    @pytest.fixture
    def ai_service(self):
        return AIAssessmentService()

    @pytest.mark.unit
    def test_generate_guidance(self, ai_service):
        """Test AI guidance generation."""
        result = ai_service.generate_guidance(
            question="What is your data retention policy?",
            context={"industry": "Technology"}
        )

        assert result.confidence_score > 0.8
        assert "GDPR" in result.guidance
        assert len(result.follow_up_suggestions) > 0
```

### Integration Test Example

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_assessment_workflow():
    """Test complete assessment workflow."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create assessment
        response = await client.post(
            "/api/v1/assessments",
            json={"framework_id": "iso27001"}
        )
        assert response.status_code == 201

        assessment_id = response.json()["assessment_id"]

        # Submit responses
        response = await client.post(
            f"/api/v1/assessments/{assessment_id}/responses",
            json={"question_id": "q1", "response": "Yes"}
        )
        assert response.status_code == 200
```

### Performance Test Example

```python
@pytest.mark.performance
@pytest.mark.benchmark
def test_ai_response_time(benchmark):
    """Benchmark AI service response time."""
    service = AIAssessmentService()

    result = benchmark(
        service.generate_guidance,
        question="Test question",
        context={}
    )

    # Assert performance requirements
    assert benchmark.stats['mean'] < 2.0  # Average < 2 seconds
    assert benchmark.stats['max'] < 5.0   # Max < 5 seconds
```

## CI/CD Integration

### GitHub Actions

The project includes comprehensive CI/CD workflows:

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        test-group: [unit, ai, api, endpoints, advanced, e2e]

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run test group
        run: |
          python test_groups.py group${{ matrix.test-group }}
```

### Test Coverage

```bash
# Generate coverage report
make test-coverage

# Fast coverage (unit tests only)
make test-coverage-fast

# View HTML report
open htmlcov/index.html
```

### SonarCloud Integration

Tests are integrated with SonarCloud for code quality:
- Automatic coverage reporting
- Code smell detection
- Security vulnerability scanning
- Maintainability metrics

## Performance Testing

### Running Benchmarks

```bash
# Run all benchmarks
make test-benchmark

# Run specific performance tests
pytest tests/performance/ --benchmark-only
```

### Load Testing

```bash
# Run stress tests
make test-stress

# Memory profiling
make test-memory
```

### Performance Metrics

Key performance targets:
- API response time: <200ms (p95)
- AI quick check: 2-5 seconds
- Standard AI queries: 10-30 seconds
- Database queries: <100ms (p95)
- Test suite completion: <30 minutes (full)

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database configuration
doppler configs
doppler secrets | grep DATABASE_URL

# Run with test database
TEST_DATABASE_URL=postgresql://test:test@localhost:5432/test_ruleiq pytest
```

#### 2. AI Service Timeouts
```bash
# Increase timeout for AI tests
pytest tests/ai/ --timeout=60
```

#### 3. Parallel Execution Issues
```bash
# Run tests sequentially if parallel fails
make test-sequential

# Or reduce worker count
pytest -n 2 tests/
```

#### 4. Import Errors
```bash
# Ensure virtual environment is activated
source /home/omar/Documents/ruleIQ/.venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Debug Mode

```bash
# Run tests with verbose output
pytest -vvs tests/unit/

# Run with debugging
pytest --pdb tests/unit/test_specific.py

# Show test output
pytest --capture=no tests/
```

### Test Profiling

```bash
# Profile test execution
make test-profile

# Identify slow tests
pytest --durations=10
```

## Best Practices

### 1. Test Isolation
- Each test should be independent
- Use fixtures for setup/teardown
- Mock external dependencies

### 2. Clear Naming
- Use descriptive test names
- Follow pattern: `test_<what>_<condition>_<expected>`

### 3. Appropriate Markers
- Mark tests with correct categories
- Use `@pytest.mark.slow` for long-running tests
- Add `@pytest.mark.skip` with reason for disabled tests

### 4. Fixtures
- Use pytest fixtures for reusable setup
- Scope fixtures appropriately (function/class/module/session)
- Document complex fixtures

### 5. Assertions
- Use specific assertions
- Include helpful error messages
- Test both success and failure cases

## Continuous Improvement

### Adding New Tests

1. Identify the test category (unit/integration/e2e)
2. Add appropriate markers
3. Place in correct directory
4. Update test groups if needed
5. Document any special requirements

### Maintaining Test Health

```bash
# Find flaky tests
pytest --flake-finder --flake-runs=10

# Update test snapshots
pytest --snapshot-update

# Clean test artifacts
make clean-test
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://testdriven.io/guides/testing-best-practices/)
- [SonarCloud Dashboard](https://sonarcloud.io/project/overview?id=ruleiq)
- Internal Slack: #testing-help