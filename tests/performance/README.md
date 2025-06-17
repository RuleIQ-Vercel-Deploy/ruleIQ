# Performance Testing Suite

Comprehensive performance testing framework for ComplianceGPT backend services.

## Overview

This performance testing suite includes:

- **API Performance Tests**: Benchmark individual API endpoints
- **Database Performance Tests**: Test database query performance and scaling
- **Load Testing**: Simulate realistic user load with Locust
- **Memory Testing**: Monitor memory usage under various conditions
- **Concurrency Testing**: Test system behavior under concurrent access

## Quick Start

### Prerequisites

```bash
# Install performance testing dependencies
pip install pytest-benchmark locust psutil pandas

# Ensure test database is running
docker-compose up -d postgres redis
```

### Running All Performance Tests

```bash
# Run complete performance test suite
python tests/performance/run_performance_tests.py

# Run with load testing (requires running application)
python tests/performance/run_performance_tests.py --load-tests --users 20 --duration 120s
```

### Running Specific Test Categories

```bash
# API performance only
pytest tests/performance/test_api_performance.py --benchmark-only

# Database performance only  
pytest tests/performance/test_database_performance.py --benchmark-only

# Load testing only
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

## Test Categories

### 1. API Performance Tests (`test_api_performance.py`)

Benchmarks critical API endpoints for response time and throughput:

- Authentication performance
- Evidence CRUD operations
- Search functionality
- Dashboard loading
- AI chat responses
- Concurrent request handling
- Bulk operations

**Key Metrics:**
- Mean response time
- 95th percentile response time
- Requests per second
- Memory usage during operations

### 2. Database Performance Tests (`test_database_performance.py`)

Tests database operations under various conditions:

- Query scaling with data volume
- Full-text search performance
- Complex aggregation queries
- Join query optimization
- Connection pool management
- Transaction performance
- Bulk operations
- Index effectiveness

**Key Metrics:**
- Query execution time
- Connection handling
- Memory usage
- Concurrent operation performance

### 3. Load Testing (`locustfile.py`)

Simulates realistic user scenarios:

- **ComplianceUser**: Standard compliance workflows
- **AIAssistantUser**: AI chat interactions
- **ReportingUser**: Report generation and analytics
- **StressTestUser**: High-intensity operations
- **PeakTrafficScenario**: Peak usage simulation

**User Scenarios:**
- Complete user onboarding workflow
- Daily compliance activities
- Evidence management
- Report generation
- AI assistance usage

### 4. Advanced Scenarios

#### WebSocket Performance
```python
# Test WebSocket chat performance
class ChatWebSocketUser(HttpUser):
    # Tests real-time chat performance
```

#### Database Stress Testing
```python
# Test database under heavy concurrent load
class DatabaseStressUser(AuthenticatedUser):
    # Complex queries, concurrent updates, large datasets
```

#### Memory Optimization
```python
# Test memory usage with large datasets
def test_memory_usage_optimization():
    # Monitor memory during large result processing
```

## Configuration

### Performance Test Runner Configuration

Create `performance_config.json`:

```json
{
  "warmup_iterations": 3,
  "benchmark_rounds": 10,
  "run_load_tests": true,
  "locust": {
    "users": 50,
    "spawn_rate": 5,
    "duration": "300s",
    "host": "http://localhost:8000"
  },
  "thresholds": {
    "api_response_time": 2.0,
    "database_query_time": 1.0,
    "memory_increase_mb": 100
  }
}
```

### pytest-benchmark Configuration

```ini
# In pytest.ini
[tool:pytest]
addopts = 
    --benchmark-warmup=3
    --benchmark-rounds=10
    --benchmark-sort=mean
    --benchmark-json=benchmark_results.json
