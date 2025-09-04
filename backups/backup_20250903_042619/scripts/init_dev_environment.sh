1#!/bin/bash 

# ruleIQ Development Environment Initialization Script
# This script sets up the development environment and starts necessary services

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}🚀 Initializing ruleIQ Development Environment${NC}"
echo -e "${BLUE}================================================${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a process is running
is_running() {
    pgrep -f "$1" > /dev/null 2>&1
}

# Step 1: Check prerequisites
echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "  ✅ Python: $PYTHON_VERSION"
else
    echo -e "  ${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo -e "  ✅ Node.js: $NODE_VERSION"
else
    echo -e "  ${RED}❌ Node.js not found${NC}"
    exit 1
fi

# Check pnpm
if command_exists pnpm; then
    PNPM_VERSION=$(pnpm --version)
    echo -e "  ✅ pnpm: $PNPM_VERSION"
else
    echo -e "  ${RED}❌ pnpm not found${NC}"
    exit 1
fi

# Check Docker
if command_exists docker; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | sed 's/,$//')
    echo -e "  ✅ Docker: $DOCKER_VERSION"
else
    echo -e "  ${RED}❌ Docker not found${NC}"
    exit 1
fi

# Step 2: Set up Python virtual environment
echo -e "\n${YELLOW}🐍 Setting up Python environment...${NC}"
cd "$PROJECT_ROOT"

if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

echo "  Activating virtual environment..."
source venv/bin/activate

echo "  Installing Python dependencies..."
pip install -r requirements.txt --quiet

# Step 3: Set up Frontend environment
echo -e "\n${YELLOW}📦 Setting up Frontend environment...${NC}"
cd "$PROJECT_ROOT/frontend"

if [ ! -d "node_modules" ]; then
    echo "  Installing frontend dependencies..."
    pnpm install
else
    echo "  Frontend dependencies already installed"
fi

# Step 4: Start Docker services
echo -e "\n${YELLOW}🐳 Starting Docker services...${NC}"
cd "$PROJECT_ROOT"

# Check if Docker daemon is running
if ! docker info > /dev/null 2>&1; then
    echo -e "  ${RED}❌ Docker daemon is not running. Please start Docker.${NC}"
    exit 1
fi

# Start database services
echo "  Starting PostgreSQL and Redis..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "  Waiting for services to be ready..."
sleep 5

# Check if services are running
if docker-compose ps | grep -q "postgres.*Up"; then
    echo -e "  ✅ PostgreSQL is running"
else
    echo -e "  ${RED}❌ PostgreSQL failed to start${NC}"
    exit 1
fi

if docker-compose ps | grep -q "redis.*Up"; then
    echo -e "  ✅ Redis is running"
else
    echo -e "  ${RED}❌ Redis failed to start${NC}"
    exit 1
fi

# Step 5: Run database migrations
echo -e "\n${YELLOW}🗄️  Running database migrations...${NC}"
cd "$PROJECT_ROOT"
alembic upgrade head
echo -e "  ✅ Database migrations complete"

# Step 6: Initialize Serena MCP Server
echo -e "\n${YELLOW}🤖 Starting Serena MCP Server...${NC}"

# Check if Serena is available at the expected location
SERENA_PATH="/home/omar/serena"
if [ -d "$SERENA_PATH" ] && [ -f "$SERENA_PATH/src/serena/mcp.py" ]; then
    # Use our custom Serena startup script
    if [ -f "$PROJECT_ROOT/scripts/start_serena_mcp.sh" ]; then
        echo "  Starting Serena MCP Server with ruleIQ configuration..."
        "$PROJECT_ROOT/scripts/start_serena_mcp.sh" start
    else
        echo -e "  ${YELLOW}⚠️  Serena startup script not found${NC}"
        echo "  Expected: $PROJECT_ROOT/scripts/start_serena_mcp.sh"
    fi
else
    echo -e "  ${YELLOW}⚠️  Serena MCP Server not found at $SERENA_PATH${NC}"
    echo "  Please install Serena MCP Server for enhanced development assistance"
    echo "  Repository: https://github.com/serena-ai/serena-mcp-server"
fi

# Step 7: Run context monitoring
echo -e "\n${YELLOW}📊 Running context change detection...${NC}"
python3 "$PROJECT_ROOT/scripts/context_monitor.py" > /dev/null 2>&1
echo -e "  ✅ Context monitoring complete"

# Step 8: Display status summary
echo -e "\n${GREEN}✨ Development Environment Ready!${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo "📍 Project Root: $PROJECT_ROOT"
echo "🐍 Python venv: Activated"
echo "📦 Frontend: Dependencies installed"
echo "🐳 Docker Services:"
echo "   - PostgreSQL: Running on port 5432"
echo "   - Redis: Running on port 6379"
if command_exists serena-mcp-server && is_running "serena-mcp-server"; then
    echo "🤖 Serena MCP: Running (ide-assistant context)"
fi
echo ""
echo -e "${BLUE}Available Commands:${NC}"
echo "  Backend:  cd $PROJECT_ROOT && python main.py"
echo "  Frontend: cd $PROJECT_ROOT/frontend && pnpm dev"
echo "  Tests:    cd $PROJECT_ROOT && pytest"
echo "  Monitor:  python3 scripts/context_monitor.py"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Start the backend: python main.py"
echo "2. Start the frontend: cd frontend && pnpm dev"
echo "3. View critical fixes: cat CRITICAL_FIXES_CHECKLIST.md"
echo ""

# Create a stop script for cleanup
cat > "$PROJECT_ROOT/scripts/stop_dev_environment.sh" << 'EOF'
#!/bin/bash

# Stop development environment services

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🛑 Stopping development environment..."

# Stop Serena MCP Server
if [ -f "$PROJECT_ROOT/scripts/stop_serena_mcp.sh" ]; then
    "$PROJECT_ROOT/scripts/stop_serena_mcp.sh" stop
else
    # Fallback to manual cleanup
    if [ -f "$PROJECT_ROOT/.serena_mcp.pid" ]; then
        PID=$(cat "$PROJECT_ROOT/.serena_mcp.pid")
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            echo "  ✅ Stopped Serena MCP Server"
        fi
        rm "$PROJECT_ROOT/.serena_mcp.pid"
    fi
fi

# Stop Docker services
cd "$PROJECT_ROOT"
docker-compose down
echo "  ✅ Stopped Docker services"

echo "✨ Development environment stopped"
EOF

chmod +x "$PROJECT_ROOT/scripts/stop_dev_environment.sh"

echo -e "${GREEN}💡 To stop all services: ./scripts/stop_dev_environment.sh${NC}"