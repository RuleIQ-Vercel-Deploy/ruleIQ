#!/bin/bash

# Serena Hooks Installation Script
# Purpose: Set up all hooks and ensure they're properly configured

set -e

HOOKS_DIR="$HOME/Documents/ruleIQ/.claude/hooks"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🚀 Installing Serena MCP Verification Hooks..."

# Make all hook scripts executable
chmod +x "$HOOKS_DIR"/*.sh 2>/dev/null || true

# Create log directory
mkdir -p /tmp/serena-hooks

# Start the continuous monitor in background
echo -e "${YELLOW}Starting continuous monitor...${NC}"
nohup bash "$HOOKS_DIR/continuous-monitor.sh" > /tmp/serena-hooks/monitor-startup.log 2>&1 &
MONITOR_PID=$!
echo "Monitor started with PID: $MONITOR_PID"

# Create Claude Code configuration if it doesn't exist
CLAUDE_CONFIG="$HOME/.claude/config.json"
if [ ! -f "$CLAUDE_CONFIG" ]; then
    mkdir -p "$HOME/.claude"
    cat > "$CLAUDE_CONFIG" <<EOF
{
  "hooks": {
    "sessionStart": "$HOOKS_DIR/session-start.sh",
    "userPromptSubmit": "$HOOKS_DIR/user-prompt-submit.sh",
    "toolCallPre": "$HOOKS_DIR/tool-call-pre.sh"
  }
}
EOF
    echo -e "${GREEN}✅ Created Claude Code configuration${NC}"
fi

# Update CLAUDE.md to include hook verification
CLAUDE_MD="$HOME/Documents/ruleIQ/CLAUDE.md"
if ! grep -q "SERENA HOOK VERIFICATION" "$CLAUDE_MD" 2>/dev/null; then
    cat >> "$CLAUDE_MD" <<'EOF'

# SERENA HOOK VERIFICATION SYSTEM

**CRITICAL: This system ensures Serena MCP is ALWAYS active**

## Automatic Verification Points:
1. **Session Start**: Serena starts automatically when Claude Code opens
2. **Before Every Prompt**: Verification runs before processing user input  
3. **Before Tool Calls**: Especially Serena tools are verified
4. **Continuous Monitoring**: Background process keeps Serena alive
5. **Pre-Action Checks**: Every significant action triggers verification

## Manual Commands (if needed):
```bash
# Check status
bash .claude/serena-session-manager.sh status

# Manual start
bash .claude/serena-session-manager.sh start

# View monitor logs
tail -f /tmp/serena-hooks/monitor.log
```

## Hook System Active Since: $(date '+%Y-%m-%d %H:%M:%S')
EOF
    echo -e "${GREEN}✅ Updated CLAUDE.md with hook documentation${NC}"
fi

# Test Serena connection
echo -e "${YELLOW}Testing Serena connection...${NC}"
bash "$HOME/Documents/ruleIQ/.claude/serena-session-manager.sh" start
sleep 2

SERENA_PID=$(pgrep -f "serena.server" 2>/dev/null || true)
if [ -n "$SERENA_PID" ]; then
    echo -e "${GREEN}✅ Serena MCP is running (PID: $SERENA_PID)${NC}"
else
    echo -e "${YELLOW}⚠️  Serena not detected, will start on first use${NC}"
fi

echo ""
echo -e "${GREEN}✅ Hook system installation complete!${NC}"
echo ""
echo "The following hooks are now active:"
echo "  • Session start hook"
echo "  • User prompt verification" 
echo "  • Tool call pre-check"
echo "  • Continuous background monitor"
echo ""
echo "Serena MCP will now be automatically verified before every action."