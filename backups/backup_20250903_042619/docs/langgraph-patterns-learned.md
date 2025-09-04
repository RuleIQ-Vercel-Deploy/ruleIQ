# LangGraph Patterns and Best Practices

## Documentation Study Summary

This document summarizes the key patterns and best practices learned from studying LangGraph documentation and existing implementation.

## Core Concepts

### 1. State Management with TypedDict
```python
from typing import TypedDict, Annotated, List, Dict
from operator import add

class GraphState(TypedDict):
    """State with automatic merging using Annotated."""
    # Accumulator fields - automatically merge
    messages: Annotated[List[Dict], add]
    errors: Annotated[List[str], add]
    
    # Override fields - last writer wins
    current_step: str
    confidence_score: float
    
    # Custom merge with lambda
    metadata: Annotated[Dict, lambda x, y: {**x, **y}]
```

### 2. Graph Construction Pattern
```python
from langgraph.graph import StateGraph

def build_compliance_graph() -> StateGraph:
    graph = StateGraph(GraphState)
    
    # Add nodes
    graph.add_node("analyze", analyze_compliance)
    graph.add_node("validate", validate_results)
    graph.add_node("error_handler", handle_errors)
    
    # Add conditional edges
    graph.add_conditional_edges(
        "analyze",
        routing_function,
        {
            "validate": "validate",
            "error": "error_handler",
            "retry": "analyze"
        }
    )
    
    # Set entry and finish
    graph.set_entry_point("analyze")
    graph.set_finish_point("validate")
    
    return graph
```

### 3. Checkpointing for State Persistence
```python
from langgraph.checkpoint.postgres import PostgresSaver

# PostgreSQL checkpointer for production
checkpointer = PostgresSaver(
    connection_string=DATABASE_URL,
    serde=JsonSerde()  # Custom serialization if needed
)

# Compile with checkpointer
graph = graph.compile(checkpointer=checkpointer)

# Use with thread_id for conversation continuity
config = {"configurable": {"thread_id": session_id}}
result = graph.invoke(input_state, config)
```

### 4. Error Handling Patterns

#### Dedicated Error Node
```python
def error_handler(state: GraphState) -> GraphState:
    """Centralized error handling with retry logic."""
    error_count = state.get("error_count", 0) + 1
    
    if error_count >= MAX_RETRIES:
        state["status"] = "failed"
        state["next_step"] = END
    else:
        state["error_count"] = error_count
        state["next_step"] = "retry"
    
    return state
```

#### Try-Catch in Nodes
```python
def safe_node_execution(state: GraphState) -> GraphState:
    try:
        # Node logic
        result = process_compliance(state)
        state["result"] = result
    except Exception as e:
        state["errors"].append(str(e))
        state["next_step"] = "error_handler"
    
    return state
```

### 5. Conditional Routing

#### Simple Condition
```python
def route_by_confidence(state: GraphState) -> str:
    if state["confidence_score"] > 0.8:
        return "high_confidence"
    elif state["confidence_score"] > 0.5:
        return "medium_confidence"
    else:
        return "manual_review"

graph.add_conditional_edges(
    "analyze",
    route_by_confidence,
    {
        "high_confidence": "auto_approve",
        "medium_confidence": "additional_checks",
        "manual_review": "human_review"
    }
)
```

#### Complex Multi-Factor Routing
```python
def complex_routing(state: GraphState) -> str:
    if state.get("errors"):
        return "error_handler"
    
    if state["retry_count"] >= 3:
        return "escalate"
    
    if state["confidence_score"] < 0.5:
        return "enhance"
    
    return "proceed"
```

### 6. Parallel Execution

```python
from langgraph.graph import StateGraph, END

graph = StateGraph(GraphState)

# Add parallel nodes
graph.add_node("check_soc2", check_soc2_compliance)
graph.add_node("check_iso", check_iso_compliance)
graph.add_node("check_gdpr", check_gdpr_compliance)
graph.add_node("aggregate", aggregate_results)

# Route to parallel execution
graph.add_edge("start", "check_soc2")
graph.add_edge("start", "check_iso")
graph.add_edge("start", "check_gdpr")

# All parallel nodes route to aggregator
graph.add_edge("check_soc2", "aggregate")
graph.add_edge("check_iso", "aggregate")
graph.add_edge("check_gdpr", "aggregate")
```

### 7. Streaming and Async Support

```python
# Async node definition
async def async_compliance_check(state: GraphState) -> GraphState:
    result = await fetch_compliance_data(state["company_id"])
    state["compliance_data"] = result
    return state

# Stream results
async def stream_graph_execution():
    async for chunk in graph.astream(input_state, config):
        print(f"Node: {chunk['node']}")
        print(f"State: {chunk['state']}")
```

