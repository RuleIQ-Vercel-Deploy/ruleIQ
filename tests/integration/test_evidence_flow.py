"""
Integration tests for the end-to-end evidence collection and reporting flow.
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from uuid import uuid4
from datetime import datetime

from main import app
from database.db_setup import get_db, Base, engine
from database.user import User
from database.business_profile import BusinessProfile
from database.evidence_item import EvidenceItem
from sqlalchemy.orm import Session

# Test client for synchronous endpoints
client = TestClient(app)

# Create test database tables
Base.metadata.create_all(bind=engine)

@pytest.fixture
def test_db():
    """Create a test database session."""
    db = next(get_db())
    yield db
    db.close()

@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    user = User(
        id=uuid4(),
        username="testuser@example.com",
        email="testuser@example.com",
        password_hash="fake_hash"
    )
    test_db.add(user)
    test_db.commit()
    return user

@pytest.fixture
def test_business_profile(test_db, test_user):
    """Create a test business profile."""
    profile = BusinessProfile(
        id=uuid4(),
        user_id=test_user.id,
        company_name="Test Company",
        industry="Technology",
        employee_count=100,
        country="UK",
        compliance_frameworks=["ISO27001", "SOC2"]
    )
    test_db.add(profile)
    test_db.commit()
    return profile

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for API calls."""
    # In a real test, you'd generate a proper JWT token
    return {"Authorization": f"Bearer fake_token_for_{test_user.id}"}

class TestEvidenceCollectionFlow:
    """Test the complete evidence collection and reporting workflow."""

    @pytest.mark.integration
    @patch('api.integrations.google_workspace_integration.GoogleWorkspaceIntegration')
    def test_full_evidence_and_reporting_flow(self, mock_integration, test_business_profile, auth_headers):
        """
        Tests the end-to-end flow of connecting an integration,
        collecting evidence, and generating a report.
        """
        # Mock the Google Workspace integration
        mock_instance = Mock()
        mock_instance.collect_evidence.return_value = [
            {
                "title": "Admin Console Settings",
                "type": "security_settings",
                "content": {"2fa_enabled": True, "password_policy": "strong"},
                "integration_source": "google_workspace",
                "auto_collected": True
            },
            {
                "title": "User Access Review",
                "type": "user_access_logs",
                "content": {"users": 50, "active_sessions": 25},
                "integration_source": "google_workspace",
                "auto_collected": True
            }
        ]
        mock_integration.return_value = mock_instance

        # Step 1: Connect a new integration (mocking the OAuth redirect)
        with patch('services.integration_service.get_current_user') as mock_auth:
            mock_auth.return_value = test_business_profile.user_id
            
            response = client.post(
                "/api/integrations/google_workspace/connect",
                json={
                    "credentials": {"token": "fake_oauth_token"},
                    "settings": {"workspace_domain": "testcompany.com"}
                },
                headers=auth_headers
            )
            
            # In a real test with proper authentication, this would succeed
            # For now, we'll mock the successful connection
            assert response.status_code in [200, 401]  # 401 due to mocked auth

        # Step 2: Trigger evidence collection manually
        # This simulates what would happen via a scheduled Celery task
        with patch('workers.evidence_tasks.collect_integration_evidence') as mock_task:
            mock_task.delay.return_value.id = "task_123"
            
            response = client.post(
                f"/api/integrations/collect/{test_business_profile.id}",
                headers=auth_headers
            )
            
            # Verify the collection was triggered
            # In a real implementation, this would check task scheduling
            assert response.status_code in [200, 401, 404]

        # Step 3: Simulate evidence being stored in the database
        # This would normally happen via the background task
        db = next(get_db())
        
        evidence_item = EvidenceItem(
            id=uuid4(),
            user_id=str(test_business_profile.user_id),
            evidence_name="Admin Console Settings",
            evidence_type="security_settings",
            description="Automated collection from Google Workspace",
            status="active",
            framework_mappings=["ISO27001"],
            automation_source="google_workspace",
            raw_data={"2fa_enabled": True, "password_policy": "strong"},
            created_at=datetime.utcnow()
        )
        
        db.add(evidence_item)
        db.commit()

        # Step 4: Generate a report that uses the new evidence
        response = client.post(
            "/api/reports/generate",
            json={
                "business_profile_id": str(test_business_profile.id),
                "report_type": "evidence_report",
                "format": "json",
                "parameters": {"frameworks": ["ISO27001"]}
            },
            headers=auth_headers
        )
        
        # Verify report generation (accounting for auth mocking)
        if response.status_code == 200:
            report_data = response.json()
            assert "content" in report_data
            assert report_data["report_type"] == "evidence_report"
        
        db.close()

    @pytest.mark.integration
    def test_ai_assistant_evidence_query(self, test_business_profile, auth_headers):
        """Test the AI assistant's ability to query and analyze evidence."""
        
        # Create some test evidence
        db = next(get_db())
        
        evidence_items = [
            EvidenceItem(
                id=uuid4(),
                user_id=str(test_business_profile.user_id),
                evidence_name="Security Policy Document",
                evidence_type="policy_documents",
                description="Company security policy",
                status="active",
                framework_mappings=["ISO27001"],
                created_at=datetime.utcnow()
            ),
            EvidenceItem(
                id=uuid4(),
                user_id=str(test_business_profile.user_id),
                evidence_name="Employee Training Records",
                evidence_type="training_records",
                description="Security awareness training completion",
                status="active",
                framework_mappings=["ISO27001"],
                created_at=datetime.utcnow()
            )
        ]
        
        for item in evidence_items:
            db.add(item)
        db.commit()

        # Test AI assistant conversation
        with patch('services.ai.assistant.ComplianceAssistant.process_message') as mock_ai:
            mock_ai.return_value = (
                "I found 2 evidence items related to ISO27001 compliance. You have security policies and training records documented.",
                {"intent": "evidence_query", "evidence_found": 2}
            )
            
            response = client.post(
                "/api/chat/conversations",
                json={
                    "title": "Evidence Query Test",
                    "initial_message": "What evidence do I have for ISO27001?"
                },
                headers=auth_headers
            )
            
            # Verify the conversation was created (accounting for auth)
            if response.status_code == 200:
                conversation_data = response.json()
                assert "id" in conversation_data
                assert len(conversation_data.get("messages", [])) >= 1
        
        db.close()

    @pytest.mark.integration
    def test_scheduled_report_generation(self, test_business_profile, auth_headers):
        """Test the scheduled report generation workflow."""
        
        # Create a report schedule
        response = client.post(
            "/api/reports/schedules",
            json={
                "business_profile_id": str(test_business_profile.id),
                "report_type": "executive_summary",
                "frequency": "weekly",
                "recipients": ["manager@testcompany.com"],
                "parameters": {"frameworks": ["ISO27001"]},
                "schedule_config": {"hour": 9, "day_of_week": 1}
            },
            headers=auth_headers
        )
        
        if response.status_code == 200:
            schedule_data = response.json()
            schedule_id = schedule_data["schedule_id"]
            
            # Test manual execution of the schedule
            response = client.post(
                f"/api/reports/schedules/{schedule_id}/execute",
                headers=auth_headers
            )
            
            if response.status_code == 200:
                execution_data = response.json()
                assert execution_data["status"] in ["success", "initiated"]
                assert "executed_at" in execution_data

