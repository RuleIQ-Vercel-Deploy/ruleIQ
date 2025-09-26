#!/bin/bash

# Deploy RuleIQ Backend to Google Cloud Run
# This script builds and deploys the application to Google Cloud Run

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check required environment variables
print_status "Checking required environment variables..."

if [ -z "$PROJECT_ID" ]; then
    print_error "PROJECT_ID environment variable is required"
    echo "Please set: export PROJECT_ID=your-gcp-project-id"
    exit 1
fi

# Set default values
REGION=${REGION:-europe-west2}
SERVICE_NAME=${SERVICE_NAME:-ruleiq}
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

print_status "Configuration:"
echo "  PROJECT_ID: ${PROJECT_ID}"
echo "  REGION: ${REGION}"
echo "  SERVICE_NAME: ${SERVICE_NAME}"
echo "  IMAGE_NAME: ${IMAGE_NAME}"

# Authenticate with Google Cloud
print_status "Authenticating with Google Cloud..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
print_status "Enabling required Google Cloud APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com

# Check if secrets exist, create them if not
print_status "Checking Google Secret Manager secrets..."

check_and_create_secret() {
    SECRET_NAME=$1
    SECRET_VALUE=$2
    
    if gcloud secrets describe ${SECRET_NAME} --project=${PROJECT_ID} >/dev/null 2>&1; then
        print_warning "Secret ${SECRET_NAME} already exists"
    else
        if [ -z "${SECRET_VALUE}" ]; then
            print_warning "Secret ${SECRET_NAME} not set. Please create it manually:"
            echo "  echo -n 'your-secret-value' | gcloud secrets create ${SECRET_NAME} --data-file=-"
        else
            print_status "Creating secret ${SECRET_NAME}..."
            echo -n "${SECRET_VALUE}" | gcloud secrets create ${SECRET_NAME} \
                --replication-policy="automatic" \
                --data-file=- \
                --project=${PROJECT_ID}
        fi
    fi
}

# Validate required secrets exist
validate_secret() {
    SECRET_NAME=$1
    if ! gcloud secrets describe ${SECRET_NAME} --project=${PROJECT_ID} >/dev/null 2>&1; then
        print_error "Required secret ${SECRET_NAME} does not exist in Google Secret Manager"
        echo "Please create it with: echo -n 'your-secret-value' | gcloud secrets create ${SECRET_NAME} --data-file=-"
        return 1
    else
        print_status "✓ Secret ${SECRET_NAME} exists"
        return 0
    fi
}

# Validate all required secrets
print_status "Validating required secrets..."
SECRETS_VALID=true

validate_secret "DATABASE_URL" || SECRETS_VALID=false
validate_secret "JWT_SECRET_KEY" || SECRETS_VALID=false
# Redis is optional in Cloud Run but check if it exists
validate_secret "REDIS_URL" || print_warning "REDIS_URL not configured (optional for Cloud Run)"
validate_secret "GOOGLE_AI_API_KEY" || print_warning "GOOGLE_AI_API_KEY not configured (optional)"

if [ "$SECRETS_VALID" = false ]; then
    print_error "One or more required secrets are missing. Please create them before deploying."
    exit 1
fi

# Check and create optional secrets
check_and_create_secret "DATABASE_URL" "${DATABASE_URL}"
check_and_create_secret "JWT_SECRET_KEY" "${JWT_SECRET_KEY}"
check_and_create_secret "REDIS_URL" "${REDIS_URL}"
check_and_create_secret "GOOGLE_AI_API_KEY" "${GOOGLE_AI_API_KEY}"

# Optional secrets
if [ -n "${SENTRY_DSN}" ]; then
    check_and_create_secret "SENTRY_DSN" "${SENTRY_DSN}"
fi

# Build the Docker image
print_status "Building Docker image..."
docker build -t ${IMAGE_NAME}:latest .

# Verify Docker image dependencies
print_status "Verifying Docker image dependencies..."
print_status "Testing asyncpg installation in built image..."
if ! docker run --rm ${IMAGE_NAME}:latest python -c "import asyncpg; print('✓ asyncpg installed successfully')"; then
    print_error "asyncpg is not properly installed in the Docker image"
    print_error "This will cause deployment failures. Check Dockerfile and requirements-cloudrun.txt"
    exit 1
