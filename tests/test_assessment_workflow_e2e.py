"""
End-to-end tests for assessment workflow with ComplianceAssistant integration (Phase 2.2).

Tests the complete assessment workflow from question help to final recommendations.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from fastapi.testclient import TestClient
from httpx import AsyncClient

from main import app
from database.user import User
from database.business_profile import BusinessProfile
from services.ai.assistant import ComplianceAssistant


@pytest.fixture
def test_user():
    """Create test user."""
    user = User()
    user.id = uuid4()
    user.email = "test@example.com"
    user.is_active = True
    return user


@pytest.fixture
def test_business_profile():
    """Create test business profile."""
    profile = BusinessProfile()
    profile.id = uuid4()
    profile.company_name = "Test Company"
    profile.industry = "Technology"
    profile.employee_count = 50
    profile.data_types = ["personal_data", "financial_data"]
    return profile


class TestCompleteAssessmentWorkflow:
    """Test complete assessment workflow with AI integration."""
    
    @pytest.mark.asyncio
    async def test_complete_gdpr_assessment_workflow(self, test_user, test_business_profile):
        """Test complete GDPR assessment workflow from start to finish."""
        
        # Mock all dependencies
        with patch('api.dependencies.auth.get_current_active_user') as mock_auth:
            with patch('api.dependencies.database.get_async_db') as mock_db:
                with patch('api.routers.ai_assessments.get_user_business_profile') as mock_get_profile:
                    
                    # Setup common mocks
                    mock_auth.return_value = test_user
                    mock_db.return_value = AsyncMock()
                    mock_get_profile.return_value = test_business_profile
                    
                    async with AsyncClient(app=app, base_url="http://test") as client:
                        
                        # Step 1: Get help for first assessment question
                        with patch.object(ComplianceAssistant, 'get_assessment_help') as mock_help:
                            mock_help.return_value = {
                                'guidance': 'GDPR applies to organizations that process personal data of EU residents.',
                                'confidence_score': 0.95,
                                'related_topics': ['personal data', 'data processing'],
                                'follow_up_suggestions': ['Review data collection practices'],
                                'source_references': ['GDPR Article 2'],
                                'request_id': 'help_gdpr_q1',
                                'generated_at': '2024-01-01T00:00:00Z',
                                'framework_id': 'gdpr',
                                'question_id': 'gdpr_scope'
                            }
                            
                            help_response = await client.post(
                                "/api/ai/assessments/gdpr/help",
                                json={
                                    "question_id": "gdpr_scope",
                                    "question_text": "Does GDPR apply to our organization?",
                                    "framework_id": "gdpr",
                                    "section_id": "scope",
                                    "user_context": {"assessment_stage": 1}
                                },
                                headers={"Authorization": "Bearer test_token"}
                            )
                            
                            assert help_response.status_code == 200
                            help_data = help_response.json()
                            assert 'GDPR applies to organizations' in help_data['guidance']
                            assert help_data['confidence_score'] >= 0.9
                        
                        # Step 2: Generate follow-up questions based on initial answers
                        with patch.object(ComplianceAssistant, 'generate_assessment_followup') as mock_followup:
                            mock_followup.return_value = {
                                'follow_up_questions': [
                                    'What types of personal data do you collect?',
                                    'Do you transfer data outside the EU?',
                                    'Do you have a Data Protection Officer?'
                                ],
                                'recommendations': [
                                    'Conduct data mapping exercise',
                                    'Review data transfer mechanisms'
                                ],
                                'confidence_score': 0.85,
                                'request_id': 'followup_gdpr_123',
                                'generated_at': '2024-01-01T00:00:00Z',
                                'framework_id': 'gdpr'
                            }
                            
                            followup_response = await client.post(
                                "/api/ai/assessments/followup",
                                json={
                                    "framework_id": "gdpr",
                                    "current_answers": {
                                        "gdpr_scope": "yes",
                                        "data_subjects": "eu_residents",
                                        "processing_purpose": "customer_management"
                                    },
                                    "business_context": {
                                        "assessment_progress": 25,
                                        "current_stage": "data_mapping"
                                    },
                                    "max_questions": 3
                                },
                                headers={"Authorization": "Bearer test_token"}
                            )
                            
                            assert followup_response.status_code == 200
                            followup_data = followup_response.json()
                            assert len(followup_data['questions']) == 3
                            assert any('personal data' in q['text'] for q in followup_data['questions'])
                        
                        # Step 3: Analyze completed assessment results
                        with patch.object(ComplianceAssistant, 'analyze_assessment_results') as mock_analysis:
                            mock_analysis.return_value = {
                                'gaps': [
                                    {
                                        'id': 'privacy_policy_gap',
                                        'title': 'Missing Privacy Policy',
                                        'description': 'No comprehensive privacy policy found',
                                        'severity': 'high',
                                        'category': 'documentation'
                                    },
                                    {
                                        'id': 'data_mapping_gap',
                                        'title': 'Incomplete Data Mapping',
                                        'description': 'Data flows not fully documented',
                                        'severity': 'medium',
                                        'category': 'process'
                                    }
                                ],
                                'recommendations': [
                                    {
                                        'id': 'privacy_policy_rec',
                                        'title': 'Create Comprehensive Privacy Policy',
                                        'description': 'Develop GDPR-compliant privacy policy',
                                        'priority': 'high',
                                        'effort_estimate': '2-3 weeks',
                                        'impact_score': 0.9
                                    }
                                ],
                                'risk_assessment': {
                                    'level': 'medium-high',
                                    'description': 'Several critical gaps identified that need immediate attention'
                                },
                                'compliance_insights': {
                                    'summary': 'Organization shows good awareness but lacks key documentation',
                                    'key_findings': [
                                        'Strong technical controls',
                                        'Weak documentation practices',
                                        'Need for staff training'
                                    ]
                                },
                                'evidence_requirements': [
                                    {
                                        'type': 'policy',
                                        'title': 'Privacy Policy',
                                        'description': 'GDPR-compliant privacy policy'
                                    }
                                ],
                                'request_id': 'analysis_gdpr_456',
                                'generated_at': '2024-01-01T00:00:00Z',
                                'framework_id': 'gdpr'
                            }
                            
                            analysis_response = await client.post(
                                "/api/ai/assessments/analysis",
                                json={
                                    "framework_id": "gdpr",
                                    "assessment_results": {
                                        "gdpr_scope": "yes",
                                        "data_subjects": "eu_residents",
                                        "privacy_policy": "missing",
                                        "data_mapping": "partial",
                                        "consent_mechanisms": "basic",
                                        "data_retention": "undefined",
                                        "breach_procedures": "informal"
                                    },
                                    "business_profile_id": str(test_business_profile.id)
                                },
                                headers={"Authorization": "Bearer test_token"}
                            )
                            
                            assert analysis_response.status_code == 200
                            analysis_data = analysis_response.json()
                            assert len(analysis_data['gaps']) == 2
                            assert analysis_data['risk_assessment']['level'] == 'medium-high'
                            assert 'privacy policy' in analysis_data['gaps'][0]['title'].lower()
                        
                        # Step 4: Generate personalized implementation recommendations
                        with patch.object(ComplianceAssistant, 'get_assessment_recommendations') as mock_recommendations:
                            mock_recommendations.return_value = {
                                'recommendations': [
                                    {
                                        'id': 'privacy_policy_impl',
                                        'title': 'Implement Privacy Policy',
                                        'description': 'Create and publish comprehensive privacy policy',
                                        'priority': 'high',
                                        'effort_estimate': '3-4 weeks',
                                        'impact_score': 0.9,
                                        'resources': ['Legal team', 'Compliance officer'],
                                        'implementation_steps': [
                                            'Review current data processing activities',
                                            'Draft privacy policy content',
                                            'Legal review and approval',
                                            'Publish and communicate to users'
                                        ]
                                    },
                                    {
                                        'id': 'data_mapping_impl',
                                        'title': 'Complete Data Mapping',
                                        'description': 'Document all data flows and processing activities',
                                        'priority': 'medium',
                                        'effort_estimate': '2-3 weeks',
                                        'impact_score': 0.7,
                                        'resources': ['IT team', 'Business analysts'],
                                        'implementation_steps': [
                                            'Identify all data sources',
                                            'Map data flows',
                                            'Document processing purposes',
                                            'Create data inventory'
                                        ]
                                    }
                                ],
                                'implementation_plan': {
                                    'phases': [
                                        {
                                            'phase_number': 1,
                                            'phase_name': 'Documentation Phase',
                                            'duration_weeks': 4,
                                            'tasks': [
                                                'Create privacy policy',
                                                'Complete data mapping'
                                            ],
                                            'dependencies': []
                                        },
                                        {
                                            'phase_number': 2,
                                            'phase_name': 'Implementation Phase',
                                            'duration_weeks': 6,
                                            'tasks': [
                                                'Deploy privacy controls',
                                                'Train staff'
                                            ],
                                            'dependencies': ['Phase 1']
                                        }
                                    ],
                                    'total_timeline_weeks': 10,
                                    'resource_requirements': [
                                        'Compliance officer (0.5 FTE)',
                                        'Legal support (0.2 FTE)',
                                        'IT support (0.3 FTE)'
                                    ]
                                },
                                'success_metrics': [
                                    'Privacy policy published',
                                    'Data mapping 100% complete',
                                    'Staff training completion rate >90%',
                                    'Zero privacy policy complaints'
                                ],
                                'request_id': 'recommendations_gdpr_789',
                                'generated_at': '2024-01-01T00:00:00Z',
                                'framework_id': 'general'
                            }
                            
                            recommendations_response = await client.post(
                                "/api/ai/assessments/recommendations",
                                json={
                                    "gaps": [
                                        {
                                            "id": "privacy_policy_gap",
                                            "title": "Missing Privacy Policy",
                                            "severity": "high"
                                        },
                                        {
                                            "id": "data_mapping_gap", 
                                            "title": "Incomplete Data Mapping",
                                            "severity": "medium"
                                        }
                                    ],
                                    "business_profile": {
                                        "name": "Test Company",
                                        "industry": "technology",
                                        "employee_count": 50,
                                        "budget_range": "25K-50K"
                                    },
                                    "existing_policies": ["security_policy", "acceptable_use_policy"],
                                    "industry_context": "technology",
                                    "timeline_preferences": "standard"
                                },
                                headers={"Authorization": "Bearer test_token"}
                            )
                            
                            assert recommendations_response.status_code == 200
                            rec_data = recommendations_response.json()
                            assert len(rec_data['recommendations']) == 2
                            assert rec_data['implementation_plan']['total_timeline_weeks'] == 10
                            assert len(rec_data['success_metrics']) == 4
                            
                            # Verify high-priority recommendation is first
                            assert rec_data['recommendations'][0]['priority'] == 'high'
                            assert 'privacy policy' in rec_data['recommendations'][0]['title'].lower()
        
        # Verify the complete workflow provides coherent results
        assert help_data['framework_id'] == 'gdpr'
        assert len(followup_data['questions']) > 0
        assert len(analysis_data['gaps']) > 0
        assert len(rec_data['recommendations']) > 0
        
        # Verify workflow continuity
        assert analysis_data['framework_id'] == 'gdpr'
        assert any('privacy' in gap['title'].lower() for gap in analysis_data['gaps'])
        assert any('privacy' in rec['title'].lower() for rec in rec_data['recommendations'])


if __name__ == "__main__":
    pytest.main([__file__])
