# GitHub Actions Complete Guide for RuleIQ

## Table of Contents
1. [Overview](#overview)
2. [Workflow Structure](#workflow-structure)
3. [Available Workflows](#available-workflows)
4. [Troubleshooting Common Issues](#troubleshooting-common-issues)
5. [Best Practices](#best-practices)
6. [Environment Variables](#environment-variables)
7. [Secrets Management](#secrets-management)
8. [Performance Optimization](#performance-optimization)
9. [Multi-Component Architecture](#multi-component-architecture)
10. [Quick Reference](#quick-reference)

## Overview

RuleIQ uses GitHub Actions for continuous integration, testing, security scanning, and deployment. Our setup handles a complex multi-component architecture with Python backend, Next.js frontend, and various microservices.

### Key Features
- ✅ Comprehensive CI/CD pipeline
- ✅ Multi-component testing (backend, frontend, integration)
- ✅ Security scanning and vulnerability detection
- ✅ Automated dependency management
- ✅ Vercel deployment integration
- ✅ Performance testing and monitoring

## Workflow Structure

### Directory Layout
```
.github/
└── workflows/
    ├── ci.yml                 # Main CI pipeline
    ├── security.yml           # Security scanning
    ├── test.yml              # Comprehensive testing
    ├── frontend.yml          # Frontend-specific pipeline
    ├── deploy-vercel.yml     # Vercel deployment
    └── dependencies.yml      # Dependency management
```

## Available Workflows

### 1. CI Pipeline (`ci.yml`)
**Triggers:** Push to main/develop, Pull requests
**Purpose:** Main continuous integration workflow

#### Jobs:
- **Backend Tests**: Python unit/integration tests with PostgreSQL/Redis
- **Frontend Build**: Next.js build and type checking
- **Validation**: API endpoint and database health checks
- **Docker Build**: Container image creation

### 2. Security Checks (`security.yml`)
**Triggers:** Push, PR, Weekly schedule
**Purpose:** Security vulnerability scanning

#### Features:
- Python security scanning (Bandit, Safety, Ruff)
- Node.js vulnerability audit
- Secret detection (Gitleaks)
- OWASP dependency check
- CodeQL analysis
- SonarCloud integration

### 3. Comprehensive Testing (`test.yml`)
**Triggers:** Push, PR, Daily schedule
**Purpose:** Full test suite execution

#### Test Types:
- Backend unit tests (multiple Python versions)
- Backend integration tests (with all services)
- Frontend unit and component tests
- End-to-end tests (Playwright)
- Performance tests (Locust)

### 4. Frontend Pipeline (`frontend.yml`)
**Triggers:** Changes to frontend/
**Purpose:** Frontend-specific checks and builds

#### Steps:
- Dependency caching with pnpm
- ESLint and Prettier checks
- TypeScript type checking
- Unit test execution
- Production build
- Bundle size analysis
- Lighthouse performance audit

### 5. Vercel Deployment (`deploy-vercel.yml`)
**Triggers:** Push to main, PRs
**Purpose:** Automated deployment to Vercel

#### Deployment Types:
- Preview deployments for PRs
- Production deployment on main branch
- Manual deployment with environment selection
- Automatic rollback on failure

### 6. Dependency Management (`dependencies.yml`)
**Triggers:** Weekly schedule, dependency file changes
**Purpose:** Keep dependencies updated and secure

#### Features:
- Python dependency analysis
- Node.js package auditing
- Automated update PRs
- License compliance checking
- Cross-component validation

## Troubleshooting Common Issues

### Issue 1: Pydantic Version Conflicts

**Error:** `pydantic 2.6.0 required but 2.9.2 installed`

**Solution:**
```yaml
# In workflow file, add:
- name: Fix pydantic version
  run: |
    pip install --force-reinstall pydantic==2.9.2
```

**Root Cause:** Transitive dependencies may require different pydantic versions. Our requirements.txt explicitly pins 2.9.2 for FastAPI compatibility.

### Issue 2: PNPM Lock File Missing

**Error:** `pnpm-lock.yaml is absent`

**Solution:**
```yaml
# Ensure working directory is set:
- name: Install dependencies
  working-directory: ./frontend
  run: |
    if [ ! -f "pnpm-lock.yaml" ]; then
      pnpm install  # Generate lock file
    else
      pnpm install --frozen-lockfile
    fi
```

**Prevention:** Always run pnpm commands from the frontend directory.

### Issue 3: Service Container Connection Issues

**Error:** `Could not connect to PostgreSQL/Redis`

**Solution:**
```yaml
services:
  postgres:
    image: postgres:14
    env:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ruleiq_test
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 5432:5432
```

**Important:** Use `localhost` for host in CI environment, not `postgres`.

### Issue 4: Environment Variable Missing

**Error:** `KeyError: 'DATABASE_URL'`

**Solution:**
```yaml
env:
  DATABASE_URL: postgresql://postgres:postgres@localhost:5432/ruleiq_test
  REDIS_URL: redis://localhost:6379/0
  JWT_SECRET_KEY: test-secret-key
  TESTING: 'true'
  DISABLE_EXTERNAL_APIS: 'true'
```

### Issue 5: Frontend Build Failures

**Common Causes:**
- Missing environment variables (NEXT_PUBLIC_*)
- TypeScript errors
- Import resolution issues

**Debug Steps:**
1. Check TypeScript configuration
2. Verify all NEXT_PUBLIC_* variables are set
3. Ensure pnpm workspace is configured correctly

## Best Practices

### 1. Workflow Organization
- Keep workflows focused on specific concerns
- Use job dependencies to control execution order
- Implement proper caching strategies
- Use matrix builds for multiple versions

### 2. Security
- Pin action versions (e.g., `actions/checkout@v4`)
- Use least-privilege permissions
- Store secrets in GitHub Secrets
- Regular security scanning
- Never commit secrets to repository

### 3. Performance
- Cache dependencies aggressively
- Use `--frozen-lockfile` for reproducible builds
- Parallelize independent jobs
- Use `continue-on-error` judiciously
- Implement timeout limits

### 4. Reliability
- Always include health checks for services
- Use retry logic for flaky operations
- Implement proper error handling
- Generate comprehensive test reports
- Upload artifacts for debugging

## Environment Variables

### Required for Backend
```bash
DATABASE_URL          # PostgreSQL connection string
REDIS_URL            # Redis connection string
JWT_SECRET_KEY       # JWT signing key
SECRET_KEY           # General secret key
ENVIRONMENT          # testing/staging/production
TESTING              # Set to 'true' in CI
DISABLE_EXTERNAL_APIS # Set to 'true' to mock external calls
```

### Required for Frontend
```bash
NODE_ENV             # development/test/production
NEXT_PUBLIC_API_URL  # Backend API URL
CI                   # Set to 'true' in CI environment
```

### Required for Deployment
```bash
VERCEL_TOKEN         # Vercel authentication
VERCEL_ORG_ID       # Vercel organization ID
VERCEL_PROJECT_ID   # Vercel project ID
PRODUCTION_DATABASE_URL  # Production database
PRODUCTION_JWT_SECRET    # Production JWT secret
PRODUCTION_REDIS_URL     # Production Redis
```

## Secrets Management

### Setting Up Secrets
1. Go to Settings → Secrets → Actions
2. Add required secrets:
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`
   - `SONAR_TOKEN` (if using SonarCloud)
   - Production secrets (DATABASE_URL, etc.)

### Using Secrets in Workflows
```yaml
env:
  MY_SECRET: ${{ secrets.MY_SECRET_NAME }}

steps:
  - name: Use secret
    run: echo "Secret is configured"
    env:
      SECRET_VALUE: ${{ secrets.SECRET_VALUE }}
```

## Performance Optimization

### 1. Dependency Caching

**Python:**
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'
```

**Node.js with pnpm:**
```yaml
- name: Get pnpm store directory
  id: pnpm-cache
  run: echo "STORE_PATH=$(pnpm store path)" >> $GITHUB_OUTPUT

- uses: actions/cache@v4
  with:
    path: ${{ steps.pnpm-cache.outputs.STORE_PATH }}
    key: ${{ runner.os }}-pnpm-${{ hashFiles('**/pnpm-lock.yaml') }}
```

### 2. Parallel Execution
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']
    node-version: ['18', '20']
```

### 3. Conditional Execution
```yaml
if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

### 4. Job Dependencies
```yaml
jobs:
  test:
    runs-on: ubuntu-latest

  deploy:
    needs: test  # Only run after test succeeds
    if: success()
```

## Multi-Component Architecture

### Backend (Python/FastAPI)
- Location: Root directory
- Dependencies: requirements.txt
- Tests: tests/
- Entry point: main.py

### Frontend (Next.js)
- Location: frontend/
- Dependencies: pnpm-lock.yaml
- Tests: frontend/tests/
- Build: pnpm build

### Visualization Backend
- Location: visualization-backend/
- Dependencies: visualization-backend/requirements.txt
- Separate service with own requirements

### Handling Multiple Components
```yaml
# Example: Running tests for all components
jobs:
  backend-test:
    steps:
      - run: pytest tests/

  frontend-test:
    steps:
      - working-directory: ./frontend
        run: pnpm test

  visualization-test:
    steps:
      - working-directory: ./visualization-backend
        run: pytest tests/
```

## Quick Reference

### Common Commands

**Run validation script:**
```bash
python scripts/validate_github_actions.py
```

**Fix common issues:**
```bash
python scripts/validate_github_actions.py --fix
```

**Test workflows locally (using act):**
```bash
act -j backend  # Test specific job
act -P ubuntu-latest=nektos/act-environments-ubuntu:18.04
```

**Check workflow syntax:**
```bash
# Using GitHub CLI
gh workflow view ci.yml
```

### Debugging Tips

1. **Enable debug logging:**
   - Add secret: `ACTIONS_RUNNER_DEBUG` = `true`
   - Add secret: `ACTIONS_STEP_DEBUG` = `true`

2. **SSH into runner (for debugging):**
   ```yaml
   - name: Setup tmate session
     uses: mxschmitt/action-tmate@v3
     if: ${{ failure() }}
   ```

3. **Check service logs:**
   ```yaml
   - name: Check PostgreSQL logs
     if: failure()
     run: docker logs $(docker ps -q --filter ancestor=postgres:14)
   ```

4. **Upload debug artifacts:**
   ```yaml
   - uses: actions/upload-artifact@v4
     if: failure()
     with:
       name: debug-logs
       path: |
         *.log
         .pytest_cache/
   ```

### Useful Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Act - Local GitHub Actions](https://github.com/nektos/act)

## Maintenance

### Weekly Tasks
- Review dependency updates from automated PRs
- Check security scan results
- Review and merge Dependabot PRs
- Monitor workflow execution times

### Monthly Tasks
- Review and optimize slow workflows
- Update action versions
- Clean up old workflow runs
- Review and update documentation

### Troubleshooting Checklist

When a workflow fails:

1. ✅ Check the error message in the workflow run
2. ✅ Verify all required secrets are set
3. ✅ Ensure service containers started correctly
4. ✅ Check for dependency version conflicts
5. ✅ Verify file paths and working directories
6. ✅ Review recent changes to workflow files
7. ✅ Run validation script locally
8. ✅ Check GitHub Status page for outages

## Support

For issues specific to RuleIQ's GitHub Actions setup:
1. Run the validation script: `python scripts/validate_github_actions.py`
2. Check this documentation for common issues
3. Review workflow run logs in GitHub
4. Create an issue with the `ci/cd` label

Remember: Most GitHub Actions issues are related to:
- Missing or incorrect environment variables
- Dependency version conflicts
- Incorrect working directories
- Service container configuration

---

*Last Updated: 2024*
*Version: 1.0.0*