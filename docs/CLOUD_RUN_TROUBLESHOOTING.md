# Google Cloud Run Deployment Troubleshooting Guide

## Overview
This guide helps resolve common issues when deploying the RuleIQ backend to Google Cloud Run, with a focus on Pydantic validation errors, dependency conflicts, and startup failures.

## Critical Issues and Solutions

### ModuleNotFoundError: No module named 'asyncpg'

**Problem**: The most critical Cloud Run deployment failure is the missing asyncpg module during application startup:

```
ModuleNotFoundError: No module named 'asyncpg'
  File "/app/api/main.py", line 12, in <module>
    from api.routers.ai_assessments import router as ai_assessments_router
  File "/app/api/routers/ai_assessments.py", line 8, in <module>
    from api.dependencies.auth import get_current_user
  File "/app/api/dependencies/auth.py", line 10, in <module>
    from database.db_setup import get_async_session_maker
  File "/app/database/db_setup.py", line 327, in <module>
    async_session_maker = get_async_session_maker()
```

**Root Cause**: 
1. **Eager Database Initialization**: Line 327 in `database/db_setup.py` creates `async_session_maker = get_async_session_maker()` at import time, forcing immediate database connection
2. **Missing asyncpg Module**: Despite being in requirements-cloudrun.txt, asyncpg is not available at runtime, suggesting a Docker build or installation issue
3. **Import Chain Failure**: The error occurs during module import chain before the application can start

**Solutions**:

1. **Fix Docker Build Dependencies**:
   ```dockerfile
   # Add build dependencies for asyncpg compilation
   RUN apt-get update && apt-get install -y \
       build-essential \
       libpq-dev \
       python3-dev \
       libffi-dev \
       gcc \
       g++ \
       && rm -rf /var/lib/apt/lists/*
   ```

2. **Verify asyncpg Installation**:
   ```dockerfile
   # Add verification step in Dockerfile
   RUN python -c "import asyncpg; print('asyncpg installed successfully')"
   RUN python -c "import psycopg; print('psycopg installed successfully')"
   ```

3. **Fix Requirements Specification**:
   ```txt
   # In requirements-cloudrun.txt
   asyncpg>=0.29.0,<1.0.0
   psycopg2-binary==2.9.9
   sqlalchemy[asyncio]==2.0.27
   ```

4. **Defer Database Initialization**:
   ```python
   # Remove eager initialization at module level
   # async_session_maker = get_async_session_maker()  # REMOVE THIS LINE
   
   # Use lazy initialization instead
   async_session_maker = None  # Will be initialized on first use
   ```

### Database Initialization at Import Time

**Problem**: Database connections are being established during module import rather than at runtime, causing startup failures in Cloud Run.

**Symptoms**:
```
Container failed to start within timeout
Import error during module loading
Database connection timeout during startup
```

**Root Cause**: 
- Line 327 in `database/db_setup.py` calls `get_async_session_maker()` at import time
- This forces immediate database connection before the application can start
- Cloud Run containers must start and listen on port 8080 within the timeout period

**Solutions**:

1. **Lazy Database Initialization**:
   ```python
   # In database/db_setup.py
   def get_async_session_maker():
       """Get the async session maker, initializing if needed."""
       global _ASYNC_SESSION_LOCAL
       
       if _ASYNC_SESSION_LOCAL is None:
           is_cloud_run = bool(os.getenv('K_SERVICE') or os.getenv('CLOUD_RUN_JOB'))
           
           try:
               _init_async_db()
           except ImportError as e:
               if is_cloud_run:
                   logger.warning(f'🌩️ Cloud Run: Async database initialization failed: {e}')
                   return None
               else:
                   raise
       
       return _ASYNC_SESSION_LOCAL
   ```

2. **Cloud Run Environment Detection**:
   ```python
   # Add Cloud Run detection in database initialization
   is_cloud_run = bool(os.getenv('K_SERVICE') or os.getenv('CLOUD_RUN_JOB'))
   
   if is_cloud_run:
       logger.info('🌩️ Cloud Run environment detected - using graceful database initialization')
   ```

3. **Error Handling for Missing Dependencies**:
   ```python
   try:
       import asyncpg
       logger.debug('asyncpg module is available')
   except ImportError as asyncpg_error:
       if is_cloud_run:
           logger.warning(f'🌩️ Cloud Run: asyncpg not available - deferring initialization')
           return  # Defer initialization in Cloud Run
       else:
           raise ImportError(f'asyncpg is required: {asyncpg_error}')
   ```

### Pydantic ValidationError: 2 validation errors

**Problem**: The most common Cloud Run deployment failure is Pydantic validation errors during application startup:

```
pydantic_core._pydantic_core.ValidationError: 2 validation errors for Settings
redis_url
  Value error, Redis URL must be provided and start with redis:// [type=value_error]
jwt_secret_key
  Value error, JWT secret key must be at least 32 characters long [type=value_error]
```

**Root Cause**: The Settings class validates all configuration during module import (before the application can start), but Cloud Run may not have all optional services configured.

**Solutions**:

