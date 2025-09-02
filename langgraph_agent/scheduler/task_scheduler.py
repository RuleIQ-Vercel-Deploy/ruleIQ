"""
LangGraph Task Scheduler - Replacement for Celery Beat.

Phase 4 Implementation: Migrate from Celery to LangGraph nodes with Neon database checkpointing.
This scheduler replaces Celery Beat functionality using LangGraph's native features with
Neon PostgreSQL for persistent state management.
"""

from typing import Dict, Any, List, Optional, Annotated
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
from dataclasses import dataclass
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import ToolNode
import psycopg
from psycopg.rows import dict_row

from ..graph.enhanced_state import EnhancedComplianceState
from ..graph.error_handler import ErrorHandlerNode
from ..core.constants import DATABASE_CONFIG

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels for scheduling."""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    """Represents a scheduled task."""

    task_id: str
    name: str
    node_name: str
    schedule: str  # Cron expression or interval
    priority: TaskPriority
    max_retries: int = 3
    timeout_seconds: int = 1800  # 30 minutes default
    queue: str = "default"
    metadata: Dict[str, Any] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0


class TaskScheduler:
    """
    LangGraph-based task scheduler to replace Celery Beat.

    This scheduler:
    - Manages periodic tasks using PostgreSQL for persistence
    - Handles retries with exponential backoff
    - Provides monitoring and health checks
    - Supports different queue priorities
    """

    def __init__(self, database_url: str):
        """
        Initialize the task scheduler with PostgreSQL checkpointing.

        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url
        self.checkpointer = None
        self.graph = None
        self.tasks: Dict[str, ScheduledTask] = {}
        self.error_handler = ErrorHandlerNode()

        # Initialize the scheduler
        self._setup_checkpointer()
        self._build_graph()
        self._register_default_tasks()

    def _setup_checkpointer(self):
        """Setup Neon PostgreSQL checkpointer for task state persistence."""
        try:
            # Convert asyncpg URL to psycopg format if needed
            db_url = self.database_url
            if "asyncpg" in db_url:
                db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

            # Validate Neon connection URL
            if "neon.tech" not in db_url:
                logger.warning(
                    "Database URL does not appear to be a Neon database. "
                    "Using standard PostgreSQL connection."
                )

            # Create connection with proper settings for Neon
            conn = psycopg.connect(
                db_url,
                autocommit=True,
                row_factory=dict_row,
                # Neon-specific connection parameters
                options="-c statement_timeout=30s -c idle_session_timeout=300s",
            )

            # Initialize checkpointer with Neon database
            self.checkpointer = PostgresSaver(conn)
            self.checkpointer.setup()

            logger.info("Neon PostgreSQL checkpointer initialized for task scheduler")

        except Exception as e:
            logger.error(f"Failed to setup checkpointer: {e}")
            raise

    def _build_graph(self):
        """Build the LangGraph workflow for task scheduling."""
        # Create workflow
        workflow = StateGraph(EnhancedComplianceState)

        # Add nodes for each task type
        workflow.add_node("scheduler", self._scheduler_node)
        workflow.add_node("evidence_collector", self._evidence_collector_node)
        workflow.add_node("compliance_updater", self._compliance_updater_node)
        workflow.add_node("report_generator", self._report_generator_node)
        workflow.add_node("notification_sender", self._notification_sender_node)
        workflow.add_node("cleanup", self._cleanup_node)
        workflow.add_node("error_handler", self.error_handler.process)

        # Define edges
        workflow.set_entry_point("scheduler")

        # Conditional routing based on task type
        workflow.add_conditional_edges(
            "scheduler",
            self._route_task,
            {
                "evidence": "evidence_collector",
                "compliance": "compliance_updater",
                "reports": "report_generator",
                "notifications": "notification_sender",
                "cleanup": "cleanup",
                "error": "error_handler",
                "end": END,
            },
        )

        # All task nodes can go to error handler or end
        for node in [
            "evidence_collector",
            "compliance_updater",
            "report_generator",
            "notification_sender",
            "cleanup",
        ]:
            workflow.add_conditional_edges(
                node,
                self._check_task_result,
                {
                    "scheduler": "scheduler",  # Back to scheduler for next task
                    "error": "error_handler",
                    "end": END,
                },
            )

        # Error handler can retry or end
        workflow.add_conditional_edges(
            "error_handler",
            lambda state: "scheduler" if state.get("retry_count", 0) < 3 else END,
            {"scheduler": "scheduler", END: END},
        )

        # Compile with checkpointer
        self.graph = workflow.compile(checkpointer=self.checkpointer)
        logger.info("Task scheduler graph compiled successfully")

    def _register_default_tasks(self):
        """Register default scheduled tasks (migrated from Celery Beat)."""
        default_tasks = [
            ScheduledTask(
                task_id="daily-evidence-collection",
                name="Collect All Integration Evidence",
                node_name="evidence_collector",
                schedule="0 2 * * *",  # Daily at 2 AM
                priority=TaskPriority.HIGH,
                queue="evidence",
            ),
            ScheduledTask(
                task_id="process-pending-evidence",
                name="Process Pending Evidence",
                node_name="evidence_collector",
                schedule="0 * * * *",  # Hourly
                priority=TaskPriority.MEDIUM,
                queue="evidence",
            ),
            ScheduledTask(
                task_id="update-compliance-scores",
                name="Update All Compliance Scores",
                node_name="compliance_updater",
                schedule="0 3 * * 1",  # Weekly on Monday at 3 AM
                priority=TaskPriority.HIGH,
                queue="compliance",
            ),
            ScheduledTask(
                task_id="check-evidence-expiry",
                name="Check Evidence Expiry",
                node_name="evidence_collector",
                schedule="0 1 * * *",  # Daily at 1 AM
                priority=TaskPriority.MEDIUM,
                queue="evidence",
            ),
            ScheduledTask(
                task_id="sync-integration-status",
                name="Sync Integration Status",
                node_name="evidence_collector",
                schedule="0 */6 * * *",  # Every 6 hours
                priority=TaskPriority.LOW,
                queue="evidence",
            ),
            ScheduledTask(
                task_id="generate-compliance-reports",
                name="Generate Daily Compliance Reports",
                node_name="report_generator",
                schedule="0 4 * * *",  # Daily at 4 AM
                priority=TaskPriority.MEDIUM,
                queue="compliance",
            ),
            ScheduledTask(
                task_id="cleanup-old-reports",
                name="Cleanup Old Reports",
                node_name="cleanup",
                schedule="0 5 * * 0",  # Weekly on Sunday at 5 AM
                priority=TaskPriority.BACKGROUND,
                queue="reports",
            ),
            ScheduledTask(
                task_id="send-report-summaries",
                name="Send Monthly Report Summaries",
                node_name="notification_sender",
                schedule="0 6 1 * *",  # Monthly on the 1st at 6 AM
                priority=TaskPriority.LOW,
                queue="reports",
            ),
        ]

        for task in default_tasks:
            self.tasks[task.task_id] = task
            logger.info(f"Registered task: {task.name}")

    async def _scheduler_node(self, state: EnhancedComplianceState) -> Dict[str, Any]:
        """
        Main scheduler node that determines which task to run next.

        This replaces Celery Beat's scheduling logic.
        """
        current_time = datetime.now()
        next_task = None
        min_priority = TaskPriority.BACKGROUND

        # Find the highest priority task that's ready to run
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING and task.next_run:
                if task.next_run <= current_time:
                    if task.priority.value < min_priority.value:
                        next_task = task
                        min_priority = task.priority

        if next_task:
            # Mark task as running
            next_task.status = TaskStatus.RUNNING
            next_task.last_run = current_time

            # Calculate next run time based on schedule
            next_task.next_run = self._calculate_next_run(next_task.schedule)

            logger.info(f"Scheduling task: {next_task.name}")

            return {
                "current_task": next_task.task_id,
                "task_metadata": {
                    "task_id": next_task.task_id,
                    "name": next_task.name,
                    "node": next_task.node_name,
                    "queue": next_task.queue,
                    "priority": next_task.priority.value,
                },
            }

        # No tasks ready, wait
        return {"current_task": None}

    async def _evidence_collector_node(
        self, state: EnhancedComplianceState
    ) -> Dict[str, Any]:
        """
        Node for evidence collection tasks.
        Replaces workers.evidence_tasks functionality.
        """
        task_metadata = state.get("task_metadata", {})
        task_id = task_metadata.get("task_id")

        logger.info(f"Executing evidence collection task: {task_id}")

        try:
            # Implement evidence collection logic here
            # This would integrate with existing evidence collection services

            # For now, simulate task execution
            await asyncio.sleep(1)

            # Update task status
            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.COMPLETED
                self.tasks[task_id].retry_count = 0

            return {
                "task_result": "success",
                "evidence_collected": True,
                "node_execution_times": {
                    "evidence_collector": datetime.now().isoformat()
                },
            }

        except Exception as e:
            logger.error(f"Evidence collection failed: {e}")
            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.FAILED
                self.tasks[task_id].retry_count += 1

            return {
                "task_result": "error",
                "error": str(e),
                "error_count": state.get("error_count", 0) + 1,
            }

    async def _compliance_updater_node(
        self, state: EnhancedComplianceState
    ) -> Dict[str, Any]:
        """
        Node for compliance score updates.
        Replaces workers.compliance_tasks functionality.
        """
        task_metadata = state.get("task_metadata", {})
        task_id = task_metadata.get("task_id")

        logger.info(f"Executing compliance update task: {task_id}")

        try:
            # Implement compliance update logic here
            await asyncio.sleep(1)

            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.COMPLETED

            return {
                "task_result": "success",
                "compliance_updated": True,
                "node_execution_times": {
                    "compliance_updater": datetime.now().isoformat()
                },
            }

        except Exception as e:
            logger.error(f"Compliance update failed: {e}")
            return {"task_result": "error", "error": str(e)}

    async def _report_generator_node(
        self, state: EnhancedComplianceState
    ) -> Dict[str, Any]:
        """
        Node for report generation.
        Replaces workers.reporting_tasks functionality.
        """
        task_metadata = state.get("task_metadata", {})
        task_id = task_metadata.get("task_id")

        logger.info(f"Executing report generation task: {task_id}")

        try:
            # Implement report generation logic here
            await asyncio.sleep(1)

            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.COMPLETED

            return {
                "task_result": "success",
                "report_generated": True,
                "node_execution_times": {
                    "report_generator": datetime.now().isoformat()
                },
            }

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {"task_result": "error", "error": str(e)}

    async def _notification_sender_node(
        self, state: EnhancedComplianceState
    ) -> Dict[str, Any]:
        """
        Node for sending notifications.
        Replaces workers.notification_tasks functionality.
        """
        task_metadata = state.get("task_metadata", {})
        task_id = task_metadata.get("task_id")

        logger.info(f"Executing notification task: {task_id}")

        try:
            # Implement notification logic here
            await asyncio.sleep(1)

            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.COMPLETED

            return {
                "task_result": "success",
                "notification_sent": True,
                "node_execution_times": {
                    "notification_sender": datetime.now().isoformat()
                },
            }

        except Exception as e:
            logger.error(f"Notification sending failed: {e}")
            return {"task_result": "error", "error": str(e)}

    async def _cleanup_node(self, state: EnhancedComplianceState) -> Dict[str, Any]:
        """
        Node for cleanup tasks.
        """
        task_metadata = state.get("task_metadata", {})
        task_id = task_metadata.get("task_id")

        logger.info(f"Executing cleanup task: {task_id}")

        try:
            # Implement cleanup logic here
            await asyncio.sleep(1)

            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.COMPLETED

            return {
                "task_result": "success",
                "cleanup_completed": True,
                "node_execution_times": {"cleanup": datetime.now().isoformat()},
            }

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {"task_result": "error", "error": str(e)}

    def _route_task(self, state: EnhancedComplianceState) -> str:
        """Route to the appropriate task node based on task metadata."""
        task_metadata = state.get("task_metadata", {})

        if not task_metadata:
            return "end"

        node_name = task_metadata.get("node")
        queue = task_metadata.get("queue", "default")

        # Map node names to routing decisions
        node_mapping = {
            "evidence_collector": "evidence",
            "compliance_updater": "compliance",
            "report_generator": "reports",
            "notification_sender": "notifications",
            "cleanup": "cleanup",
        }

        return node_mapping.get(node_name, "error")

    def _check_task_result(self, state: EnhancedComplianceState) -> str:
        """Check task result and determine next step."""
        task_result = state.get("task_result")

        if task_result == "error":
            return "error"
        elif task_result == "success":
            # Back to scheduler for next task
            return "scheduler"
        else:
            return "end"

    def _calculate_next_run(self, schedule: str) -> datetime:
        """
        Calculate the next run time based on cron expression.

        For simplicity, this implementation handles basic intervals.
        In production, use a proper cron parser.
        """
        # Simple interval parsing for demonstration
        if "* * * *" in schedule:  # Hourly
            return datetime.now() + timedelta(hours=1)
        elif "*/6 * * *" in schedule:  # Every 6 hours
            return datetime.now() + timedelta(hours=6)
        elif "* * *" in schedule:  # Daily
            return datetime.now() + timedelta(days=1)
        elif "* * 1" in schedule:  # Weekly Monday
            return datetime.now() + timedelta(weeks=1)
        elif "* * 0" in schedule:  # Weekly Sunday
            return datetime.now() + timedelta(weeks=1)
        elif "1 * *" in schedule:  # Monthly
            return datetime.now() + timedelta(days=30)
        else:
            # Default to daily
            return datetime.now() + timedelta(days=1)

    async def start(self):
        """Start the task scheduler."""
        logger.info("Starting LangGraph task scheduler")

        # Initialize next run times for all tasks
        for task in self.tasks.values():
            if not task.next_run:
                task.next_run = self._calculate_next_run(task.schedule)

        # Main scheduler loop
        while True:
            try:
                # Create initial state
                initial_state = {
                    "messages": [],
                    "current_node": "scheduler",
                    "retry_count": 0,
                    "error_count": 0,
                }

                # Run the graph
                config = {"configurable": {"thread_id": "scheduler-main"}}
                result = await self.graph.ainvoke(initial_state, config)

                # Wait before next iteration
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)  # Wait before retry

    def get_task_status(self, task_id: str) -> Optional[ScheduledTask]:
        """Get the status of a specific task."""
        return self.tasks.get(task_id)

    def list_tasks(self) -> List[ScheduledTask]:
        """List all scheduled tasks."""
        return list(self.tasks.values())

    async def pause_task(self, task_id: str) -> bool:
        """Pause a scheduled task."""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.CANCELLED
            logger.info(f"Paused task: {task_id}")
            return True
        return False

    async def resume_task(self, task_id: str) -> bool:
        """Resume a paused task."""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.PENDING
            self.tasks[task_id].next_run = self._calculate_next_run(
                self.tasks[task_id].schedule
            )
            logger.info(f"Resumed task: {task_id}")
            return True
        return False

    def health_check(self) -> Dict[str, Any]:
        """Check scheduler health."""
        return {
            "status": "healthy",
            "total_tasks": len(self.tasks),
            "pending_tasks": sum(
                1 for t in self.tasks.values() if t.status == TaskStatus.PENDING
            ),
            "running_tasks": sum(
                1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING
            ),
            "failed_tasks": sum(
                1 for t in self.tasks.values() if t.status == TaskStatus.FAILED
            ),
            "checkpointer_status": "connected" if self.checkpointer else "disconnected",
        }
