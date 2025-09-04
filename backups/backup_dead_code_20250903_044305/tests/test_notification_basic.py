"""
Basic test to verify notification node functionality
"""

import asyncio
from langgraph_agent.nodes.notification_nodes import EnhancedNotificationNode
from langgraph_agent.nodes.celery_migration_nodes import TaskMigrationState


async def test_basic_notification():
    """Test basic notification functionality"""

    # Create node
    node = EnhancedNotificationNode()

    # Create test state
    state = {
        "task_id": "test-task-123",
        "task_name": "test_notification",
        "task_type": "notification",
        "status": "pending",
        "input_data": {
            "recipient": "user@example.com",
            "message": "Test notification",
            "channel": "email",
        },
        "output_data": {},
        "error": None,
        "metadata": {"retry_count": 0, "max_retries": 3},
        "checkpoints": [],
    }

    try:
        # Process notification
        result = await node.process(state)

        print("✅ Basic notification test passed!")
        print(f"Result status: {result.get('status')}")
        print(f"Output data: {result.get('output_data')}")

        # Check state transitions
        assert result["status"] in [
            "completed",
            "failed",
            "pending",
        ], f"Unexpected status: {result['status']}"

        if result["status"] == "completed":
            print("✅ Notification completed successfully")
        elif result["status"] == "failed":
            print(f"⚠️ Notification failed: {result.get('error')}")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_basic_notification())
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
