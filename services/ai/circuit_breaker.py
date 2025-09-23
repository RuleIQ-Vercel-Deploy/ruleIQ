"""
AI Circuit Breaker Pattern Implementation

Provides circuit breaker functionality for AI services to handle failures gracefully
and implement automatic fallback mechanisms with health monitoring.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Callable, Dict, List, Optional

from services.ai.ai_types import CircuitState, FailureRecord


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""

    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 3
    time_window: int = 60
    model_timeouts: Dict[str, float] = field(default_factory=lambda: {})

    def __post_init__(self) -> None:
        """Load model timeouts from central AI configuration."""
        if not self.model_timeouts:
            try:
                from config.ai_config import MODEL_METADATA

                self.model_timeouts = {
                    model_type.value: metadata.timeout_seconds for model_type, metadata in MODEL_METADATA.items()
                }
            except ImportError:
                self.model_timeouts = {
                    "gemini-2.5-pro": 45.0,
                    "gemini-2.5-flash": 30.0,
                    "gemini-2.5-flash-8b": 20.0,
                    "gemma-3-8b-it": 15.0,
                }

    @property
    def timeout_seconds(self) -> int:
        return self.recovery_timeout


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

    @property
    def total_successes(self) -> int:
        return self.successful_requests

    @property
    def total_failures(self) -> int:
        return self.failed_requests

    @property
    def success_rate(self) -> float:
        """Calculate success rate as a ratio of successful to total requests"""
        if self.total_requests > 0:
            return self.successful_requests / self.total_requests
        return 0.0

    def update_failure_rate(self) -> None:
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

    def __init__(self, config: Optional[CircuitBreakerConfig] = None) -> None:
        self.config = config or CircuitBreakerConfig()
        self.logger = logging.getLogger(__name__)
        self._state = CircuitState.CLOSED
        self._last_failure_time: Optional[datetime] = None
        self._consecutive_successes = 0
        self._failures: Dict[str, List[FailureRecord]] = {}
        self._model_states: Dict[str, CircuitState] = {}
        self.metrics = CircuitBreakerMetrics()
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

    def _is_model_available_unlocked(self, model_name: str) -> bool:
        """Check if a specific model is available (circuit not open) - internal method without locking"""
        model_state = self._model_states.get(model_name, CircuitState.CLOSED)
        if model_state == CircuitState.OPEN:
            if self._should_attempt_reset(model_name):
                self._model_states[model_name] = CircuitState.HALF_OPEN
                self.logger.info("Circuit breaker for %s transitioning to half-open" % model_name)
                return True
            return False
        return True

    def is_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available (circuit not open)"""
        with self._lock:
            return self._is_model_available_unlocked(model_name)

    def record_success(self, model_name: str, response_time: float = 0.0) -> None:
        """Record a successful AI operation"""
        with self._lock:
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.update_failure_rate()
            if model_name not in self._model_states:
                self._model_states[model_name] = CircuitState.CLOSED
            model_state = self._model_states.get(model_name, CircuitState.CLOSED)
            if model_state == CircuitState.HALF_OPEN:
                self._consecutive_successes += 1
                if self._consecutive_successes >= self.config.success_threshold:
                    self._model_states[model_name] = CircuitState.CLOSED
                    self._state = CircuitState.CLOSED
                    self._consecutive_successes = 0
                    self.logger.info("Circuit breaker for %s closed after successful recovery" % model_name)
            self.logger.debug("Recorded success for %s (response_time: %ss)" % (model_name, response_time))

    def record_failure(
        self, model_name: str, error: Exception = None, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a failed AI operation"""
        with self._lock:
            now = datetime.now()
            self.metrics.total_requests += 1
            self.metrics.failed_requests += 1
            self.metrics.update_failure_rate()
            failure_record = FailureRecord(
                timestamp=now,
                model_name=model_name,
                error_type=type(error).__name__ if error else "Unknown",
                error_message=str(error) if error else "Unknown error",
                context=context,
            )
            if model_name not in self._failures:
                self._failures[model_name] = []
            self._failures[model_name].append(failure_record)
            self._clean_old_failures(model_name)
            recent_failures = len(self._failures[model_name])
            if recent_failures >= self.config.failure_threshold:
                self._trip_circuit(model_name)
            self.logger.warning(
                "Recorded failure for %s: %s (recent_failures: %s/%s)"
                % (model_name, error if error else "Unknown error", recent_failures, self.config.failure_threshold)
            )

    def _trip_circuit(self, model_name: str) -> None:
        """Trip the circuit breaker for a specific model"""
        self._model_states[model_name] = CircuitState.OPEN
        self._state = CircuitState.OPEN
        self._last_failure_time = datetime.now()
        self._consecutive_successes = 0
        self.metrics.circuit_trips += 1
        self.metrics.last_trip_time = self._last_failure_time
        self.metrics.current_state = CircuitState.OPEN
        self.logger.error("Circuit breaker TRIPPED for model %s" % model_name)

    def _should_attempt_reset(self, model_name: str) -> bool:
        """Check if enough time has passed to attempt circuit reset"""
        if not self._last_failure_time:
            return True
        time_since_failure = datetime.now() - self._last_failure_time
        return time_since_failure.total_seconds() >= self.config.recovery_timeout

    def _clean_old_failures(self, model_name: str) -> None:
        """Remove failures outside the time window"""
        if model_name not in self._failures:
            return
        cutoff_time = datetime.now() - timedelta(seconds=self.config.time_window)
        self._failures[model_name] = [
            failure for failure in self._failures[model_name] if failure.timestamp > cutoff_time
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
                    "available": self.is_model_available(model_name),
                }
            return {
                "overall_state": self._state.value,
                "metrics": {
                    "total_requests": self.metrics.total_requests,
                    "successful_requests": self.metrics.successful_requests,
                    "failed_requests": self.metrics.failed_requests,
                    "failure_rate": self.metrics.failure_rate,
                    "circuit_trips": self.metrics.circuit_trips,
                    "last_trip_time": self.metrics.last_trip_time.isoformat() if self.metrics.last_trip_time else None,
                },
                "models": model_health,
                "config": {
                    "failure_threshold": self.config.failure_threshold,
                    "recovery_timeout": self.config.recovery_timeout,
                    "time_window": self.config.time_window,
                },
            }

    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status (alias for get_health_status for backward compatibility)"""
        with self._lock:
            model_states = {}
            for model_name in self._model_states:
                model_states[model_name] = {
                    "state": self._model_states[model_name].value,
                    "failure_count": len(self._failures.get(model_name, [])),
                    "available": self._is_model_available_unlocked(model_name),
                }
            return {
                "overall_state": self._state.value,
                "model_states": model_states,
                "metrics": {
                    "total_requests": self.metrics.total_requests,
                    "successful_requests": self.metrics.successful_requests,
                    "failed_requests": self.metrics.failed_requests,
                    "failure_rate": self.metrics.failure_rate,
                    "circuit_trips": self.metrics.circuit_trips,
                    "last_trip_time": self.metrics.last_trip_time.isoformat() if self.metrics.last_trip_time else None,
                },
            }

    def _perform_health_check(self, model_name: str) -> bool:
        """
        Perform a health check for a specific model.
        This is a placeholder implementation that can be overridden or mocked in tests.
        """
        return self.is_model_available(model_name)

    def check_model_health(self, model_name: str) -> bool:
        """
        Check the health of a specific model.
        This method can be used by external health monitoring systems.
        """
        return self._perform_health_check(model_name)

    def reset_circuit(self, model_name: Optional[str] = None) -> None:
        """Manually reset circuit breaker (admin function)"""
        with self._lock:
            if model_name:
                self._model_states[model_name] = CircuitState.CLOSED
                if model_name in self._failures:
                    self._failures[model_name] = []
                self.logger.info("Circuit breaker manually reset for %s" % model_name)
            else:
                self._state = CircuitState.CLOSED
                self._model_states.clear()
                self._failures.clear()
                self._consecutive_successes = 0
                self._last_failure_time = None
                self.logger.info("All circuit breakers manually reset")

    def call_with_circuit_breaker(self, model_name: str, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute an operation with circuit breaker protection

        Args:
            model_name: Name of the model for tracking
            operation: The callable to execute
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation

        Returns:
            Result of the operation

        Raises:
            CircuitBreakerException: If circuit is open
            Original exceptions from the operation
        """
        from .exceptions import CircuitBreakerException

        if not self.can_make_request(model_name):
            self.logger.warning("Circuit breaker OPEN for %s - request blocked" % model_name)
            raise CircuitBreakerException(f"Circuit breaker is open for model {model_name}")
        start_time = time.time()
        try:
            result = operation(*args, **kwargs)
            response_time = time.time() - start_time
            self.record_success(model_name, response_time)
            return result
        except Exception as e:
            self.record_failure(model_name, e)
            raise

    def can_make_request(self, model_name: Optional[str] = None) -> bool:
        """
        Check if a request can be made (circuit not open)

        Args:
            model_name: Optional specific model to check

        Returns:
            True if request can proceed, False otherwise
        """
        if model_name:
            return self.is_model_available(model_name)
        return self._state != CircuitState.OPEN or self._should_attempt_reset("global")


class CircuitBreakerManager:
    """Manages multiple circuit breakers for different services"""

    def __init__(self) -> None:
        self._breakers: Dict[str, AICircuitBreaker] = {}
        self._lock = Lock()

    def get_or_create(self, service_name: str, config: Optional[CircuitBreakerConfig] = None) -> AICircuitBreaker:
        """Get or create a circuit breaker for a service"""
        with self._lock:
            if service_name not in self._breakers:
                self._breakers[service_name] = AICircuitBreaker(config)
            return self._breakers[service_name]

    def get_all_statuses(self) -> Dict[str, Any]:
        """Get status of all circuit breakers"""
        with self._lock:
            return {name: breaker.get_health_status() for name, breaker in self._breakers.items()}

    def reset_all(self) -> None:
        """Reset all circuit breakers"""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset_circuit()


_circuit_breaker_manager = CircuitBreakerManager()


def get_circuit_breaker(
    service_name: str = "ai_service", config: Optional[CircuitBreakerConfig] = None
) -> AICircuitBreaker:
    """Get or create a circuit breaker for a service"""
    return _circuit_breaker_manager.get_or_create(service_name, config)
