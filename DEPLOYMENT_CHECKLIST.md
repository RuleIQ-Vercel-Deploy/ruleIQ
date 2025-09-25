# 📋 RuleIQ Deployment Checklist

## Pre-Deployment Verification

### 🔐 Secrets Configuration
- [ ] Verify `VERCEL_ORG_ID` is set in GitHub/Doppler secrets
- [ ] Verify `VERCEL_PROJECT_ID` is set in GitHub/Doppler secrets
- [ ] Verify `VERCEL_TOKEN` is set with correct permissions
- [ ] Verify `DATABASE_URL` points to Neon production database
- [ ] Verify `JWT_SECRET` is set (32+ characters)
- [ ] Verify `SECRET_KEY` is set (32+ characters)

### 🗄️ Database Setup
- [ ] Neon database is provisioned
- [ ] Connection string is tested
- [ ] Database migrations are up to date
- [ ] Initial data/fixtures are loaded

### 🧪 Testing
- [ ] All unit tests pass locally
- [ ] Integration tests pass
- [ ] API endpoint tests pass
- [ ] Frontend builds without errors

### 📦 Build Verification
- [ ] Python dependencies are locked (`requirements.txt`)
- [ ] No syntax errors in Python code
- [ ] Environment variables are documented
- [ ] Docker image builds successfully (if applicable)

## Deployment Steps

### 1️⃣ Prepare Repository
- [ ] Latest changes are committed
- [ ] Branch is up to date with main
- [ ] Git remote is set to organization repo

### 2️⃣ Configure Secrets
#### Option A: GitHub Secrets
- [ ] Set all required secrets in GitHub Actions

#### Option B: Doppler
- [ ] Configure Doppler project
- [ ] Set `DOPPLER_TOKEN` in GitHub Actions
- [ ] Verify all secrets in Doppler dashboard

### 3️⃣ Deploy
- [ ] Push to main branch OR
- [ ] Trigger workflow manually
- [ ] Monitor GitHub Actions for deployment status
- [ ] Check deployment URL

## Post-Deployment Verification

### ✅ Application Health
- [ ] Application loads successfully
- [ ] API health endpoint responds
- [ ] Database connectivity works
- [ ] Authentication flows work

### 🔍 Monitoring
- [ ] Check error logs in Vercel dashboard
- [ ] Verify Sentry integration (if configured)
- [ ] Check performance metrics
- [ ] Test critical user flows

### 📊 Performance
- [ ] Page load time is acceptable
- [ ] API response times are within limits
- [ ] Database queries are optimized
- [ ] No memory leaks detected

## Rollback Plan

If issues are detected:

1. **Immediate Actions**
   - [ ] Document the issue
   - [ ] Capture error logs
   - [ ] Notify team members

2. **Rollback Steps**
   ```bash
   # Revert to previous deployment
   vercel rollback

   # Or redeploy previous commit
   git revert HEAD
   git push origin main
   ```

3. **Post-Rollback**
   - [ ] Verify rollback successful
   - [ ] Investigate root cause
   - [ ] Create fix and test locally
   - [ ] Schedule maintenance window if needed

## Emergency Contacts

- **DevOps Lead**: [Contact Info]
- **Database Admin**: [Contact Info]
- **Security Team**: [Contact Info]
- **On-Call Engineer**: [Contact Info]

## Resources

- [Vercel Dashboard](https://vercel.com/dashboard)
- [GitHub Actions](https://github.com/RuleIQ-Vercel-Deploy/ruleIQ/actions)
- [Doppler Dashboard](https://dashboard.doppler.com)
- [Neon Console](https://console.neon.tech)

---

Last Updated: [Date]
Next Review: [Date + 30 days]