1. **Redis Configuration for Cloud Run**:
   - Redis is now optional in Cloud Run environments
   - The application automatically detects Cloud Run (`K_SERVICE` environment variable)
   - Uses fallback Redis URL: `redis://localhost:6379/0` when not configured
   - Add Redis secret if needed:
   ```bash
   echo -n "redis://your-redis-url" | gcloud secrets create REDIS_URL --data-file=-
   ```

2. **JWT Secret Configuration**:
   - Always required and must be at least 32 characters
   - Create the secret:
   ```bash
   echo -n "$(openssl rand -base64 32)" | gcloud secrets create JWT_SECRET_KEY --data-file=-
   ```

3. **Environment Variable Configuration**:
   - **Required**: `DATABASE_URL`, `JWT_SECRET_KEY`
   - **Optional in Cloud Run**: `REDIS_URL`, `GOOGLE_AI_API_KEY`
   - **Auto-detected**: Cloud Run environment via `K_SERVICE`

### Docker Build Dependency Issues

**Problem**: Docker build fails due to missing build dependencies or incorrect package installation order.

**Symptoms**:
```
ERROR: Failed building wheel for asyncpg
ERROR: Could not build wheels for asyncpg, which is required to install pyproject.toml-based projects
Building wheel for asyncpg (pyproject.toml) ... error
```

**Root Cause**:
- Missing system dependencies required for compiling asyncpg
- Incorrect Python package installation order
- Missing PostgreSQL development headers

**Solutions**:

1. **Install Required Build Dependencies**:
   ```dockerfile
   # Add all required system packages
   RUN apt-get update && apt-get install -y \
       build-essential \
       libpq-dev \
       python3-dev \
       libffi-dev \
       gcc \
       g++ \
       curl \
       && rm -rf /var/lib/apt/lists/*
   ```

2. **Upgrade Build Tools First**:
   ```dockerfile
   # Upgrade pip, setuptools, and wheel before installing packages
   RUN python -m pip install --upgrade pip setuptools wheel
   ```

3. **Use Verbose Installation for Debugging**:
   ```dockerfile
   # Add verbose flag to see detailed installation output
   RUN pip install --no-cache-dir --verbose -r requirements-cloudrun.txt -c constraints.txt
   ```

4. **Add Comprehensive Dependency Verification**:
   ```dockerfile
   # Verify all database dependencies after installation
   RUN python -c "
   import sys
   try:
       import asyncpg
       import psycopg
       import sqlalchemy
       from sqlalchemy.ext.asyncio import create_async_engine
       print('All database dependencies verified successfully')
   except ImportError as e:
       print(f'Database dependency verification failed: {e}')
       sys.exit(1)
   "
   ```

5. **Debug Build Issues**:
   ```bash
   # Build with no cache to see all steps
   docker build --no-cache -t ruleiq-backend .
   
   # Build with progress output
   docker build --progress=plain -t ruleiq-backend .
   
   # Test specific dependency installation
   docker run --rm python:3.11-slim bash -c "
   apt-get update && apt-get install -y build-essential libpq-dev python3-dev &&
   pip install asyncpg==0.29.0 &&
   python -c 'import asyncpg; print(\"asyncpg works\")'
   "
   ```

### Container failed to start and listen on port 8080

**Problem**: Cloud Run expects the container to listen on the port specified by the `PORT` environment variable (default 8080).

**Symptoms**:
```
Cloud Run error: Container failed to start
The container failed to start listening on the port defined by PORT environment variable
```

**Solutions**:

1. **Port Configuration**:
   - Application reads `PORT` from environment: `int(os.getenv('PORT', 8000))`
   - Cloud Run sets `PORT=8080` automatically
   - Use `host="0.0.0.0"` not `localhost`

2. **Startup Command**:
   ```dockerfile
   CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
   ```

3. **Health Check Endpoints**:
   - Implement `/health/live` for liveness probe
   - Implement `/health/ready` for readiness probe
   - Must respond within 4 seconds

### Secret Management in Cloud Run

**Problem**: Secrets not properly configured or accessible to Cloud Run service.

**Complete Secret Setup**:

1. **Create Required Secrets**:
   ```bash
   # Database URL (required)
   echo -n "postgresql://user:pass@host:5432/db" | gcloud secrets create DATABASE_URL --data-file=-
   
   # JWT Secret (required)
   echo -n "$(openssl rand -base64 32)" | gcloud secrets create JWT_SECRET_KEY --data-file=-
   
   # Redis URL (optional for Cloud Run)
   echo -n "redis://your-redis-host:6379/0" | gcloud secrets create REDIS_URL --data-file=-
   
   # Google AI API Key (optional)
   echo -n "AIza..." | gcloud secrets create GOOGLE_AI_API_KEY --data-file=-
   ```

2. **Grant Access to Cloud Run**:
   ```bash
   # Get your project number
   PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")
   
   # Grant access to each secret
   for SECRET in DATABASE_URL JWT_SECRET_KEY REDIS_URL GOOGLE_AI_API_KEY; do
     gcloud secrets add-iam-policy-binding $SECRET \
       --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
       --role="roles/secretmanager.secretAccessor"
   done
   ```

3. **Cloud Build Configuration**:
   ```yaml
   --set-secrets
   DATABASE_URL=DATABASE_URL:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest,REDIS_URL=REDIS_URL:latest,GOOGLE_AI_API_KEY=GOOGLE_AI_API_KEY:latest
   ```

