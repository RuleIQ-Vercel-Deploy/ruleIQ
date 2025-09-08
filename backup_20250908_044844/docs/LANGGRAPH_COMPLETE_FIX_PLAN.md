# LangGraph Complete Implementation Fix Plan

## Current State Analysis

### Critical Issues Found
1. **Disconnected Phases**: Graph nodes exist but aren't properly integrated
2. **Fake Tests**: Tests use mocks instead of real services
3. **Incomplete Migration**: Only 25% of Celery tasks migrated (evidence_tasks only)
4. **No Working System**: Graph doesn't actually execute end-to-end workflows
5. **Missing Error Handler**: `_error_handler_node` calls error_handler.process but doesn't implement retry logic properly
6. **No Real RAG**: RAG system is mocked, not connected to actual vector stores
7. **Broken Checkpointing**: PostgreSQL checkpointer setup() not awaited properly

### Migration Status
- ✅ Evidence Tasks: 25% (2/2 tasks migrated)
- ❌ Compliance Tasks: 0% (0/2 tasks migrated)
- ❌ Notification Tasks: 0% (0/3 tasks migrated)
- ❌ Reporting Tasks: 0% (0/4 tasks migrated)
- ❌ Monitoring Tasks: 0% (0/4 tasks migrated - not compliance critical)

## Implementation Phases

### PHASE 1: Core State Management & Graph Foundation

#### 1.1 Fix Unified State Management
```python
# Location: langgraph_agent/graph/unified_state.py

from typing import TypedDict, List, Dict, Any, Optional, Literal
from datetime import datetime
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated

class UnifiedComplianceState(TypedDict):
    """Complete unified state for ALL phases."""
    
    # Core workflow fields
    workflow_id: str
    workflow_status: Literal["PENDING", "RUNNING", "COMPLETED", "FAILED", "RETRYING"]
    current_step: str
    
    # Messages with proper reducer
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Execution tracking
    steps_completed: List[str]
    steps_remaining: List[str]
    retry_count: int
    max_retries: int
    should_continue: bool
    
    # Error tracking (Phase 2 integration)
    errors: List[Dict[str, Any]]
    error_count: int
    error_correlation_id: Optional[str]
    circuit_breaker_status: Dict[str, Any]
    last_error_time: Optional[datetime]
    
    # RAG context (Phase 3 integration)
    rag_queries: List[str]
    rag_responses: List[Dict[str, Any]]
    relevant_documents: List[Dict[str, Any]]
    vector_store_status: str
    
    # Task scheduling (Phase 4 integration)
    scheduled_task_id: Optional[str]
    task_type: Optional[str]
    task_schedule: Optional[str]
    task_result: Optional[Any]
    celery_task_status: Optional[str]
    
    # Compliance specific
    compliance_data: Dict[str, Any]
    evidence_items: List[Dict[str, Any]]
    obligations: List[Dict[str, Any]]
    assessment_results: Dict[str, Any]
    
    # History and metadata
    history: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    checkpoint_id: Optional[str]
    thread_id: str
```

#### 1.2 Fix Error Handler Node
```python
# Location: langgraph_agent/graph/enhanced_app.py

async def _error_handler_node(self, state: UnifiedComplianceState) -> UnifiedComplianceState:
    """
    PROPERLY implement error handler with retry logic.
    """
    # Increment retry count
    state["retry_count"] = state.get("retry_count", 0) + 1
    
    # Check if we should retry
    if state["retry_count"] <= state.get("max_retries", 3):
        # Calculate backoff
        wait_time = min(2 ** state["retry_count"], 30)
        await asyncio.sleep(wait_time)
        
        # Update status for retry
        state["workflow_status"] = "RETRYING"
        state["should_continue"] = True
        
        logger.info(f"Retrying workflow - attempt {state['retry_count']}/{state['max_retries']}")
        
        # Clear last error to retry
        if state.get("errors"):
            state["last_error_time"] = datetime.now()
            
    else:
        # Max retries exceeded
        state["workflow_status"] = "FAILED"
        state["should_continue"] = False
        logger.error(f"Max retries exceeded - workflow failed")
    
    # Update state history
    state["history"].append({
        "timestamp": datetime.now().isoformat(),
        "action": "error_handler",
        "retry_count": state["retry_count"],
        "status": state["workflow_status"]
    })
    
    return state
```

