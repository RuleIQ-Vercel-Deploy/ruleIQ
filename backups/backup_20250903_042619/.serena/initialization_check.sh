#!/bin/bash
# Serena Initialization Status Monitor for ruleIQ
# Auto-checks and initializes Serena if needed

echo "🔧 Checking Serena MCP initialization status..."

# Check if Serena is accessible
if ! command -v serena &> /dev/null; then
    echo "❌ Serena MCP not found in PATH"
    exit 1
fi

# Get current configuration
CONFIG_OUTPUT=$(serena get_current_config 2>&1)

if [[ $? -ne 0 ]]; then
    echo "❌ Serena MCP server not responding"
    echo "   Please check if MCP server is running"
    exit 1
fi

# Check for expected indicators
PROJECT_OK=false
CONTEXT_OK=false
MODES_OK=false
ONBOARDING_OK=false

if echo "$CONFIG_OUTPUT" | grep -q "Active project: ruleIQ"; then
    PROJECT_OK=true
fi

if echo "$CONFIG_OUTPUT" | grep -q "Active context: desktop-app"; then
    CONTEXT_OK=true
fi

if echo "$CONFIG_OUTPUT" | grep -q "Active modes: interactive, editing"; then
    MODES_OK=true
fi

# Check onboarding status
ONBOARDING_OUTPUT=$(serena check_onboarding_performed 2>&1)
if echo "$ONBOARDING_OUTPUT" | grep -q "onboarding was already performed"; then
    ONBOARDING_OK=true
fi

# Report status
echo "📊 Initialization Status:"
echo "   Project (ruleIQ): $([ "$PROJECT_OK" = true ] && echo "✅" || echo "❌")"
echo "   Context (desktop-app): $([ "$CONTEXT_OK" = true ] && echo "✅" || echo "❌")"
echo "   Modes (interactive, editing): $([ "$MODES_OK" = true ] && echo "✅" || echo "❌")"
echo "   Onboarding completed: $([ "$ONBOARDING_OK" = true ] && echo "✅" || echo "❌")"

# Auto-initialize if needed
if [ "$PROJECT_OK" = false ] || [ "$CONTEXT_OK" = false ] || [ "$MODES_OK" = false ]; then
    echo ""
    echo "🔄 Auto-initializing Serena for ruleIQ project..."
    
    # Activate project
    serena activate_project ruleIQ
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Serena successfully initialized for ruleIQ"
    else
        echo "❌ Failed to initialize Serena"
        exit 1
    fi
else
    echo "✅ Serena MCP is properly initialized for ruleIQ"
fi

echo ""
echo "🎯 Ready for development work on ruleIQ project!"