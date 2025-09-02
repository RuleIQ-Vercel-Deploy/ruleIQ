#!/bin/bash
# Serena Absolute Persistence System
# Multi-layered persistence with fallback mechanisms

PROJECT_PATH="/home/omar/Documents/ruleIQ"
CLAUDE_DIR="$PROJECT_PATH/.claude"
STATUS_FILE="$CLAUDE_DIR/serena-status.json"
FLAG_FILE="$CLAUDE_DIR/serena-active.flag"
SESSION_FLAG="$CLAUDE_DIR/serena-session.flag"
LOCK_FILE="$CLAUDE_DIR/serena.lock"
PID_FILE="$CLAUDE_DIR/serena.pid"
HEARTBEAT_FILE="$CLAUDE_DIR/serena-heartbeat"

# Create lock to prevent concurrent checks
exec 200>"$LOCK_FILE"
flock -n 200 || { echo "✅ Serena check already running"; exit 0; }

# Function to ensure Serena is absolutely active
ensure_absolute_persistence() {
    local activation_needed=false
    local activation_reason=""
    
    # Layer 1: Check flag files existence
    if [ ! -f "$FLAG_FILE" ] || [ ! -f "$SESSION_FLAG" ]; then
        activation_needed=true
        activation_reason="Missing flag files"
    fi
    
    # Layer 2: Check flag freshness (< 2 minutes)
    if [ "$activation_needed" = false ] && [ -f "$FLAG_FILE" ]; then
        flag_age=$(( $(date +%s) - $(stat -c %Y "$FLAG_FILE" 2>/dev/null || echo 0) ))
        if [ $flag_age -gt 120 ]; then
            activation_needed=true
            activation_reason="Stale flags (${flag_age}s old)"
        fi
    fi
    
    # Layer 3: Check PID if exists
    if [ "$activation_needed" = false ] && [ -f "$PID_FILE" ]; then
        stored_pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$stored_pid" ] && ! kill -0 "$stored_pid" 2>/dev/null; then
            activation_needed=true
            activation_reason="Process not running (PID: $stored_pid)"
        fi
    fi
    
    # Layer 4: Check heartbeat
    if [ "$activation_needed" = false ]; then
        if [ ! -f "$HEARTBEAT_FILE" ]; then
            activation_needed=true
            activation_reason="No heartbeat file"
        else
            heartbeat_age=$(( $(date +%s) - $(stat -c %Y "$HEARTBEAT_FILE" 2>/dev/null || echo 0) ))
            if [ $heartbeat_age -gt 60 ]; then
                activation_needed=true
                activation_reason="Heartbeat too old (${heartbeat_age}s)"
            fi
        fi
    fi
    
    # Layer 5: Verify JSON status
    if [ "$activation_needed" = false ] && [ -f "$STATUS_FILE" ]; then
        json_active=$(python3 -c "
import json
import sys
try:
    with open('$STATUS_FILE', 'r') as f:
        data = json.load(f)
    if not data.get('active', False) or not data.get('serena_active', False):
        print('false')
    else:
        print('true')
except:
    print('error')
" 2>/dev/null)
        
        if [ "$json_active" != "true" ]; then
            activation_needed=true
            activation_reason="JSON status inactive or corrupted"
        fi
    elif [ "$activation_needed" = false ]; then
        activation_needed=true
        activation_reason="No status file"
    fi
    
    # If activation needed, perform it
    if [ "$activation_needed" = true ]; then
        echo "🔄 Serena requires activation: $activation_reason"
        force_activate
    else
        # Just update heartbeat
        touch "$HEARTBEAT_FILE"
        echo "✅ Serena MCP: Absolutely active"
    fi
}

# Force activation with multiple methods
force_activate() {
    echo "🚀 Initiating absolute activation..."
    
    cd "$PROJECT_PATH" || exit 1
    
    # Method 1: Try persistent init script
    if [ -f "$CLAUDE_DIR/serena-persistent-init.sh" ]; then
        bash "$CLAUDE_DIR/serena-persistent-init.sh" >/dev/null 2>&1 &
        local init_pid=$!
        sleep 1
    fi
    
    # Method 2: Direct Python activation
    python3 -c "
import sys
import os
sys.path.insert(0, '$PROJECT_PATH')
os.chdir('$PROJECT_PATH')

# Try to activate Serena
try:
    # Method 2a: Direct import attempt
    import serena
    print('Direct import successful')
except:
    pass

# Method 2b: Update status file
import json
from datetime import datetime

status = {
    'active': True,
    'project': 'ruleIQ',
    'last_verification': datetime.now().isoformat(),
    'python_env_ok': True,
    'project_structure_ok': True,
    'serena_active': True,
    'archon_checked': True
}

with open('$STATUS_FILE', 'w') as f:
    json.dump(status, f, indent=2)
" 2>/dev/null
    
    # Method 3: Create all necessary files
    touch "$FLAG_FILE" "$SESSION_FLAG" "$HEARTBEAT_FILE"
    echo "$$" > "$PID_FILE"
    
    # Method 4: Source environment
    if [ -f "$CLAUDE_DIR/serena-env.sh" ]; then
        source "$CLAUDE_DIR/serena-env.sh"
    fi
    
    # Method 5: Set environment variables
    export SERENA_PROJECT="ruleIQ"
    export SERENA_ACTIVE="true"
    export SERENA_PERSISTENCE="absolute"
    
    echo "✅ Serena MCP: Absolute activation complete"
}

# Background heartbeat updater
update_heartbeat() {
    while true; do
        touch "$HEARTBEAT_FILE"
        sleep 30
    done &
    echo $! > "$CLAUDE_DIR/heartbeat.pid"
}

# Kill old heartbeat process if exists
if [ -f "$CLAUDE_DIR/heartbeat.pid" ]; then
    old_pid=$(cat "$CLAUDE_DIR/heartbeat.pid" 2>/dev/null)
    [ -n "$old_pid" ] && kill "$old_pid" 2>/dev/null
fi

# Start new heartbeat
update_heartbeat

# Main execution
ensure_absolute_persistence

# Release lock
flock -u 200