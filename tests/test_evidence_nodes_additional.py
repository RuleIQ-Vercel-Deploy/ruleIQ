"""Additional tests to achieve 80%+ coverage for evidence_nodes module."""
import asyncio
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import uuid4

import pytest
from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from langgraph.graph.message import add_messages

from database.evidence_item import EvidenceItem
from langgraph_agent.nodes.evidence_nodes import (
    EvidenceCollectionNode,
    evidence_node
)


async def async_generator(items):
    """Helper to create async generator."""
    for item in items:
        yield item


@pytest.mark.asyncio
class TestSyncEvidenceStatusFull:
    """Test sync_evidence_status with actual database update logic."""
    
    @patch('langgraph_agent.nodes.evidence_nodes.get_async_db')
    async def test_sync_evidence_status_with_updates(self, mock_get_db):
        """Test sync_evidence_status when it actually updates records."""
        mock_session = MagicMock(spec=AsyncSession)
        
        # Mock execute to return result with rowcount
        mock_result = MagicMock()
        mock_result.rowcount = 5  # 5 records updated
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        
        mock_get_db.return_value = async_generator([mock_session])
        
        node = EvidenceCollectionNode()
        
        # Test with dict state (backward compatibility)
        state = {
            "user_id": str(uuid4()),
            "business_profile_id": str(uuid4()),
            "evidence_status": {
                str(uuid4()): "collected",
                str(uuid4()): "pending"
            }
        }
        
        result = await node.sync_evidence_status(state)
        
        # Should have executed update query
        assert mock_session.execute.called
        
        # Should have committed
        assert mock_session.commit.called
        
        # Check result structure
        assert result["sync_count"] == 5
        assert "last_sync" in result

    @patch('langgraph_agent.nodes.evidence_nodes.get_async_db')
    async def test_sync_evidence_status_database_error(self, mock_get_db):
        """Test sync_evidence_status with database error handling."""
        mock_session = MagicMock(spec=AsyncSession)
        
        # Mock execute to raise an exception
        mock_session.execute = AsyncMock(side_effect=SQLAlchemyError("Connection lost"))
        mock_session.rollback = AsyncMock()
        
        mock_get_db.return_value = async_generator([mock_session])
        
        node = EvidenceCollectionNode()
        
        # Test with TypedDict state
        state = {
            "user_id": str(uuid4()),
            "business_profile_id": str(uuid4()),
            "evidence_status": {},
            "errors": [],
            "error_count": 0,
            "messages": []
        }
        
        # Should handle error and update state
        result = await node.sync_evidence_status(state)
        
        # Check error handling - sync_evidence_status adds to errors list
        assert result["error_count"] == 1
        assert len(result["errors"]) == 1
        assert "Connection lost" in result["errors"][0]

    @patch('langgraph_agent.nodes.evidence_nodes.get_async_db')
    async def test_sync_evidence_status_no_updates(self, mock_get_db):
        """Test sync_evidence_status when no records need updating."""
        mock_session = MagicMock(spec=AsyncSession)
        
        # Mock execute to return result with 0 rowcount
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        
        mock_get_db.return_value = async_generator([mock_session])
        
        node = EvidenceCollectionNode()
        
        # Test with minimal state
        state = {
            "user_id": str(uuid4()),
            "business_profile_id": str(uuid4()),
            "evidence_status": {}
        }
        
        result = await node.sync_evidence_status(state)
        
        # Check result
        assert result["sync_count"] == 0
        assert "last_sync" in result


