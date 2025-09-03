# AI Assessment Freemium Strategy - Production Deployment Guide

## Overview

This guide provides complete instructions for deploying the AI Assessment Freemium Strategy to production. The deployment includes enhanced security, monitoring, rate limiting, and scaling capabilities specifically designed for public-facing freemium endpoints.

## 🚀 Quick Deployment Checklist

### Pre-Deployment Requirements
- [ ] **Database**: Neon PostgreSQL configured and accessible
- [ ] **Redis**: Production Redis instance configured
- [ ] **SSL Certificates**: Valid SSL certificates for domain
- [ ] **API Keys**: Google Gemini and OpenAI API keys configured
- [ ] **Environment Variables**: All production environment variables set
- [ ] **Domain**: DNS configured for ruleiq.com and subdomains
- [ ] **CDN**: CloudFront configured for static assets
- [ ] **Monitoring**: Prometheus and Grafana setup ready

### Security Requirements
- [ ] **Rate Limiting**: Enhanced rate limiting for public endpoints
- [ ] **CORS**: Properly configured for freemium frontend
- [ ] **Security Headers**: CSP, HSTS, and other security headers
- [ ] **API Keys**: Secured in environment variables or secret manager
- [ ] **Firewall**: Network security rules configured
- [ ] **Bot Protection**: Anti-bot measures implemented

## 📋 Step-by-Step Deployment

### Step 1: Infrastructure Setup

#### 1.1 Database Migration
```bash
# Run the freemium database migration
alembic upgrade head

# Verify tables were created
psql $DATABASE_URL -c "\dt freemium*"
psql $DATABASE_URL -c "\dt assessment_leads"
psql $DATABASE_URL -c "\dt ai_question_bank"
psql $DATABASE_URL -c "\dt lead_scoring_events"
```

#### 1.2 Redis Configuration
```bash
# Deploy Redis with custom configuration
docker run -d \
  --name ruleiq-redis \
  --restart unless-stopped \
  -p 6379:6379 \
  -v redis_data:/data \
  -v ./config/redis/redis.conf:/usr/local/etc/redis/redis.conf \
  redis:7-alpine redis-server /usr/local/etc/redis/redis.conf
```

#### 1.3 Environment Configuration
```bash
# Copy and configure production environment
cp config/environment/production.env.template .env
# Edit .env with actual production values
```

### Step 2: Application Deployment

#### 2.1 Build and Deploy with Docker Compose
```bash
# Build the enhanced freemium image
docker build -f Dockerfile.freemium -t ruleiq/freemium-api:latest .

# Deploy the full stack
docker-compose -f docker-compose.freemium.yml up -d

# Verify deployment
docker-compose -f docker-compose.freemium.yml ps
docker-compose -f docker-compose.freemium.yml logs app
```

#### 2.2 Health Check Verification
```bash
# Check application health
curl -f http://localhost:8000/health
curl -f http://localhost:8000/api/v1/monitoring/health

# Check freemium endpoints
curl -f http://localhost:8000/api/v1/freemium/health
```

### Step 3: Load Balancer and SSL Setup

#### 3.1 Nginx Configuration
```bash
# Copy nginx configuration
cp config/nginx/conf.d/freemium.conf /etc/nginx/conf.d/

# Install SSL certificates
cp ssl/ruleiq.com.crt /etc/nginx/ssl/
cp ssl/ruleiq.com.key /etc/nginx/ssl/

# Test and reload nginx
nginx -t
systemctl reload nginx
```

#### 3.2 Verify SSL and Security Headers
```bash
# Test SSL configuration
curl -I https://ruleiq.com/freemium
curl -I https://ruleiq.com/api/v1/freemium/health

# Verify security headers
curl -I https://ruleiq.com/freemium | grep -E "(Strict-Transport|X-Frame|X-Content-Type|CSP)"
```

### Step 4: Monitoring Setup

#### 4.1 Prometheus and Grafana
```bash
# Deploy monitoring stack
docker-compose -f docker-compose.freemium.yml up -d prometheus grafana

# Access monitoring dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/password from env)
```