### Health Check Failures

**Problem**: Cloud Run health checks fail, preventing successful deployment.

**Types of Health Checks**:

1. **Startup Probe** (most critical):
   - Checks if container started successfully
   - Timeout: 240 seconds by default
   - Path: `/health/live` or `/health`
   - Must respond quickly (<4 seconds)

2. **Liveness Probe**:
   - Checks if container is still running
   - Restarts container if failing
   - Should not include external dependencies

3. **Readiness Probe**:
   - Checks if container is ready to serve traffic
   - Can include dependency checks
   - Path: `/health/ready`

**Implementation**:
```python
@app.get('/health/live')
async def health_live():
    """Liveness probe - basic health check"""
    return {'status': 'healthy', 'timestamp': time.time()}

@app.get('/health/ready')
async def health_ready():
    """Readiness probe - includes dependency checks"""
    checks = {'status': 'healthy'}
    
    # Optional: Check database (but handle failures gracefully)
    try:
        # Quick database check
        checks['database'] = 'connected'
    except Exception:
        checks['database'] = 'disconnected'
        # Don't fail in Cloud Run if optional services unavailable
        if not settings.is_cloud_run:
            checks['status'] = 'unhealthy'
    
    return checks
```

## Quick Fixes for Current Issues

### 1. Dependency Conflicts (typing-extensions)

**Problem**: Multiple packages require different versions of `typing-extensions`, causing pip resolution failure.

**Solution**:
- Use `typing-extensions>=4.11,<5` in requirements.txt
- Use the optimized `requirements-cloudrun.txt` for deployment

### 2. Duplicate Dependencies

**Problem**: Duplicate `httpx==0.27.0` entries in requirements.txt cause build failures.

**Solution**: Remove duplicate entries from requirements.txt (line 31).

### 3. Build Failures

**Problem**: Docker build fails due to dependency resolution issues.

**Solution**: Use the minimal `requirements-cloudrun.txt` file created specifically for Cloud Run deployment.

## Common Issues and Solutions

### Build Stage Issues

#### 1. Dependency Resolution Failures

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement typing-extensions==4.12.2
ERROR: pip's dependency resolver does not currently take into account all the packages
```

**Solutions**:
1. Check for duplicate dependencies in requirements.txt
2. Use flexible version constraints: `>=4.11,<5` instead of pinned versions
3. Use the minimal requirements-cloudrun.txt file
4. Clear Docker cache: `docker system prune -a`

#### 2. Docker Build Timeouts

**Symptoms**:
```
ERROR: timeout during docker build
```

**Solutions**:
1. Use multi-stage Docker builds
2. Install only production dependencies
3. Use `requirements-cloudrun.txt` instead of full requirements.txt
4. Increase Cloud Build timeout in cloudbuild.yaml

### Runtime Issues

#### 1. Pydantic Validation During Startup

**Symptoms**:
```
pydantic_core._pydantic_core.ValidationError: 2 validation errors for Settings
redis_url
  Value error, Redis URL must be provided and start with redis://
jwt_secret_key  
  Value error, JWT secret key must be at least 32 characters long
```

**Solutions**:
1. **Cloud Run Detection**: Application automatically detects Cloud Run environment
2. **Redis Fallback**: Uses `redis://localhost:6379/0` when Redis not configured in Cloud Run
3. **Required Secrets**: Ensure `DATABASE_URL` and `JWT_SECRET_KEY` are properly set
4. **Startup Error Handling**: Application includes fallback configuration for Cloud Run

#### 2. Port Configuration

**Symptoms**:
```
Cloud Run error: Container failed to start
The container failed to start listening on the port defined by PORT environment variable
```

**Solutions**:
1. Ensure the app reads PORT from environment: `int(os.getenv('PORT', 8080))`
2. Use `0.0.0.0` as the host, not `localhost`
3. Verify the Dockerfile exposes port 8080
4. Check uvicorn startup command uses correct port

#### 3. Startup Timeout

**Symptoms**:
```
Cloud Run error: Startup probe failed
The container instance did not start successfully after 240 seconds
```

**Solutions**:
1. Add a basic `/health` endpoint that responds quickly
2. Optimize imports and startup code
3. Use lazy loading for heavy dependencies
4. Increase timeout in Cloud Run configuration

#### 4. Database Connection and Import Failures

**Symptoms**:
```
ModuleNotFoundError: No module named 'asyncpg'
ImportError: cannot import name 'get_async_session_maker' from 'database.db_setup'
RuntimeError: Async database session maker not available
```

**Root Cause**:
- Database initialization happening at import time
- Missing asyncpg dependency in Docker container
- Import chain failure preventing application startup

**Solutions**:

1. **Test Database Dependencies Locally**:
   ```bash
   # Test asyncpg installation
   docker run --rm python:3.11-slim bash -c "
   apt-get update && apt-get install -y build-essential libpq-dev python3-dev &&
   pip install asyncpg>=0.29.0 &&
   python -c 'import asyncpg; print(\"asyncpg available\")'
   "
   
   # Test full database stack
   python -c "
   import asyncpg
   import psycopg
   from sqlalchemy.ext.asyncio import create_async_engine
   print('All database modules available')
   "
   ```

