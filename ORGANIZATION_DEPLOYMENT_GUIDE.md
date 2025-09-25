# 🏢 ruleIQ Organization-Level Deployment Guide

## ✅ Organization Transfer Complete!

**New Repository**: https://github.com/RuleIQ-Vercel-Deploy/ruleIQ.git
**Organization**: RuleIQ-Vercel-Deploy
**Status**: Ready for production deployment with full Neon Database integration

## Immediate Next Steps

### 1. Configure Doppler for Secrets Management

**🔐 Using Doppler for Centralized Secrets Management**

```bash
# Run the Doppler setup script
./scripts/deploy/doppler-setup.sh

# Or manually setup Doppler:
doppler setup
# Select: RuleIQ-Vercel-Deploy organization
# Select: ruleiq project
# Select: production environment

# Verify all secrets are configured
doppler secrets

# Generate service token for GitHub Actions
doppler configs tokens create github-actions --config production --plain
```

**Add ONLY ONE Secret to GitHub Actions:**
Navigate to: https://github.com/RuleIQ-Vercel-Deploy/ruleIQ/settings/secrets/actions

```bash
DOPPLER_TOKEN: [Your Doppler service token from above]
```

**All Other Secrets Managed in Doppler:**
- `VERCEL_TOKEN` - Vercel authentication token
- `VERCEL_ORG_ID` - RuleIQ-Vercel-Deploy organization ID
- `VERCEL_PROJECT_ID` - Project ID after transfer
- `DATABASE_URL` - Neon organization database URL
- `JWT_SECRET` - Secure 32+ character secret
- `SECRET_KEY` - Secure 32+ character secret
- Optional: `OPENAI_API_KEY`, `REDIS_URL`, `SENTRY_DSN`

### 2. Deploy Using Doppler Workflow

**Important**: The standard workflow uses GitHub secrets directly. For Doppler integration:
- **Doppler-enabled workflow**: `.github/workflows/deploy-vercel-doppler.yml`
- **Standard workflow**: `.github/workflows/deploy-vercel.yml`

When using Doppler workflow:
1. Set DOPPLER_TOKEN in GitHub Actions secrets
2. Configure all other secrets in Doppler dashboard
3. Push to main branch or manually trigger via GitHub Actions

### 3. Neon Database Organization Setup

```sql
-- Use organization-level Neon database
-- Connection URL format:
postgresql://[org-user]:[password]@[org-host]/ruleiq?sslmode=require&pgbouncer=true

-- Features now available:
-- ✅ Connection pooling
-- ✅ Database branching
-- ✅ Point-in-time recovery
-- ✅ Enhanced monitoring
-- ✅ Team access
```

### 3. Deploy to Production

#### Option A: Automatic Deployment (Recommended)
```bash
# Push to main branch triggers automatic deployment
git push origin main

# Monitor deployment at:
# https://github.com/RuleIQ-Vercel-Deploy/ruleIQ/actions
```

#### Option B: Manual Deployment
```bash
# Using Vercel CLI with organization context
vercel --prod --scope ruleiq-vercel-deploy

# Or trigger manual deployment via GitHub Actions
# Go to: Actions → Vercel Deployment → Run workflow
```

## Organization Benefits Now Available

### 🚀 Enhanced Database Features
- **Connection Pooling**: Optimized for serverless functions
- **Database Branching**: Separate databases for staging/production
- **Advanced Monitoring**: Real-time database performance insights
- **Team Access**: Multiple developers can access database
- **Point-in-time Recovery**: Enhanced backup capabilities

### 🔒 Enhanced Security
- **Organization-level secrets management**
- **Team-based access controls**
- **Enhanced audit logging**
- **Production-grade security headers**
- **Advanced rate limiting**

### 📊 Enhanced Monitoring
- **Organization-level analytics**
- **Team performance dashboards**
- **Advanced error tracking**
- **Custom domain management**
- **Professional deployment notifications**

