#!/usr/bin/env python3
"""
Start the autonomous YOLO workflow for RuleIQ.
"""
import asyncio
import json
import importlib.util
from datetime import datetime

# Load YOLO system
spec = importlib.util.spec_from_file_location('yolo_system', 'yolo-system.py')
yolo_system = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yolo_system)

async def start_ruleiq_workflow():
    """Start the RuleIQ autonomous workflow."""
    print("🚀 STARTING RULEIQ AUTONOMOUS WORKFLOW")
    print("=" * 70)
    
    # Load existing state or create new orchestrator
    orchestrator = yolo_system.YOLOOrchestrator()
    
    # Ensure YOLO is active
    if orchestrator.state.mode != yolo_system.YOLOMode.ACTIVE:
        await orchestrator.activate()
    
    # Initial context for RuleIQ project
    initial_context = {
        "project": "RuleIQ Compliance Automation Platform",
        "current_sprint": "Sprint 0 - Foundation",
        "priority_tasks": [
            "P0: Backend test pass rate to 95%",
            "P0: Fix authentication flow",
            "P0: Resolve API routing issues",
            "P1: Frontend hydration fixes",
            "P1: Complete test coverage"
        ],
        "tech_stack": {
            "backend": "Python/FastAPI",
            "frontend": "Next.js/React",
            "database": "PostgreSQL with pgvector",
            "testing": "pytest/playwright"
        },
        "current_story": "S0-1.2 Agent Orchestrator Foundation",
        "acceptance_criteria": [
            "Create service layer for agents",
            "Implement handoff mechanism",
            "Add monitoring capabilities",
            "Setup error recovery"
        ]
    }
    
    # Add context to manager
    if orchestrator.context_manager:
        for key, value in initial_context.items():
            priority = yolo_system.ContextPriority.CRITICAL if key in ["priority_tasks", "current_story"] else yolo_system.ContextPriority.HIGH
            orchestrator.context_manager.add_context(
                key, json.dumps(value) if isinstance(value, (dict, list)) else value,
                priority, "pm"
            )
    
    # Set PM as current agent
    orchestrator.state.current_agent = yolo_system.AgentType.PM
    orchestrator.state.current_phase = yolo_system.WorkflowPhase.PLANNING
    
    # Create first handoff: PM → Architect
    print("\n📋 Creating Initial Handoff: PM → ARCHITECT")
    
    # PM makes initial decisions
    decisions = {}
    decision_points = [
        ("architecture_pattern", ["microservices", "monolith", "modular_monolith"]),
        ("testing_strategy", ["TDD", "BDD", "integration_first"]),
        ("deployment_approach", ["containers", "serverless", "traditional"])
    ]
    
    for decision_type, options in decision_points:
        if not decision_type.startswith("deployment"):  # Skip safety-critical
            decision = orchestrator.make_decision(decision_type, options, initial_context)
            decisions[decision_type] = decision
            print(f"   • {decision_type}: {decision}")
    
    # Create handoff package
    handoff = await orchestrator.handoff(
        to_agent=yolo_system.AgentType.ARCHITECT,
        artifacts={
            "requirements": ["PRD_draft.md", "user_stories.md"],
            "decisions": [f"{k}={v}" for k, v in decisions.items()]
        },
        context=initial_context
    )
    
    print(f"\n✅ Handoff created successfully!")
    print(f"   From: {handoff.from_agent.value}")
    print(f"   To: {handoff.to_agent.value}")
    print(f"   Context items: {len(handoff.context)}")
    print(f"   YOLO mode: {'ACTIVE' if handoff.yolo_mode else 'INACTIVE'}")
    
    # Show current status
    status = orchestrator.get_status()
    print(f"\n📊 Current Status:")
    print(f"   Phase: {status['phase']}")
    print(f"   Current Agent: {status['current_agent']}")
    print(f"   Next Agent: {status.get('next_agent', 'TBD')}")
    print(f"   Decisions Made: {status['decisions_made']}")
    
    if 'context' in status:
        print(f"\n💾 Context Manager:")
        print(f"   Total Items: {status['context']['total_items']}")
        print(f"   Total Tokens: {status['context']['total_tokens']}")
    
    print("\n" + "=" * 70)
    print("🎯 WORKFLOW INITIATED - AUTONOMOUS OPERATION IN PROGRESS")
    print("The system will continue making decisions and managing handoffs automatically.")
    print("=" * 70)
    
    # Save state
    orchestrator._save_state()
    
    return handoff

if __name__ == "__main__":
    handoff = asyncio.run(start_ruleiq_workflow())
    print(f"\n📦 Next Action: {handoff.next_action}")
    print("YOLO system is now running autonomously with context refresh enabled!")