fi

print_status "Testing psycopg installation in built image..."
if ! docker run --rm ${IMAGE_NAME}:latest python -c "import psycopg; print('✓ psycopg installed successfully')" 2>/dev/null; then
    print_warning "psycopg not available, but this is optional"
fi

print_status "Testing SQLAlchemy async support in built image..."
if ! docker run --rm ${IMAGE_NAME}:latest python -c "from sqlalchemy.ext.asyncio import create_async_engine; print('✓ SQLAlchemy async support available')"; then
    print_error "SQLAlchemy async support is not available in the Docker image"
    print_error "This will cause database connection failures"
    exit 1
fi

print_status "Testing FastAPI import in built image..."
if ! docker run --rm ${IMAGE_NAME}:latest python -c "from api.main import app; print('✓ FastAPI application imports successfully')"; then
    print_error "FastAPI application fails to import in the Docker image"
    print_error "Check application code and dependencies"
    exit 1
fi

print_status "✓ All dependency verifications passed"

# Tag with commit SHA if available
if [ -n "$(git rev-parse HEAD 2>/dev/null)" ]; then
    COMMIT_SHA=$(git rev-parse HEAD)
    docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${COMMIT_SHA}
    print_status "Tagged image with commit SHA: ${COMMIT_SHA}"
fi

# Push the image to Google Container Registry
print_status "Pushing image to Google Container Registry..."
docker push ${IMAGE_NAME}:latest

if [ -n "${COMMIT_SHA}" ]; then
    docker push ${IMAGE_NAME}:${COMMIT_SHA}
fi

# Store current revision for rollback
CURRENT_REVISION=""
if gcloud run services describe ${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID} >/dev/null 2>&1; then
    CURRENT_REVISION=$(gcloud run services describe ${SERVICE_NAME} \
        --region=${REGION} \
        --project=${PROJECT_ID} \
        --format='value(status.latestReadyRevisionName)')
    print_status "Current revision: ${CURRENT_REVISION}"
fi

# Create or update Cloud Run service
print_status "Deploying to Cloud Run..."

# Check if service exists
if gcloud run services describe ${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID} >/dev/null 2>&1; then
    print_status "Updating existing Cloud Run service..."
else
    print_status "Creating new Cloud Run service..."
fi

# Deploy the service with comprehensive error handling and improved configuration
print_status "Deploying with enhanced startup configuration for database initialization..."
if ! gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 100 \
    --min-instances 1 \
    --port 8080 \
    --execution-environment gen2 \
    --startup-cpu-boost \
    --set-env-vars "PYTHONUNBUFFERED=1,PORT=8080,ENVIRONMENT=production,K_SERVICE=ruleiq" \
    --concurrency 80 \
    --cpu-throttling \
    --update-secrets "DATABASE_URL=DATABASE_URL:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest,REDIS_URL=REDIS_URL:latest,GOOGLE_AI_API_KEY=GOOGLE_AI_API_KEY:latest" \
    --project ${PROJECT_ID}; then
    
    print_error "Deployment failed!"
    
    # Show immediate deployment logs for debugging
    print_status "Fetching recent deployment logs for debugging..."
    gcloud run logs read --service=${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID} --limit=30 || true
    
    # Check for specific error patterns
    print_status "Checking for common deployment issues..."
    RECENT_LOGS=$(gcloud run logs read --service=${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID} --limit=50 2>/dev/null || echo "")
    
    if echo "${RECENT_LOGS}" | grep -q "ModuleNotFoundError.*asyncpg"; then
        print_error "❌ asyncpg module not found - Docker build issue detected"
        echo "  Solution: Check Dockerfile and requirements-cloudrun.txt"
    fi
    
    if echo "${RECENT_LOGS}" | grep -q "database.*connection"; then
        print_error "❌ Database connection issue detected"
        echo "  Solution: Check DATABASE_URL secret and database initialization"
    fi
    
    if echo "${RECENT_LOGS}" | grep -q "Port.*already in use\|bind.*failed"; then
        print_error "❌ Port binding issue detected"
        echo "  Solution: Check PORT environment variable and application startup"
    fi
    
    # Attempt rollback if we have a previous revision
    if [ -n "${CURRENT_REVISION}" ]; then
        print_warning "Attempting to rollback to previous revision: ${CURRENT_REVISION}"
        if gcloud run services update-traffic ${SERVICE_NAME} \
            --to-revisions ${CURRENT_REVISION}=100 \
            --region ${REGION} \
            --project ${PROJECT_ID}; then
            print_status "✓ Rollback successful"
            
            # Verify rollback worked
            sleep 10
            if curl -s --max-time 30 "${SERVICE_URL}/health" >/dev/null 2>&1; then
                print_status "✓ Rollback verification: Service is responding"
            else
                print_warning "⚠ Rollback verification: Service may not be fully ready"
            fi
        else
            print_error "❌ Rollback failed"
        fi
    else
        print_warning "No previous revision available for rollback"
    fi
    
    print_error "Deployment failed. Debugging information:"
    echo "  📋 View full logs: gcloud run logs read --service=${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID}"
    echo "  🔍 Check service status: gcloud run services describe ${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID}"
    echo "  📊 Monitor metrics: https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/metrics?project=${PROJECT_ID}"
    echo "  🐛 Debug container locally: docker run -p 8080:8080 ${IMAGE_NAME}:latest"
    exit 1
