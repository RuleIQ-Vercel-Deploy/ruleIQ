# RuleIQ Configuration Guide

## Overview

RuleIQ uses a centralized configuration management system based on Pydantic for validation and environment-specific settings. The configuration system provides:

- **Type validation** - Ensures all configuration values are the correct type
- **Environment-specific configs** - Separate settings for development, staging, production, and testing
- **Startup validation** - Validates configuration and connectivity on application startup
- **Security checks** - Prevents weak secrets and insecure settings in production
- **Default values** - Sensible defaults with environment-appropriate overrides

## Quick Start

1. Copy the example configuration:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your settings

3. Validate your configuration:
   ```bash
   python config/startup_validation.py
   ```

4. Start the application

## Configuration Structure

```
config/
├── __init__.py           # Configuration loader
├── base.py               # Base configuration with validation
├── development.py        # Development settings
├── production.py         # Production settings
├── testing.py            # Testing settings
└── startup_validation.py # Startup validation script
```

## Environment Configuration

### Setting the Environment

The environment is determined by the `ENVIRONMENT` variable:

```bash
# Development (default)
ENVIRONMENT=development

# Staging
ENVIRONMENT=staging

# Production
ENVIRONMENT=production

# Testing
ENVIRONMENT=testing
```

### Environment-Specific Files

You can use environment-specific `.env` files:

- `.env` - Default, used for development
- `.env.development` - Development overrides
- `.env.production` - Production settings
- `.env.testing` - Testing configuration

## Configuration Categories

### Core Settings

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `ENVIRONMENT` | string | Yes | development | Environment name |
| `APP_NAME` | string | No | RuleIQ | Application name |
| `APP_VERSION` | string | No | 1.0.0 | Application version |
| `DEBUG` | boolean | No | false | Debug mode (must be false in production) |

### Server Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `HOST` | string | No | 0.0.0.0 | Server host |
| `PORT` | integer | No | 8000 | Server port |
| `WORKERS` | integer | No | 1 (dev), 4 (prod) | Number of worker processes |

### Security Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `SECRET_KEY` | string | **Yes** | - | Application secret key (min 32 chars) |
| `JWT_SECRET_KEY` | string | **Yes** | - | JWT signing key (min 32 chars) |
| `JWT_ALGORITHM` | string | No | HS256 | JWT algorithm |
| `JWT_EXPIRATION_DELTA_SECONDS` | integer | No | 3600 | JWT expiration time |

**Security Best Practices:**
- Generate secure keys: `openssl rand -hex 32`
- Never use default or weak keys in production
- Rotate keys periodically
- Use different keys for different environments

### Database Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `DATABASE_URL` | string | **Yes** | - | PostgreSQL connection URL |
| `DB_POOL_SIZE` | integer | No | 20 | Connection pool size |
| `DB_MAX_OVERFLOW` | integer | No | 40 | Max overflow connections |
| `DB_POOL_TIMEOUT` | integer | No | 30 | Pool timeout in seconds |
| `DB_POOL_RECYCLE` | integer | No | 3600 | Connection recycle time |

**Database URL Format:**
```
# Standard
postgresql://username:password@host:port/database

# Async (recommended)
postgresql+asyncpg://username:password@host:port/database

# With SSL
postgresql://username:password@host:port/database?sslmode=require
```

### Redis Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `REDIS_URL` | string | **Yes** | - | Redis connection URL |
| `REDIS_MAX_CONNECTIONS` | integer | No | 50 | Max Redis connections |
| `REDIS_DECODE_RESPONSES` | boolean | No | true | Decode Redis responses |

**Redis URL Format:**
```
# Standard
redis://localhost:6379/0

# With password
redis://:password@localhost:6379/0

# SSL/TLS
rediss://localhost:6379/0
```

### Neo4j Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `NEO4J_URI` | string | **Yes** | - | Neo4j connection URI |
| `NEO4J_USERNAME` | string | **Yes** | - | Neo4j username |
| `NEO4J_PASSWORD` | string | **Yes** | - | Neo4j password |

