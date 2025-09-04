# Test Suite Remediation Plan - Agentic Architecture Update

## Current Status (August 27, 2025)
- **Total Tests**: 894 collected
- **Executed**: 550 tests (after filtering collection errors)
- **Passed**: 465 tests
- **Failed**: 85 tests
- **Errors**: 366 (mostly collection/import errors)
- **Current Pass Rate**: 84.5%
- **Target Pass Rate**: 95%
- **Gap**: 10.5%

## Most Affected Test Modules
Based on failure analysis, these modules need priority attention:

### Critical Failures (20+ failures each)
1. **test_integration.py** (27 failures)
   - Root Cause: Old synchronous AI service calls
   - Fix: Update to use LangGraph async workflows
   
2. **test_ai_cost_management.py** (22 failures)
   - Root Cause: Changed cost tracking with agentic structure
   - Fix: Update cost tracking assertions for graph execution

3. **unit/services/test_ai_assistant.py** (21 failures)
   - Root Cause: ComplianceAssistant now uses graph-based flows
   - Fix: Mock graph nodes instead of direct AI calls

### High Priority (15-20 failures)
4. **test_services.py** (20 failures)
5. **test_security.py** (20 failures)
6. **integration/api/test_ai_assessments.py** (20 failures)
7. **test_usability.py** (19 failures)
8. **test_ai_ethics.py** (18 failures)

## Root Causes of Test Failures

### 1. Agentic Architecture Changes
- Old tests expect synchronous AI calls
- New system uses LangGraph with async graph execution
- State management changed from session-based to graph-based

### 2. Import/Collection Errors
- Missing dependencies for old modules
- Circular imports from refactoring
- Deprecated service classes

### 3. Mock Structure Mismatches
- Tests mock old AI service methods
- Need to mock graph nodes and edges instead

## Remediation Strategy

### Phase 1: Quick Wins (1-2 hours)
1. Fix import errors by updating paths
2. Remove tests for deprecated services
3. Skip tests that need full rewrite (temporary)

### Phase 2: Mock Updates (2-3 hours)
1. Create new mock fixtures for LangGraph components
2. Update existing mocks to match new interfaces
3. Add graph state mocks

### Phase 3: Test Rewrites (3-4 hours)
1. Rewrite critical integration tests
2. Update AI service tests for agentic flow
3. Fix state management tests

## Implementation Plan

### Step 1: Create Test Fixtures for Agentic Architecture
```python
# tests/fixtures/graph_fixtures.py
@pytest.fixture
def mock_compliance_graph():
    """Mock the compliance assessment graph."""
    # Mock graph with nodes and edges
    pass

@pytest.fixture  
def mock_graph_state():
    """Mock ComplianceState for tests."""
    # Create test state
    pass
```

### Step 2: Update Base Test Classes
```python
# tests/base_test.py
class AgenticTestCase:
    """Base class for testing agentic workflows."""
    
    async def execute_graph(self, graph, state):
        """Helper to execute graph in tests."""
        pass
```

### Step 3: Fix Priority Test Modules
- Start with test_integration.py
- Then test_ai_assistant.py
- Follow with API tests

## Expected Outcome
- **Target**: 95% pass rate (522+ passing tests out of 550)
- **Timeline**: 8-10 hours total work
- **Approach**: Focus on high-impact fixes first

## Next Actions
1. Create graph test fixtures
2. Fix import errors
3. Update 3-4 critical test files
4. Run full suite to verify improvements