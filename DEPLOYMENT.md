# ComplianceGPT Deployment Guide

This document provides a comprehensive guide for deploying ComplianceGPT to production.

## Pre-Deployment Checklist

### 1. Environment Configuration ✅

- [ ] Create `.env` file from `.env.example`
- [ ] Set `DATABASE_URL` for PostgreSQL connection
- [ ] Set `REDIS_URL` for Redis connection  
- [ ] Configure `SECRET_KEY` (use a secure random key)
- [ ] Set `GOOGLE_API_KEY` for AI functionality
- [ ] Configure `SMTP_*` variables for email notifications
- [ ] Set `ALLOWED_ORIGINS` for CORS
- [ ] Configure OAuth credentials for integrations
- [ ] Set `ENCRYPTION_KEY` for sensitive data encryption

### 2. Database Setup ✅

- [ ] PostgreSQL server is running and accessible
- [ ] Database created with proper user permissions
- [ ] Run `alembic upgrade head` to apply all migrations
- [ ] Verify all tables are created correctly
- [ ] Test database connectivity

### 3. Infrastructure Services ✅

- [ ] Redis server is running and accessible
- [ ] Test Redis connectivity and basic operations
- [ ] Ensure Redis persistence is configured if needed
- [ ] Configure Redis memory limits and eviction policies

### 4. Application Dependencies ✅

- [ ] Python 3.8+ is installed
- [ ] Virtual environment is created and activated
- [ ] All packages from `requirements.txt` are installed
- [ ] No dependency conflicts exist
- [ ] Application imports successfully

### 5. Celery Workers Setup ✅

- [ ] Celery workers can start without errors
- [ ] Celery Beat scheduler is configured
- [ ] All task queues are properly routed
- [ ] Test background task execution
- [ ] Monitor worker health and performance

### 6. Security Configuration ✅

- [ ] All secrets are properly secured (not in version control)
- [ ] HTTPS is configured (production only)
- [ ] CORS settings are appropriate for your domain
- [ ] Rate limiting is configured
- [ ] Input validation is working
- [ ] SQL injection protection is enabled

### 7. AI Services Configuration ✅

- [ ] Google AI API key is valid and has quota
- [ ] OpenAI API key is configured (optional)
- [ ] AI assistant can process test messages
- [ ] Content generation is working
- [ ] API rate limits are understood

### 8. Monitoring and Logging ✅

- [ ] Application logging is configured
- [ ] Log rotation is set up
- [ ] Error tracking is enabled
- [ ] Performance monitoring is configured
- [ ] Health check endpoints are working

## Deployment Methods

### Method 1: Docker Deployment (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd Experiment

# 2. Create environment file
cp .env.example .env
# Edit .env with your configuration

# 3. Build and start services
docker-compose up -d

# 4. Run database migrations
docker-compose exec app alembic upgrade head

# 5. Verify deployment
docker-compose exec app python scripts/deploy.py --health-check
```

### Method 2: Local Deployment

```bash
# 1. Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 4. Run database migrations
alembic upgrade head

# 5. Start Redis (if not already running)
redis-server

# 6. Start Celery workers
chmod +x start_workers.sh
./start_workers.sh

# 7. Start the application
uvicorn main:app --host 0.0.0.0 --port 8000

# 8. Verify deployment
python scripts/deploy.py --health-check
```

### Method 3: Production Server Deployment

For production deployment on a server:

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql redis-server nginx

# 2. Set up application user
sudo adduser compliancegpt
sudo su - compliancegpt

# 3. Deploy application
git clone <repository-url> /home/compliancegpt/app
cd /home/compliancegpt/app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure services
# Set up systemd services for app, celery workers, and celery beat
# Configure nginx as reverse proxy
# Set up SSL certificates

# 5. Run deployment checks
python scripts/deploy.py --health-check --host http://your-domain.com
```

## Post-Deployment Verification

### Automated Tests

Run the deployment checker:
```bash
python scripts/deploy.py --health-check --output deployment-report.json
```

### Manual Verification

1. **API Endpoints**:
   - [ ] Visit `/` - should show API info
   - [ ] Visit `/health` - should return healthy status
   - [ ] Visit `/api/docs` - should show API documentation

2. **Authentication**:
   - [ ] User registration works
   - [ ] User login works
   - [ ] JWT tokens are generated correctly

3. **Core Functionality**:
   - [ ] Business profile creation
   - [ ] Evidence item management
   - [ ] Policy generation
   - [ ] Report generation (PDF and JSON)
   - [ ] AI assistant responses

