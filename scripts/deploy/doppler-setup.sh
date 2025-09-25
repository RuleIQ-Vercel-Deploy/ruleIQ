#!/bin/bash

# Doppler Setup Script for ruleIQ Organization Deployment
# This script helps configure Doppler for organization-level secrets management

set -e

echo "🔐 Doppler Secrets Management Setup for ruleIQ"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
ORG_NAME="RuleIQ-Vercel-Deploy"
PROJECT_NAME="ruleiq"

# Check if Doppler CLI is installed
echo -e "${BLUE}Checking Doppler CLI installation...${NC}"
if command -v doppler &> /dev/null; then
    echo -e "${GREEN}✅ Doppler CLI installed: $(doppler --version)${NC}"
else
    echo -e "${RED}❌ Doppler CLI not installed${NC}"
    echo -e "${YELLOW}Installing Doppler CLI...${NC}"

    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -Ls --tlsv1.3 --proto "=https" --retry 3 https://cli.doppler.com/install.sh | sudo sh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install dopplerhq/cli/doppler
    else
        echo -e "${RED}Please install Doppler CLI manually: https://docs.doppler.com/docs/cli${NC}"
        exit 1
    fi
fi

# Check Doppler authentication
echo -e "${BLUE}Checking Doppler authentication...${NC}"
if doppler me &> /dev/null; then
    echo -e "${GREEN}✅ Authenticated as: $(doppler me --json | jq -r .name)${NC}"
else
    echo -e "${YELLOW}Please authenticate with Doppler:${NC}"
    doppler login
fi

# Setup Doppler project
echo -e "${BLUE}Setting up Doppler project...${NC}"
echo -e "${CYAN}Select the following when prompted:${NC}"
echo "  1. Organization: ${ORG_NAME}"
echo "  2. Project: ${PROJECT_NAME}"
echo "  3. Config: production (for production deployment)"
echo ""

doppler setup

# Verify setup
echo -e "${BLUE}Verifying Doppler configuration...${NC}"
PROJECT=$(doppler configure get project --plain)
CONFIG=$(doppler configure get config --plain)

if [[ "$PROJECT" == "$PROJECT_NAME" ]]; then
    echo -e "${GREEN}✅ Project configured: $PROJECT${NC}"
else
    echo -e "${YELLOW}⚠️  Project mismatch. Expected: $PROJECT_NAME, Got: $PROJECT${NC}"
fi

echo -e "${GREEN}✅ Environment: $CONFIG${NC}"

# Check required secrets
echo -e "${BLUE}Checking required secrets in Doppler...${NC}"

REQUIRED_SECRETS=(
    "VERCEL_TOKEN"
    "VERCEL_ORG_ID"
    "VERCEL_PROJECT_ID"
    "DATABASE_URL"
    "JWT_SECRET"
    "SECRET_KEY"
)

OPTIONAL_SECRETS=(
    "OPENAI_API_KEY"
    "GOOGLE_AI_API_KEY"
    "REDIS_URL"
    "SENTRY_DSN"
    "SONAR_TOKEN"
    "SONAR_HOST_URL"
)

echo -e "${CYAN}Required Secrets:${NC}"
MISSING_REQUIRED=0
for secret in "${REQUIRED_SECRETS[@]}"; do
    if doppler secrets get "$secret" --plain &> /dev/null; then
        echo -e "  ${GREEN}✅ $secret${NC}"
    else
        echo -e "  ${RED}❌ $secret (MISSING)${NC}"
        MISSING_REQUIRED=$((MISSING_REQUIRED + 1))
    fi
done

echo -e "\n${CYAN}Optional Secrets:${NC}"
for secret in "${OPTIONAL_SECRETS[@]}"; do
    if doppler secrets get "$secret" --plain &> /dev/null; then
        echo -e "  ${GREEN}✅ $secret${NC}"
    else
        echo -e "  ${YELLOW}⚠️  $secret (not configured)${NC}"
    fi
done

# Generate service token for GitHub Actions
if [[ $MISSING_REQUIRED -eq 0 ]]; then
    echo -e "\n${GREEN}All required secrets are configured!${NC}"

    echo -e "\n${BLUE}Generating Doppler service token for GitHub Actions...${NC}"
    echo -e "${YELLOW}Creating service token with read-only access to production secrets${NC}"

    # Generate token name with timestamp
    TOKEN_NAME="github-actions-$(date +%Y%m%d-%H%M%S)"

    echo -e "${CYAN}Run this command to generate a service token:${NC}"
    echo -e "${MAGENTA}doppler configs tokens create $TOKEN_NAME --config production --plain${NC}"
    echo ""
    echo -e "${YELLOW}Then add this token as DOPPLER_TOKEN in GitHub Actions:${NC}"
    echo -e "${BLUE}https://github.com/$ORG_NAME/$PROJECT_NAME/settings/secrets/actions${NC}"
else
    echo -e "\n${RED}Missing $MISSING_REQUIRED required secrets!${NC}"
    echo -e "${YELLOW}Please configure the missing secrets in Doppler:${NC}"
    echo -e "${BLUE}doppler secrets set SECRET_NAME secret_value${NC}"
    echo -e "${YELLOW}Or use the Doppler dashboard:${NC}"
    echo -e "${BLUE}https://dashboard.doppler.com${NC}"
fi

# Show how to use Doppler in development
echo -e "\n${MAGENTA}═══════════════════════════════════════════════${NC}"
echo -e "${CYAN}Development Usage:${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Run commands with Doppler:${NC}"
echo -e "  ${CYAN}doppler run -- python main.py${NC}"
echo -e "  ${CYAN}doppler run -- npm run dev${NC}"
echo ""
echo -e "${YELLOW}Export secrets to .env file (for local development):${NC}"
echo -e "  ${CYAN}doppler secrets download --no-file --format env > .env${NC}"
echo ""
echo -e "${YELLOW}View all secrets:${NC}"
echo -e "  ${CYAN}doppler secrets${NC}"
echo ""
echo -e "${YELLOW}Set a secret:${NC}"
echo -e "  ${CYAN}doppler secrets set SECRET_NAME${NC}"

# Summary
echo -e "\n${MAGENTA}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 Doppler Setup Complete!${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo "1. Ensure all required secrets are configured in Doppler"
echo "2. Generate a service token for GitHub Actions"
echo "3. Add DOPPLER_TOKEN to GitHub Actions secrets"
echo "4. Deploy with: git push origin main"
echo ""
echo -e "${GREEN}Organization: $ORG_NAME${NC}"
echo -e "${GREEN}Project: $PROJECT_NAME${NC}"
echo -e "${GREEN}Config: $CONFIG${NC}"