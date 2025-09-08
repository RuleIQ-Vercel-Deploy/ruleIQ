# RuleIQ LangGraph Testing Strategy

## Overview

This document outlines the Test-Driven Development (TDD) approach for migrating RuleIQ from Celery to LangGraph. All tests must be written BEFORE implementation, ensuring that we define expected behavior before coding.

## Core Testing Principles

### 1. Test-First Development
- **Write tests before code**: Every feature starts with failing tests
- **Red-Green-Refactor cycle**: 
  1. Write failing test (Red)
  2. Write minimal code to pass (Green)
  3. Refactor for clarity and efficiency
- **100% test coverage requirement**: No code ships without tests

### 2. Deterministic Testing
- **Mock LLM responses**: Use temperature=0 and predetermined responses
- **Fixed timestamps**: Use frozen time for reproducible tests
- **Seeded randomness**: Control all random elements in tests
- **Stable test data**: Use factory patterns for consistent test states

## Testing Architecture

### Test Structure
```
tests/
├── conftest.py                 # Global pytest configuration
├── fixtures/                   # Reusable test utilities
│   ├── __init__.py
│   ├── mock_llm.py            # Deterministic LLM mocking
│   ├── state_fixtures.py      # State builders and factories
│   └── graph_fixtures.py      # Graph test harnesses
├── unit/                       # Unit tests
│   ├── test_state_management.py
│   ├── test_nodes.py
│   ├── test_edges.py
│   └── test_checkpointing.py
├── integration/                # Integration tests
│   ├── test_graph_execution.py
│   ├── test_workflow_patterns.py
│   └── test_external_apis.py
└── e2e/                       # End-to-end tests
    ├── test_compliance_workflows.py
    └── test_migration_scenarios.py
```

### Test Categories

#### Unit Tests
- **Purpose**: Test individual components in isolation
- **Scope**: Single functions, classes, or modules
- **Speed**: < 100ms per test
- **Dependencies**: Fully mocked

Example focus areas:
- State field validation
- Individual node logic
- Edge condition evaluation
- Utility functions

#### Integration Tests
- **Purpose**: Test component interactions
- **Scope**: Multiple components working together
- **Speed**: < 1 second per test
- **Dependencies**: Some real, some mocked

Example focus areas:
- Graph construction and validation
- Node-to-node communication
- State persistence and recovery
- External API integration

#### End-to-End Tests
- **Purpose**: Test complete workflows
- **Scope**: Full system behavior
- **Speed**: < 5 seconds per test
- **Dependencies**: Minimal mocking

Example focus areas:
- Complete compliance checking workflows
- Migration from Celery tasks
- Error recovery scenarios
- Performance under load

## Key Testing Patterns

### 1. State Testing Pattern
```python
def test_state_behavior():
    # Arrange - Build test state
    state = StateBuilder()
        .with_company("test-company")
        .with_obligation("SOC2")
        .with_confidence(0.85)
        .build()
    
    # Act - Execute behavior
    result = process_state(state)
    
    # Assert - Verify outcomes
    assert result.status == "completed"
    assert result.confidence >= 0.8
```

### 2. Graph Testing Pattern
```python
def test_graph_execution():
    # Arrange - Create test harness
    harness = GraphTestHarness()
    graph = create_test_graph()
    
    # Act - Execute graph
    result = harness.execute(graph, initial_state)
    
    # Assert - Verify execution path
    harness.assert_path(["start", "process", "complete"])
    harness.assert_node_called("process", times=1)
```

### 3. Mock LLM Pattern
```python
def test_with_mock_llm():
    # Arrange - Configure deterministic responses
    mock_llm = MockLLM()
    mock_llm.add_response("analyze compliance", "compliant")
    
    # Act - Execute with mock
    result = analyze_with_llm(mock_llm, test_data)
    
    # Assert - Verify deterministic outcome
    assert result == "compliant"
    assert mock_llm.call_count == 1
```

## Testing Requirements by Phase

### Phase 0: Foundation Tests
- [ ] State initialization and validation
- [ ] Basic graph construction
- [ ] Node execution order
- [ ] Conditional routing
- [ ] Error handling basics

### Phase 1: Celery Migration Tests
- [ ] Task signature compatibility
- [ ] Result format preservation
- [ ] Error handling parity
- [ ] Performance benchmarks
- [ ] Backward compatibility

### Phase 2: Observability Tests
- [ ] Metrics emission
- [ ] Trace continuity
- [ ] Log correlation
- [ ] Performance profiling
- [ ] Cost tracking

### Phase 3: AI Evaluation Tests
- [ ] Confidence scoring
- [ ] Citation validation
- [ ] Hallucination detection
- [ ] Output consistency
- [ ] Feedback loop integration

### Phase 4-7: Advanced Feature Tests
- [ ] Evidence orchestration
- [ ] Multi-agent coordination
- [ ] Security compliance
- [ ] Regulatory updates
- [ ] Filing automation

## Mocking Strategy

### External Services
```python
# Always mock external APIs in tests
@pytest.fixture
def mock_regulation_api(mocker):
    mock = mocker.patch("app.external.regulation_api")
    mock.get_obligations.return_value = TEST_OBLIGATIONS
    return mock
```

### Database
```python
# Use test database with transactions
@pytest.fixture
def test_db(db):
    with db.transaction() as tx:
        yield tx
        tx.rollback()  # Clean rollback after each test
```

