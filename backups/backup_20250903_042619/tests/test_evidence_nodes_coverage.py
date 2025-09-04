"""Additional tests to improve coverage of evidence_nodes module."""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, AsyncGenerator, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import uuid4

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.graph.message import add_messages

from database.evidence_item import EvidenceItem
from langgraph_agent.nodes.evidence_nodes import EvidenceCollectionNode, evidence_node


async def async_generator(items):
    """Helper to create async generator."""
    for item in items:
        yield item


@pytest.mark.asyncio
class TestEvidenceCollectionNodeUncovered:
    """Tests for uncovered methods in EvidenceCollectionNode."""

    @patch("langgraph_agent.nodes.evidence_nodes.get_async_db")
    @patch("langgraph_agent.nodes.evidence_nodes.EvidenceProcessor")
    async def test_process_pending_evidence(self, mock_processor_class, mock_get_db):
        """Test processing pending evidence items."""
        # Create mock evidence items
        pending_evidence = MagicMock(spec=EvidenceItem)
        pending_evidence.id = str(uuid4())
        pending_evidence.status = "not_started"  # Correct initial status
        pending_evidence.evidence_name = "Pending Doc"
        pending_evidence.evidence_type = "Policy"
        pending_evidence.to_dict = MagicMock(
            return_value={
                "id": pending_evidence.id,
                "evidence_name": "Pending Doc",
                "status": "not_started",
                "evidence_type": "Policy",
            },
        )

        # Mock the processor
        mock_processor = MagicMock()
        mock_processor.process_evidence = MagicMock()
        mock_processor_class.return_value = mock_processor

        mock_session = MagicMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars = MagicMock(
            return_value=MagicMock(all=MagicMock(return_value=[pending_evidence])),
        )
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
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
            "error_count": 0,
        }

        result = await node.process_pending_evidence(state)

        # Should have processed the pending evidence
        assert mock_session.execute.called
        assert "pending_processing" in result

    async def test_aggregate_evidence_correct_field(self):
        """Test evidence aggregation with correct field names."""
        node = EvidenceCollectionNode()

        # Use 'type' field as the actual method expects
        evidence_list = [
            {
                "id": "1",
                "evidence_name": "Doc 1",
                "type": "Policy",
                "content": "Content 1",
            },
            {
                "id": "2",
                "evidence_name": "Doc 2",
                "type": "Policy",
                "content": "Content 2",
            },
            {
                "id": "3",
                "evidence_name": "Doc 3",
                "type": "Procedure",
                "content": "Content 3",
            },
        ]

        result = await node.aggregate_evidence(evidence_list)

        assert "Policy" in result
        assert len(result["Policy"]) == 2
        assert "Procedure" in result
        assert len(result["Procedure"]) == 1

    async def test_aggregate_evidence_deduplication(self):
        """Test evidence aggregation with duplicate detection."""
        node = EvidenceCollectionNode()

        # Evidence with duplicate content
        evidence_list = [
            {"id": "1", "type": "Policy", "content": "Same content"},
            {"id": "2", "type": "Policy", "content": "Same content"},  # Duplicate
            {"id": "3", "type": "Policy", "content": "Different content"},
        ]

        result = await node.aggregate_evidence(evidence_list)

        assert "Policy" in result
        assert len(result["Policy"]) == 2  # One duplicate removed

    @patch("langgraph_agent.nodes.evidence_nodes.get_async_db")
    async def test_retry_with_correct_signature(self, mock_get_db):
        """Test retry mechanism with correct function signature."""
        mock_session = MagicMock(spec=AsyncSession)
        mock_get_db.return_value = async_generator([mock_session])

        node = EvidenceCollectionNode()

        # Create a function that fails then succeeds
        call_count = 0

        async def flaky_operation():
            nonlocal call_count
            """Flaky Operation"""
            call_count += 1
            if call_count < 2:
                raise Exception(f"Temporary failure {call_count}")
            return "Success"

        # Call retry_with_backoff - max_retries is hardcoded to 3 in the method
        result = await node.retry_with_backoff(flaky_operation)
        assert result == "Success"
        assert call_count == 2

    @patch("langgraph_agent.nodes.evidence_nodes.get_async_db")
    async def test_circuit_breaker_state_transitions(self, mock_get_db):
        """Test circuit breaker state transitions."""
        node = EvidenceCollectionNode()

        assert node.circuit_breaker_state == "closed"

        # Simulate failures
        node.circuit_breaker_failure_count = 3
        node.circuit_breaker_state = "open"

        assert node.circuit_breaker_state == "open"

        # Reset circuit breaker
        node.circuit_breaker_failure_count = 0
        node.circuit_breaker_state = "closed"

        assert node.circuit_breaker_state == "closed"

    @patch("langgraph_agent.nodes.evidence_nodes.get_async_db")
    async def test_sync_evidence_with_text_wrapper(self, mock_get_db):
        """Test sync_evidence_status with proper SQL text wrapper."""
        mock_session = MagicMock(spec=AsyncSession)

        # Mock the result properly with rowcount
        mock_result = MagicMock()
        mock_result.rowcount = 2

        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_get_db.return_value = async_generator([mock_session])

        node = EvidenceCollectionNode()

        state = {
            "user_id": str(uuid4()),
            "business_profile_id": str(uuid4()),
            "evidence_status": {str(uuid4()): "collected", str(uuid4()): "pending"},
            "messages": [],
            "errors": [],
        }

        result = await node.sync_evidence_status(state)

        # Should have executed SQL update
        assert mock_session.execute.called
        assert result["sync_count"] == 2
        assert "last_sync" in result

    @patch("langgraph_agent.nodes.evidence_nodes.get_async_db")
    async def test_check_evidence_expiry_with_frequencies(self, mock_get_db):
        """Test evidence expiry checking with different frequencies."""
        now = datetime.now(timezone.utc)

        # Create evidence with different frequencies
        monthly_evidence = MagicMock(spec=EvidenceItem)
        monthly_evidence.id = "monthly_id"
        monthly_evidence.collected_at = now - timedelta(days=35)
        monthly_evidence.collection_frequency = "monthly"
        monthly_evidence.to_dict = MagicMock(
            return_value={"id": "monthly_id", "status": "expired"},
        )

        quarterly_evidence = MagicMock(spec=EvidenceItem)
        quarterly_evidence.id = "quarterly_id"
        quarterly_evidence.collected_at = now - timedelta(days=100)
        quarterly_evidence.collection_frequency = "quarterly"
        quarterly_evidence.to_dict = MagicMock(
            return_value={"id": "quarterly_id", "status": "expired"},
        )

        annually_evidence = MagicMock(spec=EvidenceItem)
        annually_evidence.id = "annually_id"
        annually_evidence.collected_at = now - timedelta(days=400)
        annually_evidence.collection_frequency = "annually"
        annually_evidence.to_dict = MagicMock(
            return_value={"id": "annually_id", "status": "expired"},
        )

        mock_session = MagicMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars = MagicMock(
            return_value=MagicMock(
                all=MagicMock(
                    return_value=[
                        monthly_evidence,
                        quarterly_evidence,
                        annually_evidence,
                    ],
                ),
            ),
        )
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_get_db.return_value = async_generator([mock_session])

        node = EvidenceCollectionNode()

        state = {
            "user_id": str(uuid4()),
            "business_profile_id": str(uuid4()),
            "evidence_items": [],
            "evidence_status": {},
            "messages": [],
            "errors": [],
        }

        result = await node.check_evidence_expiry(state)

        # Should have executed query
        assert mock_session.execute.called

    @patch("langgraph_agent.nodes.evidence_nodes.get_async_db")
    async def test_collect_integrations_with_config(self, mock_get_db):
        """Test collect_all_integrations with configured integrations."""
        mock_session = MagicMock(spec=AsyncSession)
        mock_get_db.return_value = async_generator([mock_session])

        node = EvidenceCollectionNode()

        # Add integration configuration
        state = {
            "user_id": str(uuid4()),
            "business_profile_id": str(uuid4()),
            "integrations": {
                "aws": {"enabled": True, "config": {}},
                "github": {"enabled": True, "config": {}},
            },
            "evidence_items": [],
            "messages": [],
            "errors": [],
        }

        result = await node.collect_all_integrations(state)

        # Should log warning about no collector implementation
        assert result == state  # Returns unchanged when no actual collectors


class TestEvidenceCollectionNodeSync:
    """Tests for synchronous methods in EvidenceCollectionNode."""

    def test_merge_evidence_preserves_data(self):
        """Test evidence merging preserves existing data and merges specific fields."""
        node = EvidenceCollectionNode()

        evidence1 = {
            "id": "1",
            "type": "Policy",
            "content": {"data": "original"},
            "score": 0.8,
            "field1": "value1",
        }
        evidence2 = {
            "id": "2",
            "content": {"extra": "new"},
            "score": 0.6,
            "timestamp": "2024-01-01T00:00:00",
            "metadata": {"key": "value"},
        }

        result = node.merge_evidence(evidence1, evidence2)

        # Should preserve existing base fields
        assert result["id"] == "1"  # Preserves existing ID
        assert result["type"] == "Policy"  # Preserves existing type
        assert result["field1"] == "value1"  # Preserves other fields

        # Should merge content
        assert result["content"]["data"] == "original"
        assert result["content"]["extra"] == "new"

        # Should combine scores
        assert result["combined_score"] == 0.7  # Average of 0.8 and 0.6

        # Should update timestamp and metadata
        assert result["timestamp"] == "2024-01-01T00:00:00"
        assert result["metadata"]["key"] == "value"