2. **Debug Import Chain**:
   ```bash
   # Test each import step
   python -c "from api.main import app; print('Main import successful')"
   python -c "from database.db_setup import get_async_session_maker; print('Database import successful')"
   python -c "from api.dependencies.auth import get_current_user; print('Auth import successful')"
   ```

3. **Verify Cloud Run Environment Detection**:
   ```python
   # Test Cloud Run detection
   import os
   is_cloud_run = bool(os.getenv('K_SERVICE') or os.getenv('CLOUD_RUN_JOB'))
   print(f'Cloud Run detected: {is_cloud_run}')
   print(f'K_SERVICE: {os.getenv("K_SERVICE")}')
   ```

4. **Test Database Initialization**:
   ```python
   # Test lazy database initialization
   from database.db_setup import get_async_session_maker
   session_maker = get_async_session_maker()
   print(f'Session maker available: {session_maker is not None}')
   ```

#### 5. Environment Variables and Settings Validation

**Symptoms**:
```
ValueError: Missing required environment variables: ['DATABASE_URL', 'JWT_SECRET_KEY']
ValidationError: Redis URL must be provided and start with redis://
ModuleNotFoundError: No module named 'asyncpg'
```

**Environment Variable Priority**:

1. **Required for All Environments**:
   - `DATABASE_URL`: PostgreSQL connection string
   - `JWT_SECRET_KEY`: At least 32 characters

2. **Optional in Cloud Run** (auto-fallback):
   - `REDIS_URL`: Uses `redis://localhost:6379/0` fallback
   - `GOOGLE_AI_API_KEY`: AI features disabled if missing

3. **Cloud Run Auto-Detection**:
   - `K_SERVICE`: Set by Cloud Run (used for environment detection)
   - `PORT`: Set to 8080 by Cloud Run
   - `ENVIRONMENT`: Set to 'production' in cloudbuild.yaml

**Solutions**:
1. Create all required secrets in Secret Manager
2. Use the updated cloudbuild.yaml with proper secret mounting
3. Verify Cloud Run service account has secret access
4. Test locally with same environment variables
5. **Test Database Dependencies**: Verify asyncpg is properly installed
6. **Check Import Chain**: Ensure all modules can be imported without errors

#### 6. Settings Initialization Errors

**Problem**: Application fails during settings initialization before reaching main logic.

**Symptoms**:
```
pydantic_core._pydantic_core.ValidationError: 2 validation errors for Settings
ModuleNotFoundError during settings import
ImportError in database initialization chain
```

**Solutions**:
1. **Cloud Run Fallback**: Application includes error handling for Cloud Run
2. **Graceful Degradation**: Optional services (Redis, AI) can be unavailable
3. **Startup Logging**: Detailed logs show which configuration path is taken
4. **Environment Detection**: Automatic Cloud Run vs development environment detection
5. **Database Initialization**: Defer database setup to runtime, not import time
6. **Dependency Verification**: Ensure all required modules are properly installed

**Debug Settings Initialization**:
```python
# Test settings loading with Cloud Run simulation
import os
os.environ['K_SERVICE'] = 'test-service'  # Simulate Cloud Run
os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'
os.environ['JWT_SECRET_KEY'] = 'a' * 32

try:
    from config.settings import Settings
    settings = Settings()
    print('✅ Settings loaded successfully!')
    print(f'Cloud Run detected: {settings.is_cloud_run}')
    print(f'Redis URL: {settings.redis_url}')
except Exception as e:
    print(f'❌ Settings initialization failed: {e}')
    import traceback
    traceback.print_exc()
```

### Health Check Failures

#### Startup Probe Failures

**Problem**: Cloud Run startup probes fail, preventing successful deployment.

**Symptoms**:
```
Startup probe failed
The container instance did not start successfully after 240 seconds
Health check timeout
Container failed to respond to health check
```

**Root Cause**:
- Health endpoint not responding within 4-second timeout
- Database initialization blocking health endpoint
- Import errors preventing application startup
- Missing asyncpg causing import chain failure

**Solutions**:

1. **Implement Fast Health Endpoints**:
   ```python
   @app.get('/health/live')
   async def health_live():
       """Liveness probe - basic health check without dependencies"""
       return {'status': 'healthy', 'timestamp': time.time()}

   @app.get('/health/ready')
   async def health_ready():
       """Readiness probe - includes dependency checks"""
       checks = {'status': 'healthy', 'timestamp': time.time()}
       
       # Test database availability (but don't fail in Cloud Run)
       try:
           from database.db_setup import test_database_connection
           if test_database_connection():
               checks['database'] = 'connected'
           else:
               checks['database'] = 'disconnected'
               # Don't fail readiness in Cloud Run if database temporarily unavailable
               is_cloud_run = bool(os.getenv('K_SERVICE'))
               if not is_cloud_run:
                   checks['status'] = 'unhealthy'
       except Exception as e:
           checks['database'] = f'error: {str(e)}'
           checks['status'] = 'degraded'  # Allow startup even with database issues
       
       return checks
   ```

