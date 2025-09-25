#!/bin/bash

# Update Git Remote to Organization Repository
# This script updates the local repository to point to the new organization repository

set -e

echo "🔄 Updating Git Remote to Organization Repository"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ORG_REPO_URL="https://github.com/RuleIQ-Vercel-Deploy/ruleIQ.git"
ORG_NAME="RuleIQ-Vercel-Deploy"
REPO_NAME="ruleIQ"

echo -e "${BLUE}Current repository status:${NC}"
git remote -v
echo ""

# Check if we're in a git repository and get the root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo '')
if [ -z "$REPO_ROOT" ]; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Verify we're at the repository root
CURRENT_DIR=$(pwd)
if [ "$CURRENT_DIR" != "$REPO_ROOT" ]; then
    echo -e "${RED}Error: This script must be run from the repository root${NC}"
    echo "Current directory: $CURRENT_DIR"
    echo "Repository root: $REPO_ROOT"
    echo ""
    echo "Please run from the repository root:"
    echo -e "  ${BLUE}cd $REPO_ROOT && ./scripts/deploy/update-git-remote.sh${NC}"
    exit 1
fi

# Backup current remote
echo -e "${YELLOW}Backing up current remote configuration...${NC}"
CURRENT_ORIGIN=$(git remote get-url origin 2>/dev/null || echo "none")
echo "Current origin: $CURRENT_ORIGIN"

# Update remote to organization repository
echo -e "${BLUE}Updating remote to organization repository...${NC}"
if git remote get-url origin >/dev/null 2>&1; then
    git remote set-url origin $ORG_REPO_URL
    echo -e "${GREEN}✅ Updated existing origin remote${NC}"
else
    git remote add origin $ORG_REPO_URL
    echo -e "${GREEN}✅ Added new origin remote${NC}"
fi

# Verify the update
echo -e "${BLUE}Verifying remote update...${NC}"
NEW_ORIGIN=$(git remote get-url origin)
if [ "$NEW_ORIGIN" = "$ORG_REPO_URL" ]; then
    echo -e "${GREEN}✅ Remote successfully updated to: $NEW_ORIGIN${NC}"
else
    echo -e "${RED}❌ Remote update failed${NC}"
    echo "Expected: $ORG_REPO_URL"
    echo "Actual: $NEW_ORIGIN"
    exit 1
fi

# Fetch from new remote
echo -e "${BLUE}Fetching from organization repository...${NC}"
if git fetch origin; then
    echo -e "${GREEN}✅ Successfully fetched from organization repository${NC}"
else
    echo -e "${YELLOW}⚠️  Fetch failed - this is normal if repository is empty${NC}"
fi

# Check current branch and suggest next steps
CURRENT_BRANCH=$(git branch --show-current)
echo ""
echo -e "${BLUE}Current branch: ${YELLOW}$CURRENT_BRANCH${NC}"
echo ""
echo -e "${GREEN}🎉 Git remote successfully updated to organization repository!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Push your current code to the organization repository:"
echo -e "   ${BLUE}git push -u origin $CURRENT_BRANCH${NC}"
echo ""
echo "2. Update GitHub Actions secrets in the organization repository:"
echo -e "   ${BLUE}https://github.com/$ORG_NAME/$REPO_NAME/settings/secrets/actions${NC}"
echo ""
echo "3. Configure Vercel project with organization:"
echo -e "   ${BLUE}vercel link${NC}"
echo ""
echo "4. Deploy to production:"
echo -e "   ${BLUE}git push origin main${NC} (triggers automatic deployment)"
echo ""
echo -e "${GREEN}Organization repository: $ORG_REPO_URL${NC}"

# Display current remotes
echo ""
echo -e "${BLUE}Updated remote configuration:${NC}"
git remote -v