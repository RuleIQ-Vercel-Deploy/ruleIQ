#!/bin/bash

# Simplified Cloud Run deployment script
# This script only handles the Cloud Run deployment since the Docker image is already built

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="ruleiq"
SERVICE_NAME="ruleiq-frontend"
REGION="europe-west2"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
DOPPLER_PROJECT="ruleiq"
DOPPLER_CONFIG="prd"
COMMIT_SHA="03553d734"  # Use the existing image
IMAGE_TAG="${IMAGE_NAME}:${COMMIT_SHA}"

echo -e "${BLUE}🚀 RuleIQ Frontend Cloud Run Deployment${NC}"
echo -e "${BLUE}=========================================${NC}"

# Create or update secrets in Google Secret Manager from Doppler
echo -e "${YELLOW}🔐 Syncing secrets from Doppler to Google Secret Manager...${NC}"

# Get environment variables from Doppler
DOPPLER_SECRETS=$(doppler secrets download --project $DOPPLER_PROJECT --config $DOPPLER_CONFIG --format json --no-file)

# List of frontend environment variables to sync
FRONTEND_SECRETS=(
    "NEXT_PUBLIC_API_URL"
    "NEXT_PUBLIC_WEBSOCKET_URL"
    "NEXT_PUBLIC_AUTH_DOMAIN"
    "NEXT_PUBLIC_JWT_EXPIRES_IN"
    "NEXT_PUBLIC_ENABLE_ANALYTICS"
    "NEXT_PUBLIC_ENABLE_SENTRY"
    "NEXT_PUBLIC_ENABLE_MOCK_DATA"
)

for secret_name in "${FRONTEND_SECRETS[@]}"; do
    # Extract value from Doppler JSON (handle case where key might not exist)
    SECRET_VALUE=$(echo "$DOPPLER_SECRETS" | jq -r ".$secret_name // empty")
    
    if [ ! -z "$SECRET_VALUE" ] && [ "$SECRET_VALUE" != "null" ] && [ "$SECRET_VALUE" != "empty" ]; then
        echo -e "${BLUE}  Creating/updating secret: ${secret_name}${NC}"
        
        # Create or update secret in Google Secret Manager
        if gcloud secrets describe $secret_name --quiet 2>/dev/null; then
            # Secret exists, add new version
            echo -n "$SECRET_VALUE" | gcloud secrets versions add $secret_name --data-file=-
        else
            # Secret doesn't exist, create it
            echo -n "$SECRET_VALUE" | gcloud secrets create $secret_name --data-file=- --labels=service=frontend,project=ruleiq
        fi
        
        # Grant access to the Cloud Run service account
        gcloud secrets add-iam-policy-binding $secret_name \
            --member="serviceAccount:${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
            --role="roles/secretmanager.secretAccessor" \
            --quiet 2>/dev/null || true
    else
        echo -e "${YELLOW}  Skipping empty secret: ${secret_name}${NC}"
    fi
done

# Create service account if it doesn't exist
echo -e "${YELLOW}🔐 Ensuring service account exists...${NC}"
if ! gcloud iam service-accounts describe "${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com" --quiet 2>/dev/null; then
    echo -e "${BLUE}  Creating service account: ${SERVICE_NAME}-sa${NC}"
    gcloud iam service-accounts create ${SERVICE_NAME}-sa \
        --display-name="RuleIQ Frontend Service Account" \
        --description="Service account for RuleIQ frontend Cloud Run service"
fi

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"

# Build secrets string for gcloud run deploy
SECRETS_STRING=""
for secret_name in "${FRONTEND_SECRETS[@]}"; do
    if gcloud secrets describe $secret_name --quiet 2>/dev/null; then
        if [ ! -z "$SECRETS_STRING" ]; then
            SECRETS_STRING="${SECRETS_STRING},"
        fi
        SECRETS_STRING="${SECRETS_STRING}${secret_name}=${secret_name}:latest"
    fi
done

# Deploy with comprehensive configuration
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 100 \
    --min-instances 1 \
    --port 3000 \
    --execution-environment gen2 \
    --cpu-boost \
    --concurrency 80 \
    --cpu-throttling \
    --set-env-vars "NODE_ENV=production,NEXT_TELEMETRY_DISABLED=1,NEXT_PUBLIC_ENV=production" \
    --set-secrets="$SECRETS_STRING" \
    --service-account="${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --labels="environment=production,service=frontend,project=ruleiq"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --format 'value(status.url)')

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Service URL: ${SERVICE_URL}${NC}"

# Validate deployment
echo -e "${YELLOW}🏥 Validating deployment...${NC}"
sleep 10  # Wait for service to stabilize

# Test health endpoint
if curl -f --max-time 30 "${SERVICE_URL}/" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${YELLOW}⚠️  Health check failed, but service might still be starting${NC}"
fi

# Show final summary
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}🎉 DEPLOYMENT SUCCESSFUL!${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}📦 Service: ${SERVICE_NAME}${NC}"
echo -e "${GREEN}🌍 URL: ${SERVICE_URL}${NC}"
echo -e "${GREEN}📍 Region: ${REGION}${NC}"
echo -e "${GREEN}🏷️  Image: ${IMAGE_TAG}${NC}"
echo -e "${GREEN}🔐 Secrets: Managed by Doppler → Google Secret Manager${NC}"
echo -e "${BLUE}================================================${NC}"

# No temporary files to clean up

echo -e "${GREEN}🚀 Frontend deployment to Cloud Run complete!${NC}"