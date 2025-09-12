# RuleIQ Incident Response Playbook

## Overview
This document provides the incident response procedures for RuleIQ production systems. Follow these procedures to ensure rapid resolution and minimal user impact.

## Incident Severity Levels

### SEV-1: Critical
- **Definition**: Complete service outage or data loss risk
- **Response Time**: Immediate (< 5 minutes)
- **Examples**:
  - Application completely down
  - Database corruption
  - Security breach detected
  - Payment processing failure

### SEV-2: Major
- **Definition**: Significant degradation affecting many users
- **Response Time**: < 15 minutes
- **Examples**:
  - Error rate > 10%
  - Response time > 5x baseline
  - Authentication service degraded
  - AI service unavailable

### SEV-3: Minor
- **Definition**: Limited impact or degradation
- **Response Time**: < 1 hour
- **Examples**:
  - Single feature unavailable
  - Performance degradation < 2x baseline
  - Non-critical service issues

## Alert Escalation Matrix

| Severity | Primary Contact | Secondary Contact | Escalation Time |
|----------|----------------|-------------------|-----------------|
| SEV-1 | On-call Engineer | Engineering Lead | 10 minutes |
| SEV-2 | On-call Engineer | Team Lead | 30 minutes |
| SEV-3 | Team Member | On-call Engineer | 2 hours |

## Response Procedures

### 1. Initial Response (0-5 minutes)

1. **Acknowledge Alert**
   ```bash
   # Via PagerDuty CLI
   pd incident acknowledge -i <incident-id>
   ```

2. **Assess Severity**
   - Check monitoring dashboards: http://localhost:3000
   - Review error rates and response times
   - Check active user sessions

3. **Initiate Communication**
   ```
   Subject: [SEV-X] Incident: <Brief Description>
   
   Status: Investigating
   Impact: <Number of users affected>
   Started: <Time>
   Lead: <Your name>
   ```

### 2. Diagnosis (5-15 minutes)

#### Quick Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database connectivity
docker exec -it ruleiq-db psql -U postgres -c "SELECT 1"

# Redis connectivity
docker exec -it ruleiq-redis redis-cli ping

# Check error logs
docker logs ruleiq-app --tail 100 | grep ERROR

# Check metrics
curl http://localhost:8000/metrics | grep error_rate
```

#### Common Issues Diagnosis

**High Error Rate**
```bash
# Check recent deployments
git log --oneline -10

# Check feature flags
curl http://localhost:8000/api/v1/feature-flags/status

# Review error patterns
docker logs ruleiq-app | grep -E "ERROR|CRITICAL" | tail -50
```

**Slow Response Time**
```bash
# Check database connections
curl http://localhost:8000/metrics | grep db_connections

# Check cache performance
curl http://localhost:8000/metrics | grep cache_hit

# Monitor CPU/Memory
docker stats ruleiq-app
```

**Authentication Issues**
```bash
# Check JWT validation errors
curl http://localhost:8000/metrics | grep jwt_validation

# Review auth logs
docker logs ruleiq-app | grep AUTH | tail -50

# Test auth endpoint
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}'
```

### 3. Mitigation (15-30 minutes)

#### Automatic Rollback Trigger
```bash
# Check rollback status
curl http://localhost:8000/api/v1/deployment/rollback/status

# Manual trigger if needed
curl -X POST http://localhost:8000/api/v1/deployment/rollback \
  -H "Content-Type: application/json" \
  -d '{"reason":"manual_trigger"}'
```

#### Enable Read-Only Mode
```bash
# Enable read-only mode to prevent data corruption
curl -X POST http://localhost:8000/api/v1/system/read-only \
  -H "Content-Type: application/json" \
  -d '{"enabled":true}'
```

#### Feature Flag Disable
```bash
# Disable problematic feature
curl -X POST http://localhost:8000/api/v1/feature-flags/disable \
  -H "Content-Type: application/json" \
  -d '{"flag_name":"new_feature"}'
```

#### Circuit Breaker Reset
```bash
# Reset circuit breaker for service
curl -X POST http://localhost:8000/api/v1/circuit-breaker/reset \
  -H "Content-Type: application/json" \
  -d '{"service":"ai_service"}'
```

### 4. Recovery Procedures

#### Database Recovery
```bash
# Restore from backup
pg_restore -h localhost -U postgres -d ruleiq backup.dump

# Run migrations
alembic upgrade head

