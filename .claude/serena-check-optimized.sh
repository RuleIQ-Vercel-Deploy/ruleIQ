#!/bin/bash
# Optimized Serena persistence check
# Lightweight check that doesn't create log spam

PROJECT_PATH="/home/omar/Documents/ruleIQ"
STATUS_FILE="$PROJECT_PATH/.claude/serena-status.json"
FLAG_FILE="$PROJECT_PATH/.claude/serena-active.flag"
SESSION_FLAG="$PROJECT_PATH/.claude/serena-session.flag"

# Quick flag-based check (no JSON parsing, no logging)
quick_check() {
    # If flag files exist and are recent (< 5 minutes), assume active
    if [ -f "$FLAG_FILE" ] && [ -f "$SESSION_FLAG" ]; then
        flag_age=$(( $(date +%s) - $(stat -c %Y "$FLAG_FILE" 2>/dev/null || echo 0) ))
        if [ $flag_age -lt 300 ]; then
            echo "✅ Serena MCP: Already active"
            return 0
        fi
    fi
    return 1
}

# Only reactivate if really needed
smart_reactivate() {
    # First try quick check
    if quick_check; then
        return 0
    fi
    
    # If quick check fails, do actual verification
    if [ -f "$STATUS_FILE" ]; then
        active=$(python3 -c "
import json
try:
    with open('$STATUS_FILE', 'r') as f:
        print(json.load(f).get('active', False))
except:
    print(False)
" 2>/dev/null)
        
        if [ "$active" = "True" ]; then
            # Just touch the flag files to update timestamp
            touch "$FLAG_FILE" "$SESSION_FLAG" 2>/dev/null
            echo "✅ Serena MCP Status: ACTIVE"
            return 0
        fi
    fi
    
    # Only if truly inactive, reactivate
    echo "🔄 Reactivating Serena MCP..."
    cd "$PROJECT_PATH" || return 1
    
    # Activate without logging every attempt
    if [ -f ".claude/serena-persistent-init.sh" ]; then
        bash .claude/serena-persistent-init.sh 2>/dev/null
    fi
    
    # Update flags
    touch "$FLAG_FILE" "$SESSION_FLAG"
    echo "✅ Serena MCP: Reactivated"
}

# Main execution
smart_reactivate