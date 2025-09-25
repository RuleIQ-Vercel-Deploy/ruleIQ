#!/bin/bash

# RuleIQ Deployment Script
# This script deploys the application to Vercel

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 RuleIQ Deployment Script${NC}"
echo "================================"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}❌ Vercel CLI is not installed${NC}"
    echo "Install with: npm install -g vercel"
    exit 1
fi

# Check environment
ENVIRONMENT=${1:-production}
echo -e "${YELLOW}📦 Deploying to: ${ENVIRONMENT}${NC}"

# Pull Vercel environment information
echo -e "${GREEN}📥 Pulling Vercel environment...${NC}"
vercel pull --yes --environment="${ENVIRONMENT}"

# Build project artifacts
echo -e "${GREEN}🔨 Building project...${NC}"
vercel build --prod

# Deploy to Vercel
echo -e "${GREEN}🚀 Deploying to Vercel...${NC}"
if [ "$ENVIRONMENT" = "production" ]; then
    DEPLOYMENT_URL=$(vercel deploy --prebuilt --prod)
else
    DEPLOYMENT_URL=$(vercel deploy --prebuilt)
fi

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "URL: ${DEPLOYMENT_URL}"

# Verify deployment
echo -e "${YELLOW}🔍 Verifying deployment...${NC}"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$DEPLOYMENT_URL")
if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Deployment verified successfully!${NC}"
else
    echo -e "${RED}⚠️ Deployment verification failed (HTTP $HTTP_STATUS)${NC}"
    exit 1
fi