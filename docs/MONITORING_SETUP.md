# RuleIQ Monitoring and Observability Setup

## Overview

RuleIQ implements a comprehensive monitoring and observability solution that includes:

- **Sentry Integration** - Error tracking and performance monitoring
- **Custom Metrics** - Business KPIs and performance metrics
- **Health Checks** - Component health monitoring
- **Alerting System** - Multi-channel alert notifications
- **Prometheus Metrics** - Standard metrics export
- **Real-time Dashboard** - Monitoring dashboard API

## Components

### 1. Sentry Error Tracking

Sentry provides real-time error tracking and performance monitoring.

#### Configuration

Set the following environment variables:

```bash
# Required
SENTRY_DSN=your-sentry-dsn-here

# Optional (defaults shown)
ENABLE_SENTRY=true
ENABLE_PERFORMANCE_MONITORING=true
TRACES_SAMPLE_RATE=0.1  # 10% of transactions
PROFILES_SAMPLE_RATE=0.1  # 10% profiling
```

#### Features

- Automatic error capture with context
- Performance transaction tracking
- Custom breadcrumbs for debugging
- User context tracking
- Environment-based configuration
- Intelligent sampling based on endpoints

### 2. Metrics Collection

The metrics system tracks both business and technical metrics.

#### Business Metrics

- Total users (active daily/weekly/monthly)
- Assessment counts and trends
- Average compliance scores
- Policy generation statistics
- AI usage and costs
- Evidence document tracking

#### Performance Metrics

- Response time percentiles (p50, p95, p99)
- Request throughput (requests/second)
- Error rates by endpoint
- Cache hit/miss ratios
- Database query performance

#### System Metrics

- CPU usage
- Memory utilization
- Disk usage
- Network statistics
- Database connection pools

### 3. Health Check System

Comprehensive health monitoring for all system components.

#### Monitored Components

- **PostgreSQL Database** - Connection, pool utilization, query performance
- **Redis Cache** - Connectivity, memory usage, performance
- **Filesystem** - Disk space, directory access
- **Google AI API** - Availability, response times
- **External APIs** - Google OAuth, Stripe, etc.
- **Background Tasks** - Task health and execution

#### Health Status Levels

- `healthy` - Component operating normally
- `degraded` - Component experiencing issues but functional
- `unhealthy` - Component is failing
- `unknown` - Unable to determine status

### 4. Alert Management

Intelligent alerting with multiple notification channels.

#### Alert Channels

- **Sentry** - Critical errors and issues
- **Email** - Important notifications (requires configuration)
- **Webhook** - Custom integrations
- **Slack** - Team notifications (optional)
- **In-App** - Dashboard alerts
- **Log** - Application logs

#### Alert Rules

The system includes pre-configured alert rules for:

- Database connection pool saturation (>85% warning, >95% critical)
- Slow database queries (>1000ms)
- High API response times (p95 >2s warning, p99 >5s critical)
- Error rate thresholds (>5% warning, >10% critical)
- Memory usage (>85% warning, >95% critical)
- Disk usage (>80% warning, >90% critical)
- Security events (failed logins, suspicious activity)
- Business metrics (low compliance scores, high AI costs)

#### Alert Configuration

```python
# Example: Custom alert rule
AlertRule(
    name="custom_metric_threshold",
    condition="business.custom_metric > threshold",
    threshold=100.0,
    duration=60,  # Seconds condition must be true
    severity=AlertSeverity.MEDIUM,
    category=AlertCategory.BUSINESS,
    channels=[AlertChannel.EMAIL, AlertChannel.IN_APP],
    cooldown=300  # Seconds before re-alerting
)
```

### 5. API Endpoints

#### Public Endpoints (No Authentication)

- `GET /api/v1/monitoring/health` - Quick health check
- `GET /api/v1/monitoring/metrics/prometheus` - Prometheus metrics export

#### Authenticated Endpoints

- `GET /api/v1/monitoring/status` - Monitoring system status
- `GET /api/v1/monitoring/metrics/business` - Business KPIs
- `GET /api/v1/monitoring/metrics/performance` - Performance metrics
- `GET /api/v1/monitoring/metrics/summary` - Comprehensive metrics
- `GET /api/v1/monitoring/health/detailed` - Detailed health check
- `GET /api/v1/monitoring/alerts` - Active alerts
- `POST /api/v1/monitoring/alerts/{id}/resolve` - Resolve alert
- `GET /api/v1/monitoring/database/status` - Database monitoring
- `GET /api/v1/monitoring/dashboard` - Dashboard data

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Key dependencies:
- `sentry-sdk[fastapi]` - Sentry integration
- `prometheus-client` - Prometheus metrics
- `psutil` - System metrics
- `aiohttp` - Webhook notifications

### 2. Configure Environment

Create or update your `.env` file:

