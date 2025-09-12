# MON-001: User Impact Mitigation & Monitoring Handoff

**Task ID**: 45a95e59-e250-48e5-97ea-8a7d2011fe17  
**Priority**: P0 - USER EXPERIENCE PROTECTION  
**Assignee**: DevOps Lead  
**Deadline**: 2025-09-10 09:00 UTC (24 hours)  
**Effort**: 8 hours  

## Current State

✅ **What Exists**:
- Basic database monitoring in `/monitoring/database_monitor.py`
- Health check endpoints
- Some logging infrastructure
- Redis available for metrics
- Docker setup present

❌ **What's Missing**:
- Prometheus metrics collection
- Grafana dashboards
- Alert rules configuration
- Automatic rollback system
- Metrics exposure in application
- Incident management workflow

## Implementation Checklist

### Phase 1: Monitoring Stack (3 hours)
- [ ] Create docker-compose for Prometheus/Grafana
- [ ] Configure Prometheus scraping
- [ ] Setup Grafana datasources
- [ ] Create initial dashboards
- [ ] Configure Alertmanager
- [ ] Test stack deployment

### Phase 2: Application Metrics (3 hours)
- [ ] Install prometheus-client library
- [ ] Create metrics middleware
- [ ] Expose /metrics endpoint
- [ ] Add custom metrics (feature flags, auth)
- [ ] Implement database pool metrics
- [ ] Add business metrics

### Phase 3: Automatic Rollback (2 hours)
- [ ] Create rollback service
- [ ] Define rollback thresholds
- [ ] Implement metric queries
- [ ] Add feature flag integration
- [ ] Create incident creation
- [ ] Test rollback scenarios

## Quick Start Commands

```bash
# Start monitoring stack
cd monitoring
docker-compose up -d

# Access services
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
# Alertmanager: http://localhost:9093

# Test metrics endpoint
curl http://localhost:8000/metrics

# Trigger test alert
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{"labels":{"alertname":"test","severity":"critical"}}]'
```

## Key Files to Create/Modify

1. **New Files**:
   - `/monitoring/docker-compose.yml` - Stack configuration
   - `/monitoring/prometheus.yml` - Prometheus config
   - `/monitoring/alerts/*.yml` - Alert rules
   - `/monitoring/metrics.py` - Application metrics
   - `/services/rollback_service.py` - Auto-rollback
   - `/monitoring/grafana/dashboards/*.json` - Dashboards

2. **Files to Modify**:
   - `/main.py` - Add metrics middleware and endpoint
   - `/requirements.txt` - Add prometheus-client

## Critical Metrics to Track

### System Metrics
```python
# These metrics MUST be implemented
request_count = Counter('ruleiq_requests_total', 'Total requests', 
                        ['method', 'endpoint', 'status'])
request_duration = Histogram('ruleiq_request_duration_seconds', 
                            'Request duration', ['method', 'endpoint'])
active_users = Gauge('ruleiq_active_users', 'Active users')
database_pool_size = Gauge('ruleiq_db_pool_size', 'DB connections', ['pool'])
```

### Security Metrics
```python
auth_failures = Counter('ruleiq_auth_failures', 'Auth failures', ['reason'])
feature_flag_eval = Counter('ruleiq_ff_evaluations', 'FF evals', 
                           ['flag_name', 'result'])
security_events = Counter('ruleiq_security_events', 'Security events', ['type'])
```

## Alert Rules Configuration

### Critical Alerts (Page immediately)
```yaml
- alert: HighErrorRate
  expr: rate(ruleiq_requests_total{status=~"5.."}[5m]) > 0.05
  for: 2m
  annotations:
    summary: "Error rate above 5%"
    
- alert: AuthenticationAttack
  expr: rate(ruleiq_auth_failures[1m]) > 10
  for: 30s
  annotations:
    summary: "Possible authentication attack"
```

### Warning Alerts (Notify team)
```yaml
- alert: HighLatency
  expr: histogram_quantile(0.95, request_duration_bucket) > 2
  for: 5m
  annotations:
    summary: "P95 latency above 2 seconds"
    
- alert: DatabasePoolPressure
  expr: ruleiq_db_pool_size / 50 > 0.8
  for: 5m
  annotations:
    summary: "Database pool above 80%"
```

