#!/bin/bash

echo "🧹 Cleaning up MCP processes..."

# Kill all MCP-related processes
echo "Stopping all MCP servers..."
pkill -f "serena-mcp" 2>/dev/null
pkill -f "smithery" 2>/dev/null
pkill -f "sequa-mcp" 2>/dev/null
pkill -f "testsprite" 2>/dev/null
pkill -f "mcp-server" 2>/dev/null
pkill -f "context7-mcp" 2>/dev/null
pkill -f "playwright-mcp" 2>/dev/null
pkill -f "archon-ui" 2>/dev/null

# Wait for processes to terminate
sleep 3

# Force kill any remaining processes
pkill -9 -f "serena-mcp" 2>/dev/null
pkill -9 -f "smithery" 2>/dev/null
pkill -9 -f "mcp.*server" 2>/dev/null

# Clean up npm cache
echo "Cleaning npm cache..."
rm -rf /home/omar/.npm/_npx/* 2>/dev/null

echo "✅ Cleanup complete!"
echo ""
echo "Remaining MCP processes:"
pgrep -f "mcp|serena|archon|smithery" | wc -l