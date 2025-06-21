"""
Integration Tests for ComplianceGPT API Endpoints

This module tests API endpoints with full database integration,
authentication, and business logic flow validation.
"""

from uuid import uuid4

import pytest


@pytest.mark.integration
class TestAuthenticationEndpoints:
    """Test authentication and user management endpoints"""

    def test_user_registration_flow(self, client):
        """Test complete user registration process"""
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
            "full_name": "New User",
            "company": "Test Company Ltd"
        }

        # Register user
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201

        response_data = response.json()
        assert response_data["email"] == user_data["email"]
        assert "id" in response_data
        assert "password" not in response_data  # Password should not be returned

    def test_user_login_flow(self, client, sample_user):
        """Test user login and token generation"""
        # First register the user
        client.post("/api/auth/register", json=sample_user)

        # Then login
        login_data = {
            "email": sample_user["email"],
            "password": sample_user["password"]
        }

        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200

        response_data = response.json()
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert response_data["token_type"] == "bearer"

    def test_protected_endpoint_access(self, client, authenticated_headers):
        """Test accessing protected endpoints with valid token"""
        response = client.get("/api/users/me", headers=authenticated_headers)
        assert response.status_code == 200

        response_data = response.json()
        assert "id" in response_data
        assert "email" in response_data

    def test_invalid_login_credentials(self, client, sample_user):
        """Test login with invalid credentials"""
        # Register user first
        client.post("/api/auth/register", json=sample_user)

        # Try login with wrong password
        login_data = {
            "email": sample_user["email"],
            "password": "WrongPassword123!"
        }

        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401

        error_data = response.json()
        assert "error" in error_data


@pytest.mark.integration
class TestBusinessProfileEndpoints:
    """Test business profile management endpoints"""

    def test_create_business_profile(self, client, authenticated_headers, sample_business_profile_data):
        """Test creating a business profile"""
        response = client.post(
            "/api/business-profiles",
            headers=authenticated_headers,
            json=sample_business_profile_data
        )
        assert response.status_code == 201

        response_data = response.json()
        assert response_data["company_name"] == sample_business_profile_data["company_name"]
        assert response_data["industry"] == sample_business_profile_data["industry"]
        assert "id" in response_data
        assert "created_at" in response_data

    def test_get_business_profile(self, client, authenticated_headers, sample_business_profile_data):
        """Test retrieving a business profile"""
        # Create profile first
        create_response = client.post(
            "/api/business-profiles",
            headers=authenticated_headers,
            json=sample_business_profile_data
        )
        profile_id = create_response.json()["id"]

        # Retrieve profile
        response = client.get(f"/api/business-profiles/{profile_id}", headers=authenticated_headers)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["id"] == profile_id
        assert response_data["company_name"] == sample_business_profile_data["company_name"]

    def test_update_business_profile(self, client, authenticated_headers, sample_business_profile_data):
        """Test updating a business profile"""
        # Create profile first
        create_response = client.post(
            "/api/business-profiles",
            headers=authenticated_headers,
            json=sample_business_profile_data
        )
        profile_id = create_response.json()["id"]

        # Update profile
        update_data = {
            "employee_count": 75,
            "industry": "FinTech"
        }

        response = client.patch(
            f"/api/business-profiles/{profile_id}",
            headers=authenticated_headers,
            json=update_data
        )
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["employee_count"] == 75
        assert response_data["industry"] == "FinTech"

    def test_business_profile_validation(self, client, authenticated_headers):
        """Test business profile validation"""
        invalid_profile = {
            "company_name": "",  # Invalid: empty
            "industry": "x",  # Invalid: too short
            "employee_count": -1  # Invalid: negative
        }

        response = client.post(
            "/api/business-profiles",
            headers=authenticated_headers,
            json=invalid_profile
        )
        assert response.status_code == 422

        error_data = response.json()
        assert "detail" in error_data  # FastAPI returns validation errors in "detail" field


