#!/bin/bash

# Neon Database Setup Script for ruleIQ
# This script helps you configure ruleIQ to use Neon as the primary database

set -e  # Exit on error

echo "=================================="
echo "ruleIQ Neon Database Setup"
echo "=================================="
echo ""

# Check if .env exists and back it up
if [ -f .env ]; then
    echo "📁 Backing up existing .env to .env.backup.$(date +%Y%m%d_%H%M%S)"
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -d "database" ]; then
    echo "❌ Error: This script must be run from the ruleIQ project root directory"
    exit 1
fi

echo "📋 Prerequisites:"
echo "1. A Neon account (sign up at https://console.neon.tech)"
echo "2. A Neon project with a database"
echo "3. Your Neon connection string"
echo ""
echo "Press Enter to continue..."
read

# Function to validate PostgreSQL connection string
validate_connection_string() {
    if [[ $1 =~ ^postgresql://.*@.*\.neon\.tech/.*\?sslmode=require$ ]]; then
        return 0
    else
        return 1
    fi
}

# Get Neon connection string
echo ""
echo "🔗 Enter your Neon DATABASE_URL:"
echo "   (It should look like: postgresql://user:password@host.neon.tech/database?sslmode=require)"
echo ""
read -p "DATABASE_URL: " DATABASE_URL

# Validate the connection string
if ! validate_connection_string "$DATABASE_URL"; then
    echo "❌ Invalid Neon connection string. Make sure it:"
    echo "   - Starts with postgresql://"
    echo "   - Contains .neon.tech"
    echo "   - Ends with ?sslmode=require"
    exit 1
fi

# Get other required variables
echo ""
echo "🔑 Enter your Google API Key (for AI services):"
read -p "GOOGLE_API_KEY: " GOOGLE_API_KEY

# Generate JWT secret if needed
echo ""
echo "🔐 Generating JWT secret key..."
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
echo "   Generated: ${JWT_SECRET_KEY:0:10}..."

# Create .env file
echo ""
echo "📝 Creating .env file..."
cat > .env << EOF
# Neon Database Configuration
DATABASE_URL=$DATABASE_URL

# Redis Configuration (local)
REDIS_URL=redis://localhost:6379/0

# AI Service Configuration
GOOGLE_API_KEY=$GOOGLE_API_KEY

# Security
JWT_SECRET_KEY=$JWT_SECRET_KEY

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Environment
ENV=development

# Application Settings
APP_NAME=ruleIQ
APP_VERSION=1.0.0
APP_HOST=0.0.0.0
APP_PORT=8000

# Database Pool Settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800

# AI Settings
AI_MODEL=gemini-1.5-flash
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=4000
AI_CACHE_TTL=3600

# Rate Limiting
RATE_LIMIT_GENERAL=100/minute
RATE_LIMIT_AI=20/minute
RATE_LIMIT_AUTH=5/minute

# Logging
LOG_LEVEL=INFO
EOF

echo "✅ Created .env file"

# Update docker-compose.yml to use the Neon version
echo ""
echo "🐳 Updating Docker configuration..."
if [ -f docker-compose.yml ] && [ -f docker-compose.neon.yml ]; then
    mv docker-compose.yml docker-compose.local.yml
    cp docker-compose.neon.yml docker-compose.yml
    echo "✅ Updated docker-compose.yml to use Neon configuration"
fi

# Create a simple test script
echo ""
echo "🧪 Creating database test script..."
cat > test-neon-connection.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse

load_dotenv()

def test_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in .env")
        return False
    
    try:
        # Parse the URL to show connection info (without password)
        parsed = urlparse(db_url)
        print(f"🔗 Connecting to Neon database:")
        print(f"   Host: {parsed.hostname}")
        print(f"   Database: {parsed.path[1:]}")
        print(f"   User: {parsed.username}")
        print(f"   SSL: Required")
        
        # Test connection
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"\n✅ Successfully connected to Neon!")
        print(f"   PostgreSQL version: {version}")
        
        # Check if tables exist
        cur.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cur.fetchone()[0]
        print(f"   Tables in database: {table_count}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
EOF
chmod +x test-neon-connection.py

# Test the connection
echo ""
echo "🧪 Testing Neon connection..."
python test-neon-connection.py

echo ""
echo "=================================="
echo "🎉 Neon setup complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Start services: docker compose up -d"
echo "2. Initialize database: python database/init_db.py"
echo "3. Run the app: python main.py"
echo ""
echo "📚 See NEON_DATABASE_SETUP.md for more details"