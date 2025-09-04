# Phase 2: Error Handling Centralization

Create a centralized error handling system for the LangGraph implementation.

## Current Issues to Fix

1. No dedicated error handling nodes
2. Try-except blocks scattered throughout node functions
3. No consistent retry strategy
4. Missing error recovery patterns

## Required Changes

### File: Create `langgraph_agent/graph/error_handler.py`

Implement a comprehensive error handling node:

```python
from langgraph_agent.graph.state import ComplianceAgentState
from typing import Dict, Any
import asyncio
import time

class ErrorHandlerNode:
    """Centralized error handling for all graph nodes."""
    
    def __init__(self):
        self.retry_strategies = {
            "rate_limit": self._handle_rate_limit,
            "database": self._handle_database_error,
            "api": self._handle_api_error,
            "validation": self._handle_validation_error,
            "timeout": self._handle_timeout_error
        }
        self.max_retries = 3
        
    async def process(self, state: ComplianceAgentState) -> ComplianceAgentState:
        """Main error processing logic."""
        # Classify error type
        error_type = self._classify_error(state)
        
        # Check retry limit
        if state.get("retry_count", 0) >= self.max_retries:
            return await self._activate_fallback(state)
        
        # Apply appropriate strategy
        handler = self.retry_strategies.get(error_type, self._generic_retry)
        return await handler(state)
```

### File: Update `langgraph_agent/graph/app.py`

1. **Add error handler node** to the graph:
   ```python
   graph.add_node("error_handler", error_handler_node.process)
   ```

2. **Add conditional edges** from all nodes to error handler:
   ```python
   for node_name in ["router", "compliance_analyzer", "obligation_finder"]:
       graph.add_conditional_edges(
           node_name,
           lambda x: "error_handler" if x.get("errors") else None
       )
   ```

3. **Implement error recovery routing**:
   ```python
   graph.add_conditional_edges(
       "error_handler",
       lambda x: x.get("last_successful_node", "router")
   )
   ```

### File: Update node implementations

Remove try-except blocks from:
- `router_node()`
- `compliance_analyzer_node()`
- `obligation_finder_node()`
- `evidence_collector_node()`

Instead, let errors propagate to the error handler.

## Error Classification Logic

```python
def _classify_error(self, state: ComplianceAgentState) -> str:
    """Classify error type from state."""
    if not state.get("errors"):
        return "unknown"
    
    last_error = state["errors"][-1]
    error_msg = str(last_error).lower()
    
    if "rate limit" in error_msg:
        return "rate_limit"
    elif "database" in error_msg or "connection" in error_msg:
        return "database"
    elif "api" in error_msg or "endpoint" in error_msg:
        return "api"
    elif "validation" in error_msg or "invalid" in error_msg:
        return "validation"
    elif "timeout" in error_msg:
        return "timeout"
    
    return "unknown"
```

## Retry Strategies

1. **Rate Limit**: Exponential backoff with jitter
2. **Database**: Linear backoff with connection pool refresh
3. **API**: Retry with fallback endpoints
4. **Validation**: No retry, immediate fallback
5. **Timeout**: Increase timeout and retry

## Testing Requirements

1. Test each error type classification
2. Verify retry strategies work
3. Test max retry limit
4. Validate fallback activation
5. Check state preservation during retries

## Success Criteria

- [ ] Error handler node created and integrated
- [ ] All nodes connected to error handler
- [ ] Retry strategies implemented
- [ ] Fallback mechanism working
- [ ] Tests passing for error scenarios
