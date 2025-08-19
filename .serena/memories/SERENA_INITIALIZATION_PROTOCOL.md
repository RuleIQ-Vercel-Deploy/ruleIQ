# Serena MCP Initialization Protocol

## Critical First Steps Before Any Code Analysis or Fixes

### 1. ALWAYS READ FIRST - Agent Operating Protocol
- **MANDATORY**: Read `ALWAYS_READ_FIRST` memory before any coding task
- This contains the Test-First Mandate and Immaculate Code Standard

### 2. RAG Documentation Access Protocol
Before attempting ANY fixes or analysis involving:
- **LangGraph** (state management, agents, checkpoints)
- **Pydantic AI** (data validation, models)
- **FastAPI** (API endpoints, routing)
- **Assessment flows** (freemium, state persistence)

**MUST PROACTIVELY ACCESS**:
1. LangGraph documentation in RAG system
2. Pydantic AI documentation in RAG system
3. Project-specific implementation patterns

### 3. Documentation Search Commands
Use these exact patterns to access documentation:
```bash
# For LangGraph issues
mcp__serena__search_for_pattern "langgraph" --context="documentation"

# For Pydantic AI issues  
mcp__serena__search_for_pattern "pydantic" --context="documentation"

# For state management patterns
mcp__serena__search_for_pattern "checkpointer" --context="implementation"
```

### 4. Verification Steps
Before any code modification:
1. ✅ Read ALWAYS_READ_FIRST protocol
2. ✅ Access relevant RAG documentation  
3. ✅ Understand existing implementation patterns
4. ✅ Write tests first (Test-First Mandate)
5. ✅ Implement with zero warnings

### 5. Critical Areas Requiring Documentation Review
- **LangGraph State Persistence**: PostgreSQL vs MemorySaver patterns
- **Assessment Agent Architecture**: State management across HTTP requests
- **Pydantic Models**: Validation and serialization patterns
- **Circuit Breaker Patterns**: AI service fallback mechanisms

## Enforcement
- No code fixes without documentation review
- No assumptions about library behavior
- Always verify against official documentation in RAG