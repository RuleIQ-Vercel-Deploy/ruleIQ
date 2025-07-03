"""
Integration tests for AI Assessment endpoints with ComplianceAssistant (Phase 2.2).

Tests the integration between AI endpoints and ComplianceAssistant methods.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from fastapi.testclient import TestClient
from httpx import AsyncClient

from main import app
from database.user import User
from database.business_profile import BusinessProfile
from services.ai.assistant import ComplianceAssistant


@pytest.fixture
def test_client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Mock user for testing."""
    user = User()
    user.id = uuid4()
    user.email = "test@example.com"
    user.is_active = True
    return user


@pytest.fixture
def mock_business_profile():
    """Mock business profile for testing."""
    profile = BusinessProfile()
    profile.id = uuid4()
    profile.company_name = "Test Company"
    profile.industry = "Technology"
    profile.employee_count = 50
    profile.data_types = ["personal_data"]
    return profile


class TestAIHelpEndpoint:
    """Test /ai/assessments/{framework_id}/help endpoint integration."""
    
    @pytest.mark.asyncio
    async def test_ai_help_endpoint_integration(self, mock_user, mock_business_profile):
        """Test AI help endpoint calls ComplianceAssistant correctly."""
        
        with patch('api.dependencies.auth.get_current_active_user') as mock_auth:
            with patch('api.dependencies.database.get_async_db') as mock_db:
                with patch('api.routers.ai_assessments.get_user_business_profile') as mock_get_profile:
                    with patch.object(ComplianceAssistant, 'get_assessment_help') as mock_help:
                        
                        # Setup mocks
                        mock_auth.return_value = mock_user
                        mock_db.return_value = AsyncMock()
                        mock_get_profile.return_value = mock_business_profile
                        
                        mock_help.return_value = {
                            'guidance': 'Test guidance',
                            'confidence_score': 0.9,
                            'related_topics': ['data protection'],
                            'follow_up_suggestions': ['Review policies'],
                            'source_references': ['GDPR Article 6'],
                            'request_id': 'test_request_123',
                            'generated_at': '2024-01-01T00:00:00Z',
                            'framework_id': 'gdpr',
                            'question_id': 'q1'
                        }
                        
                        # Make request
                        async with AsyncClient(app=app, base_url="http://test") as client:
                            response = await client.post(
                                "/api/ai/assessments/gdpr/help",
                                json={
                                    "question_id": "q1",
                                    "question_text": "What is GDPR?",
                                    "framework_id": "gdpr",
                                    "section_id": "data_protection",
                                    "user_context": {"role": "admin"}
                                },
                                headers={"Authorization": "Bearer test_token"}
                            )
                        
                        # Verify ComplianceAssistant was called correctly
                        mock_help.assert_called_once()
                        call_args = mock_help.call_args
                        assert call_args[1]['question_id'] == 'q1'
                        assert call_args[1]['question_text'] == 'What is GDPR?'
                        assert call_args[1]['framework_id'] == 'gdpr'
                        assert call_args[1]['section_id'] == 'data_protection'
                        
                        # Verify response
                        assert response.status_code == 200
                        data = response.json()
                        assert data['guidance'] == 'Test guidance'
                        assert data['confidence_score'] == 0.9


class TestAIFollowupEndpoint:
    """Test /ai/assessments/followup endpoint integration."""
    
    @pytest.mark.asyncio
    async def test_ai_followup_endpoint_integration(self, mock_user, mock_business_profile):
        """Test AI followup endpoint calls ComplianceAssistant correctly."""
        
        with patch('api.dependencies.auth.get_current_active_user') as mock_auth:
            with patch('api.dependencies.database.get_async_db') as mock_db:
                with patch('api.routers.ai_assessments.get_user_business_profile') as mock_get_profile:
                    with patch.object(ComplianceAssistant, 'generate_assessment_followup') as mock_followup:
                        
                        # Setup mocks
                        mock_auth.return_value = mock_user
                        mock_db.return_value = AsyncMock()
                        mock_get_profile.return_value = mock_business_profile
                        
                        mock_followup.return_value = {
                            'follow_up_questions': [
                                'What data do you collect?',
                                'How do you store personal data?'
                            ],
                            'recommendations': ['Review data mapping'],
                            'confidence_score': 0.8,
                            'request_id': 'followup_123',
                            'generated_at': '2024-01-01T00:00:00Z',
                            'framework_id': 'gdpr'
                        }
                        
                        # Make request
                        async with AsyncClient(app=app, base_url="http://test") as client:
                            response = await client.post(
                                "/api/ai/assessments/followup",
                                json={
                                    "framework_id": "gdpr",
                                    "current_answers": {
                                        "company_size": "50-100",
                                        "industry": "technology"
                                    },
                                    "business_context": {"progress": 50},
                                    "max_questions": 3
                                },
                                headers={"Authorization": "Bearer test_token"}
                            )
                        
                        # Verify ComplianceAssistant was called correctly
                        mock_followup.assert_called_once()
                        call_args = mock_followup.call_args
                        assert call_args[1]['framework_id'] == 'gdpr'
                        assert 'current_answers' in call_args[1]
                        
                        # Verify response
                        assert response.status_code == 200
                        data = response.json()
                        assert len(data['questions']) == 2