2. **Debug Health Check Issues**:
   ```bash
   # Test health endpoints locally
   curl -w "Time: %{time_total}s\n" http://localhost:8080/health/live
   curl -w "Time: %{time_total}s\n" http://localhost:8080/health/ready
   
   # Test with timeout simulation
   timeout 4s curl http://localhost:8080/health/live || echo "Health check timeout"
   
   # Test in Cloud Run environment simulation
   docker run -p 8080:8080 -e K_SERVICE=test -e PORT=8080 ruleiq-backend &
   sleep 10
   curl http://localhost:8080/health/live
   ```

3. **Optimize Startup Time**:
   ```python
   # Defer heavy imports and initialization
   @app.on_event("startup")
   async def startup_event():
       """Initialize services after application startup"""
       try:
           # Initialize database connections after startup
           from database.db_setup import init_db
           if not init_db():
               logger.warning("Database initialization failed - continuing with degraded functionality")
       except ImportError as e:
           logger.warning(f"Database modules not available: {e}")
   ```

#### Basic Health Endpoint

**Requirement**: Cloud Run requires a health endpoint that responds within 4 seconds.

**Implementation**:
```python
@app.get('/health')
async def health_check():
    """Basic health check - must respond quickly"""
    return {'status': 'healthy', 'timestamp': time.time()}
```

**Common Issues**:
- Database connectivity checks in health endpoint (use /health/ready instead)
- External API calls in health endpoint
- Heavy computations during health check
- Import errors preventing endpoint registration
- Missing asyncpg causing application startup failure

**Debug Health Check Failures**:
```bash
# Test health endpoint response time
time curl http://localhost:8080/health

# Test with Cloud Run timeout simulation
timeout 4s curl http://localhost:8080/health || echo "TIMEOUT - Health check too slow"

# Check if application is even starting
docker logs <container_id> | grep -E "(health|startup|error|import)"

# Test minimal health endpoint
curl -v http://localhost:8080/health/live
```

### Secret Management Issues

#### Missing Secrets

**Symptoms**:
```
ERROR: Secret "DATABASE_URL" not found
```

**Solutions**:
1. Create the secret:
   ```bash
   echo -n "postgresql://..." | gcloud secrets create DATABASE_URL --data-file=-
   ```
2. Grant Cloud Run access to the secret:
   ```bash
   gcloud secrets add-iam-policy-binding DATABASE_URL \
     --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

### Performance Issues

#### Cold Starts

**Problem**: First request takes too long (>10 seconds)

**Solutions**:
1. Set minimum instances to 1: `--min-instances=1`
2. Use `--startup-cpu-boost` flag
3. Optimize imports and initialization code
4. Use execution environment gen2: `--execution-environment=gen2`

#### Memory Issues

**Symptoms**:
```
Container terminated due to memory limit
```

**Solutions**:
1. Increase memory allocation: `--memory=2Gi`
2. Optimize memory usage in code
3. Use connection pooling for database
4. Implement proper cleanup in shutdown handlers

## Cloud Run Specific Configuration

### Environment Detection

The application automatically detects Cloud Run environment using:
```python
@property
def is_cloud_run(self) -> bool:
    """Check if running in Google Cloud Run environment."""
    return os.getenv('K_SERVICE') is not None or os.getenv('CLOUD_RUN_JOB') is not None
```

### Redis Configuration in Cloud Run

**Development/Production**: Redis URL required and validated
**Cloud Run**: Redis URL optional with automatic fallback

```python
# Automatic fallback in Cloud Run
redis_url: str = Field(
    default_factory=lambda: (
        get_secret_or_env('redis_url', 'REDIS_URL') or 
        ('redis://localhost:6379/0' if is_cloud_run else '')
    )
)
```

### Startup Sequence Optimization

1. **Settings Validation**: Cloud Run specific validation rules
2. **Error Handling**: Graceful fallback for missing optional services  
3. **Logging**: Detailed startup logging for troubleshooting
4. **Health Checks**: Separate endpoints for different probe types

## Deployment Checklist

Before deploying, ensure:

### Configuration
- [ ] No duplicate dependencies in requirements.txt
- [ ] Using `typing-extensions>=4.11,<5` for compatibility
- [ ] Created `requirements-cloudrun.txt` with minimal dependencies
- [ ] Dockerfile uses optimized requirements file

### Secrets and Environment
- [ ] `DATABASE_URL` secret created and accessible
- [ ] `JWT_SECRET_KEY` secret created (32+ characters)
- [ ] `REDIS_URL` secret created (optional for Cloud Run)
- [ ] `GOOGLE_AI_API_KEY` secret created (optional)
- [ ] Cloud Run service account has `secretmanager.secretAccessor` role
- [ ] Environment variables set in cloudbuild.yaml

### Health and Startup
- [ ] `/health/live` endpoint responds quickly (<4 seconds)
- [ ] `/health/ready` endpoint includes dependency checks
- [ ] Port configuration reads from PORT environment variable
- [ ] Application handles Cloud Run environment detection
- [ ] Startup error handling for missing optional services

### Build and Deploy
- [ ] Cloud Build timeout is sufficient (>20 minutes)
- [ ] Service name matches existing deployment ('ruleiq')
- [ ] Region matches existing deployment ('europe-west2')
- [ ] All secrets referenced in cloudbuild.yaml

## Testing Locally

Test the Docker container locally before deployment:

```bash
# Build the container
docker build -t ruleiq-backend .

