# RuleIQ LangGraph Refactoring: Production-Grade Implementation Guide

You are tasked with refactoring the RuleIQ compliance platform codebase to properly utilize LangGraph features, standardize the RAG system, and migrate from Celery to LangGraph persistence.

## 🎯 Critical Refactoring Targets

### Issue #1: Underutilized LangGraph Features
**Current Implementation in `langgraph_agent/graph/`:**
- Basic TypedDict state without proper reducers
- Simple keyword-based routing in `router_node`
- No dedicated error handling nodes
- Minimal conditional edges

**Required Changes:**
1. Enhance `ComplianceAgentState` with Annotated reducers
2. Create centralized `ErrorHandlerNode` 
3. Implement sophisticated conditional routing
4. Add proper checkpointing and interrupts

### Issue #2: Complex Custom RAG System
**Current Implementation in `langgraph_agent/agents/rag_system.py`:**
- 1200+ lines of custom RAG logic
- Custom DocumentProcessor, DocumentChunk classes
- Manual embedding generation and caching
- Custom similarity calculations

**Required Changes:**
1. Replace with LangChain components
2. Use FAISS for vector storage
3. Implement MultiQueryRetriever
4. Add CohereRerank for reranking
5. Reduce to ~200 lines total

### Issue #3: Celery Task Migration
**Current Implementation in `workers/` and `celery_app.py`:**
- 5 separate task modules
- Redis dependency
- Complex retry logic
- Celery beat schedule

**Required Changes:**
1. Convert each task to LangGraph node
2. Use PostgreSQL checkpointer
3. Implement thread-based resumption
4. Remove Redis/Celery dependencies

## 📋 Specific File Transformations

### Pattern #1: State Management Enhancement

**FILE: `langgraph_agent/graph/state.py`**

CURRENT:
```python
class ComplianceAgentState(TypedDict):
    messages: Annotated[List[GraphMessage], add_messages]
    route: Optional[RouteDecision]
    # ... other fields
```

TRANSFORM TO:
```python
from typing import Annotated
from operator import add

class ComplianceAgentState(TypedDict):
    # Enhanced with proper reducers
    messages: Annotated[List[GraphMessage], add_messages]
    errors: Annotated[List[SafeFallbackResponse], add]
    tool_outputs: Annotated[Dict[str, Any], lambda x, y: {**x, **y}]
    meta: Annotated[Dict[str, Any], lambda x, y: {**x, **y}]
    
    # Add new fields for better control
    retry_count: int
    fallback_activated: bool
    checkpoint_id: str
```

### Pattern #2: Error Handling Node

**NEW FILE: `langgraph_agent/graph/error_handler.py`**

```python
from langgraph_agent.graph.state import ComplianceAgentState
from typing import Dict, Any
import time

class ErrorHandlerNode:
    """Centralized error handling for all graph nodes."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_strategies = {
            "rate_limit": self._handle_rate_limit,
            "database": self._handle_database_error,
            "api": self._handle_api_error,
            "validation": self._handle_validation_error
        }
    
    async def process(self, state: ComplianceAgentState) -> ComplianceAgentState:
        """Main error processing logic."""
        error_type = self._classify_error(state)
        
        if state.get("retry_count", 0) >= self.max_retries:
            return self._activate_fallback(state)
        
        handler = self.retry_strategies.get(error_type, self._generic_retry)
        return await handler(state)
    
    def _handle_rate_limit(self, state: ComplianceAgentState) -> ComplianceAgentState:
        """Handle rate limit errors with exponential backoff."""
        backoff = 2 ** state.get("retry_count", 0)
        time.sleep(min(backoff, 60))
        state["retry_count"] = state.get("retry_count", 0) + 1
        state["current_node"] = state.get("last_successful_node", "router")
        return state
```

### Pattern #3: RAG Standardization

**FILE: `langgraph_agent/agents/rag_system_v2.py`**

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.retrievers import MultiQueryRetriever, EnsembleRetriever
from langchain.retrievers.document_compressors import CohereRerank
from langchain.retrievers import ContextualCompressionRetriever

class StandardizedRAG:
    """Simplified RAG using LangChain components."""
    
    def __init__(self, company_id: UUID):
        self.company_id = company_id
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = FAISS.load_local(
            f"./vectorstores/{company_id}", 
            self.embeddings
        )
        
        # Multi-query for automatic expansion
        base_retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 20}
        )
        self.retriever = MultiQueryRetriever.from_llm(
            retriever=base_retriever,
            llm=ChatOpenAI(temperature=0)
        )
        
        # Add reranking
        compressor = CohereRerank(top_n=5)
        self.final_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=self.retriever
        )
    
    async def retrieve(self, query: str) -> List[Document]:
        """Simple retrieval - all complexity handled by LangChain."""
        return await self.final_retriever.aget_relevant_documents(query)
```

### Pattern #4: Celery to LangGraph Migration

**FILE: `langgraph_agent/persistence/task_migrator.py`**

```python
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated
from operator import add

class ComplianceTaskState(TypedDict):
    """State for compliance scoring tasks."""
    company_id: str
    task_type: str
    progress: int
    results: Annotated[List[Dict], add]
    errors: Annotated[List[str], add]
    current_step: str
    completed: bool

