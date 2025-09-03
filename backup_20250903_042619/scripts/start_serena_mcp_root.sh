#!/bin/bash

# Start Serena MCP Server for ruleIQ project
echo "🤖 Starting Serena MCP Server for ruleIQ..."

# Project paths
PROJECT_DIR="/home/omar/Documents/ruleIQ"
SERENA_DIR="/home/omar/serena"

# Check if Serena exists
if [ ! -d "$SERENA_DIR" ]; then
    echo "❌ Serena directory not found at $SERENA_DIR"
    exit 1
fi

# Navigate to Serena directory and start the server
cd "$SERENA_DIR"

# Try different approaches to start Serena
echo "Attempting to start Serena MCP server..."

# Method 1: Using uv run (preferred)
if command -v uv >/dev/null 2>&1; then
    echo "  Using uv run..."
    uv run serena-mcp-server --context ide-assistant --project "$PROJECT_DIR"
elif [ -f "$SERENA_DIR/.venv/bin/python" ]; then
    # Method 2: Using virtual environment
    echo "  Using Serena virtual environment..."
    source "$SERENA_DIR/.venv/bin/activate"
    python -m serena.mcp --context ide-assistant --project "$PROJECT_DIR"
else
    # Method 3: Direct Python execution
    echo "  Using direct Python execution..."
    PYTHONPATH="$SERENA_DIR" python "$SERENA_DIR/scripts/mcp_server.py" --context ide-assistant --project "$PROJECT_DIR"
fi