"""
Test-Driven Development suite for Evidence Collection Tasks Migration.
Following TDD principles: Write tests first, then implementation.
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call
from uuid import UUID, uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError

from langgraph_agent.graph.enhanced_state import EnhancedComplianceState
from langgraph_agent.graph.error_handler import ErrorHandlerNode
from langgraph_agent.nodes.evidence_nodes import EvidenceCollectionNode

# ==========================
# Test Fixtures
# ==========================

@pytest.fixture
def mock_db_session():
    """Mock database session with async context manager."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.query = MagicMock()
    return session

@pytest.fixture
def mock_processor():
    """Mock evidence processor."""
    processor = Mock()
    processor.process_evidence = Mock(return_value=True)
    processor.validate_evidence = Mock(return_value={"valid": True, "score": 0.95})
    return processor

@pytest.fixture
def mock_duplicate_detector():
    """Mock duplicate detector."""
    detector = Mock()
    detector.is_duplicate = AsyncMock(return_value=False)
    detector.get_similar_evidence = AsyncMock(return_value=[])
    return detector

@pytest.fixture
def evidence_node():
    """Create evidence collection node instance."""
    return EvidenceCollectionNode()

@pytest.fixture
def sample_state():
    """Create sample state for testing."""
    return {
        "user_id": str(uuid4()),
        "business_profile_id": str(uuid4()),
        "evidence_items": [],
        "evidence_status": {},
        "errors": [],
        "error_count": 0,
    }

# ==========================
# Test Evidence Collection
# ==========================

class TestEvidenceCollection:
    """Test evidence collection functionality."""

    @pytest.mark.asyncio
    async def test_collect_evidence_success(self, evidence_node, sample_state, mock_db_session):
        """Test successful evidence collection."""
        # Create mock evidence items
        mock_evidence = Mock()
        mock_evidence.id = str(uuid4())
        mock_evidence.evidence_name = "Test Document"
        mock_evidence.status = "not_started"
        mock_evidence.to_dict = Mock(return_value={
            "id": mock_evidence.id,
            "evidence_name": "Test Document",
            "status": "not_started"
        })

        # Mock database query
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=Mock(all=Mock(return_value=[mock_evidence])))
        mock_db_session.execute.return_value = mock_result

        with patch("langgraph_agent.nodes.evidence_nodes.get_async_db") as mock_get_db:
            # Create async generator
            async def async_gen():
                yield mock_db_session
            mock_get_db.return_value = async_gen()

            # Execute collection
            result = await evidence_node.collect_evidence(sample_state)

            # Verify results
            assert "evidence_items" in result
            assert len(result["evidence_items"]) == 1
            assert result["evidence_items"][0]["evidence_name"] == "Test Document"

    @pytest.mark.asyncio
    async def test_collect_evidence_no_items(self, evidence_node, sample_state, mock_db_session):
        """Test evidence collection with no items."""
        # Mock empty result
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=Mock(all=Mock(return_value=[])))
        mock_db_session.execute.return_value = mock_result

        with patch("langgraph_agent.nodes.evidence_nodes.get_async_db") as mock_get_db:
            async def async_gen():
                yield mock_db_session
            mock_get_db.return_value = async_gen()

            result = await evidence_node.collect_evidence(sample_state)

            assert result["evidence_items"] == []

    @pytest.mark.asyncio
    async def test_collect_evidence_database_error(self, evidence_node, sample_state, mock_db_session):
        """Test evidence collection with database error."""
        mock_db_session.execute.side_effect = SQLAlchemyError("Database connection failed")

        with patch("langgraph_agent.nodes.evidence_nodes.get_async_db") as mock_get_db:
            async def async_gen():
                yield mock_db_session
            mock_get_db.return_value = async_gen()

            result = await evidence_node.collect_evidence(sample_state)

            assert result["error_count"] > 0
            assert "Database connection failed" in str(result["errors"])

# ==========================
# Test Evidence Processing
# ==========================

class TestEvidenceProcessing:
    """Test evidence processing functionality."""

    @pytest.mark.asyncio
    async def test_process_evidence_success(self, evidence_node, sample_state, mock_processor):
        """Test successful evidence processing."""
        evidence_item = {
            "id": str(uuid4()),
            "evidence_name": "Policy Document",
            "status": "collected"
        }
        sample_state["evidence_items"] = [evidence_item]

        with patch("langgraph_agent.nodes.evidence_nodes.EvidenceProcessor") as MockProcessor:
            MockProcessor.return_value = mock_processor
            
            result = await evidence_node.process_evidence(sample_state)
            
            assert evidence_item["id"] in result["evidence_status"]
            mock_processor.process_evidence.assert_called()

    @pytest.mark.asyncio
    async def test_process_evidence_validation_failure(self, evidence_node, sample_state, mock_processor):
        """Test evidence processing with validation failure."""
        evidence_item = {
            "id": str(uuid4()),
            "evidence_name": "Invalid Document",
            "status": "collected"
        }
        sample_state["evidence_items"] = [evidence_item]
        
        mock_processor.validate_evidence.return_value = {"valid": False, "reason": "Invalid format"}

        with patch("langgraph_agent.nodes.evidence_nodes.EvidenceProcessor") as MockProcessor:
            MockProcessor.return_value = mock_processor
            
            result = await evidence_node.process_evidence(sample_state)
            
            assert result["evidence_status"][evidence_item["id"]] == "validation_failed"

