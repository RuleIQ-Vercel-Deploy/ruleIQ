#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting SonarCloud Analysis for ruleIQ...${NC}"
echo -e "${YELLOW}Project Key: ruliq-compliance-platform${NC}"
echo -e "${YELLOW}Organization: omara1-bakri${NC}"
echo ""

# Run analysis
echo -e "${YELLOW}⏳ This will take a few minutes to analyze the entire codebase...${NC}"
npx sonarqube-scanner \
  -Dsonar.token=78c39861ad8fa298fc7b3184cfe6573012b9af49

echo ""
echo -e "${GREEN}✅ Analysis complete!${NC}"
echo -e "${GREEN}📊 View results at: https://sonarcloud.io/project/overview?id=ruliq-compliance-platform${NC}"
echo ""
echo -e "${YELLOW}Dashboard: https://sonarcloud.io/organizations/omara1-bakri/projects${NC}"