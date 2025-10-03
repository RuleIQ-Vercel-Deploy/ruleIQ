# Environment Setup Guide for RuleIQ

This comprehensive guide explains how to properly configure environment variables for RuleIQ development and production deployment.

## Table of Contents
- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Required Variables](#required-variables)
- [Database Configuration](#database-configuration)
- [AI Service Configuration](#ai-service-configuration)
- [Validation and Troubleshooting](#validation-and-troubleshooting)
- [Security Best Practices](#security-best-practices)
- [Environment-Specific Configuration](#environment-specific-configuration)
- [CI/CD Integration](#cicd-integration)

## Introduction

RuleIQ requires proper environment configuration for security and functionality. **The application will fail to start** if required environment variables are not properly configured. This design prevents insecure deployments with default passwords or missing credentials.

### Why Proper Environment Configuration Matters
- **Security**: Prevents hardcoded credentials and insecure defaults
- **Reliability**: Ensures all required services are accessible
- **Maintainability**: Centralizes configuration management
- **Team Collaboration**: Simplifies onboarding with clear documentation

## Quick Start

### Option 1: Using Doppler (Recommended for Teams)

Doppler provides centralized secret management and team collaboration features.

```bash
# Install Doppler
brew install doppler  # macOS
# or
curl -Ls https://cli.doppler.com/install.sh | sh  # Linux

# Login and setup
doppler login
doppler setup

# Verify configuration
doppler secrets

# Run application
doppler run -- python main.py
```

### Option 2: Using .env.local (Development)

For local development, you can use a `.env.local` file.

```bash
# Copy template
cp env.template .env.local

# Edit with your credentials (use your preferred editor)
nano .env.local
# or
vim .env.local
# or
code .env.local

# Validate configuration
python scripts/validate_required_env_vars.py

# Run application (will automatically load .env.local)
python main.py
```

**IMPORTANT**: Never commit `.env.local` to version control. It's already in `.gitignore`.

## Required Variables

The following environment variables are **REQUIRED**. The application will fail to start if they are missing or contain placeholder values.

### Database Credentials

#### PostgreSQL (Primary Database)
```bash
# Connection URL for Neon PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@host.neon.tech/database?sslmode=require

# Example for local development
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ruleiq_dev
```

**Where to get it:**
- Production: [Neon Console](https://console.neon.tech/)
- Development: Local PostgreSQL installation

**Security considerations:**
- Use connection pooling (asyncpg) for production
- Enable SSL mode (`sslmode=require`)
- Rotate passwords quarterly

#### Redis (Caching and Sessions)
```bash
# Redis connection URL
REDIS_URL=redis://localhost:6379/0

# For production with authentication
REDIS_URL=redis://:password@host:6379/0
```

**Where to get it:**
- Production: Redis Cloud, AWS ElastiCache, or self-hosted
- Development: Local Redis (`brew install redis` or `apt-get install redis`)

**Security considerations:**
- Always use password authentication in production
- Use separate Redis databases for different purposes (cache, sessions, celery)

#### Neo4j (Knowledge Graph)
```bash
# Neo4j AuraDB connection URI
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io

# Neo4j username (typically 'neo4j')
NEO4J_USERNAME=neo4j

# Neo4j password (generate strong password in AuraDB console)
NEO4J_PASSWORD=your-strong-password-here

# Database name (default: 'neo4j')
NEO4J_DATABASE=neo4j
```

**Where to get it:**
- Production: [Neo4j AuraDB Console](https://console.neo4j.io/)
- Development: Neo4j AuraDB free tier or local Neo4j

**Security considerations:**
- ⚠️ **NEVER use 'ruleiq123', 'password', or any default value**
- Generate strong passwords (20+ characters, mixed case, numbers, symbols)
- Use AuraDB's automatic password generation
- The application will fail to start if NEO4J_PASSWORD is missing

### Authentication & Encryption

#### JWT Secrets
```bash
# Secret key for JWT token signing (32+ characters)
JWT_SECRET=your-randomly-generated-secret-key-here

# Application secret key (32+ characters)
SECRET_KEY=another-randomly-generated-secret-key-here
```

**How to generate:**
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

#### Encryption Keys
```bash
# Fernet encryption key for sensitive data
FERNET_KEY=your-fernet-key-here
```

**How to generate:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Security considerations:**
- Never reuse keys across environments
- Store keys in Doppler or secure vault
- Rotate keys annually (requires data re-encryption)

### AI Services

**At least one AI service API key is required.**

#### OpenAI (Required)
```bash
OPENAI_API_KEY=sk-...
```

**Where to get it:**
- [OpenAI Platform](https://platform.openai.com/api-keys)

#### Anthropic (Optional)
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

**Where to get it:**
- [Anthropic Console](https://console.anthropic.com/)

#### Google AI (Optional)
```bash
GOOGLE_AI_API_KEY=AIza...
```

**Where to get it:**
- [Google AI Studio](https://makersuite.google.com/app/apikey)

**Security considerations:**
- Set usage limits on API keys
- Monitor API usage for anomalies
- Use separate keys for development and production

## Database Configuration

### PostgreSQL Setup

#### Production (Neon)
1. Create account at [neon.tech](https://neon.tech)
2. Create new project
3. Copy connection string
4. Add to environment: `DATABASE_URL=postgresql+asyncpg://...`

#### Development (Local)
```bash
# Install PostgreSQL
brew install postgresql@15  # macOS
# or
sudo apt-get install postgresql-15  # Linux

# Start PostgreSQL
brew services start postgresql@15  # macOS
# or
sudo systemctl start postgresql  # Linux

# Create database
createdb ruleiq_dev

# Set environment variable
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ruleiq_dev
```

### Redis Setup

#### Production
Use Redis Cloud, AWS ElastiCache, or self-hosted Redis with authentication.

#### Development (Local)
```bash
# Install Redis
brew install redis  # macOS
# or
sudo apt-get install redis  # Linux

# Start Redis
brew services start redis  # macOS
# or
sudo systemctl start redis  # Linux

# Set environment variable
export REDIS_URL=redis://localhost:6379/0
```

### Neo4j Setup

#### Production & Development (AuraDB - Recommended)
1. Create account at [console.neo4j.io](https://console.neo4j.io/)
2. Create new AuraDB instance (free tier available)
3. Download credentials (only shown once!)
4. Add to environment:
   ```bash
   NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your-generated-password
   ```

#### Development (Local - Not Recommended)
Local Neo4j requires Docker and more setup. AuraDB free tier is recommended instead.

## AI Service Configuration

### OpenAI Setup
1. Create account at [platform.openai.com](https://platform.openai.com/)
2. Add payment method (required for API access)
3. Generate API key: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
4. Set usage limits (recommended: $50/month for development)
5. Add to environment: `OPENAI_API_KEY=sk-...`

### Anthropic Setup (Optional)
1. Request access at [anthropic.com](https://www.anthropic.com/)
2. Generate API key in console
3. Add to environment: `ANTHROPIC_API_KEY=sk-ant-...`

### Google AI Setup (Optional)
1. Create project in [Google AI Studio](https://makersuite.google.com/)
2. Generate API key
3. Add to environment: `GOOGLE_AI_API_KEY=AIza...`

## Validation and Troubleshooting

### Validate Configuration

Run the validation script to check your environment:

```bash
# Validate all required variables
python scripts/validate_required_env_vars.py

# Validate for specific environment
python scripts/validate_required_env_vars.py --environment production

# Report only (don't fail)
python scripts/validate_required_env_vars.py --no-fail

# Minimal output
python scripts/validate_required_env_vars.py --quiet
```

### Common Error Messages and Solutions

#### "NEO4J_PASSWORD environment variable is required"
**Solution:** Set NEO4J_PASSWORD in your environment or .env.local file. Never use default passwords.

#### "At least one AI service API key is required"
**Solution:** Set at least one of OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_AI_API_KEY.

#### "contains placeholder value"
**Solution:** Replace placeholder values like "your-password-here" with actual credentials.

#### "uses insecure password"
**Solution:** Never use passwords like "password", "ruleiq123", "admin", etc. Generate strong passwords.

### Debugging Environment Issues

```bash
# Check if variables are set
env | grep NEO4J
env | grep DATABASE_URL

# Test database connections
python -c "import asyncpg; print('asyncpg installed')"
python -c "import redis; print('redis installed')"
python -c "from neo4j import GraphDatabase; print('neo4j installed')"

# Run validation with verbose output
python scripts/validate_required_env_vars.py
```

## Security Best Practices

### DO ✅
- Use Doppler for team collaboration
- Generate strong, random passwords (20+ characters)
- Store secrets in `.env.local` (never commit)
- Rotate secrets regularly (quarterly for passwords, annually for encryption keys)
- Use different secrets for each environment (dev, staging, production)
- Set API usage limits
- Monitor for secret leaks (Gitleaks, secret scanner)

### DON'T ❌
- Never commit `.env` files to version control
- Never use default passwords ("password", "ruleiq123", etc.)
- Never share secrets via email or Slack
- Never hardcode secrets in code
- Never use production secrets in development
- Never reuse passwords across services

### What to Do If Secrets Are Leaked

1. **Immediate action:**
   ```bash
   # Rotate all affected secrets immediately
   # Update in Doppler or environment
   ```

2. **Notify team:**
   - Alert team members immediately
   - Document the incident

3. **Cleanup:**
   - Remove secrets from git history (if committed)
   - Update documentation
   - Review access logs

4. **Prevention:**
   - Review secret handling practices
   - Update pre-commit hooks
   - Run security audit

## Environment-Specific Configuration

### Development Environment

```bash
# Development-specific settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Can use local services
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ruleiq_dev
REDIS_URL=redis://localhost:6379/0

# Development exemptions
# FERNET_KEY can be auto-generated in development
```

### Staging Environment

```bash
# Staging-specific settings
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Use production-like infrastructure
# All required variables must be set
# No exemptions
```

### Production Environment

```bash
# Production-specific settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# All required variables must be set
# No exemptions
# Use Doppler for secret management
```

## CI/CD Integration

### GitHub Actions

Secrets are managed in GitHub repository settings:

1. Go to repository Settings → Secrets and variables → Actions
2. Add required secrets:
   - `DATABASE_URL`
   - `REDIS_URL`
   - `NEO4J_URI`
   - `NEO4J_USERNAME`
   - `NEO4J_PASSWORD`
   - `JWT_SECRET`
   - `SECRET_KEY`
   - `FERNET_KEY`
   - `OPENAI_API_KEY`

### Workflow Usage

```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  NEO4J_PASSWORD: ${{ secrets.NEO4J_PASSWORD }}
  # ... other secrets
```

### Adding New Secrets

1. Update `scripts/validate_required_env_vars.py`
2. Update `env.template`
3. Update this documentation
4. Add to GitHub Actions secrets
5. Update Doppler configuration
6. Notify team

## Related Documentation

- [Secret Handling Guide](docs/security/SECRET_HANDLING_GUIDE.md)
- [Secret Rotation Plan](docs/security/SECRET_ROTATION_PLAN.md)
- [Environment Template](env.template)
- [Validation Script](scripts/validate_required_env_vars.py)

---

_Last updated: 2025-09-30_
