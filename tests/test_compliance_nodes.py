"""
Comprehensive test suite for compliance nodes.
Tests migration from Celery compliance_tasks to LangGraph nodes.
"""
from __future__ import annotations

# Constants
MINUTE_SECONDS = 60
DEFAULT_LIMIT = 100.0

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List
import sys
import os

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langgraph_agent.nodes.compliance_nodes import (
    compliance_check_node, 
    extract_requirements_from_rag, 
    check_compliance_status, 
    assess_compliance_risk
)
from langgraph_agent.graph.unified_state import UnifiedComplianceState

class TestComplianceCheckNode:
    """Test suite for compliance_check_node function."""

    @pytest.fixture
    def mock_state(self) -> UnifiedComplianceState:
        """Create a mock state for testing."""
        return {
            'workflow_id': 'test-workflow-123',
            'company_id': 'company-456',
            'metadata': {
                'company_id': 'company-456',
                'regulation': 'GDPR'
            },
            'relevant_documents': [{
                'content': 'The company must implement data encryption requirements.',
                'metadata': {'source': 'GDPR Article 32', 'category': 'security'}
            }],
            'compliance_data': {},
            'obligations': [],
            'errors': [],
            'error_count': 0,
            'history': []
        }

    @pytest.mark.asyncio
    async def test_compliance_check_successful(self, mock_state):
        """Test successful compliance check."""
        with patch('langgraph_agent.nodes.compliance_nodes.check_compliance_status') as mock_check:
            mock_check.return_value = {
                'obligations': [
                    {'id': '1', 'title': 'Data Encryption', 'satisfied': True},
                    {'id': '2', 'title': 'Data Retention', 'satisfied': False}
                ],
                'violations': [
                    {'id': '2', 'title': 'Data Retention', 'satisfied': False}
                ],
                'total_obligations': 2,
                'satisfied_obligations': 1,
                'compliance_score': 50.0
            }
            result = await compliance_check_node(mock_state)
            assert result['compliance_data'] is not None
            assert 'obligations' in result['compliance_data']
            assert len(result['compliance_data']['obligations']) == 2
            assert result['compliance_data']['compliance_score'] == 50.0

    @pytest.mark.asyncio
    async def test_compliance_check_with_errors(self, mock_state):
        """Test compliance check with error handling."""
        with patch('langgraph_agent.nodes.compliance_nodes.check_compliance_status') as mock_check:
            mock_check.side_effect = Exception("Compliance service unavailable")
            result = await compliance_check_node(mock_state)
            assert len(result['errors']) > 0
            assert result['error_count'] > 0
            assert 'Compliance service unavailable' in str(result['errors'][0])

    @pytest.mark.asyncio
    async def test_compliance_check_empty_documents(self):
        """Test compliance check with no documents."""
        state = {
            'workflow_id': 'test-workflow-empty',
            'company_id': 'company-456',
            'metadata': {'company_id': 'company-456', 'regulation': 'GDPR'},
            'relevant_documents': [],
            'compliance_data': {},
            'obligations': [],
            'errors': [],
            'error_count': 0,
            'history': []
        }
        with patch('langgraph_agent.nodes.compliance_nodes.check_compliance_status') as mock_check:
            mock_check.return_value = {
                'obligations': [],
                'violations': [],
                'total_obligations': 0,
                'satisfied_obligations': 0,
                'compliance_score': 100.0
            }
            result = await compliance_check_node(state)
            assert result['compliance_data']['compliance_score'] == 100.0

class TestExtractRequirementsFromRAG:
    """Test suite for extract_requirements_from_rag function."""

    @pytest.mark.asyncio
    async def test_extract_requirements_successful(self):
        """Test successful requirements extraction."""
        documents = [
            {'content': 'Data must be encrypted at rest.', 'metadata': {'source': 'GDPR'}},
            {'content': 'Access logs must be retained for 90 days.', 'metadata': {'source': 'GDPR'}}
        ]
        
        requirements = await extract_requirements_from_rag(documents)
        assert len(requirements) == 2
        assert 'must' in requirements[0]['content'].lower()

    @pytest.mark.asyncio
    async def test_extract_requirements_no_documents(self):
        """Test extraction when no relevant documents found."""
        requirements = await extract_requirements_from_rag([])
        assert requirements == []

    @pytest.mark.asyncio
    async def test_extract_requirements_with_metadata(self):
        """Test extraction preserves metadata."""
        documents = [
            {
                'content': 'Data encryption is required for all personal data.',
                'metadata': {'source': 'GDPR Article 32', 'category': 'security'}
            }
        ]
        
        requirements = await extract_requirements_from_rag(documents)
        assert len(requirements) == 1
        assert requirements[0]['source'] == 'GDPR Article 32'
        assert requirements[0]['category'] == 'security'

