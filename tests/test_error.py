import asyncio
import sys
import os

sys.path.insert(0, ".")

from langgraph_agent.graph.enhanced_app import EnhancedComplianceGraph
from langgraph_agent.graph.enhanced_state import create_enhanced_initial_state
from uuid import uuid4


async def test():
    try:
        graph = await EnhancedComplianceGraph.create()
        state = create_enhanced_initial_state(
            session_id="error-test",
            company_id=uuid4(),
            initial_message="Test",
            max_retries=2,
        )

        state["error_count"] = 2
        state["errors"] = [{"error": "Test error 1"}, {"error": "Test error 2"}]

        # Call the error handler
        updated_state = await graph._error_handler_node(state)
        print(f"Success! retry_count={updated_state['retry_count']}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


asyncio.run(test())
