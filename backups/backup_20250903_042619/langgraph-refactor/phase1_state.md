# Phase 1: State Management Enhancement

Focus on enhancing the state management in `langgraph_agent/graph/state.py` to properly utilize LangGraph features.

## Current Issues to Fix

1. The `ComplianceAgentState` lacks proper reducers for many fields
2. No automatic state merging for dictionaries and lists
3. Missing fields for better error handling and retry logic

## Required Changes

### File: `langgraph_agent/graph/state.py`

1. **Add proper Annotated reducers** to all collection fields:
   - `tool_outputs`: Use dict merger
   - `tool_calls_made`: Use list appender
   - `errors`: Use list appender
   - `meta`: Use dict merger

2. **Add new state fields** for enhanced control:
   ```python
   retry_count: int = 0
   fallback_activated: bool = False
   checkpoint_restore_count: int = 0
   last_successful_node: Optional[str] = None
   node_execution_times: Annotated[Dict[str, float], lambda x, y: {**x, **y}]
   ```

3. **Create helper functions** for state manipulation:
   - `merge_state_updates()` - Safely merge partial state updates
   - `reset_error_state()` - Clear error-related fields
   - `prepare_for_retry()` - Set up state for retry attempt

### File: Create `langgraph_agent/graph/state_utils.py`

Create utility functions for common state operations:
- State validation
- State sanitization
- State metrics calculation
- State diff generation

## Implementation Example

```python
from typing import TypedDict, Annotated, List, Dict, Any
from operator import add

class EnhancedComplianceAgentState(TypedDict):
    # Enhanced collections with proper reducers
    messages: Annotated[List[GraphMessage], add_messages]
    tool_outputs: Annotated[Dict[str, Any], lambda x, y: {**x, **y}]
    tool_calls_made: Annotated[List[Dict[str, Any]], add]
    errors: Annotated[List[SafeFallbackResponse], add]
    meta: Annotated[Dict[str, Any], lambda x, y: {**x, **y}]
    
    # New fields for better control
    retry_count: int
    fallback_activated: bool
    last_successful_node: Optional[str]
    node_execution_times: Annotated[Dict[str, float], lambda x, y: {**x, **y}]
```

## Testing Requirements

1. Verify state merging works correctly
2. Test retry counter increments
3. Validate error accumulation
4. Check metadata preservation

## Success Criteria

- [ ] All collection fields have reducers
- [ ] New control fields added
- [ ] Helper functions implemented
- [ ] Tests passing for state operations
- [ ] No breaking changes to existing functionality
