# 🚀 RuleIQ Deployment Guide

This comprehensive guide covers all aspects of deploying the RuleIQ compliance automation platform, including environment setup, health checks, deployment paths, rollback procedures, and monitoring.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Pre-Deployment Validation](#pre-deployment-validation)
4. [Deployment Paths](#deployment-paths)
5. [Health Checks](#health-checks)
6. [Testing](#testing)
7. [Rollback Procedures](#rollback-procedures)
8. [Monitoring](#monitoring)
9. [Incident Response](#incident-response)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying RuleIQ, ensure you have:

- **Python 3.11+** installed locally
- **Node.js 18+** and **pnpm 8+** for frontend
- **Docker** and **Docker Compose** for containerized deployment
- **PostgreSQL 14+** database (or Neon/Supabase for Vercel)
- **Redis** for caching (optional but recommended)
- **Git** for version control
- Access to deployment credentials

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/ruleiq.git
cd ruleiq
```

### 2. Configure Environment Variables

Use the environment template to set up your deployment configuration:

```bash
# Copy the comprehensive environment template
cp env.comprehensive.template .env

# For Vercel deployment specifically
cp .vercel.env.example .env.vercel

# Edit with your specific values
nano .env
```

### 3. Required Environment Variables

#### Core Configuration
```env
# Deployment Environment
ENVIRONMENT=production  # or staging, development
APP_VERSION=2.0.0
LOG_LEVEL=INFO

# Security Keys (generate with openssl rand -hex 32)
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

#### Database Configuration
```env
# PostgreSQL Connection
DATABASE_URL=postgresql://user:password@host:5432/ruleiq
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# For Vercel/Serverless
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require&connect_timeout=10
```

#### Optional Services
```env
# Redis Cache
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50

# AI Services
GOOGLE_AI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
```

### 4. Install Dependencies

```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
pnpm install
cd ..
```

## Pre-Deployment Validation

### 1. Run Startup Diagnostics

Check system readiness before deployment:

```bash
python startup_diagnostics.py
```

This validates:
- Environment variables
- Database connectivity
- Redis connection (if configured)
- API endpoint accessibility
- File permissions
- Port availability

Expected output:
```
✅ Environment variables configured correctly
✅ Database connection successful
✅ Redis connection successful
✅ API endpoints accessible
✅ System ready for deployment
```

### 2. Database Health Check

Verify database is properly configured:

```bash
python database_health_check.py
```

This checks:
- Connection pooling
- Table existence
- Migration status
- Performance metrics
- Connection limits

### 3. Validate API Endpoints

Ensure all endpoints are functional:

```bash
python validate_endpoints.py
```

This tests:
- Health endpoints (`/health`, `/ready`)
- Authentication routes
- Core API functionality
- Response times
- Error handling

### 4. Run Pre-Deployment Checklist

Execute comprehensive pre-deployment validation:

```bash
python deployment/pre_deployment_checklist.py
```

## Deployment Paths

### Option 1: Docker Deployment (Recommended for Production)

#### Standard Docker Deployment

```bash
# Build and start services
docker-compose up -d

# Or use the production configuration
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Blue-Green Docker Deployment

For zero-downtime deployments:

```bash
# Deploy to green environment
docker-compose -f docker-compose.green.yml up -d

# Verify green is healthy
curl http://localhost:8001/health

# Switch traffic to green
docker-compose -f docker-compose.nginx.yml exec nginx nginx -s reload

# Stop blue environment
docker-compose -f docker-compose.blue.yml down
```

### Option 2: Vercel Deployment (Serverless)

#### Quick Vercel Deploy

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

#### Detailed Vercel Setup

1. **Configure Vercel Project**:
   - Framework Preset: Other
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: `.`

2. **Set Environment Variables** in Vercel Dashboard:
   - Navigate to Settings → Environment Variables
   - Add all required variables from `.vercel.env.example`
   - Use different values for Production/Preview environments

3. **Test Locally with Vercel Environment**:
   ```bash
   python scripts/test_vercel_locally.py
   ```

4. **Deploy**:
   ```bash
   vercel --prod
   ```

See [README_VERCEL_DEPLOYMENT.md](../README_VERCEL_DEPLOYMENT.md) for detailed Vercel instructions.

### Option 3: Manual Deployment

For traditional server deployment:

```bash
# Set up Python virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start application
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Health Checks

### Automated Health Monitoring

The system provides multiple health check endpoints:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed readiness check (includes DB)
curl http://localhost:8000/ready

# Comprehensive system status
curl http://localhost:8000/api/system/status
```

### Manual Health Verification

```bash
# Run comprehensive health check
python deployment/full_app_test.py

# Check specific components
make test-health      # Health endpoints
make test-db         # Database connectivity
make test-redis      # Redis cache
make test-auth       # Authentication system
```

## Testing

### Run Test Suite

Execute tests via Makefile:

```bash
# Run all tests
make test

# Run specific test categories
make test-unit       # Unit tests only
make test-integration # Integration tests
make test-e2e        # End-to-end tests
make test-security   # Security tests

# Run with coverage
make test-coverage

# Run linting and type checking
make lint
make typecheck
```

### Performance Testing

```bash
# Load testing with artillery
npm install -g artillery
artillery quick --count 10 --num 100 http://localhost:8000/health

# Or use the Makefile
make test-performance
```

## Rollback Procedures

### Automatic Rollback System

The platform includes an automatic rollback system (`deployment/rollback.py`) that monitors key metrics and triggers rollback when thresholds are exceeded:

#### Monitored Metrics and Thresholds
- **Error Rate**: > 5% for 60 seconds
- **Response Time**: > 2x baseline for 120 seconds
- **DB Connections**: > 80% utilization for 60 seconds
- **Auth Failures**: > 100 per minute for 60 seconds
- **AI Cost Rate**: > $10 per minute for 60 seconds

#### Automatic Rollback Process

1. **Detection**: System continuously monitors metrics
2. **Trigger**: Threshold exceeded for duration
3. **Rollback**: Automatic reversion to previous version
4. **Recovery**: < 5 minutes guaranteed recovery time
5. **Alert**: Team notified via configured channels

### Manual Rollback

#### Docker Rollback

```bash
# Quick rollback to previous image
docker-compose down
docker-compose -f docker-compose.backup.yml up -d

# Or use specific version
docker-compose up -d --force-recreate ruleiq:v1.9.0
```

#### Vercel Rollback

```bash
# List recent deployments
vercel ls

# Rollback to specific deployment
vercel rollback [deployment-url]

# Or use the Vercel Dashboard
# Navigate to Deployments → Select previous → Promote to Production
```

#### Database Rollback

```bash
# Rollback to specific migration
alembic downgrade -1  # One step back
alembic downgrade [revision]  # Specific revision

# Restore from backup if needed
pg_restore -d ruleiq backup.dump
```

### Rollback Verification

After rollback, verify system health:

```bash
# Check service status
python deployment/deployment_orchestrator.py --verify-rollback

# Run health checks
curl http://localhost:8000/health
python validate_endpoints.py

# Check error rates
tail -f logs/error.log | grep ERROR
```

## Monitoring

### Monitoring Setup

The platform includes comprehensive monitoring via the `monitoring/` directory:

#### 1. Prometheus Metrics

Configure Prometheus with provided config:

```bash
# Start Prometheus
docker-compose -f docker-compose.monitoring.yml up -d prometheus

# Access metrics
http://localhost:9090
```

Key metrics exposed:
- Request rate and latency
- Error rates by endpoint
- Database connection pool stats
- Cache hit rates
- AI API usage and costs

#### 2. Alert Configuration

Alerts are defined in `monitoring/alerts.yml`:

```yaml
# Critical alerts
- High error rate (> 5%)
- Slow response times (> 2s)
- Database connection failures
- Memory usage > 90%
- Disk space < 10%
```

#### 3. Sentry Error Tracking

Configure Sentry for error tracking:

```bash
# Set in environment
SENTRY_DSN=https://your-key@sentry.io/project

# Errors automatically captured and reported
```

#### 4. Custom Monitoring

Use the database monitor for specific checks:

```python
# Run database monitoring
python monitoring/database_monitor.py

# Custom metrics collection
from monitoring.metrics import get_metrics_collector
collector = get_metrics_collector()
collector.record_metric("custom_metric", value)
```

### Monitoring Dashboards

Access monitoring dashboards:

- **Grafana**: http://localhost:3000 (if configured)
- **Prometheus**: http://localhost:9090
- **Application Metrics**: http://localhost:8000/metrics

## Incident Response

### Incident Response Workflow

1. **Detection**
   - Automated alerts via monitoring
   - User reports
   - System logs

2. **Assessment**
   ```bash
   # Quick system assessment
   python deployment/deployment_orchestrator.py --assess
   
   # Check critical services
   docker-compose ps
   curl http://localhost:8000/health
   ```

3. **Response**
   - **P0 (Critical)**: Immediate rollback if needed
   - **P1 (High)**: Fix forward or controlled rollback
   - **P2 (Medium)**: Schedule fix for next deployment
   - **P3 (Low)**: Add to backlog

4. **Recovery**
   ```bash
   # Execute recovery procedure
   python deployment/rollback.py --auto-recover
   
   # Verify recovery
   make test-health
   ```

5. **Post-Incident**
   - Document in incident log
   - Update runbooks
   - Implement preventive measures

### Emergency Contacts

- **On-Call Engineer**: Check PagerDuty
- **DevOps Team**: devops@ruleiq.com
- **Database Admin**: dba@ruleiq.com
- **Security Team**: security@ruleiq.com

## Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Issues

**Problem**: "connection pool exhausted" errors

**Solution**:
```bash
# Increase pool size
export DATABASE_POOL_SIZE=50

# Or use serverless configuration
export DATABASE_URL="${DATABASE_URL}?connect_timeout=10&pool_mode=transaction"

# Restart services
docker-compose restart api
```

#### 2. High Memory Usage

**Problem**: Container using excessive memory

**Solution**:
```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
mem_limit: 4g

# Or optimize application
export PYTHON_GC_THRESHOLD=700
```

#### 3. Slow Response Times

**Problem**: API responses taking > 2 seconds

**Solution**:
```bash
# Enable query optimization
export DATABASE_STATEMENT_TIMEOUT=5000

# Add caching
export REDIS_URL=redis://localhost:6379

# Check slow queries
tail -f logs/slow_query.log
```

#### 4. Failed Deployments

**Problem**: Deployment fails health checks

**Solution**:
```bash
# Check deployment logs
docker-compose logs --tail=100

# Verify environment variables
python startup_diagnostics.py

# Test locally first
python scripts/test_vercel_locally.py
```

### Debug Commands

```bash
# View application logs
tail -f logs/app.log

# Check error logs
grep ERROR logs/error.log

# Monitor in real-time
docker-compose logs -f

# Database queries
psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity;"

# Redis monitoring
redis-cli monitor

# System resources
htop
df -h
free -h
```

## Best Practices

1. **Always run pre-deployment checks** before deploying
2. **Use staging environment** for testing changes
3. **Monitor metrics** during and after deployment
4. **Keep rollback plan ready** before major changes
5. **Document all changes** in deployment log
6. **Use blue-green deployment** for zero downtime
7. **Automate repetitive tasks** via Makefile
8. **Regular backup** of database and configurations
9. **Security scanning** before production deployment
10. **Load testing** for performance validation

## Additional Resources

- [Frontend Deployment Guide](../frontend/DEPLOYMENT.md)
- [Vercel Deployment Guide](../README_VERCEL_DEPLOYMENT.md)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Best Practices](https://www.postgresql.org/docs/current/admin.html)
- [Monitoring Setup](../monitoring/README.md)
- [Security Guidelines](../docs/SECURITY.md)

## Support

For deployment assistance:
- Check deployment logs: `logs/deployment.log`
- Review error logs: `logs/error.log`
- Contact DevOps team: devops@ruleiq.com
- Create issue: [GitHub Issues](https://github.com/your-org/ruleiq/issues)

---

**Last Updated**: January 2025  
**Version**: 2.0.0  
**Maintained by**: RuleIQ DevOps Team