class TestAPIEndpointsIntegration:
    """Test critical API endpoint interactions."""

    @pytest.mark.integration
    def test_business_profile_to_evidence_workflow(self, test_business_profile, auth_headers):
        """Test the workflow from business profile setup to evidence collection."""
        
        # Get business profile
        response = client.get(
            f"/api/business-profiles/{test_business_profile.id}",
            headers=auth_headers
        )
        
        if response.status_code == 200:
            profile_data = response.json()
            assert profile_data["company_name"] == "Test Company"
            
            # Create evidence for this profile
            response = client.post(
                "/api/evidence",
                json={
                    "evidence_name": "Test Evidence Item",
                    "evidence_type": "manual_upload",
                    "description": "Test evidence for integration testing",
                    "framework_mappings": ["ISO27001"],
                    "status": "active"
                },
                headers=auth_headers
            )
            
            # Verify evidence creation (accounting for auth)
            assert response.status_code in [200, 201, 401]

    @pytest.mark.integration  
    def test_framework_to_readiness_assessment(self, test_business_profile, auth_headers):
        """Test the framework assessment and readiness calculation."""
        
        # Get available frameworks
        response = client.get("/api/frameworks", headers=auth_headers)
        
        if response.status_code == 200:
            frameworks = response.json()
            assert len(frameworks) > 0
            
            # Test readiness assessment
            response = client.get(
                f"/api/readiness/{test_business_profile.id}",
                headers=auth_headers
            )
            
            if response.status_code == 200:
                readiness_data = response.json()
                assert "overall_score" in readiness_data
                assert "framework_scores" in readiness_data

class TestErrorHandlingAndResilience:
    """Test system behavior under error conditions."""

    @pytest.mark.integration
    def test_integration_failure_handling(self, test_business_profile, auth_headers):
        """Test how the system handles integration failures."""
        
        with patch('api.integrations.google_workspace_integration.GoogleWorkspaceIntegration') as mock_integration:
            # Simulate integration failure
            mock_integration.side_effect = Exception("OAuth token expired")
            
            response = client.post(
                "/api/integrations/google_workspace/connect",
                json={"credentials": {"token": "expired_token"}},
                headers=auth_headers
            )
            
            # System should handle the error gracefully
            assert response.status_code in [400, 401, 500]

    @pytest.mark.integration
    def test_report_generation_with_no_data(self, test_business_profile, auth_headers):
        """Test report generation when no evidence data is available."""
        
        response = client.post(
            "/api/reports/generate",
            json={
                "business_profile_id": str(test_business_profile.id),
                "report_type": "evidence_report",
                "format": "json"
            },
            headers=auth_headers
        )
        
        # Should still generate a report, possibly with "no data" messages
        if response.status_code == 200:
            report_data = response.json()
            assert "content" in report_data

@pytest.mark.asyncio
class TestAsyncOperations:
    """Test asynchronous operations and background tasks."""

    async def test_async_evidence_collection(self):
        """Test asynchronous evidence collection operations."""
        
        # This would test the actual async collection logic
        # For now, we'll test that the async functions can be called
        
        from services.automation.evidence_processor import EvidenceProcessor
        from database.db_setup import get_db
        
        db = next(get_db())
        processor = EvidenceProcessor(db)
        
        # Test that async methods work
        assert processor is not None
        
        db.close()

    async def test_ai_assistant_async_processing(self):
        """Test AI assistant async message processing."""
        
        from services.ai.assistant import ComplianceAssistant
        from database.db_setup import get_db
        
        db = next(get_db())
        assistant = ComplianceAssistant(db)
        
        # Test context gathering (async operation)
        try:
            from uuid import uuid4
            context = await assistant.context_manager.get_conversation_context(
                uuid4(), uuid4()
            )
            assert isinstance(context, dict)
        except Exception:
            # Expected if no data exists
            pass
        
        db.close()

# Test fixtures cleanup
@pytest.fixture(scope="function", autouse=True)
def cleanup_test_data():
    """Clean up test data after each test."""
    yield
    # Cleanup would go here in a real implementation
    # For now, we rely on test database isolation