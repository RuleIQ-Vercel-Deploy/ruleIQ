"""
AI Circuit Breaker Pattern Implementation

Provides circuit breaker functionality for AI services to handle failures gracefully
and implement automatic fallback mechanisms with health monitoring.
"""

import time
import logging
from enum import Enum
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock

# Import shared types to prevent circular dependencies
from services.ai.ai_types import CircuitState, FailureRecord


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""
    failure_threshold: int = 5  # Number of failures before opening circuit
    recovery_timeout: int = 60  # Seconds before transitioning to half-open
    success_threshold: int = 3  # Successful calls needed to close circuit in half-open
    time_window: int = 60      # Time window for failure counting (seconds)
    
    # Model-specific timeouts (seconds)
    model_timeouts: Dict[str, float] = field(default_factory=lambda: {
        "gemini-2.5-pro-001": 45.0,
        "gemini-2.5-flash-001": 30.0,
        "gemini-2.5-flash-8b": 20.0,
        "gemma-3-8b-it": 15.0
    })


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    circuit_trips: int = 0
    last_trip_time: Optional[datetime] = None
    current_state: CircuitState = CircuitState.CLOSED
    failure_rate: float = 0.0
    
    def update_failure_rate(self):
        """Update the failure rate based on current metrics"""
        if self.total_requests > 0:
            self.failure_rate = self.failed_requests / self.total_requests
        else:
            self.failure_rate = 0.0


