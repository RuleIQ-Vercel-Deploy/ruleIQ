#!/bin/bash
# BMAD Agent Spawner - Launch all needed agents for P0 tasks

echo "========================================"
echo "BMAD P0 Task Agent Spawner"
echo "========================================"

# Check Archon health
echo "Checking Archon status..."
if ! curl -s http://localhost:3737/health > /dev/null; then
    echo "❌ Archon not running on port 3737"
    echo "Please start Archon first"
    exit 1
fi
echo "✅ Archon is running"

# Check existing containers
echo ""
echo "Current BMAD containers:"
docker ps --filter "name=bmad-" --format "table {{.Names}}\t{{.Status}}"

# Define P0 tasks and their agents
declare -A TASKS
TASKS["FF-001"]="backend-specialist"
TASKS["TEST-001"]="qa-specialist" 
TASKS["MON-001"]="infrastructure"
TASKS["API-001"]="backend-specialist"
TASKS["SEC-002"]="security-auditor"

echo ""
echo "Checking P0 task status..."

for TASK_ID in "${!TASKS[@]}"; do
    AGENT_TYPE="${TASKS[$TASK_ID]}"
    
    # Check if task is already complete
    if [ -f "/home/omar/Documents/ruleIQ/.bmad-core/handoffs/${TASK_ID}_complete.json" ]; then
        echo "✅ $TASK_ID - Already complete"
        continue
    fi
    
    # Check if container already running
    if docker ps --filter "name=bmad-${AGENT_TYPE}-${TASK_ID}" -q > /dev/null 2>&1; then
        echo "🔄 $TASK_ID - Agent already running"
        continue
    fi
    
    # Spawn the agent
    echo "🚀 Spawning $AGENT_TYPE for $TASK_ID..."
    
    docker run -d \
        --name "bmad-${AGENT_TYPE}-${TASK_ID}" \
        --network host \
        -v /home/omar/Documents/ruleIQ:/workspace:rw \
        -v /home/omar/Documents/ruleIQ/.bmad-core:/bmad-core:rw \
        -v /home/omar/Documents/ruleIQ/docs:/docs:ro \
        -v /home/omar/Documents/ruleIQ/.claude:/claude:ro \
        -e TASK_ID="${TASK_ID}" \
        -e AGENT_TYPE="${AGENT_TYPE}" \
        -e ARCHON_URL="http://localhost:3737" \
        -e BMAD_MODE="auto" \
        -e AUTO_MODE="true" \
        claude-agent:latest \
        bash -c "cd /workspace && claude-code auto-mode --prompt /claude/agents/${AGENT_TYPE}.md"
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully spawned ${AGENT_TYPE} for ${TASK_ID}"
    else
        echo "❌ Failed to spawn ${AGENT_TYPE} for ${TASK_ID}"
    fi
    
    # Small delay between spawns
    sleep 2
done

echo ""
echo "========================================"
echo "Final Status:"
docker ps --filter "name=bmad-" --format "table {{.Names}}\t{{.Status}}"
echo ""
echo "Monitor with: docker logs -f bmad-<agent>-<task>"
echo "Or run: ~/Documents/ruleIQ/monitor-bmad.sh"
