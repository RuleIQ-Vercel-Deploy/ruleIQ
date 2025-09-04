"""
Comprehensive integration tests for critical user workflows.
QA Specialist - Day 4 Coverage Enhancement
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
import json

from database.user import User
from api.main import app


@pytest.fixture
def test_client():
    """Create test client for API testing."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers for protected endpoints."""
    token = "test_jwt_token"
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_user_data():
    """Create sample user registration data."""
    return {
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User",
        "company_name": "Test Company",
        "role": "compliance_officer"
    }


class TestUserRegistrationWorkflow:
    """Test complete user registration and onboarding workflow."""

    @pytest.mark.asyncio
    async def test_complete_registration_flow(self, test_client, sample_user_data):
        """Test end-to-end user registration flow."""
        # Step 1: Register new user
        with patch('api.routers.auth.create_user', new_callable=AsyncMock) as mock_create:
            mock_user = MagicMock()
            mock_user.id = uuid4()
            mock_user.email = sample_user_data["email"]
            mock_create.return_value = mock_user
            
            response = test_client.post("/api/auth/register", json=sample_user_data)
            assert response.status_code == 201
            user_data = response.json()
            assert "user_id" in user_data
            assert "message" in user_data

        # Step 2: Verify email
        verification_token = "verification_token_123"
        with patch('api.routers.auth.verify_email_token', new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = True
            
            response = test_client.post(
                f"/api/auth/verify-email?token={verification_token}"
            )
            assert response.status_code == 200
            assert response.json()["verified"] is True

        # Step 3: Login
        with patch('api.routers.auth.authenticate_user', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = mock_user
            with patch('api.routers.auth.create_access_token') as mock_token:
                mock_token.return_value = "access_token_123"
                
                response = test_client.post("/api/auth/login", data={
                    "username": sample_user_data["email"],
                    "password": sample_user_data["password"]
                })
                assert response.status_code == 200
                token_data = response.json()
                assert "access_token" in token_data
                assert token_data["token_type"] == "bearer"

        # Step 4: Complete profile
        profile_data = {
            "industry": "Healthcare",
            "company_size": "50-250",
            "location": "United States",
            "compliance_frameworks": ["HIPAA", "GDPR"]
        }
        
        with patch('api.routers.business_profiles.create_profile', 
                   new_callable=AsyncMock) as mock_profile:
            mock_profile.return_value = {**profile_data, "id": str(uuid4())}
            
            response = test_client.post(
                "/api/business-profiles",
                json=profile_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            assert response.json()["industry"] == "Healthcare"

    @pytest.mark.asyncio
    async def test_registration_with_existing_email(self, test_client, sample_user_data):
        """Test registration with already registered email."""
        with patch('api.routers.auth.get_user_by_email', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = MagicMock()  # User exists
            
            response = test_client.post("/api/auth/register", json=sample_user_data)
            assert response.status_code == 400
            assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_registration_with_weak_password(self, test_client):
        """Test registration with weak password."""
        weak_user_data = {
            "email": "test@example.com",
            "password": "weak",
            "full_name": "Test User"
        }
        
        response = test_client.post("/api/auth/register", json=weak_user_data)
        assert response.status_code == 422
        assert "password" in str(response.json()["detail"]).lower()


class TestComplianceAssessmentWorkflow:
    """Test complete compliance assessment workflow."""

    @pytest.mark.asyncio
    async def test_complete_assessment_flow(self, test_client, auth_headers):
        """Test end-to-end compliance assessment workflow."""
        # Step 1: Start assessment
        assessment_data = {
            "framework": "GDPR",
            "assessment_type": "initial",
            "scope": ["data_processing", "user_rights", "security"]
        }
        
        with patch('api.routers.assessments.create_assessment', 
                   new_callable=AsyncMock) as mock_create:
            assessment_id = uuid4()
            mock_create.return_value = {
                "id": str(assessment_id),
                "status": "in_progress",
                **assessment_data
            }
            
            response = test_client.post(
                "/api/assessments/start",
                json=assessment_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            assessment = response.json()
            assert assessment["status"] == "in_progress"

        # Step 2: Answer assessment questions
        answers = [
            {"question_id": str(uuid4()), "answer": "yes", "notes": "Implemented"},
            {"question_id": str(uuid4()), "answer": "no", "notes": "Not yet implemented"},
            {"question_id": str(uuid4()), "answer": "partial", "notes": "In progress"}
        ]
        
        with patch('api.routers.assessments.save_answers', 
                   new_callable=AsyncMock) as mock_save:
            mock_save.return_value = {"saved": len(answers)}
            
            response = test_client.post(
                f"/api/assessments/{assessment_id}/answers",
                json={"answers": answers},
                headers=auth_headers
            )
            assert response.status_code == 200
            assert response.json()["saved"] == 3

        # Step 3: Complete assessment
        with patch('api.routers.assessments.complete_assessment', 
                   new_callable=AsyncMock) as mock_complete:
            mock_complete.return_value = {
                "id": str(assessment_id),
                "status": "completed",
                "score": 75,
                "recommendations": ["Implement data encryption", "Update privacy policy"]
            }
            
            response = test_client.post(
                f"/api/assessments/{assessment_id}/complete",
                headers=auth_headers
            )
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "completed"
            assert result["score"] == 75

        # Step 4: Generate report
        with patch('api.routers.reports.generate_assessment_report', 
                   new_callable=AsyncMock) as mock_report:
            report_id = uuid4()
            mock_report.return_value = {
                "id": str(report_id),
                "report_type": "assessment",
                "format": "pdf",
                "status": "generated"
            }
            
            response = test_client.post(
                f"/api/assessments/{assessment_id}/report",
                json={"format": "pdf"},
                headers=auth_headers
            )
            assert response.status_code == 201
            report = response.json()
            assert report["report_type"] == "assessment"


class TestPolicyGenerationWorkflow:
    """Test complete policy generation and management workflow."""

    @pytest.mark.asyncio
    async def test_complete_policy_workflow(self, test_client, auth_headers):
        """Test end-to-end policy generation workflow."""
        # Step 1: Generate policy
        policy_request = {
            "framework_id": str(uuid4()),
            "policy_type": "comprehensive",
            "custom_requirements": [
                "Include remote work policies",
                "Cover third-party vendors"
            ]
        }
        
        with patch('api.routers.policies.generate_compliance_policy', 
                   new_callable=AsyncMock) as mock_generate:
            policy_id = uuid4()
            mock_generate.return_value = MagicMock(
                id=policy_id,
                policy_name="GDPR Compliance Policy",
                policy_content="Policy content...",
                status="draft",
                sections=["Introduction", "Data Protection", "User Rights"]
            )
            
            response = test_client.post(
                "/api/policies/generate",
                json=policy_request,
                headers=auth_headers
            )
            assert response.status_code == 201
            policy = response.json()
            assert policy["status"] == "draft"

        # Step 2: Review and edit policy
        updates = {
            "policy_content": "Updated policy content with custom sections",
            "sections": ["Introduction", "Data Protection", "User Rights", "Remote Work"]
        }
        
        with patch('api.routers.policies.update_policy', 
                   new_callable=AsyncMock) as mock_update:
            mock_update.return_value = MagicMock(**updates)
            
            response = test_client.patch(
                f"/api/policies/{policy_id}",
                json=updates,
                headers=auth_headers
            )
            assert response.status_code == 200
            updated_policy = response.json()
            assert len(updated_policy["sections"]) == 4

        # Step 3: Validate policy
        with patch('api.routers.policies.validate_policy', 
                   new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {
                "is_valid": True,
                "completeness": 95,
                "warnings": ["Consider adding more detail to section 3"]
            }
            
            response = test_client.post(
                f"/api/policies/{policy_id}/validate",
                headers=auth_headers
            )
            assert response.status_code == 200
            validation = response.json()
            assert validation["is_valid"] is True
            assert validation["completeness"] == 95

        # Step 4: Approve policy
        with patch('api.routers.policies.approve_policy', 
                   new_callable=AsyncMock) as mock_approve:
            mock_approve.return_value = MagicMock(status="approved")
            
            response = test_client.post(
                f"/api/policies/{policy_id}/approve",
                headers=auth_headers
            )
            assert response.status_code == 200
            assert response.json()["status"] == "approved"

        # Step 5: Export policy
        with patch('api.routers.policies.export_policy', 
                   new_callable=AsyncMock) as mock_export:
            mock_export.return_value = b"PDF content"
            
            response = test_client.get(
                f"/api/policies/{policy_id}/export?format=pdf",
                headers=auth_headers
            )
            assert response.status_code == 200
            assert response.content == b"PDF content"


class TestIntegrationManagementWorkflow:
    """Test complete integration setup and management workflow."""

    @pytest.mark.asyncio
    async def test_slack_integration_workflow(self, test_client, auth_headers):
        """Test Slack integration setup workflow."""
        # Step 1: Check available integrations
        with patch('api.routers.integrations.list_available', 
                   new_callable=AsyncMock) as mock_available:
            mock_available.return_value = [
                {"type": "slack", "name": "Slack", "auth_type": "webhook"},
                {"type": "teams", "name": "Microsoft Teams", "auth_type": "oauth"}
            ]
            
            response = test_client.get("/api/integrations/available", headers=auth_headers)
            assert response.status_code == 200
            available = response.json()
            assert len(available["integrations"]) >= 2

        # Step 2: Setup Slack integration
        slack_config = {
            "type": "slack",
            "name": "Compliance Notifications",
            "configuration": {
                "webhook_url": "https://hooks.slack.com/services/XXX",
                "channel": "#compliance",
                "notifications": ["assessments", "policies", "reports"]
            }
        }
        
        with patch('api.routers.integrations.setup_integration', 
                   new_callable=AsyncMock) as mock_setup:
            integration_id = uuid4()
            mock_setup.return_value = {
                "id": str(integration_id),
                "status": "connected",
                **slack_config
            }
            
            response = test_client.post(
                "/api/integrations",
                json=slack_config,
                headers=auth_headers
            )
            assert response.status_code == 201
            integration = response.json()
            assert integration["status"] == "connected"

        # Step 3: Test connection
        with patch('api.routers.integrations.test_connection', 
                   new_callable=AsyncMock) as mock_test:
            mock_test.return_value = {
                "status": "success",
                "message": "Test message sent successfully",
                "latency_ms": 150
            }
            
            response = test_client.post(
                f"/api/integrations/{integration_id}/test",
                headers=auth_headers
            )
            assert response.status_code == 200
            test_result = response.json()
            assert test_result["status"] == "success"

        # Step 4: Configure webhooks
        webhook_config = {
            "url": "https://example.com/webhook",
            "events": ["assessment.completed", "policy.approved"],
            "secret": "webhook_secret_123"
        }
        
        with patch('api.routers.integrations.add_webhook', 
                   new_callable=AsyncMock) as mock_webhook:
            webhook_id = uuid4()
            mock_webhook.return_value = {
                "id": str(webhook_id),
                "active": True,
                **webhook_config
            }
            
            response = test_client.post(
                f"/api/integrations/{integration_id}/webhooks",
                json=webhook_config,
                headers=auth_headers
            )
            assert response.status_code == 201
            webhook = response.json()
            assert webhook["active"] is True

        # Step 5: Sync data
        with patch('api.routers.integrations.sync_data', 
                   new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = {
                "status": "completed",
                "records_synced": 150,
                "duration_seconds": 3.5
            }
            
            response = test_client.post(
                f"/api/integrations/{integration_id}/sync",
                headers=auth_headers
            )
            assert response.status_code == 200
            sync_result = response.json()
            assert sync_result["records_synced"] == 150


class TestReportingWorkflow:
    """Test complete reporting workflow."""

    @pytest.mark.asyncio
    async def test_scheduled_report_workflow(self, test_client, auth_headers):
        """Test scheduled report generation workflow."""
        # Step 1: Create report schedule
        schedule_data = {
            "report_type": "compliance_summary",
            "schedule": "weekly",
            "day_of_week": "monday",
            "time": "09:00",
            "format": "pdf",
            "recipients": ["compliance@example.com"],
            "parameters": {
                "frameworks": ["GDPR", "CCPA"],
                "include_recommendations": True
            }
        }
        
        with patch('api.routers.reports.create_report_schedule', 
                   new_callable=AsyncMock) as mock_schedule:
            schedule_id = uuid4()
            mock_schedule.return_value = {
                "id": str(schedule_id),
                "active": True,
                **schedule_data,
                "next_run": "2024-02-05 09:00:00"
            }
            
            response = test_client.post(
                "/api/reports/schedule",
                json=schedule_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            schedule = response.json()
            assert schedule["active"] is True

        # Step 2: Trigger manual report generation
        with patch('api.routers.reports.generate_report_from_schedule', 
                   new_callable=AsyncMock) as mock_generate:
            report_id = uuid4()
            mock_generate.return_value = {
                "id": str(report_id),
                "status": "processing",
                "estimated_time": "5 minutes"
            }
            
            response = test_client.post(
                f"/api/reports/schedule/{schedule_id}/run",
                headers=auth_headers
            )
            assert response.status_code == 202
            report = response.json()
            assert report["status"] == "processing"

        # Step 3: Check report status
        with patch('api.routers.reports.check_report_status', 
                   new_callable=AsyncMock) as mock_status:
            mock_status.return_value = {
                "id": str(report_id),
                "status": "completed",
                "progress": 100,
                "file_size": 2048576
            }
            
            response = test_client.get(
                f"/api/reports/{report_id}/status",
                headers=auth_headers
            )
            assert response.status_code == 200
            status = response.json()
            assert status["status"] == "completed"

        # Step 4: Download report
        with patch('api.routers.reports.get_report_file', 
                   new_callable=AsyncMock) as mock_file:
            mock_file.return_value = b"PDF report content"
            
            response = test_client.get(
                f"/api/reports/{report_id}/download",
                headers=auth_headers
            )
            assert response.status_code == 200
            assert response.content == b"PDF report content"

        # Step 5: Share report
        share_data = {
            "recipient_emails": ["manager@example.com", "auditor@example.com"],
            "message": "Please review the compliance report",
            "expiry_days": 7
        }
        
        with patch('api.routers.reports.create_share_link', 
                   new_callable=AsyncMock) as mock_share:
            mock_share.return_value = {
                "share_id": str(uuid4()),
                "share_link": f"https://example.com/shared/{uuid4()}",
                "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
            
            response = test_client.post(
                f"/api/reports/{report_id}/share",
                json=share_data,
                headers=auth_headers
            )
            assert response.status_code == 200
            share_result = response.json()
            assert "share_link" in share_result