@pytest.mark.integration
class TestAssessmentEndpoints:
    """Test assessment and questionnaire endpoints"""

    def test_create_assessment_session(self, client, authenticated_headers):
        """Test creating an assessment session"""
        session_data = {
            "session_type": "compliance_scoping"
        }

        response = client.post(
            "/api/assessments",
            headers=authenticated_headers,
            json=session_data
        )
        assert response.status_code == 201

        response_data = response.json()
        assert response_data["session_type"] == "compliance_scoping"
        assert response_data["status"] == "in_progress"
        assert "id" in response_data

    def test_get_assessment_questions(self, client, authenticated_headers):
        """Test retrieving assessment questions"""
        # Create session first
        session_response = client.post(
            "/api/assessments",
            headers=authenticated_headers,
            json={"session_type": "compliance_scoping"}
        )
        session_id = session_response.json()["id"]

        # Get questions
        response = client.get(f"/api/assessments/{session_id}/questions", headers=authenticated_headers)
        assert response.status_code == 200

        response_data = response.json()
        assert "questions" in response_data
        assert len(response_data["questions"]) > 0

    def test_submit_assessment_response(self, client, authenticated_headers):
        """Test submitting assessment responses"""
        # Create session
        session_response = client.post(
            "/api/assessments",
            headers=authenticated_headers,
            json={"session_type": "compliance_scoping"}
        )
        session_id = session_response.json()["id"]

        # Submit response
        response_data = {
            "question_id": "data_processing",
            "response": "Yes, we process customer personal data",
            "move_to_next_stage": False
        }

        response = client.post(
            f"/api/assessments/{session_id}/responses",
            headers=authenticated_headers,
            json=response_data
        )
        assert response.status_code == 200

        result = response.json()
        assert "session_updated" in result

    def test_get_assessment_recommendations(self, client, authenticated_headers):
        """Test getting assessment recommendations"""
        # Create and complete assessment session
        session_response = client.post(
            "/api/assessments",
            headers=authenticated_headers,
            json={"session_type": "compliance_scoping"}
        )
        session_id = session_response.json()["id"]

        # Submit some responses to generate recommendations
        responses = [
            {"question_id": "data_processing", "response": "yes"},
            {"question_id": "industry", "response": "technology"},
            {"question_id": "employee_count", "response": "25"}
        ]

        for resp in responses:
            client.post(
                f"/api/assessments/{session_id}/responses",
                headers=authenticated_headers,
                json=resp
            )

        # Get recommendations
        response = client.get(f"/api/assessments/{session_id}/recommendations", headers=authenticated_headers)
        assert response.status_code == 200

        response_data = response.json()
        assert "recommendations" in response_data
        assert isinstance(response_data["recommendations"], list)


@pytest.mark.integration
class TestFrameworkEndpoints:
    """Test compliance framework endpoints"""

    def test_get_available_frameworks(self, client, authenticated_headers):
        """Test retrieving available compliance frameworks"""
        response = client.get("/api/frameworks", headers=authenticated_headers)
        assert response.status_code == 200

        response_data = response.json()
        assert "frameworks" in response_data
        assert len(response_data["frameworks"]) > 0

        # Check framework structure
        framework = response_data["frameworks"][0]
        required_fields = ["id", "name", "display_name", "description", "category"]
        for field in required_fields:
            assert field in framework

    def test_get_framework_details(self, client, authenticated_headers):
        """Test retrieving detailed framework information"""
        # First get available frameworks
        frameworks_response = client.get("/api/frameworks", headers=authenticated_headers)
        framework_id = frameworks_response.json()["frameworks"][0]["id"]

        # Get framework details
        response = client.get(f"/api/frameworks/{framework_id}", headers=authenticated_headers)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["id"] == framework_id
        assert "requirements" in response_data
        assert "implementation_guidance" in response_data

    def test_framework_recommendations(self, client, authenticated_headers, sample_business_profile_data):
        """Test getting framework recommendations based on business profile"""
        # Create business profile first
        client.post(
            "/api/business-profiles",
            headers=authenticated_headers,
            json=sample_business_profile_data
        )

        # Get recommendations
        response = client.post(
            "/api/frameworks/recommend",
            headers=authenticated_headers,
            json=sample_business_profile_data
        )
        assert response.status_code == 200

        response_data = response.json()
        assert "recommendations" in response_data
        assert len(response_data["recommendations"]) > 0

        # Check recommendation structure
        recommendation = response_data["recommendations"][0]
        assert "framework" in recommendation
        assert "relevance_score" in recommendation
        assert "reasons" in recommendation
        assert "priority" in recommendation


