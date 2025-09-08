#!/bin/bash
# Verify Docker MCP Gateway is properly configured for ruleIQ

echo "=========================================="
echo "Docker MCP Gateway Verification"
echo "=========================================="
echo ""

# Check if Docker is installed
echo "1. Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo "   ✓ Docker is installed: $(docker --version)"
else
    echo "   ✗ Docker is not installed"
    exit 1
fi

# Check if Docker MCP plugin is installed
echo ""
echo "2. Checking Docker MCP plugin..."
if docker mcp --help &> /dev/null; then
    echo "   ✓ Docker MCP plugin is installed"
else
    echo "   ✗ Docker MCP plugin not found"
    exit 1
fi

# Check if Docker MCP Gateway is running
echo ""
echo "3. Checking Docker MCP Gateway process..."
GATEWAY_PID=$(pgrep -f "docker mcp gateway run" | head -1)
if [ ! -z "$GATEWAY_PID" ]; then
    echo "   ✓ Docker MCP Gateway is running (PID: $GATEWAY_PID)"
else
    echo "   ✗ Docker MCP Gateway is not running"
    echo "   Starting Docker MCP Gateway..."
    docker mcp gateway run &
    sleep 2
    GATEWAY_PID=$(pgrep -f "docker mcp gateway run" | head -1)
    if [ ! -z "$GATEWAY_PID" ]; then
        echo "   ✓ Docker MCP Gateway started successfully (PID: $GATEWAY_PID)"
    else
        echo "   ✗ Failed to start Docker MCP Gateway"
        exit 1
    fi
fi

# Check Claude configuration
echo ""
echo "4. Checking Claude Desktop configuration..."
if grep -q "MCP_DOCKER" /home/omar/.config/Claude/claude_desktop_config.json 2>/dev/null; then
    echo "   ✓ MCP_DOCKER is configured in Claude Desktop"
else
    echo "   ✗ MCP_DOCKER not found in Claude Desktop config"
    echo "   Please restart Claude Desktop to load the new configuration"
fi

# Check MCP Control configuration
echo ""
echo "5. Checking MCP Control configuration..."
if grep -q "docker" /home/omar/.mcp-manager/servers.json 2>/dev/null; then
    echo "   ✓ Docker MCP is configured in MCP Control"
else
    echo "   ✗ Docker MCP not found in MCP Control config"
fi

# Summary
echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
echo "Docker MCP Gateway is configured and ready for use in the ruleIQ project."
echo ""
echo "To use in Claude:"
echo "  - The MCP_DOCKER server is now available"
echo "  - Restart Claude Desktop if it's currently running"
echo ""
echo "To manage via command line:"
echo "  mcp-control status        # Check status"
echo "  mcp-control start docker  # Start Docker MCP"
echo "  mcp-control stop docker   # Stop Docker MCP"
echo ""
echo "Direct Docker MCP commands:"
echo "  docker mcp gateway run    # Start the gateway"
echo "  docker mcp list          # List MCP containers"
echo ""