### 8. Tool Integration

```python
from langchain.tools import Tool

compliance_tool = Tool(
    name="compliance_checker",
    func=check_compliance,
    description="Check compliance requirements"
)

def tool_node(state: GraphState) -> GraphState:
    """Node that uses tools."""
    result = compliance_tool.run(state["query"])
    state["tool_result"] = result
    return state
```

### 9. Memory and Context

```python
from langgraph.prebuilt import MemorySaver

# Add memory to preserve context
memory = MemorySaver()

graph = graph.compile(
    checkpointer=checkpointer,
    memory=memory
)

# Access previous interactions
config = {
    "configurable": {
        "thread_id": session_id,
        "memory_key": "compliance_history"
    }
}
```

### 10. Testing Patterns

```python
def test_graph_execution():
    """Test graph with mock state."""
    # Create test state
    test_state = GraphState(
        company_id="test-company",
        messages=[],
        errors=[],
        confidence_score=0.0
    )
    
    # Create test graph
    graph = build_compliance_graph()
    
    # Mock external calls
    with patch("external_api.fetch") as mock_fetch:
        mock_fetch.return_value = {"status": "compliant"}
        
        # Execute graph
        result = graph.invoke(test_state)
        
        # Assert execution path
        assert result["status"] == "completed"
        assert len(result["messages"]) > 0
```

## Migration from Celery

### Key Differences

| Aspect | Celery | LangGraph |
|--------|--------|-----------|
| State | Stateless tasks | Stateful graph |
| Flow | Linear chains | Conditional graphs |
| Persistence | Redis/RabbitMQ | PostgreSQL checkpoints |
| Error Handling | Task retry | Error nodes + conditional routing |
| Observability | Flower | Built-in streaming + LangSmith |

### Migration Pattern

```python
# Celery Task
@celery.task(bind=True, max_retries=3)
def check_compliance_task(self, company_id):
    try:
        result = check_compliance(company_id)
        return result
    except Exception as exc:
        raise self.retry(exc=exc)

# LangGraph Equivalent
def check_compliance_node(state: GraphState) -> GraphState:
    """LangGraph node with built-in retry via graph structure."""
    try:
        result = check_compliance(state["company_id"])
        state["compliance_result"] = result
        state["next_step"] = "validate"
    except Exception as e:
        state["errors"].append(str(e))
        state["retry_count"] += 1
        state["next_step"] = "error_handler"
    
    return state
```

## Performance Considerations

### 1. Checkpoint Optimization
- Use batch checkpointing for high-throughput scenarios
- Consider checkpoint compression for large states
- Implement checkpoint cleanup for old threads

### 2. State Size Management
- Keep state minimal - avoid storing large documents
- Use references/IDs instead of full objects
- Implement state pruning for long conversations

### 3. Parallel Execution
- Use parallel nodes for independent checks
- Implement proper aggregation nodes
- Consider rate limiting for external API calls

### 4. Caching Strategy
- Cache expensive computations at node level
- Use Redis for temporary state caching
- Implement cache invalidation logic

## Common Pitfalls to Avoid

1. **Mutable State Mutation**: Always return new state, don't mutate in-place
2. **Missing Error Handlers**: Every graph should have error recovery paths
3. **Infinite Loops**: Add max iteration limits to cyclic graphs
4. **Checkpoint Bloat**: Regularly clean up old checkpoints
5. **Synchronous Blocking**: Use async nodes for I/O operations

## Best Practices Checklist

- [ ] Use TypedDict with Annotated for state definition
- [ ] Implement error handler nodes
- [ ] Add conditional routing for all decision points
- [ ] Enable checkpointing for production
- [ ] Write deterministic tests with mock LLMs
- [ ] Monitor graph execution metrics
- [ ] Document state schema and transitions
- [ ] Implement proper retry mechanisms
- [ ] Use streaming for real-time feedback
- [ ] Add observability with LangSmith integration

## Resources

### Official Documentation
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [State Management Guide](https://langchain-ai.github.io/langgraph/concepts/#state)
- [Checkpointing Guide](https://langchain-ai.github.io/langgraph/concepts/#checkpoints)
- [Testing Guide](https://langchain-ai.github.io/langgraph/how-tos/testing/)

### Example Repositories
- [LangGraph Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [Plan and React Agent](https://github.com/foreveryh/langgraph-plan-and-react-agent)
- [Multi-Agent Workflows](https://github.com/langchain-ai/langgraph/tree/main/examples/multi_agent)

### Community Resources
- [GitHub Discussions](https://github.com/langchain-ai/langgraph/discussions)
- [Discord Community](https://discord.gg/langchain)
- [Stack Overflow Tag](https://stackoverflow.com/questions/tagged/langgraph)