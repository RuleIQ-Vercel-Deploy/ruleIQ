# 🚀 ruleIQ Vercel Deployment Guide

This comprehensive guide will walk you through deploying the ruleIQ compliance automation platform to Vercel's serverless infrastructure.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Environment Variables](#environment-variables)
4. [Database Setup](#database-setup)
5. [Deployment Process](#deployment-process)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Performance Optimization](#performance-optimization)
9. [Monitoring](#monitoring)
10. [Security Best Practices](#security-best-practices)
11. [Cost Optimization](#cost-optimization)

## Prerequisites

Before deploying to Vercel, ensure you have:

- **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
- **GitHub Account**: For automatic deployments
- **PostgreSQL Database**: We recommend [Neon](https://neon.tech) or [Supabase](https://supabase.com)
- **Node.js**: Version 18+ installed locally
- **Python**: Version 3.11 installed locally
- **Vercel CLI**: Install with `npm i -g vercel`

## Quick Start

Deploy ruleIQ in 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/your-org/ruleiq.git
cd ruleiq

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment template
cp .vercel.env.example .env

# 4. Configure environment variables
# Edit .env with your database URL and API keys

# 5. Run deployment check
python scripts/vercel_deploy_check.py

# 6. Test locally
python scripts/test_vercel_locally.py

# 7. Deploy to Vercel
vercel --prod
```

## Environment Variables

### Required Variables

Set these in the Vercel Dashboard under **Settings → Environment Variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db?sslmode=require` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Generate with `openssl rand -hex 32` |
| `SECRET_KEY` | Application secret key | Generate with `openssl rand -hex 32` |
| `ENVIRONMENT` | Deployment environment | `production` |

### Optional Services

Enable additional features by setting these variables:

| Variable | Service | Purpose |
|----------|---------|---------|
| `GOOGLE_AI_API_KEY` | Google AI (Gemini) | AI-powered assessments |
| `OPENAI_API_KEY` | OpenAI | Alternative AI provider |
| `REDIS_URL` | Redis | Caching and rate limiting |
| `NEO4J_URI` | Neo4j | Knowledge graph features |
| `STRIPE_SECRET_KEY` | Stripe | Payment processing |
| `SENDGRID_API_KEY` | SendGrid | Email notifications |

### Setting Variables in Vercel

1. Go to your project in Vercel Dashboard
2. Navigate to **Settings → Environment Variables**
3. Add each variable with appropriate values
4. Select environments (Production/Preview/Development)
5. Click **Save**

## Database Setup

### Using Neon (Recommended)

1. **Create Neon Account**: Sign up at [neon.tech](https://neon.tech)
2. **Create Database**:
   ```sql
   CREATE DATABASE ruleiq;
   ```
3. **Get Connection String**: Copy from Neon dashboard
4. **Configure for Serverless**:
   ```
   postgresql://user:pass@host/ruleiq?sslmode=require&connect_timeout=10
   ```
5. **Run Migrations**:
   ```bash
   alembic upgrade head
   ```

### Using Supabase

1. **Create Supabase Project**: Sign up at [supabase.com](https://supabase.com)
2. **Get Database URL**: From project settings
3. **Enable Connection Pooling**: Use the pooler URL for serverless
4. **Set in Vercel**: Add DATABASE_URL to environment variables

### Database Optimization Tips

- Use connection pooling URLs for serverless
- Enable SSL mode (`sslmode=require`)
- Set appropriate timeouts (`connect_timeout=10`)
- Consider using Vercel Postgres for tighter integration

### Serverless Database Connection Management

The ruleIQ API uses a serverless-optimized database connection approach implemented in `database/serverless_db.py`:

**Approach**: Keep `api/index.py` as handler with serverless DB lifecycle

**Key Features**:
- **NullPool Strategy**: Uses SQLAlchemy's NullPool to prevent connection pooling issues in serverless
- **Per-Request Cleanup**: Automatic connection disposal after each request via middleware
- **Fast Health Checks**: Quick database connectivity checks (<200ms) for readiness endpoints
- **Environment Detection**: Automatically switches between serverless (NullPool) and local (standard pooling) modes

**Implementation Details**:

1. **Database Module** (`database/serverless_db.py`):
   - Provides `get_db_session()` for dependency injection
   - Implements `test_database_connection()` for health checks
   - Includes `cleanup_connections()` for request cleanup

2. **API Handler** (`api/index.py`):
   - Imports serverless DB helpers
   - **Runtime Override**: Automatically routes all `database.db_setup.get_db_session` imports to the serverless version when running on Vercel (detected via VERCEL environment variables)
   - Middleware automatically cleans up connections after each request
   - Health endpoints use quick connectivity checks

3. **Unified Session Provider**:
   - All routers and services continue using their existing `from database.db_setup import get_db_session` imports
   - The runtime override in `api/index.py` transparently switches to serverless sessions on Vercel
   - No code changes required in routers or services
   - Local development continues using pooled connections for better performance

4. **Connection Lifecycle**:
   ```python
   # Request starts
   → Middleware processes request
   → DB session created on-demand via get_db_session()
   → Request processing
   → Response sent
   → cleanup_connections() called automatically
   # Request ends - no lingering connections
   ```

**Performance Benefits**:
- Zero connection accumulation across requests
- Minimal cold start impact
- Reliable connection management
- No connection pool exhaustion issues

## Deployment Process

### Method 1: GitHub Integration (Recommended)

1. **Connect GitHub**:
   - In Vercel Dashboard, click **New Project**
   - Import your GitHub repository
   - Vercel auto-detects Python project

2. **Configure Project**:
   - Framework Preset: **Other**
   - Root Directory: `.` (or your project root)
   - Build Command: `pip install -r requirements.txt`

3. **Set Environment Variables**:
   - Add all required variables
   - Use different values for Production/Preview

4. **Deploy**:
   - Click **Deploy**
   - Vercel builds and deploys automatically

5. **Automatic Deployments**:
   - Push to main branch triggers production deployment
   - Pull requests create preview deployments

### Method 2: Vercel CLI

1. **Login to Vercel**:
   ```bash
   vercel login
   ```

2. **Link Project**:
   ```bash
   vercel link
   ```

3. **Deploy to Preview**:
   ```bash
   vercel
   ```

4. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

5. **Check Deployment**:
   ```bash
   vercel ls
   vercel inspect [deployment-url]
   ```

### Method 3: Manual Upload

1. **Build Project**:
   ```bash
   pip install -r requirements.txt -t .
   ```

2. **Create Deployment**:
   - Go to Vercel Dashboard
   - Drag and drop project folder
   - Configure environment variables

## Testing

### Local Testing

Test the application locally with Vercel-like environment:

```bash
# Run comprehensive local tests
python scripts/test_vercel_locally.py

# Check deployment readiness
python scripts/vercel_deploy_check.py
```

### Test Endpoints

After deployment, test critical endpoints:

```bash
# Health check
curl https://your-app.vercel.app/api/health

# Readiness check
curl https://your-app.vercel.app/api/ready

# API Documentation
open https://your-app.vercel.app/api/docs
```

### Load Testing

Test performance under load:

```bash
# Install artillery
npm install -g artillery

# Run load test
artillery quick --count 10 --num 100 https://your-app.vercel.app/api/health
```

## Troubleshooting

### Common Issues and Solutions

#### 1. **Cold Start Timeouts**

**Problem**: Function times out on first request
**Solution**:
- Increase `maxDuration` in vercel.json (up to 60s)
- Optimize imports in vercel_handler.py
- Use Vercel Edge Functions for critical paths

#### 2. **Database Connection Errors**

**Problem**: "connection pool exhausted" or timeout errors
**Solution**:
- Use serverless-optimized connection URL
- Implement connection pooling with NullPool
- Add retry logic for transient failures

#### 3. **Memory Limit Exceeded**

**Problem**: Function runs out of memory
**Solution**:
- Increase memory in vercel.json (up to 3008 MB)
- Optimize large dependencies
- Use lazy loading for heavy modules

#### 4. **Import Errors**

**Problem**: Module not found errors
**Solution**:
- Ensure all dependencies in requirements.txt
- Check Python version compatibility (3.11)
- Verify package names and versions

#### 5. **Environment Variable Issues**

**Problem**: Missing or incorrect environment variables
**Solution**:
- Double-check variable names in Vercel Dashboard
- Use correct environment (Production/Preview)
- Verify variable values don't contain quotes

### Debug Commands

```bash
# View deployment logs
vercel logs [deployment-url]

# Check function logs
vercel logs --follow

# Inspect deployment
vercel inspect [deployment-url]

# List all deployments
vercel ls

# Remove deployment
vercel rm [deployment-url]
```

## Performance Optimization

### 1. **Optimize Cold Starts**

- Minimize dependencies
- Use lazy imports for heavy modules
- Enable Vercel Edge Caching
- Consider using Vercel Edge Functions

### 2. **Reduce Bundle Size**

```bash
# Check bundle size
du -sh api/

# Remove unused dependencies
pip uninstall unused-package

# Use production dependencies only
pip install --no-dev -r requirements.txt
```

### 3. **Implement Caching**

- Use Vercel Edge Cache for static responses
- Implement Redis caching for dynamic data
- Add Cache-Control headers

### 4. **Database Optimization**

- Use connection pooling
- Implement query caching
- Add database indexes
- Use read replicas for queries

### 5. **Code Optimization**

```python
# Lazy load heavy modules
def get_ai_service():
    from services.ai import AIService
    return AIService()

# Use async operations
async def process_data():
    results = await asyncio.gather(
        fetch_data1(),
        fetch_data2()
    )
```

## Monitoring

### 1. **Vercel Analytics**

- Enable in Vercel Dashboard
- Monitor function execution times
- Track error rates
- View traffic patterns

### 2. **Custom Monitoring**

```python
# Add custom metrics
import time
start = time.time()
# ... operation ...
duration = time.time() - start
logger.info(f"Operation took {duration}s")
```

### 3. **Error Tracking**

Configure Sentry for error tracking:

```bash
# Set in environment variables
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
```

### 4. **Health Monitoring**

Set up uptime monitoring:
- Use Vercel's built-in monitoring
- Configure external monitors (UptimeRobot, Pingdom)
- Set up alerts for downtime

## Security Best Practices

### 1. **Environment Variables**

- Never commit secrets to git
- Use Vercel's secret management
- Rotate keys regularly
- Use different keys for environments

### 2. **API Security**

- Implement rate limiting
- Use JWT authentication
- Validate all inputs
- Add CORS restrictions

### 3. **Database Security**

- Always use SSL connections
- Implement row-level security
- Use parameterized queries
- Limit database permissions

### 4. **Headers & Middleware**

```python
# Security headers are configured in vercel_handler.py
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

## Cost Optimization

### 1. **Vercel Pricing Tiers**

- **Hobby**: Free, 100GB bandwidth
- **Pro**: $20/month, 1TB bandwidth
- **Enterprise**: Custom pricing

### 2. **Optimization Tips**

- Use Edge Caching to reduce function invocations
- Optimize images and static assets
- Implement efficient database queries
- Monitor usage in Vercel Dashboard

### 3. **Cost Monitoring**

```bash
# Check usage
vercel billing

# Set spending limits
# Configure in Vercel Dashboard → Settings → Billing
```

## Advanced Configuration

### Custom Domains

1. Add domain in Vercel Dashboard
2. Configure DNS records
3. Enable automatic SSL

### Staging Environments

```bash
# Deploy to staging
vercel --target staging

# Use environment-specific variables
VERCEL_ENV=staging vercel
```

### CI/CD Integration

```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

## Support & Resources

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **ruleIQ Issues**: [GitHub Issues](https://github.com/your-org/ruleiq/issues)
- **Community Support**: [Vercel Discord](https://vercel.com/discord)
- **Status Page**: [status.vercel.com](https://status.vercel.com)

## Conclusion

You've successfully deployed ruleIQ to Vercel! The application is now running on a globally distributed, serverless infrastructure with automatic scaling and high availability.

### Next Steps

1. Configure custom domain
2. Set up monitoring alerts
3. Implement CI/CD pipeline
4. Optimize performance based on metrics
5. Scale as your usage grows

For questions or issues, please refer to our [GitHub repository](https://github.com/your-org/ruleiq) or contact support.

---

**Last Updated**: January 2025
**Version**: 2.0.0
**License**: MIT