#### 1.3 Build Complete Graph
```python
# Location: langgraph_agent/graph/complete_graph.py

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg
from psycopg.rows import dict_row

def build_integrated_graph() -> CompiledGraph:
    """Build complete integrated graph with ALL nodes."""
    
    graph = StateGraph(UnifiedComplianceState)
    
    # Add ALL nodes from ALL phases
    graph.add_node("state_validator", state_validator_node)
    graph.add_node("error_handler", error_handler_node)
    graph.add_node("rag_query", rag_query_node)
    graph.add_node("evidence_collection", evidence_collection_node)
    graph.add_node("compliance_check", compliance_check_node)
    graph.add_node("notification", notification_node)
    graph.add_node("reporting", reporting_node)
    graph.add_node("task_scheduler", task_scheduler_node)
    
    # Entry point
    graph.set_entry_point("state_validator")
    
    # Add conditional edges with proper routing
    def route_after_validation(state: UnifiedComplianceState) -> str:
        """Route based on task type."""
        if state.get("error_count", 0) > 0:
            return "error_handler"
        
        task_type = state.get("task_type", "compliance_check")
        
        if task_type == "evidence_collection":
            return "evidence_collection"
        elif task_type == "compliance_check":
            return "rag_query"  # Query first, then check
        elif task_type == "notification":
            return "notification"
        elif task_type == "reporting":
            return "reporting"
        else:
            return "compliance_check"
    
    graph.add_conditional_edges(
        "state_validator",
        route_after_validation,
        {
            "error_handler": "error_handler",
            "evidence_collection": "evidence_collection",
            "rag_query": "rag_query",
            "compliance_check": "compliance_check",
            "notification": "notification",
            "reporting": "reporting"
        }
    )
    
    # Error handler routing
    def route_after_error(state: UnifiedComplianceState) -> str:
        if state["should_continue"]:
            return state.get("current_step", "state_validator")
        return END
    
    graph.add_conditional_edges(
        "error_handler",
        route_after_error
    )
    
    # RAG to compliance
    graph.add_edge("rag_query", "compliance_check")
    
    # Compliance to notification
    graph.add_edge("compliance_check", "notification")
    
    # Evidence to compliance
    graph.add_edge("evidence_collection", "compliance_check")
    
    # Notification to reporting
    graph.add_edge("notification", "reporting")
    
    # Reporting to end
    graph.add_edge("reporting", END)
    
    # Set up proper PostgreSQL checkpointing
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Fix the connection setup
    conn = psycopg.connect(
        DATABASE_URL,
        autocommit=True,
        row_factory=dict_row
    )
    
    checkpointer = PostgresSaver(conn)
    
    # Properly await setup in async context
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(checkpointer.setup())
    
    # Compile with checkpointing
    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_review"],
        interrupt_after=["critical_decision"]
    )
```

### PHASE 2: Integrated Error Handling

