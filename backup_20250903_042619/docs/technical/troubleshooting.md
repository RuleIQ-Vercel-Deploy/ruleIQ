# Troubleshooting Guide

## Common Issues and Solutions

### Backend Issues

#### 1. Database Connection Failures

**Symptoms:**
- `sqlalchemy.exc.OperationalError: could not connect to server`
- `Connection refused` errors
- Application fails to start

**Solutions:**

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start PostgreSQL if stopped
sudo systemctl start postgresql

# Verify connection manually
psql -U ruleiq_user -d ruleiq -h localhost

# Check database exists
sudo -u postgres psql -l | grep ruleiq

# Reset connection if needed
sudo systemctl restart postgresql
```

**Environment Check:**
```bash
# Verify DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql://user:password@host:port/database

# Test connection with Python
python -c "
from sqlalchemy import create_engine
engine = create_engine('your_database_url')
print('Database connection successful!')
"
```

#### 2. Redis Connection Issues

**Symptoms:**
- `redis.exceptions.ConnectionError`
- Cache operations failing
- Session storage not working

**Solutions:**

```bash
# Check Redis status
redis-cli ping
# Should return: PONG

# Start Redis if stopped
sudo systemctl start redis

# Check Redis configuration
redis-cli config get "*"

# Clear Redis data if corrupted
redis-cli flushall
```

#### 3. Migration Errors

**Symptoms:**
- `alembic.util.exc.CommandError`
- Database schema mismatches
- Migration conflicts

**Solutions:**

```bash
# Check current migration status
alembic current

# View migration history
alembic history

# Reset migrations (DEVELOPMENT ONLY)
alembic downgrade base
alembic upgrade head

# Fix migration conflicts
alembic merge -m "merge conflict resolution" head1 head2
```

#### 4. Import Errors

**Symptoms:**
- `ModuleNotFoundError`
- `ImportError: cannot import name`
- Circular import errors

**Solutions:**

```bash
# Verify virtual environment
source .venv/bin/activate
which python

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# For circular imports, check import order in __init__.py files
```

#### 5. AI Service Failures

**Symptoms:**
- `google.generativeai.types.BlockedPromptException`
- API rate limiting errors
- Circuit breaker activation

**Solutions:**

```bash
# Check API keys
echo $GOOGLE_API_KEY

# Test AI service health
curl http://localhost:8000/api/ai/health

# Reset circuit breaker
curl -X POST http://localhost:8000/api/ai/circuit-breaker/reset

# Check rate limiting status
curl http://localhost:8000/api/ai/rate-limits
```

### Frontend Issues

#### 1. Build Failures

**Symptoms:**
- TypeScript compilation errors
- Next.js build failures
- Module resolution errors

**Solutions:**

```bash
cd frontend

# Clear cache and reinstall
rm -rf .next node_modules
pnpm install

# Check for TypeScript errors
pnpm typecheck

# Build in development mode for better error messages
pnpm build

# Check for duplicate dependencies
pnpm ls --depth=0
```

#### 2. API Connection Issues

**Symptoms:**
- Network request failures
- CORS errors
- Authentication failures

**Solutions:**

```bash
# Verify API URL configuration
grep NEXT_PUBLIC_API_URL .env.local

# Test API connection
curl http://localhost:8000/health

# Check CORS configuration in backend
grep ALLOWED_ORIGINS ../.env

# Verify JWT token format
# Check browser dev tools > Application > Session Storage
```

#### 3. Styling Issues

**Symptoms:**
- Tailwind classes not working
- Component styling broken
- Design system inconsistencies

**Solutions:**

```bash
# Rebuild Tailwind CSS
pnpm dev  # This regenerates CSS

# Check Tailwind configuration
cat tailwind.config.ts

# Verify component imports
# Check for missing shadcn/ui components

# Test with new theme
NEXT_PUBLIC_USE_NEW_THEME=true pnpm dev
```

### Performance Issues

#### 1. Slow API Responses

**Diagnosis:**
```bash
# Check database performance
curl http://localhost:8000/api/monitoring/database

