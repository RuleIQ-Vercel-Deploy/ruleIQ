#!/bin/bash

# 🔐 RuleIQ Doppler Secrets Setup Script
# Run this after: doppler login && doppler setup --project ruleiq

echo "🔐 RuleIQ Doppler Secrets Setup"
echo "=================================="

# Check if logged in
if ! doppler whoami &>/dev/null; then
    echo "❌ Not logged in to Doppler. Please run:"
    echo "   doppler login"
    exit 1
fi

echo "✅ Logged in as: $(doppler whoami)"

# Check if project is setup
if ! doppler configure get project &>/dev/null; then
    echo "❌ Doppler not configured in this directory. Please run:"
    echo "   doppler setup --project ruleiq --config dev"
    exit 1
fi

echo "✅ Using project: $(doppler configure get project)"
echo "✅ Using config: $(doppler configure get config)"
echo ""

# Generate secure keys
echo "🔑 Generating secure keys..."

# Generate JWT secret (32 bytes base64)
JWT_SECRET=$(openssl rand -base64 32)

# Generate secret key (64 chars)
SECRET_KEY=$(openssl rand -hex 32)

# Generate encryption key (32 chars)
ENCRYPTION_KEY=$(openssl rand -base64 32 | head -c 32)

# Generate Fernet key
FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

echo "✅ Secure keys generated"
echo ""

# Set development secrets
echo "🔐 Setting development secrets..."

# Application settings
doppler secrets set ENVIRONMENT="development" --silent
doppler secrets set DEBUG="true" --silent
doppler secrets set APP_NAME="RuleIQ" --silent
doppler secrets set APP_VERSION="1.0.0" --silent
doppler secrets set APP_URL="http://localhost:3000" --silent
doppler secrets set API_VERSION="v1" --silent

# Database (placeholder - update with real values)
doppler secrets set DATABASE_URL="postgresql+asyncpg://username:password@your-neon-host/database?sslmode=require" --silent
doppler secrets set TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/ruleiq_test" --silent
doppler secrets set DB_POOL_SIZE="10" --silent
doppler secrets set DB_MAX_OVERFLOW="20" --silent
doppler secrets set DB_POOL_TIMEOUT="30" --silent
doppler secrets set DB_POOL_RECYCLE="1800" --silent

# Redis (placeholder - update with real values)
doppler secrets set REDIS_URL="redis://localhost:6379/0" --silent
doppler secrets set REDIS_HOST="localhost" --silent
doppler secrets set REDIS_PORT="6379" --silent
doppler secrets set REDIS_DB="0" --silent

# JWT & Security (auto-generated secure values)
doppler secrets set JWT_SECRET_KEY="$JWT_SECRET" --silent
doppler secrets set JWT_ALGORITHM="HS256" --silent
doppler secrets set JWT_ACCESS_TOKEN_EXPIRE_MINUTES="30" --silent
doppler secrets set JWT_REFRESH_TOKEN_EXPIRE_DAYS="7" --silent
doppler secrets set SECRET_KEY="$SECRET_KEY" --silent
doppler secrets set ENCRYPTION_KEY="$ENCRYPTION_KEY" --silent
doppler secrets set FERNET_KEY="$FERNET_KEY" --silent

# API Configuration
doppler secrets set NEXT_PUBLIC_API_URL="http://localhost:8000" --silent
doppler secrets set API_HOST="0.0.0.0" --silent
doppler secrets set API_PORT="8000" --silent
doppler secrets set API_WORKERS="2" --silent

# AI Services (placeholder - add your real keys)
doppler secrets set OPENAI_API_KEY="your_openai_api_key_here" --silent
doppler secrets set GOOGLE_AI_API_KEY="your_google_ai_api_key_here" --silent

# Feature flags
doppler secrets set ENABLE_AI_FEATURES="true" --silent
doppler secrets set ENABLE_OAUTH="true" --silent
doppler secrets set ENABLE_EMAIL_NOTIFICATIONS="true" --silent
doppler secrets set ENABLE_FILE_UPLOAD="true" --silent

# CORS and security
doppler secrets set CORS_ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000" --silent
doppler secrets set ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000" --silent

echo "✅ Development secrets configured!"
echo ""

# Show what was set
echo "📋 Configured secrets:"
doppler secrets --only-names

echo ""
echo "🎉 Doppler setup complete!"
echo ""
echo "⚠️  IMPORTANT NEXT STEPS:"
echo "1. Update DATABASE_URL with your real Neon PostgreSQL connection string"
echo "2. Update REDIS_URL with your real Redis connection string (if using external Redis)"
echo "3. Add your real API keys for OpenAI, Google AI, etc."
echo "4. For production, create a 'prd' config: doppler configs create prd"
echo ""
echo "🔧 To update secrets:"
echo "   doppler secrets set DATABASE_URL='your-real-database-url'"
echo "   doppler secrets set OPENAI_API_KEY='your-real-openai-key'"
echo ""
echo "🚀 To run your app with Doppler:"
echo "   doppler run -- python main.py"
echo "   doppler run -- npm run dev (for frontend)"
echo ""
echo "🔍 To test the SecretsVault:"
echo "   doppler run -- python config/secrets_vault.py health"