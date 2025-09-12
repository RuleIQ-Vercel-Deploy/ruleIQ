# 🔐 RuleIQ Doppler Secrets Vault Integration

**Production-Ready Secrets Management with Doppler Integration**

## Overview

The RuleIQ SecretsVault provides multi-platform secrets management with **Doppler as the primary production solution**. This implementation automatically detects the deployment environment and uses the most appropriate secrets backend.

## 🚀 Architecture

### Backend Priority (Auto-Detection)
1. **Doppler Secrets Management** (Preferred for production)
2. **Vercel Environment Variables** (Vercel deployments)  
3. **AWS Secrets Manager** (Enterprise/self-hosted)
4. **Local Environment Variables** (Development fallback)

### Detection Logic
- **Doppler**: Auto-detected via `DOPPLER_TOKEN` or `DOPPLER_PROJECT` environment variables
- **Vercel**: Auto-detected via `VERCEL` environment variable
- **AWS**: Manual activation via `SECRETS_MANAGER_ENABLED=true`
- **Local**: Default fallback for development

## 🔧 Doppler Setup for Production

### 1. Doppler Account Setup
```bash
# Install Doppler CLI (if needed)
curl -Ls https://cli.doppler.com/install.sh | sudo sh

# Login to Doppler
doppler login

# Setup your project
doppler setup
```

### 2. Configure Doppler for Vercel
```bash
# Install Vercel integration
doppler integrations install vercel

# Sync secrets to Vercel
doppler secrets download --format env > .env.production
# Upload to Vercel via dashboard or CLI
```

### 3. Required Environment Variables
```bash
# Doppler Configuration (auto-injected by Doppler)
DOPPLER_TOKEN=dp.st.xxxx
DOPPLER_PROJECT=ruleiq
DOPPLER_CONFIG=prd  # or dev, stg
DOPPLER_ENVIRONMENT=production
```

## 📡 API Endpoints

### Health Check
```http
GET /api/v1/secrets-vault/health
Authorization: Bearer <jwt_token>
```

**Response (Doppler Active)**:
```json
{
  "status": "healthy",
  "enabled": true,
  "vault_type": "Doppler Secrets Management",
  "message": "Doppler secrets management active with token authentication",
  "project": "ruleiq",
  "config": "prd",
  "environment": "production",
  "token_configured": true
}
```

### Status Check
```http
GET /api/v1/secrets-vault/status
Authorization: Bearer <jwt_token>
```

### Connection Test
```http
POST /api/v1/secrets-vault/test
Authorization: Bearer <jwt_token>
```

### Configuration
```http
GET /api/v1/secrets-vault/config
Authorization: Bearer <jwt_token>
```

## 🔐 Secret Keys Mapping

The SecretsVault uses standardized secret keys that map to environment variables:

### Database & Infrastructure
- `database_url` → `DATABASE_URL` or `VAULT_SECRET_DATABASE_URL`
- `redis_url` → `REDIS_URL` or `VAULT_SECRET_REDIS_URL`

### Authentication & Security
- `jwt_secret` → `JWT_SECRET` or `VAULT_SECRET_JWT_SECRET`
- `secret_key` → `SECRET_KEY` or `VAULT_SECRET_SECRET_KEY`
- `encryption_key` → `ENCRYPTION_KEY` or `VAULT_SECRET_ENCRYPTION_KEY`

### AI Services
- `openai_api_key` → `OPENAI_API_KEY` or `VAULT_SECRET_OPENAI_API_KEY`
- `google_ai_api_key` → `GOOGLE_AI_API_KEY` or `VAULT_SECRET_GOOGLE_AI_API_KEY`

### OAuth & External Services
- `google_client_id` → `GOOGLE_CLIENT_ID` or `VAULT_SECRET_GOOGLE_CLIENT_ID`
- `stripe_secret_key` → `STRIPE_SECRET_KEY` or `VAULT_SECRET_STRIPE_SECRET_KEY`

## 💻 Code Usage

### Direct Access
```python
from config.secrets_vault import get_secrets_vault

# Get vault instance
vault = get_secrets_vault()

# Retrieve secrets
db_url = vault.get_secret("database_url")
api_key = vault.get_secret("openai_api_key")

# Health check
health = vault.health_check()
print(f"Vault status: {health['status']}")
```

### Convenience Functions
```python
from config.secrets_vault import get_secret, vault_health_check

# Quick access
database_url = get_secret("database_url")
health = vault_health_check()
```