def create_compliance_scoring_graph():
    """Create graph for compliance scoring (replaces Celery task)."""
    
    graph = StateGraph(ComplianceTaskState)
    
    # Add nodes for each step
    graph.add_node("fetch_profiles", fetch_profiles_node)
    graph.add_node("calculate_scores", calculate_scores_node)
    graph.add_node("update_database", update_database_node)
    graph.add_node("send_notifications", send_notifications_node)
    graph.add_node("error_handler", error_handler_node)
    
    # Add edges
    graph.set_entry_point("fetch_profiles")
    graph.add_edge("fetch_profiles", "calculate_scores")
    graph.add_edge("calculate_scores", "update_database")
    graph.add_edge("update_database", "send_notifications")
    
    # Add conditional error routing
    for node in ["fetch_profiles", "calculate_scores", "update_database"]:
        graph.add_conditional_edges(
            node,
            lambda x: "error_handler" if x.get("errors") else None
        )
    
    # Compile with checkpointer
    checkpointer = PostgresSaver.from_conn_string(
        "postgresql://user:pass@localhost/compliance"
    )
    
    return graph.compile(checkpointer=checkpointer)

async def run_compliance_scoring(company_id: str):
    """Run compliance scoring with persistence (replaces Celery delay)."""
    graph = create_compliance_scoring_graph()
    
    thread_id = f"compliance_score_{company_id}_{datetime.now().date()}"
    config = {"configurable": {"thread_id": thread_id}}
    
    # Check if already in progress
    state = graph.get_state(config)
    if state and not state.values.get("completed"):
        # Resume from checkpoint
        result = await graph.ainvoke(None, config)
    else:
        # Start new
        initial_state = {
            "company_id": company_id,
            "task_type": "compliance_scoring",
            "progress": 0,
            "current_step": "fetch_profiles"
        }
        result = await graph.ainvoke(initial_state, config)
    
    return result
```

### Pattern #5: Enhanced Routing

**FILE: `langgraph_agent/graph/router_v2.py`**

```python
from langgraph_agent.graph.state import ComplianceAgentState
from typing import Literal

class EnhancedRouter:
    """Sophisticated routing with ML-based classification."""
    
    def __init__(self):
        self.routes = {
            "compliance_query": "compliance_analyzer",
            "obligation_search": "obligation_finder",
            "evidence_request": "evidence_collector",
            "legal_review": "legal_reviewer",
            "report_generation": "report_generator",
            "risk_assessment": "risk_analyzer"
        }
    
    def route(self, state: ComplianceAgentState) -> str:
        """Determine next node based on state analysis."""
        
        # Check for errors first
        if state.get("error_count", 0) > 0:
            return "error_handler"
        
        # Check for interrupts
        if state.get("requires_human_review"):
            return "human_review"
        
        # Analyze message intent
        intent = self._classify_intent(state)
        
        # Route based on intent and context
        if intent == "compliance_query":
            if state.get("profile") is None:
                return "profile_loader"
            return self.routes[intent]
        
        return self.routes.get(intent, "compliance_analyzer")
    
    def _classify_intent(self, state: ComplianceAgentState) -> str:
        """Classify user intent from messages."""
        last_message = state["messages"][-1].content.lower()
        
        # Intent classification logic
        if "obligation" in last_message or "requirement" in last_message:
            return "obligation_search"
        elif "evidence" in last_message or "document" in last_message:
            return "evidence_request"
        elif "legal" in last_message or "review" in last_message:
            return "legal_review"
        elif "report" in last_message or "summary" in last_message:
            return "report_generation"
        elif "risk" in last_message or "assessment" in last_message:
            return "risk_assessment"
        else:
            return "compliance_query"
```

## 🔄 Migration Strategy

### Step 1: Create Parallel Implementation
1. Create new files with "_v2" suffix
2. Implement new patterns alongside existing code
3. No changes to existing functionality

### Step 2: Create Adapters
1. Build adapters to bridge old and new implementations
2. Test adapters thoroughly
3. Gradual traffic shifting

### Step 3: Migrate Component by Component
1. Start with state management (lowest risk)
2. Then RAG system (medium risk)
3. Finally Celery tasks (highest risk)

### Step 4: Validate and Clean Up
1. Run comprehensive tests
2. Performance benchmarking
3. Remove old implementations

## ⚡ Performance Targets

- State operations: <1ms
- RAG retrieval: <500ms
- Task checkpoint save: <10ms
- Error recovery: <100ms

## 🧪 Validation Checklist

### State Management
- [ ] All state fields have proper reducers
- [ ] Error handler node integrated
- [ ] Conditional routing works
- [ ] Checkpointing verified

### RAG System
- [ ] LangChain components integrated
- [ ] Vector store operational
- [ ] Reranking functional
- [ ] Performance improved

### Task Migration
- [ ] All Celery tasks converted
- [ ] Checkpointing works
- [ ] Thread resumption tested
- [ ] No Redis dependency

## 🚨 Critical Warnings

1. **Do NOT modify existing files directly** - create new versions
2. **Test adapters thoroughly** before switching traffic
3. **Monitor performance** during migration
4. **Keep rollback plan ready** at each phase
5. **Document all changes** for team knowledge transfer

## 📊 Expected Outcomes

- **Code Reduction**: 60-80%
- **Performance Gain**: 2-3x
- **Infrastructure Simplification**: Remove Redis, Celery
- **Maintainability**: Industry-standard components
- **Testing**: Easier with standard patterns

This refactoring will transform RuleIQ into a reference implementation for LangGraph-based compliance systems.
