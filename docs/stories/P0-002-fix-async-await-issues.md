# Story: Fix Async/Await Implementation Issues

## Story ID: P0-002
**Epic**: EPIC-2025-001
**Priority**: P0 - CRITICAL
**Sprint**: Immediate
**Story Points**: 3
**Owner**: Backend Team

## Status
**Current**: Draft
**Target**: Done
**Blocked By**: P0-001 (QueryCategory Enum)

## Story
**AS A** developer  
**I WANT** all async/await operations to be properly implemented  
**SO THAT** the application runs without coroutine errors and warnings

## Background
Quinn's review identified multiple async/await issues including:
- Coroutine comparison errors in create_iq_agent
- Unawaited Neo4j operations
- Improper async context managers
- Missing error handling for async operations

## Acceptance Criteria
1. ✅ **GIVEN** the create_iq_agent function  
   **WHEN** comparing or checking coroutines  
   **THEN** proper await syntax is used and no comparison warnings occur

2. ✅ **GIVEN** any Neo4j database operation  
   **WHEN** executed in an async context  
   **THEN** it must be properly awaited with appropriate error handling

3. ✅ **GIVEN** async context managers  
   **WHEN** used for resource management  
   **THEN** they must use `async with` syntax correctly

4. ✅ **GIVEN** any async function  
   **WHEN** an error occurs  
   **THEN** it must be caught and handled appropriately without exposing internals

## Technical Requirements

### Key Issues to Fix
1. **Coroutine Comparison** in `services/iq_agent.py`:
   ```python
   # WRONG
   if some_coroutine == something:
   
   # CORRECT
   result = await some_coroutine
   if result == something:
   ```

2. **Neo4j Operations**:
   ```python
   # Add proper await
   async def query_graph(self, query):
       try:
           result = await self.neo4j.execute_query(query)
           return result
       except Exception as e:
           logger.error(f"Neo4j query failed: {e}")
           raise
   ```

3. **Context Managers**:
   ```python
   # Proper async context manager
   async with self.get_session() as session:
       result = await session.execute(query)
   ```

### Files to Review and Fix
- `services/iq_agent.py` - Main async issues
- `services/compliance_memory_manager.py` - Memory operations
- `services/neo4j_service.py` - Database operations
- Any file with `async def` functions

## Tasks/Subtasks
- [ ] Audit all async functions for proper await usage
- [ ] Fix coroutine comparison in create_iq_agent
- [ ] Add await to all Neo4j operations
- [ ] Implement proper async context managers
- [ ] Add try/except blocks for async error handling
- [ ] Add logging for async operation failures
- [ ] Test concurrent async operations

## Testing
```python
# Test async operations
import asyncio
import pytest

@pytest.mark.asyncio
async def test_async_operations():
    """Test that all async operations complete without warnings"""
    agent = await create_iq_agent(neo4j_service, session)
    assert agent is not None
    
    # Test concurrent operations
    tasks = [agent.process_query(q) for q in test_queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Verify no coroutine warnings
    assert all(not isinstance(r, RuntimeWarning) for r in results)
```

## Definition of Done
- [ ] No coroutine comparison warnings in logs
- [ ] All Neo4j operations properly awaited
- [ ] Async context managers implemented correctly
- [ ] Error handling added for all async operations
- [ ] Integration tests pass without async warnings
- [ ] Code reviewed for async best practices
- [ ] Performance tested with concurrent requests

## Notes
- Run with `python -W error::RuntimeWarning` to catch all async issues
- Use `asyncio.create_task()` for fire-and-forget operations
- Consider using `asyncio.gather()` for parallel operations
- Must complete after P0-001 to test properly

---
*Story created: 2025-01-12*
*Last updated: 2025-01-12*