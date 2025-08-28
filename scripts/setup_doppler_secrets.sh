#!/bin/bash

# Doppler Secrets Setup Script for ruleIQ
# =========================================
# This script helps configure Doppler secrets for the project
# Run this after installing Doppler CLI: https://docs.doppler.com/docs/install-cli

set -e

echo "🔐 Doppler Secrets Setup for ruleIQ"
echo "===================================="
echo ""

# Check if Doppler CLI is installed
if ! command -v doppler &> /dev/null; then
    echo "❌ Doppler CLI not found. Please install it first:"
    echo "   brew install dopplerhq/cli/doppler (macOS)"
    echo "   or visit: https://docs.doppler.com/docs/install-cli"
    exit 1
fi

echo "✅ Doppler CLI found"
echo ""

# Login to Doppler if needed
if ! doppler configure get token &> /dev/null; then
    echo "📝 Please login to Doppler:"
    doppler login
fi

# Setup project
echo "🔧 Setting up Doppler project..."
doppler setup --project ruleiq --config dev

echo ""
echo "📝 Adding Abacus AI Secrets to Doppler"
echo "======================================="
echo ""
echo "⚠️  CRITICAL: The following secrets need to be added to Doppler immediately:"
echo ""
echo "1. ABACUS_AI_API_KEY"
echo "2. ABACUS_AI_DEPLOYMENT_ID"
echo "3. ABACUS_AI_DEPLOYMENT_TOKEN"
echo ""
echo "These credentials were previously hardcoded and have been exposed."
echo "Please rotate them immediately and add new ones to Doppler."
echo ""

# Prompt to add secrets
read -p "Would you like to add these secrets now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Please enter the new Abacus AI credentials:"
    echo "(Note: These should be NEW credentials after rotating the exposed ones)"
    echo ""
    
    read -s -p "Enter ABACUS_AI_API_KEY: " api_key
    echo ""
    read -p "Enter ABACUS_AI_DEPLOYMENT_ID: " deployment_id
    echo ""
    read -s -p "Enter ABACUS_AI_DEPLOYMENT_TOKEN: " deployment_token
    echo ""
    
    # Add secrets to Doppler
    echo "$api_key" | doppler secrets set ABACUS_AI_API_KEY --plain
    echo "$deployment_id" | doppler secrets set ABACUS_AI_DEPLOYMENT_ID --plain
    echo "$deployment_token" | doppler secrets set ABACUS_AI_DEPLOYMENT_TOKEN --plain
    
    echo ""
    echo "✅ Secrets added to Doppler successfully!"
else
    echo ""
    echo "⚠️  Please add the secrets manually using:"
    echo "   doppler secrets set ABACUS_AI_API_KEY"
    echo "   doppler secrets set ABACUS_AI_DEPLOYMENT_ID" 
    echo "   doppler secrets set ABACUS_AI_DEPLOYMENT_TOKEN"
fi

echo ""
echo "📋 Other Important Secrets to Migrate"
echo "======================================"
echo ""
echo "Please ensure these other secrets are also in Doppler:"
echo ""
echo "Database & Infrastructure:"
echo "  - DATABASE_URL"
echo "  - REDIS_URL"
echo ""
echo "Authentication:"
echo "  - JWT_SECRET"
echo "  - GOOGLE_CLIENT_ID"
echo "  - GOOGLE_CLIENT_SECRET"
echo ""
echo "AI Services:"
echo "  - GOOGLE_AI_API_KEY"
echo "  - OPENAI_API_KEY (if used)"
echo ""
echo "Monitoring:"
echo "  - SENTRY_DSN"
echo ""
echo "Neo4j (if used):"
echo "  - NEO4J_URI"
echo "  - NEO4J_PASSWORD"
echo ""

# Test the configuration
echo "🧪 Testing Doppler configuration..."
echo ""
if doppler secrets get ABACUS_AI_API_KEY --plain &> /dev/null; then
    echo "✅ Doppler secrets are accessible!"
    echo ""
    echo "To run the application with Doppler secrets:"
    echo "  doppler run -- python main.py"
    echo "  doppler run -- npm run dev"
    echo ""
else
    echo "⚠️  Doppler secrets not yet configured. Please add them as shown above."
fi

echo ""
echo "📚 Next Steps:"
echo "============="
echo "1. Rotate the exposed Abacus AI credentials immediately"
echo "2. Add all secrets to Doppler using the commands above"
echo "3. Update your .env.local file to include: DOPPLER_TOKEN=<your-service-token>"
echo "4. Test the application with: doppler run -- python main.py"
echo ""
echo "For more information: https://docs.doppler.com/docs"