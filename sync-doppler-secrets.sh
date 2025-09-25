#!/bin/bash

# Quick script to sync Doppler secrets to Google Secret Manager
# Usage: ./sync-doppler-secrets.sh

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-ruleiq}
DOPPLER_PROJECT=${DOPPLER_PROJECT:-ruleiq}
DOPPLER_CONFIG=${DOPPLER_CONFIG:-production}

echo "🔄 Syncing Doppler secrets to Google Secret Manager..."
echo "   Project: ${PROJECT_ID}"
echo "   Doppler: ${DOPPLER_PROJECT}/${DOPPLER_CONFIG}"

# Check prerequisites
if ! command -v doppler &> /dev/null; then
    echo "❌ Doppler CLI not found. Install from: https://docs.doppler.com/docs/install-cli"
    exit 1
fi

if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not found"
    exit 1
fi

# Set GCP project
gcloud config set project ${PROJECT_ID}

# Core secrets required for Cloud Run
SECRETS=(
    "DATABASE_URL"
    "JWT_SECRET_KEY"
    "REDIS_URL"
    "GOOGLE_API_KEY"
    "GOOGLE_AI_API_KEY"
)

# Sync each secret
for SECRET in "${SECRETS[@]}"; do
    echo -n "Syncing ${SECRET}... "

    # Get value from Doppler
    VALUE=$(doppler secrets get ${SECRET} --plain 2>/dev/null || echo "")

    if [ -z "${VALUE}" ]; then
        echo "⚠️  Not found in Doppler"
        continue
    fi

    # Create or update in GCP
    if gcloud secrets describe ${SECRET} >/dev/null 2>&1; then
        echo -n "${VALUE}" | gcloud secrets versions add ${SECRET} --data-file=- >/dev/null 2>&1
        echo "✅ Updated"
    else
        echo -n "${VALUE}" | gcloud secrets create ${SECRET} --replication-policy="automatic" --data-file=- >/dev/null 2>&1
        echo "✅ Created"
    fi

    # Grant access to Cloud Run service accounts
    for SA in "${PROJECT_ID}-compute@developer.gserviceaccount.com" "${PROJECT_ID}@appspot.gserviceaccount.com"; do
        gcloud secrets add-iam-policy-binding ${SECRET} \
            --member="serviceAccount:${SA}" \
            --role="roles/secretmanager.secretAccessor" >/dev/null 2>&1 || true
    done
done

echo ""
echo "✅ Secrets synced successfully!"
echo ""
echo "To deploy Cloud Run with these secrets, run:"
echo "  gcloud builds submit --config cloudbuild.yaml"
echo ""
echo "Or trigger via GitHub push to main branch"