#!/bin/bash
# RuleIQ Claude + MCP Initialization Script
# This script launches Claude and automatically runs initialization commands

set -e

echo "🚀 RuleIQ Claude Auto-Initialization"
echo "===================================="

# Check if we're in the ruleIQ directory
if [ ! -f "CLAUDE.md" ]; then
    echo "❌ Error: Not in ruleIQ project directory"
    echo "Please run this script from /home/omar/Documents/ruleIQ/"
    exit 1
fi

# Check if Claude CLI is available
if ! command -v claude &> /dev/null; then
    echo "❌ Error: Claude CLI not found"
    echo "Please ensure Claude CLI is installed and in PATH"
    exit 1
fi

# Set up environment for MCP servers
export RULEIQ_PROJECT_PATH="/home/omar/Documents/ruleIQ"
export SERENA_ACTIVE=true
export ARCHON_ACTIVE=true

echo "✅ Environment configured"
echo "📂 Project: $RULEIQ_PROJECT_PATH"
echo ""

# Create initialization file that Claude will execute
INIT_FILE="/tmp/ruleiq_claude_init.txt"
cat > "$INIT_FILE" << 'EOF'
I'll initialize your ruleIQ session with both MCP servers.

First, let me verify Serena MCP is active:
/usr/bin/python3 /home/omar/Documents/ruleIQ/.claude/serena-verification.py

Now checking Archon MCP health:
mcp__archon__health_check

Activating ruleIQ project in Serena:
mcp__serena__activate_project ruleIQ

Reading project documentation:
cat /home/omar/Documents/ruleIQ/CLAUDE.md | head -50

Checking current Archon tasks:
mcp__archon__list_tasks filter_by="status" filter_value="todo"

Your ruleIQ session is now initialized with:
✅ Serena MCP: Code intelligence active
✅ Archon MCP: Task management ready
✅ Project context loaded

Remember the golden rule: Always check Archon tasks FIRST before any coding.
EOF

echo "📋 Initialization commands prepared"
echo ""
echo "🚀 Launching Claude with auto-initialization..."
echo "================================================"
echo ""
echo "Claude will automatically:"
echo "1. Verify both MCP servers are active"
echo "2. Load project documentation"
echo "3. Check current tasks in Archon"
echo "4. Be ready for your commands"
echo ""
echo "Starting Claude now..."
echo "================================================"

# Launch Claude with initialization file
claude --dangerously-skip-permissions < "$INIT_FILE"

# Cleanup
rm -f "$INIT_FILE"