# Review slow queries
psql -U ruleiq_user -d ruleiq -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"

# Monitor connection pool usage
curl http://localhost:8000/api/monitoring/database/pool
```

**Solutions:**
- Add database indexes for frequently queried columns
- Optimize N+1 queries
- Implement query result caching
- Review database connection pool settings

#### 2. High Memory Usage

**Diagnosis:**
```bash
# Check process memory usage
ps aux | grep python
ps aux | grep node

# Monitor database connections
psql -U ruleiq_user -d ruleiq -c "
SELECT count(*) as active_connections 
FROM pg_stat_activity 
WHERE state = 'active';
"
```

**Solutions:**
- Implement pagination for large datasets
- Add memory limits to Docker containers
- Optimize data serialization
- Review caching strategies

### Development Environment Issues

#### 1. Port Conflicts

**Symptoms:**
- `EADDRINUSE: address already in use`
- Services fail to start

**Solutions:**

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 $(lsof -t -i:8000)

# Use alternative ports
PORT=8001 python main.py
```

#### 2. Permission Issues

**Symptoms:**
- File permission errors
- Database access denied

**Solutions:**

```bash
# Fix file permissions
chmod -R 755 .
chown -R $USER:$USER .

# PostgreSQL permissions
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE ruleiq TO ruleiq_user;
```

### Testing Issues

#### 1. Test Database Issues

**Solutions:**

```bash
# Create test database
createdb ruleiq_test

# Run tests with test database
TEST_DATABASE_URL=postgresql://user:pass@localhost/ruleiq_test pytest

# Clean test database after runs
dropdb ruleiq_test
createdb ruleiq_test
```

#### 2. Flaky Tests

**Diagnosis:**
- Tests pass individually but fail in suite
- Race conditions in async tests
- Database state leaking between tests

**Solutions:**
- Use database transactions that rollback
- Add proper test isolation
- Use mock objects for external services
- Add retry logic for flaky external dependencies

## Monitoring and Alerting

### Health Check Endpoints

```bash
# Overall system health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/api/monitoring/health

# AI services health
curl http://localhost:8000/api/ai/health

# Frontend health (if running)
curl http://localhost:3000/api/health
```

### Log Analysis

**Backend Logs:**
```bash
# View application logs
tail -f logs/app.log

# Filter for errors
grep ERROR logs/app.log

# Database query logs
grep "slow query" logs/app.log
```

**Frontend Logs:**
```bash
# Next.js logs
cd frontend
pnpm dev 2>&1 | tee frontend.log

# Browser console logs
# Check browser dev tools > Console
```

### Performance Monitoring

```bash
# Database performance
curl http://localhost:8000/api/monitoring/database/pool

# API performance metrics
curl http://localhost:8000/api/monitoring/prometheus
```

## Getting Help

### Escalation Process

1. **Check documentation** in `/docs/`
2. **Search existing issues** in repository
3. **Check logs** for detailed error messages
4. **Create minimal reproduction** case
5. **Contact development team** with:
   - Error messages
   - Steps to reproduce
   - Environment details
   - Log excerpts

### Useful Commands Reference

```bash
# System information
uname -a
python --version
node --version
pnpm --version

# Service status
systemctl status postgresql
systemctl status redis
docker ps

# Process monitoring
top
htop
ps aux | grep python

# Network debugging
netstat -tulpn
ss -tulpn
curl -v http://localhost:8000/health
```

### Emergency Procedures

**System Recovery:**
1. Stop all services
2. Backup current data
3. Reset to known good state
4. Restart services
5. Verify functionality
6. Monitor for issues

**Data Recovery:**
1. Check recent backups
2. Review transaction logs
3. Use point-in-time recovery if available
4. Contact database administrator

---

*For additional support, see [Developer Setup](../developer/setup.md) or contact the development team.*