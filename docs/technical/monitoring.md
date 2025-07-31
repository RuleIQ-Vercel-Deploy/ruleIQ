# System Monitoring Setup

## Overview

ruleIQ includes comprehensive monitoring capabilities for database health, API performance, AI service usage, and system metrics. This guide covers monitoring setup, configuration, and best practices.

## Monitoring Components

### 1. Health Check Endpoints

**Basic Health Check (Public):**
```bash
curl http://localhost:8000/health
```

**Comprehensive System Status (Authenticated):**
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/monitoring/database
```

### 2. Database Monitoring

**Connection Pool Metrics:**
- Active/idle connections
- Pool utilization percentage
- Connection errors and timeouts
- Query performance statistics

**Health Indicators:**
- Response time monitoring
- Slow query detection
- Connection availability
- Resource utilization

### 3. API Performance Monitoring

**Metrics Tracked:**
- Request/response times
- Error rates by endpoint
- Rate limiting statistics
- Authentication success rates

**Endpoints:**
```bash
# Performance overview
GET /api/monitoring/status

# Detailed metrics
GET /api/monitoring/prometheus
```

### 4. AI Service Monitoring

**Circuit Breaker Status:**
- Service availability
- Failure rates
- Recovery time
- Fallback usage

**Cost Tracking:**
- Token usage by service
- Daily/monthly spending
- Budget alerts
- Optimization recommendations

## Setup Instructions

### 1. Enable Monitoring Services

**Environment Configuration:**
```bash
# Enable monitoring features
ENABLE_MONITORING=true
ENABLE_PROMETHEUS=true
MONITORING_INTERVAL=30

# Database monitoring
DB_MONITORING_ENABLED=true
DB_SLOW_QUERY_THRESHOLD=100  # milliseconds

# AI monitoring
AI_COST_TRACKING=true
AI_CIRCUIT_BREAKER=true
```

### 2. Prometheus Integration

**Install Prometheus:**
```bash
# Using Docker
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

**Configuration (prometheus.yml):**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ruleiq-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/monitoring/prometheus'
    scrape_interval: 15s
    bearer_token: 'your_monitoring_token'
```

### 3. Grafana Dashboard

**Install Grafana:**
```bash
# Using Docker
docker run -d \
  --name grafana \
  -p 3001:3000 \
  grafana/grafana
```

**Dashboard Configuration:**
- Add Prometheus as data source
- Import ruleIQ dashboard templates
- Configure alerts and notifications

### 4. Alert Manager Setup

**Alert Rules:**
```yaml
groups:
  - name: ruleiq_alerts
    rules:
      - alert: DatabaseHighConnections
        expr: database_connections_active / database_connections_total > 0.8
        for: 5m
        annotations:
          summary: "High database connection usage"
          
      - alert: APIHighErrorRate
        expr: api_errors_total / api_requests_total > 0.05
        for: 2m
        annotations:
          summary: "High API error rate detected"
          
      - alert: AIServiceDown
        expr: ai_service_availability < 1
        for: 1m
        annotations:
          summary: "AI service unavailable"
```

## Monitoring Dashboards

### 1. System Overview Dashboard

**Key Metrics:**
- Overall system health status
- API request volume and latency
- Database connection utilization
- Error rates by service
- Active user sessions

### 2. Database Performance Dashboard

**Metrics:**
- Connection pool status
- Query performance distribution
- Slow query identification
- Lock detection and resolution
- Storage and memory usage

### 3. AI Services Dashboard

**Tracking:**
- Token usage trends
- Cost analysis by service
- Circuit breaker status
- Model performance metrics
- Error rates and types

### 4. Business Metrics Dashboard

**KPIs:**
- User activity and engagement
- Compliance assessment completions
- Evidence upload rates
- System adoption metrics

## Alerting Strategy

### 1. Critical Alerts (Immediate Response)

- Database connection failures
- API service unavailability
- Authentication system failures
- Data corruption detection
- Security breach indicators

### 2. Warning Alerts (Monitor Closely)

- High database connection usage (>80%)
- Elevated API error rates (>5%)
- AI service performance degradation
- Disk space warnings
- Memory usage spikes

### 3. Info Alerts (Trend Monitoring)

- Daily usage summaries
- Performance optimization opportunities
- Cost optimization recommendations
- Security audit summaries

## Monitoring Best Practices

### 1. Threshold Configuration

**Database Monitoring:**
```python
# Connection pool thresholds
POOL_USAGE_WARNING = 0.7  # 70%
POOL_USAGE_CRITICAL = 0.9  # 90%

