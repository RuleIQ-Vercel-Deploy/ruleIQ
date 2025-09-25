#!/bin/bash

# Configure GitHub Secrets for Vercel Deployment
# This script helps set up the required secrets in the GitHub repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Configuration
ORG_NAME="RuleIQ-Vercel-Deploy"
REPO_NAME="ruleIQ"
REPO_SLUG="${ORG_NAME}/${REPO_NAME}"

echo -e "${MAGENTA}${BOLD}🔐 GitHub Secrets Configuration for Vercel Deployment${NC}"
echo -e "${BLUE}============================================================${NC}"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo -e "${YELLOW}Install it from: https://cli.github.com/${NC}"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with GitHub CLI${NC}"
    echo -e "${YELLOW}Run: gh auth login${NC}"
    exit 1
fi

# Get Vercel configuration from local .vercel/project.json
if [ -f ".vercel/project.json" ]; then
    echo -e "${GREEN}✅ Found local Vercel configuration${NC}"
    VERCEL_PROJECT_ID=$(jq -r '.projectId' .vercel/project.json)
    VERCEL_ORG_ID=$(jq -r '.orgId' .vercel/project.json)
    echo -e "  Project ID: ${CYAN}${VERCEL_PROJECT_ID}${NC}"
    echo -e "  Org ID: ${CYAN}${VERCEL_ORG_ID}${NC}"
else
    echo -e "${YELLOW}⚠️  No .vercel/project.json found${NC}"
    echo "Please provide the Vercel configuration:"
    read -p "VERCEL_PROJECT_ID: " VERCEL_PROJECT_ID
    read -p "VERCEL_ORG_ID: " VERCEL_ORG_ID
fi

# Get Vercel token
echo -e "\n${YELLOW}📝 Vercel Token Required${NC}"
echo -e "Get your token from: ${CYAN}https://vercel.com/account/tokens${NC}"
echo -e "Create a new token with 'Full Access' scope"
read -s -p "Enter VERCEL_TOKEN: " VERCEL_TOKEN
echo

# Get Neon database URL (optional but recommended)
echo -e "\n${YELLOW}📝 Neon Database Configuration (optional)${NC}"
echo -e "Get your database URL from: ${CYAN}https://console.neon.tech/${NC}"
read -p "Enter NEON_DATABASE_URL (or press Enter to skip): " NEON_DATABASE_URL

echo -e "\n${BLUE}============================================================${NC}"
echo -e "${CYAN}Configuring secrets for: ${REPO_SLUG}${NC}"
echo -e "${BLUE}============================================================${NC}"

# Function to set secret
set_secret() {
    local name=$1
    local value=$2
    if [ -n "$value" ]; then
        echo -n -e "${YELLOW}Setting ${name}...${NC} "
        if echo "$value" | gh secret set "$name" --repo "$REPO_SLUG" 2>/dev/null; then
            echo -e "${GREEN}✅${NC}"
        else
            echo -e "${RED}❌ Failed${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}Skipping ${name} (no value provided)${NC}"
    fi
}

# Set the secrets
echo -e "\n${CYAN}Setting GitHub repository secrets...${NC}"
set_secret "VERCEL_TOKEN" "$VERCEL_TOKEN"
set_secret "VERCEL_ORG_ID" "$VERCEL_ORG_ID"
set_secret "VERCEL_PROJECT_ID" "$VERCEL_PROJECT_ID"

if [ -n "$NEON_DATABASE_URL" ]; then
    set_secret "NEON_DATABASE_URL" "$NEON_DATABASE_URL"
fi

# Verify secrets are set
echo -e "\n${CYAN}Verifying secrets...${NC}"
SECRETS=$(gh secret list --repo "$REPO_SLUG" 2>/dev/null)

if echo "$SECRETS" | grep -q "VERCEL_TOKEN"; then
    echo -e "${GREEN}✅ VERCEL_TOKEN is set${NC}"
else
    echo -e "${RED}❌ VERCEL_TOKEN is missing${NC}"
fi

if echo "$SECRETS" | grep -q "VERCEL_ORG_ID"; then
    echo -e "${GREEN}✅ VERCEL_ORG_ID is set${NC}"
else
    echo -e "${RED}❌ VERCEL_ORG_ID is missing${NC}"
fi

if echo "$SECRETS" | grep -q "VERCEL_PROJECT_ID"; then
    echo -e "${GREEN}✅ VERCEL_PROJECT_ID is set${NC}"
else
    echo -e "${RED}❌ VERCEL_PROJECT_ID is missing${NC}"
fi

if echo "$SECRETS" | grep -q "NEON_DATABASE_URL"; then
    echo -e "${GREEN}✅ NEON_DATABASE_URL is set${NC}"
else
    echo -e "${YELLOW}⚠️  NEON_DATABASE_URL not set (optional)${NC}"
fi

echo -e "\n${BLUE}============================================================${NC}"
echo -e "${GREEN}${BOLD}✅ Configuration Complete!${NC}"
echo -e "\n${CYAN}Next steps:${NC}"
echo -e "1. Re-run the deployment: ${YELLOW}python3 scripts/deploy/execute-org-deployment.py --yes${NC}"
echo -e "2. Monitor at: ${CYAN}https://github.com/${REPO_SLUG}/actions${NC}"
echo -e "3. Check Vercel dashboard: ${CYAN}https://vercel.com/${NC}"

echo -e "\n${MAGENTA}Note: The secrets are now stored in the GitHub repository.${NC}"
echo -e "${MAGENTA}They will be used automatically by GitHub Actions.${NC}"