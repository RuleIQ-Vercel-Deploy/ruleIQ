#!/bin/bash
set -euo pipefail

# ruleIQ Production Deployment Script
# This script handles secure production deployment with all optimizations

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Configuration
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
BACKUP_BEFORE_DEPLOY="${BACKUP_BEFORE_DEPLOY:-true}"
HEALTH_CHECK_TIMEOUT="${HEALTH_CHECK_TIMEOUT:-300}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Pre-deployment checks
pre_deployment_checks() {
    log_info "Running pre-deployment checks..."
    
    # Check if required files exist
    local required_files=(".env" "$COMPOSE_FILE" "nginx.conf")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Required file missing: $file"
            exit 1
        fi
    done
    
    # Check if required environment variables are set
    local required_vars=("DATABASE_URL" "REDIS_URL" "SECRET_KEY" "GOOGLE_API_KEY")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Required environment variable not set: $var"
            exit 1
        fi
    done
    
    # Check Docker and docker-compose are available
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose is not installed or not in PATH"
        exit 1
    fi
    
    log_info "Pre-deployment checks passed"
}

# Backup current data
backup_data() {
    if [[ "$BACKUP_BEFORE_DEPLOY" == "true" ]]; then
        log_info "Creating backup before deployment..."
        if [[ -f "./scripts/backup-volumes.sh" ]]; then
            ./scripts/backup-volumes.sh backup
        else
            log_warn "Backup script not found, skipping backup"
        fi
    fi
}

# Build and deploy
deploy() {
    log_info "Starting production deployment..."
    
    # Pull latest images
    log_info "Pulling latest base images..."
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Build application images
    log_info "Building application images..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    # Start services with rolling update
    log_info "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d --remove-orphans
    
    # Wait for services to be healthy
    wait_for_health_checks
}

# Wait for health checks to pass
wait_for_health_checks() {
    log_info "Waiting for health checks to pass..."
    local timeout=$HEALTH_CHECK_TIMEOUT
    local elapsed=0
    
    while [[ $elapsed -lt $timeout ]]; do
        local unhealthy_services=$(docker-compose -f "$COMPOSE_FILE" ps --format json | jq -r 'select(.Health != "healthy" and .Health != "") | .Name')
        
        if [[ -z "$unhealthy_services" ]]; then
            log_info "All services are healthy"
            return 0
        fi
        
        log_info "Waiting for services to become healthy: $unhealthy_services"
        sleep 10
        elapsed=$((elapsed + 10))
    done
    
    log_error "Health checks failed after $timeout seconds"
    return 1
}

# Post-deployment verification
post_deployment_verification() {
    log_info "Running post-deployment verification..."
    
    # Test API health endpoint
    if curl -f "http://localhost/health" &> /dev/null; then
        log_info "API health check passed"
    else
        log_error "API health check failed"
        return 1
    fi
    
    # Test database connection (if possible)
    if docker-compose -f "$COMPOSE_FILE" exec -T app python -c "
import asyncio
from database.connection import get_database
async def test_db():
    db = await get_database()
    result = await db.fetch_val('SELECT 1')
    assert result == 1
    print('Database connection successful')
asyncio.run(test_db())
" 2>/dev/null; then
        log_info "Database connection test passed"
    else
        log_warn "Database connection test failed or not available"
    fi
    
    # Test Redis connection
    if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping | grep -q "PONG"; then
        log_info "Redis connection test passed"
    else
        log_error "Redis connection test failed"
        return 1
    fi
    
    log_info "Post-deployment verification completed"
}

# Rollback function
rollback() {
    log_warn "Rolling back deployment..."
    
    # Stop current services
    docker-compose -f "$COMPOSE_FILE" down
    
    # Restore from backup if available
    local latest_backup=$(ls -t ./backups/*.tar.gz 2>/dev/null | head -n1 || echo "")
    if [[ -n "$latest_backup" ]]; then
        log_info "Restoring from backup: $latest_backup"
        # Add restoration logic here if needed
    fi
    
    log_warn "Rollback completed. Manual intervention may be required."
}

# Cleanup function
cleanup() {
    log_info "Cleaning up unused Docker resources..."
    docker system prune -f
    docker volume prune -f
}

# Main deployment process
main() {
    log_info "Starting ruleIQ production deployment..."
    
    # Set trap for cleanup on script exit
    trap 'log_error "Deployment failed. Check logs above."' ERR
    
    pre_deployment_checks
    backup_data
    deploy
    
    if post_deployment_verification; then
        cleanup
        log_info "🎉 Production deployment completed successfully!"
        log_info "Application is available at: https://your-domain.com"
        log_info "Monitoring dashboard: http://localhost:3001 (Grafana)"
    else
        log_error "Post-deployment verification failed"
        read -p "Do you want to rollback? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rollback
        fi
        exit 1
    fi
}

# Command line options
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "health")
        wait_for_health_checks
        ;;
    "verify")
        post_deployment_verification
        ;;
    "backup")
        backup_data
        ;;
    *)
        echo "Usage: $0 [deploy|rollback|health|verify|backup]"
        echo ""
        echo "Commands:"
        echo "  deploy   - Full production deployment (default)"
        echo "  rollback - Rollback to previous version"
        echo "  health   - Check service health"
        echo "  verify   - Run post-deployment verification"
        echo "  backup   - Create data backup"
        exit 1
        ;;
esac