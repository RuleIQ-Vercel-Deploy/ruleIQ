#!/usr/bin/env python3
"""
Monitor the YOLO system status in real-time.
"""
import json
import time
import importlib.util
from pathlib import Path
from datetime import datetime

# Load YOLO system
spec = importlib.util.spec_from_file_location('yolo_system', 'yolo-system.py')
yolo_system = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yolo_system)

def monitor_yolo():
    """Monitor YOLO system status."""
    print("🔍 YOLO SYSTEM MONITOR")
    print("=" * 70)

    orchestrator = yolo_system.YOLOOrchestrator()

    # Load state
    state_file = Path("state/yolo-state.json")
    if state_file.exists():
        with open(state_file) as f:
            state_data = json.load(f)
            print(f"📅 Last Updated: {state_data.get('last_save', 'Unknown')}")

    while True:
        try:
            status = orchestrator.get_status()

            # Clear screen (optional - comment out if you prefer scrolling)
            # print("\033[2J\033[H")

            print("\n" + "=" * 70)
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 70)

            print(f"\n🚦 Mode: {status['mode'].upper()}")
            print(f"📍 Phase: {status['phase'] or 'None'}")
            print(f"👤 Current Agent: {status['current_agent'] or 'None'}")
            print(f"➡️  Next Agent: {status.get('next_agent') or 'TBD'}")

            print("\n📊 Statistics:")
            print(f"   • Decisions Made: {status['decisions_made']}")
            print(f"   • Errors: {status['errors']}")
            print(f"   • Progress: {status['progress']:.1f}%")
            print(f"   • Uptime: {status['uptime']}")

            if 'context' in status and isinstance(status['context'], dict):
                if 'total_items' in status['context']:
                    print("\n💾 Context Management:")
                    print(f"   • Total Items: {status['context']['total_items']}")
                    print(f"   • Total Tokens: {status['context']['total_tokens']}")

                    if status['context'].get('agents'):
                        print(f"   • Active Agents: {len(status['context']['agents'])}")
                        for agent, info in list(status['context']['agents'].items())[:3]:
                            if isinstance(info, dict) and 'tokens' in info:
                                utilization = info.get('utilization', '0%')
                                print(f"     - {agent}: {info['tokens']} tokens ({utilization})")

            # Check recent decisions
            if orchestrator.state.decisions_made:
                print("\n🎯 Recent Decisions:")
                for decision in orchestrator.state.decisions_made[-3:]:
                    print(f"   • {decision['type']}: {decision['choice']}")

            # Check for errors
            if orchestrator.state.errors_encountered:
                print("\n⚠️  Recent Errors:")
                for error in orchestrator.state.errors_encountered[-2:]:
                    print(f"   • {error}")

            # Workflow status
            if status['phase']:
                phases = list(yolo_system.WorkflowPhase)
                current_idx = phases.index(yolo_system.WorkflowPhase(status['phase']))
                progress_bar = ""
                for i, phase in enumerate(phases):
                    if i < current_idx:
                        progress_bar += "✅"
                    elif i == current_idx:
                        progress_bar += "🔄"
                    else:
                        progress_bar += "⭕"
                print(f"\n📈 Workflow Progress: {progress_bar}")

            if status['mode'] == 'active':
                print("\n✅ System is running autonomously...")
            elif status['mode'] == 'paused':
                print("\n⏸️  System is paused. Use 'resume' to continue.")
            elif status['mode'] == 'error':
                print("\n❌ System stopped due to errors.")
            else:
                print("\n💤 System is inactive.")

            print("\nPress Ctrl+C to exit monitor")

            # Wait before next update
            time.sleep(5)

        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"\n⚠️  Error reading status: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_yolo()
