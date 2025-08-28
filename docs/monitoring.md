# Monitoring & Observability Guide

## Overview

The ruleIQ platform includes comprehensive monitoring and observability features to ensure system reliability, performance tracking, and efficient debugging. This guide covers the monitoring infrastructure, configuration options, and best practices.

## Architecture

### Core Components

1. **Structured Logging** (`app.core.monitoring.logger`)
   - JSON-formatted logs for production
   - Request ID tracking across all log entries
   - Context-aware logging with automatic metadata injection
   - Log level management per environment

2. **Error Handling** (`app.core.monitoring.error_handler`)
   - Custom exception hierarchy
   - Automatic error response formatting
   - Sentry integration for error tracking
   - Request context preservation in error logs

3. **Metrics Collection** (`app.core.monitoring.metrics`)
   - Prometheus-compatible metrics
   - Counter, Gauge, Histogram, and Summary types
   - Business and technical metrics tracking
   - System resource monitoring (CPU, memory, disk)

4. **Health Checks** (`app.core.monitoring.health`)
   - Database connectivity checks
   - Redis availability monitoring
   - Disk space and memory usage checks
   - External service health verification
   - Configurable check intervals and thresholds

5. **Middleware Stack** (`app.core.monitoring.middleware`)
   - Request ID tracking
   - Request/response logging
   - Performance monitoring
   - Metrics collection
   - Security headers injection

6. **Sentry Integration** (`app.core.monitoring.sentry_integration`)
   - Error and exception tracking
   - Performance monitoring
   - Release tracking
   - User context preservation
   - Sensitive data sanitization

## Configuration

### Environment Variables

```bash
# Sentry Configuration
SENTRY_DSN=https://your-key@sentry.io/project-id
ENVIRONMENT=production  # or development, staging

# Monitoring Flags
ENABLE_SENTRY=true
ENABLE_METRICS=true
ENABLE_HEALTH_CHECKS=true

# Performance Thresholds
SLOW_REQUEST_THRESHOLD=1.0  # seconds

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json  # or text for development
```

### Application Setup

The monitoring system is automatically configured when the application starts:

```python
from app.core.monitoring.setup import configure_from_settings

# In your FastAPI app initialization
app = FastAPI()
configure_from_settings(app)
```

This single call sets up:
- All middleware components
- Error handlers
- Health check endpoints
- Metrics collection
- Sentry integration
- Graceful shutdown handling

## API Endpoints

### Health Checks

#### Main Health Check
```http
GET /api/monitoring/health
```

Returns comprehensive health status:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00Z",
  "checks": [
    {
      "name": "database",
      "status": "healthy",
      "message": "Database connection successful",
      "duration_ms": 5.2
    },
    {
      "name": "redis",
      "status": "healthy",
      "message": "Redis connection successful",
      "duration_ms": 2.1
    }
  ]
}
```

#### Liveness Probe
```http
GET /api/monitoring/liveness
```
Minimal check for container orchestration (returns 200 if alive).

#### Readiness Probe
```http
GET /api/monitoring/readiness
```
Checks if the application is ready to handle requests.

### Metrics

#### Prometheus Metrics
```http
GET /api/monitoring/metrics
```

Returns metrics in Prometheus format:
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/api/users",status="200"} 1234

# HELP http_request_duration_seconds HTTP request duration
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 950
```

## Monitoring Patterns

### Request Tracking

Every request is assigned a unique ID for tracing:

```python
from app.core.monitoring.logger import get_logger

logger = get_logger(__name__)

# Request ID is automatically included in logs
logger.info("Processing user request", user_id=user_id)
# Output: {"timestamp": "...", "request_id": "uuid", "message": "Processing user request", "user_id": 123}
```

### Custom Metrics

Add business-specific metrics:

```python
from app.core.monitoring.metrics import get_metrics_collector

collector = get_metrics_collector()

# Track compliance checks
counter = collector.register_counter(
    "compliance_checks_total",
    "Total compliance checks performed",
    labels={"type": "SOC2"}
)
counter.increment()

# Track processing time
with collector.timer("compliance_check_duration_seconds"):
    # Perform compliance check
    pass
```

### Error Context

Provide context for errors:

```python
from app.core.monitoring.error_handler import ApplicationError

# Raise with context
raise ApplicationError(
    message="Failed to process compliance check",
    code="COMPLIANCE_CHECK_FAILED",
    details={
        "check_id": check_id,
        "framework": "SOC2",
        "error": str(e)
    }
)
```

### Health Check Registration

Add custom health checks:

```python
from app.core.monitoring.health import HealthCheck, HealthCheckResult, HealthStatus
from app.core.monitoring.health import register_health_check

class CustomServiceHealthCheck(HealthCheck):
    async def check(self) -> HealthCheckResult:
        try:
            # Check your service
            if service_is_healthy():
                return HealthCheckResult(
                    name="custom_service",
                    status=HealthStatus.HEALTHY,
                    message="Service is operational"
                )
        except Exception as e:
            return HealthCheckResult(
                name="custom_service",
                status=HealthStatus.UNHEALTHY,
                message=f"Service check failed: {str(e)}"
            )

# Register during app startup
register_health_check(CustomServiceHealthCheck())
```

## Performance Monitoring

### Slow Request Detection

Requests exceeding the configured threshold are automatically logged:

```
WARNING: Slow request detected: GET /api/compliance/check
Duration: 2.5s (threshold: 1.0s)
Memory delta: 15MB
```

### Database Query Monitoring

Track database performance:

```python
from app.core.monitoring.metrics import get_metrics_collector

collector = get_metrics_collector()

async with collector.async_timer("database_query_duration_seconds", labels={"query": "get_user"}):
    result = await db.execute(query)
```

