#!/bin/bash
# BMad YOLO Integration Script - Enables YOLO mode for all BMad agents

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# YOLO directories
YOLO_DIR=".bmad-core/yolo"
LOGS_DIR="$YOLO_DIR/logs"
STATE_DIR="$YOLO_DIR/state"
DECISIONS_DIR="$YOLO_DIR/decisions"

# Create YOLO directory structure
create_yolo_structure() {
    echo -e "${BLUE}Creating YOLO directory structure...${NC}"
    mkdir -p "$YOLO_DIR"
    mkdir -p "$LOGS_DIR"
    mkdir -p "$STATE_DIR"
    mkdir -p "$DECISIONS_DIR"
    
    # Create initial state file
    cat > "$STATE_DIR/yolo-state.json" <<EOF
{
  "mode": "off",
  "initialized": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "version": "1.0.0",
  "agents": {
    "pm": {"enabled": false, "last_active": null},
    "architect": {"enabled": false, "last_active": null},
    "po": {"enabled": false, "last_active": null},
    "sm": {"enabled": false, "last_active": null},
    "dev": {"enabled": false, "last_active": null},
    "qa": {"enabled": false, "last_active": null}
  },
  "workflow": {
    "current_phase": null,
    "current_agent": null,
    "next_agent": null,
    "progress": 0
  },
  "statistics": {
    "decisions_made": 0,
    "handoffs_completed": 0,
    "errors_encountered": 0,
    "workflows_completed": 0
  }
}
EOF
    echo -e "${GREEN}✓ YOLO structure created${NC}"
}

# Create YOLO configuration
create_yolo_config() {
    echo -e "${BLUE}Creating YOLO configuration...${NC}"
    cat > "$YOLO_DIR/yolo-config.yaml" <<'EOF'
# BMad YOLO Configuration
version: 1.0.0

# YOLO Mode Settings
yolo:
  enabled: false
  auto_approve: true
  skip_confirmations: true
  use_defaults: true
  max_consecutive_errors: 3
  safety_stop_on_critical: true

# Default Decisions
defaults:
  technical:
    language: python
    framework: fastapi
    frontend: nextjs
    database: postgresql
    testing: pytest
    ci_cd: github_actions
    containerization: docker
    
  process:
    epic_count: 3
    stories_per_epic: 4
    test_coverage_target: 80
    code_review_required: true
    auto_merge_on_pass: true
    
  workflow:
    on_success: proceed_to_next
    on_minor_issues: document_and_continue
    on_major_issues: pause_and_alert
    on_critical_error: stop_and_rollback

# Agent Configurations
agents:
  pm:
    auto_decisions:
      - create_prd
      - define_epics
      - set_priorities
    handoff_to: architect
    
  architect:
    auto_decisions:
      - design_architecture
      - choose_tech_stack
      - define_patterns
    handoff_to: po
    
  po:
    auto_decisions:
      - shard_documents
      - create_epics
      - prioritize_backlog
    handoff_to: sm
    
  sm:
    auto_decisions:
      - create_stories
      - assign_points
      - set_sprint
    handoff_to: dev
    
  dev:
    auto_decisions:
      - implement_story
      - write_tests
      - update_docs
    handoff_to: qa
    
  qa:
    auto_decisions:
      - run_tests
      - validate_requirements
      - make_gate_decision
    handoff_to: sm

# Safety Mechanisms
safety:
  stop_keywords:
    - delete
    - drop
    - remove
    - destroy
    - payment
    - billing
    - credential
    - password
    - production
    - deploy
    
  require_confirmation:
    - database_migration
    - api_changes
    - security_updates
    - production_deployment
    
  max_auto_decisions: 100
  decision_timeout_minutes: 60

# Workflow Phases
workflow:
  phases:
    - planning
    - architecture
    - story_creation
    - development
    - testing
    - review
    - deployment
    - complete
    
  transitions:
    planning: architecture
    architecture: story_creation
    story_creation: development
    development: testing
    testing: review
    review: deployment
    deployment: complete

# Logging
logging:
  level: INFO
  file: yolo.log
  max_size_mb: 100
  rotation_count: 5
  
# Monitoring
monitoring:
  health_check_interval: 30
  metrics_enabled: true
  alert_on_errors: true
  slack_webhook: null
EOF
    echo -e "${GREEN}✓ YOLO configuration created${NC}"
}

