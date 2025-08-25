# LangGraph Best Practices for ruleIQ - Production Guide

## Core Architecture Principles

### 1. State Management
```python
# GOOD: Typed state with clear schema
class ComplianceAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    business_profile_id: str
    compliance_context: dict
    evidence_items: list[dict]
    current_step: str
    error_count: int
    checkpoint_id: Optional[str]

# BAD: Untyped dictionary state
state = {"messages": [], "data": {}}
```

### 2. Graph Structure Patterns

#### Conditional Edges with Error Handling
```python
def should_continue(state: ComplianceAgentState) -> str:
    """Router function with error awareness."""
    if state["error_count"] > 3:
        return "error_handler"
    if state["current_step"] == "complete":
        return END
    return "continue"

graph.add_conditional_edges(
    "assessment_node",
    should_continue,
    {
        "continue": "next_question",
        "error_handler": "fallback_node",
        END: END
    }
)
```

#### Subgraphs for Complex Workflows
```python
# Create reusable subgraphs for common patterns
evidence_subgraph = StateGraph(EvidenceState)
evidence_subgraph.add_node("retrieve", retrieve_evidence)
evidence_subgraph.add_node("validate", validate_evidence)
evidence_subgraph.add_node("classify", classify_evidence)

# Compile and use in main graph
evidence_chain = evidence_subgraph.compile()
main_graph.add_node("process_evidence", evidence_chain)
```

### 3. Persistence & Checkpointing

#### PostgreSQL Checkpointer (Recommended for ruleIQ)
```python
from langgraph.checkpoint.postgres import PostgresSaver

# Use with existing PostgreSQL connection
checkpointer = PostgresSaver.from_conn_string(
    DATABASE_URL,
    serde=JsonPlusSerializer()  # Handles complex types
)

# Compile with checkpointing
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"],  # Pause for human input
    interrupt_after=["critical_decision"]  # Pause after important steps
)
```

#### Thread Management for Sessions
```python
# Unique thread per assessment session
thread_config = {
    "configurable": {
        "thread_id": f"assessment_{session_id}",
        "checkpoint_ns": "compliance_assessment"
    }
}

# Resume from checkpoint
async for event in app.astream(
    {"user_input": message},
    config=thread_config,
    stream_mode="values"
):
    # Process streaming events
    pass
```

### 4. Tool Integration Best Practices

#### Structured Tool Creation
```python
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

class ComplianceQueryInput(BaseModel):
    regulation: str = Field(description="Regulation code (GDPR, DPA2018)")
    company_size: str = Field(description="Company size category")
    
compliance_tool = StructuredTool.from_function(
    func=query_compliance_graph,
    name="compliance_checker",
    description="Check compliance requirements",
    args_schema=ComplianceQueryInput,
    return_direct=False,  # Let agent process result
    handle_tool_error=True  # Graceful error handling
)
```

#### Tool Binding Pattern
```python
# Bind tools to LLM for function calling
llm_with_tools = llm.bind_tools([
    compliance_tool,
    evidence_tool,
    regulation_tool
])

# Use in node
async def agent_node(state: ComplianceAgentState):
    response = await llm_with_tools.ainvoke(state["messages"])
    if response.tool_calls:
        # Execute tools
        return {"messages": [response], "tool_calls": response.tool_calls}
    return {"messages": [response]}
```

### 5. Error Handling & Recovery

#### Circuit Breaker Pattern
```python
class CircuitBreakerNode:
    def __init__(self, max_failures=3, reset_timeout=60):
        self.failure_count = 0
        self.max_failures = max_failures
        self.last_failure_time = None
        
    async def __call__(self, state):
        if self.failure_count >= self.max_failures:
            if time.time() - self.last_failure_time < self.reset_timeout:
                return {"status": "circuit_open", "fallback": True}
        
        try:
            result = await self.execute(state)
            self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            return {"status": "error", "error": str(e)}
```

#### Retry with Exponential Backoff
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_external_api(state):
    # API call with automatic retry
    pass
```

### 6. Streaming & Real-time Updates

#### Streaming Patterns
```python
# Stream with different modes
async def stream_assessment(app, input_state, config):
    # Stream full values
    async for state in app.astream(input_state, config, stream_mode="values"):
        yield {"type": "state", "data": state}
    
    # Stream updates only
    async for update in app.astream(input_state, config, stream_mode="updates"):
        yield {"type": "update", "data": update}
    
    # Stream specific events
    async for event in app.astream_events(input_state, config, version="v2"):
        if event["event"] == "on_chat_model_stream":
            yield {"type": "token", "data": event["data"]["chunk"]}
