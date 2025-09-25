#!/bin/bash

# Setup Google Cloud Service Account for GitHub Actions
# This creates a service account with necessary permissions for Cloud Run deployment

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_info() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Configuration
PROJECT_ID=${PROJECT_ID:-ruleiq}
SERVICE_ACCOUNT_NAME="github-actions-deploy"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="gcp-sa-key.json"

echo ""
echo "==========================================="
echo "Google Cloud Service Account Setup"
echo "==========================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud SDK is not installed"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
print_status "Setting project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
print_status "Enabling required Google Cloud APIs..."
gcloud services enable \
    iam.googleapis.com \
    cloudresourcemanager.googleapis.com \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    --project=${PROJECT_ID}

# Check if service account exists
print_info "Checking if service account exists..."
if gcloud iam service-accounts describe ${SERVICE_ACCOUNT_EMAIL} --project=${PROJECT_ID} >/dev/null 2>&1; then
    print_warning "Service account ${SERVICE_ACCOUNT_EMAIL} already exists"
    read -p "Do you want to create a new key for this account? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Exiting without changes"
        exit 0
    fi
else
    # Create service account
    print_status "Creating service account ${SERVICE_ACCOUNT_NAME}..."
    gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
        --display-name="GitHub Actions Deploy Account" \
        --description="Service account for GitHub Actions to deploy to Cloud Run" \
        --project=${PROJECT_ID}
fi

# Grant necessary roles to the service account
print_status "Granting necessary roles to service account..."

ROLES=(
    "roles/run.admin"                    # Deploy and manage Cloud Run services
    "roles/storage.admin"                 # Push images to Container Registry
    "roles/secretmanager.admin"           # Manage secrets
    "roles/iam.serviceAccountUser"        # Act as service account
    "roles/cloudbuild.builds.builder"     # Submit builds
    "roles/viewer"                        # View project resources
)

for ROLE in "${ROLES[@]}"; do
    print_info "Granting ${ROLE}..."
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="${ROLE}" \
        --project=${PROJECT_ID} >/dev/null 2>&1 || true
done

# Create and download service account key
print_status "Creating service account key..."
gcloud iam service-accounts keys create ${KEY_FILE} \
    --iam-account=${SERVICE_ACCOUNT_EMAIL} \
    --project=${PROJECT_ID}

# Display the key (base64 encoded for easy copying)
print_status "Service account key created successfully!"
echo ""
echo "==========================================="
echo "IMPORTANT: Save this information"
echo "==========================================="
echo ""
print_info "Service Account Email: ${SERVICE_ACCOUNT_EMAIL}"
print_info "Key saved to: ${KEY_FILE}"
echo ""
print_warning "GitHub Secret Setup Instructions:"
echo ""
echo "1. Copy the JSON key content:"
echo "   cat ${KEY_FILE}"
echo ""
echo "2. Go to your GitHub repository:"
echo "   https://github.com/RuleIQ-Vercel-Deploy/ruleIQ/settings/secrets/actions"
echo ""
echo "3. Click 'New repository secret'"
echo ""
echo "4. Add the following secret:"
echo "   Name: GCP_SA_KEY"
echo "   Value: [Paste the entire JSON content from step 1]"
echo ""
echo "5. Click 'Add secret'"
echo ""
echo "==========================================="
echo ""
print_warning "SECURITY NOTES:"
echo "• Keep the ${KEY_FILE} file secure and never commit it to git"
echo "• Add ${KEY_FILE} to .gitignore"
echo "• Delete the local key file after adding to GitHub secrets"
echo "• The key provides full deployment access to your GCP project"
echo ""
echo "To view the key content for copying:"
echo ""
echo "cat ${KEY_FILE}"
echo ""
echo "To delete the key file after setup:"
echo "rm ${KEY_FILE}"
echo ""
print_status "Setup complete!"