# Google Cloud Run Deployment Troubleshooting Guide

## Overview
This guide helps resolve common issues when deploying the RuleIQ backend to Google Cloud Run, with a focus on dependency conflicts and build failures.

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

#### 1. Port Configuration

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

#### 2. Startup Timeout

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

#### 3. Environment Variables

**Symptoms**:
```
ValueError: Missing required environment variables: ['DATABASE_URL', 'JWT_SECRET_KEY']
```

**Solutions**:
1. Create secrets in Secret Manager:
   ```bash
   echo -n "your-database-url" | gcloud secrets create DATABASE_URL --data-file=-
   echo -n "your-jwt-key" | gcloud secrets create JWT_SECRET_KEY --data-file=-
   ```
2. Reference secrets in cloudbuild.yaml
3. Verify secrets are properly mounted in Cloud Run

### Health Check Failures

#### Basic Health Endpoint

**Requirement**: Cloud Run requires a health endpoint that responds within 4 seconds.

**Implementation**:
```python
@app.get('/health')
async def health_check():
    return {'status': 'healthy', 'timestamp': time.time()}
```

**Common Issues**:
- Database connectivity checks in health endpoint (use /health/ready instead)
- External API calls in health endpoint
- Heavy computations during health check

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

## Deployment Checklist

Before deploying, ensure:

- [ ] No duplicate dependencies in requirements.txt
- [ ] Using `typing-extensions>=4.11,<5` for compatibility
- [ ] Created `requirements-cloudrun.txt` with minimal dependencies
- [ ] Dockerfile uses optimized requirements file
- [ ] Basic `/health` endpoint exists and responds quickly
- [ ] Port configuration reads from PORT environment variable
- [ ] All required secrets created in Secret Manager
- [ ] Cloud Build timeout is sufficient (>20 minutes)
- [ ] Service account has necessary permissions

## Testing Locally

Test the Docker container locally before deployment:

```bash
# Build the container
docker build -t ruleiq-backend .

# Run with environment variables
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e DATABASE_URL="postgresql://..." \
  -e JWT_SECRET_KEY="your-key" \
  ruleiq-backend

# Test health endpoint
curl http://localhost:8080/health
```

## Useful Commands

### View Logs
```bash
# Recent logs
gcloud run logs read --service=ruleiq-backend --region=us-central1

# Stream logs
gcloud run logs tail --service=ruleiq-backend --region=us-central1
```

### Check Service Status
```bash
gcloud run services describe ruleiq-backend --region=us-central1
```

### Rollback Deployment
```bash
# List revisions
gcloud run revisions list --service=ruleiq-backend --region=us-central1

# Route traffic to previous revision
gcloud run services update-traffic ruleiq-backend \
  --to-revisions=PREVIOUS_REVISION=100 --region=us-central1
```

### Debug Container Locally
```bash
# Run with shell access
docker run -it --entrypoint /bin/bash ruleiq-backend

# Check installed packages
pip list | grep typing-extensions
```

## Best Practices

1. **Always use minimal requirements** for Cloud Run deployments
2. **Test locally** before deploying
3. **Monitor logs** during deployment
4. **Use health checks** appropriately
5. **Implement graceful shutdown** handlers
6. **Set resource limits** appropriately
7. **Use Secret Manager** for sensitive data
8. **Enable startup CPU boost** for faster cold starts
9. **Use execution environment gen2** for better performance
10. **Keep containers stateless** - don't rely on local filesystem

## Getting Help

If issues persist:

1. Check Cloud Run logs for detailed error messages
2. Verify all environment variables and secrets are set
3. Test the container locally with the same configuration
4. Review the Google Cloud Run documentation
5. Check the project's GitHub issues for similar problems

## References

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Run Troubleshooting Guide](https://cloud.google.com/run/docs/troubleshooting)
- [Container Runtime Contract](https://cloud.google.com/run/docs/container-contract)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)