# Create YOLO command wrapper
create_yolo_commands() {
    echo -e "${BLUE}Creating YOLO command wrapper...${NC}"
    cat > "$YOLO_DIR/yolo-commands.sh" <<'EOF'
#!/bin/bash
# YOLO Command Wrapper for BMad

YOLO_STATE=".bmad-core/yolo/state/yolo-state.json"

# Enable YOLO mode
yolo_on() {
    echo "🚀 Enabling YOLO mode..."
    python3 .bmad-core/yolo/yolo-system.py enable
    echo "✅ YOLO mode ACTIVE"
}

# Disable YOLO mode
yolo_off() {
    echo "🛑 Disabling YOLO mode..."
    python3 .bmad-core/yolo/yolo-system.py disable
    echo "❌ YOLO mode DISABLED"
}

# Check YOLO status
yolo_status() {
    echo "📊 YOLO Status:"
    python3 .bmad-core/yolo/yolo-system.py status
}

# Start workflow
yolo_workflow() {
    local phase=${1:-planning}
    echo "🎯 Starting workflow at $phase phase..."
    python3 .bmad-core/yolo/yolo-system.py workflow "$phase"
}

# Auto handoff
yolo_handoff() {
    local agent=$1
    if [ -z "$agent" ]; then
        echo "❌ Please specify target agent"
        return 1
    fi
    echo "📦 Creating handoff to $agent..."
    python3 .bmad-core/yolo/yolo-system.py handoff "$agent"
}

# Show decisions
yolo_decisions() {
    echo "📝 Recent YOLO decisions:"
    python3 .bmad-core/yolo/yolo-system.py decisions
}

# Process command
case "$1" in
    on)
        yolo_on
        ;;
    off)
        yolo_off
        ;;
    status)
        yolo_status
        ;;
    workflow)
        yolo_workflow "$2"
        ;;
    handoff)
        yolo_handoff "$2"
        ;;
    decisions)
        yolo_decisions
        ;;
    *)
        echo "Usage: $0 {on|off|status|workflow|handoff|decisions}"
        exit 1
        ;;
esac
EOF
    chmod +x "$YOLO_DIR/yolo-commands.sh"
    echo -e "${GREEN}✓ YOLO commands created${NC}"
}

# Create YOLO agent templates
create_agent_templates() {
    echo -e "${BLUE}Creating YOLO agent templates...${NC}"
    
    # PM Agent YOLO template
    cat > "$YOLO_DIR/agent-pm-yolo.md" <<'EOF'
# PM Agent YOLO Template

## Auto-Decisions
- Number of epics: 3-5
- Priority scheme: MoSCoW
- Sprint length: 2 weeks
- Team size assumption: 5-8 developers

## Handoff Package
```json
{
  "artifacts": ["docs/prd.md"],
  "next_action": "create_architecture",
  "context": {
    "epics_created": 3,
    "total_story_points": 50
  }
}
```
EOF

    # Dev Agent YOLO template
    cat > "$YOLO_DIR/agent-dev-yolo.md" <<'EOF'
# Dev Agent YOLO Template

## Auto-Decisions
- Use existing patterns from codebase
- Test coverage minimum: 80%
- Follow project lint rules
- Auto-fix minor issues

## Handoff Package
```json
{
  "artifacts": ["files_created", "files_modified"],
  "next_action": "run_tests",
  "context": {
    "story_id": "current",
    "tests_written": true,
    "coverage": 85
  }
}
```
EOF

    # QA Agent YOLO template
    cat > "$YOLO_DIR/agent-qa-yolo.md" <<'EOF'
# QA Agent YOLO Template

## Auto-Decisions
- Pass if coverage > 80%
- Pass if no critical issues
- Document minor issues
- Auto-approve if all tests pass

## Gate Decisions
- PASS: All criteria met
- CONDITIONAL: Minor issues documented
- FAIL: Critical issues or < 70% coverage
EOF

    echo -e "${GREEN}✓ Agent templates created${NC}"
}

