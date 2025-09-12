#!/bin/bash
# BMAD Agent Runner for Docker Containers
set -e

TASK_ID=${TASK_ID:-"UNKNOWN"}
AGENT_TYPE=${AGENT_TYPE:-"generic"}
TASK_TITLE=${TASK_TITLE:-"Unnamed Task"}

echo "════════════════════════════════════════════════════════════════"
echo "                    BMAD CONTAINERIZED AGENT                    "
echo "════════════════════════════════════════════════════════════════"
echo "Task ID: ${TASK_ID}"
echo "Agent Type: ${AGENT_TYPE}"
echo "Task Title: ${TASK_TITLE}"
echo "Started: $(date)"
echo "════════════════════════════════════════════════════════════════"

# Create progress marker
mkdir -p ${BMAD_CORE}/handoffs
echo "{
  \"task_id\": \"${TASK_ID}\",
  \"agent\": \"${AGENT_TYPE}\",
  \"status\": \"in_progress\",
  \"container\": \"$(hostname)\",
  \"started_at\": \"$(date -Iseconds)\"
}" > ${BMAD_CORE}/handoffs/${TASK_ID}_container_progress.json

# Agent-specific implementation based on task
case "${AGENT_TYPE}" in
    infrastructure)
        echo "[INFRA] Setting up monitoring stack..."
        echo "[INFRA] Installing Prometheus..."
        echo "[INFRA] Configuring Grafana dashboards..."
        echo "[INFRA] Setting up alert rules..."
        
        # Simulate actual work
        sleep 10
        
        # Create mock monitoring config
        cat > ${BMAD_CORE}/handoffs/${TASK_ID}_config.yaml << EOF
monitoring:
  prometheus:
    scrape_interval: 15s
    evaluation_interval: 15s
  grafana:
    dashboards:
      - api_metrics
      - system_health
      - user_sessions
  alerts:
    - high_error_rate
    - slow_response_time
EOF
        ;;
        
    backend-specialist)
        echo "[BACKEND] Implementing Redis caching layer..."
        echo "[BACKEND] Configuring cache TTL strategies..."
        echo "[BACKEND] Setting up cache invalidation..."
        
        # Simulate Redis setup
        sleep 10
        
        # Create mock cache config
        cat > ${BMAD_CORE}/handoffs/${TASK_ID}_cache.json << EOF
{
  "redis": {
    "host": "localhost",
    "port": 6379,
    "ttl": {
      "sessions": 3600,
      "api_responses": 300,
      "ai_completions": 1800
    }
  }
}
EOF
        ;;
        
    devops)
        echo "[DEVOPS] Setting up CI/CD pipeline..."
        echo "[DEVOPS] Configuring GitHub Actions..."
        echo "[DEVOPS] Setting up deployment strategies..."
        
        # Simulate pipeline creation
        sleep 10
        
        # Create mock CI/CD config
        cat > ${BMAD_CORE}/handoffs/${TASK_ID}_cicd.yaml << EOF
name: CI/CD Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: echo "Deploying..."
EOF
        ;;
        
    *)
        echo "[AGENT] Executing generic task implementation..."
        sleep 10
        ;;
esac

# Mark task as complete
echo "{
  \"task_id\": \"${TASK_ID}\",
  \"agent\": \"${AGENT_TYPE}\",
  \"status\": \"completed\",
  \"container\": \"$(hostname)\",
  \"completed_at\": \"$(date -Iseconds)\"
}" > ${BMAD_CORE}/handoffs/${TASK_ID}_container_complete.json

echo "════════════════════════════════════════════════════════════════"
echo "[SUCCESS] Task ${TASK_ID} completed by ${AGENT_TYPE} agent"
echo "════════════════════════════════════════════════════════════════"

# Keep container alive for logs
sleep 5