# ==========================
# Test Duplicate Detection
# ==========================

class TestDuplicateDetection:
    """Test duplicate evidence detection."""

    @pytest.mark.asyncio
    async def test_detect_duplicate_evidence(self, evidence_node, sample_state, mock_duplicate_detector):
        """Test detection of duplicate evidence."""
        evidence_item = {
            "id": str(uuid4()),
            "evidence_name": "Duplicate Document",
            "content_hash": "abc123"
        }
        sample_state["evidence_items"] = [evidence_item]
        
        mock_duplicate_detector.is_duplicate.return_value = True

        with patch("langgraph_agent.nodes.evidence_nodes.DuplicateDetector") as MockDetector:
            MockDetector.return_value = mock_duplicate_detector
            
            result = await evidence_node.check_duplicates(sample_state)
            
            assert evidence_item["id"] in result.get("duplicate_evidence", [])

    @pytest.mark.asyncio
    async def test_no_duplicates_found(self, evidence_node, sample_state, mock_duplicate_detector):
        """Test when no duplicates are found."""
        evidence_item = {
            "id": str(uuid4()),
            "evidence_name": "Unique Document",
            "content_hash": "xyz789"
        }
        sample_state["evidence_items"] = [evidence_item]

        with patch("langgraph_agent.nodes.evidence_nodes.DuplicateDetector") as MockDetector:
            MockDetector.return_value = mock_duplicate_detector
            
            result = await evidence_node.check_duplicates(sample_state)
            
            assert "duplicate_evidence" not in result or evidence_item["id"] not in result.get("duplicate_evidence", [])

# ==========================
# Test Status Synchronization
# ==========================

class TestStatusSync:
    """Test evidence status synchronization."""

    @pytest.mark.asyncio
    async def test_sync_evidence_status(self, evidence_node, sample_state, mock_db_session):
        """Test synchronizing evidence status to database."""
        evidence_id = str(uuid4())
        sample_state["evidence_status"] = {
            evidence_id: "processed"
        }

        with patch("langgraph_agent.nodes.evidence_nodes.get_async_db") as mock_get_db:
            async def async_gen():
                yield mock_db_session
            mock_get_db.return_value = async_gen()

            result = await evidence_node.sync_evidence_status(sample_state)
            
            mock_db_session.execute.assert_called()
            mock_db_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_sync_status_with_error(self, evidence_node, sample_state, mock_db_session):
        """Test status sync with database error."""
        sample_state["evidence_status"] = {
            str(uuid4()): "failed"
        }
        
        mock_db_session.commit.side_effect = SQLAlchemyError("Commit failed")

        with patch("langgraph_agent.nodes.evidence_nodes.get_async_db") as mock_get_db:
            async def async_gen():
                yield mock_db_session
            mock_get_db.return_value = async_gen()

            result = await evidence_node.sync_evidence_status(sample_state)
            
            assert result["error_count"] > 0
            mock_db_session.rollback.assert_called()

# ==========================
# Test Error Handling
# ==========================

class TestErrorHandling:
    """Test error handling in evidence nodes."""

    @pytest.mark.asyncio
    async def test_handle_processing_error(self, evidence_node, sample_state):
        """Test handling of processing errors."""
        error = Exception("Processing failed")
        
        result = evidence_node.handle_error(sample_state, error, "process_evidence")
        
        assert result["error_count"] == 1
        assert len(result["errors"]) == 1
        assert "Processing failed" in str(result["errors"][0])

    @pytest.mark.asyncio
    async def test_error_recovery(self, evidence_node, sample_state):
        """Test error recovery mechanism."""
        sample_state["error_count"] = 2
        sample_state["retry_count"] = 1
        sample_state["max_retries"] = 3
        
        with patch.object(evidence_node, "collect_evidence") as mock_collect:
            mock_collect.return_value = {**sample_state, "evidence_items": []}
            
            can_retry = evidence_node.can_retry(sample_state)
            assert can_retry is True
            
            # Test recovery
            result = await evidence_node.retry_operation(sample_state, "collect_evidence")
            assert result["retry_count"] == 2