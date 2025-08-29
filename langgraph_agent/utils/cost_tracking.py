"""
Cost tracking decorator and utilities for LangGraph nodes.

This module provides decorators and utilities to track AI costs
across all LangGraph nodes, integrating with the existing cost
management infrastructure.
"""

import asyncio
import functools
import time
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from datetime import datetime
import logging

from services.ai.cost_management import AICostManager, AIUsageMetrics

logger = logging.getLogger(__name__)

# Type variable for decorated functions
F = TypeVar('F', bound=Callable[..., Any])

# Global cost manager instance
_cost_manager: Optional[AICostManager] = None


def get_cost_manager() -> AICostManager:
    """Get or create the global cost manager instance."""
    global _cost_manager
    if _cost_manager is None:
        _cost_manager = AICostManager()
    return _cost_manager


def track_node_cost(
    node_name: Optional[str] = None,
    service_name: str = "langgraph",
    model_name: Optional[str] = None,
    track_tokens: bool = True
) -> Callable[[F], F]:
    """
    Decorator to track costs for LangGraph nodes.
    
    Args:
        node_name: Name of the node (defaults to function name)
        service_name: Service identifier for cost tracking
        model_name: AI model being used (if applicable)
        track_tokens: Whether to track token usage
        
    Returns:
        Decorated function that tracks costs
        
    Example:
        @track_node_cost(node_name="compliance_check", model_name="gpt-4")
        async def compliance_check_node(state: AgentState) -> AgentState:
            # Node implementation
            pass
    """
    def decorator(func: F) -> F:
        # Determine if function is async
        is_async = asyncio.iscoroutinefunction(func)
        
        # Get node name from parameter or function name
        actual_node_name = node_name or func.__name__
        
        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                cost_manager = get_cost_manager()
                
                # Extract state if available
                state = None
                if args and hasattr(args[0], '__dict__'):
                    state = args[0]
                
                # Initialize metrics
                input_tokens = 0
                output_tokens = 0
                total_cost = 0.0
                
                try:
                    # Get user ID from state if available
                    user_id = None
                    if state and hasattr(state, 'user_id'):
                        user_id = state.user_id
                    elif state and hasattr(state, 'get'):
                        user_id = state.get('user_id')
                    
                    # Execute the node function
                    result = await func(*args, **kwargs)
                    
                    # Extract token counts from result if available
                    if isinstance(result, dict):
                        if 'usage' in result:
                            usage = result['usage']
                            if isinstance(usage, dict):
                                input_tokens = usage.get('input_tokens', 0)
                                output_tokens = usage.get('output_tokens', 0)
                        
                        # Also check for token counts in state updates
                        if 'input_tokens' in result:
                            input_tokens = result['input_tokens']
                        if 'output_tokens' in result:
                            output_tokens = result['output_tokens']
                        if 'total_cost' in result:
                            total_cost = result['total_cost']
                    
                    # Calculate execution time
                    execution_time = time.time() - start_time
                    
                    # Track the usage
                    if track_tokens and (input_tokens > 0 or output_tokens > 0):
                        await cost_manager.track_ai_request(
                            model=model_name or "unknown",
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            user_id=user_id or "system",
                            service_name=f"{service_name}.{actual_node_name}",
                            metadata={
                                "node_name": actual_node_name,
                                "execution_time": execution_time,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        )
                        
                        logger.info(
                            f"Cost tracked for {actual_node_name}: "
                            f"input_tokens={input_tokens}, "
                            f"output_tokens={output_tokens}, "
                            f"cost=${total_cost:.4f}, "
                            f"execution_time={execution_time:.2f}s"
                        )
                    
                    # Add cost info to result if it's a dict
                    if isinstance(result, dict) and not result.get('cost_tracking'):
                        result['cost_tracking'] = {
                            'node_name': actual_node_name,
                            'input_tokens': input_tokens,
                            'output_tokens': output_tokens,
                            'total_cost': total_cost,
                            'execution_time': execution_time
                        }
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Error in cost tracking for {actual_node_name}: {e}")
                    # Re-raise the original exception
                    raise
                    
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                cost_manager = get_cost_manager()
                
                # Extract state if available
                state = None
                if args and hasattr(args[0], '__dict__'):
                    state = args[0]
                
                # Initialize metrics
                input_tokens = 0
                output_tokens = 0
                total_cost = 0.0
                
                try:
                    # Get user ID from state if available
                    user_id = None
                    if state and hasattr(state, 'user_id'):
                        user_id = state.user_id
                    elif state and hasattr(state, 'get'):
                        user_id = state.get('user_id')
                    
                    # Execute the node function
                    result = func(*args, **kwargs)
                    
                    # Extract token counts from result if available
                    if isinstance(result, dict):
                        if 'usage' in result:
                            usage = result['usage']
                            if isinstance(usage, dict):
                                input_tokens = usage.get('input_tokens', 0)
                                output_tokens = usage.get('output_tokens', 0)
                        
                        # Also check for token counts in state updates
                        if 'input_tokens' in result:
                            input_tokens = result['input_tokens']
                        if 'output_tokens' in result:
                            output_tokens = result['output_tokens']
                        if 'total_cost' in result:
                            total_cost = result['total_cost']
                    
                    # Calculate execution time
                    execution_time = time.time() - start_time
                    
                    # Track the usage synchronously (run in thread if needed)
                    if track_tokens and (input_tokens > 0 or output_tokens > 0):
                        # For sync functions, we'll track without await
                        asyncio.create_task(
                            cost_manager.track_ai_request(
                                model=model_name or "unknown",
                                input_tokens=input_tokens,
                                output_tokens=output_tokens,
                                user_id=user_id or "system",
                                service_name=f"{service_name}.{actual_node_name}",
                                metadata={
                                    "node_name": actual_node_name,
                                    "execution_time": execution_time,
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                            )
                        )
                        
                        logger.info(
                            f"Cost tracked for {actual_node_name}: "
                            f"input_tokens={input_tokens}, "
                            f"output_tokens={output_tokens}, "
                            f"cost=${total_cost:.4f}, "
                            f"execution_time={execution_time:.2f}s"
                        )
                    
                    # Add cost info to result if it's a dict
                    if isinstance(result, dict) and not result.get('cost_tracking'):
                        result['cost_tracking'] = {
                            'node_name': actual_node_name,
                            'input_tokens': input_tokens,
                            'output_tokens': output_tokens,
                            'total_cost': total_cost,
                            'execution_time': execution_time
                        }
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Error in cost tracking for {actual_node_name}: {e}")
                    # Re-raise the original exception
                    raise
                    
            return sync_wrapper
    
    return decorator


def aggregate_node_costs(state: Dict[str, Any]) -> Dict[str, float]:
    """
    Aggregate cost tracking information from multiple nodes in the state.
    
    Args:
        state: The LangGraph state dictionary
        
    Returns:
        Dictionary with aggregated cost metrics
    """
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0.0
    total_execution_time = 0.0
    node_costs = {}
    
    # Look for cost tracking in state
    if 'cost_tracking' in state:
        tracking = state['cost_tracking']
        if isinstance(tracking, dict):
            total_input_tokens += tracking.get('input_tokens', 0)
            total_output_tokens += tracking.get('output_tokens', 0)
            total_cost += tracking.get('total_cost', 0.0)
            total_execution_time += tracking.get('execution_time', 0.0)
            
            node_name = tracking.get('node_name', 'unknown')
            node_costs[node_name] = tracking.get('total_cost', 0.0)
    
    # Look for accumulated costs
    if 'accumulated_costs' in state:
        for node_name, cost in state['accumulated_costs'].items():
            node_costs[node_name] = cost
            total_cost += cost
    
    return {
        'total_input_tokens': total_input_tokens,
        'total_output_tokens': total_output_tokens,
        'total_cost': total_cost,
        'total_execution_time': total_execution_time,
        'node_costs': node_costs
    }


class CostTrackingContext:
    """
    Context manager for tracking costs across multiple operations.
    
    Example:
        with CostTrackingContext("workflow_name") as tracker:
            # Perform operations
            result = await some_ai_operation()
            tracker.add_tokens(100, 50)  # input, output
            
        total_cost = tracker.total_cost
    """
    
    def __init__(self, context_name: str, user_id: Optional[str] = None):
        self.context_name = context_name
        self.user_id = user_id or "system"
        self.cost_manager = get_cost_manager()
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_cost = 0.0
        self.start_time = None
        self.operations = []
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        
        # Log aggregated costs
        logger.info(
            f"Cost tracking context '{self.context_name}' completed: "
            f"input_tokens={self.input_tokens}, "
            f"output_tokens={self.output_tokens}, "
            f"total_cost=${self.total_cost:.4f}, "
            f"execution_time={execution_time:.2f}s"
        )
        
    def add_tokens(self, input_tokens: int, output_tokens: int, cost: Optional[float] = None):
        """Add token counts to the context."""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        if cost:
            self.total_cost += cost
            
    def add_operation(self, operation_name: str, metrics: Dict[str, Any]):
        """Track an individual operation within the context."""
        self.operations.append({
            'name': operation_name,
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': metrics
        })