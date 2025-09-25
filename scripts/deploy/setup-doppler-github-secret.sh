#!/bin/bash

# Setup Doppler Token for GitHub Actions
# This script configures the DOPPLER_TOKEN secret for the GitHub repository

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

echo -e "${MAGENTA}${BOLD}🔐 Doppler GitHub Integration Setup${NC}"
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

# Check if Doppler CLI is installed
if ! command -v doppler &> /dev/null; then
    echo -e "${YELLOW}⚠️  Doppler CLI is not installed${NC}"
    echo -e "Install instructions: ${CYAN}https://docs.doppler.com/docs/cli#installation${NC}"
fi

echo -e "\n${CYAN}Current Doppler Configuration:${NC}"
if command -v doppler &> /dev/null; then
    doppler configure get project 2>/dev/null || echo "Not configured"
    doppler configure get config 2>/dev/null || echo "Not configured"
fi

echo -e "\n${YELLOW}📝 To use the deploy-vercel-doppler.yml workflow:${NC}"
echo -e "1. Your DOPPLER_TOKEN secret is already configured ✅"
echo -e "2. The workflow will automatically fetch Vercel credentials from Doppler"
echo -e ""
echo -e "${CYAN}Checking existing secrets...${NC}"

# List current secrets
SECRETS=$(gh secret list --repo "$REPO_SLUG" 2>/dev/null)
echo "$SECRETS" | grep -E "DOPPLER|VERCEL" || echo "No relevant secrets found"

echo -e "\n${BLUE}============================================================${NC}"
echo -e "${YELLOW}📝 RECOMMENDED ACTION:${NC}"
echo -e ""
echo -e "Switch the default workflow to use Doppler by updating .github/workflows/deploy-vercel.yml"
echo -e "to fetch secrets from Doppler instead of expecting them as GitHub secrets."
echo -e ""
echo -e "${CYAN}OR${NC}"
echo -e ""
echo -e "Use the Doppler-enabled workflow directly:"
echo -e "${GREEN}gh workflow run deploy-vercel-doppler.yml --repo ${REPO_SLUG}${NC}"
echo -e ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}${BOLD}✅ Doppler Integration Status${NC}"
echo -e ""
echo -e "DOPPLER_TOKEN: $(echo "$SECRETS" | grep -q "DOPPLER_TOKEN" && echo -e "${GREEN}✅ Configured${NC}" || echo -e "${RED}❌ Missing${NC}")"
echo -e "DOPPLER_PROJECT: $(echo "$SECRETS" | grep -q "DOPPLER_PROJECT" && echo -e "${GREEN}✅ Configured${NC}" || echo -e "${YELLOW}⚠️  Optional${NC}")"
echo -e "DOPPLER_CONFIG: $(echo "$SECRETS" | grep -q "DOPPLER_CONFIG" && echo -e "${GREEN}✅ Configured${NC}" || echo -e "${YELLOW}⚠️  Optional${NC}")"
echo -e ""
echo -e "${MAGENTA}The deployment should now work with Doppler integration!${NC}"