@pytest.mark.integration
class TestPolicyEndpoints:
    """Test policy generation endpoints"""

    def test_generate_policy(self, client, authenticated_headers, mock_ai_client, sample_business_profile_data):
        """Test AI-powered policy generation"""
        # Setup mock AI response
        mock_ai_client.generate_content.return_value.text = """
        # Data Protection Policy

        ## 1. Purpose and Scope
        This policy establishes guidelines for the protection of personal data...

        ## 2. Data Processing Principles
        We commit to processing personal data in accordance with GDPR principles...
        """

        # Create business profile
        client.post(
            "/api/business-profiles",
            headers=authenticated_headers,
            json=sample_business_profile_data
        )

        # Get framework ID
        frameworks_response = client.get("/api/frameworks", headers=authenticated_headers)
        framework_id = frameworks_response.json()["frameworks"][0]["id"]

        # Generate policy
        policy_request = {
            "framework_id": framework_id,
            "customizations": {
                "company_name": sample_business_profile_data["company_name"],
                "industry": sample_business_profile_data["industry"]
            }
        }

        response = client.post(
            "/api/policies/generate",
            headers=authenticated_headers,
            json=policy_request
        )
        assert response.status_code == 201

        response_data = response.json()
        assert "policy_name" in response_data
        assert "content" in response_data
        assert "status" in response_data
        assert response_data["status"] == "draft"

    def test_get_generated_policies(self, client, authenticated_headers):
        """Test retrieving generated policies"""
        response = client.get("/api/policies", headers=authenticated_headers)
        assert response.status_code == 200

        response_data = response.json()
        assert "policies" in response_data
        assert isinstance(response_data["policies"], list)

    def test_update_policy_status(self, client, authenticated_headers, mock_ai_client, sample_business_profile_data):
        """Test updating policy approval status"""
        # Generate a policy first
        client.post(
            "/api/business-profiles",
            headers=authenticated_headers,
            json=sample_business_profile_data
        )

        frameworks_response = client.get("/api/frameworks", headers=authenticated_headers)
        framework_id = frameworks_response.json()["frameworks"][0]["id"]

        mock_ai_client.generate_content.return_value.text = "Sample policy content"

        policy_response = client.post(
            "/api/policies/generate",
            headers=authenticated_headers,
            json={"framework_id": framework_id}
        )
        policy_id = policy_response.json()["id"]

        # Update policy status
        update_data = {
            "status": "approved",
            "approved": True
        }

        response = client.patch(
            f"/api/policies/{policy_id}/status",
            headers=authenticated_headers,
            json=update_data
        )
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["status"] == "approved"
        assert response_data["approved"] is True