```bash
# Sentry Configuration
SENTRY_DSN=https://your-key@sentry.io/project-id
ENABLE_SENTRY=true

# Alert Notifications (optional)
ALERT_WEBHOOK_URL=https://your-webhook-endpoint
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Monitoring Thresholds
DISK_WARNING_THRESHOLD=80.0
DISK_CRITICAL_THRESHOLD=90.0
MEMORY_WARNING_THRESHOLD=85.0
MEMORY_CRITICAL_THRESHOLD=95.0
```

### 3. Initialize Monitoring

The monitoring system initializes automatically on application startup. To manually initialize:

```python
from monitoring.startup import initialize_monitoring_system

# In your FastAPI lifespan context
monitoring_state = await initialize_monitoring_system()
```

### 4. Integrate with Application

Update your `main.py`:

```python
from monitoring.startup import initialize_monitoring_system, shutdown_monitoring_system

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize monitoring
    monitoring_state = await initialize_monitoring_system()
    app.state.monitoring = monitoring_state
    
    yield
    
    # Shutdown monitoring
    await shutdown_monitoring_system(monitoring_state)
```

## Usage Examples

### Recording Custom Metrics

```python
from monitoring import get_metrics_collector

collector = get_metrics_collector()

# Record a request
collector.record_request(
    method="POST",
    endpoint="/api/v1/assessments",
    status_code=200,
    response_time=0.145,
    user_id="user123"
)

# Record AI usage
collector.record_ai_request(
    model="gemini-1.5-flash",
    endpoint="/api/v1/chat",
    response_time=2.3,
    cost=0.002,
    tokens_used=450
)
```

### Creating Alerts

```python
from monitoring import get_alert_manager, AlertSeverity, AlertCategory, AlertChannel

manager = get_alert_manager()

alert = manager.create_alert(
    title="High API Usage",
    message="API usage exceeds normal patterns",
    severity=AlertSeverity.MEDIUM,
    category=AlertCategory.BUSINESS,
    component="api",
    metadata={"requests_per_minute": 1500},
    channels=[AlertChannel.EMAIL, AlertChannel.IN_APP]
)
```

### Health Checks

```python
from monitoring import get_health_checker

checker = get_health_checker()

# Run comprehensive health check
system_health = await checker.check_all_components()
print(f"System status: {system_health.status}")

# Check specific component
db_health = await checker.check_database_health(db_session)
print(f"Database status: {db_health.status}")
```

## Monitoring Dashboard

Access the monitoring dashboard through the API:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/monitoring/dashboard
```

Response includes:
- Current health status
- Active alerts summary
- Business metrics
- Performance metrics
- Database status
- Environment information

## Prometheus Integration

Configure Prometheus to scrape metrics:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'ruleiq'
    scrape_interval: 30s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/monitoring/metrics/prometheus'
```

## Alert Webhook Format

Webhooks receive POST requests with the following format:

```json
{
  "alert": {
    "id": "database_capacity_1234567890",
    "title": "Database Connection Pool High",
    "message": "Pool utilization is 87%, threshold is 85%",
    "severity": "high",
    "category": "capacity",
    "component": "database",
    "timestamp": "2024-01-15T10:30:00Z",
    "metadata": {
      "pool_utilization": 87,
      "threshold": 85
    }
  },
  "environment": "production",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Troubleshooting

### Sentry Not Capturing Events

1. Verify `SENTRY_DSN` is set correctly
2. Check `ENABLE_SENTRY=true` in environment
3. Ensure network connectivity to Sentry
4. Check Sentry project settings and quotas

### Metrics Not Updating

1. Verify background tasks are running
2. Check database connectivity
3. Review logs for metric collection errors
4. Ensure sufficient permissions for system metrics

### Alerts Not Firing

1. Check alert rule thresholds
2. Verify alert channels are configured
3. Review cooldown periods
4. Check condition duration requirements

### High Memory Usage

1. Review metric history retention settings
2. Adjust `max_history_size` in collectors
3. Check for memory leaks in custom metrics
4. Monitor background task resource usage

## Best Practices

1. **Set Appropriate Thresholds** - Tune alert thresholds based on your system's normal behavior
2. **Use Sampling** - Adjust Sentry sampling rates for cost optimization
3. **Regular Health Checks** - Monitor the `/health` endpoint with external monitoring
4. **Alert Fatigue** - Configure cooldowns to prevent alert spam
5. **Metric Retention** - Balance history size with memory usage
6. **Security** - Protect monitoring endpoints with authentication
7. **Documentation** - Document custom metrics and alert rules
8. **Testing** - Test alert channels regularly using test alerts

## Performance Impact

The monitoring system is designed for minimal performance impact:

- Metrics collection: <1% CPU overhead
- Health checks: Async, non-blocking
- Alert evaluation: 30-second intervals
- Sentry: Configurable sampling rates
- Background tasks: Separate async loops

## Support

For monitoring issues or questions:

1. Check application logs for monitoring errors
2. Review Sentry dashboard for captured issues
3. Verify configuration in settings
4. Test individual components using API endpoints