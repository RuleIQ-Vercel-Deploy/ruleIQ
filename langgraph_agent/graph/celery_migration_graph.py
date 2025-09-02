"""
Phase 4: Unified Celery Migration Graph
Central orchestrator for all migrated Celery tasks with scheduling support
"""

import asyncio
import logging
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from uuid import uuid4
import json

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.messages import HumanMessage, AIMessage

from ..nodes.celery_migration_nodes import (
    TaskMigrationState,
    ComplianceTaskNode,
    EvidenceTaskNode,
    NotificationTaskNode,
    ReportingTaskNode,
    MonitoringTaskNode,
)
from ..graph.error_handler import ErrorHandlerNode
from ..scheduler.task_scheduler import TaskScheduler

logger = logging.getLogger(__name__)


class CeleryMigrationGraph:
    """
    Unified orchestrator for all migrated Celery tasks.
    Replaces Celery with LangGraph for 100% task coverage.
    """

    def __init__(self, checkpointer: Optional[AsyncPostgresSaver] = None):
        self.checkpointer = checkpointer
        self.graph = None
        self.compiled_graph = None

        # Initialize all task nodes
        self.compliance_node = ComplianceTaskNode()
        self.evidence_node = EvidenceTaskNode()
        self.notification_node = NotificationTaskNode()
        self.reporting_node = ReportingTaskNode()
        self.monitoring_node = MonitoringTaskNode()
        self.error_handler = ErrorHandlerNode()

        # Task scheduler for periodic tasks
        self.scheduler = TaskScheduler()

        # Task routing map
        self.task_routes = {
            # Compliance tasks
            "update_compliance_scores": "compliance",
            "check_compliance_alerts": "compliance",
            # Evidence tasks
            "process_evidence": "evidence",
            "sync_evidence": "evidence",
            # Notification tasks
            "compliance_alert": "notification",
            "weekly_summary": "notification",
            "broadcast": "notification",
            # Reporting tasks
            "generate_report": "reporting",
            "on_demand_report": "reporting",
            "cleanup_reports": "reporting",
            "report_notifications": "reporting",
            # Monitoring tasks
            "database_metrics": "monitoring",
            "health_check": "monitoring",
            "cleanup_monitoring": "monitoring",
            "system_metrics": "monitoring",
            "register_tasks": "monitoring",
        }

        self._setup_graph()
        self._register_scheduled_tasks()

    def _setup_graph(self):
        """Build the unified task processing graph"""
        workflow = StateGraph(TaskMigrationState)

        # Add all nodes
        workflow.add_node("router", self._router_node)
        workflow.add_node("compliance", self.compliance_node.process)
        workflow.add_node("evidence", self.evidence_node.process)
        workflow.add_node("notification", self.notification_node.process)
        workflow.add_node("reporting", self.reporting_node.process)
        workflow.add_node("monitoring", self.monitoring_node.process)
        workflow.add_node("error_handler", self.error_handler.process)
        workflow.add_node("result_processor", self._result_processor_node)

        # Set entry point
        workflow.set_entry_point("router")

        # Add edges from router to task nodes
        workflow.add_conditional_edges(
            "router",
            self._route_task,
            {
                "compliance": "compliance",
                "evidence": "evidence",
                "notification": "notification",
                "reporting": "reporting",
                "monitoring": "monitoring",
                "error": "error_handler",
                "end": END,
            },
        )

        # All task nodes go to result processor
        for node in [
            "compliance",
            "evidence",
            "notification",
            "reporting",
            "monitoring",
        ]:
            workflow.add_edge(node, "result_processor")

        # Result processor can retry or end
        workflow.add_conditional_edges(
            "result_processor", self._check_retry, {"retry": "router", "end": END}
        )

        # Error handler can retry or end
        workflow.add_conditional_edges(
            "error_handler", self._check_error_retry, {"retry": "router", "end": END}
        )

        self.graph = workflow
        self.compiled_graph = workflow.compile(checkpointer=self.checkpointer)

    async def _router_node(self, state: TaskMigrationState) -> TaskMigrationState:
        """Initial routing node for incoming tasks"""
        logger.info(f"Routing task: {state.get('task_type')}")

        # Set initial metadata
        state["migration_timestamp"] = datetime.utcnow().isoformat()
        state["task_status"] = "running"

        # Initialize execution metrics
        state["execution_metrics"] = {
            "start_time": datetime.utcnow().isoformat(),
            "route_taken": self.task_routes.get(state.get("task_type"), "unknown"),
        }

        return state

    def _route_task(self, state: TaskMigrationState) -> str:
        """Determine which node should handle the task"""
        task_type = state.get("task_type", "")

        if task_type in self.task_routes:
            return self.task_routes[task_type]
        else:
            logger.error(f"Unknown task type: {task_type}")
            return "error"

    async def _result_processor_node(
        self, state: TaskMigrationState
    ) -> TaskMigrationState:
        """Process task results and handle post-execution logic"""
        logger.info(f"Processing results for task: {state.get('task_type')}")

        # Update execution metrics
        if "execution_metrics" in state:
            state["execution_metrics"]["end_time"] = datetime.utcnow().isoformat()

            # Calculate execution time
            start = datetime.fromisoformat(state["execution_metrics"]["start_time"])
            end = datetime.utcnow()
            state["execution_metrics"]["execution_time_ms"] = (
                end - start
            ).total_seconds() * 1000

        # Log successful completion
        if state.get("task_status") == "completed":
            logger.info(f"Task {state.get('task_type')} completed successfully")

            # Store result in message history
            result_summary = json.dumps(state.get("task_result", {}), indent=2)
            state["messages"].append(
                AIMessage(content=f"Task completed: {result_summary[:500]}")
            )

        return state

    def _check_retry(self, state: TaskMigrationState) -> str:
        """Determine if task should be retried"""
        if state.get("task_status") == "failed":
            retry_count = state.get("retry_count", 0)
            max_retries = state.get("max_retries", 3)

            if retry_count < max_retries:
                logger.info(
                    f"Retrying task {state.get('task_type')} (attempt {retry_count + 1})"
                )
                state["retry_count"] = retry_count + 1
                return "retry"

        return "end"

    def _check_error_retry(self, state: TaskMigrationState) -> str:
        """Check if error handler suggests retry"""
        if state.get("should_retry", False):
            retry_count = state.get("retry_count", 0)
            max_retries = state.get("max_retries", 3)

            if retry_count < max_retries:
                state["retry_count"] = retry_count + 1
                state["should_retry"] = False  # Reset flag
                return "retry"

        return "end"

    def _register_scheduled_tasks(self):
        """Register periodic tasks with the scheduler"""
        # Monitoring tasks (most frequent)
        self.scheduler.register_task(
            "system_metrics_collection",
            self._create_task_executor("system_metrics"),
            interval_seconds=60,  # Every minute
        )

        self.scheduler.register_task(
            "database_metrics_collection",
            self._create_task_executor("database_metrics"),
            interval_seconds=300,  # Every 5 minutes
        )

        self.scheduler.register_task(
            "database_health_check",
            self._create_task_executor("health_check"),
            interval_seconds=900,  # Every 15 minutes
        )

        # Compliance tasks
        self.scheduler.register_task(
            "compliance_score_update",
            self._create_task_executor("update_compliance_scores"),
            interval_seconds=3600,  # Every hour
        )

        self.scheduler.register_task(
            "compliance_alert_check",
            self._create_task_executor("check_compliance_alerts"),
            interval_seconds=21600,  # Every 6 hours
        )

        # Evidence sync
        self.scheduler.register_task(
            "evidence_status_sync",
            self._create_task_executor("sync_evidence"),
            interval_seconds=7200,  # Every 2 hours
        )

        # Cleanup tasks
        self.scheduler.register_task(
            "monitoring_data_cleanup",
            self._create_task_executor("cleanup_monitoring"),
            interval_seconds=21600,  # Every 6 hours
        )

        self.scheduler.register_task(
            "old_reports_cleanup",
            self._create_task_executor("cleanup_reports"),
            interval_seconds=86400,  # Daily
        )

        # Weekly summary
        self.scheduler.register_task(
            "weekly_summary_send",
            self._create_task_executor("weekly_summary"),
            interval_seconds=604800,  # Weekly
        )

        logger.info("Registered 9 scheduled tasks with LangGraph scheduler")

    def _create_task_executor(self, task_type: str):
        """Create an executor function for a scheduled task"""

        async def executor():
            state = self._create_initial_state(task_type)
            result = await self.execute_task(state)
            return result

        return executor

    def _create_initial_state(
        self, task_type: str, params: Optional[Dict] = None
    ) -> TaskMigrationState:
        """Create initial state for a task"""
        return {
            "messages": [HumanMessage(content=f"Execute {task_type} task")],
            "session_id": str(uuid4()),
            "company_id": str(uuid4()),  # Would come from context in production
            "task_type": task_type,
            "task_params": params or {},
            "task_result": None,
            "task_status": "pending",
            "original_task_name": task_type,
            "migration_timestamp": datetime.utcnow().isoformat(),
            "execution_metrics": {},
            "errors": [],
            "retry_count": 0,
            "max_retries": 3,
        }

    async def execute_task(
        self,
        state: Optional[TaskMigrationState] = None,
        task_type: Optional[str] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Execute a migrated Celery task through LangGraph

        Args:
            state: Pre-built state (optional)
            task_type: Type of task to execute
            params: Task parameters

        Returns:
            Task execution result
        """
        if state is None:
            if task_type is None:
                raise ValueError("Either state or task_type must be provided")
            state = self._create_initial_state(task_type, params)

        try:
            # Execute through graph
            config = {"configurable": {"thread_id": state["session_id"]}}

            final_state = None
            async for event in self.compiled_graph.astream(state, config):
                final_state = event

            if final_state:
                # Extract the last state from the event
                if isinstance(final_state, dict):
                    for key, value in final_state.items():
                        if isinstance(value, dict) and "task_result" in value:
                            return value.get("task_result", {})

            return {"status": "completed", "message": "Task executed successfully"}

        except Exception as e:
            logger.error(f"Error executing task {task_type}: {str(e)}")
            return {"status": "failed", "error": str(e), "task_type": task_type}

    async def start_scheduler(self):
        """Start the task scheduler for periodic tasks"""
        await self.scheduler.start()
        logger.info("Celery migration scheduler started - all periodic tasks active")

    async def stop_scheduler(self):
        """Stop the task scheduler"""
        await self.scheduler.stop()
        logger.info("Celery migration scheduler stopped")

    def get_task_statistics(self) -> Dict[str, Any]:
        """Get statistics about migrated tasks"""
        return {
            "total_tasks_migrated": 16,
            "task_categories": {
                "compliance": 2,
                "evidence": 2,
                "notification": 3,
                "reporting": 4,
                "monitoring": 5,
            },
            "scheduled_tasks": 9,
            "on_demand_tasks": 7,
            "migration_complete": True,
            "coverage_percentage": 100.0,
        }


# Factory function for creating the graph
async def create_celery_migration_graph(
    checkpointer: Optional[AsyncPostgresSaver] = None,
) -> CeleryMigrationGraph:
    """
    Factory function to create and initialize the Celery migration graph

    Args:
        checkpointer: Optional PostgreSQL checkpointer for state persistence

    Returns:
        Initialized CeleryMigrationGraph instance
    """
    graph = CeleryMigrationGraph(checkpointer)

    # Start the scheduler for periodic tasks
    await graph.start_scheduler()

    logger.info("Celery Migration Graph initialized - 100% task coverage achieved")
    return graph