#### 2.1 Create Integrated Error Handler
```python
# Location: langgraph_agent/graph/integrated_error_handler.py

class IntegratedErrorHandler:
    """Complete error handler with circuit breaker."""
    
    def __init__(self):
        self.circuit_breakers = {}
        self.error_counts = {}
        
    async def handle_node_error(
        self,
        node_name: str,
        error: Exception,
        state: UnifiedComplianceState
    ) -> UnifiedComplianceState:
        """Handle errors with circuit breaker pattern."""
        
        # Track error
        error_id = str(uuid4())
        error_details = {
            "id": error_id,
            "node": node_name,
            "error": str(error),
            "type": type(error).__name__,
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc()
        }
        
        state["errors"].append(error_details)
        state["error_count"] = len(state["errors"])
        state["error_correlation_id"] = error_id
        
        # Check circuit breaker
        if node_name not in self.circuit_breakers:
            self.circuit_breakers[node_name] = {
                "failures": 0,
                "last_failure": None,
                "state": "CLOSED"
            }
        
        breaker = self.circuit_breakers[node_name]
        breaker["failures"] += 1
        breaker["last_failure"] = datetime.now()
        
        # Open circuit if too many failures
        if breaker["failures"] >= 3:
            breaker["state"] = "OPEN"
            state["circuit_breaker_status"] = {
                node_name: "OPEN"
            }
            state["workflow_status"] = "FAILED"
            state["should_continue"] = False
            logger.error(f"Circuit breaker OPEN for {node_name}")
        else:
            # Decide retry vs fail
            if self._is_retryable_error(error):
                state["should_continue"] = True
                state["current_step"] = node_name  # Retry same node
            else:
                state["workflow_status"] = "FAILED"
                state["should_continue"] = False
        
        return state
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if error is retryable."""
        retryable_types = [
            ConnectionError,
            TimeoutError,
            RateLimitError,
            TemporaryFailure
        ]
        return any(isinstance(error, t) for t in retryable_types)
```

#### 2.2 Wrap All Nodes
```python
# Location: langgraph_agent/graph/node_wrapper.py

def wrap_node_with_error_handling(node_func):
    """Wrap any node with error handling."""
    
    async def wrapped(state: UnifiedComplianceState) -> UnifiedComplianceState:
        error_handler = IntegratedErrorHandler()
        
        try:
            # Update current step
            state["current_step"] = node_func.__name__
            
            # Execute node
            result = await node_func(state)
            
            # Mark step completed
            state["steps_completed"].append(node_func.__name__)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in {node_func.__name__}: {e}")
            return await error_handler.handle_node_error(
                node_func.__name__, e, state
            )
    
    wrapped.__name__ = node_func.__name__
    return wrapped
```

### PHASE 3: Real RAG Implementation

#### 3.1 Implement Real RAG System
```python
# Location: langgraph_agent/rag/real_rag_system.py

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from tenacity import retry, stop_after_attempt, wait_exponential

class RealRAGSystem:
    """REAL RAG implementation with actual services."""
    
    def __init__(self):
        # Use real embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize or load vector store
        self.vector_store = self._initialize_vector_store()
        
        # Create retriever with compression
        self.retriever = self._create_retriever()
        
    def _initialize_vector_store(self):
        """Initialize FAISS vector store."""
        vector_path = "./compliance_vectors"
        
        if os.path.exists(vector_path):
            # Load existing
            return FAISS.load_local(
                folder_path=vector_path,
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            # Create new and populate with compliance docs
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            from langchain_community.document_loaders import DirectoryLoader
            
            # Load compliance documents
            loader = DirectoryLoader(
                "./compliance_docs",
                glob="**/*.md",
                show_progress=True
            )
            documents = loader.load()
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            texts = text_splitter.split_documents(documents)
            
            # Create vector store
            vector_store = FAISS.from_documents(texts, self.embeddings)
            
            # Save for future use
            vector_store.save_local(vector_path)
            
            return vector_store
    
    def _create_retriever(self):
        """Create retriever with reranking."""
        base_retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 10}
        )
        
        # Add compression for better results
        llm = ChatOpenAI(temperature=0)
        compressor = LLMChainExtractor.from_llm(llm)
        
        return ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def query_with_retry(
        self,
        query: str,
        state: UnifiedComplianceState,
        max_retries: int = 3
    ) -> UnifiedComplianceState:
        """Query with automatic retry and state update."""
        
        try:
            # Store query
            state["rag_queries"].append({
                "query": query,
                "timestamp": datetime.now().isoformat()
            })
            
            # Retrieve documents
            relevant_docs = await self.retriever.aget_relevant_documents(query)
            
            # Process and store results
            processed_docs = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": getattr(doc, "score", None)
                }
                for doc in relevant_docs
            ]
            
            state["relevant_documents"].extend(processed_docs)
            state["rag_responses"].append({
                "query": query,
                "documents": processed_docs,
                "timestamp": datetime.now().isoformat()
            })
            
            state["vector_store_status"] = "HEALTHY"
            
            logger.info(f"RAG query successful - found {len(relevant_docs)} documents")
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            state["vector_store_status"] = "ERROR"
            raise
        
        return state
```

