# Story: Repair LLM Integration

## Story ID: P0-003
**Epic**: EPIC-2025-001
**Priority**: P0 - CRITICAL
**Sprint**: Immediate
**Story Points**: 2
**Owner**: Backend Team

## Status
**Current**: Draft
**Target**: Done
**Blocked By**: P0-001 (QueryCategory Enum)

## Story
**AS A** system developer  
**I WANT** the LLM integration to use the correct async methods  
**SO THAT** AI operations work without deprecated method errors

## Background
Quinn's review found that the LLM integration is using the deprecated `ainvoke` method which no longer exists in the current LangChain version. This needs to be replaced with `agenerate` or `acall`. Additionally, retry logic and proper error handling are missing.

## Acceptance Criteria
1. ✅ **GIVEN** the ChatOpenAI instance in `services/iq_agent.py`  
   **WHEN** making async LLM calls  
   **THEN** it must use `agenerate()` or `acall()` instead of `ainvoke()`

2. ✅ **GIVEN** any LLM operation  
   **WHEN** a transient error occurs (rate limit, timeout)  
   **THEN** it must retry with exponential backoff (max 3 retries)

3. ✅ **GIVEN** an LLM response  
   **WHEN** token counting is needed  
   **THEN** proper token counting methods must be implemented

4. ✅ **GIVEN** an LLM failure after retries  
   **WHEN** the system cannot get a response  
   **THEN** it must fall back gracefully with an appropriate error message

## Technical Requirements

### Fix LLM Method Calls
```python
# services/iq_agent.py - Line 78
# WRONG
response = await self.llm.ainvoke(messages)

# CORRECT - Option 1: Using agenerate
from langchain_core.messages import HumanMessage, SystemMessage

messages = [
    SystemMessage(content=self.system_prompt),
    HumanMessage(content=user_query)
]
result = await self.llm.agenerate([messages])
response = result.generations[0][0].text

# CORRECT - Option 2: Using acall (if available)
response = await self.llm.acall(prompt=user_query)
```

### Implement Retry Logic
```python
import asyncio
from typing import Optional
import backoff

class IQComplianceAgent:
    async def _call_llm_with_retry(
        self, 
        messages: List[Any], 
        max_retries: int = 3
    ) -> Optional[str]:
        """Call LLM with exponential backoff retry logic"""
        
        @backoff.on_exception(
            backoff.expo,
            (RateLimitError, TimeoutError),
            max_tries=max_retries,
            max_time=30
        )
        async def _make_call():
            try:
                result = await self.llm.agenerate([messages])
                return result.generations[0][0].text
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                raise
        
        try:
            return await _make_call()
        except Exception as e:
            logger.error(f"LLM call failed after {max_retries} retries: {e}")
            return None  # Fallback
```

### Add Token Counting
```python
from tiktoken import encoding_for_model

def count_tokens(self, text: str, model: str = "gpt-4") -> int:
    """Count tokens in text for the specified model"""
    try:
        encoding = encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback to approximate count
        return len(text) // 4
```

### Files to Update
- `services/iq_agent.py` - Primary LLM integration
- Any other files using ChatOpenAI or LLM calls

## Tasks/Subtasks
- [ ] Replace all `ainvoke` calls with `agenerate` or `acall`
- [ ] Implement retry logic with exponential backoff
- [ ] Add token counting functionality
- [ ] Implement fallback responses for failures
- [ ] Add comprehensive error logging
- [ ] Test with rate limiting scenarios
- [ ] Document new LLM calling patterns

## Testing
```python
# Test LLM integration
@pytest.mark.asyncio
async def test_llm_integration():
    agent = IQComplianceAgent(neo4j_service, llm_model="gpt-4")
    
    # Test successful call
    response = await agent._call_llm_with_retry([
        SystemMessage(content="You are a helpful assistant"),
        HumanMessage(content="Hello")
    ])
    assert response is not None
    
    # Test retry on rate limit
    with patch.object(agent.llm, 'agenerate', side_effect=[
        RateLimitError("Rate limited"),
        RateLimitError("Rate limited"),
        Mock(generations=[[Mock(text="Success")]])
    ]):
        response = await agent._call_llm_with_retry(messages)
        assert response == "Success"
    
    # Test fallback after max retries
    with patch.object(agent.llm, 'agenerate', side_effect=RateLimitError("Rate limited")):
        response = await agent._call_llm_with_retry(messages)
        assert response is None  # Should fallback gracefully
```

## Definition of Done
- [ ] No `ainvoke` method calls remain in codebase
- [ ] Retry logic implemented and tested
- [ ] Token counting works accurately
- [ ] Fallback mechanism in place
- [ ] All LLM integration tests pass
- [ ] Error handling comprehensive
- [ ] Performance acceptable under load

## Dependencies
```python
# Required packages
langchain-openai >= 0.0.5
tiktoken >= 0.5.0
backoff >= 2.2.0
```

## Notes
- Check LangChain documentation for latest async patterns
- Consider implementing a circuit breaker for persistent failures
- Monitor token usage to prevent cost overruns
- May need to update LangChain version if methods unavailable

---
*Story created: 2025-01-12*
*Last updated: 2025-01-12*