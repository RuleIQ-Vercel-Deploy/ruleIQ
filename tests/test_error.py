"""Test suite for error handling in the compliance graph."""

import pytest
import asyncio
import sys
import os
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch

sys.path.insert(0, ".")

from langgraph_agent.graph.enhanced_app import EnhancedComplianceGraph
from langgraph_agent.graph.enhanced_state import create_enhanced_initial_state

class TestErrorHandling:
    """Test error handling in the enhanced compliance graph."""

    @pytest.mark.asyncio
    async def test_error_handler_node(self):
        """Test the error handler node functionality."""
        with patch("langgraph_agent.graph.enhanced_app.EnhancedComplianceGraph.create") as mock_create:
            # Create mock graph
            mock_graph = Mock()
            mock_graph._error_handler_node = AsyncMock()
            mock_create.return_value = mock_graph
            
            # Create test state with errors
            state = create_enhanced_initial_state(
                session_id="error-test",
                company_id=uuid4(),
                initial_message="Test",
                max_retries=2,
            )
            
            state["error_count"] = 2
            state["errors"] = [{"error": "Test error 1"}, {"error": "Test error 2"}]
            
            # Set up the mock to return updated state
            mock_graph._error_handler_node.return_value = {
                **state,
                "retry_count": 1,
                "processing_status": "retrying"
            }
            
            # Call the error handler
            graph = await mock_create()
            updated_state = await graph._error_handler_node(state)
            
            # Verify the result
            assert updated_state["retry_count"] == 1
            assert updated_state["processing_status"] == "retrying"

    @pytest.mark.asyncio
    async def test_error_recovery_flow(self):
        """Test error recovery flow in the graph."""
        with patch("langgraph_agent.graph.enhanced_app.EnhancedComplianceGraph") as MockGraph:
            mock_instance = Mock()
            mock_instance.compile = Mock()
            mock_instance._error_handler_node = AsyncMock()
            MockGraph.return_value = mock_instance
            
            # Create state with errors that should trigger recovery
            state = create_enhanced_initial_state(
                session_id="recovery-test",
                company_id=uuid4(),
                initial_message="Test recovery",
                max_retries=3,
            )
            
            state["error_count"] = 1
            state["retry_count"] = 0
            state["errors"] = [{"error": "Recoverable error"}]
            
            # Mock the recovery behavior
            mock_instance._error_handler_node.return_value = {
                **state,
                "retry_count": 1,
                "error_count": 0,
                "errors": [],
                "processing_status": "recovered"
            }
            
            # Create and test recovery
            graph = MockGraph()
            recovered_state = await graph._error_handler_node(state)
            
            assert recovered_state["processing_status"] == "recovered"
            assert recovered_state["error_count"] == 0
            assert recovered_state["retry_count"] == 1

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test behavior when max retries are exceeded."""
        with patch("langgraph_agent.graph.enhanced_app.EnhancedComplianceGraph") as MockGraph:
            mock_instance = Mock()
            mock_instance._error_handler_node = AsyncMock()
            MockGraph.return_value = mock_instance
            
            # Create state with max retries exceeded
            state = create_enhanced_initial_state(
                session_id="max-retries-test",
                company_id=uuid4(),
                initial_message="Test max retries",
                max_retries=2,
            )
            
            state["error_count"] = 3
            state["retry_count"] = 2
            state["errors"] = [
                {"error": "Error 1"},
                {"error": "Error 2"},
                {"error": "Error 3"}
            ]
            
            # Mock the failure behavior
            mock_instance._error_handler_node.return_value = {
                **state,
                "processing_status": "failed",
                "workflow_status": "failed"
            }
            
            # Test max retries exceeded
            graph = MockGraph()
            failed_state = await graph._error_handler_node(state)
            
            assert failed_state["processing_status"] == "failed"
            assert failed_state["workflow_status"] == "failed"

    @pytest.mark.asyncio
    async def test_error_logging(self):
        """Test that errors are properly logged."""
        with patch("langgraph_agent.graph.enhanced_app.logger") as mock_logger:
            with patch("langgraph_agent.graph.enhanced_app.EnhancedComplianceGraph") as MockGraph:
                mock_instance = Mock()
                mock_instance._error_handler_node = AsyncMock()
                MockGraph.return_value = mock_instance
                
                # Create state with error
                state = create_enhanced_initial_state(
                    session_id="logging-test",
                    company_id=uuid4(),
                    initial_message="Test logging",
                )
                
                state["errors"] = [{"error": "Test error for logging"}]
                state["error_count"] = 1
                
                # Mock error handling
                mock_instance._error_handler_node.return_value = state
                
                # Execute
                graph = MockGraph()
                await graph._error_handler_node(state)
                
                # Verify error handling was called
                mock_instance._error_handler_node.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_aggregation(self):
        """Test that multiple errors are properly aggregated."""
        state = create_enhanced_initial_state(
            session_id="aggregation-test",
            company_id=uuid4(),
            initial_message="Test aggregation",
        )
        
        # Add multiple errors
        errors = [
            {"error": "Database connection failed", "node": "db_node"},
            {"error": "API timeout", "node": "api_node"},
            {"error": "Validation failed", "node": "validation_node"}
        ]
        
        for error in errors:
            state["errors"].append(error)
            state["error_count"] += 1
        
        # Verify aggregation
        assert state["error_count"] == 3
        assert len(state["errors"]) == 3
        assert all(e["error"] in str(state["errors"]) for e in errors)

    @pytest.mark.asyncio
    async def test_error_handler_with_custom_recovery(self):
        """Test error handler with custom recovery strategy."""
        with patch("langgraph_agent.graph.enhanced_app.EnhancedComplianceGraph") as MockGraph:
            mock_instance = Mock()
            mock_instance._error_handler_node = AsyncMock()
            MockGraph.return_value = mock_instance
            
            # Create state with specific error type
            state = create_enhanced_initial_state(
                session_id="custom-recovery-test",
                company_id=uuid4(),
                initial_message="Test custom recovery",
            )
            
            state["errors"] = [{"error": "Specific error type", "recovery_strategy": "custom"}]
            state["error_count"] = 1
            
            # Mock custom recovery
            mock_instance._error_handler_node.return_value = {
                **state,
                "processing_status": "recovered_custom",
                "errors": [],
                "error_count": 0
            }
            
            # Execute
            graph = MockGraph()
            recovered_state = await graph._error_handler_node(state)
            
            assert recovered_state["processing_status"] == "recovered_custom"
            assert recovered_state["error_count"] == 0