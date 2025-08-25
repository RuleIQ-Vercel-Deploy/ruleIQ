#!/usr/bin/bash
# Serena MCP Session Monitor
# Quick status check and reactivation if needed

PROJECT_PATH="/home/omar/Documents/ruleIQ"
STATUS_FILE="$PROJECT_PATH/.claude/serena-status.json"
LOG_FILE="$PROJECT_PATH/.claude/serena-monitor.log"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Quick status check
check_status() {
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
    
    cd "$PROJECT_PATH" || return 1
    
    # Source environment if available
    if [ -f ".claude/serena-env.sh" ]; then
        source .claude/serena-env.sh
    fi
    
    # Run verification script
    if [ -f ".claude/serena-verification.py" ]; then
        python3 .claude/serena-verification.py >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "🔄 Serena MCP: Quick reactivation successful"
            log "Quick reactivation: SUCCESS"
            return 0
        fi
    fi
    
    echo "⚠️  Serena MCP: Quick reactivation failed"
    log "Quick reactivation: FAILED"
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