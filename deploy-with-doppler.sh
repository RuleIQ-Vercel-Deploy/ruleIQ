#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 RuleIQ Doppler Deployment Helper"
echo "===================================="
echo ""

# 1. Check preconditions
echo "📋 Checking preconditions..."

# Check for doppler
if ! command -v doppler &> /dev/null; then
    echo -e "${RED}❌ Doppler CLI is not installed${NC}"
    echo "Please install it from: https://docs.doppler.com/docs/install-cli"
    exit 1
fi

# Check for jq
if ! command -v jq &> /dev/null; then
    echo -e "${RED}❌ jq is not installed${NC}"
    echo "Please install it using: apt-get install jq (or brew install jq on macOS)"
    exit 1
fi

echo -e "${GREEN}✅ All required tools are installed${NC}"
echo ""

# 2. Run configuration script
echo "🔧 Configuring Doppler secrets..."
if [ -f "scripts/deploy/configure-doppler-secrets.sh" ]; then
    bash scripts/deploy/configure-doppler-secrets.sh
else
    echo -e "${RED}❌ Configuration script not found at scripts/deploy/configure-doppler-secrets.sh${NC}"
    exit 1
fi
echo ""

# 3. Validate required secrets in Doppler
echo "🔍 Validating secrets in Doppler..."

PROJECT="ruleiq"
CONFIGS=("stg" "prd")
REQUIRED_SECRETS=("VERCEL_TOKEN" "VERCEL_ORG_ID" "VERCEL_PROJECT_ID" "DATABASE_URL")

for CONFIG in "${CONFIGS[@]}"; do
    echo "  Checking $CONFIG environment..."
    CONFIG_NAME=$([ "$CONFIG" = "stg" ] && echo "staging/preview" || echo "production")

    for SECRET in "${REQUIRED_SECRETS[@]}"; do
        if doppler secrets get "$SECRET" --plain --project="$PROJECT" --config="$CONFIG" >/dev/null 2>&1; then
            echo -e "    ${GREEN}✅ $SECRET exists in $CONFIG_NAME${NC}"
        else
            echo -e "    ${RED}❌ $SECRET missing in $CONFIG_NAME${NC}"
            MISSING_SECRETS=true
        fi
    done
done

if [ "${MISSING_SECRETS:-false}" = "true" ]; then
    echo -e "${RED}Some required secrets are missing. Please configure them before proceeding.${NC}"
    exit 1
fi
echo ""

# 4. Display or re-display DOPPLER_TOKEN
echo "📝 GitHub Actions Setup"
echo "======================="
echo ""

# Try to get the service token for GitHub Actions
SERVICE_TOKEN=$(doppler configs tokens list --project="$PROJECT" --config="prd" --json 2>/dev/null | jq -r '.[] | select(.name == "github-actions") | .token' || echo "")

if [ -z "$SERVICE_TOKEN" ]; then
    echo "Creating new service token for GitHub Actions..."
    SERVICE_TOKEN=$(doppler configs tokens create github-actions --project="$PROJECT" --config="prd" --plain 2>/dev/null || echo "")
fi

if [ -n "$SERVICE_TOKEN" ]; then
    echo -e "${GREEN}✅ Service token for GitHub Actions:${NC}"
    echo ""
    echo "Add this as a secret named DOPPLER_TOKEN in your GitHub repository:"
    echo "1. Go to: https://github.com/[your-org]/ruleiq/settings/secrets/actions"
    echo "2. Click 'New repository secret'"
    echo "3. Name: DOPPLER_TOKEN"
    echo "4. Value:"
    echo ""
    echo -e "${YELLOW}$SERVICE_TOKEN${NC}"
    echo ""
    echo "This token provides access to all configured environments."
else
    echo -e "${RED}❌ Could not retrieve or create service token${NC}"
    echo "Please create it manually in the Doppler dashboard"
fi
echo ""

# 5. Offer to trigger deployment
echo "🚀 Deployment Options"
echo "===================="
echo ""
echo "You can now:"
echo "1. Trigger deployment via GitHub Actions:"
echo "   - Go to: https://github.com/[your-org]/ruleiq/actions/workflows/deploy-vercel-doppler.yml"
echo "   - Click 'Run workflow'"
echo "   - Select environment (production or preview)"
echo ""
echo "2. Push to main branch to trigger automatic production deployment"
echo ""
echo "3. Create a pull request to trigger preview deployment"
echo ""

read -p "Would you like to test the deployment locally? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🧪 Running local deployment test..."

    # Check if vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        echo -e "${YELLOW}⚠️  Vercel CLI not installed. Installing...${NC}"
        npm install -g vercel@latest
    fi

    # Test with preview config
    echo "Testing with preview environment..."
    doppler run --project="$PROJECT" --config="stg" -- bash -c 'echo "✅ Can access Doppler secrets"'

    # Pull Vercel environment
    echo "Pulling Vercel environment..."
    doppler run --project="$PROJECT" --config="stg" -- vercel pull --yes --environment=preview

    echo -e "${GREEN}✅ Local test successful!${NC}"
    echo "You can now trigger the GitHub Action for full deployment."
fi

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo "Your project is ready for Doppler-based Vercel deployments."