#!/bin/bash
# RuleIQ Production Deployment Script
# Tests locally, builds, and deploys to Cloud Run

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-$(gcloud config get project 2>/dev/null)}
SERVICE_NAME=${SERVICE_NAME:-ruleiq-backend}
REGION=${REGION:-europe-west2}
IMAGE_TAG=${IMAGE_TAG:-$(git rev-parse --short HEAD 2>/dev/null || echo "latest")}
IMAGE_NAME="europe-west2-docker.pkg.dev/$PROJECT_ID/ruleiq/$SERVICE_NAME:$IMAGE_TAG"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

echo "🚀 RuleIQ Production Deployment"
echo "==============================="
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo "Image: $IMAGE_NAME"
echo

# Step 1: Verify Doppler is configured
if ! doppler secrets --only-names >/dev/null 2>&1; then
    print_error "Doppler not configured. Run: doppler setup"
    exit 1
fi
print_status "Doppler configuration verified"

# Step 2: Test the production app locally
print_status "Testing production app locally..."
if ! timeout 10s doppler run -- python -c "
import sys
sys.path.insert(0, '.')
try:
    from production_start import app
    print('✅ Production app imports successfully')
except Exception as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"; then
    print_error "Production app failed local test. Check imports."
    exit 1
fi

# Step 3: Build the Docker image
print_status "Building Docker image..."
if docker build -f Dockerfile.production -t $SERVICE_NAME:$IMAGE_TAG .; then
    print_status "Docker image built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

# Step 4: Test the container locally
print_status "Testing container locally..."
CONTAINER_ID=$(docker run -d -p 8081:8080 -e DOPPLER_TOKEN="$DOPPLER_TOKEN" $SERVICE_NAME:$IMAGE_TAG)
sleep 5

if curl -f http://localhost:8081/health >/dev/null 2>&1; then
    print_status "Container test successful"
    docker stop $CONTAINER_ID >/dev/null
else
    print_error "Container test failed"
    docker logs $CONTAINER_ID
    docker stop $CONTAINER_ID >/dev/null
    exit 1
fi

# Step 5: Push to Artifact Registry
print_status "Pushing to Artifact Registry..."
docker tag $SERVICE_NAME:$IMAGE_TAG $IMAGE_NAME
if docker push $IMAGE_NAME; then
    print_status "Image pushed to registry"
else
    print_error "Failed to push image"
    exit 1
fi

# Step 6: Deploy to Cloud Run
print_status "Deploying to Cloud Run..."
if gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --region $REGION \
  --allow-unauthenticated \
  --set-secrets DOPPLER_TOKEN=DOPPLER_TOKEN:latest \
  --cpu 1 \
  --memory 512Mi \
  --max-instances 5 \
  --min-instances 0 \
  --concurrency 80 \
  --timeout 300 \
  --port 8080; then
    print_status "Deployment successful!"
else
    print_error "Deployment failed"
    exit 1
fi

# Step 7: Get service URL and test
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)")
print_status "Service URL: $SERVICE_URL"

echo
print_status "Testing deployed service..."
if curl -f "$SERVICE_URL/health" >/dev/null 2>&1; then
    print_status "🎉 Deployment successful! Service is healthy."
    echo "📱 Service URL: $SERVICE_URL"
    echo "🏥 Health: $SERVICE_URL/health"
    echo "📊 Status: $SERVICE_URL/api/v1/status"
else
    print_warning "Deployment completed but service not responding"
    echo "Check logs with: gcloud run services logs read $SERVICE_NAME --region $REGION"
fi

echo
print_status "Deployment complete!"