fi

print_status "Deployment completed successfully"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --format='value(status.url)')

print_status "Service deployed successfully!"
echo "Service URL: ${SERVICE_URL}"

# Comprehensive health check validation
print_status "Performing comprehensive health check validation..."

# Wait for service to be ready with enhanced timeout for database initialization
print_status "Waiting for service to be ready (allowing extra time for database initialization)..."
READY_TIMEOUT=180  # Increased timeout for database initialization
READY_COUNT=0

while [ $READY_COUNT -lt $READY_TIMEOUT ]; do
    SERVICE_STATUS=$(gcloud run services describe ${SERVICE_NAME} \
        --region=${REGION} \
        --project=${PROJECT_ID} \
        --format='value(status.conditions[0].status)' 2>/dev/null || echo "Unknown")
    
    if [ "${SERVICE_STATUS}" = "True" ]; then
        print_status "✓ Service is ready"
        break
    fi
    
    # Show progress and check for issues
    if [ $((READY_COUNT % 30)) -eq 0 ] && [ $READY_COUNT -gt 0 ]; then
        print_status "Still waiting... (${READY_COUNT}/${READY_TIMEOUT}s) - Status: ${SERVICE_STATUS}"
        
        # Check recent logs for startup issues
        STARTUP_LOGS=$(gcloud run logs read --service=${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID} --limit=10 2>/dev/null || echo "")
        if echo "${STARTUP_LOGS}" | grep -q "ERROR\|CRITICAL\|Failed\|Exception"; then
            print_warning "⚠ Detected errors in startup logs:"
            echo "${STARTUP_LOGS}" | grep -E "ERROR|CRITICAL|Failed|Exception" | tail -3
        fi
    fi
    
    sleep 5
    READY_COUNT=$((READY_COUNT + 5))
    
    if [ $READY_COUNT -ge $READY_TIMEOUT ]; then
        print_error "❌ Service failed to become ready within ${READY_TIMEOUT} seconds"
        
        # Show detailed failure information
        print_status "Gathering failure diagnostics..."
        
        # Get service conditions
        SERVICE_CONDITIONS=$(gcloud run services describe ${SERVICE_NAME} \
            --region=${REGION} \
            --project=${PROJECT_ID} \
            --format='value(status.conditions[].message)' 2>/dev/null || echo "Unable to fetch conditions")
        
        print_error "Service conditions: ${SERVICE_CONDITIONS}"
        
        # Show recent logs
        print_status "Recent startup logs:"
        gcloud run logs read --service=${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID} --limit=20 || true
        
        print_error "Debugging commands:"
        echo "  📋 Full logs: gcloud run logs read --service=${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID}"
        echo "  🔍 Service details: gcloud run services describe ${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID}"
        echo "  🐛 Test locally: docker run -p 8080:8080 -e PORT=8080 ${IMAGE_NAME}:latest"
        
        exit 1
    fi
done

