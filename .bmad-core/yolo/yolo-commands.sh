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