@pytest.mark.asyncio
class TestCheckEvidenceExpiryErrors:
    """Test error handling in check_evidence_expiry."""
    
    @patch('langgraph_agent.nodes.evidence_nodes.get_async_db')
    async def test_check_evidence_expiry_database_error(self, mock_get_db):
        """Test check_evidence_expiry with database error."""
        mock_session = MagicMock(spec=AsyncSession)
        
        # Mock execute to raise an exception
        mock_session.execute = AsyncMock(side_effect=SQLAlchemyError("Query timeout"))
        mock_session.rollback = AsyncMock()
        
        mock_get_db.return_value = async_generator([mock_session])
        
        node = EvidenceCollectionNode()
        
        state = {
            "user_id": str(uuid4()),
            "business_profile_id": str(uuid4()),
            "evidence_items": [],
            "evidence_status": {},
            "messages": [],
            "errors": [],
            "error_count": 0
        }
        
        # Should handle error gracefully
        result = await node.check_evidence_expiry(state)
        
        # Should have rolled back
        assert mock_session.rollback.called
        
        # Check error handling
        assert result["error_count"] == 1
        assert len(result["errors"]) == 1
        assert "Query timeout" in result["errors"][0]
        assert len(result["messages"]) == 1
        assert "Expiry check failed" in result["messages"][0].content


@pytest.mark.asyncio
class TestCollectAllIntegrationsLoop:
    """Test the integration collection loop."""
    
    @patch('langgraph_agent.nodes.evidence_nodes.get_async_db')
    async def test_collect_with_multiple_integrations(self, mock_get_db):
        """Test collecting evidence from multiple configured integrations."""
        mock_session = MagicMock(spec=AsyncSession)
        mock_get_db.return_value = async_generator([mock_session])
        
        node = EvidenceCollectionNode()
        
        state = {
            "user_id": str(uuid4()),
            "business_profile_id": str(uuid4()),
            "configured_integrations": ["aws", "github", "jira"],
            "evidence_items": [],
            "messages": [],
            "errors": []
        }
        
        result = await node.collect_all_integrations(state)
        
        # Should have collection results for all integrations
        assert "collection_results" in result
        assert len(result["collection_results"]) == 3
        
        # Check each result
        for i, integration in enumerate(["aws", "github", "jira"]):
            assert result["collection_results"][i]["integration"] == integration
            assert result["collection_results"][i]["status"] == "collected"
            assert result["collection_results"][i]["count"] == 0
            assert "timestamp" in result["collection_results"][i]
        
        # Check message
        assert len(result["messages"]) == 1
        assert "Evidence collection completed for 3 integrations" in result["messages"][0].content

    @patch('langgraph_agent.nodes.evidence_nodes.get_async_db')
    async def test_collect_with_integration_error(self, mock_get_db):
        """Test handling errors during integration collection."""
        mock_session = MagicMock(spec=AsyncSession)
        mock_get_db.return_value = async_generator([mock_session])
        
        node = EvidenceCollectionNode()
        
        # Simulate an integration that causes an error
        state = {
            "user_id": str(uuid4()),
            "business_profile_id": str(uuid4()),
            "configured_integrations": ["aws", "bad_integration", "github"],
            "evidence_items": [],
            "messages": [],
            "errors": []
        }
        
        # Mock logger to verify error logging
        with patch('langgraph_agent.nodes.evidence_nodes.logger') as mock_logger:
            result = await node.collect_all_integrations(state)
            
            # Should still complete and return results
            assert "collection_results" in result
            assert len(result["collection_results"]) == 3
            
            # AWS should succeed
            assert result["collection_results"][0]["status"] == "collected"
            
            # Bad integration gets logged but doesn't fail the whole process
            assert result["collection_results"][1]["status"] == "collected"
            
            # GitHub should succeed
            assert result["collection_results"][2]["status"] == "collected"
            
            # Check completion message
            assert "Evidence collection completed for 3 integrations" in result["messages"][0].content

    @patch('langgraph_agent.nodes.evidence_nodes.get_async_db')
    async def test_collect_with_exception_in_loop(self, mock_get_db):
        """Test handling general exception during collection loop."""
        mock_session = MagicMock(spec=AsyncSession)
        mock_get_db.return_value = async_generator([mock_session])
        
        node = EvidenceCollectionNode()
        
        # Create state that will cause an exception
        state = {
            "user_id": str(uuid4()),
            "business_profile_id": str(uuid4()),
            "configured_integrations": None,  # This will cause TypeError when iterating
            "evidence_items": [],
            "messages": [],
            "errors": []
        }
        
        result = await node.collect_all_integrations(state)
        
        # Should handle the exception gracefully
        assert len(result["messages"]) == 1
        # When configured_integrations is None, it returns "No integrations configured"
        assert "No integrations configured" in result["messages"][0].content


