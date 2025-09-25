#!/bin/bash

# Doppler Secrets Configuration Script for RuleIQ
# This script configures the missing Vercel organization secrets in Doppler
# and prepares the environment for deployment with Doppler integration

set -e

echo "========================================="
echo "Doppler Secrets Configuration for RuleIQ"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Doppler CLI is installed
if ! command -v doppler &> /dev/null; then
    echo -e "${RED}❌ Doppler CLI is not installed${NC}"
    echo "Please install Doppler CLI first:"
    echo "  curl -Ls https://cli.doppler.com/install.sh | sh"
    exit 1
fi

echo -e "${GREEN}✅ Doppler CLI is installed${NC}"
echo ""

# Check if user is logged in to Doppler
if ! doppler whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️ You need to log in to Doppler${NC}"
    echo "Running: doppler login"
    doppler login
fi

echo -e "${GREEN}✅ Logged in to Doppler${NC}"
echo ""

# Project configuration from .vercel/project.json
VERCEL_ORG_ID="team_bGqFKQr7Q4LAO7GfXITsoA55"
VERCEL_PROJECT_ID="prj_KEX8s9AmCqmnioQRYN4KE0VdBP7n"

echo "📋 Project Configuration:"
echo "  - Vercel Organization ID: $VERCEL_ORG_ID"
echo "  - Vercel Project ID: $VERCEL_PROJECT_ID"
echo ""

# Switch to production configuration
echo "🔄 Switching to production configuration..."
doppler setup --project=ruleiq --config=production

echo -e "${GREEN}✅ Switched to production configuration${NC}"
echo ""

# Function to check if a secret exists
check_secret() {
    local secret_name=$1
    if doppler secrets get "$secret_name" --plain &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to set a secret
set_secret() {
    local secret_name=$1
    local secret_value=$2

    echo "  Setting $secret_name..."
    if doppler secrets set "$secret_name" "$secret_value" &> /dev/null; then
        echo -e "  ${GREEN}✅ $secret_name configured${NC}"
    else
        echo -e "  ${RED}❌ Failed to set $secret_name${NC}"
        return 1
    fi
}

echo "🔍 Checking and configuring required secrets..."
echo ""

# Configure Vercel organization secrets
echo "📦 Configuring Vercel Organization Secrets:"
if check_secret "VERCEL_ORG_ID"; then
    echo -e "  ${GREEN}✅ VERCEL_ORG_ID already configured${NC}"
else
    set_secret "VERCEL_ORG_ID" "$VERCEL_ORG_ID"
fi

if check_secret "VERCEL_PROJECT_ID"; then
    echo -e "  ${GREEN}✅ VERCEL_PROJECT_ID already configured${NC}"
else
    set_secret "VERCEL_PROJECT_ID" "$VERCEL_PROJECT_ID"
fi

echo ""

# Check for VERCEL_TOKEN
echo "🔐 Checking authentication tokens:"
if check_secret "VERCEL_TOKEN"; then
    echo -e "  ${GREEN}✅ VERCEL_TOKEN is configured${NC}"
else
    echo -e "  ${YELLOW}⚠️ VERCEL_TOKEN is not configured${NC}"
    echo ""
    echo "  To get your Vercel token:"
    echo "  1. Visit: https://vercel.com/account/tokens"
    echo "  2. Create a new token with full access"
    echo "  3. Copy the token"
    echo ""
    read -p "  Enter your Vercel token (input will be hidden): " -s VERCEL_TOKEN
    echo ""

    if [ -n "$VERCEL_TOKEN" ]; then
        set_secret "VERCEL_TOKEN" "$VERCEL_TOKEN"
    else
        echo -e "  ${RED}❌ Vercel token is required${NC}"
        exit 1
    fi
fi

echo ""

# Validate other required secrets
echo "🔍 Validating existing secrets:"
REQUIRED_SECRETS=(
    "DATABASE_URL"
    "JWT_SECRET_KEY"
    "NEXTAUTH_SECRET"
    "NEXTAUTH_URL"
    "OPENAI_API_KEY"
)

missing_secrets=()
for secret in "${REQUIRED_SECRETS[@]}"; do
    if check_secret "$secret"; then
        echo -e "  ${GREEN}✅ $secret is configured${NC}"
    else
        echo -e "  ${YELLOW}⚠️ $secret is missing${NC}"
        missing_secrets+=("$secret")
    fi
done

echo ""

if [ ${#missing_secrets[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️ Some secrets are missing:${NC}"
    for secret in "${missing_secrets[@]}"; do
        echo "  - $secret"
    done
    echo ""
    echo "These secrets should be configured for full functionality."
    echo "You can add them using: doppler secrets set SECRET_NAME"
    echo ""
fi

# Generate service token for GitHub Actions
echo "🔑 Generating GitHub Actions service token..."
echo ""
echo "Creating a service token for GitHub Actions CI/CD..."

# Generate the service token
SERVICE_TOKEN=$(doppler configs tokens create github-actions --project=ruleiq --config=production --plain 2>/dev/null || true)

if [ -n "$SERVICE_TOKEN" ]; then
    echo -e "${GREEN}✅ Service token generated successfully${NC}"
    echo ""
    echo "========================================="
    echo "IMPORTANT: Add this token to GitHub Secrets"
    echo "========================================="
    echo ""
    echo "1. Go to your GitHub repository settings"
    echo "2. Navigate to Settings > Secrets and variables > Actions"
    echo "3. Click 'New repository secret'"
    echo "4. Name: DOPPLER_TOKEN"
    echo "5. Value: (shown below)"
    echo ""
    echo "----------------------------------------"
    echo "$SERVICE_TOKEN"
    echo "----------------------------------------"
    echo ""
    echo "⚠️ This token will not be shown again!"
else
    echo -e "${YELLOW}ℹ️ Service token may already exist${NC}"
    echo ""
    echo "To view existing tokens:"
    echo "  doppler configs tokens list --project=ruleiq --config=production"
    echo ""
    echo "To revoke and create a new token:"
    echo "  doppler configs tokens revoke github-actions --project=ruleiq --config=production"
    echo "  doppler configs tokens create github-actions --project=ruleiq --config=production"
fi

echo ""
echo "========================================="
echo "✅ Doppler Configuration Complete"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Add the DOPPLER_TOKEN to GitHub Secrets (if not already done)"
echo "2. Push to main branch to trigger deployment"
echo "3. The deploy-vercel-doppler.yml workflow will handle the deployment"
echo ""
echo "To test locally:"
echo "  doppler run -- npm run dev"
echo ""
echo "To view all configured secrets:"
echo "  doppler secrets --project=ruleiq --config=production"
echo ""