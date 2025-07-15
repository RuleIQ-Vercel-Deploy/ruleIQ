# Critical Fixes Setup Guide

## Overview

This document provides setup instructions for the critical database and encryption fixes implemented for the ruleIQ third-party integration system.

## ⚠️ Critical Requirements

Before deploying to production, you **MUST** complete these steps:

### 1. Environment Variables

Add these required environment variables to your `.env` file:

```bash
# Credential Encryption (REQUIRED)
CREDENTIAL_MASTER_KEY=your-32-character-master-key-here
DEPLOYMENT_ID=production-deployment-v1

# Database (if not already configured)
DATABASE_URL=postgresql://user:password@localhost/ruleiq

# Optional: Enhanced Security
CREDENTIAL_ENCRYPTION_ALGORITHM=AES-256
CREDENTIAL_KEY_DERIVATION_ITERATIONS=100000
```

### 2. Generate Master Encryption Key

**Generate a secure master key:**

```bash
# Generate a 32-character secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use OpenSSL
openssl rand -base64 32
```

**⚠️ CRITICAL SECURITY NOTES:**
- Store this key securely (use a secret management service in production)
- Never commit this key to version control
- Losing this key means losing access to ALL stored credentials
- Use different keys for different environments (dev/staging/prod)

### 3. Database Migration

Run the migration to create the new tables:

```bash
# From the ruleIQ root directory
python database/migrations/create_integration_tables.py
```

This creates the following tables:
- `integrations` - Integration configurations with encrypted credentials
- `evidence_collections` - Evidence collection requests and status
- `evidence_items` - Individual evidence items
- `integration_health_logs` - Health check history
- `evidence_audit_logs` - Audit trail for all operations

### 4. Database Indexes

The tables include performance indexes for:
- User and provider lookups
- Evidence collection queries
- Audit log searches
- Health monitoring

### 5. Test the Setup

**Test encryption system:**

```python
from core.security.credential_encryption import verify_encryption_health

# Test encryption/decryption
health = verify_encryption_health()
print(f"Encryption health: {health['status']}")
```

**Test database integration:**

```python
from database.services.integration_service import IntegrationService
from database.db_setup import get_async_db

# Test database connection
async def test_db():
    async for db in get_async_db():
        service = IntegrationService(db)
        # Test service initialization
        break

import asyncio
asyncio.run(test_db())
```

## 📋 Production Deployment Checklist

### Database Security
- [ ] Master encryption key generated and stored securely
- [ ] Database connection secured with SSL
- [ ] Database user has minimal required permissions
- [ ] Database backups configured and encrypted

### Application Security
- [ ] All environment variables configured
- [ ] Secret management system configured (AWS Secrets Manager, HashiCorp Vault, etc.)
- [ ] Audit logging enabled
- [ ] Rate limiting configured

### Integration Security
- [ ] Integration credentials stored encrypted
- [ ] API rate limits configured
- [ ] Health monitoring enabled
- [ ] Error handling tested

### Monitoring
- [ ] Database performance monitoring
- [ ] Encryption health monitoring
- [ ] Integration health monitoring
- [ ] Audit log monitoring

## 🔧 Usage Examples

### AWS Integration Configuration

```python
from database.services.integration_service import IntegrationService
from api.clients.base_api_client import APICredentials, AuthType

# Configure AWS integration
credentials = APICredentials(
    provider="aws",
    auth_type=AuthType.ROLE_ASSUMPTION,
    credentials={
        "role_arn": "arn:aws:iam::123456789012:role/ruleIQ-Evidence-Collection",
        "external_id": "unique-external-id"
    },
    region="us-east-1"
)

service = IntegrationService(db)
integration = await service.store_integration_config(
    user_id="user-123",
    provider="aws",
    credentials=credentials,
    health_info={"status": "healthy"}
)
```

### Evidence Collection

```python
from database.services.integration_service import EvidenceCollectionService

# Start evidence collection
evidence_service = EvidenceCollectionService(db)
collection = await evidence_service.create_evidence_collection(
    integration_id=str(integration.id),
    user_id="user-123",
    framework_id="soc2_type2",
    evidence_types_requested=["iam_policies", "iam_users"],
    business_profile={"company_size": "medium"}
)
```

## 🚨 Security Warnings

### What NOT to Do:
- ❌ Never store credentials in plaintext
- ❌ Never commit encryption keys to version control
- ❌ Never use the same encryption key across environments
- ❌ Never ignore encryption errors
- ❌ Never skip database migrations

### What TO Do:
- ✅ Always use the credential encryption system
- ✅ Always validate encryption health on startup
- ✅ Always use secure key storage in production
- ✅ Always monitor audit logs
- ✅ Always test integrations after deployment

## 🔍 Troubleshooting

### Encryption Errors

**"CREDENTIAL_MASTER_KEY environment variable is required"**
- Solution: Generate and set the master key environment variable

**"Failed to decrypt credentials"**
- Possible causes: Key changed, corrupted data, wrong environment
- Solution: Check key consistency, verify environment configuration

### Database Errors

**"Table 'integrations' doesn't exist"**
- Solution: Run the database migration script

**"Foreign key constraint fails"**
- Solution: Ensure user exists before creating integration

### Integration Errors

**"Authentication failed"**
- Solution: Verify credentials are correct and not expired

**"Rate limit exceeded"**
- Solution: Implement retry logic with exponential backoff

## 📞 Support

For issues with the critical fixes:

1. Check the logs in `/logs/` directory
2. Verify environment variables are set correctly
3. Test encryption system health
4. Check database connectivity
5. Validate integration credentials

## 📈 Performance Monitoring

Monitor these metrics:
- Encryption/decryption response times
- Database query performance
- Integration health check response times
- Evidence collection completion rates

Expected performance:
- Encryption: <10ms per operation
- Database queries: <100ms for typical operations
- Integration health checks: <5s per integration
- Evidence collection: 5-15 minutes for full collection

## 🎯 Success Criteria

The system is ready for production when:
- ✅ All database tables created successfully
- ✅ Encryption health check passes
- ✅ Test integrations can be configured
- ✅ Evidence collection completes successfully
- ✅ Audit logs are being created
- ✅ Health monitoring is working

---

**Remember: These fixes address critical security vulnerabilities. Do not deploy without implementing the encryption system and database models.**