# Test with minimal Cloud Run environment
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e K_SERVICE=test-service \
  -e ENVIRONMENT=production \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e JWT_SECRET_KEY="$(openssl rand -base64 32)" \
  ruleiq-backend

# Test with full environment (including optional services)
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e DATABASE_URL="postgresql://..." \
  -e JWT_SECRET_KEY="your-32-char-key" \
  -e REDIS_URL="redis://localhost:6379/0" \
  -e GOOGLE_AI_API_KEY="AIza..." \
  ruleiq-backend

# Test health endpoints
curl http://localhost:8080/health/live
curl http://localhost:8080/health/ready

# Test Cloud Run environment detection
curl http://localhost:8080/api/v1/health | jq '.environment'
```

### Local Testing with Cloud Run Emulation

```bash
# Install Cloud Run emulator
gcloud components install cloud-run-proxy

# Test with actual secrets
gcloud run services proxy ruleiq --port=8080 --region=europe-west2
```

## Useful Commands

### View Logs
```bash
# Recent logs (updated service name and region)
gcloud run logs read --service=ruleiq --region=europe-west2

# Stream logs for real-time troubleshooting
gcloud run logs tail --service=ruleiq --region=europe-west2

# Filter for specific errors
gcloud run logs read --service=ruleiq --region=europe-west2 --filter="severity>=ERROR"

# Look for Pydantic validation errors
gcloud run logs read --service=ruleiq --region=europe-west2 --filter="textPayload:ValidationError"
```

### Check Service Status
```bash
# Service details
gcloud run services describe ruleiq --region=europe-west2

# Check current revision
gcloud run revisions list --service=ruleiq --region=europe-west2 --limit=5

# Check secret access
gcloud run services describe ruleiq --region=europe-west2 --format="value(spec.template.spec.template.spec.containers[0].env[].valueFrom.secretKeyRef)"
```

### Debug Secrets and Environment
```bash
# List available secrets
gcloud secrets list

# Check secret versions
gcloud secrets versions list DATABASE_URL
gcloud secrets versions list JWT_SECRET_KEY
gcloud secrets versions list REDIS_URL

# Test secret access (be careful with sensitive data)
gcloud secrets versions access latest --secret="DATABASE_URL" | head -c 20

# Check service account permissions
gcloud projects get-iam-policy $(gcloud config get-value project) \
  --flatten="bindings[].members" \
  --filter="bindings.members:*compute@developer.gserviceaccount.com"
```

### Rollback Deployment
```bash
# List revisions with traffic allocation
gcloud run revisions list --service=ruleiq --region=europe-west2

# Route traffic to previous revision
gcloud run services update-traffic ruleiq \
  --to-revisions=PREVIOUS_REVISION=100 --region=europe-west2

# Quick rollback to previous working revision
gcloud run services update-traffic ruleiq \
  --to-latest --region=europe-west2
```

### Debug Container Locally
```bash
# Run with shell access for debugging
docker run -it --entrypoint /bin/bash ruleiq-backend

# Check installed packages and versions
pip list | grep asyncpg
pip list | grep psycopg
pip list | grep typing-extensions
pip list | grep pydantic

# Test database dependencies
python -c "
try:
    import asyncpg
    print('✅ asyncpg available')
    print(f'asyncpg version: {asyncpg.__version__}')
except ImportError as e:
    print(f'❌ asyncpg not available: {e}')

try:
    import psycopg
    print('✅ psycopg available')
except ImportError as e:
    print(f'❌ psycopg not available: {e}')
"

# Test database setup import chain
python -c "
try:
    from database.db_setup import get_async_session_maker
    print('✅ Database setup import successful')
    
    session_maker = get_async_session_maker()
    print(f'✅ Session maker available: {session_maker is not None}')
except ImportError as e:
    print(f'❌ Database setup import failed: {e}')
    import traceback
    traceback.print_exc()
"

# Test settings validation manually
python -c "
import os
os.environ['K_SERVICE'] = 'test'  # Simulate Cloud Run
os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'
os.environ['JWT_SECRET_KEY'] = 'a' * 32

try:
    from config.settings import Settings
    settings = Settings()
    print('✅ Settings loaded successfully!')
    print(f'Cloud Run detected: {settings.is_cloud_run}')
    print(f'Redis URL: {settings.redis_url}')
except Exception as e:
    print(f'❌ Settings validation failed: {e}')
    import traceback
    traceback.print_exc()
"

# Test application import and startup
python -c "
try:
    from api.main import app
    print('✅ Application import successful')
except ImportError as e:
    print(f'❌ Application import failed: {e}')
    import traceback
    traceback.print_exc()
"

# Test health endpoints
python -c "
import os
os.environ['K_SERVICE'] = 'test'
os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'
os.environ['JWT_SECRET_KEY'] = 'a' * 32

try:
    from api.main import app
    print('✅ Health endpoints should be available')
    # Test that the app can be created without errors
except Exception as e:
    print(f'❌ Health endpoint test failed: {e}')
    import traceback
    traceback.print_exc()
"
```

### Database-Specific Debugging Commands

```bash
# Test asyncpg installation and functionality
python -c "
import asyncpg
import asyncio