# Enhanced endpoint testing with better debugging
test_endpoint() {
    local endpoint=$1
    local expected_code=$2
    local description=$3
    local max_retries=6  # Increased retries for database initialization
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        local response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 30 "${SERVICE_URL}${endpoint}" 2>/dev/null || echo "000")
        
        if [ "${response_code}" = "${expected_code}" ]; then
            print_status "✓ ${description} passed (HTTP ${response_code})"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            print_warning "⚠ ${description} failed (HTTP ${response_code}), retrying... (${retry_count}/${max_retries})"
            
            # Show response body for debugging on certain failures
            if [ "${response_code}" = "500" ] || [ "${response_code}" = "503" ]; then
                local response_body=$(curl -s --max-time 30 "${SERVICE_URL}${endpoint}" 2>/dev/null || echo "Unable to fetch response body")
                print_warning "Response body: ${response_body}"
                
                # Check logs for this specific failure
                print_status "Checking recent logs for errors..."
                RECENT_ERROR_LOGS=$(gcloud run logs read --service=${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID} --limit=5 2>/dev/null || echo "")
                if echo "${RECENT_ERROR_LOGS}" | grep -q "ERROR\|Exception\|Failed"; then
                    echo "${RECENT_ERROR_LOGS}" | grep -E "ERROR|Exception|Failed" | tail -2
                fi
            fi
            
            sleep 15  # Increased wait time for database initialization
        fi
    done
    
    print_error "❌ ${description} failed after ${max_retries} attempts (HTTP ${response_code})"
    
    # Final debugging attempt
    print_status "Final debugging attempt for ${endpoint}:"
    local final_response=$(curl -s --max-time 30 "${SERVICE_URL}${endpoint}" 2>/dev/null || echo "Connection failed")
    echo "Final response: ${final_response}"
    
    return 1
}

# Test all health endpoints with enhanced validation
HEALTH_CHECKS_PASSED=true

print_status "Starting comprehensive health check validation..."

# Test basic connectivity first
print_status "Testing basic connectivity..."
if ! curl -s --max-time 30 "${SERVICE_URL}" >/dev/null 2>&1; then
    print_error "❌ Basic connectivity to service failed"
    print_status "Service URL: ${SERVICE_URL}"
    HEALTH_CHECKS_PASSED=false
else
    print_status "✓ Basic connectivity successful"
fi

# Test health endpoints in order of importance
print_status "Testing health endpoints..."
test_endpoint "/health" "200" "Basic health check" || HEALTH_CHECKS_PASSED=false
test_endpoint "/health/live" "200" "Liveness check" || HEALTH_CHECKS_PASSED=false
test_endpoint "/health/ready" "200" "Readiness check" || HEALTH_CHECKS_PASSED=false

# Test API endpoints
print_status "Testing API endpoints..."
test_endpoint "/api/v1/health" "200" "API health check" || HEALTH_CHECKS_PASSED=false

# Test database connectivity through health endpoint
print_status "Testing database connectivity..."
DB_HEALTH_RESPONSE=$(curl -s --max-time 30 "${SERVICE_URL}/api/v1/health/detailed" 2>/dev/null || echo '{"error": "Failed to fetch"}')
if echo "${DB_HEALTH_RESPONSE}" | grep -q '"database".*"healthy"'; then
    print_status "✓ Database connectivity check passed"
elif echo "${DB_HEALTH_RESPONSE}" | grep -q '"database".*"unhealthy"'; then
    print_warning "⚠ Database connectivity issues detected"
    echo "Database health response: ${DB_HEALTH_RESPONSE}"
else
    print_warning "⚠ Unable to determine database health status"
fi

# Test detailed health endpoint and show response
print_status "Testing detailed health endpoint..."
DETAILED_HEALTH=$(curl -s --max-time 30 ${SERVICE_URL}/api/v1/health/detailed 2>/dev/null || echo '{"error": "Failed to fetch detailed health"}')
echo "Detailed health response:"
echo "${DETAILED_HEALTH}" | jq '.' 2>/dev/null || echo "${DETAILED_HEALTH}"