### Time and Dates
```python
# Freeze time for deterministic tests
@pytest.fixture
def frozen_time():
    with freeze_time("2024-01-15 10:00:00") as frozen:
        yield frozen
```

## Performance Testing

### Benchmarks
- Graph execution: < 100ms for simple paths
- State persistence: < 50ms per checkpoint
- LLM calls: Mocked to 0ms, real tracked separately
- Database queries: < 10ms per query

### Load Testing
```python
@pytest.mark.performance
def test_concurrent_executions():
    # Test 100 concurrent graph executions
    # Assert no deadlocks or race conditions
    # Verify linear scaling up to 10x load
```

## Continuous Testing

### Pre-commit Hooks
```yaml
- id: pytest-unit
  name: Run unit tests
  entry: pytest tests/unit --fail-fast
  language: system
  pass_filenames: false
```

### CI Pipeline
```yaml
test:
  stage: test
  script:
    - pytest tests/unit --cov=app --cov-report=term
    - pytest tests/integration
    - pytest tests/e2e --markers=smoke
```

### Test Coverage Requirements
- Minimum 80% overall coverage
- 100% coverage for critical paths
- 90% coverage for state management
- 85% coverage for graph execution

## Testing Tools

### Required Packages
```python
# pyproject.toml or requirements-test.txt
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-mock>=3.10.0
pytest-cov>=4.0.0
pytest-timeout>=2.1.0
pytest-benchmark>=4.0.0
freezegun>=1.2.0
faker>=18.0.0
factory-boy>=3.2.0
hypothesis>=6.0.0  # For property-based testing
```

### Recommended VS Code Extensions
- Python Test Explorer
- Coverage Gutters
- Test Explorer UI

## Test Naming Conventions

### Test File Names
- `test_<module_name>.py` for unit tests
- `test_integration_<feature>.py` for integration
- `test_e2e_<workflow>.py` for end-to-end

### Test Function Names
- Start with `test_`
- Describe the scenario: `test_<scenario>_<expected_outcome>`
- Examples:
  - `test_state_initialization_with_defaults`
  - `test_parallel_execution_completes_all_branches`
  - `test_retry_exhaustion_raises_error`

### Test Class Names
- Group related tests: `Test<Component><Aspect>`
- Examples:
  - `TestStateManagement`
  - `TestConditionalEdges`
  - `TestErrorRecovery`

## Common Testing Scenarios

### 1. Happy Path Testing
```python
def test_compliance_check_happy_path():
    """Test successful compliance check workflow."""
    # Test the ideal scenario with no errors
```

### 2. Error Path Testing
```python
def test_compliance_check_with_api_failure():
    """Test graceful handling of API failures."""
    # Test error recovery and fallback behavior
```

### 3. Edge Case Testing
```python
def test_compliance_check_with_empty_obligations():
    """Test behavior with no obligations to check."""
    # Test boundary conditions
```

### 4. Performance Testing
```python
@pytest.mark.benchmark
def test_state_persistence_performance(benchmark):
    """Benchmark state persistence operations."""
    result = benchmark(persist_state, large_state)
    assert result.timing < 0.1  # 100ms threshold
```

## Test Maintenance

### Regular Reviews
- Weekly: Review failing tests
- Monthly: Update test data and mocks
- Quarterly: Performance benchmark review
- Yearly: Full test suite audit

### Test Refactoring Rules
1. Keep tests simple and readable
2. Avoid test interdependencies
3. Minimize test fixture complexity
4. Extract common patterns to fixtures
5. Document non-obvious test logic

### Debugging Failed Tests
1. Check test assumptions first
2. Verify mock configurations
3. Review recent code changes
4. Check for environment differences
5. Use pytest debugging flags:
   ```bash
   pytest -vvs --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb
   ```

## Migration Testing Strategy

### Parallel Testing Phase
During migration, run both Celery and LangGraph implementations:
```python
def test_celery_langgraph_parity():
    celery_result = run_celery_task(test_input)
    langgraph_result = run_langgraph_workflow(test_input)
    assert celery_result == langgraph_result
```

### Gradual Cutover Testing
1. Shadow mode: Run both, use Celery results
2. Comparison mode: Run both, alert on differences
3. Canary mode: Route percentage to LangGraph
4. Full migration: 100% LangGraph

### Rollback Testing
Ensure ability to quickly revert:
```python
def test_rollback_to_celery():
    # Test that we can disable LangGraph and fall back to Celery
    # without data loss or service disruption
```

## Test Metrics and Reporting

### Key Metrics
- Test execution time
- Test flakiness rate
- Coverage percentage
- Test-to-code ratio
- Defect escape rate

### Reporting Tools
- Coverage reports: `pytest-cov`
- Test reports: `pytest-html`
- Performance reports: `pytest-benchmark`
- Flakiness detection: `pytest-rerunfailures`

## Conclusion

This testing strategy ensures that our migration from Celery to LangGraph is:
1. **Safe**: No functionality is lost
2. **Reliable**: All edge cases are covered
3. **Observable**: Clear metrics and monitoring
4. **Reversible**: Can roll back if needed
5. **Performant**: Meets or exceeds current performance

By following TDD principles and this comprehensive testing strategy, we ensure that each phase of the migration is validated before proceeding to the next.