class TestAIAnalysisEndpoint:
    """Test /ai/assessments/analysis endpoint integration."""
    
    @pytest.mark.asyncio
    async def test_ai_analysis_endpoint_integration(self, mock_user, mock_business_profile):
        """Test AI analysis endpoint calls ComplianceAssistant correctly."""
        
        with patch('api.dependencies.auth.get_current_active_user') as mock_auth:
            with patch('api.dependencies.database.get_async_db') as mock_db:
                with patch('api.routers.ai_assessments.get_user_business_profile') as mock_get_profile:
                    with patch.object(ComplianceAssistant, 'analyze_assessment_results') as mock_analysis:
                        
                        # Setup mocks
                        mock_auth.return_value = mock_user
                        mock_db.return_value = AsyncMock()
                        mock_get_profile.return_value = mock_business_profile
                        
                        mock_analysis.return_value = {
                            'gaps': [
                                {
                                    'id': 'gap1',
                                    'title': 'Missing Privacy Policy',
                                    'description': 'No privacy policy found',
                                    'severity': 'high',
                                    'category': 'documentation'
                                }
                            ],
                            'recommendations': [
                                {
                                    'id': 'rec1',
                                    'title': 'Create Privacy Policy',
                                    'description': 'Develop comprehensive privacy policy',
                                    'priority': 'high',
                                    'effort_estimate': '2-3 weeks',
                                    'impact_score': 0.9
                                }
                            ],
                            'risk_assessment': {
                                'level': 'medium',
                                'description': 'Some compliance gaps identified'
                            },
                            'compliance_insights': {
                                'summary': 'Overall compliance is progressing'
                            },
                            'evidence_requirements': [],
                            'request_id': 'analysis_123',
                            'generated_at': '2024-01-01T00:00:00Z',
                            'framework_id': 'gdpr'
                        }
                        
                        # Make request
                        async with AsyncClient(app=app, base_url="http://test") as client:
                            response = await client.post(
                                "/api/ai/assessments/analysis",
                                json={
                                    "framework_id": "gdpr",
                                    "assessment_results": {
                                        "privacy_policy": "missing",
                                        "data_mapping": "partial"
                                    },
                                    "business_profile_id": str(mock_business_profile.id)
                                },
                                headers={"Authorization": "Bearer test_token"}
                            )
                        
                        # Verify ComplianceAssistant was called correctly
                        mock_analysis.assert_called_once()
                        call_args = mock_analysis.call_args
                        assert call_args[1]['framework_id'] == 'gdpr'
                        assert 'assessment_results' in call_args[1]
                        
                        # Verify response
                        assert response.status_code == 200
                        data = response.json()
                        assert len(data['gaps']) == 1
                        assert len(data['recommendations']) == 1


class TestAIRecommendationsEndpoint:
    """Test /ai/assessments/recommendations endpoint integration."""
    
    @pytest.mark.asyncio
    async def test_ai_recommendations_endpoint_integration(self, mock_user):
        """Test AI recommendations endpoint calls ComplianceAssistant correctly."""
        
        with patch('api.dependencies.auth.get_current_active_user') as mock_auth:
            with patch('api.dependencies.database.get_async_db') as mock_db:
                with patch.object(ComplianceAssistant, 'get_assessment_recommendations') as mock_recommendations:
                    
                    # Setup mocks
                    mock_auth.return_value = mock_user
                    mock_db.return_value = AsyncMock()
                    
                    mock_recommendations.return_value = {
                        'recommendations': [
                            {
                                'id': 'rec1',
                                'title': 'Implement Data Mapping',
                                'description': 'Create comprehensive data mapping',
                                'priority': 'high',
                                'effort_estimate': '4-6 weeks',
                                'impact_score': 0.8,
                                'implementation_steps': [
                                    'Identify data sources',
                                    'Map data flows',
                                    'Document processes'
                                ]
                            }
                        ],
                        'implementation_plan': {
                            'phases': [
                                {
                                    'phase_number': 1,
                                    'phase_name': 'Assessment',
                                    'duration_weeks': 2,
                                    'tasks': ['Review current state'],
                                    'dependencies': []
                                }
                            ],
                            'total_timeline_weeks': 12,
                            'resource_requirements': ['Compliance team']
                        },
                        'success_metrics': ['Data mapping completed'],
                        'request_id': 'recommendations_123',
                        'generated_at': '2024-01-01T00:00:00Z',
                        'framework_id': 'general'
                    }
                    
                    # Make request
                    async with AsyncClient(app=app, base_url="http://test") as client:
                        response = await client.post(
                            "/api/ai/assessments/recommendations",
                            json={
                                "gaps": [
                                    {"id": "gap1", "title": "Missing data mapping"}
                                ],
                                "business_profile": {
                                    "name": "Test Company",
                                    "industry": "technology"
                                },
                                "existing_policies": ["security_policy"],
                                "industry_context": "technology",
                                "timeline_preferences": "standard"
                            },
                            headers={"Authorization": "Bearer test_token"}
                        )
                    
                    # Verify ComplianceAssistant was called correctly
                    mock_recommendations.assert_called_once()
                    call_args = mock_recommendations.call_args
                    assert len(call_args[1]['gaps']) == 1
                    assert call_args[1]['business_profile']['name'] == 'Test Company'
                    
                    # Verify response
                    assert response.status_code == 200
                    data = response.json()
                    assert len(data['recommendations']) == 1
                    assert 'implementation_plan' in data


if __name__ == "__main__":
    pytest.main([__file__])
