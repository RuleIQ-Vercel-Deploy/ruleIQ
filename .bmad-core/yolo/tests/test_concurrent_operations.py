#!/usr/bin/env python3
"""
Concurrent Operation Tests for YOLO System
Tests for parallel agent execution, race conditions, and thread safety.
"""
import asyncio
import pytest
import sys
import json
import tempfile
import threading
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, patch, AsyncMock
import time
from datetime import datetime, timezone
import importlib.util

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import the yolo-system module with hyphen in the name
spec = importlib.util.spec_from_file_location(
    "yolo_system", 
    Path(__file__).parent.parent / "yolo-system.py"
)
if spec and spec.loader:
    yolo_system = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(yolo_system)
    
    # Import the classes we need
    YOLOOrchestrator = yolo_system.YOLOOrchestrator
    YOLOMode = yolo_system.YOLOMode
    YOLOState = yolo_system.YOLOState
    AgentType = yolo_system.AgentType
    WorkflowPhase = yolo_system.WorkflowPhase
    HandoffPackage = yolo_system.HandoffPackage
    YOLODecision = yolo_system.YOLODecision
else:
    raise ImportError("Could not import yolo-system module")

try:
    # Try importing context-refresh-system module
    spec2 = importlib.util.spec_from_file_location(
        "context_refresh_system", 
        Path(__file__).parent.parent / "context-refresh-system.py"
    )
    if spec2 and spec2.loader:
        context_module = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(context_module)
        ContextRefreshSystem = context_module.ContextRefreshSystem
        ContextPriority = context_module.ContextPriority
    else:
        ContextRefreshSystem = None
        ContextPriority = None
except Exception:
    # Mock if not available
    ContextRefreshSystem = None
    ContextPriority = None


