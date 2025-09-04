# Postman Environment Setup with Doppler Integration

## Environment Files Overview

### 📁 Available Environment Files

1. **`environment-doppler-synced.json`** ⭐ RECOMMENDED
   - **Purpose**: Auto-synced from Doppler secrets
   - **Updates**: Run `./scripts/sync-doppler-to-postman.sh` to refresh
   - **Contains**: All 50 Doppler secrets
   - **Security**: Contains actual secret values - DO NOT COMMIT

2. **`environment-development.json`**
   - **Purpose**: Development environment template
   - **Base URL**: `http://localhost:8000`
   - **Secrets**: References Doppler via `{{DOPPLER_*}}` placeholders
   - **Use Case**: Local development testing

3. **`environment-production.json`**
   - **Purpose**: Production environment template
   - **Base URL**: `https://api.ruleiq.com`
   - **Secrets**: References Doppler via `{{DOPPLER_*}}` placeholders
   - **Use Case**: Production API testing

4. **`newman-environment-doppler.json`**
   - **Purpose**: Newman CLI automated testing
   - **Format**: Simplified for CLI usage
   - **Contains**: Critical secrets only

## 🔧 Setup Instructions

### Step 1: Import Collection and Environment

1. Open Postman
2. Click **Import** button
3. Select files:
   - Collection: `postman/ruleIQ-api-collection.json`
   - Environment: `postman/environment-doppler-synced.json`

### Step 2: Verify Doppler Integration

The synced environment includes all Doppler secrets with prefix `doppler_`:
- `doppler_database-url`
- `doppler_jwt-secret-key`
- `doppler_google-ai-api-key`
- `doppler_openai-api-key`
- `doppler_encryption-key`
- And 45 more...

### Step 3: Configure Active Environment

1. Click the environment dropdown (top-right)
2. Select **"RuleIQ dev (Doppler Synced)"**
3. Verify the base_url is correct:
   - Development: `http://localhost:8000`
   - Production: Update as needed

## 🔄 Syncing with Doppler

### Automatic Sync Script

```bash
# Run this to update Postman environment from Doppler
./scripts/sync-doppler-to-postman.sh
```

This script:
- ✅ Fetches all secrets from current Doppler environment
- ✅ Creates Postman-compatible environment file
- ✅ Creates Newman-compatible environment file
- ✅ Adds files to .gitignore for security

### Manual Doppler Commands

```bash
# Check current Doppler config
doppler configs

# Switch environment
doppler configure set config dev  # or staging, production

# View all secrets
doppler secrets

# Get specific secret
doppler secrets get DATABASE_URL
```

## 🔐 Security Best Practices

### DO NOT:
- ❌ Commit `environment-doppler-synced.json` to git
- ❌ Share environment files with actual secret values
- ❌ Store tokens in collection files

### DO:
- ✅ Use Doppler for all secret management
- ✅ Run sync script when secrets change
- ✅ Keep environment files in `.gitignore`
- ✅ Use environment variables for all sensitive data

## 🧪 Testing Workflows

### Local Development Testing

1. Start backend:
   ```bash
   doppler run -- uvicorn main:app --reload
   ```

2. Import environment: `environment-doppler-synced.json`

3. Run authentication flow:
   - POST `/api/v1/auth/register` - Create test user
   - POST `/api/v1/auth/login` - Get access token
   - Token auto-saved to `access_token` variable

4. Test authenticated endpoints with token

### Newman CLI Testing

```bash
# Run full test suite
newman run postman/ruleIQ-api-collection.json \
  -e postman/newman-environment-doppler.json \
  --reporters cli,json \
  --reporter-json-export test-results.json

# Run specific folder
newman run postman/ruleIQ-api-collection.json \
  --folder "Authentication" \
  -e postman/newman-environment-doppler.json
```

### CI/CD Integration

```yaml
# .github/workflows/api-tests.yml
name: API Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: dopplerhq/cli-action@v1
      - run: |
          ./scripts/sync-doppler-to-postman.sh
          npm install -g newman
          newman run postman/ruleIQ-api-collection.json \
            -e postman/newman-environment-doppler.json
```

## 📊 Environment Variables Reference

### Core Variables
| Variable | Description | Source |
|----------|-------------|--------|
| `base_url` | API base URL | Manual/Doppler |
| `api_version` | API version (v1) | Doppler |
| `access_token` | JWT access token | Runtime |
| `refresh_token` | JWT refresh token | Runtime |

### Doppler Secrets (Auto-synced)
| Variable | Description | Prefix |
|----------|-------------|--------|
| `doppler_database-url` | PostgreSQL connection | `doppler_` |
| `doppler_jwt-secret-key` | JWT signing key | `doppler_` |
| `doppler_google-ai-api-key` | Google AI API | `doppler_` |
| `doppler_openai-api-key` | OpenAI API | `doppler_` |
| `doppler_encryption-key` | Data encryption | `doppler_` |

### Test Data Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `test_user_email` | Test account email | test@example.com |
| `test_user_password` | Test account password | Test123!@# |
| `test_business_profile_id` | Test profile ID | (Set at runtime) |

## 🚨 Troubleshooting

### Issue: Secrets not loading
**Solution**: Run sync script:
```bash
./scripts/sync-doppler-to-postman.sh
```

### Issue: Authentication failing
**Solution**: Check JWT token:
1. Login via `/api/v1/auth/login`
2. Verify `access_token` is set in environment
3. Check token expiry (default: 30 minutes)

### Issue: Wrong environment
**Solution**: Verify Doppler config:
```bash
doppler configs
doppler configure set config dev  # Switch to dev
```

### Issue: Newman tests failing
**Solution**: Ensure backend is running:
```bash
doppler run -- uvicorn main:app --reload
```

## 📝 Notes

- The collection contains 79 endpoints across 9 service areas
- All endpoints use `/api/v1/` prefix
- Authentication uses Bearer token scheme
- Doppler manages 50+ secrets across environments
- Environment files are git-ignored for security

## 🔗 Related Documentation

- [Postman Collection](./ruleIQ-api-collection.json)
- [Validation Report](./VALIDATION_REPORT.md)
- [Sync Script](../scripts/sync-doppler-to-postman.sh)
- [Doppler Dashboard](https://dashboard.doppler.com)

---
Last Updated: 2025-08-26
Generated by: RuleIQ API Environment Setup