class AICircuitBreaker:
    """
    Circuit breaker for AI services with model-specific failure tracking
    and automatic fallback capabilities.
    """
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        self.config = config or CircuitBreakerConfig()
        self.logger = logging.getLogger(__name__)
        
        # Circuit state management
        self._state = CircuitState.CLOSED
        self._last_failure_time: Optional[datetime] = None
        self._consecutive_successes = 0
        
        # Failure tracking per model
        self._failures: Dict[str, List[FailureRecord]] = {}
        self._model_states: Dict[str, CircuitState] = {}
        
        # Metrics tracking
        self.metrics = CircuitBreakerMetrics()
        
        # Thread safety
        self._lock = Lock()
        
    @property
    def state(self) -> CircuitState:
        """Get current circuit state"""
        return self._state
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)"""
        return self._state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open (failing fast)"""
        return self._state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing recovery)"""
        return self._state == CircuitState.HALF_OPEN
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available (circuit not open)"""
        with self._lock:
            model_state = self._model_states.get(model_name, CircuitState.CLOSED)
            
            if model_state == CircuitState.OPEN:
                # Check if enough time has passed to transition to half-open
                if self._should_attempt_reset(model_name):
                    self._model_states[model_name] = CircuitState.HALF_OPEN
                    self.logger.info(f"Circuit breaker for {model_name} transitioning to half-open")
                    return True
                return False
            
            return True
    
    def record_success(self, model_name: str, response_time: float = 0.0):
        """Record a successful AI operation"""
        with self._lock:
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.update_failure_rate()
            
            model_state = self._model_states.get(model_name, CircuitState.CLOSED)
            
            if model_state == CircuitState.HALF_OPEN:
                self._consecutive_successes += 1
                if self._consecutive_successes >= self.config.success_threshold:
                    # Circuit recovered, close it
                    self._model_states[model_name] = CircuitState.CLOSED
                    self._state = CircuitState.CLOSED
                    self._consecutive_successes = 0
                    self.logger.info(f"Circuit breaker for {model_name} closed after successful recovery")
            
            self.logger.debug(f"Recorded success for {model_name} (response_time: {response_time:.2f}s)")
    
    def record_failure(self, model_name: str, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Record a failed AI operation"""
        with self._lock:
            now = datetime.now()
            
            # Update metrics
            self.metrics.total_requests += 1
            self.metrics.failed_requests += 1
            self.metrics.update_failure_rate()
            
            # Create failure record
            failure_record = FailureRecord(
                timestamp=now,
                model_name=model_name,
                error_type=type(error).__name__,
                error_message=str(error),
                context=context
            )
            
            # Add to model-specific failures
            if model_name not in self._failures:
                self._failures[model_name] = []
            
            self._failures[model_name].append(failure_record)
            
            # Clean old failures outside time window
            self._clean_old_failures(model_name)
            
            # Check if we should trip the circuit
            recent_failures = len(self._failures[model_name])
            if recent_failures >= self.config.failure_threshold:
                self._trip_circuit(model_name)
            
            self.logger.warning(
                f"Recorded failure for {model_name}: {error} "
                f"(recent_failures: {recent_failures}/{self.config.failure_threshold})"
            )
    
    def _trip_circuit(self, model_name: str):
        """Trip the circuit breaker for a specific model"""
        self._model_states[model_name] = CircuitState.OPEN
        self._state = CircuitState.OPEN
        self._last_failure_time = datetime.now()
        self._consecutive_successes = 0
        
        # Update metrics
        self.metrics.circuit_trips += 1
        self.metrics.last_trip_time = self._last_failure_time
        self.metrics.current_state = CircuitState.OPEN
        
        self.logger.error(f"Circuit breaker TRIPPED for model {model_name}")
    
    def _should_attempt_reset(self, model_name: str) -> bool:
        """Check if enough time has passed to attempt circuit reset"""
        if not self._last_failure_time:
            return True
        
        time_since_failure = datetime.now() - self._last_failure_time
        return time_since_failure.total_seconds() >= self.config.recovery_timeout
    
    def _clean_old_failures(self, model_name: str):
        """Remove failures outside the time window"""
        if model_name not in self._failures:
            return
        
        cutoff_time = datetime.now() - timedelta(seconds=self.config.time_window)
        self._failures[model_name] = [
            failure for failure in self._failures[model_name]
            if failure.timestamp > cutoff_time
        ]
    
    def get_failure_count(self, model_name: str) -> int:
        """Get current failure count for a model within time window"""
        with self._lock:
            self._clean_old_failures(model_name)
            return len(self._failures.get(model_name, []))
    
    def get_model_state(self, model_name: str) -> CircuitState:
        """Get circuit state for a specific model"""
        return self._model_states.get(model_name, CircuitState.CLOSED)
    
    def get_available_models(self, model_list: List[str]) -> List[str]:
        """Get list of available models (circuits not open)"""
        available = []
        for model in model_list:
            if self.is_model_available(model):
                available.append(model)
        return available
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        with self._lock:
            model_health = {}
            for model_name in self._model_states:
                model_health[model_name] = {
                    "state": self._model_states[model_name].value,
                    "failure_count": self.get_failure_count(model_name),
                    "available": self.is_model_available(model_name)
                }
            
            return {
                "overall_state": self._state.value,
                "metrics": {
                    "total_requests": self.metrics.total_requests,
                    "successful_requests": self.metrics.successful_requests,
                    "failed_requests": self.metrics.failed_requests,
                    "failure_rate": self.metrics.failure_rate,
                    "circuit_trips": self.metrics.circuit_trips,
                    "last_trip_time": self.metrics.last_trip_time.isoformat() if self.metrics.last_trip_time else None
                },
                "models": model_health,
                "config": {
                    "failure_threshold": self.config.failure_threshold,
                    "recovery_timeout": self.config.recovery_timeout,
                    "time_window": self.config.time_window
                }
            }
    
    def reset_circuit(self, model_name: Optional[str] = None):
        """Manually reset circuit breaker (admin function)"""
        with self._lock:
            if model_name:
                # Reset specific model
                self._model_states[model_name] = CircuitState.CLOSED
                if model_name in self._failures:
                    self._failures[model_name] = []
                self.logger.info(f"Circuit breaker manually reset for {model_name}")
            else:
                # Reset all circuits
                self._state = CircuitState.CLOSED
                self._model_states.clear()
                self._failures.clear()
                self._consecutive_successes = 0
                self._last_failure_time = None
                self.logger.info("All circuit breakers manually reset")
    
    def call_with_circuit_breaker(
        self, 
        model_name: str, 
        operation: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """
        Execute a synchronous operation with circuit breaker protection
        
        Args:
            model_name: Name of the AI model being used
            operation: Synchronous function to execute
            *args, **kwargs: Arguments for the operation
            
        Returns:
            Result of the operation
            
        Raises:
            AIServiceException: If circuit is open or operation fails
        """
        if not self.is_model_available(model_name):
            from services.ai.exceptions import AIServiceException
            raise AIServiceException(
                message=f"Circuit breaker is OPEN for model {model_name}",
                service_name="AI Circuit Breaker",
                error_code="CIRCUIT_OPEN",
                context={"model_name": model_name, "state": self.get_model_state(model_name).value}
            )
        
        start_time = time.time()
        try:
            result = operation(*args, **kwargs)
            response_time = time.time() - start_time
            self.record_success(model_name, response_time)
            return result
            
        except Exception as error:
            self.record_failure(model_name, error, {"operation": operation.__name__})
            raise
    
    async def async_call_with_circuit_breaker(
        self, 
        model_name: str, 
        operation: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """
        Execute an asynchronous operation with circuit breaker protection
        
        Args:
            model_name: Name of the AI model being used
            operation: Asynchronous function to execute
            *args, **kwargs: Arguments for the operation
            
        Returns:
            Result of the operation
            
        Raises:
            AIServiceException: If circuit is open or operation fails
        """
        if not self.is_model_available(model_name):
            from services.ai.exceptions import AIServiceException
            raise AIServiceException(
                message=f"Circuit breaker is OPEN for model {model_name}",
                service_name="AI Circuit Breaker",
                error_code="CIRCUIT_OPEN",
                context={"model_name": model_name, "state": self.get_model_state(model_name).value}
            )
        
        start_time = time.time()
        try:
            result = await operation(*args, **kwargs)
            response_time = time.time() - start_time
            self.record_success(model_name, response_time)
            return result
            
        except Exception as error:
            self.record_failure(model_name, error, {"operation": operation.__name__})
            raise


# Global circuit breaker instance
_circuit_breaker: Optional[AICircuitBreaker] = None


def get_circuit_breaker() -> AICircuitBreaker:
    """Get global circuit breaker instance"""
    global _circuit_breaker
    if _circuit_breaker is None:
        _circuit_breaker = AICircuitBreaker()
    return _circuit_breaker


def reset_circuit_breaker():
    """Reset global circuit breaker (for testing)"""
    global _circuit_breaker
    _circuit_breaker = None