```

### 7. Observability & Monitoring

#### LangSmith Integration
```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "ruleiq-compliance"

# Custom run naming
from langsmith import traceable

@traceable(name="compliance_assessment", run_type="chain")
async def run_assessment(profile_id: str):
    # Traced execution
    pass
```

#### Structured Logging
```python
import structlog

logger = structlog.get_logger()

async def logged_node(state):
    logger.info(
        "node_execution",
        node_name="assessment",
        thread_id=state.get("thread_id"),
        step=state.get("current_step"),
        profile_id=state.get("business_profile_id")
    )
    # Node logic
    return state
```

### 8. Testing Patterns

#### Unit Testing Nodes
```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_assessment_node():
    state = ComplianceAgentState(
        messages=[HumanMessage(content="Test")],
        business_profile_id="test-123",
        current_step="initial"
    )
    
    node = assessment_node
    result = await node(state)
    
    assert result["current_step"] == "question_1"
    assert len(result["messages"]) > len(state["messages"])
```

#### Integration Testing Graphs
```python
@pytest.mark.asyncio
async def test_full_assessment_flow():
    app = build_assessment_graph()
    
    # Mock external dependencies
    with patch("services.neo4j_service.query") as mock_query:
        mock_query.return_value = {"requirements": [...]}
        
        result = await app.ainvoke(
            {"messages": [HumanMessage(content="Start assessment")]},
            {"configurable": {"thread_id": "test"}}
        )
        
        assert result["current_step"] == "complete"
```

### 9. Performance Optimization

#### Parallel Node Execution
```python
# Use parallel execution for independent operations
graph.add_node("parallel_checks", RunnableParallel({
    "compliance": check_compliance,
    "evidence": retrieve_evidence,
    "risk": calculate_risk
}))
```

#### Caching Strategies
```python
from functools import lru_cache
from cachetools import TTLCache

# Cache expensive computations
regulation_cache = TTLCache(maxsize=100, ttl=3600)

@lru_cache(maxsize=128)
def get_regulation_requirements(regulation_code: str):
    # Expensive database query
    pass
```

### 10. Production Deployment

#### Configuration Management
```python
from pydantic_settings import BaseSettings

class LangGraphConfig(BaseSettings):
    checkpoint_ttl: int = 86400  # 24 hours
    max_iterations: int = 20
    timeout_seconds: int = 300
    enable_tracing: bool = True
    fallback_model: str = "gpt-3.5-turbo"
    
    class Config:
        env_prefix = "LANGGRAPH_"
```

#### Graceful Shutdown
```python
import signal
import asyncio

class GracefulShutdown:
    def __init__(self, app):
        self.app = app
        self.shutdown_event = asyncio.Event()
        
    async def handle_shutdown(self):
        # Save checkpoints
        await self.app.checkpointer.flush()
        # Close connections
        await self.app.close()
        self.shutdown_event.set()
```

## Anti-Patterns to Avoid

1. **Don't use untyped state** - Always use TypedDict or Pydantic models
2. **Don't ignore checkpointing** - Essential for production reliability
3. **Don't hardcode tool descriptions** - Use structured schemas
4. **Don't skip error nodes** - Always have fallback paths
5. **Don't use synchronous I/O** - Use async throughout
6. **Don't ignore streaming** - Users expect real-time feedback
7. **Don't skip observability** - You'll need debugging in production

## ruleIQ-Specific Recommendations

1. **Use PostgreSQL checkpointing** - Leverage existing database
2. **Implement circuit breakers** - For Neo4j and API calls
3. **Add compliance audit trails** - Log all decisions
4. **Use subgraphs** - For evidence processing, risk assessment
5. **Implement human-in-the-loop** - For critical compliance decisions
6. **Cache regulation data** - Reduce Neo4j query load
7. **Stream assessment progress** - Better UX for long assessments

## Performance Targets

- Node execution: < 500ms average
- Checkpoint save: < 100ms
- Stream latency: < 50ms
- Error recovery: < 2 seconds
- Memory per thread: < 50MB

## Next Steps for ruleIQ

1. Implement PostgreSQL checkpointing in IQComplianceAgent
2. Add circuit breakers to Neo4j service calls
3. Create subgraphs for evidence and risk workflows
4. Implement streaming for assessment progress
5. Add LangSmith tracing with custom metadata
6. Build comprehensive test suite for graph flows

This guide prioritizes production reliability, observability, and performance - essential for a compliance platform where accuracy and auditability are critical.