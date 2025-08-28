"""
Tests for monitoring components.
"""

import pytest
import asyncio
import json
import logging
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.monitoring.logger import (
    setup_logging,
    get_logger,
    StructuredFormatter,
    ColoredFormatter,
    set_request_id,
    clear_request_id,
)
from app.core.monitoring.error_handler import (
    ApplicationError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ExternalServiceError,
    ErrorHandler,
    GlobalErrorHandler,
)
from app.core.monitoring.metrics import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    MetricsCollector,
    track_request,
    track_error,
    track_exception,
    get_metrics,
)
from app.core.monitoring.health import (
    HealthStatus,
    HealthCheckResult,
    HealthCheck,
    DatabaseHealthCheck,
    RedisHealthCheck,
    DiskSpaceHealthCheck,
    MemoryHealthCheck,
    ExternalServiceHealthCheck,
    HealthCheckRegistry,
    run_health_checks,
)
from app.core.monitoring.shutdown import (
    GracefulShutdown,
    ConnectionDrainer,
    get_shutdown_manager,
    get_connection_drainer,
)


class TestLogger:
    """Test logging functionality."""
    
    def test_structured_formatter(self):
        """Test structured JSON formatter."""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        output = formatter.format(record)
        data = json.loads(output)
        
        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["message"] == "Test message"
        assert "timestamp" in data
    
    def test_colored_formatter(self):
        """Test colored console formatter."""
        formatter = ColoredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Error message",
            args=(),
            exc_info=None
        )
        
        output = formatter.format(record)
        assert "ERROR" in output
        assert "Error message" in output
        assert "\033[" in output  # ANSI color code
    
    def test_request_id_context(self):
        """Test request ID context management."""
        request_id = "test-request-123"
        
        set_request_id(request_id)
        logger = get_logger("test")
        
        # Mock handler to capture output
        handler = MagicMock()
        logger.addHandler(handler)
        
        logger.info("Test with request ID")
        
        clear_request_id()
        
        # Verify request ID was in context
        handler.handle.assert_called_once()


class TestErrorHandler:
    """Test error handling functionality."""
    
    def test_application_error(self):
        """Test ApplicationError creation and conversion."""
        error = ApplicationError(
            message="Test error",
            code="TEST_ERROR",
            status_code=500,
            details={"field": "value"}
        )
        
        assert error.message == "Test error"
        assert error.code == "TEST_ERROR"
        assert error.status_code == 500
        assert error.details["field"] == "value"
        
        # Test dictionary conversion
        error_dict = error.to_dict()
        assert error_dict["error"]["code"] == "TEST_ERROR"
        assert error_dict["error"]["message"] == "Test error"
        
        # Test response conversion
        response = error.to_response()
        assert response.status_code == 500
    
    def test_validation_error(self):
        """Test ValidationError with field information."""
        error = ValidationError(
            message="Invalid input",
            field="email"
        )
        
        assert error.status_code == 400
        assert error.code == "VALIDATION_ERROR"
        assert error.details["field"] == "email"
    
    def test_not_found_error(self):
        """Test NotFoundError with resource information."""
        error = NotFoundError(
            resource="User",
            identifier="123"
        )
        
        assert error.status_code == 404
        assert "User not found: 123" in error.message
        assert error.details["resource"] == "User"
        assert error.details["identifier"] == "123"
    
    @pytest.mark.asyncio
    async def test_error_handler(self):
        """Test ErrorHandler with callbacks."""
        handler = ErrorHandler()
        
        # Add context
        handler.add_context(user_id="123", action="test")
        
        # Add callback
        callback_called = False
        def callback(error, context):
            nonlocal callback_called
            callback_called = True
            assert context["user_id"] == "123"
        
        handler.register_callback(callback)
        
        # Handle error
        error = ApplicationError("Test", "TEST", 500)
        response = await handler.handle_error(error)
        
        assert response.status_code == 500
        assert callback_called


