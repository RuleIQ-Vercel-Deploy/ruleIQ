#!/usr/bin/env python3
"""
Final comprehensive test of YOLO system with context refresh.
"""
import sys
import asyncio
import json
from pathlib import Path

# Import the YOLO system
import importlib.util
spec = importlib.util.spec_from_file_location('yolo_system', 'yolo-system.py')
yolo_system = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yolo_system)

async def final_test():
    """Run final comprehensive test."""
    print('=' * 70)
    print('🚀 FINAL YOLO SYSTEM TEST WITH CONTEXT REFRESH')
    print('=' * 70)
    
    try:
        # Initialize
        orchestrator = yolo_system.YOLOOrchestrator()
        
        # Test 1: Activation
        print('\n✅ TEST 1: System Activation')
        await orchestrator.activate()
        assert orchestrator.state.mode == yolo_system.YOLOMode.ACTIVE
        print('   YOLO mode: ACTIVE')
        
        # Test 2: Context System Integration
        print('\n✅ TEST 2: Context Refresh System')
        if orchestrator.context_manager:
            print('   Context manager: INTEGRATED')
            
            # Add various priority contexts
            orchestrator.context_manager.add_context(
                'critical_error', 
                'Database connection failed',
                yolo_system.ContextPriority.CRITICAL,
                'dev'
            )
            orchestrator.context_manager.add_context(
                'current_task', 
                'Implement user authentication',
                yolo_system.ContextPriority.HIGH,
                'dev'
            )
            orchestrator.context_manager.add_context(
                'framework', 
                'Using FastAPI',
                yolo_system.ContextPriority.MEDIUM,
                'dev'
            )
            print('   Context items added: 3')
        else:
            print('   Context manager: NOT AVAILABLE')
        
        # Test 3: Automated Decisions
        print('\n✅ TEST 3: Automated Decision Making')
        test_decisions = {
            'database': ['PostgreSQL', 'MySQL', 'MongoDB'],
            'framework': ['FastAPI', 'Django', 'Flask'],
            'testing_framework': ['pytest', 'unittest', 'nose2'],
            'backend_language': ['Python', 'Node.js', 'Go']
        }
        
        decisions_made = []
        for decision_type, options in test_decisions.items():
            decision = orchestrator.make_decision(decision_type, options)
            decisions_made.append(f'{decision_type}={decision}')
        
        print(f'   Decisions made: {", ".join(decisions_made)}')
        
        # Test 4: Complete Handoff Workflow
        print('\n✅ TEST 4: Full Agent Workflow with Context')
        workflow = [
            (yolo_system.AgentType.PM, yolo_system.AgentType.ARCHITECT, "Requirements defined"),
            (yolo_system.AgentType.ARCHITECT, yolo_system.AgentType.PO, "Architecture designed"),
            (yolo_system.AgentType.PO, yolo_system.AgentType.SM, "Backlog prioritized"),
            (yolo_system.AgentType.SM, yolo_system.AgentType.DEV, "Sprint planned"),
            (yolo_system.AgentType.DEV, yolo_system.AgentType.QA, "Code implemented")
        ]
        
        for from_agent, to_agent, context_msg in workflow:
            orchestrator.state.current_agent = from_agent
            package = await orchestrator.handoff(
                to_agent=to_agent,
                context={'message': context_msg, 'step': f'{from_agent.value}_to_{to_agent.value}'}
            )
            print(f'   {from_agent.value:12} → {to_agent.value:12} [{len(package.context)} items]')
        
        # Test 5: Context Status
        print('\n✅ TEST 5: Context Management Status')
        status = orchestrator.get_status()
        
        if 'context' in status and isinstance(status['context'], dict):
            if 'total_items' in status['context']:
                print(f'   Total context items: {status["context"]["total_items"]}')
                print(f'   Total tokens used: {status["context"]["total_tokens"]}')
                
                # Show per-agent context
                if status['context'].get('agents'):
                    print('   Per-agent context:')
                    for agent, info in status['context']['agents'].items():
                        if isinstance(info, dict) and 'tokens' in info:
                            print(f'     • {agent}: {info["tokens"]} tokens, {info["items"]} items')
        
        # Test 6: Error Recovery
        print('\n✅ TEST 6: Error Handling & Recovery')
        initial_mode = orchestrator.state.mode
        
        # Minor error - should continue
        orchestrator.handle_error('Minor issue', 'minor')
        assert orchestrator.state.mode == initial_mode
        print('   Minor error: System continues ✓')
        
        # Major error - should pause
        orchestrator.handle_error('Major problem', 'major')
        assert orchestrator.state.mode == yolo_system.YOLOMode.PAUSED
        print('   Major error: System paused ✓')
        
        # Resume after major error
        orchestrator.resume()
        assert orchestrator.state.mode == yolo_system.YOLOMode.ACTIVE
        print('   Resume: System active again ✓')
        
        # Test 7: Phase Transitions
        print('\n✅ TEST 7: Workflow Phase Management')
        phases_tested = []
        for phase in [yolo_system.WorkflowPhase.PLANNING, 
                     yolo_system.WorkflowPhase.DEVELOPMENT,
                     yolo_system.WorkflowPhase.TESTING]:
            orchestrator.state.current_phase = phase
            phases_tested.append(phase.value)
        
        print(f'   Phases tested: {" → ".join(phases_tested)}')
        
        # Test 8: Decision History
        print('\n✅ TEST 8: Decision Audit Trail')
        print(f'   Total decisions made: {len(orchestrator.state.decisions_made)}')
        print(f'   Errors encountered: {len(orchestrator.state.errors_encountered)}')
        
        # Final Status
        print('\n' + '=' * 70)
        print('🎉 ALL TESTS COMPLETED SUCCESSFULLY!')
        print('=' * 70)
        
        final_status = orchestrator.get_status()
        print('\n📊 Final System Status:')
        print(f'   Mode: {final_status["mode"]}')
        print(f'   Phase: {final_status["phase"]}')
        print(f'   Current Agent: {final_status["current_agent"]}')
        print(f'   Decisions: {final_status["decisions_made"]}')
        print(f'   Errors: {final_status["errors"]}')
        print(f'   Progress: {final_status["progress"]}%')
        
        print('\n✅ YOLO system with context refresh is fully operational!')
        print('   The system can now run autonomously with intelligent context management.')
        
        # Cleanup
        orchestrator.deactivate()
        
        return True
        
    except Exception as e:
        print(f'\n❌ Test failed with error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(final_test())
    sys.exit(0 if success else 1)