#### 4.2 Configure Alerting
```bash
# Import Grafana dashboards for freemium metrics
# Configure Slack/PagerDuty webhooks in alert rules
# Test alert notifications
```

### Step 5: Frontend Deployment

#### 5.1 Build and Deploy Frontend
```bash
cd frontend

# Install dependencies and build
pnpm install
pnpm build

# Deploy to CDN/hosting platform
# Configure environment variables for API endpoints
```

#### 5.2 Verify Frontend Integration
```bash
# Test freemium landing page
curl -f https://ruleiq.com/freemium

# Test API integration from frontend
# Open browser developer tools and check network requests
```

### Step 6: Load Testing and Performance Validation

#### 6.1 Run Load Tests
```bash
# Install k6 if not already installed
# Run freemium load tests
k6 run --vus 50 --duration 5m tests/load/freemium-endpoints.js

# Monitor performance during load test
```

#### 6.2 Performance Benchmarks
- **Email Capture**: < 200ms response time, 5 req/min per IP
- **Assessment Start**: < 2s response time, 10 req/min per IP  
- **Question Answering**: < 1s response time, 50 req/min per IP
- **Results Generation**: < 5s response time, cached for 1 hour
- **Overall Error Rate**: < 1%
- **Rate Limit Effectiveness**: 429 responses for exceeded limits

### Step 7: Security Verification

#### 7.1 Security Testing
```bash
# Test rate limiting
for i in {1..10}; do curl -X POST https://ruleiq.com/api/v1/freemium/capture-email -d '{"email":"test@example.com"}'; done

# Test CORS policies
curl -H "Origin: https://malicious.com" https://ruleiq.com/api/v1/freemium/capture-email

# Test input validation
curl -X POST https://ruleiq.com/api/v1/freemium/capture-email -d '{"email":"invalid-email"}'
```

#### 7.2 Bot Protection Verification
```bash
# Test with bot-like user agents
curl -H "User-Agent: bot/1.0" https://ruleiq.com/api/v1/freemium/capture-email
curl -H "User-Agent: curl/7.64.1" https://ruleiq.com/api/v1/freemium/capture-email
```

## 🔧 Configuration Details

### Rate Limiting Configuration
The freemium deployment implements multi-tier rate limiting:

- **Email Capture**: 5 requests per 5 minutes per IP
- **Assessment Start**: 10 requests per 5 minutes per IP
- **Question Answering**: 50 requests per 5 minutes per IP
- **Results Viewing**: 20 requests per 5 minutes per IP (cached)
- **Global Limits**: 100 requests per minute per IP

### Caching Strategy
- **AI Results**: 1-2 hours cache (Redis)
- **Questions**: 24 hours cache (Redis)
- **Static Assets**: 1 year cache (CDN)
- **API Responses**: 5 minutes cache (Nginx)

### Security Measures
- **CSP Headers**: Restricts script and style sources
- **CORS**: Limited to ruleiq.com domains
- **Rate Limiting**: Prevents abuse and DDoS
- **Input Validation**: Prevents injection attacks
- **Bot Detection**: Blocks automated requests

## 📊 Monitoring and Alerts

### Key Metrics to Monitor
1. **Request Volume**: Freemium endpoint traffic
2. **Response Times**: P95 response times < 2s
3. **Error Rates**: Overall error rate < 1%
4. **Conversion Rates**: Email capture to assessment completion
5. **AI Costs**: Daily AI service costs
6. **Rate Limit Hits**: Blocked requests due to rate limiting

### Critical Alerts
- **High Error Rate**: > 5% error rate for 2 minutes
- **Slow Response Times**: P95 > 2s for 3 minutes
- **AI Service Failure**: > 10% AI failure rate
- **High AI Costs**: > $100/day AI costs
- **Email Capture Down**: Critical endpoint unavailable

