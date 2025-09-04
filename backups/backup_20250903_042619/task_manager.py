#!/usr/bin/env python3
"""Task management utility for RuleIQ Agent Factory"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

STATE_FILE = Path("task-state/current-state.json")

def load_state():
    """Load current task state"""
    if not STATE_FILE.exists():
        return {}
    with open(STATE_FILE) as f:
        return json.load(f)

def save_state(state):
    """Save task state"""
    STATE_FILE.parent.mkdir(exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def update_task(task_id, status, agent=None):
    """Update task status"""
    state = load_state()
    if task_id in state.get("tasks", {}):
        state["tasks"][task_id]["status"] = status
        if agent:
            state["tasks"][task_id]["assigned_to"] = agent
        if status == "in_progress":
            state["tasks"][task_id]["started_at"] = datetime.now().isoformat()
        save_state(state)
        print(f"✅ Task {task_id} updated to {status}")
    else:
        print(f"❌ Task {task_id} not found")
def calculate_deadline(priority):
    """Calculate deadline based on priority"""
    now = datetime.now()
    if priority == "P0":
        return now + timedelta(hours=24)
    elif priority == "P1":
        return now + timedelta(hours=48)
    elif priority == "P2":
        return now + timedelta(days=7)
    else:
        return now + timedelta(days=14)

def check_deadlines():
    """Check for approaching deadlines"""
    state = load_state()
    now = datetime.now()
    alerts = []
    
    for task_id, task in state.get("tasks", {}).items():
        if task["status"] == "in_progress" and task.get("deadline"):
            deadline = datetime.fromisoformat(task["deadline"])
            time_left = deadline - now
            
            if time_left < timedelta(hours=12) and task["priority"] == "P0":
                alerts.append(f"⚠️  P0 task {task_id} deadline in {time_left.hours} hours!")
            elif time_left < timedelta(hours=36) and task["priority"] == "P1":
                alerts.append(f"⚠️  P1 task {task_id} deadline in {time_left.hours} hours!")
    
    return alerts
def get_status():
    """Get current project status"""
    state = load_state()
    
    # Count tasks by status
    total = len(state.get("tasks", {}))
    completed = len([t for t in state.get("tasks", {}).values() if t["status"] == "complete"])
    in_progress = len([t for t in state.get("tasks", {}).values() if t["status"] == "in_progress"])
    pending = len([t for t in state.get("tasks", {}).values() if t["status"] == "pending"])
    
    print(f"\n📊 RuleIQ Task Status")
    print(f"{'='*40}")
    print(f"Current Priority: {state.get('current_priority', 'P0')}")
    print(f"Total Tasks: {total}")
    print(f"✅ Completed: {completed}")
    print(f"⏳ In Progress: {in_progress}")
    print(f"⏸️  Pending: {pending}")
    print(f"Progress: {completed/total*100:.1f}%")
    
    # Check for alerts
    alerts = check_deadlines()
    if alerts:
        print(f"\n🚨 Alerts:")
        for alert in alerts:
            print(f"  {alert}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        get_status()
    elif sys.argv[1] == "update":
        if len(sys.argv) >= 4:
            update_task(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
        else:
            print("Usage: python task_manager.py update <task_id> <status> [agent]")
    elif sys.argv[1] == "status":
        get_status()
    else:
        print("Commands: status | update <task_id> <status> [agent]")