# Query performance thresholds
SLOW_QUERY_WARNING = 100   # ms
SLOW_QUERY_CRITICAL = 500  # ms
```

**API Monitoring:**
```python
# Response time thresholds
API_RESPONSE_WARNING = 200   # ms
API_RESPONSE_CRITICAL = 1000 # ms

# Error rate thresholds
ERROR_RATE_WARNING = 0.02    # 2%
ERROR_RATE_CRITICAL = 0.05   # 5%
```

### 2. Data Retention

**Metrics Retention:**
- High-frequency metrics: 7 days
- Medium-frequency metrics: 30 days
- Low-frequency metrics: 90 days
- Alert history: 1 year

**Log Retention:**
- Application logs: 30 days
- Access logs: 90 days
- Error logs: 1 year
- Audit logs: 7 years (compliance requirement)

### 3. Performance Optimization

**Regular Reviews:**
- Weekly performance reports
- Monthly capacity planning
- Quarterly optimization reviews
- Annual architecture assessments

## Troubleshooting Monitoring Issues

### 1. Missing Metrics

**Check Configuration:**
```bash
# Verify monitoring is enabled
curl http://localhost:8000/api/monitoring/status

# Check Prometheus endpoint
curl http://localhost:8000/api/monitoring/prometheus
```

### 2. Alert Fatigue

**Optimization Strategies:**
- Adjust thresholds based on baseline performance
- Group related alerts
- Implement alert escalation
- Use smart notification routing

### 3. Performance Impact

**Monitoring Overhead:**
- Monitor the monitoring system resource usage
- Optimize metric collection frequency
- Use sampling for high-volume metrics
- Implement efficient data storage

## Integration Examples

### 1. Slack Notifications

```python
# webhook integration for alerts
async def send_alert_to_slack(alert_data):
    webhook_url = "https://hooks.slack.com/your-webhook"
    payload = {
        "text": f"🚨 {alert_data['title']}",
        "attachments": [{
            "color": "danger" if alert_data["severity"] == "critical" else "warning",
            "fields": [
                {"title": "Service", "value": alert_data["service"], "short": True},
                {"title": "Metric", "value": alert_data["metric"], "short": True}
            ]
        }]
    }
    # Send webhook request
```

### 2. PagerDuty Integration

```python
# critical alert escalation
async def trigger_pagerduty_alert(incident_data):
    payload = {
        "routing_key": os.getenv("PAGERDUTY_ROUTING_KEY"),
        "event_action": "trigger",
        "payload": {
            "summary": incident_data["summary"],
            "source": "ruleiq-monitoring",
            "severity": "critical"
        }
    }
    # Send to PagerDuty API
```

### 3. Custom Dashboards

```python
# business metrics API
@router.get("/business-metrics")
async def get_business_metrics():
    return {
        "active_users_24h": await get_active_users_count(),
        "assessments_completed_today": await get_daily_assessments(),
        "evidence_uploaded_today": await get_daily_evidence(),
        "compliance_score_average": await get_avg_compliance_score()
    }
```

## Security Considerations

### 1. Access Control

- Restrict monitoring endpoints to authenticated users
- Use separate monitoring service accounts
- Implement role-based access for different monitoring levels

### 2. Data Privacy

- Avoid logging sensitive data in metrics
- Encrypt monitoring data in transit and at rest
- Implement data anonymization where possible

### 3. Monitoring the Monitoring

- Monitor monitoring system health
- Set up backup monitoring systems for critical alerts
- Implement monitoring system failover procedures

---

*For troubleshooting monitoring issues, see [Troubleshooting Guide](troubleshooting.md).*