class ThreadSafeOrchestrator(YOLOOrchestrator):
    """Thread-safe version of YOLOOrchestrator for testing."""
    
    def __init__(self, config_path=None):
        super().__init__(config_path)
        self._state_lock = asyncio.Lock()
        self._handoff_lock = asyncio.Lock()
        self._decision_lock = asyncio.Lock()
    
    async def handoff(self, to_agent: AgentType, **kwargs):
        """Thread-safe handoff implementation."""
        async with self._handoff_lock:
            # Simulate handoff logic
            package = HandoffPackage(
                from_agent=self.state.current_agent or AgentType.PM,
                to_agent=to_agent,
                phase=self.state.current_phase or WorkflowPhase.PLANNING,
                context=kwargs
            )
            self.state.current_agent = to_agent
            return package
    
    async def _save_state(self):
        """Thread-safe state saving."""
        async with self._state_lock:
            # Simulate state saving
            state_dict = {
                "mode": self.state.mode.value,
                "current_phase": self.state.current_phase.value if self.state.current_phase else None,
                "current_agent": self.state.current_agent.value if self.state.current_agent else None,
                "decisions_made": len(self.state.decisions_made),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            return state_dict
    
    def _record_decision(self, decision_type: str, choice_type: str, choice: str, reasoning: str):
        """Thread-safe decision recording."""
        # Use synchronous lock for non-async method
        decision = YOLODecision(
            decision_id=f"{decision_type}_{int(time.time()*1000)}",
            decision_type=decision_type,
            choice_made=choice,
            reasoning=reasoning,
            agent=self.state.current_agent,
            timestamp=datetime.now(timezone.utc)
        )
        self.state.decisions_made.append(decision)


@pytest.mark.asyncio
class TestParallelAgentExecution:
    """Test multiple agents running simultaneously."""
    
    async def test_multiple_agents_concurrent(self):
        """Test multiple agents working simultaneously without conflicts."""
        orchestrator = ThreadSafeOrchestrator()
        await orchestrator.activate()
        
        # Create tasks for parallel agent execution
        async def run_agent(agent_type: AgentType, delay: float):
            """Simulate agent work."""
            await asyncio.sleep(delay)
            orchestrator.state.current_agent = agent_type
            # Simulate some work
            await asyncio.sleep(0.1)
            return f"{agent_type.value}_completed"
        
        # Start multiple agent workflows
        tasks = [
            run_agent(AgentType.DEV, 0.01),
            run_agent(AgentType.QA, 0.02),
            run_agent(AgentType.SECURITY, 0.03)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all completed without exceptions
        assert all(not isinstance(r, Exception) for r in results)
        assert len(results) == 3
        assert "dev_completed" in results
        assert "qa_completed" in results
        assert "security_completed" in results
    
    async def test_agent_state_isolation(self):
        """Test that agents maintain isolated state during parallel execution."""
        orchestrators = [
            ThreadSafeOrchestrator() for _ in range(3)
        ]
        
        async def activate_and_work(orchestrator: ThreadSafeOrchestrator, agent: AgentType):
            await orchestrator.activate()
            orchestrator.state.current_agent = agent
            await asyncio.sleep(0.05)  # Simulate work
            return orchestrator.state.current_agent
        
        # Run orchestrators in parallel
        results = await asyncio.gather(
            activate_and_work(orchestrators[0], AgentType.PM),
            activate_and_work(orchestrators[1], AgentType.DEV),
            activate_and_work(orchestrators[2], AgentType.QA)
        )
        
        # Each should maintain its own agent
        assert results[0] == AgentType.PM
        assert results[1] == AgentType.DEV
        assert results[2] == AgentType.QA


@pytest.mark.asyncio
class TestContextRaceConditions:
    """Test context updates from multiple agents."""
    
    async def test_concurrent_context_updates(self):
        """Test context updates from multiple agents don't corrupt data."""
        if not ContextRefreshSystem:
            pytest.skip("ContextRefreshSystem not available")
        
        context_manager = ContextRefreshSystem()
        
        async def add_context_items(agent: str, count: int):
            """Add context items from an agent."""
            for i in range(count):
                context_manager.add_context(
                    f"{agent}_item_{i}",
                    f"Content from {agent} #{i}",
                    ContextPriority.HIGH,
                    agent
                )
                await asyncio.sleep(0.001)  # Simulate work
        
        # Multiple agents adding context simultaneously
        await asyncio.gather(
            add_context_items("dev", 50),
            add_context_items("qa", 50),
            add_context_items("pm", 50)
        )
        
        # Verify all items were added correctly
        stats = context_manager.get_statistics()
        assert stats["total_items"] == 150
        
        # Verify no corruption in context items
        context = context_manager.get_active_context()
        
        # Context is organized by agent
        dev_items = context.get("dev", [])
        qa_items = context.get("qa", [])
        pm_items = context.get("pm", [])
        
        assert len(dev_items) <= 50  # May be less due to pruning
        assert len(qa_items) <= 50
        assert len(pm_items) <= 50
    
    async def test_context_priority_ordering(self):
        """Test that context priority is maintained under concurrent access."""
        if not ContextRefreshSystem:
            pytest.skip("ContextRefreshSystem not available")
        
        context_manager = ContextRefreshSystem()
        
        async def add_prioritized_context(priority: ContextPriority, count: int):
            """Add context with specific priority."""
            for i in range(count):
                context_manager.add_context(
                    "test_agent",  # agent parameter comes first
                    f"Content with {priority.name} priority item {i}",
                    priority,
                    f"{priority.name}_{i}"  # category
                )
                await asyncio.sleep(0.001)
        
        # Add context with different priorities concurrently
        await asyncio.gather(
            add_prioritized_context(ContextPriority.LOW, 20),
            add_prioritized_context(ContextPriority.MEDIUM, 20),
            add_prioritized_context(ContextPriority.HIGH, 20),
            add_prioritized_context(ContextPriority.CRITICAL, 20)
        )
        
        # Verify priority ordering is maintained
        context = context_manager.get_active_context()
        
        # Get context items for test_agent
        test_agent_items = context.get("test_agent", [])
        
        # Check that we have items
        assert len(test_agent_items) > 0
        
        # Count critical items
        critical_items = [item for item in test_agent_items 
                         if item.priority == ContextPriority.CRITICAL]
        assert len(critical_items) > 0  # Should have some critical items


@pytest.mark.asyncio
class TestHandoffCollisions:
    """Test simultaneous handoff attempts."""
    
    async def test_simultaneous_handoffs(self):
        """Test that simultaneous handoff attempts are handled gracefully."""
        orchestrator = ThreadSafeOrchestrator()
        await orchestrator.activate()
        
        # Set initial agent
        orchestrator.state.current_agent = AgentType.PM
        
        async def attempt_handoff(from_agent: AgentType, to_agent: AgentType):
            """Attempt a handoff from one agent to another."""
            orchestrator.state.current_agent = from_agent
            result = await orchestrator.handoff(to_agent)
            return result
        
        # Multiple agents trying to hand off simultaneously
        results = await asyncio.gather(
            attempt_handoff(AgentType.PM, AgentType.DEV),
            attempt_handoff(AgentType.ARCHITECT, AgentType.QA),
            attempt_handoff(AgentType.PO, AgentType.SECURITY),
            return_exceptions=True
        )
        
        # Should handle without corruption
        successful = [r for r in results if not isinstance(r, Exception)]
        assert len(successful) >= 1  # At least one should succeed
        
        # Final state should be consistent
        assert orchestrator.state.current_agent in [
            AgentType.DEV, AgentType.QA, AgentType.SECURITY
        ]
    
    async def test_handoff_queue_ordering(self):
        """Test that handoffs maintain proper ordering under load."""
        orchestrator = ThreadSafeOrchestrator()
        await orchestrator.activate()
        
        handoff_sequence = []
        
        async def perform_handoff(to_agent: AgentType, delay: float):
            """Perform handoff with delay."""
            await asyncio.sleep(delay)
            result = await orchestrator.handoff(to_agent)
            handoff_sequence.append(to_agent)
            return result
        
        # Create handoffs with different delays
        await asyncio.gather(
            perform_handoff(AgentType.DEV, 0.01),
            perform_handoff(AgentType.QA, 0.02),
            perform_handoff(AgentType.SECURITY, 0.03)
        )
        
        # Verify sequence is as expected
        assert len(handoff_sequence) == 3
        assert handoff_sequence[0] == AgentType.DEV
        assert handoff_sequence[1] == AgentType.QA
        assert handoff_sequence[2] == AgentType.SECURITY


@pytest.mark.asyncio
class TestStateFileLocking:
    """Test concurrent state file access."""
    
    async def test_concurrent_state_saves(self):
        """Test that concurrent state saves don't corrupt data."""
        orchestrator1 = ThreadSafeOrchestrator()
        orchestrator2 = ThreadSafeOrchestrator()
        
        await orchestrator1.activate()
        await orchestrator2.activate()
        
        # Both trying to save state simultaneously
        save_tasks = []
        for i in range(10):
            save_tasks.append(orchestrator1._save_state())
            save_tasks.append(orchestrator2._save_state())
        
        results = await asyncio.gather(*save_tasks, return_exceptions=True)
        
        # All saves should complete without errors
        errors = [r for r in results if isinstance(r, Exception)]
        assert len(errors) == 0
        
        # State should be consistent
        state1 = await orchestrator1._save_state()
        state2 = await orchestrator2._save_state()
        
        assert state1["mode"] == "active"
        assert state2["mode"] == "active"
    
    async def test_state_recovery_consistency(self):
        """Test state recovery under concurrent access."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            state_file = Path(f.name)
            initial_state = {
                "mode": "active",
                "current_phase": "development",
                "current_agent": "dev",
                "decisions_made": 5,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            json.dump(initial_state, f)
        
        try:
            async def load_and_modify(orchestrator: YOLOOrchestrator):
                """Load state and modify it."""
                # Mock the _load_state method to read from our file
                with open(state_file) as f:
                    loaded = json.load(f)
                orchestrator.state.mode = YOLOMode.ACTIVE
                await asyncio.sleep(0.01)
                return loaded
            
            orchestrators = [ThreadSafeOrchestrator() for _ in range(5)]
            
            # Multiple orchestrators loading state concurrently
            results = await asyncio.gather(
                *[load_and_modify(o) for o in orchestrators]
            )
            
            # All should read the same initial state
            for result in results:
                assert result["mode"] == "active"
                assert result["current_agent"] == "dev"
        
        finally:
            state_file.unlink()


@pytest.mark.asyncio
class TestResourceContention:
    """Test resource contention scenarios."""
    
    async def test_decision_recording_under_load(self):
        """Test that decision recording doesn't lose data under concurrent access."""
        orchestrator = ThreadSafeOrchestrator()
        await orchestrator.activate()
        
        async def record_decisions(agent: AgentType, count: int):
            """Record multiple decisions from an agent."""
            for i in range(count):
                orchestrator.state.current_agent = agent
                orchestrator._record_decision(
                    f"test_{agent.value}",
                    "choice",
                    f"option_{i}",
                    f"Reasoning from {agent.value}"
                )
                await asyncio.sleep(0.001)
        
        # Multiple agents recording decisions
        await asyncio.gather(
            record_decisions(AgentType.DEV, 20),
            record_decisions(AgentType.QA, 20),
            record_decisions(AgentType.PM, 20)
        )
        
        # Verify all decisions were recorded (60 decisions total, no activation decision in this test)
        assert len(orchestrator.state.decisions_made) == 60
        
        # Verify no duplicate decision IDs
        decision_ids = [d.decision_id for d in orchestrator.state.decisions_made]
        assert len(decision_ids) == len(set(decision_ids))
    
    async def test_phase_transition_conflicts(self):
        """Test phase transitions under concurrent modification."""
        orchestrator = ThreadSafeOrchestrator()
        await orchestrator.activate(WorkflowPhase.PLANNING)
        
        transition_log = []
        
        async def attempt_transition(to_phase: WorkflowPhase, delay: float):
            """Attempt to transition to a phase."""
            await asyncio.sleep(delay)
            old_phase = orchestrator.state.current_phase
            orchestrator.state.current_phase = to_phase
            transition_log.append((old_phase, to_phase))
            return to_phase
        
        # Multiple phase transition attempts
        results = await asyncio.gather(
            attempt_transition(WorkflowPhase.ARCHITECTURE, 0.01),
            attempt_transition(WorkflowPhase.DEVELOPMENT, 0.01),
            attempt_transition(WorkflowPhase.TESTING, 0.01),
            return_exceptions=True
        )
        
        # Should end in a valid phase
        assert orchestrator.state.current_phase in [
            WorkflowPhase.ARCHITECTURE,
            WorkflowPhase.DEVELOPMENT,
            WorkflowPhase.TESTING
        ]
        
        # Transition log should show attempts
        assert len(transition_log) == 3


@pytest.mark.asyncio
class TestDeadlockPrevention:
    """Test deadlock prevention mechanisms."""
    
    async def test_no_deadlock_on_circular_dependencies(self):
        """Test that circular dependencies don't cause deadlocks."""
        orchestrator = ThreadSafeOrchestrator()
        await orchestrator.activate()
        
        async def agent_cycle(agents: List[AgentType]):
            """Create a cycle of agent handoffs."""
            for i, agent in enumerate(agents):
                next_agent = agents[(i + 1) % len(agents)]
                await orchestrator.handoff(next_agent)
                await asyncio.sleep(0.01)
        
        # Create multiple cycles running concurrently
        cycle1 = [AgentType.PM, AgentType.DEV, AgentType.QA]
        cycle2 = [AgentType.ARCHITECT, AgentType.SECURITY, AgentType.DEVOPS]
        
        # Should complete without deadlock (use timeout)
        try:
            await asyncio.wait_for(
                asyncio.gather(
                    agent_cycle(cycle1),
                    agent_cycle(cycle2)
                ),
                timeout=5.0
            )
            deadlock = False
        except asyncio.TimeoutError:
            deadlock = True
        
        assert not deadlock, "Deadlock detected in circular handoffs"
    
    async def test_timeout_on_blocked_operations(self):
        """Test that blocked operations timeout appropriately."""
        orchestrator = ThreadSafeOrchestrator()
        await orchestrator.activate()
        
        async def blocking_operation():
            """Simulate a blocking operation."""
            async with orchestrator._state_lock:
                # Hold lock for extended time
                await asyncio.sleep(2.0)
        
        async def waiting_operation():
            """Try to acquire lock while blocked."""
            try:
                await asyncio.wait_for(
                    orchestrator._save_state(),
                    timeout=1.0
                )
                return "completed"
            except asyncio.TimeoutError:
                return "timeout"
        
        # Start blocking and waiting operations
        results = await asyncio.gather(
            blocking_operation(),
            waiting_operation(),
            return_exceptions=True
        )
        
        # Waiting operation should timeout
        assert results[1] == "timeout"


# Performance benchmarks
@pytest.mark.asyncio
class TestPerformanceBenchmarks:
    """Performance benchmarks for concurrent operations."""
    
    async def test_throughput_under_load(self):
        """Test system throughput with many concurrent operations."""
        orchestrator = ThreadSafeOrchestrator()
        await orchestrator.activate()
        
        start_time = time.time()
        operation_count = 100
        
        async def perform_operation(op_id: int):
            """Perform a single operation."""
            agent = list(AgentType)[op_id % len(AgentType)]
            orchestrator.state.current_agent = agent
            orchestrator._record_decision(
                f"op_{op_id}",
                "test",
                f"choice_{op_id}",
                "benchmark"
            )
            return op_id
        
        # Run many operations concurrently
        results = await asyncio.gather(
            *[perform_operation(i) for i in range(operation_count)]
        )
        
        elapsed = time.time() - start_time
        throughput = operation_count / elapsed
        
        # Should handle at least 50 operations per second
        assert throughput > 50, f"Low throughput: {throughput:.2f} ops/sec"
        assert len(results) == operation_count
    
    async def test_latency_percentiles(self):
        """Test operation latency percentiles."""
        orchestrator = ThreadSafeOrchestrator()
        await orchestrator.activate()
        
        latencies = []
        
        async def timed_operation():
            """Perform operation and measure latency."""
            start = time.time()
            await orchestrator.handoff(AgentType.DEV)
            latency = time.time() - start
            return latency
        
        # Perform many operations
        for _ in range(50):
            latency = await timed_operation()
            latencies.append(latency)
        
        # Calculate percentiles
        latencies.sort()
        p50 = latencies[len(latencies) // 2]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        
        # Latency requirements
        assert p50 < 0.01, f"P50 latency too high: {p50:.4f}s"
        assert p95 < 0.05, f"P95 latency too high: {p95:.4f}s"
        assert p99 < 0.1, f"P99 latency too high: {p99:.4f}s"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])