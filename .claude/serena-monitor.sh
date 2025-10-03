#!/usr/bin/bash
# Serena MCP Session Monitor
# Quick status check and reactivation if needed

PROJECT_PATH="/home/omar/Documents/ruleIQ"
STATUS_FILE="$PROJECT_PATH/.claude/serena-status.json"
LOG_FILE="$PROJECT_PATH/.claude/serena-monitor.log"
LOCK_FILE="$PROJECT_PATH/.claude/serena.lock"
METRICS_FILE="$PROJECT_PATH/.claude/serena-metrics.json"

# Function to log with timestamp and auto-rotation
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"

    # Rotate log if it exceeds 1MB (more aggressive)
    local log_size=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null || echo 0)
    if [ "$log_size" -gt 1048576 ]; then
        if [ -f "$PROJECT_PATH/.claude/log-rotation.sh" ]; then
            bash "$PROJECT_PATH/.claude/log-rotation.sh" >/dev/null 2>&1
        fi
    fi
}

# Function to check for duplicate Serena instances
check_duplicate_instances() {
    local instance_count=$(pgrep -fc "serena start-mcp-server.*ruleIQ" 2>/dev/null || echo 0)
    if [ "$instance_count" -gt 1 ]; then
        log "⚠️ Multiple Serena instances detected ($instance_count), cleaning up..."
        # Get all PIDs except the most recent one
        pgrep -f "serena start-mcp-server.*ruleIQ" 2>/dev/null | head -n -1 | while read pid; do
            kill "$pid" 2>/dev/null && log "Killed duplicate instance: $pid"
        done
        return 1
    fi
    return 0
}

# Function to clean up zombie processes
cleanup_zombies() {
    # Find and clean up zombie Serena processes
    local zombies=$(ps aux | grep -E "serena.*<defunct>" | grep -v grep | awk '{print $2}')
    if [ -n "$zombies" ]; then
        log "🧹 Cleaning up zombie processes: $zombies"
        echo "$zombies" | xargs kill -9 2>/dev/null || true
    fi
}

# Function to acquire lock
acquire_lock() {
    local max_wait=5
    local waited=0

    while [ $waited -lt $max_wait ]; do
        if [ ! -f "$LOCK_FILE" ]; then
            # No lock file, create it
            echo $$ > "$LOCK_FILE"
            log "Lock acquired by PID $$"
            return 0
        fi

        # Check if lock is stale (process not running)
        local lock_pid=$(cat "$LOCK_FILE" 2>/dev/null)
        if [ -n "$lock_pid" ] && ! kill -0 "$lock_pid" 2>/dev/null; then
            log "Removing stale lock from PID $lock_pid"
            rm -f "$LOCK_FILE"
            echo $$ > "$LOCK_FILE"
            log "Lock acquired by PID $$ (stale removed)"
            return 0
        fi

        # Lock is held by active process, wait
        sleep 1
        waited=$((waited + 1))
    done

    log "Failed to acquire lock after ${max_wait}s (held by PID $lock_pid)"
    return 1
}

# Function to release lock
release_lock() {
    if [ -f "$LOCK_FILE" ]; then
        local lock_pid=$(cat "$LOCK_FILE" 2>/dev/null)
        if [ "$lock_pid" = "$$" ]; then
            rm -f "$LOCK_FILE"
            log "Lock released by PID $$"
        fi
    fi
}

# Function to log metrics
log_metrics() {
    local instance_count=$(pgrep -fc "serena start-mcp-server.*ruleIQ" 2>/dev/null || echo 0)
    local zombie_count=$(ps aux | grep -E "serena.*<defunct>" | grep -v grep | wc -l)
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Create or append to metrics file
    local metrics_entry=$(cat <<EOF
{
  "timestamp": "$timestamp",
  "instance_count": $instance_count,
  "zombie_count": $zombie_count,
  "action": "${1:-status_check}"
}
EOF
)

    # Append to metrics array (keep last 100 entries)
    if [ ! -f "$METRICS_FILE" ]; then
        echo '{"metrics": []}' > "$METRICS_FILE"
    fi

    python3 -c "
import json
import sys
from pathlib import Path

metrics_file = Path('$METRICS_FILE')
try:
    data = json.loads(metrics_file.read_text())
    metrics = data.get('metrics', [])
    metrics.append($metrics_entry)

    # Keep only last 100 entries
    if len(metrics) > 100:
        metrics = metrics[-100:]

    data['metrics'] = metrics
    metrics_file.write_text(json.dumps(data, indent=2))
except Exception as e:
    print(f'Metrics logging error: {e}', file=sys.stderr)
" 2>/dev/null || true
}

# Quick status check
check_status() {
    log_metrics "status_check"

    if [ -f "$STATUS_FILE" ]; then
        # Check if status file indicates active state
        if python3 -c "
import json
try:
    with open('$STATUS_FILE', 'r') as f:
        status = json.load(f)
    if status.get('active', False):
        print('ACTIVE')
    else:
        print('INACTIVE')
except:
    print('UNKNOWN')
" | grep -q "ACTIVE"; then
            echo "✅ Serena MCP Status: ACTIVE"
            log "Status check: ACTIVE"
            return 0
        fi
    fi

    echo "⚠️  Serena MCP Status: INACTIVE or UNKNOWN"
    log "Status check: INACTIVE"
    return 1
}

# Quick reactivation
quick_reactivate() {
    log "Attempting quick reactivation..."

    # Acquire lock to prevent concurrent reactivations
    if ! acquire_lock; then
        log "Could not acquire lock, another reactivation in progress"
        echo "⏳ Serena MCP: Reactivation already in progress"
        log_metrics "reactivate_skipped_lock"
        return 1
    fi

    # Ensure lock is released on exit
    trap release_lock EXIT

    # First, check for and clean up duplicate instances
    check_duplicate_instances
    cleanup_zombies

    # Check if Serena is already running
    local instance_count=$(pgrep -fc "serena start-mcp-server.*ruleIQ" 2>/dev/null || echo 0)
    if [ "$instance_count" -gt 0 ]; then
        log "Serena already running (count: $instance_count), skipping reactivation"
        echo "✅ Serena MCP: Already active"
        log_metrics "reactivate_skipped_running"
        release_lock
        return 0
    fi

    cd "$PROJECT_PATH" || {
        release_lock
        return 1
    }

    # Source environment if available
    if [ -f ".claude/serena-env.sh" ]; then
        source .claude/serena-env.sh
    fi

    # Run verification script only if no instances running
    if [ -f ".claude/serena-verification.py" ]; then
        python3 .claude/serena-verification.py >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "🔄 Serena MCP: Quick reactivation successful"
            log "Quick reactivation: SUCCESS"
            log_metrics "reactivate_success"
            release_lock
            return 0
        fi
    fi

    echo "⚠️  Serena MCP: Quick reactivation failed"
    log "Quick reactivation: FAILED"
    log_metrics "reactivate_failed"
    release_lock
    return 1
}

# Main execution
main() {
    case "${1:-status}" in
        "status")
            check_status
            ;;
        "reactivate")
            if ! check_status; then
                quick_reactivate
            else
                echo "✅ Serena MCP: Already active"
            fi
            ;;
        "force-reactivate")
            quick_reactivate
            ;;
        *)
            echo "Usage: $0 {status|reactivate|force-reactivate}"
            echo "  status         - Check current Serena status"
            echo "  reactivate     - Reactivate if inactive"
            echo "  force-reactivate - Force reactivation regardless of status"
            exit 1
            ;;
    esac
}

main "$@"