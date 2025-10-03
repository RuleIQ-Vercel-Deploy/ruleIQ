#!/bin/bash

# Session Start Hook
# Purpose: Automatically start Serena when Claude Code session begins

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 Claude Code Session Starting..."

# Start Serena MCP Server
bash "$HOME/Documents/ruleIQ/.claude/serena-session-manager.sh" start

# Verify it started
sleep 2
SERENA_PID=$(pgrep -f "serena.server" 2>/dev/null || true)

if [ -n "$SERENA_PID" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Serena MCP initialized successfully"
    
    # Create initial verification status
    cat > "$HOME/Documents/ruleIQ/.claude/serena-verification.json" <<EOF
{
  "status": "active",
  "pid": "$SERENA_PID",
  "started_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "last_check": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "verification_enabled": true
}
EOF
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  Warning: Serena MCP failed to start"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  Manual start required: bash .claude/serena-session-manager.sh start"
fi