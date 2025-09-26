#!/bin/bash

# Claude Code Action Wrapper
# Purpose: Intercept and verify Serena status before EVERY action
# This script wraps around Claude Code's tool calls

set -e

HOOK_DIR="$HOME/Documents/ruleIQ/.claude/hooks"
PRE_ACTION_HOOK="$HOOK_DIR/pre-action-serena-check.sh"

# Function to run pre-action checks
run_pre_checks() {
    if [ -f "$PRE_ACTION_HOOK" ]; then
        bash "$PRE_ACTION_HOOK"
        if [ $? -ne 0 ]; then
            echo "⚠️  Pre-action checks failed. Aborting."
            exit 1
        fi
    fi
}

# Function to ensure continuous monitoring
monitor_serena() {
    while true; do
        sleep 30
        if ! pgrep -f "serena.server" > /dev/null; then
            echo "⚠️  Serena MCP stopped unexpectedly. Restarting..."
            bash "$HOME/Documents/ruleIQ/.claude/serena-session-manager.sh" start
        fi
    done &
}

# Main execution
echo "🚀 Claude Code Action Wrapper Active"
run_pre_checks
monitor_serena

# Execute the actual command passed to the wrapper
"$@"