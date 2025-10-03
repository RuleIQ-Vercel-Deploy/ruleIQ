# AI Refactoring Functional Testing Guide

**Date**: 2025-09-30
**Purpose**: Standardized approach for functional testing of ported AI service methods

---

## Overview

When porting methods from `assistant_legacy.py` to modular domain services, we **MUST** create functional tests that verify actual behavior, not just structural integrity.

## Why Functional Tests?

**Structural tests** only verify:
- Imports work
- Methods exist
- Basic instantiation

**Functional tests** verify:
- Method calls correct dependencies
- Parameters are passed correctly
- Output format matches legacy
- Error handling works
- Business logic executes properly

## Testing Pattern

### 1. Test File Structure

```python
"""
Functional tests for [ServiceName]

These tests verify that ported methods actually work with real logic,
not just structural verification.

These are unit tests with complete mocking - no database required.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4
from datetime import datetime

# Mark all tests in this module as not requiring database
pytestmark = pytest.mark.unit

from services.ai.domains.[service_name] import [ServiceClass]


@pytest.fixture
def mock_response_generator():
    """Mock response generator that simulates AI response."""
    generator = Mock()
    generator.generate_simple = AsyncMock(return_value="Mock AI response")
    return generator


@pytest.fixture
def mock_context_manager():
    """Mock context manager with realistic business data."""
    manager = AsyncMock()
    manager.get_conversation_context.return_value = {
        'business_profile': {'company_name': 'Test Corp'},
        'recent_evidence': []
    }
    return manager


@pytest.fixture
def [service_name]([dependencies]):
    """Create service with mocks."""
    return [ServiceClass]([dependencies])


@pytest.mark.asyncio
class Test[MethodName]Functional:
    """Functional tests for [method_name] method."""

    async def test_calls_dependencies_correctly(self, service, mocks):
        """Verify method calls dependencies with correct parameters."""
        # Test implementation
        pass

    async def test_output_format_matches_legacy(self, service, mocks):
        """Verify output format matches legacy implementation."""
        # Test implementation
        pass

    async def test_error_handling(self, service, mocks):
        """Verify proper exception handling."""
        # Test implementation
        pass
```

### 2. Test Categories

Every ported method should have tests in these categories:

#### A. Dependency Call Verification
Verify the method calls each dependency:
- Context manager
- Response generator
- Prompt templates
- Other services

```python
async def test_calls_context_manager(self, service, mock_context_manager):
    """Verify method calls context manager to get business context."""
    await service.method(...)

    # Verify called
    mock_context_manager.get_conversation_context.assert_called_once()

    # Verify parameters
    call_args = mock_context_manager.get_conversation_context.call_args
    assert call_args[0][1] == expected_business_id
```

#### B. Parameter Correctness
Verify parameters are passed correctly:

```python
async def test_calls_response_generator(self, service, mock_generator):
    """Verify method calls response generator with correct parameters."""
    await service.method(...)

    call_kwargs = mock_generator.generate_simple.call_args[1]

    assert 'system_prompt' in call_kwargs
    assert 'expected text' in call_kwargs['system_prompt'].lower()
    assert call_kwargs['task_type'] == 'expected_type'
    assert call_kwargs['context']['key'] == expected_value
```

#### C. Output Format Verification
Verify output matches legacy format:

```python
async def test_output_format_matches_legacy(self, service):
    """Verify output format matches legacy implementation."""
    result = await service.method(...)

    # Legacy returns: List[Dict[str, Any]]
    assert isinstance(result, list)
    assert len(result) == 1

    # Legacy format: [{'key1': ..., 'key2': ..., 'key3': ...}]
    assert 'key1' in result[0]
    assert 'key2' in result[0]
    assert 'key3' in result[0]

    # Verify timestamp format
    datetime.fromisoformat(result[0]['generated_at'])
```

#### D. Error Handling
Verify exceptions are handled correctly:

```python
async def test_handles_not_found(self, service):
    """Verify proper exception handling when resource not found."""
    from core.exceptions import NotFoundException

    service.context_manager.get_conversation_context.side_effect = NotFoundException(
        "Business profile not found"
    )

    with pytest.raises(NotFoundException):
        await service.method(...)


async def test_handles_generator_failure(self, service):
    """Verify proper exception handling when AI generation fails."""
    from core.exceptions import BusinessLogicException

    service.response_generator.generate_simple.side_effect = Exception("API timeout")

    with pytest.raises(BusinessLogicException) as exc_info:
        await service.method(...)

    assert "unexpected error" in str(exc_info.value).lower()
```

