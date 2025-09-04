!# Phase 4: Celery to LangGraph Migration

Convert Celery background tasks to LangGraph nodes with built-in persistence.

## Current Issues to Fix

1. Dependency on Redis and Celery
2. Complex retry logic in task decorators
3. Separate beat schedule configuration
4. No built-in state persistence

## Required Changes

### File: Create `langgraph_agent/persistence/compliance_tasks.py`

Convert compliance scoring Celery task to LangGraph:

```python
from typing import TypedDict, Annotated, List, Dict, Any
from operator import add
from datetime import datetime
from uuid import UUID
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

class ComplianceTaskState(TypedDict):
    """State for compliance scoring tasks."""
    task_id: str
    task_type: str
    company_id: Optional[str]
    
    # Progress tracking
    current_step: str
    progress: int
    total_items: int
    
    # Results
    processed_profiles: Annotated[List[str], add]
    scores: Annotated[Dict[str, float], lambda x, y: {**x, **y}]
    alerts: Annotated[List[Dict[str, Any]], add]
    
    # Error handling
    errors: Annotated[List[str], add]
    retry_count: int
    
    # Completion
    completed: bool
    completion_time: Optional[datetime]
    
def create_compliance_scoring_graph():
    """Create graph for compliance scoring (replaces Celery task)."""
    
    graph = StateGraph(ComplianceTaskState)
    
    # Node: Fetch all business profiles
    async def fetch_profiles_node(state: ComplianceTaskState) -> ComplianceTaskState:
        """Fetch all business profiles for scoring."""
        logger.info(f"Fetching profiles for task {state['task_id']}")
        
        try:
            from database.db_setup import get_async_db
            from database.business_profile import BusinessProfile
            
            async for db in get_async_db():
                profiles_res = await db.execute(select(BusinessProfile))
                profiles = profiles_res.scalars().all()
                
                state["total_items"] = len(profiles)
                state["current_step"] = "calculate_scores"
                state["progress"] = 20
                
                # Store profile IDs for processing
                for profile in profiles:
                    state["processed_profiles"].append(str(profile.id))
                
                logger.info(f"Found {len(profiles)} profiles to score")
                
        except Exception as e:
            state["errors"].append(f"Failed to fetch profiles: {e}")
            state["current_step"] = "error"
        
        return state
    
    # Node: Calculate compliance scores
    async def calculate_scores_node(state: ComplianceTaskState) -> ComplianceTaskState:
        """Calculate compliance scores for all profiles."""
        logger.info(f"Calculating scores for {len(state['processed_profiles'])} profiles")
        
        try:
            from services.readiness_service import generate_readiness_assessment
            from database.db_setup import get_async_db
            
            async for db in get_async_db():
                for i, profile_id in enumerate(state["processed_profiles"]):
                    try:
                        # Calculate score
                        readiness_data = await generate_readiness_assessment(
                            UUID(profile_id), db
                        )
                        
                        score = readiness_data.get("overall_score", 0)
                        state["scores"][profile_id] = score
                        
                        # Check for alerts
                        if score < 70:
                            state["alerts"].append({
                                "profile_id": profile_id,
                                "score": score,
                                "message": "Compliance score below threshold"
                            })
                        
                        # Update progress
                        state["progress"] = 20 + int((i + 1) / len(state["processed_profiles"]) * 60)
                        
                    except Exception as e:
                        state["errors"].append(f"Failed to score profile {profile_id}: {e}")
                
                state["current_step"] = "send_notifications"
                state["progress"] = 80
                
        except Exception as e:
            state["errors"].append(f"Failed to calculate scores: {e}")
            state["current_step"] = "error"
        
        return state
    
    # Node: Send notifications for alerts
    async def send_notifications_node(state: ComplianceTaskState) -> ComplianceTaskState:
        """Send notifications for compliance alerts."""
        logger.info(f"Sending notifications for {len(state['alerts'])} alerts")
        
        if state["alerts"]:
            # Here you would integrate with notification service
            # For now, just log
            for alert in state["alerts"]:
                logger.warning(f"Compliance alert: Profile {alert['profile_id']} score {alert['score']}")
        
        state["current_step"] = "complete"
        state["progress"] = 100
        state["completed"] = True
        state["completion_time"] = datetime.utcnow()
        
        return state
    
    # Node: Error handler
    async def error_handler_node(state: ComplianceTaskState) -> ComplianceTaskState:
        """Handle errors with retry logic."""
        logger.error(f"Error in compliance scoring: {state['errors']}")
        
        if state["retry_count"] < 3:
            state["retry_count"] += 1
            # Reset to last successful step
            if state["processed_profiles"]:
                state["current_step"] = "calculate_scores"
            else:
                state["current_step"] = "fetch_profiles"
            logger.info(f"Retrying from {state['current_step']}, attempt {state['retry_count']}")
        else:
            state["current_step"] = "failed"
            state["completed"] = True
            logger.error(f"Task {state['task_id']} failed after {state['retry_count']} retries")
        
        return state
    
    # Add nodes to graph
    graph.add_node("fetch_profiles", fetch_profiles_node)
    graph.add_node("calculate_scores", calculate_scores_node)
    graph.add_node("send_notifications", send_notifications_node)
    graph.add_node("error_handler", error_handler_node)
    
    # Define edges
    graph.set_entry_point("fetch_profiles")
    
    # Conditional routing based on current_step
    def route_by_step(state: ComplianceTaskState) -> str:
        return state["current_step"]
    
    graph.add_conditional_edges(
        "fetch_profiles",
        route_by_step,
        {
            "calculate_scores": "calculate_scores",
            "error": "error_handler"
        }
    )
    
    graph.add_conditional_edges(
        "calculate_scores",
        route_by_step,
        {
            "send_notifications": "send_notifications",
            "error": "error_handler"
        }
    )
    
    graph.add_conditional_edges(
        "error_handler",
        route_by_step,
        {
            "fetch_profiles": "fetch_profiles",
            "calculate_scores": "calculate_scores",
            "failed": END
        }
    )
    
    graph.add_edge("send_notifications", END)
    
    # Compile with checkpointer
    checkpointer = PostgresSaver.from_conn_string(
        "postgresql://user:pass@localhost/compliance"
    )
    
    return graph.compile(checkpointer=checkpointer)


class ComplianceTaskManager:
    """Manager for compliance tasks (replaces Celery)."""
    
    def __init__(self):
        self.graph = create_compliance_scoring_graph()
        self.active_tasks: Dict[str, str] = {}  # task_id -> thread_id
    
    async def update_all_compliance_scores(self, company_id: Optional[str] = None):
        """
        Update compliance scores for all profiles.
        Replaces: workers.compliance_tasks.update_all_compliance_scores
        """
        task_id = f"compliance_score_{datetime.now().isoformat()}"
        thread_id = f"thread_{task_id}"
        
        # Check if already running
        if company_id and company_id in self.active_tasks:
            existing_thread = self.active_tasks[company_id]
            state = self.graph.get_state({"configurable": {"thread_id": existing_thread}})
            
            if state and not state.values.get("completed", False):
                logger.info(f"Task already running for company {company_id}")
                return {"status": "already_running", "thread_id": existing_thread}
        
        # Initialize state
        initial_state = ComplianceTaskState(
            task_id=task_id,
            task_type="compliance_scoring",
            company_id=company_id,
            current_step="fetch_profiles",
            progress=0,
            total_items=0,
            processed_profiles=[],
            scores={},
            alerts=[],
            errors=[],
            retry_count=0,
            completed=False,
            completion_time=None
        )
        
        # Run with checkpointing
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Start async execution
            result = await self.graph.ainvoke(initial_state, config)
            
            # Store task reference
            if company_id:
                self.active_tasks[company_id] = thread_id
            
            return {
                "status": "completed" if result["completed"] else "failed",
                "task_id": task_id,
                "thread_id": thread_id,
                "scores_calculated": len(result["scores"]),
                "alerts_generated": len(result["alerts"]),
                "errors": result["errors"]
            }
            
        except Exception as e:
            logger.error(f"Failed to run compliance scoring: {e}")
            return {
                "status": "error",
                "task_id": task_id,
                "error": str(e)
            }
    
    async def check_compliance_alerts(self):
        """
        Check for compliance alerts.
        Replaces: workers.compliance_tasks.check_compliance_alerts
        """
        # Reuse the same graph but focus on alerts
        result = await self.update_all_compliance_scores()
        
        if result["status"] == "completed":
            return {
                "status": "completed",
                "alerts_count": result.get("alerts_generated", 0),
                "alerts": []  # Would fetch from state if needed
            }
        
        return result
    
    def get_task_status(self, thread_id: str) -> Dict[str, Any]:
        """Get status of a running task (replaces Celery result backend)."""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)
        
        if not state:
            return {"status": "not_found"}
        
        values = state.values
        return {
            "status": "completed" if values.get("completed") else "running",
            "progress": values.get("progress", 0),
            "current_step": values.get("current_step"),
            "errors": values.get("errors", []),
            "scores_calculated": len(values.get("scores", {})),
            "alerts_generated": len(values.get("alerts", []))
        }
```

