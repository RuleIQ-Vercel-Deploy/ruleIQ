#!/bin/bash

# RuleIQ Frontend Deployment Script for Google Cloud Run
# This script deploys the Next.js frontend to Google Cloud Run using Doppler for secrets management

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

echo -e "${BLUE}🚀 RuleIQ Frontend Deployment to Google Cloud Run${NC}"
echo -e "${BLUE}================================================${NC}"

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install Google Cloud SDK.${NC}"
    exit 1
fi

# Check if doppler is installed and authenticated
if ! command -v doppler &> /dev/null; then
    echo -e "${RED}❌ Doppler CLI not found. Please install Doppler CLI.${NC}"
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
    exit 1
fi

# Verify gcloud authentication and project
echo -e "${YELLOW}🔐 Verifying gcloud authentication...${NC}"
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠️  Setting gcloud project to ${PROJECT_ID}...${NC}"
    gcloud config set project $PROJECT_ID
fi

# Verify Doppler authentication
echo -e "${YELLOW}🔐 Verifying Doppler authentication...${NC}"
if ! doppler projects > /dev/null 2>&1; then
    echo -e "${RED}❌ Doppler not authenticated. Please run 'doppler login'${NC}"
    exit 1
fi

# Enable required APIs
echo -e "${YELLOW}🔧 Ensuring required APIs are enabled...${NC}"
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable secretmanager.googleapis.com --quiet

# Check if the production build exists
echo -e "${YELLOW}📦 Checking if production build exists...${NC}"
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Not in a Node.js project directory. Please run from the frontend directory.${NC}"
    exit 1
fi

# Install dependencies and build
echo -e "${YELLOW}📦 Installing dependencies and building...${NC}"
if command -v pnpm &> /dev/null; then
    echo -e "${BLUE}Using pnpm...${NC}"
    pnpm install --frozen-lockfile
    
    # Inject production environment variables from Doppler during build
    echo -e "${YELLOW}🔑 Loading production environment from Doppler...${NC}"
    doppler run --project $DOPPLER_PROJECT --config $DOPPLER_CONFIG -- pnpm build
else
    echo -e "${BLUE}Using npm...${NC}"
    npm ci
    doppler run --project $DOPPLER_PROJECT --config $DOPPLER_CONFIG -- npm run build
fi

# Build Docker image
echo -e "${YELLOW}🐳 Building Docker image...${NC}"
COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "local")
IMAGE_TAG="${IMAGE_NAME}:${COMMIT_SHA}"
IMAGE_LATEST="${IMAGE_NAME}:latest"

# Get environment variables from Doppler for Docker build
echo -e "${YELLOW}🔑 Preparing environment variables for Docker build...${NC}"

# Get individual secrets directly from Doppler
NEXT_PUBLIC_API_URL=$(doppler secrets get NEXT_PUBLIC_API_URL --project $DOPPLER_PROJECT --config $DOPPLER_CONFIG --plain)
NEXT_PUBLIC_WEBSOCKET_URL=$(doppler secrets get NEXT_PUBLIC_WEBSOCKET_URL --project $DOPPLER_PROJECT --config $DOPPLER_CONFIG --plain)
NEXT_PUBLIC_AUTH_DOMAIN=$(doppler secrets get NEXT_PUBLIC_AUTH_DOMAIN --project $DOPPLER_PROJECT --config $DOPPLER_CONFIG --plain)
NEXT_PUBLIC_JWT_EXPIRES_IN=$(doppler secrets get NEXT_PUBLIC_JWT_EXPIRES_IN --project $DOPPLER_PROJECT --config $DOPPLER_CONFIG --plain)
NEXT_PUBLIC_ENABLE_ANALYTICS=$(doppler secrets get NEXT_PUBLIC_ENABLE_ANALYTICS --project $DOPPLER_PROJECT --config $DOPPLER_CONFIG --plain)
NEXT_PUBLIC_ENABLE_SENTRY=$(doppler secrets get NEXT_PUBLIC_ENABLE_SENTRY --project $DOPPLER_PROJECT --config $DOPPLER_CONFIG --plain)
NEXT_PUBLIC_ENABLE_MOCK_DATA=$(doppler secrets get NEXT_PUBLIC_ENABLE_MOCK_DATA --project $DOPPLER_PROJECT --config $DOPPLER_CONFIG --plain)

