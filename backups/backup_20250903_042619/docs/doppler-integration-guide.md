# Doppler Secrets Management Integration Guide

## Overview

RuleIQ uses Doppler for centralized secrets management across all environments. This guide covers setup, usage, troubleshooting, and best practices.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Setup Instructions](#setup-instructions)
4. [Secret Categories](#secret-categories)
5. [Environment Configuration](#environment-configuration)
6. [CI/CD Integration](#cicd-integration)
7. [Local Development](#local-development)
8. [Secret Rotation](#secret-rotation)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## Quick Start

```bash
# Install Doppler CLI
curl -Ls https://cli.doppler.com/install.sh | sh

# Login to Doppler
doppler login

# Setup project
doppler setup --project ruleiq --config dev

# Run application with secrets
doppler run -- python main.py

# Or use Python SDK
from app.core.doppler_config import get_secret
api_key = get_secret('OPENAI_API_KEY')
```

## Architecture

### Integration Points

```
┌─────────────────────────────────────────────────────────┐
│                    Doppler Cloud                        │
│  ┌─────────────┬──────────────┬───────────────┐       │
│  │     Dev     │   Staging    │  Production   │       │
│  │   Config    │    Config    │    Config     │       │
│  └──────┬──────┴───────┬──────┴───────┬───────┘       │
│         │              │              │                │
└─────────┼──────────────┼──────────────┼────────────────┘
          │              │              │
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │  Local   │  │  CI/CD   │  │   Prod   │
    │   Dev    │  │ Pipeline │  │  Server  │
    └──────────┘  └──────────┘  └──────────┘
```

### Fallback Mechanism

1. **Primary**: Doppler CLI via subprocess
2. **Secondary**: Doppler Python SDK
3. **Tertiary**: Environment variables
4. **Quaternary**: `.env` file (development only)

## Setup Instructions

### 1. Install Prerequisites

```bash
# Install Doppler CLI
curl -Ls https://cli.doppler.com/install.sh | sh

# Install Python SDK
pip install doppler-sdk

# Verify installation
doppler --version
python -c "import doppler_sdk; print('SDK installed')"
```

### 2. Configure Environments

```bash
# Development
doppler setup --project ruleiq --config dev

# Staging (create if needed)
doppler configs create --project ruleiq --name staging

# Production (create if needed)  
doppler configs create --project ruleiq --name production
```

### 3. Set Required Secrets

```bash
# Set a secret
doppler secrets set DATABASE_URL "postgresql://user:pass@host:5432/db"

# Set multiple secrets
doppler secrets set JWT_SECRET_KEY "your-secret" REDIS_URL "redis://localhost:6379"

# Upload from file
doppler secrets upload .env
```

## Secret Categories

### Database Configuration
| Secret | Purpose | Format | Example |
|--------|---------|--------|---------|
| DATABASE_URL | Primary database connection | PostgreSQL URL | `postgresql://user:pass@host/db` |
| TEST_DATABASE_URL | Test database connection | PostgreSQL URL | `postgresql://user:pass@host/test_db` |
| DB_POOL_SIZE | Connection pool size | Integer | `20` |
| DB_MAX_OVERFLOW | Max overflow connections | Integer | `10` |
| DB_POOL_TIMEOUT | Connection timeout (seconds) | Integer | `30` |
| DB_POOL_RECYCLE | Connection recycle time | Integer | `3600` |

### Authentication & Security
| Secret | Purpose | Format | Example |
|--------|---------|--------|---------|
| JWT_SECRET_KEY | JWT signing key | String (min 32 chars) | `your-secret-key-min-32-chars` |
| JWT_ALGORITHM | JWT algorithm | String | `HS256` |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | Access token expiry | Integer | `30` |
| JWT_REFRESH_TOKEN_EXPIRE_DAYS | Refresh token expiry | Integer | `7` |
| SECRET_KEY | Application secret | String (min 32 chars) | `app-secret-key` |
| ENCRYPTION_KEY | Data encryption key | Base64 string | `base64-encoded-key` |
| FERNET_KEY | Fernet encryption key | Fernet key | `generated-fernet-key` |

### AI Services
| Secret | Purpose | Format | Example |
|--------|---------|--------|---------|
| OPENAI_API_KEY | OpenAI API access | String | `sk-...` |
| GOOGLE_AI_API_KEY | Google AI API access | String | `AIza...` |
| LANGCHAIN_API_KEY | LangChain API access | String | `lc-...` |

### Infrastructure Services
| Secret | Purpose | Format | Example |
|--------|---------|--------|---------|
| REDIS_URL | Redis connection | Redis URL | `redis://localhost:6379/0` |
| REDIS_HOST | Redis hostname | String | `localhost` |
| REDIS_PORT | Redis port | Integer | `6379` |
| REDIS_DB | Redis database | Integer | `0` |
| CELERY_BROKER_URL | Celery broker | URL | `redis://localhost:6379/1` |
| CELERY_RESULT_BACKEND | Celery results | String | `redis://localhost:6379/2` |

### Neo4j Graph Database
| Secret | Purpose | Format | Example |
|--------|---------|--------|---------|
| NEO4J_URI | Neo4j connection URI | Bolt URL | `bolt://localhost:7687` |
| NEO4J_USERNAME | Neo4j username | String | `neo4j` |
| NEO4J_PASSWORD | Neo4j password | String | `password` |
| NEO4J_DATABASE | Neo4j database name | String | `neo4j` |

### Application Configuration
| Secret | Purpose | Format | Example |
|--------|---------|--------|---------|
| ENVIRONMENT | Environment name | String | `dev`, `staging`, `production` |
| DEBUG | Debug mode | Boolean | `false` |
| API_HOST | API host | String | `0.0.0.0` |
| API_PORT | API port | Integer | `8000` |
| API_WORKERS | Worker count | Integer | `4` |
| APP_URL | Application URL | URL | `https://app.ruleiq.com` |

### Frontend Configuration
| Secret | Purpose | Format | Example |
|--------|---------|--------|---------|
| NEXT_PUBLIC_API_URL | API endpoint | URL | `https://api.ruleiq.com` |
| NEXT_PUBLIC_STACK_PROJECT_ID | Stack Auth project | String | `project-id` |
| NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY | Stack Auth public key | String | `pub-key` |
| STACK_SECRET_SERVER_KEY | Stack Auth secret | String | `secret-key` |

## Environment Configuration

### Development Environment

```bash
# Set up development
doppler setup --project ruleiq --config dev

# Run with Doppler
doppler run -- python main.py
doppler run -- pytest
doppler run -- npm run dev
```

### Staging Environment

```bash
# Set up staging
doppler setup --project ruleiq --config staging

# Deploy with staging secrets
doppler run --config staging -- ./deploy.sh
```

### Production Environment

```bash
# Set up production
doppler setup --project ruleiq --config production

# Use service token for production
export DOPPLER_TOKEN="dp.st.production.xxxxx"
python main.py
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Doppler
        run: |
          curl -Ls https://cli.doppler.com/install.sh | sh
          
      - name: Deploy with Doppler
        env:
          DOPPLER_TOKEN: ${{ secrets.DOPPLER_SERVICE_TOKEN }}
        run: |
          doppler run -- ./deploy.sh
```

### Service Tokens

```bash
# Create service token for CI/CD
doppler configs tokens create --project ruleiq --config production --name "GitHub Actions"

# Use in CI/CD
export DOPPLER_TOKEN="dp.st.production.xxxxx"
doppler run -- command
```

## Local Development

### Using Doppler CLI

```bash
# Standard run
doppler run -- python main.py

# With specific config
doppler run --config dev -- python main.py

# Export to .env (for compatibility)
doppler secrets download --no-file --format env > .env
```

### Using Python Integration

```python
from app.core.doppler_config import (
    get_doppler_config,
    get_secret,
    get_database_url,
    validate_startup_secrets
)

# Initialize on startup
validate_startup_secrets()

# Get individual secrets
api_key = get_secret('OPENAI_API_KEY')

# Get configuration groups
config = get_doppler_config()
jwt_config = config.get_jwt_config()
ai_config = config.get_ai_config()
neo4j_config = config.get_neo4j_config()

# Inject all secrets to environment
config.inject_to_environment()
```

### Fallback for Offline Development

```python
# Create .env.local for offline work
DATABASE_URL=postgresql://localhost/ruleiq_dev
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=dev-secret-key-for-local-testing
# ... other required secrets
```

## Secret Rotation

### Manual Rotation

```bash
# Rotate a secret
doppler secrets set JWT_SECRET_KEY "new-secret-value"

# Rotate with Python
from app.core.doppler_config import get_doppler_config
config = get_doppler_config()
config.rotate_secret('JWT_SECRET_KEY', 'new-secret-value')
```

### Automated Rotation Workflow

```python
# scripts/rotate_secrets.py
import secrets
from app.core.doppler_config import get_doppler_config

def rotate_jwt_key():
    """Rotate JWT secret key."""
    config = get_doppler_config()
    new_key = secrets.token_urlsafe(32)
    
    # Rotate in Doppler
    if config.rotate_secret('JWT_SECRET_KEY', new_key):
        print("JWT key rotated successfully")
        
        # Trigger application restart
        # notify_services_of_rotation()
    else:
        print("Failed to rotate JWT key")

if __name__ == "__main__":
    rotate_jwt_key()
```

## Troubleshooting

### Common Issues

#### 1. Doppler CLI Not Found

```bash
# Error: Doppler CLI not found
# Solution: Install Doppler
curl -Ls https://cli.doppler.com/install.sh | sh

# Add to PATH if needed
export PATH="$HOME/.doppler/bin:$PATH"
```

#### 2. Authentication Issues

```bash
# Error: Not authenticated
# Solution: Login to Doppler
doppler login

# Or use service token
export DOPPLER_TOKEN="your-service-token"
```

#### 3. Project Not Configured

```bash
# Error: No project configured
# Solution: Setup project
doppler setup --project ruleiq --config dev

# Or set via environment
export DOPPLER_PROJECT="ruleiq"
export DOPPLER_CONFIG="dev"
```

#### 4. Secret Not Found

```python
# Error: Secret 'XYZ' not found
# Check if secret exists
doppler secrets get XYZ

# Set if missing
doppler secrets set XYZ "value"

# Use fallback in code
value = get_secret('XYZ', 'default-value')
```

#### 5. Python SDK Issues

```python
# Error: doppler_sdk not found
# Solution: Install SDK
pip install doppler-sdk

# Use fallback mechanism
from app.core.doppler_config import get_secret
# Will fallback to env vars if SDK fails
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

from app.core.doppler_config import get_doppler_config
config = get_doppler_config()
config.initialize()  # Will log debug info
```

### Verification Script

```bash
# Run verification
python scripts/verify_doppler_secrets.py

# Check specific secret
doppler secrets get DATABASE_URL

# Test runtime injection
doppler run -- python -c "import os; print(os.getenv('DATABASE_URL'))"
```

## Best Practices

### 1. Secret Naming Convention

- Use UPPER_SNAKE_CASE
- Prefix with service name (e.g., `REDIS_`, `NEO4J_`)
- Be descriptive (e.g., `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`)

### 2. Environment Separation

```bash
# Never share secrets between environments
doppler secrets --config dev      # Development secrets
doppler secrets --config staging  # Staging secrets  
doppler secrets --config production # Production secrets
```

### 3. Access Control

- Use service tokens for CI/CD
- Limit access to production secrets
- Enable audit logging
- Lock production configuration

### 4. Secret Validation

```python
# Always validate on startup
from app.core.doppler_config import validate_startup_secrets
validate_startup_secrets()

# Custom validation
def validate_api_keys():
    config = get_doppler_config()
    required = ['OPENAI_API_KEY', 'GOOGLE_AI_API_KEY']
    valid, missing = config.validate_required_secrets(required)
    
    if not valid:
        logger.warning(f"Missing AI keys: {missing}")
        # Handle gracefully
```

### 5. Fallback Strategy

```python
# Always provide fallbacks
database_url = get_secret('DATABASE_URL', 'postgresql://localhost/dev')

# Check initialization
config = get_doppler_config()
if not config._initialized:
    logger.warning("Using environment variables (Doppler not available)")
```

### 6. Security Considerations

- Never log secret values
- Use short-lived tokens for CI/CD
- Rotate secrets regularly
- Monitor secret access
- Use different secrets per environment

### 7. Testing with Doppler

```bash
# Run tests with test configuration
doppler run --config test -- pytest

# Mock in unit tests
def test_with_mock_secrets(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql://test/db')
    # Test code
```

## Migration Checklist

- [x] Install Doppler CLI
- [x] Configure ruleiq project
- [x] Set up dev environment
- [x] Migrate all secrets to Doppler
- [x] Install Python SDK
- [x] Create doppler_config.py module
- [x] Add fallback mechanisms
- [x] Create verification script
- [x] Document all secrets
- [ ] Set up staging environment
- [ ] Set up production environment
- [ ] Configure CI/CD service tokens
- [ ] Implement secret rotation
- [ ] Add monitoring and alerts

## Support

For issues or questions:

1. Check this documentation
2. Run verification script: `python scripts/verify_doppler_secrets.py`
3. Check Doppler dashboard: https://dashboard.doppler.com
4. Review logs: `doppler activity`
5. Contact DevOps team for production issues