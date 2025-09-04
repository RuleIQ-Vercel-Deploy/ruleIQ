#!/bin/bash

# Setup script for PostgreSQL test database
# This ensures LangGraph checkpointing tests work seamlessly

set -e

echo "🚀 Setting up PostgreSQL test environment for LangGraph checkpointing..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if docker compose is installed
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Function to wait for PostgreSQL to be ready
wait_for_postgres() {
    echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready...${NC}"
    for i in {1..30}; do
        if docker exec ruleiq-test-db pg_isready -U postgres > /dev/null 2>&1; then
            echo -e "${GREEN}✅ PostgreSQL is ready!${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
    done
    echo -e "${RED}❌ PostgreSQL failed to start${NC}"
    return 1
}

# Stop any existing test containers
echo "🧹 Cleaning up any existing test containers..."
docker compose -f docker-compose.test.yml down 2>/dev/null || true

# Start PostgreSQL test container
echo "🐘 Starting PostgreSQL test container..."
docker compose -f docker-compose.test.yml up -d postgres-test

# Wait for PostgreSQL to be ready
if wait_for_postgres; then
    echo -e "${GREEN}✅ PostgreSQL test database is ready!${NC}"
    
    # Create test database if it doesn't exist
    docker exec ruleiq-test-db psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'compliance_test'" | grep -q 1 || \
        docker exec ruleiq-test-db psql -U postgres -c "CREATE DATABASE compliance_test"
    
    # Show connection info
    echo ""
    echo "📋 Connection Information:"
    echo "------------------------"
    echo "Host: localhost"
    echo "Port: 5433"
    echo "Database: compliance_test"
    echo "Username: postgres"
    echo "Password: postgres"
    echo ""
    echo "🔗 Connection String:"
    echo "postgresql://postgres:postgres@localhost:5433/compliance_test"
    echo ""
    echo "🎯 Environment Variable (add to .env):"
    echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5433/compliance_test"
    echo ""
    
    # Export for current session
    export DATABASE_URL="postgresql://postgres:postgres@localhost:5433/compliance_test"
    echo -e "${GREEN}✅ DATABASE_URL exported for current session${NC}"
else
    echo -e "${RED}❌ Failed to start PostgreSQL${NC}"
    exit 1
fi