class TestMetrics:
    """Test metrics collection functionality."""
    
    def test_counter(self):
        """Test Counter metric."""
        counter = Counter("test_counter", "Test counter")
        
        assert counter.value == 0
        
        counter.increment()
        assert counter.value == 1
        
        counter.increment(5)
        assert counter.value == 6
        
        counter.reset()
        assert counter.value == 0
        
        # Test negative increment should raise error
        with pytest.raises(ValueError):
            counter.increment(-1)
    
    def test_gauge(self):
        """Test Gauge metric."""
        gauge = Gauge("test_gauge", "Test gauge")
        
        gauge.set(10)
        assert gauge.value == 10
        
        gauge.increment(5)
        assert gauge.value == 15
        
        gauge.decrement(3)
        assert gauge.value == 12
    
    def test_histogram(self):
        """Test Histogram metric."""
        histogram = Histogram(
            "test_histogram",
            "Test histogram",
            buckets=[1, 5, 10]
        )
        
        histogram.observe(0.5)
        histogram.observe(3)
        histogram.observe(7)
        histogram.observe(15)
        
        assert histogram.count == 4
        assert histogram.sum == 25.5
        assert histogram.bucket_counts[1] == 1  # 0.5 <= 1
        assert histogram.bucket_counts[5] == 2  # 0.5, 3 <= 5
        assert histogram.bucket_counts[10] == 3  # 0.5, 3, 7 <= 10
        assert histogram.bucket_counts[float('inf')] == 4  # All values
        
        # Test percentiles
        p50 = histogram.get_percentile(50)
        assert p50 is not None
    
    def test_summary(self):
        """Test Summary metric with time window."""
        summary = Summary(
            "test_summary",
            "Test summary",
            window_size=1  # 1 second window
        )
        
        summary.observe(10)
        summary.observe(20)
        summary.observe(30)
        
        assert summary.count == 3
        assert summary.sum == 60
        
        # Test window expiration
        import time
        time.sleep(1.1)
        summary.observe(40)  # This will clear old values
        
        assert summary.count == 1
        assert summary.sum == 40
    
    def test_metrics_collector(self):
        """Test MetricsCollector."""
        collector = MetricsCollector()
        
        # Test registration
        counter = collector.register_counter("test_counter", "Test")
        assert counter is not None
        
        # Test retrieval
        same_counter = collector.get_metric("test_counter")
        assert same_counter is counter
        
        # Test with labels
        labeled_counter = collector.register_counter(
            "labeled_counter",
            "Test",
            {"env": "test"}
        )
        assert labeled_counter.labels["env"] == "test"
    
    def test_track_request(self):
        """Test request tracking."""
        track_request(
            method="GET",
            path="/api/test",
            status_code=200,
            duration=0.5
        )
        
        metrics = get_metrics()
        assert "metrics" in metrics
        assert len(metrics["metrics"]) > 0