#### E. Legacy Comparison Tests
Verify behavior matches legacy:

```python
async def test_matches_legacy_call_sequence(self, service, mocks):
    """Verify method follows same call sequence as legacy implementation."""
    await service.method(...)

    # Verify call sequence matches legacy:
    # 1. Get context
    assert mocks['context_manager'].get_conversation_context.called

    # 2. Build prompt
    assert mocks['prompt_templates'].get_prompt.called

    # 3. Generate response
    assert mocks['response_generator'].generate_simple.called

    # Verify order
    assert mocks['context_manager'].get_conversation_context.call_count == 1
    assert mocks['prompt_templates'].get_prompt.call_count == 1
    assert mocks['response_generator'].generate_simple.call_count == 1
```

### 3. Running Tests

#### Via Pytest (may have database fixture issues)
```bash
pytest tests/unit/ai/test_[service]_functional.py -v
```

#### Via Manual Python Script (recommended for development)
```bash
python << 'EOF'
import asyncio
from unittest.mock import AsyncMock, Mock
# ... setup mocks and run tests manually
EOF
```

#### Verification Script
Create a standalone script to verify tests pass:

```bash
source .venv/bin/activate && python << 'PYTHON_EOF'
import asyncio
from unittest.mock import AsyncMock, Mock
from services.ai.domains.[service] import [Service]

async def run_tests():
    # Create mocks
    mock_generator = Mock()
    mock_generator.generate_simple = AsyncMock(return_value="Test response")
    # ... other mocks

    # Create service
    service = [Service](mock_generator, ...)

    # Test 1
    result = await service.method(...)
    assert result is not None, "❌ Test failed"
    print("✅ Test 1 PASSED")

    # More tests...

    print("\n🎉 ALL TESTS PASSED!")

asyncio.run(run_tests())
PYTHON_EOF
```

## Example: EvidenceService.get_recommendations()

See `tests/unit/ai/test_evidence_service_functional.py` for complete example.

**Key tests:**
1. ✅ Calls context manager with correct business_profile_id
2. ✅ Calls prompt templates with framework and context
3. ✅ Calls response generator with correct system prompt and task_type
4. ✅ Returns list with single dict containing: framework, recommendations, generated_at
5. ✅ Includes AI response in output
6. ✅ Works with different frameworks (GDPR, ISO27001, SOC2, HIPAA)
7. ✅ Preserves control_id parameter for API compatibility
8. ✅ Handles NotFoundException correctly
9. ✅ Handles generator failures with BusinessLogicException
10. ✅ Matches legacy call sequence
11. ✅ Output format matches legacy exactly

**Manual Test Results:**
```
✅ Test 1 PASSED: Context manager was called
✅ Test 2 PASSED: Response generator was called
✅ Test 3 PASSED: Result is a list with 1 item
✅ Test 4 PASSED: Result has correct framework
✅ Test 5 PASSED: Result has correct recommendations
✅ Test 6 PASSED: Result has valid generated_at timestamp
✅ Test 7 PASSED: Response generator called with correct system prompt
✅ Test 8 PASSED: task_type is correct
✅ Test 9 PASSED: Framework passed in context

🎉 ALL 9 FUNCTIONAL TESTS PASSED!
```

## Checklist for Each Ported Method

Before marking a method as "complete", verify:

- [ ] Functional test file created in `tests/unit/ai/`
- [ ] Tests cover all 5 categories (A-E above)
- [ ] Tests verify dependency calls
- [ ] Tests verify parameter correctness
- [ ] Tests verify output format matches legacy
- [ ] Tests verify error handling
- [ ] Tests compare with legacy call sequence
- [ ] Manual test script runs successfully
- [ ] All tests pass (via pytest or manual script)
- [ ] Test documentation updated

## Benefits

1. **Confidence**: Know the ported code actually works
2. **Regression Prevention**: Catch breaking changes immediately
3. **Documentation**: Tests serve as executable documentation
4. **Debugging**: Easy to isolate issues
5. **Maintenance**: Future changes can be verified quickly

## Next Steps After Testing

Once functional tests pass:

1. Mark method as ✅ Complete in analysis docs
2. Update migration progress tracking
3. Move to next method in priority order
4. Consider integration testing if multiple services interact

---

**Remember**: Structural verification is NOT enough. Every ported method needs functional tests that prove it works!
