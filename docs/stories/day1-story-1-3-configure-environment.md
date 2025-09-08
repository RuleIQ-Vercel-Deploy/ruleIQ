# Story 1.3: Complete Environment Configuration

## Story Details
**ID**: DEPLOY-003  
**Priority**: P0 (Critical Blocker)  
**Estimated Time**: 2 hours  
**Assigned To**: Backend Developer / DevOps  
**Day**: 1 (Sept 9)  
**Status**: Ready for Development  

## User Story
As a system administrator,  
I want all required environment variables configured,  
so that all services can connect and function properly.

## Technical Context
**Current Issue**: Missing `.env` file with required service configurations  
**Impact**: Services cannot connect to external APIs, databases, or send emails  
**Required Services**: Google AI API, OAuth, SMTP, PostgreSQL, Redis, Stripe  

## Acceptance Criteria
- [ ] Create `.env` file from template with all required values
- [ ] Configure Google AI API key and verify connectivity
- [ ] Set up OAuth credentials for all providers
- [ ] Configure SMTP settings and test email sending
- [ ] Set database and Redis connection strings
- [ ] Document all required environment variables
- [ ] Create `.env.example` with sanitized values

## Implementation Steps
1. **Create Base Environment File** (15 min)
   ```bash
   # Copy from template if exists
   cp .env.example .env 2>/dev/null || touch .env
   
   # Set proper permissions
   chmod 600 .env
   ```

2. **Configure Database Connections** (20 min)
   ```bash
   # PostgreSQL
   DATABASE_URL=postgresql://user:password@localhost:5432/ruleiq
   
   # Redis
   REDIS_URL=redis://localhost:6379
   REDIS_DB=0
   ```

3. **Configure External APIs** (45 min)
   ```bash
   # Google AI API
   GOOGLE_AI_API_KEY=your_api_key_here
   GOOGLE_AI_MODEL=gemini-pro
   
   # OAuth Providers
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   GITHUB_CLIENT_ID=your_client_id
   GITHUB_CLIENT_SECRET=your_client_secret
   
   # NextAuth
   NEXTAUTH_URL=http://localhost:3000
   NEXTAUTH_SECRET=generate_with_openssl_rand_base64_32
   ```

4. **Configure Email Service** (20 min)
   ```bash
   # SMTP Configuration
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   SMTP_FROM=noreply@ruleiq.com
   ```

5. **Configure Payment Gateway** (10 min)
   ```bash
   # Stripe
   STRIPE_PUBLIC_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

6. **Test Connections** (10 min)
   ```python
   # Create test script: test_env.py
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   # Test database connection
   # Test Redis connection
   # Test API keys
   # Test SMTP
   ```

## Environment Variables Documentation
```markdown
## Required Environment Variables

### Database
- DATABASE_URL: PostgreSQL connection string
- REDIS_URL: Redis connection string

### Authentication
- NEXTAUTH_URL: Application URL
- NEXTAUTH_SECRET: Session encryption key (32 chars)

### External APIs
- GOOGLE_AI_API_KEY: Google AI API key
- GOOGLE_CLIENT_ID: OAuth client ID
- GOOGLE_CLIENT_SECRET: OAuth client secret

### Email
- SMTP_HOST: Email server host
- SMTP_PORT: Email server port
- SMTP_USER: Email username
- SMTP_PASSWORD: Email password

### Payments
- STRIPE_PUBLIC_KEY: Publishable key
- STRIPE_SECRET_KEY: Secret key
```

## Verification Checklist
- [ ] All environment variables set
- [ ] Database connection successful
- [ ] Redis connection successful
- [ ] Google AI API responds
- [ ] OAuth flow works
- [ ] Test email sends successfully
- [ ] Payment gateway connects

## Commands
```bash
# Generate secure secret
openssl rand -base64 32

# Test database connection
psql $DATABASE_URL -c "SELECT 1"

# Test Redis connection
redis-cli ping

# Validate .env file
python scripts/validate_env.py
```

## Security Checklist
- [ ] `.env` file added to `.gitignore`
- [ ] No secrets in code or commits
- [ ] `.env.example` contains only placeholder values
- [ ] File permissions set to 600
- [ ] Secrets rotated if previously exposed

## Definition of Done
- [ ] All required environment variables configured
- [ ] All service connections tested and working
- [ ] `.env.example` created with documentation
- [ ] Security checklist completed
- [ ] Team notified of new configuration
- [ ] Documentation updated

## Rollback Plan
1. Keep backup of working `.env` file
2. If services fail, restore previous configuration
3. Test each service individually to isolate issues

## Notes
- Use strong, unique passwords for all services
- Consider using a secrets management service for production
- Document any service-specific configuration quirks
- Set up monitoring for API rate limits

---
**Created**: September 8, 2024  
**Last Updated**: September 8, 2024  
**Story Points**: 3