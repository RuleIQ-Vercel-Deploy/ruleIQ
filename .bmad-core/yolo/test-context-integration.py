#!/usr/bin/env python3
"""
Test script to verify YOLO and Context Refresh integration.
"""
import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

import importlib.util

# Load the yolo-system module with hyphen in name
spec = importlib.util.spec_from_file_location("yolo_system", "yolo-system.py")
yolo_system = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yolo_system)

YOLOOrchestrator = yolo_system.YOLOOrchestrator
AgentType = yolo_system.AgentType


async def test_integration():
    """Test YOLO with context refresh integration."""
    print("=" * 60)
    print("Testing YOLO + Context Refresh Integration")
    print("=" * 60)

    # Initialize orchestrator
    orchestrator = YOLOOrchestrator()

    # Check if context manager is available
    if orchestrator.context_manager:
        print("✅ Context refresh system integrated successfully")
    else:
        print("⚠️  Context refresh system not available")

    # Activate YOLO mode
    await orchestrator.activate()
    print("✅ YOLO mode activated")

    # Test context during handoff
    print("\n📋 Testing handoff with context refresh...")

    # Simulate some context
    test_context = {
        "current_task": "Implement user authentication",
        "requirements": ["JWT tokens", "Password hashing", "Email verification"],
        "completed_steps": ["Database schema created", "API endpoints defined"],
        "pending_items": ["Frontend forms", "Email service integration"],
        "notes": "Using FastAPI with SQLAlchemy for backend"
    }

    # Create handoff from PM to Architect
    orchestrator.state.current_agent = AgentType.PM
    package = await orchestrator.handoff(
        to_agent=AgentType.ARCHITECT,
        artifacts={"documents": ["PRD.md", "requirements.txt"]},
        context=test_context
    )

    print(f"✅ Handoff created from {package.from_agent.value} to {package.to_agent.value}")
    print(f"   Context items: {len(package.context)}")

    # Get status with context info
    status = orchestrator.get_status()
    print("\n📊 YOLO Status with Context:")
    print(json.dumps(status, indent=2, default=str))

    # Test decision making
    print("\n🤖 Testing automated decision making...")
    decision = orchestrator.make_decision(
        "framework_choice",
        ["FastAPI", "Django", "Flask"],
        context={"requirements": "Need async support and OpenAPI docs"}
    )
    print(f"✅ Decision made: {decision}")

    # Simulate handoff to Dev
    package = await orchestrator.handoff(
        to_agent=AgentType.DEV,
        artifacts={"designs": ["architecture.md", "api_spec.yaml"]},
        context={"framework": decision, "previous_context": test_context}
    )
    print(f"✅ Handoff to {package.to_agent.value} with refreshed context")

    # Final status
    final_status = orchestrator.get_status()
    if "context" in final_status:
        print("\n📈 Context Manager Stats:")
        print(f"   Total items: {final_status['context'].get('total_items', 0)}")
        print(f"   Total tokens: {final_status['context'].get('total_tokens', 0)}")
        if final_status['context'].get('agents'):
            for agent, info in final_status['context']['agents'].items():
                print(f"   {agent}: {info['tokens']} tokens, {info['items']} items")

    # Deactivate
    orchestrator.deactivate()
    print("\n✅ Test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_integration())