#### 3.2 Create RAG Node
```python
# Location: langgraph_agent/nodes/rag_node.py

@wrap_node_with_error_handling
async def rag_query_node(state: UnifiedComplianceState) -> UnifiedComplianceState:
    """RAG query node with real implementation."""
    
    rag_system = RealRAGSystem()
    
    # Build query based on context
    query = build_compliance_query(state)
    
    # Execute query
    state = await rag_system.query_with_retry(query, state)
    
    # Analyze results for compliance
    if state["relevant_documents"]:
        compliance_context = analyze_compliance_context(
            state["relevant_documents"]
        )
        state["compliance_data"]["rag_context"] = compliance_context
    
    return state

def build_compliance_query(state: UnifiedComplianceState) -> str:
    """Build query from state context."""
    task_type = state.get("task_type", "compliance_check")
    
    if task_type == "compliance_check":
        regulation = state.get("metadata", {}).get("regulation", "GDPR")
        scope = state.get("metadata", {}).get("scope", "user_data")
        return f"What are the compliance requirements for {regulation} regarding {scope}?"
    
    elif task_type == "evidence_collection":
        evidence_type = state.get("metadata", {}).get("evidence_type", "policy")
        return f"What evidence is required to demonstrate {evidence_type} compliance?"
    
    return "General compliance requirements"
```

### PHASE 4: Complete Celery Task Migration

#### 4.1 Compliance Tasks Node (25% → 50%)
```python
# Location: langgraph_agent/nodes/compliance_nodes.py

@wrap_node_with_error_handling
async def compliance_check_node(state: UnifiedComplianceState) -> UnifiedComplianceState:
    """Complete compliance check implementation."""
    
    # Port from workers/compliance_tasks.py
    company_id = state.get("metadata", {}).get("company_id")
    regulation = state.get("metadata", {}).get("regulation", "GDPR")
    
    # Get compliance requirements from RAG
    requirements = extract_requirements_from_rag(state["relevant_documents"])
    
    # Check compliance status
    compliance_status = await check_compliance_status(
        company_id=company_id,
        regulation=regulation,
        requirements=requirements
    )
    
    # Store results
    state["compliance_data"]["check_results"] = compliance_status
    state["obligations"] = compliance_status.get("obligations", [])
    
    # Determine if notification needed
    if compliance_status.get("violations"):
        state["metadata"]["notify_required"] = True
        state["metadata"]["notify_type"] = "violation"
    
    return state

async def check_compliance_status(
    company_id: str,
    regulation: str,
    requirements: List[Dict]
) -> Dict:
    """Check compliance against requirements."""
    
    # Query Neo4j for current compliance state
    async with get_neo4j_session() as session:
        result = await session.run(
            """
            MATCH (c:Company {id: $company_id})-[:SUBJECT_TO]->(r:Regulation {name: $regulation})
            MATCH (r)-[:CONTAINS]->(o:Obligation)
            OPTIONAL MATCH (c)-[:HAS_EVIDENCE]->(e:Evidence)-[:SATISFIES]->(o)
            RETURN o, collect(e) as evidence
            """,
            company_id=company_id,
            regulation=regulation
        )
        
        obligations = []
        violations = []
        
        async for record in result:
            obligation = record["o"]
            evidence = record["evidence"]
            
            ob_data = {
                "id": obligation["id"],
                "title": obligation["title"],
                "satisfied": len(evidence) > 0,
                "evidence": [e["id"] for e in evidence]
            }
            
            obligations.append(ob_data)
            
            if not ob_data["satisfied"]:
                violations.append(ob_data)
        
        return {
            "obligations": obligations,
            "violations": violations,
            "compliance_score": len([o for o in obligations if o["satisfied"]]) / len(obligations) if obligations else 0
        }
```