```

## Performance Thresholds

### API Performance
- Authentication: < 500ms mean
- Evidence creation: < 1s mean  
- Search operations: < 800ms mean
- Dashboard loading: < 1.5s mean
- AI responses: < 3s mean

### Database Performance
- Simple queries: < 200ms mean
- Complex queries: < 2s mean
- Aggregations: < 300ms mean
- Bulk operations: < 2s for 100 items

### Load Testing
- < 5% failure rate under normal load
- < 2s average response time under load
- Supports 100+ concurrent users

### Resource Usage
- Memory increase < 100MB during tests
- CPU usage < 80% under normal load

## Running in CI/CD

### GitHub Actions Example

```yaml
name: Performance Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  performance:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest-benchmark locust psutil pandas
      
      - name: Run performance tests
        run: |
          python tests/performance/run_performance_tests.py \
            --exclude "Load Testing" \
            --benchmark-compare baseline_results.json
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: |
            performance_report_*.json
            benchmark_results.json
```

## Interpreting Results

### Benchmark Results
```json
{
  "benchmarks": [
    {
      "name": "test_evidence_creation_performance",
      "stats": {
        "mean": 0.845,     // Average time in seconds
        "stddev": 0.123,   // Standard deviation
        "min": 0.678,      // Fastest execution
        "max": 1.234,      // Slowest execution
        "rounds": 10       // Number of test rounds
      }
    }
  ]
}
```

### Load Test Results
```
Name                 # reqs  # fails  Avg    Min    Max    Med   req/s failures/s
GET /api/evidence     1250      0     125     95    450    120    12.5     0.00
POST /api/evidence     500      2     340    180    890    320     5.0     0.02
```

### Performance Issues Detection

The test runner automatically identifies:

- **Slow Response Times**: > 2s mean response time
- **High Failure Rates**: > 5% request failures  
- **Resource Issues**: > 80% CPU or > 85% memory
- **Regression Detection**: Performance degradation vs baseline

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Ensure test database is running
   docker-compose up -d postgres
   ```

2. **High Memory Usage**
   ```bash
   # Monitor memory during tests
   python tests/performance/run_performance_tests.py --include "Memory Testing"
   ```

3. **Load Test Failures**
   ```bash
   # Start application before load tests
   python main.py &
   python tests/performance/run_performance_tests.py --load-tests
   ```

### Performance Debugging

1. **Enable SQL Logging**
   ```python
   # In test configuration
   logging.basicConfig()
   logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
   ```

2. **Profile Slow Tests**
   ```bash
   # Use cProfile for detailed profiling
   python -m cProfile -o profile.stats tests/performance/test_api_performance.py
   ```

3. **Monitor Resource Usage**
   ```bash
   # Use system monitoring during tests
   htop  # In separate terminal during test execution
   ```

## Extending Performance Tests

### Adding New Benchmark Tests

```python
def test_new_feature_performance(self, benchmark, client, authenticated_headers):
    """Benchmark new feature performance"""
    
    def new_feature_operation():
        response = client.post("/api/new-feature", 
                             json={"test": "data"}, 
                             headers=authenticated_headers)
        assert response.status_code == 200
        return response.json()
    
    result = benchmark(new_feature_operation)
    
    # Performance assertions
    assert benchmark.stats.mean < 1.0  # < 1s mean
    assert benchmark.stats.max < 3.0   # < 3s max
```

### Adding Load Test Scenarios

```python
class NewFeatureUser(AuthenticatedUser):
    """Test new feature under load"""
    wait_time = between(1, 3)
    
    @task(5)
    def use_new_feature(self):
        """Use new feature repeatedly"""
        response = self.client.post("/api/new-feature",
                                  json={"test": "data"},
                                  headers=self.headers)
        if response.status_code != 200:
            print(f"New feature failed: {response.status_code}")
```

## Best Practices

1. **Test Data Management**
   - Use isolated test data for each test
   - Clean up test data after completion
   - Use realistic data volumes

2. **Performance Assertions**
   - Set realistic performance thresholds
   - Consider different environments (CI vs local)
   - Monitor performance trends over time

3. **Resource Management**
   - Monitor memory usage during tests
   - Clean up connections and resources
   - Use connection pooling appropriately

4. **Continuous Monitoring**
   - Run performance tests regularly
   - Compare against baseline results
   - Alert on performance regressions

5. **Documentation**
   - Document performance requirements
   - Explain test scenarios and expectations
   - Maintain performance test documentation