class TestCheckComplianceStatus:
    """Test suite for check_compliance_status function."""

    @pytest.mark.asyncio
    async def test_check_compliance_with_neo4j(self):
        """Test compliance check using Neo4j."""
        with patch('langgraph_agent.nodes.compliance_nodes.get_neo4j_service') as mock_service:
            mock_neo4j = AsyncMock()
            mock_neo4j.driver = True
            mock_neo4j.execute_query = AsyncMock(return_value=[
                {
                    'o': {'id': '1', 'title': 'Data Encryption', 'description': 'Encrypt data'},
                    'evidence': [{'id': 'e1'}]
                },
                {
                    'o': {'id': '2', 'title': 'Access Control', 'description': 'Control access'},
                    'evidence': []
                }
            ])
            mock_service.return_value = mock_neo4j
            
            result = await check_compliance_status('company-123', 'GDPR', [])
            assert result['total_obligations'] == 2
            assert result['satisfied_obligations'] == 1
            assert result['compliance_score'] == 50.0
            assert len(result['violations']) == 1

    @pytest.mark.asyncio
    async def test_check_compliance_no_obligations(self):
        """Test compliance check when no obligations exist."""
        with patch('langgraph_agent.nodes.compliance_nodes.get_neo4j_service') as mock_service:
            mock_neo4j = AsyncMock()
            mock_neo4j.driver = True
            mock_neo4j.execute_query = AsyncMock(return_value=[])
            mock_service.return_value = mock_neo4j
            
            result = await check_compliance_status('company-123', 'GDPR', [])
            assert result['total_obligations'] == 0
            assert result['satisfied_obligations'] == 0
            assert result['compliance_score'] == 100.0
            assert len(result['violations']) == 0

    @pytest.mark.asyncio
    async def test_check_compliance_neo4j_unavailable(self):
        """Test compliance check when Neo4j is unavailable."""
        with patch('langgraph_agent.nodes.compliance_nodes.get_neo4j_service') as mock_service:
            mock_service.return_value = None
            
            result = await check_compliance_status('company-123', 'GDPR', [])
            assert 'error' in result
            assert result['error'] == 'Database service not available'
            assert result['compliance_score'] == 0

class TestAssessComplianceRisk:
    """Test suite for assess_compliance_risk function."""

    @pytest.mark.asyncio
    async def test_assess_risk_high(self):
        """Test risk assessment for high risk scenario."""
        compliance_data = {
            'compliance_score': 30.0,
            'violations': [
                {'id': '1', 'title': 'Data Encryption', 'severity': 'high'},
                {'id': '2', 'title': 'Access Control', 'severity': 'high'}
            ]
        }
        
        risk = await assess_compliance_risk(compliance_data)
        assert risk['risk_level'] == 'high'
        assert risk['risk_score'] >= 70
        assert len(risk['critical_issues']) >= 2

    @pytest.mark.asyncio
    async def test_assess_risk_medium(self):
        """Test risk assessment for medium risk scenario."""
        compliance_data = {
            'compliance_score': 65.0,
            'violations': [
                {'id': '1', 'title': 'Audit Logging', 'severity': 'medium'}
            ]
        }
        
        risk = await assess_compliance_risk(compliance_data)
        assert risk['risk_level'] == 'medium'
        assert 30 <= risk['risk_score'] < 70

    @pytest.mark.asyncio
    async def test_assess_risk_low(self):
        """Test risk assessment for low risk scenario."""
        compliance_data = {
            'compliance_score': 95.0,
            'violations': []
        }
        
        risk = await assess_compliance_risk(compliance_data)
        assert risk['risk_level'] == 'low'
        assert risk['risk_score'] < 30
        assert len(risk['critical_issues']) == 0

    @pytest.mark.asyncio
    async def test_assess_risk_with_recommendations(self):
        """Test that risk assessment includes recommendations."""
        compliance_data = {
            'compliance_score': 50.0,
            'violations': [
                {'id': '1', 'title': 'Data Encryption', 'severity': 'high'}
            ]
        }
        
        risk = await assess_compliance_risk(compliance_data)
        assert 'recommendations' in risk
        assert len(risk['recommendations']) > 0