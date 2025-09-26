#!/bin/bash

# Continuous Serena Monitor
# Purpose: Background process that ensures Serena stays active

LOG_DIR="/tmp/serena-hooks"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/monitor.log"
PID_FILE="/tmp/serena-monitor.pid"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "Monitor already running with PID $OLD_PID"
        exit 0
    fi
fi

# Save current PID
echo $$ > "$PID_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting continuous Serena monitor" >> "$LOG_FILE"

# Monitoring loop
while true; do
    SERENA_PID=$(pgrep -f "serena.server" 2>/dev/null || true)
    SESSION_FLAG="$HOME/Documents/ruleIQ/.claude/serena-session.flag"
    
    if [ -z "$SERENA_PID" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  Serena not running, attempting restart..." >> "$LOG_FILE"
        bash "$HOME/Documents/ruleIQ/.claude/serena-session-manager.sh" start
        
        sleep 3
        SERENA_PID=$(pgrep -f "serena.server" 2>/dev/null || true)
        
        if [ -n "$SERENA_PID" ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Serena restarted successfully (PID: $SERENA_PID)" >> "$LOG_FILE"
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Failed to restart Serena" >> "$LOG_FILE"
        fi
    fi
    
    # Update session flag to keep it alive
    if [ -f "$SESSION_FLAG" ]; then
        touch "$SESSION_FLAG"
    fi
    
    # Sleep for monitoring interval
    sleep 30
done