### AI Services Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `OPENAI_API_KEY` | string | Conditional | - | OpenAI API key |
| `OPENAI_MODEL` | string | No | gpt-4-turbo | OpenAI model |
| `OPENAI_TEMPERATURE` | float | No | 0.7 | OpenAI temperature |
| `OPENAI_MAX_TOKENS` | integer | No | 2000 | Max tokens |
| `GOOGLE_API_KEY` | string | Conditional | - | Google API key |
| `GOOGLE_AI_API_KEY` | string | Conditional | - | Google AI API key |
| `ANTHROPIC_API_KEY` | string | Conditional | - | Anthropic API key |
| `CLAUDE_MODEL` | string | No | claude-3-opus-20240229 | Claude model |

**Note:** At least one AI service key is required if `ENABLE_AI_PROCESSING=true`

### File Storage Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `UPLOAD_DIR` | string | No | uploads | Upload directory |
| `MAX_FILE_SIZE` | integer | No | 10485760 | Max file size in bytes |
| `ALLOWED_EXTENSIONS` | string | No | pdf,txt,doc,docx,csv | Allowed file extensions |

### Logging Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `LOG_LEVEL` | string | No | INFO | Log level |
| `LOG_FORMAT` | string | No | See defaults | Log format string |
| `LOG_FILE` | string | No | - | Log file path |
| `LOG_MAX_BYTES` | integer | No | 10485760 | Max log file size |
| `LOG_BACKUP_COUNT` | integer | No | 5 | Number of backup files |

**Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL

### CORS Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `CORS_ORIGINS` | string | No | * (dev), specific (prod) | Allowed origins |
| `CORS_ALLOW_CREDENTIALS` | boolean | No | true | Allow credentials |
| `CORS_ALLOW_METHODS` | string | No | * | Allowed methods |
| `CORS_ALLOW_HEADERS` | string | No | * | Allowed headers |

**Production CORS:**
```bash
# Never use * in production
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=Content-Type,Authorization
```

### Rate Limiting Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `RATE_LIMIT_ENABLED` | boolean | No | true | Enable rate limiting |
| `RATE_LIMIT_REQUESTS` | integer | No | 100 | Requests per window |
| `RATE_LIMIT_WINDOW` | integer | No | 60 | Time window in seconds |

### Feature Flags

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `ENABLE_AI_PROCESSING` | boolean | No | true | Enable AI processing |
| `ENABLE_CACHING` | boolean | No | true | Enable caching |
| `ENABLE_MONITORING` | boolean | No | false (dev), true (prod) | Enable monitoring |
| `ENABLE_DEBUG_TOOLBAR` | boolean | No | false | Debug toolbar (dev only) |
| `ENABLE_PROFILING` | boolean | No | false | Enable profiling (dev only) |
| `ENABLE_SQL_ECHO` | boolean | No | false | Log SQL queries (dev only) |

## Using Configuration in Code

### Basic Usage

```python
from config import get_current_config

# Get configuration singleton
config = get_current_config()

# Access configuration values
database_url = config.DATABASE_URL
is_production = config.is_production()
is_development = config.is_development()
```

### Loading Specific Environment

```python
from config import get_config

# Load specific environment
config = get_config("production")
```

### Accessing Grouped Settings

```python
# Get database configuration
db_config = config.get_db_config()
# Returns: {"url": "...", "pool_size": 20, ...}

# Get Redis configuration
redis_config = config.get_redis_config()

# Get AI services configuration
ai_config = config.get_ai_config()
```

## Startup Validation

### Running Validation

```bash
# Validate current environment
python config/startup_validation.py

# Validate specific environment
python config/startup_validation.py production
```

### Validation Checks

The startup validation performs:

