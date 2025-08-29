"""
Complete integrated graph for LangGraph compliance system.
Connects ALL nodes from ALL phases with proper routing and error handling.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional
from uuid import uuid4

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg
from psycopg.rows import dict_row
from langchain_core.messages import HumanMessage, AIMessage

from langgraph_agent.graph.unified_state import UnifiedComplianceState, create_unified_initial_state
from langgraph_agent.graph.integrated_error_handler import IntegratedErrorHandler
from langgraph_agent.nodes.evidence_nodes import evidence_collection_node
from langgraph_agent.nodes.compliance_nodes import compliance_check_node
from langgraph_agent.nodes.notification_nodes import notification_node
from langgraph_agent.nodes.reporting_nodes import reporting_node
from langgraph_agent.nodes.rag_node import rag_query_node
from langgraph_agent.nodes.state_validator import state_validator_node
from langgraph_agent.nodes.task_scheduler_node import task_scheduler_node

logger = logging.getLogger(__name__)


async def setup_postgresql_checkpointer() -> PostgresSaver:
    """
    Properly set up PostgreSQL checkpointer with async initialization.
    
    Returns:
        Configured PostgresSaver instance
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Handle different URL formats
    if "asyncpg" in DATABASE_URL:
        # Convert asyncpg URL to psycopg format
        DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    logger.info("Initializing PostgreSQL checkpointer")
    
    try:
        # Create connection with proper settings
        conn = psycopg.connect(
            DATABASE_URL,
            autocommit=True,
            row_factory=dict_row
        )
        
        # Create checkpointer
        checkpointer = PostgresSaver(conn)
        
        # Properly await setup in async context
        await checkpointer.setup()
        
        logger.info("PostgreSQL checkpointer initialized successfully")
        
        return checkpointer
        
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL checkpointer: {e}")
        raise


