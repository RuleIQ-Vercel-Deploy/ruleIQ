# 🚀 Backend Fixes Deployment Guide

## 📋 Overview

This guide provides step-by-step instructions for deploying the comprehensive backend security and performance fixes implemented for the ruleIQ project.

## ✅ Pre-Deployment Checklist

### 1. Environment Configuration

```bash
# Verify environment variables are set
echo "DATABASE_URL: $DATABASE_URL"
echo "SECRET_KEY: $SECRET_KEY"
echo "REDIS_URL: $REDIS_URL"
```

### 2. Security Validation

```bash
# Run security validation script
python scripts/validate_config.py
```

### 3. Database Migration

```bash
# Apply database migrations
alembic upgrade head
```

## 🔧 Deployment Steps

### Step 1: Environment Setup

```bash
# Copy environment template
cp env.template .env

# Edit .env with production values
nano .env
```

### Step 2: Database Migration

```bash
# Apply performance indexes
alembic upgrade head

# Verify indexes are created
psql $DATABASE_URL -c "\d evidence"
psql $DATABASE_URL -c "\d assessments"
```

### Step 3: Security Configuration

```bash
# Generate secure keys if needed
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Set production environment variables
export ENVIRONMENT=production
export DEBUG=false
export SECRET_KEY="your-generated-secure-key"
```

### Step 4: Run Tests

```bash
# Run security tests
pytest tests/security/test_security_fixes.py -v

# Run performance tests
pytest tests/performance/test_performance_fixes.py -v

# Run integration tests
pytest tests/integration/ -v
```

### Step 5: Security Audit

```bash
# Run security audit script
python scripts/security_audit.py

# Check for exposed secrets
grep -r "password\|secret\|key" --exclude-dir=.git --exclude-dir=__pycache__ . | grep -v ".env"
```

## 🔍 Post-Deployment Validation

### 1. API Health Check

```bash
# Test API endpoints
curl -X GET http://localhost:8000/api/v1/health

# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}'
```

### 2. Database Performance

```bash
# Check query performance
psql $DATABASE_URL -c "EXPLAIN ANALYZE SELECT * FROM evidence WHERE user_id = 1;"

# Verify indexes are being used
psql $DATABASE_URL -c "SELECT schemaname,tablename,attname,n_distinct,correlation FROM pg_stats WHERE tablename = 'evidence';"
```

### 3. Security Headers

```bash
# Check security headers
curl -I http://localhost:8000/api/v1/health
```

## 🚨 Rollback Procedures

### Quick Rollback

```bash
# Rollback database migration
alembic downgrade -1

# Revert to previous deployment
git checkout HEAD~1
```

### Emergency Rollback

```bash
# Stop services
docker-compose down

# Restore from backup
pg_restore -d $DATABASE_URL backup.sql

# Restart with previous version
docker-compose up -d
```

## 📊 Monitoring Setup

### 1. Application Monitoring

```bash
# Set up logging
export LOG_LEVEL=INFO
export LOG_FILE=/var/log/ruleiq/app.log

# Configure monitoring
export SENTRY_DSN="your-sentry-dsn"
```

### 2. Database Monitoring

```bash
# Monitor slow queries
psql $DATABASE_URL -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

### 3. Security Monitoring

```bash
# Monitor failed login attempts
tail -f /var/log/ruleiq/security.log | grep "authentication_failed"
```

## 🔄 Continuous Deployment

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy Backend Fixes
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run Security Tests
        run: pytest tests/security/

      - name: Run Performance Tests
        run: pytest tests/performance/

      - name: Deploy to Production
        run: |
          docker-compose -f docker-compose.prod.yml up -d
```

## 📞 Support & Troubleshooting

### Common Issues

#### 1. Database Migration Fails

```bash
# Check migration status
alembic current

# Manual rollback
alembic downgrade base
alembic upgrade head
```

#### 2. Security Headers Missing

```bash
# Check middleware configuration
python -c "from api.main import app; print(app.middleware_stack)"
```

#### 3. Performance Issues

```bash
# Check database indexes
psql $DATABASE_URL -c "\di"

# Check query performance
psql $DATABASE_URL -c "SELECT * FROM pg_stat_user_tables ORDER BY seq_scan DESC;"
```

### Support Contacts

- **Security Issues**: security@ruleiq.com
- **Performance Issues**: performance@ruleiq.com
- **General Support**: support@ruleiq.com

## 🎯 Success Metrics

### Security Metrics

- [ ] All security tests pass
- [ ] No exposed credentials in logs
- [ ] Security headers present in all responses
- [ ] Rate limiting working correctly

### Performance Metrics

- [ ] Database queries < 100ms
- [ ] API response time < 500ms
- [ ] No N+1 query issues
- [ ] Memory usage stable

### Monitoring Metrics

- [ ] Error rate < 1%
- [ ] Uptime > 99.9%
- [ ] Response time p95 < 1s
- [ ] Database connection pool healthy

## 📝 Documentation Updates

### API Documentation

- [ ] Update OpenAPI specs
- [ ] Document new security headers
- [ ] Update rate limiting documentation

### Developer Documentation

- [ ] Update setup instructions
- [ ] Document security best practices
- [ ] Update deployment procedures

---

## ✅ Deployment Complete

Once all steps are completed and verified, your backend fixes are successfully deployed and the application is ready for production use.

**Last Updated**: 2025-07-19
**Version**: 1.0.0
**Status**: Production Ready
