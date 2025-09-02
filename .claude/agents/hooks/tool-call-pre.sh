#!/bin/bash

# Tool Call Pre-Hook
# Purpose: Verify Serena before ANY tool is called by Claude Code

TOOL_NAME="$1"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Check if this is a Serena tool call
if [[ "$TOOL_NAME" == mcp__serena__* ]]; then
    # Verify Serena is running
    SERENA_PID=$(pgrep -f "serena.server" 2>/dev/null || true)
    
    if [ -z "$SERENA_PID" ]; then
        echo "[$TIMESTAMP] ❌ CRITICAL: Attempting to call Serena tool but server is NOT running!"
        echo "[$TIMESTAMP] 🔄 Emergency start of Serena MCP..."
        
        bash "$HOME/Documents/ruleIQ/.claude/serena-session-manager.sh" start
        sleep 3
        
        SERENA_PID=$(pgrep -f "serena.server" 2>/dev/null || true)
        if [ -n "$SERENA_PID" ]; then
            echo "[$TIMESTAMP] ✅ Serena MCP emergency start successful"
        else
            echo "[$TIMESTAMP] ❌ Failed to start Serena MCP - tool call will fail"
            exit 1
        fi
    fi
fi

# Log all tool calls for monitoring
echo "[$TIMESTAMP] Tool call: $TOOL_NAME" >> /tmp/claude-code-tools.log