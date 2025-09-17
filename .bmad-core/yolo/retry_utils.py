#!/usr/bin/env python3
"""
Retry utilities for BMad YOLO System
Provides exponential backoff retry logic and circuit breaker patterns.
"""
import asyncio
import logging
from functools import wraps
from typing import TypeVar, Callable, Optional, Dict, Any
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class RetryMetrics:
    """Metrics for retry operations."""
    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    retry_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    circuit_state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0

    def record_success(self):
        """Record a successful attempt."""
        self.total_attempts += 1
        self.successful_attempts += 1
        self.last_success_time = datetime.now(timezone.utc)
        self.consecutive_failures = 0
        if self.circuit_state == CircuitState.HALF_OPEN:
            self.circuit_state = CircuitState.CLOSED
            logger.info("Circuit breaker closed - recovery successful")

    def record_failure(self):
        """Record a failed attempt."""
        self.total_attempts += 1
        self.failed_attempts += 1
        self.last_failure_time = datetime.now(timezone.utc)
        self.consecutive_failures += 1

    def record_retry(self):
        """Record a retry attempt."""
        self.retry_count += 1

    def should_open_circuit(self, threshold: int = 5) -> bool:
        """Check if circuit should open based on consecutive failures."""
        if self.consecutive_failures >= threshold:
            if self.circuit_state != CircuitState.OPEN:
                self.circuit_state = CircuitState.OPEN
                logger.warning(f"Circuit breaker opened after {self.consecutive_failures} failures")
            return True
        return False

    def can_attempt(self, cooldown_seconds: int = 60) -> bool:
        """Check if we can attempt based on circuit state."""
        if self.circuit_state == CircuitState.CLOSED:
            return True

        if self.circuit_state == CircuitState.OPEN:
            if self.last_failure_time:
                elapsed = (datetime.now(timezone.utc) - self.last_failure_time).total_seconds()
                if elapsed > cooldown_seconds:
                    self.circuit_state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker half-open - testing recovery")
                    return True
            return False

        # HALF_OPEN - allow one attempt
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get retry statistics."""
        success_rate = 0.0
        if self.total_attempts > 0:
            success_rate = self.successful_attempts / self.total_attempts

        return {
            "total_attempts": self.total_attempts,
            "successful_attempts": self.successful_attempts,
            "failed_attempts": self.failed_attempts,
            "retry_count": self.retry_count,
            "success_rate": success_rate,
            "circuit_state": self.circuit_state.value,
            "consecutive_failures": self.consecutive_failures,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_success": self.last_success_time.isoformat() if self.last_success_time else None
        }


# Global metrics storage
_retry_metrics: Dict[str, RetryMetrics] = {}


def get_retry_metrics(func_name: str) -> RetryMetrics:
    """Get or create retry metrics for a function."""
    if func_name not in _retry_metrics:
        _retry_metrics[func_name] = RetryMetrics()
    return _retry_metrics[func_name]


def async_retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    max_backoff: float = 60.0,
    retriable_exceptions: tuple = (Exception,),
    circuit_breaker: bool = True,
    circuit_threshold: int = 5,
    circuit_cooldown: int = 60
):
    """
    Decorator for async functions with exponential backoff retry and circuit breaker.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
        max_backoff: Maximum backoff time in seconds
        retriable_exceptions: Tuple of exceptions to retry on
        circuit_breaker: Enable circuit breaker pattern
        circuit_threshold: Consecutive failures before opening circuit
        circuit_cooldown: Seconds to wait before attempting recovery
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            metrics = get_retry_metrics(func_name)

            # Check circuit breaker
            if circuit_breaker:
                if not metrics.can_attempt(circuit_cooldown):
                    error_msg = f"Circuit breaker OPEN for {func_name}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)

            last_exception = None

            for attempt in range(max_attempts):
                try:
                    # Log attempt
                    if attempt > 0:
                        logger.info(f"Retry attempt {attempt + 1}/{max_attempts} for {func_name}")
                        metrics.record_retry()

                    # Call the function
                    result = await func(*args, **kwargs)

                    # Record success
                    metrics.record_success()

                    if attempt > 0:
                        logger.info(f"Retry successful for {func_name} on attempt {attempt + 1}")

                    return result

                except retriable_exceptions as e:
                    last_exception = e
                    metrics.record_failure()

                    # Check if we should retry
                    if attempt < max_attempts - 1:
                        # Calculate backoff time
                        wait_time = min(backoff_factor ** attempt, max_backoff)

                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func_name}: {e}. "
                            f"Retrying in {wait_time:.1f}s..."
                        )

                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func_name}. "
                            f"Last error: {e}"
                        )

                        # Check circuit breaker
                        if circuit_breaker:
                            metrics.should_open_circuit(circuit_threshold)

                except Exception as e:
                    # Non-retriable exception
                    logger.error(f"Non-retriable exception in {func_name}: {e}")
                    metrics.record_failure()
                    if circuit_breaker:
                        metrics.should_open_circuit(circuit_threshold)
                    raise

            # All retries exhausted
            if last_exception:
                raise last_exception

        # Add metrics access method
        wrapper.get_metrics = lambda: get_retry_metrics(f"{func.__module__}.{func.__name__}")

        return wrapper
    return decorator


def sync_retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    max_backoff: float = 60.0,
    retriable_exceptions: tuple = (Exception,)
):
    """
    Decorator for sync functions with exponential backoff retry.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
        max_backoff: Maximum backoff time in seconds
        retriable_exceptions: Tuple of exceptions to retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time

            func_name = f"{func.__module__}.{func.__name__}"
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    if attempt > 0:
                        logger.info(f"Retry attempt {attempt + 1}/{max_attempts} for {func_name}")

                    result = func(*args, **kwargs)

                    if attempt > 0:
                        logger.info(f"Retry successful for {func_name} on attempt {attempt + 1}")

                    return result

                except retriable_exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        wait_time = min(backoff_factor ** attempt, max_backoff)
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func_name}: {e}. "
                            f"Retrying in {wait_time:.1f}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func_name}")

            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def get_all_retry_metrics() -> Dict[str, Dict[str, Any]]:
    """Get all retry metrics for monitoring."""
    return {
        func_name: metrics.get_stats()
        for func_name, metrics in _retry_metrics.items()
    }


def reset_retry_metrics(func_name: Optional[str] = None):
    """Reset retry metrics for a specific function or all functions."""
    if func_name:
        if func_name in _retry_metrics:
            _retry_metrics[func_name] = RetryMetrics()
            logger.info(f"Reset retry metrics for {func_name}")
    else:
        _retry_metrics.clear()
        logger.info("Reset all retry metrics")


# Example usage
if __name__ == "__main__":
    # Example async function with retry
    @async_retry(max_attempts=3, backoff_factor=2.0)
    async def example_async_function():
        """Example function that might fail."""
        import random
        if random.random() < 0.7:  # 70% chance of failure
            raise ConnectionError("Simulated connection error")
        return "Success!"

    # Run example
    async def main():
        try:
            result = await example_async_function()
            print(f"Result: {result}")
        except Exception as e:
            print(f"Failed: {e}")

        # Print metrics
        metrics = example_async_function.get_metrics()
        print(f"Metrics: {metrics.get_stats()}")

    asyncio.run(main())