# Enhanced health check validation and debugging
if [ "$HEALTH_CHECKS_PASSED" = false ]; then
    print_error "❌ Some health checks failed. Deployment has issues."
    
    # Comprehensive debugging information
    print_status "🔍 Gathering comprehensive debugging information..."
    
    # Service status
    print_status "Service status:"
    gcloud run services describe ${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID} --format='table(status.conditions[].type,status.conditions[].status,status.conditions[].message)' || true
    
    # Recent logs with error filtering
    print_status "Recent error logs:"
    ERROR_LOGS=$(gcloud run logs read --service=${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID} --limit=30 2>/dev/null || echo "Unable to fetch logs")
    echo "${ERROR_LOGS}" | grep -E "ERROR|CRITICAL|Exception|Failed|asyncpg|database" || echo "No specific errors found in recent logs"
    
    # Container resource usage
    print_status "Container resource information:"
    gcloud run services describe ${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID} --format='value(spec.template.spec.containers[0].resources)' || true
    
    # Environment variables (without secrets)
    print_status "Environment configuration:"
    gcloud run services describe ${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID} --format='value(spec.template.spec.containers[0].env[].name)' | grep -v "SECRET" || true
    
    print_error "🚨 Deployment validation failed. Debugging resources:"
    echo "  📋 Full logs: gcloud run logs read --service=${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID} --limit=100"
    echo "  🔍 Service details: gcloud run services describe ${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID}"
    echo "  📊 Metrics: https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/metrics?project=${PROJECT_ID}"
    echo "  🐛 Local testing: docker run -p 8080:8080 -e PORT=8080 -e ENVIRONMENT=development ${IMAGE_NAME}:latest"
    echo "  🔧 Debug container: docker run -it --entrypoint=/bin/bash ${IMAGE_NAME}:latest"
    echo ""
    echo "Common fixes:"
    echo "  • Check asyncpg installation: docker run --rm ${IMAGE_NAME}:latest python -c 'import asyncpg'"
    echo "  • Verify database URL: Check DATABASE_URL secret in Google Secret Manager"
    echo "  • Test database connection: Verify database is accessible from Cloud Run"
    echo "  • Check startup time: Database initialization may need more time"
    
    exit 1
fi

print_status "Deployment and validation complete!"
echo ""
echo "============================================"
echo "Deployment Summary:"
echo "  Service: ${SERVICE_NAME}"
echo "  Region: ${REGION}"
echo "  URL: ${SERVICE_URL}"
echo "  Image: ${IMAGE_NAME}:latest"
if [ -n "${COMMIT_SHA}" ]; then
    echo "  Commit: ${COMMIT_SHA}"
fi
echo ""
echo "Health Check Results:"
echo "  ✓ All health endpoints are responding correctly"
echo "  ✓ Service is ready to handle traffic"
echo ""
echo "Useful Commands:"
echo "  📋 View logs: gcloud run logs read --service=${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID}"
echo "  📊 Monitor metrics: https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/metrics?project=${PROJECT_ID}"
echo "  🔍 Service details: gcloud run services describe ${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID}"
echo "  🐛 Debug locally: docker run -p 8080:8080 -e PORT=8080 ${IMAGE_NAME}:latest"
echo "  🔧 Container shell: docker run -it --entrypoint=/bin/bash ${IMAGE_NAME}:latest"
echo ""
echo "API Endpoints:"
echo "  🏥 Health: ${SERVICE_URL}/health"
echo "  🏥 API Health: ${SERVICE_URL}/api/v1/health"
echo "  🏥 Detailed Health: ${SERVICE_URL}/api/v1/health/detailed"
echo "  📚 API Docs: ${SERVICE_URL}/docs"
echo "  📚 OpenAPI Schema: ${SERVICE_URL}/openapi.json"
echo ""
echo "Dependency Verification:"
echo "  ✓ asyncpg: Verified during build"
echo "  ✓ SQLAlchemy async: Verified during build"
echo "  ✓ FastAPI import: Verified during build"
echo "  ✓ Health endpoints: Validated post-deployment"
echo "============================================"

# Optional: Set up custom domain
if [ -n "${CUSTOM_DOMAIN}" ]; then
    print_status "Setting up custom domain ${CUSTOM_DOMAIN}..."
    gcloud run domain-mappings create \
        --service ${SERVICE_NAME} \
        --domain ${CUSTOM_DOMAIN} \
        --region ${REGION} \
        --project ${PROJECT_ID}
fi

exit 0
