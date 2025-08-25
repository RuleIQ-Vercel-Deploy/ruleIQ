# 🔐 Postman + Doppler Integration Guide

## Overview
This guide shows how to use Postman with your existing Doppler secrets management for the ruleIQ API testing.

## 📋 Prerequisites
- Doppler CLI installed and configured
- Postman Desktop App (required for environment variable access)
- ruleIQ Doppler project setup completed

## 🚀 Quick Setup

### 1. Verify Doppler Setup
```bash
# Check login status
doppler whoami

# Check project configuration
doppler configure get project  # Should show: ruleiq
doppler configure get config   # Should show: dev, staging, or prod
```

### 2. Set Environment Variables for Postman
```bash
# Export all secrets to environment (for Postman Desktop)
eval $(doppler secrets --format env-no-quotes)

# Or run Postman with Doppler secrets loaded
doppler run -- /snap/postman/current/Postman
```

### 3. Import Enhanced Collection
Import the `ruleiq_postman_collection_with_doppler.json` file which includes:
- Auto-loading of Doppler secrets
- JWT token management
- Environment variable integration

## 🔧 Integration Methods

### Method 1: Environment Variable Export (Recommended)
```bash
# Export Doppler secrets to shell environment
eval $(doppler secrets download --no-file --format env-no-quotes)

# Launch Postman (it will inherit environment variables)
postman
```

### Method 2: Newman CLI with Doppler
```bash
# Run collections via command line with Doppler
doppler run -- newman run ruleiq_postman_collection_with_doppler.json

# Or with specific environment file
doppler run -- newman run collection.json -e environment.json
```

### Method 3: Pre-request Scripts (Advanced)
The enhanced collection includes pre-request scripts that:
- Check for Doppler environment variables
- Fetch secrets via Doppler API (requires DOPPLER_TOKEN)
- Auto-refresh JWT tokens
- Validate credentials before requests

## 📊 Environment Variables Mapping

### From Doppler → Postman Environment
| Doppler Secret | Postman Variable | Usage |
|----------------|------------------|-------|
| `DATABASE_URL` | `database_url` | Database connection |
| `REDIS_URL` | `redis_url` | Redis cache |
| `JWT_SECRET_KEY` | `jwt_secret` | Token validation |
| `GOOGLE_API_KEY` | `google_api_key` | AI services |
| `TEST_USER_EMAIL` | `test_user_email` | Login testing |
| `TEST_USER_PASSWORD` | `test_user_password` | Login testing |

### Manual Environment Setup
If automatic loading doesn't work, set these in Postman Environment:

```json
{
  "base_url": "http://localhost:8000",
  "jwt_token": "",
  "DOPPLER_TOKEN": "dp.st.dev.your_token_here"
}
```

## 🔄 Automated Workflows

### 1. Login Flow with Doppler Credentials
The collection includes an automated login request that:
- Uses `TEST_USER_EMAIL` and `TEST_USER_PASSWORD` from Doppler
- Automatically saves JWT token to environment
- Sets user_id and business_profile_id

### 2. API Key Validation
Pre-request scripts verify that required API keys are available:
```javascript
// Check for Google API key before AI requests
const apiKey = pm.environment.get('google_api_key');
if (!apiKey) {
    console.error('❌ Google API key missing from Doppler');
}
```

## 🛠️ Troubleshooting

### Issue: Environment Variables Not Loading
**Solution**: 
```bash
# Verify Doppler secrets are accessible
doppler secrets

# Check environment variable export
echo $GOOGLE_API_KEY
echo $DATABASE_URL

# Re-export if needed
eval $(doppler secrets download --no-file --format env-no-quotes)
```

### Issue: JWT Token Expired
**Solution**: The collection auto-detects expired tokens and shows refresh warnings. Use the refresh token endpoint or re-login.

### Issue: Postman Can't Access Process Environment
**Solution**: Use Postman Desktop App (not web version) and ensure it's launched after environment export.

## 🔒 Security Best Practices

### 1. Never Hardcode Secrets
```javascript
// ❌ Don't do this
const apiKey = "AIzaSyBxxxxxxxxxxxxxxxxxxxxxxx";

// ✅ Do this instead
const apiKey = pm.environment.get('google_api_key');
```

### 2. Use Doppler Service Tokens for CI/CD
```bash
# Create service token for automated testing
doppler service-tokens create postman-testing --config dev

# Use in Newman CLI
DOPPLER_TOKEN=dp.st.dev.xxx newman run collection.json
```

### 3. Separate Environments
- `dev` config: Development API keys and test credentials
- `staging` config: Staging environment secrets
- `prod` config: Production secrets (restricted access)

## 📈 Testing Workflows

### 1. Full API Test Suite
```bash
# Run complete test suite with Doppler secrets
doppler run -- newman run ruleiq_postman_collection_with_doppler.json \
  --reporters cli,json \
  --reporter-json-export test-results.json
```

### 2. Smoke Tests
```bash
# Quick health check with minimal endpoints
doppler run -- newman run collection.json \
  --folder "Health Check" \
  --folder "Authentication"
```

### 3. CI/CD Integration
```bash
# In GitHub Actions or similar
- name: Run API Tests
  env:
    DOPPLER_TOKEN: ${{ secrets.DOPPLER_TOKEN }}
  run: |
    doppler secrets download --no-file --format env >> $GITHUB_ENV
    newman run collection.json --reporters junit --reporter-junit-export results.xml
```

## 🎯 Advanced Features

### 1. Dynamic Secret Rotation
The collection can detect when secrets change in Doppler:
```javascript
// Pre-request script checks secret freshness
const lastSecretUpdate = pm.environment.get('secrets_last_updated');
const now = Date.now();
if (!lastSecretUpdate || (now - lastSecretUpdate) > 300000) { // 5 minutes
    // Refresh secrets from Doppler API
}
```

### 2. Multi-Environment Testing
```bash
# Test against different environments
doppler run --config dev -- newman run collection.json
doppler run --config staging -- newman run collection.json
```

### 3. Secret Validation
Pre-request scripts validate that all required secrets are present:
```javascript
const requiredSecrets = ['google_api_key', 'database_url', 'jwt_secret'];
const missingSecrets = requiredSecrets.filter(secret => 
    !pm.environment.get(secret)
);
if (missingSecrets.length > 0) {
    throw new Error(`Missing secrets: ${missingSecrets.join(', ')}`);
}
```

## 📚 Resources

- **Doppler Documentation**: https://docs.doppler.com/
- **Postman Environment Variables**: https://learning.postman.com/docs/sending-requests/variables/
- **Newman CLI**: https://learning.postman.com/docs/running-collections/using-newman-cli/

## ✅ Quick Verification

Test your setup:
```bash
# 1. Check Doppler connection
doppler secrets --only-names

# 2. Export environment
eval $(doppler secrets download --no-file --format env-no-quotes)

# 3. Verify key variables
echo "Database: ${DATABASE_URL:0:20}..."
echo "Google API: ${GOOGLE_API_KEY:0:20}..."

# 4. Launch Postman
postman &

# 5. Import enhanced collection and test!
```

---

**Generated**: 2025-08-22  
**ruleIQ API Version**: v2.0.0  
**Doppler Integration**: Production-Ready