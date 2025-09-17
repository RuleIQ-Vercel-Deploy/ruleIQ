#!/usr/bin/env python3
"""
Activate YOLO mode and start autonomous RuleIQ workflow.
"""
import asyncio
import json
import importlib.util

# Load YOLO system
spec = importlib.util.spec_from_file_location('yolo_system', 'yolo-system.py')
yolo_system = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yolo_system)

async def activate_and_start():
    """Activate YOLO and initiate RuleIQ workflow."""
    print("=" * 70)
    print("🚀 ACTIVATING BMAD YOLO SYSTEM FOR RULEIQ")
    print("=" * 70)

    # Initialize orchestrator
    orchestrator = yolo_system.YOLOOrchestrator()

    # Activate YOLO mode
    await orchestrator.activate()
    print("✅ YOLO Mode: ACTIVE")
    print("✅ Context Refresh: ENABLED")
    print("✅ Autonomous Operation: READY")

    # Set initial context for RuleIQ
    print("\n📋 Loading RuleIQ Project Context...")

    initial_context = {
        "project": "RuleIQ Compliance Automation Platform",
        "objective": "Complete P0 and P1 priority tasks",
        "immediate_priorities": [
            "Fix backend test pass rate (target: 95%)",
            "Resolve authentication flow issues",
            "Fix API routing problems",
            "Address frontend hydration bugs"
        ],
        "current_state": {
            "backend_tests": "Failing at 75%",
            "auth_system": "JWT implementation incomplete",
            "api_routes": "Some 404 errors",
            "frontend": "Hydration warnings in console"
        },
        "tech_stack": {
            "backend": "Python 3.12, FastAPI, SQLAlchemy",
            "frontend": "Next.js 14, React 18, TypeScript",
            "database": "PostgreSQL with pgvector",
            "testing": "pytest, playwright",
            "ci_cd": "GitHub Actions"
        }
    }

    # Initialize as PM to start workflow
    orchestrator.state.current_agent = yolo_system.AgentType.PM
    orchestrator.state.current_phase = yolo_system.WorkflowPhase.PLANNING

    # Add context to manager
    if orchestrator.context_manager:
        for key, value in initial_context.items():
            priority = (
                yolo_system.ContextPriority.CRITICAL
                if key in ["immediate_priorities", "current_state"]
                else yolo_system.ContextPriority.HIGH
            )
            orchestrator.context_manager.add_context(
                key,
                json.dumps(value) if isinstance(value, (dict, list)) else value,
                priority,
                "pm"
            )
        print(f"✅ Loaded {len(initial_context)} context items")

    # Make initial planning decisions
    print("\n🤖 Making Initial Decisions...")

    decisions = {
        "approach": orchestrator.make_decision(
            "fix_approach",
            ["incremental_fixes", "complete_rewrite", "hybrid_approach"],
            {"priority": "Quick fixes for P0 issues"}
        ),
        "test_strategy": orchestrator.make_decision(
            "test_fixing_strategy",
            ["fix_existing_tests", "write_new_tests", "both"],
            {"current_coverage": "75%", "target": "95%"}
        ),
        "parallel_work": orchestrator.make_decision(
            "work_distribution",
            ["sequential", "parallel_tracks", "staged"],
            {"team_size": "multi-agent", "urgency": "high"}
        )
    }

    for key, value in decisions.items():
        print(f"   • {key}: {value}")

    # Create first handoff to Architect
    print("\n📦 Creating Handoff: PM → ARCHITECT")

    handoff = await orchestrator.handoff(
        to_agent=yolo_system.AgentType.ARCHITECT,
        artifacts={
            "priorities": ["P0_tasks.md", "P1_tasks.md"],
            "current_issues": ["test_failures.log", "auth_bugs.md"]
        },
        context={
            **initial_context,
            "decisions": decisions,
            "next_steps": "Analyze architecture for fixing priority issues"
        }
    )

    print("✅ Handoff Complete!")
    print(f"   • To: {handoff.to_agent.value}")
    print(f"   • Context Items: {len(handoff.context)}")
    print(f"   • Next Action: {handoff.next_action}")

    # Display status
    status = orchestrator.get_status()
    print("\n" + "=" * 70)
    print("📊 YOLO SYSTEM STATUS")
    print("=" * 70)
    print(f"Mode: {status['mode'].upper()}")
    print(f"Phase: {status['phase']}")
    print(f"Current Agent: {status['current_agent']}")
    print(f"Decisions Made: {status['decisions_made']}")

    if 'context' in status:
        print("\n💾 Context Manager:")
        print(f"   Total Items: {status['context']['total_items']}")
        print(f"   Total Tokens: {status['context']['total_tokens']}")

    print("\n" + "=" * 70)
    print("🎯 AUTONOMOUS WORKFLOW STARTED!")
    print("=" * 70)
    print("\nThe YOLO system is now running autonomously.")
    print("It will:")
    print("  1. Make decisions automatically")
    print("  2. Hand off work between agents")
    print("  3. Manage context intelligently")
    print("  4. Fix RuleIQ priority issues")
    print("\nMonitor progress with: python3 monitor.py")
    print("=" * 70)

    # Save state
    orchestrator._save_state()

    return orchestrator

if __name__ == "__main__":
    orchestrator = asyncio.run(activate_and_start())