## Sentry Integration

### Error Tracking

Errors are automatically sent to Sentry with context:

```python
from app.core.monitoring.sentry_integration import capture_exception, set_user_context

# Set user context for better debugging
set_user_context(
    user_id=str(user.id),
    username=user.username,
    email=user.email
)

# Capture exceptions with additional context
try:
    # Some operation
    pass
except Exception as e:
    capture_exception(
        e,
        compliance_framework="SOC2",
        check_id=check_id
    )
```

### Performance Monitoring

Track transaction performance:

```python
from app.core.monitoring.sentry_integration import sentry_transaction

with sentry_transaction("compliance", "check_compliance"):
    # Perform compliance check
    pass
```

## Graceful Shutdown

The application handles shutdown gracefully:

```python
from app.core.monitoring.shutdown import get_shutdown_manager

manager = get_shutdown_manager()

# Register cleanup callbacks
async def cleanup_connections():
    await db.close()
    await redis.close()

manager.register_cleanup_callback(cleanup_connections)

# During shutdown:
# 1. Stop accepting new requests
# 2. Wait for active requests to complete (with timeout)
# 3. Execute cleanup callbacks
# 4. Exit cleanly
```

## Dashboards and Alerting

### Recommended Setup

1. **Prometheus + Grafana**
   - Scrape `/api/monitoring/metrics` endpoint
   - Use provided Grafana dashboards (see `monitoring/grafana/`)
   - Configure alerts for critical metrics

2. **Sentry Alerts**
   - Error rate thresholds
   - New error types
   - Performance degradation
   - Release tracking

3. **Health Check Monitoring**
   - Configure uptime monitoring for `/api/monitoring/health`
   - Set up alerts for degraded or unhealthy status
   - Monitor individual component health

### Key Metrics to Monitor

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `http_requests_failed_total` | Failed HTTP requests | > 1% of total requests |
| `http_request_duration_seconds` | Request latency | p99 > 2 seconds |
| `compliance_check_duration_seconds` | Compliance check time | p95 > 5 seconds |
| `memory_usage_bytes` | Memory consumption | > 80% of available |
| `cpu_usage_percent` | CPU utilization | > 70% sustained |
| `database_connection_pool_exhausted` | DB pool exhaustion | Any occurrence |
| `errors_total` | Application errors | Rate increase > 50% |

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Check `/api/monitoring/metrics` for memory trends
   - Review slow query logs in Sentry
   - Analyze memory profiling data

2. **Slow Requests**
   - Check performance traces in Sentry
   - Review slow request logs
   - Analyze database query performance

3. **Health Check Failures**
   - Check specific component status in `/api/monitoring/health`
   - Review error logs for failed components
   - Verify external service connectivity

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
LOG_LEVEL=DEBUG LOG_FORMAT=text python main.py
```

This provides:
- Detailed request/response logging
- SQL query logging
- Middleware execution timing
- Detailed error stack traces

## Best Practices

1. **Structured Logging**
   - Always use the provided logger
   - Include relevant context in log messages
   - Use appropriate log levels

2. **Metric Naming**
   - Follow Prometheus naming conventions
   - Use consistent labels
   - Avoid high-cardinality labels

3. **Error Handling**
   - Use custom exception classes
   - Provide meaningful error messages
   - Include debugging context

4. **Performance**
   - Set appropriate health check intervals
   - Use metric sampling for high-volume endpoints
   - Implement circuit breakers for external services

5. **Security**
   - Never log sensitive data (passwords, tokens)
   - Sanitize error messages for external responses
   - Use Sentry's PII scrubbing features

## Testing

Run monitoring tests:

```bash
# Run all monitoring tests
pytest tests/test_monitoring.py -v

# Test specific component
pytest tests/test_monitoring.py::TestHealthChecks -v

# Test with coverage
pytest tests/test_monitoring.py --cov=app.core.monitoring
```

## Migration Guide

If migrating from another monitoring solution:

1. **Update Configuration**
   - Set environment variables
   - Update `settings.py` if needed

2. **Replace Logging**
   ```python
   # Old
   import logging
   logger = logging.getLogger(__name__)
   
   # New
   from app.core.monitoring.logger import get_logger
   logger = get_logger(__name__)
   ```

3. **Update Error Handling**
   ```python
   # Old
   raise ValueError("Invalid input")
   
   # New
   from app.core.monitoring.error_handler import ValidationError
   raise ValidationError("Invalid input", field="email")
   ```

4. **Add Metrics**
   ```python
   from app.core.monitoring.metrics import track_request, track_performance
   
   # Track API requests
   track_request(method="GET", path="/api/users", status_code=200, duration=0.05)
   
   # Track operations
   track_performance("database_query", duration=0.02, success=True)
   ```

## Support

For monitoring-related issues:
1. Check this documentation
2. Review error logs in Sentry
3. Check system metrics in Grafana
4. Contact the DevOps team

## Appendix

### Environment-Specific Configuration

#### Development
```yaml
log_level: DEBUG
log_format: text
enable_sentry: false
enable_metrics: true
slow_request_threshold: 2.0
```

#### Staging
```yaml
log_level: INFO
log_format: json
enable_sentry: true
enable_metrics: true
slow_request_threshold: 1.5
```

#### Production
```yaml
log_level: WARNING
log_format: json
enable_sentry: true
enable_metrics: true
slow_request_threshold: 1.0
```

### Monitoring Checklist

- [ ] Sentry DSN configured
- [ ] Log level appropriate for environment
- [ ] Health checks passing
- [ ] Metrics endpoint accessible
- [ ] Graceful shutdown tested
- [ ] Alert rules configured
- [ ] Dashboards set up
- [ ] Runbook documented
- [ ] Team trained on monitoring tools