#### 4.2 Notification Tasks Node (50% → 75%)
```python
# Location: langgraph_agent/nodes/notification_nodes.py

@wrap_node_with_error_handling
async def notification_node(state: UnifiedComplianceState) -> UnifiedComplianceState:
    """Complete notification implementation."""
    
    if not state.get("metadata", {}).get("notify_required"):
        return state
    
    notify_type = state["metadata"].get("notify_type", "info")
    
    # Port from workers/notification_tasks.py
    notifications_sent = []
    
    # Email notification
    if notify_type in ["violation", "critical"]:
        email_result = await send_email_notification(
            recipients=get_compliance_team_emails(),
            subject=f"Compliance {notify_type.upper()}: Action Required",
            body=format_compliance_notification(state)
        )
        notifications_sent.append(email_result)
    
    # Slack notification
    if os.getenv("SLACK_WEBHOOK_URL"):
        slack_result = await send_slack_notification(
            channel="#compliance-alerts",
            message=format_slack_message(state),
            severity=notify_type
        )
        notifications_sent.append(slack_result)
    
    # In-app notification
    app_result = await create_in_app_notification(
        user_ids=get_compliance_user_ids(),
        notification_type=notify_type,
        data=state["compliance_data"]
    )
    notifications_sent.append(app_result)
    
    state["metadata"]["notifications_sent"] = notifications_sent
    
    return state

async def send_email_notification(recipients: List[str], subject: str, body: str) -> Dict:
    """Send email via SendGrid or similar."""
    # Real implementation
    pass

async def send_slack_notification(channel: str, message: str, severity: str) -> Dict:
    """Send Slack webhook notification."""
    # Real implementation
    pass
```

#### 4.3 Reporting Tasks Node (75% → 100%)
```python
# Location: langgraph_agent/nodes/reporting_nodes.py

@wrap_node_with_error_handling
async def reporting_node(state: UnifiedComplianceState) -> UnifiedComplianceState:
    """Complete reporting implementation."""
    
    # Port from workers/reporting_tasks.py
    report_type = state.get("metadata", {}).get("report_type", "compliance_summary")
    
    if report_type == "compliance_summary":
        report = await generate_compliance_summary(state)
    elif report_type == "audit_trail":
        report = await generate_audit_trail(state)
    elif report_type == "risk_assessment":
        report = await generate_risk_assessment(state)
    else:
        report = await generate_standard_report(state)
    
    # Store report
    report_path = await store_report(report)
    
    # Update state
    state["metadata"]["report_generated"] = True
    state["metadata"]["report_path"] = report_path
    state["metadata"]["report_id"] = report["id"]
    
    # Store in database
    await save_report_metadata(report)
    
    return state

async def generate_compliance_summary(state: UnifiedComplianceState) -> Dict:
    """Generate comprehensive compliance report."""
    
    return {
        "id": str(uuid4()),
        "type": "compliance_summary",
        "generated_at": datetime.now().isoformat(),
        "workflow_id": state["workflow_id"],
        "compliance_score": state["compliance_data"].get("check_results", {}).get("compliance_score"),
        "obligations": state["obligations"],
        "evidence": state["evidence_items"],
        "violations": state["compliance_data"].get("check_results", {}).get("violations", []),
        "recommendations": generate_recommendations(state)
    }
```

### PHASE 5: Working Task Scheduler

