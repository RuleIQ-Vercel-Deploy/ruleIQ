"""Cost tracking middleware for API requests.

This module provides middleware to track costs associated with API requests,
including AI service usage, database operations, and external API calls.
"""
from __future__ import annotations

import time
import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from decimal import Decimal
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message
from config.logging_config import get_logger
from config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class CostTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track costs associated with API requests."""
    
    def __init__(
        self,
        app,
        enable_tracking: bool = True,
        track_ai_costs: bool = True,
        track_db_costs: bool = False,
        cost_calculator: Optional[Callable] = None
    ):
        """
        Initialize cost tracking middleware.
        
        Args:
            app: The FastAPI application
            enable_tracking: Whether to enable cost tracking
            track_ai_costs: Track AI service costs
            track_db_costs: Track database operation costs
            cost_calculator: Custom cost calculation function
        """
        super().__init__(app)
        self.enable_tracking = enable_tracking
        self.track_ai_costs = track_ai_costs
        self.track_db_costs = track_db_costs
        self.cost_calculator = cost_calculator or self._default_cost_calculator
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and track associated costs.
        
        Args:
            request: The incoming request
            call_next: Next middleware in chain
            
        Returns:
            Response with cost tracking headers if enabled
        """
        if not self.enable_tracking:
            return await call_next(request)
        
        # Initialize cost tracking context
        request.state.cost_tracking = {
            "start_time": time.time(),
            "ai_costs": Decimal("0"),
            "db_costs": Decimal("0"),
            "api_costs": Decimal("0"),
            "total_cost": Decimal("0"),
            "cost_items": []
        }
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate total cost
            if hasattr(request.state, "cost_tracking"):
                cost_data = request.state.cost_tracking
                cost_data["end_time"] = time.time()
                cost_data["duration_ms"] = (cost_data["end_time"] - cost_data["start_time"]) * 1000
                
                # Calculate total
                cost_data["total_cost"] = (
                    cost_data["ai_costs"] +
                    cost_data["db_costs"] +
                    cost_data["api_costs"]
                )
                
                # Add cost headers if enabled
                if settings.include_cost_headers:
                    response.headers["X-Request-Cost"] = str(cost_data["total_cost"])
                    response.headers["X-Request-Duration-MS"] = str(int(cost_data["duration_ms"]))
                
                # Log cost data
                if cost_data["total_cost"] > 0:
                    logger.info(
                        f"Request cost tracking - Path: {request.url.path}, "
                        f"Total Cost: ${cost_data['total_cost']}, "
                        f"Duration: {cost_data['duration_ms']:.2f}ms"
                    )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in cost tracking middleware: {e}")
            return await call_next(request)
    
    def _default_cost_calculator(self, operation_type: str, metadata: Dict[str, Any]) -> Decimal:
        """
        Default cost calculation function.
        
        Args:
            operation_type: Type of operation (ai, db, api)
            metadata: Operation metadata
            
        Returns:
            Calculated cost in USD
        """
        if operation_type == "ai":
            # Example AI cost calculation
            input_tokens = metadata.get("input_tokens", 0)
            output_tokens = metadata.get("output_tokens", 0)
            model = metadata.get("model", "gpt-3.5-turbo")
            
            # Simplified pricing (actual prices would be fetched from config)
            costs = {
                "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
                "gpt-4": {"input": 0.03, "output": 0.06},
                "claude-2": {"input": 0.008, "output": 0.024}
            }
            
            model_costs = costs.get(model, costs["gpt-3.5-turbo"])
            cost = Decimal(str(
                (input_tokens * model_costs["input"] / 1000) +
                (output_tokens * model_costs["output"] / 1000)
            ))
            return cost
        
        elif operation_type == "db":
            # Example database cost calculation
            read_units = metadata.get("read_units", 0)
            write_units = metadata.get("write_units", 0)
            
            # Simplified pricing
            cost = Decimal(str(
                (read_units * 0.00001) +  # $0.01 per 1000 read units
                (write_units * 0.00005)    # $0.05 per 1000 write units
            ))
            return cost
        
        elif operation_type == "api":
            # Example external API cost calculation
            api_name = metadata.get("api_name", "unknown")
            calls = metadata.get("calls", 1)
            
            # Simplified pricing
            api_costs = {
                "google_maps": 0.005,
                "sendgrid": 0.001,
                "twilio": 0.01
            }
            
            cost_per_call = api_costs.get(api_name, 0.001)
            cost = Decimal(str(calls * cost_per_call))
            return cost
        
        return Decimal("0")


def track_cost(
    request: Request,
    operation_type: str,
    metadata: Dict[str, Any],
    cost: Optional[Decimal] = None
) -> None:
    """
    Track cost for an operation within a request.
    
    Args:
        request: The current request
        operation_type: Type of operation (ai, db, api)
        metadata: Operation metadata
        cost: Optional pre-calculated cost
    """
    if not hasattr(request.state, "cost_tracking"):
        return
    
    tracking = request.state.cost_tracking
    
    # Calculate cost if not provided
    if cost is None and hasattr(request.app.state, "cost_tracking_middleware"):
        middleware = request.app.state.cost_tracking_middleware
        cost = middleware.cost_calculator(operation_type, metadata)
    
    if cost is None:
        cost = Decimal("0")
    
    # Update appropriate cost category
    if operation_type == "ai":
        tracking["ai_costs"] += cost
    elif operation_type == "db":
        tracking["db_costs"] += cost
    elif operation_type == "api":
        tracking["api_costs"] += cost
    
    # Add to cost items list
    tracking["cost_items"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "type": operation_type,
        "cost": str(cost),
        "metadata": metadata
    })


async def get_request_cost_summary(request: Request) -> Dict[str, Any]:
    """
    Get cost summary for the current request.
    
    Args:
        request: The current request
        
    Returns:
        Dictionary with cost breakdown
    """
    if not hasattr(request.state, "cost_tracking"):
        return {
            "tracking_enabled": False,
            "total_cost": "0",
            "breakdown": {}
        }
    
    tracking = request.state.cost_tracking
    
    return {
        "tracking_enabled": True,
        "total_cost": str(tracking["total_cost"]),
        "breakdown": {
            "ai_costs": str(tracking["ai_costs"]),
            "db_costs": str(tracking["db_costs"]),
            "api_costs": str(tracking["api_costs"])
        },
        "duration_ms": tracking.get("duration_ms", 0),
        "item_count": len(tracking["cost_items"])
    }


__all__ = [
    "CostTrackingMiddleware",
    "track_cost",
    "get_request_cost_summary"
]