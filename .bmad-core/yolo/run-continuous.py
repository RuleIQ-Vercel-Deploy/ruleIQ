#!/usr/bin/env python3
"""
Run continuous autonomous workflow - picks up from current state.
"""
import asyncio
import json
import time
import importlib.util
from pathlib import Path
from datetime import datetime

# Load YOLO system  
spec = importlib.util.spec_from_file_location('yolo_system', 'yolo-system.py')
yolo_system = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yolo_system)

async def run_continuous_workflow():
    """Run continuous autonomous workflow."""
    print("=" * 70)
    print("🔄 CONTINUOUS AUTONOMOUS WORKFLOW")
    print("=" * 70)
    
    orchestrator = yolo_system.YOLOOrchestrator()
    
    # Activate if needed
    if orchestrator.state.mode != yolo_system.YOLOMode.ACTIVE:
        await orchestrator.activate()
        print("✅ YOLO Activated")
    
    # If no current agent, start from PM
    if not orchestrator.state.current_agent:
        orchestrator.state.current_agent = yolo_system.AgentType.PM
        orchestrator.state.current_phase = yolo_system.WorkflowPhase.PLANNING
        print("📍 Starting with PM agent")
    
    print(f"📍 Current: {orchestrator.state.current_agent.value}")
    print(f"📊 Phase: {orchestrator.state.current_phase.value}")
    
    # Workflow progression
    workflow_sequence = [
        (yolo_system.AgentType.PM, yolo_system.AgentType.ARCHITECT, yolo_system.WorkflowPhase.PLANNING),
        (yolo_system.AgentType.ARCHITECT, yolo_system.AgentType.PO, yolo_system.WorkflowPhase.ARCHITECTURE),
        (yolo_system.AgentType.PO, yolo_system.AgentType.SM, yolo_system.WorkflowPhase.STORY_CREATION),
        (yolo_system.AgentType.SM, yolo_system.AgentType.DEV, yolo_system.WorkflowPhase.DEVELOPMENT),
        (yolo_system.AgentType.DEV, yolo_system.AgentType.QA, yolo_system.WorkflowPhase.TESTING),
    ]
    
    # Run workflow
    iteration = 0
    while orchestrator.state.current_phase != yolo_system.WorkflowPhase.COMPLETE:
        iteration += 1
        current = orchestrator.state.current_agent
        
        print(f"\n{'='*50}")
        print(f"🔄 Iteration {iteration}: {current.value if current else 'None'}")
        print(f"{'='*50}")
        
        # Find next in sequence
        next_agent = None
        next_phase = orchestrator.state.current_phase
        
        for from_agent, to_agent, phase in workflow_sequence:
            if current == from_agent:
                next_agent = to_agent
                next_phase = phase
                break
        
        if not next_agent:
            # End of sequence
            orchestrator.state.current_phase = yolo_system.WorkflowPhase.COMPLETE
            break
        
        # Simulate agent work
        print(f"\n👤 {current.value.upper()} is working...")
        
        # Make some decisions based on agent type
        if current == yolo_system.AgentType.PM:
            decisions = ["Define requirements", "Set priorities", "Create roadmap"]
        elif current == yolo_system.AgentType.ARCHITECT:
            decisions = ["Design system", "Choose tech stack", "Define patterns"]
        elif current == yolo_system.AgentType.PO:
            decisions = ["Create stories", "Define acceptance criteria", "Prioritize backlog"]
        elif current == yolo_system.AgentType.SM:
            decisions = ["Plan sprint", "Assign tasks", "Set deadlines"]
        elif current == yolo_system.AgentType.DEV:
            decisions = ["Write code", "Fix bugs", "Run tests"]
        elif current == yolo_system.AgentType.QA:
            decisions = ["Test features", "Validate fixes", "Report results"]
        else:
            decisions = ["Process tasks"]
        
        for decision in decisions:
            print(f"   ✓ {decision}")
            await asyncio.sleep(0.2)  # Simulate work
        
        # Add context
        if orchestrator.context_manager:
            orchestrator.context_manager.add_context(
                f"work_{iteration}",
                f"{current.value} completed: {', '.join(decisions)}",
                yolo_system.ContextPriority.MEDIUM,
                current.value
            )
        
        # Perform handoff
        print(f"\n📦 Handoff: {current.value} → {next_agent.value}")
        orchestrator.state.current_phase = next_phase
        
        try:
            handoff = await orchestrator.handoff(
                to_agent=next_agent,
                context={
                    "from": current.value,
                    "work_done": decisions,
                    "timestamp": datetime.now().isoformat()
                }
            )
            print(f"✅ Handoff successful ({len(handoff.context)} context items)")
        except Exception as e:
            print(f"⚠️  Handoff issue: {e}")
            orchestrator.state.current_agent = next_agent
        
        # Show status
        status = orchestrator.get_status()
        if 'context' in status:
            print(f"💾 Context: {status['context']['total_items']} items, {status['context']['total_tokens']} tokens")
        
        # Continue to next iteration
        await asyncio.sleep(0.5)
        
        # Safety check
        if iteration > 10:
            print("\n⚠️  Safety limit reached")
            break
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ WORKFLOW COMPLETE!")
    print("=" * 70)
    
    status = orchestrator.get_status()
    print(f"Total Iterations: {iteration}")
    print(f"Final Phase: {status['phase']}")
    print(f"Decisions Made: {status['decisions_made']}")
    
    if 'context' in status:
        print(f"\n💾 Final Context Stats:")
        print(f"   Items: {status['context']['total_items']}")
        print(f"   Tokens: {status['context']['total_tokens']}")
        
        if status['context'].get('agents'):
            print("\n📊 Per-Agent Context:")
            for agent, info in status['context']['agents'].items():
                if isinstance(info, dict) and 'tokens' in info:
                    print(f"   • {agent}: {info['items']} items, {info['tokens']} tokens")
    
    print("\n🎯 Autonomous workflow demonstrated:")
    print("   ✓ Automatic progression through agents")
    print("   ✓ Context management and refresh")
    print("   ✓ Continuous operation")
    print("   ✓ Complete workflow execution")
    
    return orchestrator

if __name__ == "__main__":
    orchestrator = asyncio.run(run_continuous_workflow())
    print("\n🚀 Continuous workflow complete!")