@pytest.mark.integration
class TestImplementationEndpoints:
    """Test implementation planning endpoints"""

    def test_generate_implementation_plan(self, client, authenticated_headers, sample_business_profile_data):
        """Test generating implementation plans"""
        # Setup prerequisites
        client.post(
            "/api/business-profiles",
            headers=authenticated_headers,
            json=sample_business_profile_data
        )

        frameworks_response = client.get("/api/frameworks", headers=authenticated_headers)
        framework_id = frameworks_response.json()["frameworks"][0]["id"]

        # Generate implementation plan
        plan_request = {
            "framework_id": framework_id
        }

        response = client.post(
            "/api/implementation/plans",
            headers=authenticated_headers,
            json=plan_request
        )
        assert response.status_code == 201

        response_data = response.json()
        assert "plan_name" in response_data
        assert "total_phases" in response_data
        assert "total_tasks" in response_data
        assert "estimated_duration_weeks" in response_data
        assert response_data["status"] == "not_started"

    def test_get_implementation_plans(self, client, authenticated_headers):
        """Test retrieving implementation plans"""
        response = client.get("/api/implementation/plans", headers=authenticated_headers)
        assert response.status_code == 200

        response_data = response.json()
        assert "plans" in response_data
        assert isinstance(response_data["plans"], list)

    def test_update_task_progress(self, client, authenticated_headers, sample_business_profile_data):
        """Test updating implementation task progress"""
        # Generate plan first
        client.post(
            "/api/business-profiles",
            headers=authenticated_headers,
            json=sample_business_profile_data
        )

        frameworks_response = client.get("/api/frameworks", headers=authenticated_headers)
        framework_id = frameworks_response.json()["frameworks"][0]["id"]

        plan_response = client.post(
            "/api/implementation/plans",
            headers=authenticated_headers,
            json={"framework_id": framework_id}
        )
        plan_id = plan_response.json()["id"]

        # Get plan details to find a task
        plan_details = client.get(f"/api/implementation/plans/{plan_id}", headers=authenticated_headers)
        tasks = plan_details.json()["tasks"]
        task_id = tasks[0]["id"] if tasks else None

        if task_id:
            # Update task
            update_data = {
                "status": "in_progress",
                "assigned_to": "Test User",
                "notes": "Started working on this task"
            }

            response = client.patch(
                f"/api/implementation/plans/{plan_id}/tasks/{task_id}",
                headers=authenticated_headers,
                json=update_data
            )
            assert response.status_code == 200

            response_data = response.json()
            assert "task_updated" in response_data


@pytest.mark.integration
class TestEvidenceEndpoints:
    """Test evidence collection endpoints"""

    def test_get_evidence_requirements(self, client, authenticated_headers, sample_business_profile_data):
        """Test retrieving evidence requirements"""
        # Setup prerequisites
        client.post(
            "/api/business-profiles",
            headers=authenticated_headers,
            json=sample_business_profile_data
        )

        frameworks_response = client.get("/api/frameworks", headers=authenticated_headers)
        framework_id = frameworks_response.json()["frameworks"][0]["id"]

        # Get evidence requirements
        response = client.get(
            f"/api/evidence/requirements?framework_id={framework_id}",
            headers=authenticated_headers
        )
        assert response.status_code == 200

        response_data = response.json()
        assert "requirements" in response_data
        assert isinstance(response_data["requirements"], list)

    def test_create_evidence_item(self, client, authenticated_headers, sample_business_profile_data):
        """Test creating evidence items"""
        # Setup prerequisites
        client.post(
            "/api/business-profiles",
            headers=authenticated_headers,
            json=sample_business_profile_data
        )

        frameworks_response = client.get("/api/frameworks", headers=authenticated_headers)
        framework_id = frameworks_response.json()["frameworks"][0]["id"]

        # Create evidence item
        evidence_data = {
            "framework_id": framework_id,
            "control_id": str(uuid4()),
            "evidence_type": "document",
            "title": "Data Protection Policy Document",
            "description": "Company data protection policy",
            "automation_possible": False,
            "collection_method": "manual"
        }

        response = client.post(
            "/api/evidence",
            headers=authenticated_headers,
            json=evidence_data
        )
        assert response.status_code == 201

        response_data = response.json()
        assert response_data["title"] == evidence_data["title"]
        assert response_data["evidence_type"] == evidence_data["evidence_type"]
        assert "id" in response_data

    def test_update_evidence_status(self, client, authenticated_headers, sample_business_profile_data):
        """Test updating evidence collection status"""
        # Setup and create evidence item
        client.post(
            "/api/business-profiles",
            headers=authenticated_headers,
            json=sample_business_profile_data
        )

        frameworks_response = client.get("/api/frameworks", headers=authenticated_headers)
        framework_id = frameworks_response.json()["frameworks"][0]["id"]

        evidence_response = client.post(
            "/api/evidence",
            headers=authenticated_headers,
            json={
                "framework_id": framework_id,
                "control_id": str(uuid4()),
                "evidence_type": "document",
                "title": "Test Evidence",
                "collection_method": "manual"
            }
        )
        evidence_id = evidence_response.json()["id"]

        # Update status
        update_data = {
            "status": "collected",
            "notes": "Evidence successfully collected"
        }

        response = client.patch(
            f"/api/evidence/{evidence_id}",
            headers=authenticated_headers,
            json=update_data
        )
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["status"] == "collected"