## Grafana Dashboard Requirements

### Main Dashboard Panels
1. **Request Rate** - Requests per second by endpoint
2. **Error Rate** - 5xx errors percentage
3. **Latency** - P50, P95, P99 response times
4. **Active Users** - Currently active users
5. **Feature Flags** - Evaluation rates and results
6. **Auth Events** - Login success/failure rates
7. **Database** - Connection pool usage
8. **System Health** - CPU, Memory, Disk

### Feature Flag Dashboard
1. **Flag Status** - Enabled/disabled states
2. **Evaluation Rate** - Per flag per minute
3. **Rollout Progress** - Percentage served
4. **Recent Changes** - Audit trail
5. **Impact Metrics** - Error correlation

## Automatic Rollback Logic

```python
class RollbackThresholds:
    ERROR_RATE = 0.05      # 5% error rate
    P95_LATENCY = 2.0      # 2 seconds
    AUTH_FAILURES = 100    # per minute
    DB_POOL_USAGE = 0.9    # 90% pool usage
    
async def should_rollback(metrics):
    if metrics['error_rate'] > ERROR_RATE:
        return True, "High error rate"
    if metrics['p95_latency'] > P95_LATENCY:
        return True, "High latency"
    if metrics['auth_failures_pm'] > AUTH_FAILURES:
        return True, "Auth attack detected"
    return False, None
```

## Success Validation

Run this validation script:

```bash
#!/bin/bash
# /scripts/validate_monitoring.sh

echo "Validating monitoring setup..."

# Check services are running
docker-compose ps | grep prometheus | grep Up || exit 1
docker-compose ps | grep grafana | grep Up || exit 1

# Test metrics endpoint
curl -s http://localhost:8000/metrics | grep ruleiq_ || exit 1

# Test Prometheus is scraping
curl -s http://localhost:9090/api/v1/targets | grep "health\":\"up" || exit 1

# Test alert rules loaded
curl -s http://localhost:9090/api/v1/rules | grep "groups" || exit 1

echo "✅ Monitoring validated!"
```

## Incident Response Workflow

When automatic rollback triggers:

1. **Immediate Actions**:
   - Disable recent feature flags
   - Send PagerDuty alert
   - Create incident ticket
   - Post to #incidents Slack

2. **Within 5 minutes**:
   - Engineering lead acknowledges
   - Rollback confirmation
   - Status page update
   - Customer communication if needed

3. **Post-Incident**:
   - Root cause analysis
   - Postmortem document
   - Action items tracking
   - Monitoring improvements

## Performance Requirements

- Metrics collection overhead <1% CPU
- Prometheus scraping every 15 seconds
- Alert evaluation every 30 seconds
- Rollback decision within 1 minute
- Dashboard refresh every 5 seconds

## Escalation Path

If blocked or behind schedule:
1. **Hour 2**: Docker stack must be running
2. **Hour 4**: Basic metrics exposed
3. **Hour 6**: Critical alerts configured
4. **Hour 7**: Rollback system functional
5. **Hour 8**: Documentation complete

## Dependencies

- Docker and docker-compose installed
- Port 3000, 9090, 9093 available
- Application metrics library installed
- Redis for metric buffering

## Handoff to P1 Tasks

Once complete:
1. Monitoring stack fully operational
2. All critical metrics exposed
3. Dashboards created and tested
4. Alert rules validated
5. Automatic rollback tested
6. Runbook documented

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Prometheus can't scrape | Check network, firewall, /metrics endpoint |
| Grafana won't start | Check port conflicts, permissions |
| Metrics missing | Verify middleware order, check exempted paths |
| Alerts not firing | Check alert rules syntax, thresholds |
| Rollback too sensitive | Adjust thresholds, add confirmation delay |

## Default Credentials

- Grafana: admin/admin (change immediately)
- Prometheus: No auth (secure in production)
- Alertmanager: No auth (secure in production)

---

**Remember**: This system protects users from bad deployments. Zero data loss and <5min recovery are mandatory.