# Build with cache optimization and environment variables
docker build \
    --cache-from $IMAGE_LATEST \
    -t $IMAGE_TAG \
    -t $IMAGE_LATEST \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg NEXT_PUBLIC_API_URL="$NEXT_PUBLIC_API_URL" \
    --build-arg NEXT_PUBLIC_WEBSOCKET_URL="$NEXT_PUBLIC_WEBSOCKET_URL" \
    --build-arg NEXT_PUBLIC_AUTH_DOMAIN="$NEXT_PUBLIC_AUTH_DOMAIN" \
    --build-arg NEXT_PUBLIC_JWT_EXPIRES_IN="$NEXT_PUBLIC_JWT_EXPIRES_IN" \
    --build-arg NEXT_PUBLIC_ENABLE_ANALYTICS="$NEXT_PUBLIC_ENABLE_ANALYTICS" \
    --build-arg NEXT_PUBLIC_ENABLE_SENTRY="$NEXT_PUBLIC_ENABLE_SENTRY" \
    --build-arg NEXT_PUBLIC_ENABLE_MOCK_DATA="$NEXT_PUBLIC_ENABLE_MOCK_DATA" \
    --build-arg NEXT_PUBLIC_ENV="production" \
    .

# Push image to Container Registry
echo -e "${YELLOW}📤 Pushing image to Container Registry...${NC}"
docker push $IMAGE_TAG
docker push $IMAGE_LATEST

# Create or update secrets in Google Secret Manager from Doppler
echo -e "${YELLOW}🔐 Syncing secrets from Doppler to Google Secret Manager...${NC}"

# Get environment variables from Doppler
doppler secrets download --project $DOPPLER_PROJECT --config $DOPPLER_CONFIG --format json --silent
DOPPLER_SECRETS=$(cat doppler.json)

# List of frontend environment variables to sync
FRONTEND_SECRETS=(
    "NEXT_PUBLIC_API_URL"
    "NEXT_PUBLIC_WEBSOCKET_URL"
    "NEXT_PUBLIC_APP_URL"
    "NEXT_PUBLIC_HELP_URL"
    "NEXT_PUBLIC_DOCS_URL"
    "NEXT_PUBLIC_AUTH_DOMAIN"
    "NEXT_PUBLIC_JWT_EXPIRES_IN"
    "NEXT_PUBLIC_SUPPORT_EMAIL"
    "NEXT_PUBLIC_ADMIN_EMAIL"
    "NEXT_PUBLIC_CONTACT_EMAIL"
    "NEXT_PUBLIC_ENABLE_ANALYTICS"
    "NEXT_PUBLIC_ENABLE_SENTRY"
    "NEXT_PUBLIC_ENABLE_MOCK_DATA"
    "SENTRY_DSN"
    "SENTRY_ORG"
    "SENTRY_PROJECT"
    "SENTRY_AUTH_TOKEN"
    "NEXT_PUBLIC_VERCEL_ANALYTICS_ID"
    "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY"
)

for secret_name in "${FRONTEND_SECRETS[@]}"; do
    # Extract value from Doppler JSON (handle case where key might not exist)
    SECRET_VALUE=$(echo "$DOPPLER_SECRETS" | jq -r ".$secret_name // empty")
    
    if [ ! -z "$SECRET_VALUE" ] && [ "$SECRET_VALUE" != "null" ]; then
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
    --startup-cpu-boost \
    --concurrency 80 \
    --cpu-throttling \
    --set-env-vars "NODE_ENV=production,PORT=3000,NEXT_TELEMETRY_DISABLED=1,NEXT_PUBLIC_ENV=production" \
    --set-secrets="$SECRETS_STRING" \
    --service-account="${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --labels="environment=production,service=frontend,project=ruleiq" \
    --quiet

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

# Optional: Open in browser (uncomment if desired)
# echo -e "${BLUE}Opening service URL in browser...${NC}"
# xdg-open "$SERVICE_URL" 2>/dev/null || open "$SERVICE_URL" 2>/dev/null || true

# Clean up temporary files
rm -f doppler.json

echo -e "${GREEN}🚀 Frontend deployment complete!${NC}"
