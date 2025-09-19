# RuleIQ Frontend Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Pusher Configuration](#pusher-configuration)
4. [Vercel KV Setup](#vercel-kv-setup)
5. [Doppler Integration](#doppler-integration)
6. [Deployment Configuration](#deployment-configuration)
7. [Security Headers](#security-headers)
8. [Cron Jobs](#cron-jobs)
9. [Smoke Tests](#smoke-tests)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

- Node.js 18+ and pnpm 8+
- Vercel CLI: `pnpm add -g vercel`
- Doppler CLI (optional): `curl -Ls https://cli.doppler.com/install.sh | sh`
- Access to production environment variables
- Git repository with main branch protection

## Environment Setup

### 1. Local Development

```bash
# Copy environment template
cp env.production.template .env.production.local

# Fill in your production values
# NEVER commit .env.production.local to git
```

### 2. Staging Environment

```bash
# Use Doppler for staging
doppler setup
doppler secrets download --config staging > .env.staging.local
```

### 3. Production Environment

Production secrets should be managed through Vercel's dashboard or Doppler, never stored locally.

## Pusher Configuration

### 1. Create Pusher App

1. Sign up at [pusher.com](https://pusher.com)
2. Create new app: "ruleiq-production"
3. Select cluster closest to your users (e.g., `eu` for UK)
4. Enable client events if needed

### 2. Configure Environment Variables

```bash
# In Vercel Dashboard or Doppler
NEXT_PUBLIC_PUSHER_KEY=your-app-key
NEXT_PUBLIC_PUSHER_CLUSTER=eu
PUSHER_APP_ID=your-app-id
PUSHER_SECRET=your-app-secret
```

### 3. Test Connection

```typescript
// Test in browser console
const pusher = new Pusher(process.env.NEXT_PUBLIC_PUSHER_KEY, {
  cluster: process.env.NEXT_PUBLIC_PUSHER_CLUSTER
});
pusher.connection.bind('connected', () => console.log('Connected!'));
```

## Vercel KV Setup

### 1. Provision KV Store

```bash
# Via Vercel CLI
vercel env add VERCEL_KV_REST_API_URL
vercel env add VERCEL_KV_REST_API_TOKEN

# Or via Dashboard
# Project Settings > Storage > Create Database > KV
```

### 2. Configure Regions

For UK compliance, select European regions:
- Primary: `lhr1` (London)
- Replica: `fra1` (Frankfurt)

### 3. Test KV Connection

```typescript
// pages/api/test-kv.ts
import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  await kv.set('test', 'value');
  const value = await kv.get('test');
  res.json({ success: true, value });
}
```

## Doppler Integration

### 1. Setup Project

```bash
# Install Doppler CLI
curl -Ls https://cli.doppler.com/install.sh | sh

# Login and setup
doppler login
doppler setup --project ruleiq --config production
```

### 2. Sync with Vercel

```bash
# Install Vercel integration
doppler integrations create vercel

# Sync secrets
doppler secrets sync
```

### 3. Local Development with Doppler

```bash
# Run with production secrets (BE CAREFUL!)
doppler run --config production -- pnpm dev

# Run with staging secrets (SAFER)
doppler run --config staging -- pnpm dev
```

## Deployment Configuration

### 1. vercel.json Settings

```json
{
  "functions": {
    "app/api/pusher/auth/route.ts": {
      "maxDuration": 10
    },
    "app/api/cron/[...path]/route.ts": {
      "maxDuration": 60
    }
  },
  "regions": ["lhr1"],
  "env": {
    "NODE_ENV": "production"
  }
}
```

### 2. Build Configuration

```json
// package.json
{
  "scripts": {
    "build:production": "NODE_ENV=production next build",
    "deploy:production": "pnpm build:production && vercel --prod",
    "deploy:staging": "vercel"
  }
}
```

## Security Headers

### 1. Content Security Policy

```typescript
// middleware.ts
const cspHeader = `
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval' https://*.pusher.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self' data:;
  connect-src 'self' https://*.pusher.com https://api.ruleiq.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
`;
```

### 2. Apply Headers

```typescript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()'
          }
        ]
      }
    ];
  }
};
```

## Cron Jobs

### 1. Setup Cron Endpoints

```typescript
// app/api/cron/daily-audit/route.ts
export async function GET(request: Request) {
  const authHeader = request.headers.get('authorization');
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return new Response('Unauthorized', { status: 401 });
  }

  // Run daily audit
  await runDailyAudit();

  return Response.json({ success: true });
}
```

### 2. Configure in Vercel

```json
// vercel.json
{
  "crons": [{
    "path": "/api/cron/daily-audit",
    "schedule": "0 0 * * *"
  }]
}
```

## Smoke Tests

### 1. Health Check

```bash
# Test API health
curl https://your-domain.com/api/health

# Expected response
{"status":"healthy","timestamp":"2024-01-01T00:00:00Z"}
```

### 2. Pusher Authentication

```bash
# Test Pusher auth endpoint
curl -X POST https://your-domain.com/api/pusher/auth \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"socket_id":"12345.67890","channel_name":"private-test"}'
```

### 3. Critical Pages

```bash
# Test main pages return 200
for path in "/" "/dashboard" "/assessment" "/login"; do
  echo "Testing $path..."
  curl -s -o /dev/null -w "%{http_code}" "https://your-domain.com$path"
done
```

### 4. Automated Smoke Test Script

```typescript
// scripts/smoke-test.ts
import axios from 'axios';

const BASE_URL = process.env.DEPLOYMENT_URL || 'https://your-domain.com';

async function runSmokeTests() {
  const tests = [
    { name: 'Health Check', url: '/api/health', expectedStatus: 200 },
    { name: 'Homepage', url: '/', expectedStatus: 200 },
    { name: 'Dashboard', url: '/dashboard', expectedStatus: 200 },
    { name: 'Pusher Auth', url: '/api/pusher/auth', expectedStatus: 401 }, // Without auth
  ];

  let failures = 0;

  for (const test of tests) {
    try {
      const response = await axios.get(`${BASE_URL}${test.url}`, {
        validateStatus: () => true
      });

      if (response.status !== test.expectedStatus) {
        console.error(`❌ ${test.name}: Expected ${test.expectedStatus}, got ${response.status}`);
        failures++;
      } else {
        console.log(`✅ ${test.name}: OK`);
      }
    } catch (error) {
      console.error(`❌ ${test.name}: Failed with error`, error.message);
      failures++;
    }
  }

  if (failures > 0) {
    console.error(`\n❌ ${failures} test(s) failed`);
    process.exit(1);
  } else {
    console.log(`\n✅ All smoke tests passed`);
  }
}

runSmokeTests();
```

## Deployment Process

### 1. Pre-deployment Checklist

- [ ] All tests passing: `pnpm test`
- [ ] Type checking passes: `pnpm typecheck`
- [ ] Linting passes: `pnpm lint`
- [ ] Build succeeds: `pnpm build:production`
- [ ] Environment variables configured in Vercel
- [ ] Database migrations completed
- [ ] Feature flags configured

### 2. Deploy to Staging

```bash
# Deploy to staging
vercel

# Run smoke tests
pnpm smoke:staging
```

### 3. Deploy to Production

```bash
# Deploy to production
vercel --prod

# Run smoke tests
pnpm smoke:production

# Monitor for 15 minutes
vercel logs --follow
```

### 4. Rollback if Needed

```bash
# List deployments
vercel ls

# Rollback to previous
vercel rollback [deployment-url]
```

## Troubleshooting

### Common Issues

#### Pusher Connection Failures
- Check if `NEXT_PUBLIC_PUSHER_KEY` is set in Vercel
- Verify cluster matches your Pusher app settings
- Check browser console for CORS errors

#### KV Connection Issues
- Ensure `VERCEL_KV_REST_API_URL` includes `https://`
- Verify token has correct permissions
- Check KV dashboard for rate limits

#### Build Failures
- Clear Next.js cache: `rm -rf .next`
- Check for missing environment variables
- Verify Node.js version matches production

#### CORS Errors
- Update `CORS_ALLOWED_ORIGINS` in environment
- Check API routes include proper headers
- Verify domain in Pusher app settings

### Debug Commands

```bash
# Check environment variables
vercel env ls

# View recent logs
vercel logs --since 1h

# Check function logs
vercel logs --function api/pusher/auth

# Monitor real-time
vercel dev --debug
```

## Security Considerations

1. **Never expose secrets in client-side code**
2. **Use `NEXT_PUBLIC_` prefix only for public values**
3. **Rotate secrets quarterly**
4. **Enable Vercel's DDoS protection**
5. **Use rate limiting on all API routes**
6. **Implement CSP headers strictly**
7. **Regular security audits with `pnpm audit`**

## Support

For deployment issues:
- Check Vercel Status: https://vercel.com/status
- Review Pusher Status: https://status.pusher.com
- Contact DevOps team: devops@ruleiq.com