### Business Metrics
- **Email Captures**: Daily new leads
- **Assessment Completions**: Conversion from start to finish
- **Results Views**: Users viewing their results
- **Conversion Rate**: Assessment to paid conversion
- **Cost Per Lead**: AI costs per captured email

## 🚨 Troubleshooting Guide

### Common Issues

#### High Response Times
```bash
# Check application logs
docker-compose -f docker-compose.freemium.yml logs app

# Check database performance
psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Check Redis performance
redis-cli --latency
```

#### Rate Limiting Issues
```bash
# Check rate limit configurations
redis-cli keys "rate_limit:*"
redis-cli get "rate_limit:ip:x.x.x.x:endpoint:/api/v1/freemium/capture-email"

# Reset rate limits for testing
redis-cli flushdb
```

#### AI Service Failures
```bash
# Check AI service logs
docker-compose -f docker-compose.freemium.yml logs celery_worker

# Test AI services directly
curl -X POST https://ruleiq.com/api/v1/ai/test -H "Authorization: Bearer $API_KEY"
```

### Performance Optimization

#### Database Optimization
```sql
-- Check slow queries
SELECT query, mean_time, calls, total_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Optimize freemium table indexes
ANALYZE assessment_leads;
ANALYZE freemium_assessment_sessions;
```

#### Redis Optimization
```bash
# Check Redis memory usage
redis-cli info memory

# Optimize Redis configuration
redis-cli config set maxmemory-policy allkeys-lru
```

## 🔄 Continuous Deployment

### CI/CD Pipeline
The GitHub Actions workflow in `.github/workflows/freemium-deployment.yml` provides:

1. **Automated Testing**: Unit, integration, and load tests
2. **Security Scanning**: Vulnerability and dependency checks
3. **Build and Push**: Docker image builds with caching
4. **Blue-Green Deployment**: Zero-downtime deployments
5. **Rollback Capability**: Automatic rollback on failure
6. **Post-Deployment Monitoring**: Health checks and metric validation

### Deployment Triggers
- **Main Branch**: Automatic production deployment
- **Feature Branches**: Staging deployment for testing
- **Manual Triggers**: On-demand deployments with environment selection

## 📈 Scaling Recommendations

### Horizontal Scaling
- **API Instances**: Scale to 4-8 instances based on traffic
- **Celery Workers**: Scale AI processing workers based on queue length
- **Redis**: Consider Redis Cluster for high availability
- **Database**: Use read replicas for read-heavy workloads

### Vertical Scaling
- **Memory**: 2GB+ per API instance for AI processing
- **CPU**: 2+ cores per instance for concurrent request handling
- **Storage**: SSD storage for database and Redis
- **Network**: High bandwidth for API responses and AI calls

## 🎯 Success Criteria

### Performance Targets
- [ ] **Email Capture**: < 200ms response time, 99.9% uptime
- [ ] **Assessment Flow**: < 5s end-to-end completion time
- [ ] **AI Processing**: < 30s for question generation and analysis
- [ ] **Conversion Rate**: > 5% from email capture to results view
- [ ] **Cost Efficiency**: < $0.50 per lead for AI processing

### Security Targets
- [ ] **Zero High-Severity Vulnerabilities**: Regular security scans
- [ ] **Rate Limiting Effectiveness**: 99%+ of abuse blocked
- [ ] **HTTPS Enforcement**: 100% HTTPS traffic
- [ ] **Data Protection**: GDPR compliance for EU users

### Business Targets
- [ ] **Lead Generation**: 1000+ qualified leads per month
- [ ] **Conversion Rate**: 10%+ conversion to paid plans
- [ ] **User Experience**: < 2% abandonment rate during assessment
- [ ] **Support Tickets**: < 1% of users require support

---

## 📞 Support and Maintenance

For ongoing support and maintenance:
1. Monitor Grafana dashboards daily
2. Review security logs weekly  
3. Update dependencies monthly
4. Conduct load tests before major traffic events
5. Backup database and Redis daily
6. Test disaster recovery procedures quarterly

**Deployment completed successfully!** 🎉