#### 5.1 Implement Working Scheduler
```python
# Location: langgraph_agent/scheduler/working_scheduler.py

class WorkingTaskScheduler:
    """ACTUALLY working task scheduler."""
    
    def __init__(self, graph: CompiledGraph):
        self.graph = graph
        self.tasks = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = False
        self.scheduler = AsyncIOScheduler()
        
    async def schedule_task(
        self,
        task_type: str,
        schedule: str,  # Cron expression
        data: Dict[str, Any]
    ) -> ScheduledTask:
        """Schedule a task for execution."""
        
        task = ScheduledTask(
            id=str(uuid4()),
            type=task_type,
            schedule=schedule,
            data=data,
            status="SCHEDULED",
            created_at=datetime.now()
        )
        
        self.tasks[task.id] = task
        
        # Add to scheduler
        self.scheduler.add_job(
            func=self._execute_task_wrapper,
            trigger=CronTrigger.from_crontab(schedule),
            id=task.id,
            args=[task.id],
            replace_existing=True
        )
        
        return task
    
    async def _execute_task_wrapper(self, task_id: str):
        """Wrapper for task execution."""
        task = self.tasks.get(task_id)
        if task:
            await self.execute_task(task)
    
    async def execute_task(self, task: ScheduledTask) -> Any:
        """ACTUALLY execute the task through the graph."""
        
        # Create initial state
        initial_state = UnifiedComplianceState(
            workflow_id=str(uuid4()),
            workflow_status="PENDING",
            current_step="state_validator",
            messages=[],
            steps_completed=[],
            steps_remaining=["state_validator", task.type],
            retry_count=0,
            max_retries=3,
            should_continue=True,
            errors=[],
            error_count=0,
            error_correlation_id=None,
            circuit_breaker_status={},
            last_error_time=None,
            rag_queries=[],
            rag_responses=[],
            relevant_documents=[],
            vector_store_status="UNKNOWN",
            scheduled_task_id=task.id,
            task_type=task.type,
            task_schedule=task.schedule,
            task_result=None,
            celery_task_status=None,
            compliance_data={},
            evidence_items=[],
            obligations=[],
            assessment_results={},
            history=[],
            metadata=task.data,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            checkpoint_id=None,
            thread_id=f"task-{task.id}"
        )
        
        try:
            # Update task status
            task.status = "RUNNING"
            task.started_at = datetime.now()
            
            # Configure thread
            config = {
                "configurable": {
                    "thread_id": initial_state["thread_id"],
                    "checkpoint_ns": "scheduled_tasks"
                }
            }
            
            # ACTUALLY RUN THE GRAPH
            logger.info(f"Executing task {task.id} through graph")
            
            final_state = await self.graph.ainvoke(
                initial_state,
                config=config
            )
            
            # Update task with results
            task.status = "COMPLETED"
            task.completed_at = datetime.now()
            task.result = {
                "workflow_id": final_state["workflow_id"],
                "status": final_state["workflow_status"],
                "compliance_data": final_state["compliance_data"],
                "report_id": final_state.get("metadata", {}).get("report_id")
            }
            
            logger.info(f"Task {task.id} completed successfully")
            
            return task.result
            
        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            task.status = "FAILED"
            task.error = str(e)
            task.completed_at = datetime.now()
            raise
    
    async def start(self):
        """Start the scheduler."""
        self.running = True
        self.scheduler.start()
        logger.info("Task scheduler started")
        
    async def stop(self):
        """Stop the scheduler."""
        self.running = False
        self.scheduler.shutdown()
        logger.info("Task scheduler stopped")
```

### Integration Layer: Master Orchestrator

```python
# Location: langgraph_agent/orchestrator.py

class ComplianceOrchestrator:
    """Master orchestrator connecting all components."""
    
    def __init__(self):
        # Build complete graph
        self.graph = build_integrated_graph()
        
        # Initialize scheduler with graph
        self.scheduler = WorkingTaskScheduler(self.graph)
        
        # Initialize error handler
        self.error_handler = IntegratedErrorHandler()
        
        # Initialize RAG system
        self.rag_system = RealRAGSystem()
        
        # Track active workflows
        self.active_workflows = {}
        
    async def start_system(self):
        """Start all system components."""
        
        logger.info("Starting Compliance Orchestrator")
        
        # Initialize vector stores
        await self.rag_system._initialize_vector_store()
        
        # Start scheduler
        await self.scheduler.start()
        
        # Process any pending tasks
        await self.process_pending_tasks()
        
        logger.info("Compliance Orchestrator started successfully")
    
    async def run_workflow(
        self,
        workflow_type: str,
        input_data: Dict[str, Any]
    ) -> UnifiedComplianceState:
        """Execute a complete workflow."""
        
        workflow_id = str(uuid4())
        
        # Create initial state
        initial_state = create_unified_initial_state(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            input_data=input_data
        )
        
        # Configure thread
        config = {
            "configurable": {
                "thread_id": f"workflow-{workflow_id}",
                "checkpoint_ns": "compliance_workflows"
            }
        }
        
        # Track workflow
        self.active_workflows[workflow_id] = {
            "status": "RUNNING",
            "started_at": datetime.now()
        }
        
        try:
            # Execute workflow
            final_state = await self.graph.ainvoke(
                initial_state,
                config=config
            )
            
            # Update tracking
            self.active_workflows[workflow_id]["status"] = "COMPLETED"
            self.active_workflows[workflow_id]["completed_at"] = datetime.now()
            
            return final_state
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}")
            self.active_workflows[workflow_id]["status"] = "FAILED"
            self.active_workflows[workflow_id]["error"] = str(e)
            raise
    
    async def process_pending_tasks(self):
        """Process any tasks that were scheduled while system was down."""
        
        # Query database for pending scheduled tasks
        # Re-schedule them with the scheduler
        pass
```