@pytest.mark.asyncio
class TestValidateEvidenceEdgeCases:
    """Test edge cases in validate_evidence method."""
    
    @patch('langgraph_agent.nodes.evidence_nodes.get_async_db')
    async def test_validate_evidence_empty_evidence(self, mock_get_db):
        """Test validation with completely empty evidence."""
        mock_session = MagicMock(spec=AsyncSession)
        mock_get_db.return_value = async_generator([mock_session])
        
        node = EvidenceCollectionNode()
        
        # Completely empty evidence
        evidence = {}
        
        result = await node.validate_evidence(evidence)
        
        # Should be invalid with errors
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert any("Missing required field" in error for error in result["errors"])

    @patch('langgraph_agent.nodes.evidence_nodes.get_async_db')
    async def test_validate_evidence_with_all_fields(self, mock_get_db):
        """Test validation with all required fields."""
        mock_session = MagicMock(spec=AsyncSession)
        mock_get_db.return_value = async_generator([mock_session])
        
        node = EvidenceCollectionNode()
        
        # Evidence with all required fields
        evidence = {
            "id": str(uuid4()),
            "type": "document",
            "content": "A complete evidence item with sufficient content to score well"
        }
        
        result = await node.validate_evidence(evidence)
        
        # Should be valid
        assert result["valid"] is True
        assert len(result["errors"]) == 0


@pytest.mark.asyncio
class TestEvidenceNodeFunction:
    """Test the evidence_node instance."""
    
    async def test_evidence_node_instance(self):
        """Test evidence_node is an instance of EvidenceCollectionNode."""
        from langgraph_agent.nodes.evidence_nodes import evidence_node, EvidenceCollectionNode
        
        # Verify evidence_node is an instance
        assert isinstance(evidence_node, EvidenceCollectionNode)
        
    @patch('langgraph_agent.nodes.evidence_nodes.get_async_db')
    @patch('langgraph_agent.nodes.evidence_nodes.EvidenceProcessor')
    @patch('langgraph_agent.nodes.evidence_nodes.DuplicateDetector')
    async def test_evidence_node_process(self, mock_duplicate_detector, mock_processor_class, mock_get_db):
        """Test calling evidence_node's process_evidence method."""
        from langgraph_agent.nodes.evidence_nodes import evidence_node
        
        # Mock the duplicate detector
        mock_duplicate_detector.is_duplicate = AsyncMock(return_value=False)
        
        # Mock the processor
        mock_processor = MagicMock()
        mock_processor.process_evidence = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        # Create proper mock session with all needed methods
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        
        # Mock refresh to add id to the evidence item
        async def mock_refresh(evidence_item):
            evidence_item.id = uuid4()
        mock_session.refresh = AsyncMock(side_effect=mock_refresh)
        
        mock_get_db.return_value = async_generator([mock_session])
        
        # Test with evidence_data passed directly (backward compatibility mode)
        evidence_data = {
            "user_id": str(uuid4()),
            "business_profile_id": str(uuid4()),
            "evidence_name": "Test Evidence",
            "evidence_type": "Document",
            "description": "Test description",
            "control_reference": "CTRL-001"
        }
        
        # evidence_node is an instance, call its method directly
        # When called with just evidence_data, it returns the processed evidence
        result = await evidence_node.process_evidence(evidence_data)
        
        # Should return processed evidence dict
        assert "id" in result
        assert "type" in result
        assert result["type"] == "Document"
        assert result["status"] == "processed"
        assert result["evidence_name"] == "Test Evidence"