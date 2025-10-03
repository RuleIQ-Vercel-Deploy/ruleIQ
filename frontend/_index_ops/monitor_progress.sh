#!/bin/bash
# 4-Agent Progress Monitor
# Real-time status dashboard for parallel execution

FRONTEND_ROOT="/home/omar/Documents/ruleIQ/frontend"
SESSION_NAME="ruleiq_agents"

cd "$FRONTEND_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

show_status() {
    clear
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                    4-AGENT EXECUTION MONITOR                    ${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Session status
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        echo -e "${GREEN}📡 Tmux Session: ${SESSION_NAME} (ACTIVE)${NC}"
    else
        echo -e "${RED}📡 Tmux Session: ${SESSION_NAME} (NOT FOUND)${NC}"
        echo ""
        echo -e "${YELLOW}💡 To start session: ./_index_ops/launch_4agent_session.sh${NC}"
        return
    fi
    
    echo -e "${BLUE}🕐 Last Updated: $(date)${NC}"
    echo ""
    
    # Agent status indicators
    echo -e "${PURPLE}┌─────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${PURPLE}│                        AGENT STATUS                         │${NC}"
    echo -e "${PURPLE}├─────────────────────────────────────────────────────────────┤${NC}"
    
    # Agent 1: Style Core
    if [ -f "_index_ops/quality_gate/style_rules.json" ]; then
        echo -e "${PURPLE}│${NC} Agent 1 (Style Core)           ${GREEN}✅ COMPLETE${NC}              ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   └─ style_rules.json           ${GREEN}[READY]${NC}                 ${PURPLE}│${NC}"
    else
        echo -e "${PURPLE}│${NC} Agent 1 (Style Core)           ${YELLOW}⏳ WORKING${NC}               ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   └─ style_rules.json           ${RED}[PENDING]${NC}               ${PURPLE}│${NC}"
    fi
    
    # Agent 2: Component Audit  
    if [ -f "_index_ops/components_ready.flag" ]; then
        echo -e "${PURPLE}│${NC} Agent 2 (Component Audit)      ${GREEN}✅ COMPLETE${NC}              ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   ├─ components_inventory.json  ${GREEN}[READY]${NC}                 ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   ├─ components_decisions.md    ${GREEN}[READY]${NC}                 ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   └─ components_ready.flag      ${GREEN}[SIGNALED]${NC}              ${PURPLE}│${NC}"
    elif [ -f "_index_ops/quality_gate/style_rules.json" ]; then
        echo -e "${PURPLE}│${NC} Agent 2 (Component Audit)      ${YELLOW}⏳ WORKING${NC}               ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   ├─ components_inventory.json  ${YELLOW}[IN PROGRESS]${NC}           ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   ├─ components_decisions.md    ${YELLOW}[IN PROGRESS]${NC}           ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   └─ components_ready.flag      ${RED}[PENDING]${NC}               ${PURPLE}│${NC}"
    else
        echo -e "${PURPLE}│${NC} Agent 2 (Component Audit)      ${RED}❌ WAITING${NC}               ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   └─ Waiting for Agent 1        ${RED}[BLOCKED]${NC}               ${PURPLE}│${NC}"
    fi
    
    # Agent 3: Quality Gate
    if [ -f "_index_ops/quality_gate/PASS.flag" ]; then
        echo -e "${PURPLE}│${NC} Agent 3 (Quality Gate)         ${GREEN}✅ COMPLETE${NC}              ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   ├─ Storybook setup            ${GREEN}[READY]${NC}                 ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   ├─ quality_gate/report.json   ${GREEN}[READY]${NC}                 ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   └─ quality_gate/PASS.flag     ${GREEN}[SIGNALED]${NC}              ${PURPLE}│${NC}"
    elif [ -f "_index_ops/quality_gate/FAIL.flag" ]; then
        echo -e "${PURPLE}│${NC} Agent 3 (Quality Gate)         ${RED}❌ FAILED${NC}                ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   └─ See quality_gate/report.md ${RED}[CHECK LOGS]${NC}            ${PURPLE}│${NC}"
    elif [ -f "_index_ops/components_ready.flag" ] && [ -f "_index_ops/quality_gate/style_rules.json" ]; then
        echo -e "${PURPLE}│${NC} Agent 3 (Quality Gate)         ${YELLOW}⏳ WORKING${NC}               ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   ├─ Running Iron-Fist checks   ${YELLOW}[IN PROGRESS]${NC}           ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   └─ Building Storybook         ${YELLOW}[IN PROGRESS]${NC}           ${PURPLE}│${NC}"
    else
        echo -e "${PURPLE}│${NC} Agent 3 (Quality Gate)         ${RED}❌ WAITING${NC}               ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   └─ Waiting for Agents 1 & 2   ${RED}[BLOCKED]${NC}               ${PURPLE}│${NC}"
    fi
    
    # Agent 4: Req Page Builder
    if [ -f "_req_pages/req_index.json" ]; then
        echo -e "${PURPLE}│${NC} Agent 4 (Req Page Builder)     ${GREEN}✅ COMPLETE${NC}              ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   ├─ wireframes/create-wireframe ${GREEN}[READY]${NC}                 ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   ├─ screenshots/create-wireframe ${GREEN}[READY]${NC}                ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   └─ req_index.json             ${GREEN}[READY]${NC}                 ${PURPLE}│${NC}"
    elif [ -f "_index_ops/quality_gate/PASS.flag" ]; then
        echo -e "${PURPLE}│${NC} Agent 4 (Req Page Builder)     ${YELLOW}⏳ WORKING${NC}               ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   ├─ Creating Excalidraw wireframe ${YELLOW}[IN PROGRESS]${NC}         ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   ├─ Building Next.js route     ${YELLOW}[IN PROGRESS]${NC}           ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   └─ Generating screenshots     ${YELLOW}[IN PROGRESS]${NC}           ${PURPLE}│${NC}"
    else
        echo -e "${PURPLE}│${NC} Agent 4 (Req Page Builder)     ${RED}❌ WAITING${NC}               ${PURPLE}│${NC}"
        echo -e "${PURPLE}│${NC}   └─ Waiting for Agent 3 PASS   ${RED}[BLOCKED]${NC}               ${PURPLE}│${NC}"
    fi
    
    echo -e "${PURPLE}└─────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    
    # File system status
    echo -e "${BLUE}📁 KEY FILES STATUS:${NC}"
    
    # Check critical files
    files=(
        "_index_ops/quality_gate/style_rules.json:Agent 1 Output"
        "_index_ops/components_inventory.json:Agent 2 Inventory" 
        "_index_ops/components_decisions.md:Agent 2 Decisions"
        "_index_ops/components_ready.flag:Agent 2 Signal"
        "_index_ops/quality_gate/report.json:Agent 3 Report"
        "_index_ops/quality_gate/PASS.flag:Agent 3 Signal"
        "_req_pages/wireframes/create-wireframe.png:Agent 4 Wireframe"
        "_req_pages/screenshots/create-wireframe.png:Agent 4 Screenshot"
        "_req_pages/req_index.json:Agent 4 Index"
    )
    
    for file_info in "${files[@]}"; do
        IFS=':' read -r file desc <<< "$file_info"
        if [ -f "$file" ]; then
            size=$(du -h "$file" | cut -f1)
            modified=$(stat -c %y "$file" 2>/dev/null | cut -d. -f1 || echo "unknown")
            echo -e "  ${GREEN}✓${NC} $desc ${GREEN}($size)${NC} - $modified"
        else
            echo -e "  ${RED}✗${NC} $desc ${RED}[Missing]${NC}"
        fi
    done
    
    echo ""
    echo -e "${BLUE}🎛️  CONTROLS:${NC}"
    echo -e "   ${YELLOW}Ctrl+C${NC}     - Stop monitoring"
    echo -e "   ${YELLOW}tmux attach -t ruleiq_agents${NC} - Attach to session" 
    echo -e "   ${YELLOW}Ctrl+b + 1,2,3,4${NC} - Switch between agents"
    echo ""
}

# Main monitoring loop
if [ "$1" = "--once" ]; then
    show_status
else
    echo -e "${BLUE}Starting 4-Agent Progress Monitor...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    echo ""
    
    while true; do
        show_status
        sleep 3
    done
fi