4. **Background Tasks**:
   - [ ] Evidence collection tasks
   - [ ] Report generation tasks  
   - [ ] Email notifications
   - [ ] Scheduled tasks

5. **Integrations**:
   - [ ] Google Workspace integration setup
   - [ ] OAuth flow works
   - [ ] Evidence collection from integrations

### Load Testing

Run load tests to ensure performance:
```bash
pip install locust
locust -f tests/load/locustfile.py --host=http://your-domain.com
```

## Monitoring Setup

### Application Monitoring

1. **Health Checks**:
   ```bash
   # Set up monitoring that checks these endpoints regularly
   curl http://your-domain.com/health
   curl http://your-domain.com/api/evidence/health
   ```

2. **Performance Metrics**:
   - Response times for critical endpoints
   - Database query performance
   - Memory and CPU usage
   - Redis performance

3. **Error Tracking**:
   - Application error rates
   - Failed background tasks
   - Integration failures
   - Database connection issues

### Alerting

Set up alerts for:
- [ ] Application downtime
- [ ] High error rates (>5%)
- [ ] Slow response times (>2s for critical endpoints)
- [ ] Failed Celery tasks
- [ ] Database connection failures
- [ ] Redis connection failures
- [ ] High memory/CPU usage (>80%)

## Backup and Recovery

### Database Backups

```bash
# Daily automated backup
pg_dump -h localhost -U username dbname > backup_$(date +%Y%m%d).sql

# Restore from backup
psql -h localhost -U username dbname < backup_20240101.sql
```

### Application Backups

- [ ] Code repository is backed up
- [ ] Environment configuration is secured
- [ ] Uploaded files are backed up
- [ ] Redis data persistence is configured

## Security Hardening

### Production Security Checklist

- [ ] All default passwords changed
- [ ] Firewall configured to allow only necessary ports
- [ ] SSH access secured with key-based authentication
- [ ] Regular security updates applied
- [ ] SSL/TLS certificates configured and auto-renewing
- [ ] Database access restricted to application only
- [ ] Redis access restricted and password-protected
- [ ] Application runs as non-root user
- [ ] Sensitive environment variables are encrypted
- [ ] CORS is properly configured
- [ ] Rate limiting is enabled

### Regular Maintenance

- [ ] Weekly dependency updates
- [ ] Monthly security patches
- [ ] Quarterly security audits
- [ ] Regular backup testing
- [ ] Performance optimization reviews

## Troubleshooting Guide

### Common Issues

1. **Database Connection Errors**:
   ```bash
   # Check database status
   pg_isready -h localhost -p 5432
   
   # Check connection string
   psql "postgresql://user:pass@host:port/db"
   ```

2. **Redis Connection Errors**:
   ```bash
   # Check Redis status
   redis-cli ping
   
   # Check Redis configuration
   redis-cli config get "*"
   ```

3. **Celery Worker Issues**:
   ```bash
   # Check worker status
   celery -A celery_app inspect active
   
   # Check beat scheduler
   celery -A celery_app inspect scheduled
   
   # Restart workers
   pkill -f celery
   ./start_workers.sh
   ```

4. **AI Service Errors**:
   - Verify API keys are correct
   - Check API quota and rate limits
   - Test with simple requests first

5. **Performance Issues**:
   - Check database query performance
   - Monitor memory usage
   - Review background task queue length
   - Optimize slow endpoints

### Log Locations

- Application logs: `logs/compliancegpt.log`
- Error logs: `logs/errors.log` 
- Celery worker logs: `logs/celery_worker.log`
- Celery beat logs: `logs/celery_beat.log`
- System logs: `/var/log/syslog`

## Support and Maintenance

### Regular Tasks

- [ ] Monitor application health daily
- [ ] Review error logs weekly
- [ ] Update dependencies monthly
- [ ] Review and rotate API keys quarterly
- [ ] Backup verification monthly
- [ ] Performance optimization quarterly

### Emergency Procedures

1. **Application Down**:
   - Check system resources
   - Review recent deployments
   - Check database connectivity
   - Restart services if needed

2. **Database Issues**:
   - Check disk space
   - Review recent migrations
   - Check connection limits
   - Consider failover if configured

3. **High Load**:
   - Scale Celery workers
   - Add caching where needed
   - Optimize database queries
   - Consider load balancing

---

For additional support, refer to the application logs and monitoring dashboards. Keep this deployment guide updated as the application evolves.