class TestHealthChecks:
    """Test health check functionality."""
    
    @pytest.mark.asyncio
    async def test_health_check_result(self):
        """Test HealthCheckResult."""
        result = HealthCheckResult(
            name="test",
            status=HealthStatus.HEALTHY,
            message="Test is healthy",
            details={"version": "1.0"},
            duration_ms=10.5
        )
        
        assert result.name == "test"
        assert result.status == HealthStatus.HEALTHY
        assert result.details["version"] == "1.0"
        assert result.duration_ms == 10.5
        
        # Test dictionary conversion
        result_dict = result.to_dict()
        assert result_dict["name"] == "test"
        assert result_dict["status"] == HealthStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_database_health_check(self):
        """Test DatabaseHealthCheck."""
        # Mock session factory
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=MagicMock(scalar=MagicMock(return_value=1)))
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        session_factory = MagicMock(return_value=mock_session)
        
        check = DatabaseHealthCheck(session_factory)
        result = await check.check()
        
        assert result.status == HealthStatus.HEALTHY
        assert "successful" in result.message
    
    @pytest.mark.asyncio
    async def test_disk_space_health_check(self):
        """Test DiskSpaceHealthCheck."""
        check = DiskSpaceHealthCheck(
            path="/",
            warning_threshold=80.0,
            critical_threshold=90.0
        )
        
        result = await check.check()
        
        # Result depends on actual disk usage
        assert result.status in [
            HealthStatus.HEALTHY,
            HealthStatus.DEGRADED,
            HealthStatus.UNHEALTHY
        ]
        assert "percent_used" in result.details
    
    @pytest.mark.asyncio
    async def test_memory_health_check(self):
        """Test MemoryHealthCheck."""
        check = MemoryHealthCheck(
            warning_threshold=80.0,
            critical_threshold=90.0
        )
        
        result = await check.check()
        
        assert result.status in [
            HealthStatus.HEALTHY,
            HealthStatus.DEGRADED,
            HealthStatus.UNHEALTHY
        ]
        assert "percent_used" in result.details
    
    @pytest.mark.asyncio
    async def test_health_check_registry(self):
        """Test HealthCheckRegistry."""
        registry = HealthCheckRegistry()
        
        # Create mock check
        mock_check = Mock(spec=HealthCheck)
        mock_check.name = "test_check"
        mock_check.critical = False
        mock_check.check = AsyncMock(
            return_value=HealthCheckResult(
                name="test_check",
                status=HealthStatus.HEALTHY,
                message="OK"
            )
        )
        
        # Register check
        registry.register(mock_check)
        assert len(registry.checks) == 1
        
        # Run checks
        results = await registry.run_checks(use_cache=False)
        assert len(results) == 1
        assert results[0].status == HealthStatus.HEALTHY
        
        # Test overall status
        overall = registry.get_overall_status(results)
        assert overall == HealthStatus.HEALTHY


class TestShutdown:
    """Test graceful shutdown functionality."""
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown(self):
        """Test GracefulShutdown."""
        shutdown = GracefulShutdown(timeout=1.0)
        
        # Add cleanup callback
        cleanup_called = False
        async def cleanup():
            nonlocal cleanup_called
            cleanup_called = True
        
        shutdown.add_cleanup(cleanup)
        
        # Register task
        task = asyncio.create_task(asyncio.sleep(0.1))
        shutdown.register_task(task)
        
        # Trigger shutdown
        await shutdown.shutdown()
        
        assert cleanup_called
        assert shutdown._shutdown_initiated
        assert task.cancelled()
    
    @pytest.mark.asyncio
    async def test_connection_drainer(self):
        """Test ConnectionDrainer."""
        drainer = ConnectionDrainer(drain_timeout=0.5)
        
        assert drainer.active_connections == 0
        
        # Simulate connection
        async with drainer:
            assert drainer.active_connections == 1
        
        assert drainer.active_connections == 0
        
        # Test draining
        async with drainer:
            # Start drain
            drain_task = asyncio.create_task(drainer.drain())
            await asyncio.sleep(0.1)
            
        # Drain should complete
        await drain_task
        assert drainer.active_connections == 0


class TestMonitoringIntegration:
    """Test monitoring integration with FastAPI."""
    
    def test_monitoring_endpoints(self):
        """Test monitoring API endpoints."""
        from app.api.monitoring import router, setup_health_checks
        
        app = FastAPI()
        app.include_router(router)
        
        # Setup health checks
        setup_health_checks()
        
        client = TestClient(app)
        
        # Test liveness
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        
        # Test metrics endpoint
        response = client.get("/metrics/json")
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_monitoring_middleware(self):
        """Test monitoring middleware stack."""
        from app.core.monitoring.middleware import (
            RequestIDMiddleware,
            LoggingMiddleware,
            MetricsMiddleware,
            PerformanceMiddleware,
            SecurityHeadersMiddleware,
        )
        
        app = FastAPI()
        
        # Add middleware
        app.add_middleware(SecurityHeadersMiddleware)
        app.add_middleware(PerformanceMiddleware, slow_request_threshold=0.1)
        app.add_middleware(MetricsMiddleware)
        app.add_middleware(LoggingMiddleware)
        app.add_middleware(RequestIDMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}
        
        client = TestClient(app)
        
        # Make request
        response = client.get("/test")
        assert response.status_code == 200
        
        # Check headers
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers
        assert "X-Content-Type-Options" in response.headers