## Testing Requirements

### 1. Real Integration Test
```python
# Location: tests/test_complete_integration.py

@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_compliance_workflow():
    """Test COMPLETE workflow with REAL services."""
    
    # Initialize orchestrator
    orchestrator = ComplianceOrchestrator()
    await orchestrator.start_system()
    
    # Schedule a real compliance check task
    task = await orchestrator.scheduler.schedule_task(
        task_type="compliance_check",
        schedule="0 */4 * * *",  # Every 4 hours
        data={
            "company_id": str(uuid4()),
            "regulation": "GDPR",
            "scope": "user_data"
        }
    )
    
    # Execute immediately for testing
    await orchestrator.scheduler.execute_task(task)
    
    # Wait for completion
    await asyncio.sleep(5)
    
    # Verify ACTUAL execution
    assert task.status == "COMPLETED"
    assert task.result is not None
    
    # Verify all phases executed
    result = task.result
    assert result["workflow_id"] is not None
    assert result["status"] == "COMPLETED"
    assert "compliance_data" in result
    assert "report_id" in result
    
    # Stop system
    await orchestrator.scheduler.stop()
```

### 2. Load Test
```python
@pytest.mark.load
@pytest.mark.asyncio
async def test_concurrent_workflows():
    """Test system under load."""
    
    orchestrator = ComplianceOrchestrator()
    await orchestrator.start_system()
    
    # Run 10 concurrent workflows
    tasks = []
    for i in range(10):
        task = orchestrator.run_workflow(
            workflow_type="compliance_check",
            input_data={"test_id": i}
        )
        tasks.append(task)
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks)
    
    # Verify all completed
    for result in results:
        assert result["workflow_status"] in ["COMPLETED", "FAILED"]
```

## Delivery Checklist

- [ ] UnifiedComplianceState fully implemented
- [ ] Error handler node properly implements retry logic
- [ ] Graph connects all nodes with proper routing
- [ ] PostgreSQL checkpointing works correctly
- [ ] Circuit breakers protect all external calls
- [ ] RAG system uses real OpenAI API and FAISS
- [ ] All 4 Celery task types fully migrated:
  - [ ] Evidence tasks (2/2)
  - [ ] Compliance tasks (2/2)
  - [ ] Notification tasks (3/3)
  - [ ] Reporting tasks (4/4)
- [ ] Scheduler actually executes tasks through graph
- [ ] Integration tests use real services (no mocks)
- [ ] System handles errors gracefully with retries
- [ ] Load tests pass with 10+ concurrent workflows
- [ ] 24-hour stability test passes
- [ ] Monitoring and alerting configured
- [ ] Documentation complete

## Success Metrics

1. **100% Task Migration**: All 11 Celery tasks migrated
2. **Real Service Integration**: OpenAI, PostgreSQL, Neo4j all connected
3. **Error Recovery**: 95% of transient errors recovered automatically
4. **Performance**: <500ms node execution, <100ms checkpoint save
5. **Stability**: 24-hour continuous operation without crashes
6. **Test Coverage**: 90%+ with real integration tests

## Next Steps

1. Start with Phase 1 - Fix state management and graph foundation
2. Ensure error handler node is properly implemented
3. Build complete graph with all nodes connected
4. Proceed phase by phase, testing each thoroughly
5. No phase is complete until integration tests pass