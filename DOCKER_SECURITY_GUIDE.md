# Docker Security and Deployment Guide

## 🛡️ Security Hardening Overview

This guide covers the Docker security optimizations implemented for the ruleIQ platform.

## 📁 File Structure

- `Dockerfile` - Multi-stage production-optimized container
- `.dockerignore` - Build context optimization
- `docker-compose.yml` - Development environment with security controls
- `docker-compose.prod.yml` - Production environment
- `docker-compose.security.yml` - Security hardening overlay
- `docker-compose.monitoring.yml` - Observability stack
- `nginx.conf` - Reverse proxy with security headers
- `scripts/backup-volumes.sh` - Volume backup automation
- `scripts/deploy-production.sh` - Production deployment automation

## 🔧 Key Security Features

### Container Security
- ✅ **Multi-stage builds** - Reduced attack surface
- ✅ **Non-root users** - All services run as unprivileged users
- ✅ **Read-only filesystems** - Prevents runtime modifications
- ✅ **Capability dropping** - Minimal required Linux capabilities
- ✅ **No new privileges** - Prevents privilege escalation
- ✅ **Resource limits** - CPU and memory constraints

### Network Security
- ✅ **Private networks** - Services isolated in custom bridge networks
- ✅ **Port binding restrictions** - Redis bound to localhost only in development
- ✅ **Encrypted network overlay** - Production network encryption
- ✅ **Rate limiting** - API endpoint protection via nginx
- ✅ **Security headers** - HSTS, CSP, CSRF protection

### Data Protection
- ✅ **Volume encryption** - Persistent data protection
- ✅ **Automated backups** - Regular data snapshots
- ✅ **Secrets management** - Environment-based configuration
- ✅ **TLS termination** - nginx handles SSL/TLS

## 🚀 Deployment Commands

### Development Environment
```bash
# Start development services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Environment
```bash
# Deploy with all security features
docker-compose -f docker-compose.prod.yml -f docker-compose.security.yml up -d

# Or use the deployment script
./scripts/deploy-production.sh

# Monitor deployment
docker-compose -f docker-compose.prod.yml ps
```

### Monitoring Stack
```bash
# Start monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana dashboard
# http://localhost:3001 (admin/admin)
```

## 📊 Health Checks and Monitoring

### Built-in Health Checks
- **FastAPI App**: HTTP health endpoint (`/health`)
- **Celery Workers**: Celery inspect command
- **Redis**: Redis PING command
- **PostgreSQL**: pg_isready check
- **nginx**: Process and upstream checks

### Monitoring Stack
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization dashboards
- **Node Exporter**: System metrics
- **Redis Exporter**: Redis-specific metrics

### Key Metrics to Monitor
- Response time and error rates
- Memory and CPU usage
- Database connection pool status
- Celery queue lengths
- Redis memory usage and hit rates

## 🔒 Security Configurations

### nginx Security Headers
```nginx
# Essential security headers
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline';" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Rate Limiting Configuration
- **General API**: 100 requests/minute per IP
- **Authentication**: 10 requests/minute per IP  
- **AI Endpoints**: 20 requests/minute per IP
- **Connection Limits**: 10 concurrent connections per IP

### Container Hardening
- All containers run with `--cap-drop=ALL`
- Specific capabilities added only when required
- Read-only root filesystem with tmpfs for temporary files
- Process limits and file descriptor limits applied

## 💾 Backup and Recovery

### Automated Backups
```bash
# Create backup of all volumes
./scripts/backup-volumes.sh backup

# List available backups
./scripts/backup-volumes.sh list

# Restore specific volume
./scripts/backup-volumes.sh restore redis_data redis_data_20231201_120000.tar.gz

# Cleanup old backups (>7 days)
./scripts/backup-volumes.sh cleanup
```

### Manual Backup Commands
```bash
# Backup specific volume manually
docker run --rm -v ruleiq_redis_data:/data:ro -v $(pwd)/backups:/backup alpine:latest \
  tar czf /backup/redis_manual_backup.tar.gz -C /data .

# Backup database
docker-compose exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql
```

## 🔧 Troubleshooting

### Common Issues

**Container Won't Start**
```bash
# Check container logs
docker-compose logs service_name

# Check resource limits
docker stats

# Verify health checks
docker-compose ps
```

**Permission Errors**
```bash
# Fix volume permissions
docker-compose exec app chown -R appuser:appuser /app/logs

# Check user mapping
docker-compose exec app id
```

**Network Connectivity**
```bash
# Test network connectivity
docker-compose exec app ping redis
docker-compose exec app ping db

# Check port bindings
netstat -tulpn | grep docker
```

### Performance Optimization

**Memory Usage**
- Monitor container memory with `docker stats`
- Adjust resource limits in compose files
- Configure Redis maxmemory policies

**Database Performance**
- Monitor slow queries with PostgreSQL logs
- Use connection pooling
- Regular VACUUM and ANALYZE operations

**Redis Optimization**
- Configure appropriate memory limits
- Use LRU eviction policies
- Monitor hit/miss ratios

## 🌐 Production Deployment Checklist

### Pre-deployment
- [ ] Environment variables configured (`.env`)
- [ ] SSL certificates in place (`./ssl/`)
- [ ] DNS records pointing to server
- [ ] Firewall rules configured
- [ ] Backup system tested
- [ ] Monitoring stack configured

### Deployment
- [ ] Run security scan: `docker scout cves`
- [ ] Execute deployment script: `./scripts/deploy-production.sh`
- [ ] Verify all health checks pass
- [ ] Test critical API endpoints
- [ ] Check monitoring dashboards
- [ ] Verify backup automation

### Post-deployment
- [ ] Monitor error rates and response times
- [ ] Check log aggregation
- [ ] Verify SSL/TLS configuration
- [ ] Test backup and restore procedures
- [ ] Update documentation with any changes

## 📝 Environment Variables

### Required Production Variables
```bash
# Application
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@db:5432/ruleiq
REDIS_URL=redis://redis:6379

# AI Services
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-api-key

# Security
FERNET_KEY=your-fernet-key-here
ALLOWED_ORIGINS=https://your-domain.com

# Database (if using managed PostgreSQL)
POSTGRES_DB=ruleiq
POSTGRES_USER=dbuser
POSTGRES_PASSWORD=secure-password

# Redis (if using authentication)
REDIS_PASSWORD=redis-password
```

## 🔍 Security Audit Commands

```bash
# Scan for vulnerabilities
docker scout cves

# Check running processes in containers
docker-compose exec app ps aux

# Verify non-root execution
docker-compose exec app id

# Check file permissions
docker-compose exec app ls -la /app

# Network inspection
docker network ls
docker network inspect ruleiq_compliancegpt-network
```

## 📞 Support and Maintenance

### Regular Maintenance Tasks
- Weekly: Review monitoring dashboards and logs
- Monthly: Update base images and dependencies  
- Quarterly: Security audit and penetration testing
- As needed: Scale resources based on usage patterns

### Log Locations
- Application logs: `docker-compose logs app`
- nginx logs: `docker-compose logs nginx`
- Database logs: `docker-compose logs db`
- Redis logs: `docker-compose logs redis`

This security-hardened Docker setup provides enterprise-grade protection while maintaining performance and scalability for the ruleIQ compliance platform.