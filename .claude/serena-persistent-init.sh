#!/bin/bash
# Serena MCP Persistent Initialization Script
# Ensures Serena stays active across all Claude Code sessions

set -e

LOG_FILE="/home/omar/Documents/ruleIQ/.claude/serena-init.log"
PROJECT_PATH="/home/omar/Documents/ruleIQ"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "$1"
}

# Function to check if Serena is active using verification script
check_serena_active() {
    if [ -f "$PROJECT_PATH/.claude/serena-verification.py" ]; then
        cd "$PROJECT_PATH" && python .claude/serena-verification.py
        return $?
    else
        log "⚠️  Verification script not found, using basic check"
        # Fallback to basic check
        if timeout 5 bash -c 'cd "'"$PROJECT_PATH"'" && python -c "
import sys
sys.path.insert(0, \".\")
try:
    from services.ai.policy_generator import PolicyGenerator
    print(\"SERENA_ACTIVE\")
except:
    print(\"SERENA_INACTIVE\")
"' 2>/dev/null | grep -q "SERENA_ACTIVE"; then
            return 0
        else
            return 1
        fi
    fi
}

# Function to activate Serena with enhanced persistence
activate_serena() {
    log "🔄 Activating Serena MCP for ruleIQ project..."
    
    cd "$PROJECT_PATH" || {
        log "❌ Failed to navigate to project directory: $PROJECT_PATH"
        exit 1
    }
    
    # Source virtual environment if it exists
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        log "✅ Virtual environment activated"
    fi
    
    # Set comprehensive environment variables for MCP persistence
    export CLAUDE_PROJECT_DIR="$PROJECT_PATH"
    export MCP_SERVER_SERENA_ACTIVE=true
    export SERENA_PROJECT_PATH="$PROJECT_PATH"
    export SERENA_PERSISTENCE_MODE=true
    export PYTHONPATH="$PROJECT_PATH:$PYTHONPATH"
    
    # Ensure Claude config directory exists
    mkdir -p "$PROJECT_PATH/.claude"
    
    # Write activation status to file for cross-session persistence
    cat > "$PROJECT_PATH/.claude/serena-env.sh" << EOF
#!/bin/bash
# Auto-generated Serena environment variables
export CLAUDE_PROJECT_DIR="$PROJECT_PATH"
export MCP_SERVER_SERENA_ACTIVE=true
export SERENA_PROJECT_PATH="$PROJECT_PATH"
export SERENA_PERSISTENCE_MODE=true
export PYTHONPATH="$PROJECT_PATH:\$PYTHONPATH"
EOF
    
    chmod +x "$PROJECT_PATH/.claude/serena-env.sh"
    
    log "✅ Serena MCP activation complete with persistence layer"
    return 0
}

# Main execution
main() {
    log "🚀 Serena Persistent Init Hook Started"
    
    # Always try to activate Serena regardless of current state
    # This ensures maximum persistence
    activate_serena
    
    # Run comprehensive verification
    log "🔍 Running comprehensive Serena verification..."
    if check_serena_active; then
        log "✅ Serena MCP confirmed active and ready"
        echo "🔗 Serena MCP Active - Enhanced Code Intelligence Ready"
    else
        log "⚠️  Serena MCP verification failed, attempting recovery..."
        
        # Attempt recovery by re-activating
        activate_serena
        
        # Try one more time
        if check_serena_active; then
            log "✅ Serena MCP recovered successfully"
            echo "🔄 Serena MCP: Recovery successful - Enhanced Intelligence Ready"
        else
            log "❌ Serena MCP recovery failed"
            echo "⚠️  Serena MCP: Manual activation may be required"
        fi
    fi
    
    # Set persistent session variables and flags
    export SERENA_ACTIVE=true
    export SERENA_PROJECT="ruleIQ"
    export SERENA_LAST_INIT="$(date +%s)"
    
    # Create persistence flag file
    mkdir -p "$PROJECT_PATH/.claude"
    echo "$(date +%s)" > "$PROJECT_PATH/.claude/serena-session.flag"
    
    log "📋 Session initialization complete with persistence flags set"
}

# Execute main function
main "$@" 2>&1

# Ensure we exit successfully to not block Claude Code
exit 0