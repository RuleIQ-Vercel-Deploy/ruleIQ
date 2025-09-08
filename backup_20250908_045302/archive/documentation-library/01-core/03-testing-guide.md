# NexCompli Testing Guide

## Overview

NexCompli uses a sophisticated chunked test execution strategy to optimize test performance and reliability. Tests are organized into logical chunks and executed with optimal parallelism based on test type and system resources.

## Quick Start

```bash
# Fast unit tests (recommended for development)
make test-fast

# Integration tests
make test-integration

# Complete test suite
make test-full

# CI/CD optimized
make test-ci
```

## Test Execution Modes

### 🚀 Fast Mode (`test-fast`)
- **Purpose**: Quick feedback during development
- **Includes**: Unit tests only
- **Parallelism**: High (auto-detected CPU cores)
- **Duration**: ~2-5 minutes
- **Use case**: Development, pre-commit checks

```bash
make test-fast
# or
python scripts/run_tests_chunked.py --mode fast
```

### 🔗 Integration Mode (`test-integration`)
- **Purpose**: Test API endpoints and service interactions
- **Includes**: Integration tests with database
- **Parallelism**: Medium (2-4 workers)
- **Duration**: ~5-10 minutes
- **Use case**: Feature testing, API validation

```bash
make test-integration
# or
python scripts/run_tests_chunked.py --mode integration
```

### ⚡ Performance Mode (`test-performance`)
- **Purpose**: Benchmark and load testing
- **Includes**: Performance and benchmark tests
- **Parallelism**: Sequential (for accurate measurements)
- **Duration**: ~15-30 minutes
- **Use case**: Performance validation, optimization

```bash
make test-performance
# or
python scripts/run_tests_chunked.py --mode performance
```

### 🎪 Full Mode (`test-full`)
- **Purpose**: Complete test coverage
- **Includes**: All test categories in optimized chunks
- **Parallelism**: Mixed (optimized per chunk type)
- **Duration**: ~20-40 minutes
- **Use case**: Release validation, comprehensive testing

```bash
make test-full
# or
python scripts/run_tests_chunked.py --mode full
```

### 🏗️ CI Mode (`test-ci`)
- **Purpose**: Optimized for CI/CD environments
- **Includes**: Critical tests with fixed parallelism
- **Parallelism**: Fixed (4 workers for consistency)
- **Duration**: ~10-15 minutes
- **Use case**: GitHub Actions, automated testing

```bash
make test-ci
# or
python scripts/run_tests_chunked.py --mode ci
```

## Specialized Test Categories

### 🤖 AI Tests (`test-ai`)
- AI compliance accuracy
- Model validation
- Ethical AI testing

### 🔒 Security Tests (`test-security`)
- Authentication and authorization
- Security vulnerability testing
- Access control validation

### 🎯 E2E Tests (`test-e2e`)
- Complete user workflows
- End-to-end integration
- User journey validation

## Test Organization

```
tests/
├── unit/           # Fast, isolated unit tests
├── integration/    # API and service integration tests
├── performance/    # Performance and benchmark tests
├── e2e/           # End-to-end workflow tests
├── security/      # Security and auth tests
├── ai/            # AI and compliance tests
└── monitoring/    # Monitoring and metrics tests
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.ai` - AI-related tests
- `@pytest.mark.slow` - Tests taking >5 seconds
- `@pytest.mark.smoke` - Quick smoke tests

## Performance Optimization

### System Resource Detection
The test runner automatically detects system resources and optimizes parallelism:

```bash
# Check system info
make test-info
```

### Parallelism Strategy
- **Unit tests**: High parallelism (auto-detected cores)
- **Integration tests**: Medium parallelism (2-4 workers)
- **Database tests**: Sequential (1 worker)
- **Performance tests**: Sequential (accurate measurements)
- **E2E tests**: Sequential (workflow integrity)

### Memory Management
- Automatic worker count adjustment based on available memory
- ~2GB memory allocation per worker
- Graceful degradation on resource-constrained systems

## Development Workflow

### Pre-commit Testing
```bash
# Quick validation before committing
make test-fast
```

### Feature Development
```bash
# Test specific functionality
make test-integration
```

### Release Preparation
```bash
# Comprehensive validation
make test-full
```

### Continuous Development
```bash
# Watch mode (requires pytest-watch)
make test-watch
```

## Advanced Usage

### Custom Test Execution
```bash
# Run specific test file
make test-file FILE=tests/unit/test_specific.py

# Run tests matching pattern
make test-pattern PATTERN="test_user_*"

# Run tests with specific marker
python -m pytest -m "unit and not slow"
```

### Coverage Reports
```bash
# Generate coverage report
make test-coverage

# Fast coverage (unit tests only)
make test-coverage-fast
```

### Benchmarking
```bash
# Run only benchmark tests
make test-benchmark
```

### Debugging
```bash
# Sequential execution for debugging
make test-sequential

# Verbose output
python -m pytest -v --tb=long
```

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Tests
  run: make test-ci

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### Performance Monitoring
```yaml
- name: Performance Tests
  run: make test-performance
  
- name: Upload Benchmark Results
  uses: benchmark-action/github-action-benchmark@v1
```

## Troubleshooting

### Common Issues

1. **Memory Issues**
   ```bash
   # Reduce parallelism
   python scripts/run_tests_chunked.py --mode fast --max-concurrent 2
   ```

2. **Database Connection Issues**
   ```bash
   # Run database tests sequentially
   python -m pytest tests/integration/database/ -n 1
   ```

3. **Timeout Issues**
   ```bash
   # Increase timeout for slow tests
   python -m pytest --timeout=600
   ```

### Performance Tuning

1. **Optimize Worker Count**
   - Monitor CPU and memory usage
   - Adjust based on test type and system resources

2. **Test Isolation**
   - Ensure tests don't interfere with each other
   - Use proper fixtures and cleanup

3. **Resource Management**
   - Clean up test artifacts regularly
   - Monitor disk space usage

## Best Practices

1. **Test Categories**
   - Keep unit tests fast and isolated
   - Use appropriate markers
   - Minimize external dependencies

2. **Parallel Execution**
   - Design tests for parallel execution
   - Avoid shared state between tests
   - Use proper database isolation

3. **Performance Testing**
   - Run performance tests sequentially
   - Use consistent test environments
   - Monitor for performance regressions

4. **CI/CD**
   - Use CI mode for consistent results
   - Cache dependencies when possible
   - Fail fast on critical test failures

## Monitoring and Metrics

The test execution provides detailed metrics:
- Execution time per chunk
- Success/failure rates
- Resource utilization
- Parallel efficiency

Use these metrics to optimize test execution and identify bottlenecks.