def build_integrated_graph(checkpointer: Optional[PostgresSaver] = None):
    """
    Build complete integrated graph with ALL nodes from ALL phases.
    
    Args:
        checkpointer: Optional pre-configured checkpointer
        
    Returns:
        Compiled graph ready for execution
    """
    logger.info("Building integrated compliance graph")
    
    # Create graph with unified state
    graph = StateGraph(UnifiedComplianceState)
    
    # Initialize error handler for node wrapping
    error_handler = IntegratedErrorHandler()
    
    # Wrap all nodes with error handling
    wrapped_state_validator = error_handler.wrap_node(state_validator_node)
    wrapped_rag_query = error_handler.wrap_node(rag_query_node)
    wrapped_evidence_collection = error_handler.wrap_node(evidence_collection_node)
    wrapped_compliance_check = error_handler.wrap_node(compliance_check_node)
    wrapped_notification = error_handler.wrap_node(notification_node)
    wrapped_reporting = error_handler.wrap_node(reporting_node)
    wrapped_task_scheduler = error_handler.wrap_node(task_scheduler_node)
    
    # Add ALL nodes from ALL phases
    graph.add_node("state_validator", wrapped_state_validator)
    graph.add_node("error_handler", error_handler_node)
    graph.add_node("rag_query", wrapped_rag_query)
    graph.add_node("evidence_collection", wrapped_evidence_collection)
    graph.add_node("compliance_check", wrapped_compliance_check)
    graph.add_node("notification", wrapped_notification)
    graph.add_node("reporting", wrapped_reporting)
    graph.add_node("task_scheduler", wrapped_task_scheduler)
    
    # Set entry point
    graph.set_entry_point("state_validator")
    
    # Define routing functions
    def route_after_validation(state: UnifiedComplianceState) -> str:
        """Route based on workflow state after validation."""
        
        # Check for errors first
        if state.get("error_count", 0) > 0 and not state.get("should_continue", True):
            return "error_handler"
        
        # Route based on task type
        task_type = state.get("task_type", "compliance_check")
        
        routing_map = {
            "evidence_collection": "evidence_collection",
            "compliance_check": "rag_query",  # Query first, then check
            "notification": "notification",
            "reporting": "reporting",
            "scheduled_task": "task_scheduler"
        }
        
        next_node = routing_map.get(task_type, "compliance_check")
        logger.info(f"Routing from validation to {next_node} for task type {task_type}")
        
        return next_node
    
    def route_after_error(state: UnifiedComplianceState) -> str:
        """Route after error handling."""
        
        if state.get("should_continue", False):
            # Continue from where we left off
            current_step = state.get("current_step", "state_validator")
            logger.info(f"Retrying from step: {current_step}")
            return current_step
        else:
            # Workflow failed, end
            logger.info("Workflow failed after error handling, ending")
            return END
    
    def route_after_compliance(state: UnifiedComplianceState) -> str:
        """Route after compliance check."""
        
        # Check if notification is required
        if state.get("metadata", {}).get("notify_required", False):
            return "notification"
        else:
            return "reporting"
    
    def route_after_evidence(state: UnifiedComplianceState) -> str:
        """Route after evidence collection."""
        
        # Evidence should lead to compliance check
        if state.get("relevant_documents"):
            return "rag_query"  # Query compliance rules with evidence context
        else:
            return "compliance_check"
    
    # Add conditional edges with proper routing
    graph.add_conditional_edges(
        "state_validator",
        route_after_validation,
        {
            "error_handler": "error_handler",
            "evidence_collection": "evidence_collection",
            "rag_query": "rag_query",
            "compliance_check": "compliance_check",
            "notification": "notification",
            "reporting": "reporting",
            "task_scheduler": "task_scheduler"
        }
    )
    
    # Error handler routing
    graph.add_conditional_edges(
        "error_handler",
        route_after_error,
        {
            "state_validator": "state_validator",
            "evidence_collection": "evidence_collection",
            "rag_query": "rag_query",
            "compliance_check": "compliance_check",
            "notification": "notification",
            "reporting": "reporting",
            "task_scheduler": "task_scheduler",
            END: END
        }
    )
    
    # Evidence collection routing
    graph.add_conditional_edges(
        "evidence_collection",
        route_after_evidence,
        {
            "rag_query": "rag_query",
            "compliance_check": "compliance_check"
        }
    )
    
    # RAG to compliance check
    graph.add_edge("rag_query", "compliance_check")
    
    # Compliance check routing
    graph.add_conditional_edges(
        "compliance_check",
        route_after_compliance,
        {
            "notification": "notification",
            "reporting": "reporting"
        }
    )
    
    # Notification to reporting
    graph.add_edge("notification", "reporting")
    
    # Reporting to end
    graph.add_edge("reporting", END)
    
    # Task scheduler can trigger any workflow
    graph.add_edge("task_scheduler", "state_validator")
    
    # Compile with checkpointing if available
    if checkpointer:
        logger.info("Compiling graph with PostgreSQL checkpointing")
        compiled_graph = graph.compile(
            checkpointer=checkpointer,
            interrupt_before=["human_review"],  # Pause for human input
            interrupt_after=["critical_decision"]  # Pause after important steps
        )
    else:
        logger.warning("Compiling graph without checkpointing")
        compiled_graph = graph.compile()
    
    logger.info("Graph compilation complete")
    
    return compiled_graph


async def error_handler_node(state: UnifiedComplianceState) -> UnifiedComplianceState:
    """
    Global error handler node for the graph.
    Implements retry logic and workflow status management.
    """
    # Increment retry count
    state["retry_count"] = state.get("retry_count", 0) + 1
    max_retries = state.get("max_retries", 3)
    
    logger.info(f"Error handler: attempt {state['retry_count']}/{max_retries}")
    
    if state["retry_count"] <= max_retries:
        # Calculate exponential backoff
        wait_time = min(2 ** (state["retry_count"] - 1), 30)
        await asyncio.sleep(wait_time)
        
        # Update for retry
        state["workflow_status"] = "RETRYING"
        state["should_continue"] = True
        
        # Add to history
        state["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "error_retry",
            "retry_count": state["retry_count"],
            "wait_time": wait_time
        })
        
    else:
        # Max retries exceeded
        state["workflow_status"] = "FAILED"
        state["should_continue"] = False
        
        state["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "workflow_failed",
            "reason": "max_retries_exceeded"
        })
    
    return state


async def create_and_initialize_graph():
    """
    Create and initialize the complete graph with proper async setup.
    
    Returns:
        Fully initialized and compiled graph
    """
    # Set up checkpointer properly
    checkpointer = await setup_postgresql_checkpointer()
    
    # Build graph with checkpointer
    graph = build_integrated_graph(checkpointer)
    
    return graph


# For synchronous contexts that need the graph
def get_graph_sync():
    """
    Get a compiled graph in synchronous context.
    Note: This won't have checkpointing enabled.
    """
    return build_integrated_graph(checkpointer=None)