## Deployment Verification Checklist

### ✅ Pre-Deployment
- [ ] GitHub Actions secrets updated in organization repository
- [ ] Neon Database configured at organization level
- [ ] Vercel project transferred and linked
- [ ] Environment variables configured
- [ ] Team access permissions set

### ✅ During Deployment
- [ ] GitHub Actions workflow executes successfully
- [ ] Vercel build completes without errors
- [ ] Database connectivity established
- [ ] Organization context validated
- [ ] Deployment URL generated

### ✅ Post-Deployment
- [ ] Health endpoints responding (/health, /ready)
- [ ] Database connection pooling active
- [ ] API authentication working
- [ ] AI services responding (if configured)
- [ ] Organization-level monitoring active
- [ ] Team notifications configured

## Production URLs

After successful deployment, your application will be available at:
- **Production**: https://[your-app].vercel.app
- **API Documentation**: https://[your-app].vercel.app/docs
- **Health Check**: https://[your-app].vercel.app/health
- **Organization Dashboard**: Vercel organization dashboard

## Team Collaboration

### Adding Team Members
1. **Vercel Organization**: Add team members in Vercel dashboard
2. **GitHub Repository**: Add collaborators to organization repository
3. **Neon Database**: Grant database access to team members
4. **Deployment Access**: Configure deployment permissions

### Deployment Permissions
- **Admins**: Full deployment and configuration access
- **Developers**: Deploy to preview environments
- **Viewers**: Read-only access to deployments and logs

## Monitoring and Maintenance

### Real-time Monitoring
- **Vercel Analytics**: Organization-level performance metrics
- **Database Monitoring**: Neon organization dashboard
- **Error Tracking**: Sentry organization integration
- **Uptime Monitoring**: Custom monitoring solutions

### Regular Maintenance
- **Security Updates**: Regular dependency updates
- **Database Maintenance**: Neon organization maintenance windows
- **Performance Optimization**: Based on organization analytics
- **Team Training**: Keep team updated on deployment procedures

## Support and Troubleshooting

### Organization-Level Support
- **Vercel Support**: Enhanced support for organization accounts
- **Neon Support**: Team/organization support channels
- **GitHub Support**: Organization-level GitHub support
- **Internal Team**: Documented procedures for team support

### Common Issues
1. **Permission Errors**: Verify organization access levels
2. **Database Connection**: Check organization database URL
3. **Environment Variables**: Confirm organization-level secrets
4. **Deployment Failures**: Review organization workflow logs

## Next Steps After Deployment

1. **Custom Domain**: Configure professional domain
2. **Advanced Monitoring**: Set up comprehensive monitoring
3. **Team Training**: Train team on organization procedures
4. **Documentation**: Update team documentation
5. **Scaling**: Plan for organization-level scaling

## Local Development Dependencies

When running deployment scripts locally, ensure you have the following dependencies installed:

### Required Tools
- **Python 3.11+**: Required for all deployment scripts
- **Git**: For repository management

### Python Packages
```bash
pip install requests  # For API interactions
```

### Optional CLI Tools
- **Vercel CLI**: For direct deployment management
  ```bash
  npm install -g vercel
  ```
- **Doppler CLI**: For secrets management (if using Doppler)
  ```bash
  # macOS
  brew install dopplerhq/cli/doppler

  # Linux
  curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh | sudo sh
  ```
- **jq**: For JSON processing
  ```bash
  # macOS
  brew install jq

  # Linux
  sudo apt-get install jq  # Debian/Ubuntu
  sudo yum install jq      # CentOS/RHEL
  ```

### Script Requirements File
For convenience, install Python dependencies:
```bash
pip install -r scripts/deploy/requirements.txt
```

---

**🎉 Congratulations!** Your ruleIQ application is now ready for organization-level production deployment with full Neon Database integration and enhanced team collaboration features.

**Ready to deploy?** Push to main branch or run the deployment workflow!