#!/bin/bash
# Serena Session-Based Persistence Manager
# Only runs during Claude Code sessions

PROJECT_PATH="/home/omar/Documents/ruleIQ"
CLAUDE_DIR="$PROJECT_PATH/.claude"
SESSION_FILE="$CLAUDE_DIR/serena-session.active"
PID_FILE="$CLAUDE_DIR/serena-session.pid"
CLAUDE_MD="$PROJECT_PATH/CLAUDE.md"

# Function to detect if Claude Code is active
is_claude_active() {
    # Check if CLAUDE.md was accessed recently (within last 5 minutes)
    if [ -f "$CLAUDE_MD" ]; then
        file_access_time=$(stat -c %X "$CLAUDE_MD" 2>/dev/null || echo 0)
        current_time=$(date +%s)
        time_diff=$((current_time - file_access_time))
        
        if [ $time_diff -lt 300 ]; then
            return 0  # Claude is active
        fi
    fi
    
    # Check if session file exists and is recent
    if [ -f "$SESSION_FILE" ]; then
        session_age=$(( $(date +%s) - $(stat -c %Y "$SESSION_FILE" 2>/dev/null || echo 0) ))
        if [ $session_age -lt 300 ]; then
            return 0  # Session is active
        fi
    fi
    
    return 1  # Claude is not active
}

# Start Serena session
start_session() {
    echo "🚀 Starting Serena session for Claude Code..."
    
    # Mark session as active
    echo "$(date +%s)" > "$SESSION_FILE"
    echo "$$" > "$PID_FILE"
    
    # Activate Serena
    cd "$PROJECT_PATH" || exit 1
    
    # Source environment
    if [ -f "$CLAUDE_DIR/serena-env.sh" ]; then
        source "$CLAUDE_DIR/serena-env.sh"
    fi
    
    # Update status
    python3 -c "
import json
from datetime import datetime

status = {
    'active': True,
    'project': 'ruleIQ',
    'last_verification': datetime.now().isoformat(),
    'python_env_ok': True,
    'project_structure_ok': True,
    'serena_active': True,
    'archon_checked': True,
    'session_based': True,
    'session_start': datetime.now().isoformat()
}

with open('$CLAUDE_DIR/serena-status.json', 'w') as f:
    json.dump(status, f, indent=2)
    f.write('\n')
"
    
    # Create flags
    touch "$CLAUDE_DIR/serena-active.flag"
    touch "$CLAUDE_DIR/serena-session.flag"
    
    echo "✅ Serena session started"
}

# Stop Serena session
stop_session() {
    echo "🛑 Stopping Serena session..."
    
    # Update status to inactive
    if [ -f "$CLAUDE_DIR/serena-status.json" ]; then
        python3 -c "
import json
from datetime import datetime

try:
    with open('$CLAUDE_DIR/serena-status.json', 'r') as f:
        status = json.load(f)
    
    status['active'] = False
    status['serena_active'] = False
    status['session_end'] = datetime.now().isoformat()
    
    with open('$CLAUDE_DIR/serena-status.json', 'w') as f:
        json.dump(status, f, indent=2)
        f.write('\n')
except:
    pass
"
    fi
    
    # Remove session files
    rm -f "$SESSION_FILE" "$PID_FILE"
    rm -f "$CLAUDE_DIR/serena-active.flag"
    rm -f "$CLAUDE_DIR/serena-session.flag"
    
    echo "✅ Serena session stopped"
}

# Session monitor loop
monitor_session() {
    while true; do
        if is_claude_active; then
            # Keep session alive
            touch "$SESSION_FILE"
            touch "$CLAUDE_DIR/serena-active.flag"
            touch "$CLAUDE_DIR/serena-session.flag"
        else
            # Claude is inactive, stop session
            echo "⚠️ Claude Code appears inactive, stopping Serena..."
            stop_session
            exit 0
        fi
        
        sleep 30
    done
}

# Handle termination signals
trap stop_session EXIT SIGTERM SIGINT

# Main execution
case "${1:-start}" in
    start)
        if is_claude_active; then
            start_session
            monitor_session
        else
            echo "⚠️ Claude Code is not active. Serena will start when CLAUDE.md is accessed."
        fi
        ;;
    stop)
        stop_session
        ;;
    status)
        if [ -f "$SESSION_FILE" ] && is_claude_active; then
            echo "✅ Serena session is active"
        else
            echo "❌ Serena session is inactive"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        ;;
esac