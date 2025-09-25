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
REGION=${REGION:-us-central1}
SERVICE_NAME=${SERVICE_NAME:-ruleiq-backend}
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

# Check and create required secrets
check_and_create_secret "DATABASE_URL" "${DATABASE_URL}"
check_and_create_secret "JWT_SECRET_KEY" "${JWT_SECRET_KEY}"
check_and_create_secret "GOOGLE_API_KEY" "${GOOGLE_API_KEY}"
check_and_create_secret "GOOGLE_AI_API_KEY" "${GOOGLE_AI_API_KEY}"

# Optional secrets
if [ -n "${REDIS_URL}" ]; then
    check_and_create_secret "REDIS_URL" "${REDIS_URL}"
fi

if [ -n "${SENTRY_DSN}" ]; then
    check_and_create_secret "SENTRY_DSN" "${SENTRY_DSN}"
fi

# Build the Docker image
print_status "Building Docker image..."
docker build -t ${IMAGE_NAME}:latest .

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

# Create or update Cloud Run service
print_status "Deploying to Cloud Run..."

# Check if service exists
if gcloud run services describe ${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID} >/dev/null 2>&1; then
    print_status "Updating existing Cloud Run service..."
else
    print_status "Creating new Cloud Run service..."
fi

# Deploy the service
gcloud run deploy ${SERVICE_NAME} \
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
    --set-env-vars "PYTHONUNBUFFERED=1,PORT=8080,ENVIRONMENT=production" \
    --concurrency 80 \
    --cpu-throttling \
    --update-secrets "DATABASE_URL=DATABASE_URL:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest,GOOGLE_API_KEY=GOOGLE_API_KEY:latest,GOOGLE_AI_API_KEY=GOOGLE_AI_API_KEY:latest,REDIS_URL=REDIS_URL:latest" \
    --project ${PROJECT_ID}

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --format='value(status.url)')

print_status "Service deployed successfully!"
echo "Service URL: ${SERVICE_URL}"

# Test the health endpoint
print_status "Testing health endpoints..."

# Wait for service to be ready
sleep 10

# Test liveness endpoint
print_status "Testing liveness endpoint..."
LIVENESS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${SERVICE_URL}/health/live)

if [ "${LIVENESS_RESPONSE}" = "200" ]; then
    print_status "✓ Liveness check passed"
else
    print_error "✗ Liveness check failed (HTTP ${LIVENESS_RESPONSE})"
fi

# Test readiness endpoint
print_status "Testing readiness endpoint..."
READINESS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${SERVICE_URL}/health/ready)

if [ "${READINESS_RESPONSE}" = "200" ]; then
    print_status "✓ Readiness check passed"
else
    print_warning "✗ Readiness check failed (HTTP ${READINESS_RESPONSE}) - Database might not be connected"
fi

# Test detailed health endpoint
print_status "Testing detailed health endpoint..."
curl -s ${SERVICE_URL}/api/v1/health/detailed | jq '.' || true

print_status "Deployment complete!"
echo ""
echo "============================================"
echo "Deployment Summary:"
echo "  Service: ${SERVICE_NAME}"
echo "  Region: ${REGION}"
echo "  URL: ${SERVICE_URL}"
echo "  Image: ${IMAGE_NAME}:latest"
echo ""
echo "Next steps:"
echo "  1. Verify the service at: ${SERVICE_URL}"
echo "  2. Check logs: gcloud run logs read --service=${SERVICE_NAME} --region=${REGION}"
echo "  3. Monitor metrics in Google Cloud Console"
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