#!/bin/bash
# Quick session starter for Serena
# Runs the session manager in background with proper detachment

PROJECT_PATH="/home/omar/Documents/ruleIQ"
CLAUDE_DIR="$PROJECT_PATH/.claude"
LOG_FILE="$CLAUDE_DIR/serena-session.log"

# Check if already running
if pgrep -f "serena-session-manager.sh" > /dev/null; then
    echo "✅ Serena session manager already running"
    exit 0
fi

# Start session manager in background
echo "🚀 Starting Serena session manager..."
nohup bash "$CLAUDE_DIR/serena-session-manager.sh" start > "$LOG_FILE" 2>&1 &
MANAGER_PID=$!

# Give it a moment to start
sleep 2

# Check if it started successfully
if kill -0 $MANAGER_PID 2>/dev/null; then
    echo "✅ Serena session manager started (PID: $MANAGER_PID)"
    echo "📝 Logs: tail -f $LOG_FILE"
else
    echo "❌ Failed to start session manager"
    exit 1
fi