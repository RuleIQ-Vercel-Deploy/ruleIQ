#!/bin/bash

# Pre-Action Serena MCP Verification Hook
# Purpose: Ensure Serena is active before EVERY Claude Code action
# Version: 2.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Log file for tracking
LOG_FILE="/tmp/serena-hook.log"

# Function to check Serena status
check_serena_status() {
    local serena_pid=$(pgrep -f "serena.server" 2>/dev/null || true)
    local session_flag="$HOME/Documents/ruleIQ/.claude/serena-session.flag"
    local status_file="$HOME/Documents/ruleIQ/.claude/serena-status.json"
    
    if [ -n "$serena_pid" ] && [ -f "$session_flag" ]; then
        return 0
    else
        return 1
    fi
}

# Function to start Serena
start_serena() {
    echo -e "${YELLOW}Starting Serena MCP Server...${NC}"
    bash "$HOME/Documents/ruleIQ/.claude/serena-session-manager.sh" start
    sleep 2
}

# Function to verify Serena is responding
verify_serena_responsive() {
    # Check if the MCP server is actually responding
    if command -v serena &> /dev/null; then
        timeout 5 serena /list_memories &>/dev/null && return 0 || return 1
    fi
    return 1
}

# Main verification logic
echo "🔍 Pre-Action Hook: Verifying Serena MCP Status..."

if ! check_serena_status; then
    echo -e "${RED}❌ Serena MCP is NOT active!${NC}"
    start_serena
    
    # Wait for startup
    for i in {1..10}; do
        if check_serena_status; then
            echo -e "${GREEN}✅ Serena MCP successfully started${NC}"
            break
        fi
        sleep 1
    done
    
    if ! check_serena_status; then
        echo -e "${RED}⚠️  CRITICAL: Failed to start Serena MCP${NC}"
        echo "Please run manually: bash .claude/serena-session-manager.sh start"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Serena MCP is active${NC}"
fi

# Verify responsiveness
if verify_serena_responsive; then
    echo -e "${GREEN}✅ Serena MCP is responding${NC}"
else
    echo -e "${YELLOW}⚠️  Serena MCP may not be fully responsive${NC}"
fi

# Log the check
echo "$(date '+%Y-%m-%d %H:%M:%S') - Serena check completed" >> "$LOG_FILE"

# Update session timestamp
touch "$HOME/Documents/ruleIQ/.claude/serena-session.flag"

echo "✅ Pre-action verification complete"