# Verify integrity
docker exec -it ruleiq-db psql -U postgres -d ruleiq -c "\dt"
```

#### Session Recovery
```bash
# Restore all user sessions
curl -X POST http://localhost:8000/api/v1/sessions/restore-all

# Verify session count
curl http://localhost:8000/metrics | grep active_sessions
```

#### Cache Rebuild
```bash
# Clear corrupted cache
docker exec -it ruleiq-redis redis-cli FLUSHDB

# Warm up cache
curl -X POST http://localhost:8000/api/v1/cache/warmup
```

## Communication Templates

### Initial Alert
```
Subject: [SEV-X] INVESTIGATING: <Issue Description>

Team,

We are currently investigating <issue description>.

Impact: <Estimated number of users affected>
Started: <Time>
Current Status: Investigating root cause
Lead: <Incident commander name>

Updates will follow every 15 minutes.
```

### Update Template
```
Subject: [SEV-X] UPDATE: <Issue Description>

Status Update #<number>

Current Status: <Investigating/Mitigating/Monitoring>
Actions Taken:
- <Action 1>
- <Action 2>

Next Steps:
- <Next action>

ETA for resolution: <Time estimate>
```

### Resolution Template
```
Subject: [SEV-X] RESOLVED: <Issue Description>

The incident has been resolved.

Resolution: <What fixed the issue>
Duration: <Total time>
Impact: <Final impact assessment>
Root Cause: <Brief root cause>

Post-mortem scheduled for: <Date/Time>
```

## Status Page Updates

### Degraded Performance
```
Title: Degraded Performance
Status: Partial Outage
Message: We are experiencing slower than normal response times. 
Our team is investigating and working on a resolution.
```

### Service Disruption
```
Title: Service Disruption
Status: Major Outage
Message: Some users may experience errors when accessing RuleIQ. 
We have identified the issue and are implementing a fix.
```

### Resolved
```
Title: Issue Resolved
Status: Operational
Message: The issue has been resolved and all systems are operational. 
We apologize for any inconvenience.
```

## Post-Mortem Template

```markdown
# Post-Mortem: [Incident Title]
Date: [Date]
Authors: [Names]
Status: [Draft/Final]

## Executive Summary
[2-3 sentence summary of the incident and impact]

## Impact
- Duration: [Start time - End time]
- Users Affected: [Number/%]
- Services Affected: [List]
- Data Loss: [Yes/No]

## Timeline
- HH:MM - Alert triggered
- HH:MM - Engineer acknowledged
- HH:MM - Root cause identified
- HH:MM - Mitigation started
- HH:MM - Service restored
- HH:MM - Incident resolved

## Root Cause
[Detailed explanation of what caused the incident]

## Resolution
[How the incident was resolved]

## Lessons Learned
### What Went Well
- [Item 1]
- [Item 2]

### What Went Wrong
- [Item 1]
- [Item 2]

### Where We Got Lucky
- [Item 1]

## Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| [Action 1] | [Name] | [Date] | [Status] |
| [Action 2] | [Name] | [Date] | [Status] |

## Supporting Documentation
- [Link to dashboards]
- [Link to logs]
- [Link to metrics]
```

## Monitoring Links

- **Grafana Dashboards**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093
- **Application Health**: http://localhost:8000/health
- **Metrics Endpoint**: http://localhost:8000/metrics

## Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| On-Call Engineer | Rotation | See PagerDuty | oncall@ruleiq.com |
| Engineering Lead | [Name] | [Phone] | [Email] |
| VP Engineering | [Name] | [Phone] | [Email] |
| Security Team | Security | [Phone] | security@ruleiq.com |

## Recovery Time Objectives

- **RTO (Recovery Time Objective)**: < 5 minutes
- **RPO (Recovery Point Objective)**: < 1 minute
- **MTTR (Mean Time To Recovery)**: < 15 minutes

## Automated Recovery Features

1. **Automatic Rollback**: Triggers on error rate > 5% for 1 minute
2. **Session Preservation**: Zero data loss during deployments
3. **Circuit Breakers**: Automatic service isolation on failures
4. **Read-Only Mode**: Automatic degradation to prevent data corruption
5. **Feature Flag Disable**: Automatic disable on error threshold

## Testing Procedures

### Monthly Drills
- Rollback testing
- Session recovery testing
- Database failover testing
- Cache rebuild testing

### Quarterly Reviews
- Incident response time analysis
- Post-mortem action item review
- Playbook updates
- Contact list verification

---

**Remember**: The goal is to minimize user impact and restore service as quickly as possible. Don't hesitate to escalate if needed.