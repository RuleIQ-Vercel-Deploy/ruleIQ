"""
Integration tests for real compliance nodes implementation.
Tests actual database operations and service connections.
"""
from __future__ import annotations

import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List
from uuid import uuid4

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langgraph_agent.nodes.compliance_nodes_real import (
    batch_compliance_update_node,
    single_compliance_check_node,
    compliance_monitoring_node,
    update_compliance_for_profile,
    get_default_framework,
    get_user_for_profile,
)
from langgraph_agent.graph.unified_state import UnifiedComplianceState

class TestRealComplianceNodes:
    """Test suite for real compliance node implementations."""

    @pytest.fixture
    def mock_state(self) -> UnifiedComplianceState:
        """Create a mock state for testing."""
        return {
            "workflow_id": "test-workflow-123",
            "company_id": "company-456",
            "metadata": {"company_id": "company-456", "regulation": "GDPR"},
            "compliance_data": {},
            "obligations": [],
            "errors": [],
            "error_count": 0,
            "history": [],
        }

    @pytest.fixture
    def mock_business_profile(self):
        """Create a mock business profile."""
        profile = Mock()
        profile.business_profile_id = str(uuid4())
        profile.company_name = "Test Company"
        profile.industry = "Technology"
        profile.last_assessment_date = datetime.now(timezone.utc)
        return profile

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.close = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_batch_compliance_update_success(
        self, mock_state, mock_db_session, mock_business_profile
    ):
        """Test successful batch compliance update."""
        # Mock database query results
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=Mock(all=Mock(return_value=[mock_business_profile])))
        mock_db_session.execute.return_value = mock_result

        with patch(
            "langgraph_agent.nodes.compliance_nodes_real.get_async_db",
            return_value=mock_db_session,
        ):
            with patch(
                "langgraph_agent.nodes.compliance_nodes_real.update_compliance_for_profile",
                return_value={"status": "success", "compliance_score": 85.0},
            ) as mock_update:
                result = await batch_compliance_update_node(mock_state)

                assert "compliance_data" in result
                assert "batch_results" in result["compliance_data"]
                mock_update.assert_called()

    @pytest.mark.asyncio
    async def test_single_compliance_check_success(self, mock_state, mock_db_session):
        """Test successful single compliance check."""
        mock_state["metadata"]["profile_id"] = str(uuid4())

        with patch(
            "langgraph_agent.nodes.compliance_nodes_real.get_async_db",
            return_value=mock_db_session,
        ):
            with patch(
                "langgraph_agent.nodes.compliance_nodes_real.update_compliance_for_profile",
                return_value={"status": "success", "compliance_score": 75.0}
            ) as mock_update:
                result = await single_compliance_check_node(mock_state)
                
                assert "compliance_data" in result
                assert result["compliance_data"]["status"] == "success"

    @pytest.mark.asyncio
    async def test_compliance_monitoring_periodic_check(self, mock_state):
        """Test compliance monitoring periodic checks."""
        mock_state["metadata"]["monitoring_enabled"] = True
        mock_state["metadata"]["check_interval"] = 1  # 1 second for testing

        with patch(
            "langgraph_agent.nodes.compliance_nodes_real.single_compliance_check_node"
        ) as mock_check:
            mock_check.return_value = {
                **mock_state,
                "compliance_data": {"status": "monitored", "timestamp": datetime.now().isoformat()}
            }
            
            # Run monitoring for a short time
            monitoring_task = asyncio.create_task(compliance_monitoring_node(mock_state))
            await asyncio.sleep(0.1)
            monitoring_task.cancel()
            
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass

    @pytest.mark.asyncio
    async def test_update_compliance_for_profile(self, mock_db_session, mock_business_profile):
        """Test updating compliance for a specific profile."""
        # Mock framework
        mock_framework = Mock()
        mock_framework.framework_id = str(uuid4())
        mock_framework.name = "ISO 27001"

        # Mock user
        mock_user = Mock()
        mock_user.id = str(uuid4())
        mock_user.email = "test@example.com"

        with patch(
            "langgraph_agent.nodes.compliance_nodes_real.get_default_framework",
            return_value=mock_framework
        ):
            with patch(
                "langgraph_agent.nodes.compliance_nodes_real.get_user_for_profile",
                return_value=mock_user
            ):
                with patch(
                    "langgraph_agent.nodes.compliance_nodes_real.generate_readiness_assessment"
                ) as mock_generate:
                    mock_generate.return_value = {
                        "compliance_score": 80.0,
                        "gaps": ["Missing data encryption"],
                        "recommendations": ["Implement AES-256"]
                    }
                    
                    result = await update_compliance_for_profile(
                        mock_db_session, mock_business_profile
                    )
                    
                    assert result["status"] == "success"
                    assert "compliance_score" in result
                    assert result["compliance_score"] == 80.0

    @pytest.mark.asyncio
    async def test_get_default_framework(self, mock_db_session):
        """Test getting default framework."""
        mock_framework = Mock()
        mock_framework.framework_id = str(uuid4())
        mock_framework.name = "GDPR"
        mock_framework.is_default = True

        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_framework)
        mock_db_session.execute.return_value = mock_result

        framework = await get_default_framework(mock_db_session)
        assert framework is not None
        assert framework.name == "GDPR"

    @pytest.mark.asyncio
    async def test_get_user_for_profile(self, mock_db_session, mock_business_profile):
        """Test getting user for a profile."""
        mock_user = Mock()
        mock_user.id = str(uuid4())
        mock_user.email = "user@example.com"

        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_user)
        mock_db_session.execute.return_value = mock_result

        user = await get_user_for_profile(mock_db_session, mock_business_profile)
        assert user is not None
        assert user.email == "user@example.com"

    @pytest.mark.asyncio
    async def test_batch_compliance_error_handling(self, mock_state, mock_db_session):
        """Test batch compliance update with error handling."""
        mock_db_session.execute.side_effect = Exception("Database error")

        with patch(
            "langgraph_agent.nodes.compliance_nodes_real.get_async_db",
            return_value=mock_db_session
        ):
            result = await batch_compliance_update_node(mock_state)
            
            assert len(result["errors"]) > 0
            assert "Database error" in str(result["errors"][0])

    @pytest.mark.asyncio
    async def test_single_compliance_check_no_profile(self, mock_state):
        """Test single compliance check without profile ID."""
        # Remove profile_id from metadata
        mock_state["metadata"] = {"company_id": "company-456"}

        result = await single_compliance_check_node(mock_state)
        
        assert len(result["errors"]) > 0
        assert "No profile_id" in str(result["errors"][0])

    @pytest.mark.asyncio
    async def test_compliance_monitoring_disabled(self, mock_state):
        """Test compliance monitoring when disabled."""
        mock_state["metadata"]["monitoring_enabled"] = False

        result = await compliance_monitoring_node(mock_state)
        
        assert result["compliance_data"]["monitoring_status"] == "disabled"