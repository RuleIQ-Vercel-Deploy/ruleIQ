#!/bin/bash
# RuleIQ Agent Factory Initialization Script

echo "🚀 RuleIQ Agent Factory Initializer"
echo "===================================="

# Check if we're in the right directory
if [ ! -f ".claude/CLAUDE.md" ]; then
    echo "❌ Error: Not in ruleIQ project directory"
    echo "Please run from: ~/Documents/ruleIQ"
    exit 1
fi

echo "✅ Project directory confirmed"

# Check task state
if [ -f "task-state/current-state.json" ]; then
    echo "✅ Task state file exists"
    python3 task_manager.py status
else
    echo "❌ Task state file missing - creating..."
    mkdir -p task-state
    echo '{"current_priority":"P0","tasks":{}}' > task-state/current-state.json
fi

# Display available agents
echo -e "\n📋 Available Agents:"
for agent in .claude/agents/*.md; do
    name=$(basename "$agent" .md)
    echo "  • $name"
done

# Display available commands
echo -e "\n🔧 Available Commands:"
for cmd in .claude/commands/*.md; do
    name=$(basename "$cmd" .md)
    echo "  • /$name"
done
echo -e "\n🎯 Priority P0 Tasks (CRITICAL):"
echo "  • a02d81dc - Fix env var configuration"
echo "  • 2ef17163 - Configure test DB"
echo "  • d28d8c18 - Fix datetime errors"
echo "  • a681da5e - Fix generator syntax"
echo "  • 5d753858 - Fix test class init"
echo "  • 799f27b3 - Add test fixtures"

echo -e "\n📝 Quick Start Instructions:"
echo "1. Open Claude Code"
echo "2. Load orchestrator agent: .claude/agents/orchestrator.md"
echo "3. Orchestrator will spawn specialists as needed"
echo "4. Monitor progress: python3 task_manager.py status"
echo "5. Check gates: /check-gate P0"

echo -e "\n⏰ Timeframe Reminders:"
echo "  P0: 24 hours max (escalate at 12h)"
echo "  P1: 48 hours max (escalate at 36h)"
echo "  P2: 1 week max (escalate at 5 days)"

echo -e "\n🚦 Current Gate Status:"
if grep -q '"P0": "complete"' task-state/current-state.json 2>/dev/null; then
    echo "  P0: ✅ Complete - P1 unlocked"
else
    echo "  P0: ⏳ In Progress - P1 blocked"
fi

echo -e "\n Ready to start! Load the orchestrator agent in Claude Code.\n"