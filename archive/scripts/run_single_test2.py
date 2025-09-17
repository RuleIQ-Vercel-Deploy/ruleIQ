#!/usr/bin/env python
"""Run individual test methods directly"""
import logging
logger = logging.getLogger(__name__)


import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tests.test_notification_migration_tdd import TestNotificationStateTransitions
from langgraph_agent.nodes.notification_nodes import EnhancedNotificationNode


async def main():
    """Run a single test method"""
    test_instance = TestNotificationStateTransitions()

    # Create node and base state
    notification_node = EnhancedNotificationNode()
    base_state = {
        "task_id": "test-123",
        "task_type": "compliance_alert",
        "task_status": "pending",
        "task_params": {},
        "retry_count": 0,
        "max_retries": 3,
    }

    logger.info("Testing: pending -> running state transition")
    try:
        await test_instance.test_state_transition_pending_to_running(
            notification_node, base_state
        )
        logger.info("✅ Test passed: pending -> running transition")
    except Exception as e:
        logger.info(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
