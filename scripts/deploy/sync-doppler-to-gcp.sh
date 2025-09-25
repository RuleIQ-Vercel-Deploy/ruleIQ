#!/bin/bash

# Sync Doppler secrets to Google Secret Manager
# This script fetches secrets from Doppler and creates/updates them in Google Secret Manager

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

# Check if Doppler CLI is installed
if ! command -v doppler &> /dev/null; then
    print_error "Doppler CLI is not installed"
    echo "Install it from: https://docs.doppler.com/docs/install-cli"
    exit 1
fi

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud SDK is not installed"
    exit 1
fi

# Check required environment variables
if [ -z "$PROJECT_ID" ]; then
    print_error "PROJECT_ID environment variable is required"
    echo "Please set: export PROJECT_ID=your-gcp-project-id"
    exit 1
fi

# Set Doppler project and config
DOPPLER_PROJECT=${DOPPLER_PROJECT:-ruleiq}
DOPPLER_CONFIG=${DOPPLER_CONFIG:-production}

print_status "Configuration:"
echo "  GCP Project ID: ${PROJECT_ID}"
echo "  Doppler Project: ${DOPPLER_PROJECT}"
echo "  Doppler Config: ${DOPPLER_CONFIG}"

# Authenticate with Google Cloud
print_status "Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# Enable Secret Manager API if not already enabled
print_status "Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com

# List of secrets to sync from Doppler to GCP
SECRETS_TO_SYNC=(
    "DATABASE_URL"
    "JWT_SECRET_KEY"
    "REDIS_URL"
    "GOOGLE_API_KEY"
    "GOOGLE_AI_API_KEY"
    "OPENAI_API_KEY"
    "SENTRY_DSN"
    "AWS_ACCESS_KEY_ID"
    "AWS_SECRET_ACCESS_KEY"
    "STRIPE_API_KEY"
    "STRIPE_WEBHOOK_SECRET"
    "SENDGRID_API_KEY"
    "PUSHER_APP_ID"
    "PUSHER_KEY"
    "PUSHER_SECRET"
    "PUSHER_CLUSTER"
)

print_status "Fetching secrets from Doppler..."

# Function to create or update a secret in GCP
sync_secret() {
    local SECRET_NAME=$1
    local SECRET_VALUE=$2

    # Check if secret exists
    if gcloud secrets describe ${SECRET_NAME} --project=${PROJECT_ID} >/dev/null 2>&1; then
        print_status "Updating secret ${SECRET_NAME}..."
        # Create new version of existing secret
        echo -n "${SECRET_VALUE}" | gcloud secrets versions add ${SECRET_NAME} \
            --data-file=- \
            --project=${PROJECT_ID}
    else
        print_status "Creating secret ${SECRET_NAME}..."
        # Create new secret
        echo -n "${SECRET_VALUE}" | gcloud secrets create ${SECRET_NAME} \
            --replication-policy="automatic" \
            --data-file=- \
            --project=${PROJECT_ID}
    fi

    # Grant Cloud Run service account access to the secret
    print_status "Granting Cloud Run access to ${SECRET_NAME}..."
    gcloud secrets add-iam-policy-binding ${SECRET_NAME} \
        --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor" \
        --project=${PROJECT_ID} >/dev/null 2>&1 || true

    # Also grant compute service account access
    gcloud secrets add-iam-policy-binding ${SECRET_NAME} \
        --member="serviceAccount:${PROJECT_ID}-compute@developer.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor" \
        --project=${PROJECT_ID} >/dev/null 2>&1 || true
}

# Sync each secret
for SECRET_NAME in "${SECRETS_TO_SYNC[@]}"; do
    print_status "Processing ${SECRET_NAME}..."

    # Get secret value from Doppler
    SECRET_VALUE=$(doppler secrets get ${SECRET_NAME} --plain --project ${DOPPLER_PROJECT} --config ${DOPPLER_CONFIG} 2>/dev/null || echo "")

    if [ -z "${SECRET_VALUE}" ]; then
        print_warning "Secret ${SECRET_NAME} not found in Doppler or is empty, skipping..."
    else
        sync_secret "${SECRET_NAME}" "${SECRET_VALUE}"
        print_status "✓ ${SECRET_NAME} synced successfully"
    fi
done

print_status "Secret synchronization complete!"

# List all secrets in GCP
print_status "Current secrets in Google Secret Manager:"
gcloud secrets list --project=${PROJECT_ID} --format="table(name)"

print_status "Done! Secrets have been synced from Doppler to Google Secret Manager"
echo ""
echo "Next steps:"
echo "1. Deploy your Cloud Run service with these secrets"
echo "2. The secrets will be automatically injected as environment variables"
echo ""
echo "To manually verify a secret:"
echo "  gcloud secrets versions access latest --secret=DATABASE_URL --project=${PROJECT_ID}"