### File: Create `langgraph_agent/persistence/scheduler.py`

Replace Celery Beat with simple scheduler:

```python
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)

class TaskScheduler:
    """Simple task scheduler to replace Celery Beat."""
    
    def __init__(self):
        self.scheduled_tasks: Dict[str, Dict[str, Any]] = {}
        self.running = False
        self.task_manager = ComplianceTaskManager()
    
    def schedule_task(
        self,
        name: str,
        func: Callable,
        interval: timedelta,
        start_time: datetime = None
    ):
        """Schedule a recurring task."""
        self.scheduled_tasks[name] = {
            "func": func,
            "interval": interval,
            "last_run": start_time or datetime.utcnow(),
            "next_run": (start_time or datetime.utcnow()) + interval
        }
        logger.info(f"Scheduled task {name} with interval {interval}")
    
    async def run_scheduler(self):
        """Main scheduler loop."""
        self.running = True
        logger.info("Task scheduler started")
        
        while self.running:
            now = datetime.utcnow()
            
            for name, task in self.scheduled_tasks.items():
                if now >= task["next_run"]:
                    logger.info(f"Running scheduled task: {name}")
                    
                    try:
                        # Run task
                        await task["func"]()
                        
                        # Update schedule
                        task["last_run"] = now
                        task["next_run"] = now + task["interval"]
                        
                    except Exception as e:
                        logger.error(f"Failed to run task {name}: {e}")
            
            # Sleep for a minute before checking again
            await asyncio.sleep(60)
    
    def setup_default_schedule(self):
        """Set up default schedule (replaces Celery beat schedule)."""
        
        # Daily compliance score update
        self.schedule_task(
            "daily_compliance_scores",
            self.task_manager.update_all_compliance_scores,
            timedelta(days=1)
        )
        
        # Hourly alert check
        self.schedule_task(
            "hourly_alert_check",
            self.task_manager.check_compliance_alerts,
            timedelta(hours=1)
        )
```

## Migration Steps

1. Create LangGraph versions of each Celery task
2. Implement checkpointing for persistence
3. Create simple scheduler for periodic tasks
4. Update API endpoints to use new task manager
5. Remove Celery and Redis dependencies

## Testing Requirements

1. Tasks complete successfully
2. Checkpointing allows resumption
3. Retry logic works
4. Scheduled tasks run on time
5. No Redis/Celery dependencies

## Success Criteria

- [ ] All Celery tasks converted to LangGraph
- [ ] Checkpointing operational
- [ ] Scheduler replacing Beat
- [ ] Tests passing for all tasks
- [ ] Redis/Celery removed from requirements.txt
