#!/bin/bash

# User Prompt Submit Hook
# Purpose: Verify Serena before processing any user prompt

SERENA_PID=$(pgrep -f "serena.server" 2>/dev/null || true)
SESSION_FLAG="$HOME/Documents/ruleIQ/.claude/serena-session.flag"

if [ -n "$SERENA_PID" ] && [ -f "$SESSION_FLAG" ]; then
    echo "✅ Serena MCP Status: ACTIVE"
    echo "✅ Serena MCP: Already active"
else
    echo "⚠️  Serena MCP Status: INACTIVE"
    echo "🔄 Starting Serena MCP..."
    bash "$HOME/Documents/ruleIQ/.claude/serena-session-manager.sh" start
    sleep 2
    
    # Verify it started
    SERENA_PID=$(pgrep -f "serena.server" 2>/dev/null || true)
    if [ -n "$SERENA_PID" ]; then
        echo "✅ Serena MCP: Successfully started"
    else
        echo "❌ Serena MCP: Failed to start - manual intervention required"
        echo "Run: bash .claude/serena-session-manager.sh start"
    fi
fi