async def test_asyncpg():
    try:
        # Test basic asyncpg functionality (without actual connection)
        print(f'asyncpg version: {asyncpg.__version__}')
        print('✅ asyncpg module is functional')
        return True
    except Exception as e:
        print(f'❌ asyncpg test failed: {e}')
        return False

result = asyncio.run(test_asyncpg())
print(f'asyncpg test result: {result}')
"

# Test database URL parsing
python -c "
from database.db_setup import DatabaseConfig
import os

os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost:5432/db'

try:
    original, sync_url, async_url = DatabaseConfig.get_database_urls()
    print(f'✅ Database URL parsing successful')
    print(f'Original: {original}')
    print(f'Sync: {sync_url}')
    print(f'Async: {async_url}')
except Exception as e:
    print(f'❌ Database URL parsing failed: {e}')
"

# Test database engine creation (without connection)
python -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost:5432/db'
os.environ['K_SERVICE'] = 'test'  # Simulate Cloud Run

try:
    from database.db_setup import DatabaseConfig
    from sqlalchemy.ext.asyncio import create_async_engine
    
    _, _, async_url = DatabaseConfig.get_database_urls()
    engine_kwargs = DatabaseConfig.get_engine_kwargs(is_async=True)
    
    # Test engine creation (this should work even without database connection)
    engine = create_async_engine(async_url, **engine_kwargs)
    print('✅ Async engine creation successful')
    
except ImportError as e:
    print(f'❌ Engine creation failed due to missing module: {e}')
except Exception as e:
    print(f'❌ Engine creation failed: {e}')
"
```

### Advanced Debugging

```bash
# Check Cloud Run service configuration
gcloud run services describe ruleiq --region=europe-west2 \
  --format="export" > current-service-config.yaml

# Compare with working configuration
gcloud run services describe ruleiq --region=europe-west2 \
  --format="value(spec.template.spec.template.spec.containers[0].env[].name)"

# Test container startup locally with exact Cloud Run environment
docker run --rm \
  -e K_SERVICE=ruleiq \
  -e PORT=8080 \
  -e ENVIRONMENT=production \
  -e DATABASE_URL="$(gcloud secrets versions access latest --secret=DATABASE_URL)" \
  -e JWT_SECRET_KEY="$(gcloud secrets versions access latest --secret=JWT_SECRET_KEY)" \
  -p 8080:8080 \
  ruleiq-backend

# Debug specific database issues
docker run --rm -it \
  -e K_SERVICE=ruleiq \
  -e DATABASE_URL="postgresql://test:test@localhost:5432/test" \
  -e JWT_SECRET_KEY="$(openssl rand -base64 32)" \
  --entrypoint /bin/bash \
  ruleiq-backend \
  -c "
  echo 'Testing database dependencies...'
  python -c 'import asyncpg; print(\"asyncpg OK\")'
  python -c 'import psycopg; print(\"psycopg OK\")'
  python -c 'from database.db_setup import get_async_session_maker; print(\"Database setup OK\")'
  python -c 'from api.main import app; print(\"Application import OK\")'
  echo 'All tests completed'
  "

# Test build process step by step
docker build --target=<stage> -t debug-build .
docker run --rm -it debug-build /bin/bash

# Check for missing dependencies in built image
docker run --rm ruleiq-backend pip list | grep -E "(asyncpg|psycopg|sqlalchemy)"