1. **Environment validation** - Checks environment settings
2. **Secret validation** - Ensures strong secrets
3. **Database connectivity** - Tests database connection
4. **Redis connectivity** - Tests Redis connection
5. **Neo4j connectivity** - Tests Neo4j connection
6. **AI service validation** - Checks API keys
7. **File system validation** - Checks directories and permissions
8. **Security validation** - Ensures secure settings in production
9. **Performance validation** - Checks performance settings

### Integration with Application

```python
# In your main application file
from config.startup_validation import run_startup_validation

# Run validation on startup
if __name__ == "__main__":
    # Validate configuration
    if not run_startup_validation(exit_on_error=True):
        print("Configuration validation failed")
        sys.exit(1)
    
    # Start application
    app.run()
```

## Production Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Generate strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Use production database URL (not localhost)
- [ ] Use production Redis URL (not localhost)
- [ ] Configure proper CORS origins (not *)
- [ ] Enable rate limiting
- [ ] Enable monitoring
- [ ] Configure proper logging
- [ ] Enable all security features
- [ ] Set appropriate worker count
- [ ] Configure SSL/TLS

### Production Configuration Example

```bash
# .env.production
ENVIRONMENT=production
DEBUG=false

# Security
SECRET_KEY=<generated-32-char-hex>
JWT_SECRET_KEY=<generated-32-char-hex>
JWT_EXPIRATION_DELTA_SECONDS=3600

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db.example.com:5432/ruleiq
DB_POOL_SIZE=30
DB_MAX_OVERFLOW=50

# Redis
REDIS_URL=redis://:password@prod-redis.example.com:6379/0
REDIS_MAX_CONNECTIONS=100

# CORS
CORS_ORIGINS=https://app.example.com,https://www.example.com

# Security
SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Strict

# Performance
WORKERS=8
ENABLE_COMPRESSION=true
ENABLE_CACHING=true

# Monitoring
ENABLE_MONITORING=true
ENABLE_ERROR_TRACKING=true
```

## Testing Configuration

### Testing Environment

```python
# config/testing.py provides test-specific defaults
from config import get_config

config = get_config("testing")
```

### Test Configuration Example

```bash
# .env.testing
ENVIRONMENT=testing
DATABASE_URL=postgresql://localhost/ruleiq_test
REDIS_URL=redis://localhost:6379/15
USE_AI_MOCKS=true
```

## Troubleshooting

### Common Issues

1. **Configuration not loading**
   - Check file exists: `.env` or environment-specific file
   - Verify file permissions
   - Check for syntax errors in `.env` file

2. **Validation failures**
   - Run `python config/startup_validation.py` for detailed errors
   - Check connectivity to external services
   - Verify all required fields are set

3. **Production issues**
   - Ensure production-specific validation passes
   - Check for development values in production config
   - Verify SSL/TLS settings

### Debug Configuration Loading

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from config import get_config
config = get_config()  # Will show debug output
```

## Migration Guide

### From Old Configuration System

If migrating from the old configuration system:

1. **Identify all environment variables** currently in use
2. **Map to new configuration** structure
3. **Update code** to use new configuration API
4. **Test thoroughly** in all environments

### Example Migration

Old:
```python
import os
database_url = os.getenv("DATABASE_URL")
debug = os.getenv("DEBUG", "false").lower() == "true"
```

New:
```python
from config import get_current_config
config = get_current_config()
database_url = config.DATABASE_URL
debug = config.DEBUG
```

## Best Practices

1. **Never commit secrets** - Use `.gitignore` for `.env` files
2. **Use environment-specific files** - Separate dev/prod configs
3. **Validate on startup** - Catch configuration issues early
4. **Monitor configuration** - Log configuration loading
5. **Rotate secrets regularly** - Update keys periodically
6. **Use strong secrets** - Generate with `openssl rand -hex 32`
7. **Document changes** - Update this guide when adding variables
8. **Test configuration** - Validate in all environments
9. **Use defaults wisely** - Secure defaults for production
10. **Keep it DRY** - Use base configuration for shared settings