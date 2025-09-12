#!/bin/bash
# BMAD Hub Orchestrator Monitor
set -e

PROJECT_ROOT="/home/omar/Documents/ruleIQ"
ORCHESTRATOR_DIR="${PROJECT_ROOT}/.bmad-core/orchestrator"
HANDOFFS_DIR="${PROJECT_ROOT}/.bmad-core/handoffs"

echo "Starting BMAD Hub Orchestrator Monitor..."

while true; do
    clear
    echo "═══════════════════════════════════════════════════════════════════"
    echo "     BMAD HUB ORCHESTRATOR - Container-less Agent Coordination     "
    echo "                     $(date +'%Y-%m-%d %H:%M:%S')"
    echo "═══════════════════════════════════════════════════════════════════"
    
    # Check for completed tasks
    echo -e "\n📋 CHECKING TASK COMPLETIONS:"
    for complete_file in ${HANDOFFS_DIR}/*_complete.json; do
        if [ -f "$complete_file" ]; then
            TASK_ID=$(basename "$complete_file" | cut -d_ -f1)
            echo "  ✅ Task $TASK_ID completed"
            
            # Update Archon (get actual task UUID from Archon)
            TASK_UUID=$(curl -s http://localhost:3737/projects/304f8bae-31ce-4116-8b37-8d23726f20ab/tasks | \
                jq -r ".tasks[] | select(.title | contains(\"$TASK_ID\")) | .id" | head -1)
            
            if [ ! -z "$TASK_UUID" ]; then
                echo "     Updating Archon task $TASK_UUID to completed..."
                curl -X PATCH http://localhost:3737/tasks/${TASK_UUID} \
                    -H "Content-Type: application/json" \
                    -d '{"status": "completed"}' 2>/dev/null
                
                # Archive completion file
                mv "$complete_file" "${complete_file}.archived"
            fi
        fi
    done
    
    # Show running agents (check PIDs)
    echo -e "\n🤖 ACTIVE AGENTS:"
    for pidfile in /tmp/bmad-agent-*.pid; do
        if [ -f "$pidfile" ]; then
            PID=$(cat "$pidfile")
            TASK=$(basename "$pidfile" | sed 's/bmad-agent-//;s/.pid//')
            if ps -p $PID > /dev/null 2>&1; then
                echo "  🟢 Agent for $TASK (PID: $PID) - Running"
            else
                echo "  ⚫ Agent for $TASK (PID: $PID) - Completed"
                rm "$pidfile"
            fi
        fi
    done
    
    # Show pending P0 tasks
    echo -e "\n🚨 PENDING P0 TASKS (Critical Security):"
    curl -s http://localhost:3737/projects/304f8bae-31ce-4116-8b37-8d23726f20ab/tasks | \
        jq -r '.tasks[] | select(.status != "completed" and (.title | startswith("SEC-"))) | "  - \(.title)"' 2>/dev/null
    
    # Show pending P1 tasks
    echo -e "\n⚡ PENDING P1 TASKS (Core Features):"
    curl -s http://localhost:3737/projects/304f8bae-31ce-4116-8b37-8d23726f20ab/tasks | \
        jq -r '.tasks[] | select(.status != "completed" and ((.title | startswith("FE-")) or (.title | startswith("BE-")) or (.title | startswith("A11Y-")))) | "  - \(.title) [\(.assignee)]"' 2>/dev/null | head -10
    
    # Show task summary
    echo -e "\n📊 TASK SUMMARY:"
    TOTAL=$(curl -s http://localhost:3737/projects/304f8bae-31ce-4116-8b37-8d23726f20ab/tasks | jq '.total_count' 2>/dev/null)
    COMPLETED=$(curl -s http://localhost:3737/projects/304f8bae-31ce-4116-8b37-8d23726f20ab/tasks | jq '.tasks | map(select(.status == "completed")) | length' 2>/dev/null)
    TODO=$(curl -s http://localhost:3737/projects/304f8bae-31ce-4116-8b37-8d23726f20ab/tasks | jq '.tasks | map(select(.status == "todo")) | length' 2>/dev/null)
    IN_PROGRESS=$(curl -s http://localhost:3737/projects/304f8bae-31ce-4116-8b37-8d23726f20ab/tasks | jq '.tasks | map(select(.status == "doing")) | length' 2>/dev/null)
    
    echo "  Total Tasks: ${TOTAL:-0}"
    echo "  Completed: ${COMPLETED:-0}"
    echo "  In Progress: ${IN_PROGRESS:-0}"
    echo "  Todo: ${TODO:-0}"
    
    echo -e "\n═══════════════════════════════════════════════════════════════════"
    echo "Press Ctrl+C to stop monitoring. Refreshing in 30 seconds..."
    
    sleep 30
done