# Create YOLO monitoring dashboard
create_monitoring_dashboard() {
    echo -e "${BLUE}Creating YOLO monitoring dashboard...${NC}"
    cat > "$YOLO_DIR/dashboard.html" <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BMad YOLO Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            font-size: 3em;
            margin-bottom: 10px;
        }
        .status {
            text-align: center;
            font-size: 1.5em;
            margin-bottom: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .card h2 {
            margin-top: 0;
            font-size: 1.5em;
            border-bottom: 2px solid rgba(255, 255, 255, 0.3);
            padding-bottom: 10px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .metric:last-child {
            border-bottom: none;
        }
        .value {
            font-weight: bold;
            color: #ffd700;
        }
        .progress-bar {
            width: 100%;
            height: 30px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress {
            height: 100%;
            background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        .active { color: #00ff00; }
        .paused { color: #ffff00; }
        .error { color: #ff0000; }
        .button {
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid white;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            margin: 5px;
            transition: all 0.3s;
        }
        .button:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.05);
        }
        .controls {
            text-align: center;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 BMad YOLO Dashboard</h1>
        <div class="status">
            Status: <span id="status" class="active">ACTIVE</span>
        </div>
        
        <div class="progress-bar">
            <div class="progress" id="progress" style="width: 45%">45%</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>📊 Workflow Status</h2>
                <div class="metric">
                    <span>Current Phase:</span>
                    <span class="value">Development</span>
                </div>
                <div class="metric">
                    <span>Current Agent:</span>
                    <span class="value">Dev</span>
                </div>
                <div class="metric">
                    <span>Next Agent:</span>
                    <span class="value">QA</span>
                </div>
                <div class="metric">
                    <span>Progress:</span>
                    <span class="value">45%</span>
                </div>
            </div>
            
            <div class="card">
                <h2>📈 Metrics</h2>
                <div class="metric">
                    <span>Decisions Made:</span>
                    <span class="value">127</span>
                </div>
                <div class="metric">
                    <span>Handoffs:</span>
                    <span class="value">8</span>
                </div>
                <div class="metric">
                    <span>Errors:</span>
                    <span class="value">2</span>
                </div>
                <div class="metric">
                    <span>Uptime:</span>
                    <span class="value">2:34:15</span>
                </div>
            </div>
            
            <div class="card">
                <h2>🤖 Agent Activity</h2>
                <div class="metric">
                    <span>PM:</span>
                    <span class="value">✅ Complete</span>
                </div>
                <div class="metric">
                    <span>Architect:</span>
                    <span class="value">✅ Complete</span>
                </div>
                <div class="metric">
                    <span>Dev:</span>
                    <span class="value">🔄 Active</span>
                </div>
                <div class="metric">
                    <span>QA:</span>
                    <span class="value">⏳ Pending</span>
                </div>
            </div>
            
            <div class="card">
                <h2>📝 Recent Decisions</h2>
                <div class="metric">
                    <span>Framework:</span>
                    <span class="value">FastAPI</span>
                </div>
                <div class="metric">
                    <span>Database:</span>
                    <span class="value">PostgreSQL</span>
                </div>
                <div class="metric">
                    <span>Testing:</span>
                    <span class="value">pytest</span>
                </div>
                <div class="metric">
                    <span>Coverage:</span>
                    <span class="value">85%</span>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <button class="button" onclick="toggleYOLO()">Toggle YOLO</button>
            <button class="button" onclick="pauseYOLO()">Pause</button>
            <button class="button" onclick="showDecisions()">Show Decisions</button>
            <button class="button" onclick="refreshStatus()">Refresh</button>
        </div>
    </div>
    
    <script>
        function toggleYOLO() {
            console.log('Toggling YOLO mode...');
            // Implementation would connect to backend
        }
        
        function pauseYOLO() {
            console.log('Pausing YOLO mode...');
        }
        
        function showDecisions() {
            console.log('Showing decisions...');
        }
        
        function refreshStatus() {
            location.reload();
        }
        
        // Auto-refresh every 5 seconds
        setInterval(refreshStatus, 5000);
    </script>
</body>
</html>
EOF
    echo -e "${GREEN}✓ Monitoring dashboard created${NC}"
}

# Main installation
main() {
    echo -e "${YELLOW}╔══════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║     BMad YOLO System Installation    ║${NC}"
    echo -e "${YELLOW}╚══════════════════════════════════════╝${NC}"
    echo
    
    create_yolo_structure
    create_yolo_config
    create_yolo_commands
    create_agent_templates
    create_monitoring_dashboard
    
    echo
    echo -e "${GREEN}✅ BMad YOLO System Successfully Installed!${NC}"
    echo
    echo -e "${BLUE}Available Commands:${NC}"
    echo "  .bmad-core/yolo/yolo-commands.sh on       - Enable YOLO mode"
    echo "  .bmad-core/yolo/yolo-commands.sh off      - Disable YOLO mode"
    echo "  .bmad-core/yolo/yolo-commands.sh status   - Check status"
    echo "  .bmad-core/yolo/yolo-commands.sh workflow - Start workflow"
    echo
    echo -e "${YELLOW}⚠️  Warning: YOLO mode enables aggressive automation${NC}"
    echo -e "${YELLOW}    Use with caution in production environments${NC}"
    echo
    echo -e "${GREEN}Dashboard available at: .bmad-core/yolo/dashboard.html${NC}"
}

# Run main installation
main