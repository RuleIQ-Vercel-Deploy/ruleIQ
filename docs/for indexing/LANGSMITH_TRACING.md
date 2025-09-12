# LangSmith Tracing Documentation

## Overview

LangSmith tracing has been integrated into the ruleIQ LangGraph assessment agent to provide comprehensive observability for all AI operations. This enables monitoring, debugging, and optimization of the agent's behavior in both development and production environments.

## Setup

### 1. Environment Configuration

Add the following environment variables to your `.env` or `.env.local` file:

```bash
# Enable LangSmith Tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__your_api_key_here
LANGCHAIN_PROJECT=ruleiq-assessment
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

### 2. Obtaining API Keys

1. Sign up for LangSmith at [https://smith.langchain.com](https://smith.langchain.com)
2. Navigate to Settings → API Keys
3. Create a new API key
4. Copy the key (it should start with `ls__`)

### 3. Verifying Configuration

Run the configuration validator:

```bash
python config/langsmith_config.py
```

Expected output:
```
✅ LangSmith tracing is properly configured!
  Project: ruleiq-assessment
  Endpoint: https://api.smith.langchain.com
  View traces at: https://smith.langchain.com
```

## Architecture

### Configuration Module

The core configuration is managed by `config/langsmith_config.py`:

- `LangSmithConfig`: Configuration manager with validation
- `with_langsmith_tracing`: Decorator for adding tracing to async functions
- Automatic metadata and tag extraction from function parameters

### Decorated Nodes

The following LangGraph nodes have been instrumented with tracing:

#### Evidence Collection Nodes (`langgraph_agent/nodes/evidence_nodes.py`)
- `evidence.process` - Process evidence items
- `evidence.cleanup_stale` - Clean up expired evidence
- `evidence.sync_status` - Synchronize evidence status
- `evidence.check_expiry` - Check evidence expiration
- `evidence.collect_integrations` - Collect from all integrations
- `evidence.process_pending` - Process pending evidence
- `evidence.validate` - Validate evidence items
- `evidence.aggregate` - Aggregate evidence results
- `evidence.collection_node` - Main evidence collection node

#### Compliance Nodes (`langgraph_agent/nodes/compliance_nodes_real.py`)
- `compliance.batch_update` - Batch compliance updates
- `compliance.single_check` - Single compliance check
- `compliance.monitoring` - Compliance monitoring

#### RAG Nodes (`langgraph_agent/nodes/rag_node.py`)
- `rag.query` - Main RAG query operations
- `rag.retrieve_documents` - Document retrieval
- `rag.semantic_search` - Semantic search operations

## Usage

### Basic Usage

Once configured, tracing happens automatically for all decorated functions:

```python
# Automatic tracing when calling decorated nodes
state = await evidence_node.process_evidence(state=evidence_state)
# This will automatically create a trace with:
# - Operation name: "evidence.process"
# - Session ID from state
# - Current phase from state
# - Input/output metadata
```

### Adding Tracing to New Functions

To add tracing to a new async function:

```python
from config.langsmith_config import with_langsmith_tracing

class MyNode:
    @with_langsmith_tracing("my_operation_name")
    async def my_function(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Your function logic here
        return state
```

### Custom Metadata

The decorator automatically extracts metadata from function parameters:

- `session_id`: Extracted from kwargs or state
- `current_phase`: Extracted from state
- `inputs/outputs`: Automatically captured

### Viewing Traces

1. Navigate to [https://smith.langchain.com](https://smith.langchain.com)
2. Select your project (e.g., "ruleiq-assessment")
3. View traces in real-time or historical data

## What You'll See in LangSmith

### Trace Information
- **Operation Timeline**: Complete flow through the state graph
- **Node Execution**: Each node with inputs and outputs
- **AI Model Calls**: Prompts and responses
- **Error Traces**: Failures with stack traces
- **Performance Metrics**: Latency for each operation

### Metadata Tags
- `session:{id}`: Assessment session identifier
- `phase:{name}`: Current assessment phase
- `evidence.{operation}`: Evidence operations
- `compliance.{operation}`: Compliance operations
- `rag.{operation}`: RAG operations

## Testing

### Unit Tests

Run the comprehensive test suite:

```bash
# Run all LangSmith integration tests
python -m pytest tests/test_langsmith_integration.py -v

# Test categories:
# - Configuration validation (13 tests)
# - Metadata collection (6 tests)
# - Tracing decorators (4 tests)
# - Performance impact (3 tests)
# - Error scenarios (4 tests)
# - Trace data structure (3 tests)
# - LangGraph integration (2 tests)
# - Mock callbacks (2 tests)
```

### Integration Tests

Run end-to-end integration tests:

```bash
python -m pytest tests/test_langsmith_integration_e2e.py -v

# Tests:
# - Complete workflow tracing
# - Concurrent execution
# - Error handling
# - Nested operations
```

## Performance Considerations

### Overhead

- Minimal performance impact when tracing is enabled (~1-2ms per operation)
- No impact when `LANGCHAIN_TRACING_V2=false`
- Asynchronous trace submission doesn't block operations

### Best Practices

1. **Development**: Enable tracing for debugging
2. **Staging**: Enable tracing for monitoring
3. **Production**: Enable selectively based on needs
4. **High-volume**: Consider sampling strategies

## Troubleshooting

### Common Issues

1. **Tracing Not Working**
   - Verify `LANGCHAIN_TRACING_V2=true`
   - Check API key starts with `ls__`
   - Ensure network connectivity to LangSmith

2. **Missing Traces**
   - Check project name matches configuration
   - Verify function has decorator
   - Check for exceptions preventing trace completion

3. **Performance Issues**
   - Consider disabling in high-volume scenarios
   - Use sampling if needed
   - Check network latency to LangSmith

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger("config.langsmith_config").setLevel(logging.DEBUG)
```

## Security

- API keys should never be committed to version control
- Use environment variables or secure secret management
- Rotate API keys periodically
- Review traced data for sensitive information

## Additional Resources

- [LangSmith Documentation](https://docs.langsmith.com)
- [LangChain Tracing Guide](https://python.langchain.com/docs/guides/tracing)
- [Best Practices](https://docs.langsmith.com/best-practices)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review test files for examples
3. Contact the development team
4. Open an issue in the repository