### Using Secret Keys Constants
```python
from config.secrets_vault import get_secret, SecretKeys

# Type-safe access
db_url = get_secret(SecretKeys.DATABASE_URL)
jwt_secret = get_secret(SecretKeys.JWT_SECRET)
openai_key = get_secret(SecretKeys.OPENAI_API_KEY)
```

## 🏗️ Integration with Settings

The SecretsVault is integrated with Pydantic settings:

```python
# config/settings.py
from config.secrets_vault import get_secret

class Settings(BaseSettings):
    database_url: str = Field(default_factory=lambda: get_secret("database_url") or "sqlite:///fallback.db")
    jwt_secret: str = Field(default_factory=lambda: get_secret("jwt_secret") or "dev-secret")
    openai_api_key: Optional[str] = Field(default_factory=lambda: get_secret("openai_api_key"))
    
    def get_secrets_vault_health(self) -> Dict[str, Any]:
        """Get SecretsVault health status for monitoring"""
        from config.secrets_vault import vault_health_check
        return vault_health_check()
```

## 🔍 Monitoring & Health Checks

### Application Health Endpoint
The main application health check includes SecretsVault status:

```http
GET /api/v1/health/detailed
```

**Response includes**:
```json
{
  "secrets_vault": {
    "status": "healthy",
    "enabled": true,
    "vault_type": "Doppler Secrets Management",
    "message": "Doppler secrets management active"
  }
}
```

### CLI Testing
```bash
# Test health
python config/secrets_vault.py health

# Get secret (masked output)
python config/secrets_vault.py get database_url

# List all secrets
python config/secrets_vault.py list
```

## 🚨 Security Features

### 1. Secure Logging
- Secret values are never logged in plaintext
- Debug logs show only key names and sources
- Health checks don't expose sensitive information

### 2. Automatic Cache Management
- LRU cache for performance (100 entries max)
- Cache clearing on secret rotation
- Memory-efficient secret storage

### 3. Backend Detection
- Secure environment variable detection
- No hardcoded credentials in code
- Graceful fallbacks for missing configurations

### 4. Error Handling
- Comprehensive error logging without exposing secrets
- Fallback chains for high availability
- User-friendly error messages

## 🔄 Secret Rotation

### Doppler (Recommended)
Secrets are rotated via Doppler Dashboard or CLI:
```bash
# Update secret in Doppler
doppler secrets set DATABASE_URL="new-connection-string"

# Secrets auto-sync to connected services (Vercel, etc.)
```

### Manual Rotation
The SecretsVault logs rotation instructions for manual backends:
```python
vault.rotate_secret("database_url", "new-value")
# Logs: Instructions for manual rotation via Doppler Dashboard
```

## 🚀 Deployment

### Vercel + Doppler (Recommended)
1. Configure Doppler integration with Vercel
2. Set `DOPPLER_TOKEN` in Vercel environment variables
3. Doppler automatically injects all secrets
4. Deploy normally - SecretsVault auto-detects Doppler

### Environment Variables
```bash
# Production
DOPPLER_TOKEN=dp.st.production.xxxx
DOPPLER_PROJECT=ruleiq
DOPPLER_CONFIG=prd

# Development  
DOPPLER_TOKEN=dp.st.development.xxxx
DOPPLER_PROJECT=ruleiq
DOPPLER_CONFIG=dev
```

## 🛠️ Troubleshooting

### Doppler Not Detected
```bash
# Check environment variables
echo $DOPPLER_TOKEN
echo $DOPPLER_PROJECT

# Test health check
python config/secrets_vault.py health
```

### API Access Issues
```bash
# Test API endpoints
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/secrets-vault/health
```

### Secret Not Found
1. Check Doppler Dashboard for secret existence
2. Verify environment variable naming (uppercase)
3. Test with vault-style naming: `VAULT_SECRET_<KEY>`

## 📈 Performance

- **LRU Cache**: 100 entry limit for frequently accessed secrets
- **Lazy Loading**: Secrets loaded only when requested
- **Connection Pooling**: AWS clients reuse connections
- **Memory Efficient**: Minimal memory footprint per secret

## 🔗 Integration Status

✅ **FastAPI Integration**: Complete with REST API  
✅ **Settings Integration**: Pydantic Settings with vault support  
✅ **Health Monitoring**: Comprehensive health checks  
✅ **Error Handling**: Graceful fallbacks and logging  
✅ **Multi-Platform**: Doppler, Vercel, AWS, Local support  
✅ **Production Ready**: Security, caching, and monitoring

---

**🔐 SecretsVault**: Production-ready secrets management with Doppler integration for the ruleIQ compliance platform.