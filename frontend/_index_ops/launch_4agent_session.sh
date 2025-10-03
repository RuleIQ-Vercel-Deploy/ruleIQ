#!/bin/bash
# 4-Agent Parallel Execution Session Launcher
# Frontend Audit & Component System + Requirement Pages

set -e

FRONTEND_ROOT="/home/omar/Documents/ruleIQ/frontend"
SESSION_NAME="ruleiq_agents"

cd "$FRONTEND_ROOT"

echo "🚀 Launching 4-Agent Tmux Session: $SESSION_NAME"
echo "Repository: $FRONTEND_ROOT"

# Kill existing session if it exists
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true

# Create new session with Agent 1
echo "📋 Creating tmux session with 4 agents..."
tmux new-session -d -s "$SESSION_NAME" -n "Agent1_StyleCore" -c "$FRONTEND_ROOT"

# Add remaining agents
tmux new-window -t "$SESSION_NAME" -n "Agent2_ComponentAudit" -c "$FRONTEND_ROOT"
tmux new-window -t "$SESSION_NAME" -n "Agent3_QualityGate" -c "$FRONTEND_ROOT"
tmux new-window -t "$SESSION_NAME" -n "Agent4_ReqPageBuilder" -c "$FRONTEND_ROOT"

# Send task instructions to each agent
echo "💼 Dispatching tasks to each agent..."

# Agent 1: Style Core (no dependencies)
tmux send-keys -t "$SESSION_NAME:Agent1_StyleCore" "clear && echo '🎯 Agent 1: STYLE-CORE Starting...'" C-m
tmux send-keys -t "$SESSION_NAME:Agent1_StyleCore" "echo 'Task: Parse globals.css and extract design tokens'" C-m
tmux send-keys -t "$SESSION_NAME:Agent1_StyleCore" "echo 'Output: _index_ops/quality_gate/style_rules.json'" C-m
tmux send-keys -t "$SESSION_NAME:Agent1_StyleCore" "echo '📖 See: _index_ops/AGENT1_STYLECORE_TASKS.md for detailed instructions'" C-m

# Agent 2: Component Audit (depends on Agent 1)
tmux send-keys -t "$SESSION_NAME:Agent2_ComponentAudit" "clear && echo '🎯 Agent 2: COMPONENT-AUDIT Starting...'" C-m
tmux send-keys -t "$SESSION_NAME:Agent2_ComponentAudit" "echo 'Prerequisites: Waiting for style_rules.json from Agent 1'" C-m
tmux send-keys -t "$SESSION_NAME:Agent2_ComponentAudit" "echo 'Task: Inventory components, use MCP for generation'" C-m
tmux send-keys -t "$SESSION_NAME:Agent2_ComponentAudit" "echo 'Output: components_inventory.json, components_decisions.md'" C-m
tmux send-keys -t "$SESSION_NAME:Agent2_ComponentAudit" "echo '📖 See: _index_ops/AGENT2_COMPONENTAUDIT_TASKS.md'" C-m

# Agent 3: Quality Gate (depends on Agent 1 & 2)
tmux send-keys -t "$SESSION_NAME:Agent3_QualityGate" "clear && echo '🎯 Agent 3: QUALITY-GATE + STORYBOOK Starting...'" C-m
tmux send-keys -t "$SESSION_NAME:Agent3_QualityGate" "echo 'Prerequisites: style_rules.json + components_ready.flag'" C-m
tmux send-keys -t "$SESSION_NAME:Agent3_QualityGate" "echo 'Task: Implement Iron-Fist Quality Gate & Storybook'" C-m
tmux send-keys -t "$SESSION_NAME:Agent3_QualityGate" "echo 'Output: quality_gate/report.json|md, PASS.flag'" C-m
tmux send-keys -t "$SESSION_NAME:Agent3_QualityGate" "echo '📖 See: _index_ops/AGENT3_QUALITYGATE_TASKS.md'" C-m

# Agent 4: Requirement Page Builder (depends on Agent 3)
tmux send-keys -t "$SESSION_NAME:Agent4_ReqPageBuilder" "clear && echo '🎯 Agent 4: REQ-PAGE BUILDER Starting...'" C-m
tmux send-keys -t "$SESSION_NAME:Agent4_ReqPageBuilder" "echo 'Prerequisites: Waiting for quality_gate/PASS.flag from Agent 3'" C-m
tmux send-keys -t "$SESSION_NAME:Agent4_ReqPageBuilder" "echo 'Task: Build Create Wireframe page with Excalidraw MCP'" C-m
tmux send-keys -t "$SESSION_NAME:Agent4_ReqPageBuilder" "echo 'Output: wireframes/*, screenshots/*, reports/*'" C-m
tmux send-keys -t "$SESSION_NAME:Agent4_ReqPageBuilder" "echo '📖 See: _index_ops/AGENT4_REQPAGEBUILDER_TASKS.md'" C-m

echo ""
echo "✅ 4-Agent Session Created Successfully!"
echo ""
echo "🔗 To attach to the session:"
echo "    tmux attach-session -t $SESSION_NAME"
echo ""
echo "🚪 To navigate between agents:"
echo "    Ctrl+b + 1  →  Agent 1 (Style Core)"
echo "    Ctrl+b + 2  →  Agent 2 (Component Audit)" 
echo "    Ctrl+b + 3  →  Agent 3 (Quality Gate)"
echo "    Ctrl+b + 4  →  Agent 4 (Req Page Builder)"
echo ""
echo "📊 To monitor progress:"
echo "    watch -n 2 'ls -la _index_ops/quality_gate/ _index_ops/components_ready.flag 2>/dev/null || echo \"Waiting for signals...\"'"
echo ""
echo "📋 Task Instructions Available In:"
echo "    _index_ops/AGENT1_STYLECORE_TASKS.md"
echo "    _index_ops/AGENT2_COMPONENTAUDIT_TASKS.md" 
echo "    _index_ops/AGENT3_QUALITYGATE_TASKS.md"
echo "    _index_ops/AGENT4_REQPAGEBUILDER_TASKS.md"
echo ""
echo "🎯 Expected Key Outputs:"
echo "    Agent 1: style_rules.json"
echo "    Agent 2: components_inventory.json, components_decisions.md"
echo "    Agent 3: quality_gate/report.json|md, PASS.flag"  
echo "    Agent 4: wireframes/*, screenshots/*, reports/*"
echo ""
echo "⚡ Ready for parallel execution!"