@pytest.mark.integration
class TestReadinessEndpoints:
    """Test compliance readiness assessment endpoints"""

    def test_get_readiness_assessment(self, client, authenticated_headers, sample_business_profile_data):
        """Test getting compliance readiness assessment"""
        # Setup prerequisites
        client.post(
            "/api/business-profiles",
            headers=authenticated_headers,
            json=sample_business_profile_data
        )

        # Get readiness assessment
        response = client.get("/api/readiness/assessment", headers=authenticated_headers)
        assert response.status_code == 200

        response_data = response.json()
        assert "overall_score" in response_data
        assert "framework_scores" in response_data
        assert "risk_level" in response_data
        assert "recommendations" in response_data

        # Validate score ranges
        assert 0 <= response_data["overall_score"] <= 100
        assert response_data["risk_level"] in ["Low", "Medium", "High", "Critical"]

    def test_generate_compliance_report(self, client, authenticated_headers, sample_business_profile_data):
        """Test generating compliance reports"""
        # Setup prerequisites
        client.post(
            "/api/business-profiles",
            headers=authenticated_headers,
            json=sample_business_profile_data
        )

        # Generate report
        report_request = {
            "title": "Q1 2024 Compliance Report",
            "framework": "GDPR",
            "report_type": "executive",
            "format": "pdf",
            "include_evidence": True,
            "include_recommendations": True
        }

        response = client.post(
            "/api/readiness/reports",
            headers=authenticated_headers,
            json=report_request
        )
        assert response.status_code == 201

        response_data = response.json()
        assert "report_id" in response_data
        assert "download_url" in response_data
        assert response_data["status"] == "generated"


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete end-to-end user workflows"""

    def test_complete_compliance_journey(self, client, authenticated_headers, mock_ai_client, sample_business_profile_data):
        """Test complete compliance implementation journey"""
        # Setup AI mock
        mock_ai_client.generate_content.return_value.text = "Generated compliance content"

        # 1. Create business profile
        profile_response = client.post(
            "/api/business-profiles",
            headers=authenticated_headers,
            json=sample_business_profile_data
        )
        assert profile_response.status_code == 201

        # 2. Complete assessment
        assessment_response = client.post(
            "/api/assessments",
            headers=authenticated_headers,
            json={"session_type": "compliance_scoping"}
        )
        session_id = assessment_response.json()["id"]

        # Submit assessment responses
        responses = [
            {"question_id": "data_processing", "response": "yes"},
            {"question_id": "industry", "response": "technology"},
            {"question_id": "employee_count", "response": "25"}
        ]

        for resp in responses:
            client.post(
                f"/api/assessments/{session_id}/responses",
                headers=authenticated_headers,
                json=resp
            )

        # 3. Get framework recommendations
        recommendations_response = client.get(
            f"/api/assessments/{session_id}/recommendations",
            headers=authenticated_headers
        )
        assert recommendations_response.status_code == 200

        # 4. Generate policies
        frameworks_response = client.get("/api/frameworks", headers=authenticated_headers)
        framework_id = frameworks_response.json()["frameworks"][0]["id"]

        policy_response = client.post(
            "/api/policies/generate",
            headers=authenticated_headers,
            json={"framework_id": framework_id}
        )
        assert policy_response.status_code == 201

        # 5. Create implementation plan
        plan_response = client.post(
            "/api/implementation/plans",
            headers=authenticated_headers,
            json={"framework_id": framework_id}
        )
        assert plan_response.status_code == 201

        # 6. Check readiness assessment
        readiness_response = client.get("/api/readiness/assessment", headers=authenticated_headers)
        assert readiness_response.status_code == 200

        # Verify the complete workflow created all necessary components
        readiness_data = readiness_response.json()
        assert "overall_score" in readiness_data
        assert readiness_data["overall_score"] >= 0