# Test import chain step by step
docker run --rm ruleiq-backend python -c "
import sys
modules_to_test = [
    'asyncpg',
    'psycopg', 
    'sqlalchemy',
    'sqlalchemy.ext.asyncio',
    'database.db_setup',
    'api.dependencies.auth',
    'api.routers.ai_assessments',
    'api.main'
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError as e:
        print(f'❌ {module}: {e}')
        break
"
```

### Database Connection Testing

```bash
# Test database connectivity without asyncpg
docker run --rm \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  ruleiq-backend \
  python -c "
import psycopg
from urllib.parse import urlparse

db_url = 'postgresql://user:pass@host:5432/db'  # Replace with actual URL
parsed = urlparse(db_url)

try:
    # Test sync connection (should work with psycopg)
    import psycopg
    print('✅ psycopg available for sync connections')
except ImportError:
    print('❌ psycopg not available')

try:
    # Test async connection (requires asyncpg)
    import asyncpg
    print('✅ asyncpg available for async connections')
except ImportError:
    print('❌ asyncpg not available - async operations will fail')
"

# Test database initialization in Cloud Run mode
docker run --rm \
  -e K_SERVICE=test-service \
  -e DATABASE_URL="postgresql://test:test@localhost:5432/test" \
  -e JWT_SECRET_KEY="$(openssl rand -base64 32)" \
  ruleiq-backend \
  python -c "
import os
print(f'Cloud Run detected: {bool(os.getenv(\"K_SERVICE\"))}')

try:
    from database.db_setup import get_async_session_maker
    session_maker = get_async_session_maker()
    
    if session_maker is None:
        print('⚠️  Async session maker is None (expected in Cloud Run with missing asyncpg)')
    else:
        print('✅ Async session maker available')
        
except Exception as e:
    print(f'❌ Database setup failed: {e}')
"
```

## Best Practices

### Configuration Management
1. **Environment Detection**: Use automatic Cloud Run detection for configuration
2. **Graceful Degradation**: Make optional services truly optional in Cloud Run
3. **Secret Management**: Use Google Secret Manager for all sensitive data
4. **Validation Strategy**: Implement environment-specific validation rules

### Deployment Strategy
5. **Minimal Requirements**: Use `requirements-cloudrun.txt` for Cloud Run deployments
6. **Test Locally**: Always test with Cloud Run environment variables locally
7. **Monitor Startup**: Watch logs during deployment for validation errors
8. **Health Checks**: Implement separate liveness and readiness probes

### Performance Optimization
9. **Startup CPU Boost**: Enable `--startup-cpu-boost` for faster cold starts
10. **Execution Environment**: Use `gen2` for better performance
11. **Resource Limits**: Set appropriate memory and CPU limits
12. **Connection Pooling**: Use database connection pooling

### Error Handling
13. **Graceful Shutdown**: Implement proper shutdown handlers
14. **Startup Error Handling**: Handle missing optional dependencies gracefully
15. **Logging Strategy**: Use structured logging with appropriate levels
16. **Rollback Plan**: Always have a rollback strategy ready

### Security
17. **Stateless Containers**: Don't rely on local filesystem
18. **Least Privilege**: Grant minimal required permissions to service accounts
19. **Secret Rotation**: Regularly rotate secrets and API keys
20. **Environment Isolation**: Use different secrets for different environments

## Common Error Messages and Solutions

### "ModuleNotFoundError: No module named 'asyncpg'"
- **Cause**: asyncpg not properly installed in Docker container or missing build dependencies
- **Solution**: 
  1. Add build dependencies to Dockerfile: `build-essential libpq-dev python3-dev`
  2. Verify installation: `RUN python -c "import asyncpg; print('asyncpg OK')"`
  3. Use correct requirements: `asyncpg>=0.29.0,<1.0.0`
  4. Check import chain: test each module import step by step

### "ValidationError: 2 validation errors for Settings"
- **Cause**: Missing or invalid `DATABASE_URL` or `JWT_SECRET_KEY`
- **Solution**: Create secrets in Secret Manager and verify access permissions

### "Container failed to start and listen on port 8080"
- **Cause**: Application not binding to correct port or host, or import errors preventing startup
- **Solution**: 
  1. Use `PORT` environment variable and bind to `0.0.0.0`
  2. Fix import chain issues (especially asyncpg)
  3. Test application import: `python -c "from api.main import app"`

### "Startup probe failed"
- **Cause**: Health endpoint not responding within timeout, often due to database initialization blocking startup
- **Solution**: 
  1. Implement fast `/health/live` endpoint without database dependencies
  2. Defer database initialization to runtime, not import time
  3. Fix asyncpg import issues that prevent application startup

### "Secret not found" or "Permission denied"
- **Cause**: Secret doesn't exist or service account lacks access
- **Solution**: Create secret and grant `secretmanager.secretAccessor` role

### "Redis URL must be provided and start with redis://"
- **Cause**: Redis validation failing in Cloud Run
- **Solution**: Update to latest settings.py with Cloud Run detection

### "ImportError: cannot import name 'get_async_session_maker'"
- **Cause**: Database setup module failing to import due to missing asyncpg
- **Solution**:
  1. Fix asyncpg installation in Docker build
  2. Add error handling for missing asyncpg in Cloud Run
  3. Use lazy initialization instead of eager import-time initialization

### "RuntimeError: Async database session maker not available"
- **Cause**: Database initialization failed, often due to missing asyncpg
- **Solution**:
  1. Check asyncpg installation: `python -c "import asyncpg"`
  2. Verify Cloud Run environment detection
  3. Use graceful degradation for missing async database support

### "Failed building wheel for asyncpg"
- **Cause**: Missing build dependencies for compiling asyncpg
- **Solution**:
  1. Install build tools: `build-essential libpq-dev python3-dev gcc g++`
  2. Upgrade pip and setuptools before installing packages
  3. Use verbose pip install to debug build issues

## Getting Help

If issues persist after following this guide:

### Immediate Steps
1. **Check Cloud Run logs** for detailed error messages
2. **Verify secrets** are created and accessible
3. **Test container locally** with exact Cloud Run environment
4. **Review service configuration** against working deployments

### Debugging Checklist
- [ ] All required secrets exist in Secret Manager
- [ ] Service account has `secretmanager.secretAccessor` role
- [ ] Application detects Cloud Run environment (`K_SERVICE` set)
- [ ] Health endpoints respond quickly
- [ ] Port configuration uses `PORT` environment variable
- [ ] No Pydantic validation errors in startup logs

### Advanced Troubleshooting
- Compare current deployment with previous working version
- Test with minimal environment (only required secrets)
- Check for recent changes in dependencies or configuration
- Verify Cloud Run service limits and quotas

### External Resources
- Check project's GitHub issues for similar problems
- Review Google Cloud Run status page for service issues
- Consult team documentation for environment-specific configurations

## References

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Run Troubleshooting Guide](https://cloud.google.com/run/docs/troubleshooting)
- [Container Runtime Contract](https://cloud.google.com/run/docs/container-contract)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
