"""
End-to-End Tests for User Onboarding Flow

Tests the complete user onboarding process from registration
through framework recommendation and initial compliance setup.
"""

import pytest
import time
from uuid import uuid4

from tests.conftest import assert_api_response_security


@pytest.mark.e2e
class TestUserOnboardingFlow:
    """Test complete user onboarding workflow"""

    def test_complete_user_onboarding_workflow(self, client, sample_user_data, sample_business_profile):
        """Test complete user onboarding from registration to framework recommendations"""
        
        # Step 1: User Registration
        registration_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
            "full_name": sample_user_data["full_name"],
            "company": sample_business_profile["company_name"]
        }
        
        register_response = client.post("/api/auth/register", json=registration_data)
        assert register_response.status_code == 201
        assert_api_response_security(register_response)
        
        register_data = register_response.json()
        assert "user_id" in register_data
        assert register_data["email"] == registration_data["email"]
        assert register_data["full_name"] == registration_data["full_name"]
        
        # Step 2: User Login
        login_data = {
            "email": registration_data["email"],
            "password": registration_data["password"]
        }
        
        login_response = client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200
        assert_api_response_security(login_response)
        
        login_result = login_response.json()
        assert "access_token" in login_result
        assert "token_type" in login_result
        assert login_result["token_type"] == "bearer"
        
        # Set up authentication headers for subsequent requests
        auth_headers = {"Authorization": f"Bearer {login_result['access_token']}"}
        
        # Step 3: Create Business Profile
        business_profile_data = {
            "company_name": sample_business_profile["company_name"],
            "industry": sample_business_profile["industry"],
            "employee_count": sample_business_profile["employee_count"],
            "revenue_range": sample_business_profile["revenue_range"],
            "location": sample_business_profile["location"],
            "description": sample_business_profile["description"],
            "data_processing": sample_business_profile["data_processing"]
        }
        
        profile_response = client.post(
            "/api/business-profiles",
            json=business_profile_data,
            headers=auth_headers
        )
        assert profile_response.status_code == 201
        assert_api_response_security(profile_response)
        
        profile_data = profile_response.json()
        assert "id" in profile_data
        assert profile_data["company_name"] == business_profile_data["company_name"]
        assert profile_data["industry"] == business_profile_data["industry"]
        
        business_profile_id = profile_data["id"]
        
        # Step 4: Start Compliance Assessment
        assessment_data = {
            "business_profile_id": business_profile_id,
            "assessment_type": "compliance_scoping",
            "frameworks_of_interest": ["GDPR", "ISO 27001"]
        }
        
        assessment_response = client.post(
            "/api/assessments",
            json=assessment_data,
            headers=auth_headers
        )
        assert assessment_response.status_code == 201
        assert_api_response_security(assessment_response)
        
        assessment_result = assessment_response.json()
        assert "session_id" in assessment_result
        assert "current_stage" in assessment_result
        assert "total_stages" in assessment_result
        assert assessment_result["status"] == "in_progress"
        
        assessment_id = assessment_result["session_id"]
        
        # Step 5: Complete Assessment Questions
        # Simulate answering assessment questions
        assessment_questions = [
            {
                "question_id": "data_processing",
                "response": "yes",
                "details": "We process customer personal data and employee records"
            },
            {
                "question_id": "data_types",
                "response": ["personal_data", "sensitive_data"],
                "details": "Customer information and employee HR data"
            },
            {
                "question_id": "international_transfers",
                "response": "yes",
                "details": "We use cloud services with international data centers"
            },
            {
                "question_id": "current_security_measures",
                "response": ["encryption", "access_controls", "backups"],
                "details": "Basic security measures in place"
            },
            {
                "question_id": "compliance_experience",
                "response": "basic",
                "details": "Limited compliance experience"
            }
        ]
        
        for question in assessment_questions:
            response_data = {
                "question_id": question["question_id"],
                "response": question["response"],
                "details": question.get("details", ""),
                "move_to_next_stage": True
            }
            
            answer_response = client.post(
                f"/api/assessments/{assessment_id}/responses",
                json=response_data,
                headers=auth_headers
            )
            assert answer_response.status_code == 200
            
            answer_result = answer_response.json()
            assert "session_updated" in answer_result
            assert answer_result["session_updated"] is True
        
        # Step 6: Complete Assessment and Get Recommendations
        complete_response = client.post(
            f"/api/assessments/{assessment_id}/complete",
            headers=auth_headers
        )
        assert complete_response.status_code == 200
        
        complete_result = complete_response.json()
        assert complete_result["status"] == "completed"
        assert "recommendations" in complete_result
        assert len(complete_result["recommendations"]) > 0
        
        # Step 7: Get Framework Recommendations
        recommendations_response = client.get(
            f"/api/frameworks/recommendations/{business_profile_id}",
            headers=auth_headers
        )
        assert recommendations_response.status_code == 200
        assert_api_response_security(recommendations_response)
        
        recommendations = recommendations_response.json()
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Verify recommendation structure
        for recommendation in recommendations:
            assert "framework" in recommendation
            assert "relevance_score" in recommendation
            assert "priority" in recommendation
            assert "reasons" in recommendation
            assert 0 <= recommendation["relevance_score"] <= 100
            assert recommendation["priority"] in ["High", "Medium", "Low"]
        
        # GDPR should be highly recommended for EU data processing
        gdpr_recommendation = next(
            (r for r in recommendations if r["framework"]["name"] == "GDPR"), 
            None
        )
        assert gdpr_recommendation is not None
        assert gdpr_recommendation["relevance_score"] >= 80
        assert gdpr_recommendation["priority"] in ["High", "Medium"]
        
        # Step 8: Select Frameworks and Create Implementation Plan
        selected_frameworks = [
            gdpr_recommendation["framework"]["id"],
            # Add ISO 27001 if recommended
        ]
        
        if len(recommendations) > 1:
            iso_recommendation = next(
                (r for r in recommendations if "ISO" in r["framework"]["name"]), 
                None
            )
            if iso_recommendation:
                selected_frameworks.append(iso_recommendation["framework"]["id"])
        
        implementation_data = {
            "business_profile_id": business_profile_id,
            "framework_ids": selected_frameworks,
            "timeline_preference": "standard",
            "resource_allocation": "medium"
        }
        
        implementation_response = client.post(
            "/api/implementation/plans",
            json=implementation_data,
            headers=auth_headers
        )
        assert implementation_response.status_code == 201
        assert_api_response_security(implementation_response)
        
        implementation_result = implementation_response.json()
        assert "plan_id" in implementation_result
        assert "total_phases" in implementation_result
        assert "estimated_duration_weeks" in implementation_result
        assert implementation_result["total_phases"] > 0
        assert implementation_result["estimated_duration_weeks"] > 0
        
        # Step 9: Verify User Dashboard Shows Complete Setup
        dashboard_response = client.get("/api/users/dashboard", headers=auth_headers)
        assert dashboard_response.status_code == 200
        assert_api_response_security(dashboard_response)
        
        dashboard_data = dashboard_response.json()
        assert "business_profile" in dashboard_data
        assert "compliance_status" in dashboard_data
        assert "recommended_frameworks" in dashboard_data
        assert "implementation_plan" in dashboard_data
        assert "onboarding_completed" in dashboard_data
        assert dashboard_data["onboarding_completed"] is True
        
        # Verify compliance status reflects setup
        compliance_status = dashboard_data["compliance_status"]
        assert "overall_score" in compliance_status
        assert "framework_scores" in compliance_status
        assert compliance_status["overall_score"] >= 0

    def test_user_onboarding_with_assessment_restart(self, client, sample_user_data, sample_business_profile):
        """Test user onboarding with assessment restart scenario"""
        
        # Complete registration and login
        register_response = client.post("/api/auth/register", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
            "full_name": sample_user_data["full_name"]
        })
        assert register_response.status_code == 201
        
        login_response = client.post("/api/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        assert login_response.status_code == 200
        
        auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        # Create business profile
        profile_response = client.post(
            "/api/business-profiles",
            json=sample_business_profile,
            headers=auth_headers
        )
        assert profile_response.status_code == 201
        business_profile_id = profile_response.json()["id"]
        
        # Start assessment
        assessment_response = client.post(
            "/api/assessments",
            json={"business_profile_id": business_profile_id},
            headers=auth_headers
        )
        assert assessment_response.status_code == 201
        assessment_id = assessment_response.json()["session_id"]
        
        # Answer some questions
        partial_response = client.post(
            f"/api/assessments/{assessment_id}/responses",
            json={
                "question_id": "data_processing",
                "response": "yes",
                "move_to_next_stage": True
            },
            headers=auth_headers
        )
        assert partial_response.status_code == 200
        
        # Restart assessment
        restart_response = client.post(
            f"/api/assessments/{assessment_id}/restart",
            headers=auth_headers
        )
        assert restart_response.status_code == 200
        
        restart_result = restart_response.json()
        assert restart_result["status"] == "in_progress"
        assert restart_result["current_stage"] == 1
        
        # Complete assessment after restart
        complete_questions = [
            {"question_id": "data_processing", "response": "yes"},
            {"question_id": "data_types", "response": ["personal_data"]},
            {"question_id": "compliance_experience", "response": "none"}
        ]
        
        for question in complete_questions:
            client.post(
                f"/api/assessments/{assessment_id}/responses",
                json={**question, "move_to_next_stage": True},
                headers=auth_headers
            )
        
        # Complete assessment
        complete_response = client.post(
            f"/api/assessments/{assessment_id}/complete",
            headers=auth_headers
        )
        assert complete_response.status_code == 200
        assert complete_response.json()["status"] == "completed"

    def test_user_onboarding_with_minimal_data(self, client):
        """Test user onboarding with minimal required data"""
        
        # Register with minimal data
        minimal_user_data = {
            "email": f"minimal-{uuid4()}@example.com",
            "password": "MinimalPassword123!",
            "full_name": "Minimal User"
        }
        
        register_response = client.post("/api/auth/register", json=minimal_user_data)
        assert register_response.status_code == 201
        
        # Login
        login_response = client.post("/api/auth/login", json={
            "email": minimal_user_data["email"],
            "password": minimal_user_data["password"]
        })
        assert login_response.status_code == 200
        
        auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        # Create minimal business profile
        minimal_profile = {
            "company_name": "Minimal Corp",
            "industry": "Technology",
            "employee_count": 5
        }
        
        profile_response = client.post(
            "/api/business-profiles",
            json=minimal_profile,
            headers=auth_headers
        )
        assert profile_response.status_code == 201
        business_profile_id = profile_response.json()["id"]
        
        # Skip detailed assessment and get basic recommendations
        quick_assessment_data = {
            "business_profile_id": business_profile_id,
            "assessment_type": "quick_setup",
            "industry_standard": True
        }
        
        quick_response = client.post(
            "/api/assessments/quick",
            json=quick_assessment_data,
            headers=auth_headers
        )
        assert quick_response.status_code == 200
        
        quick_result = quick_response.json()
        assert "recommendations" in quick_result
        assert len(quick_result["recommendations"]) > 0
        
        # Should still get basic framework recommendations
        assert any("GDPR" in rec["framework"]["name"] for rec in quick_result["recommendations"])

    def test_user_onboarding_error_recovery(self, client, sample_user_data):
        """Test user onboarding with error recovery scenarios"""
        
        # Test registration with existing email
        register_response1 = client.post("/api/auth/register", json=sample_user_data)
        assert register_response1.status_code == 201
        
        # Attempt to register with same email
        register_response2 = client.post("/api/auth/register", json=sample_user_data)
        assert register_response2.status_code == 409  # Conflict
        assert "already exists" in register_response2.json()["detail"]
        
        # Successful login with existing account
        login_response = client.post("/api/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        assert login_response.status_code == 200
        
        auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        # Test business profile creation with invalid data
        invalid_profile = {
            "company_name": "",  # Invalid: empty name
            "industry": "InvalidIndustry",  # Invalid: not in allowed list
            "employee_count": -5  # Invalid: negative count
        }
        
        invalid_response = client.post(
            "/api/business-profiles",
            json=invalid_profile,
            headers=auth_headers
        )
        assert invalid_response.status_code == 422
        
        # Correct the data and try again
        valid_profile = {
            "company_name": "Valid Corp",
            "industry": "Technology",
            "employee_count": 25
        }
        
        valid_response = client.post(
            "/api/business-profiles",
            json=valid_profile,
            headers=auth_headers
        )
        assert valid_response.status_code == 201
        
        # Continue with successful onboarding
        dashboard_response = client.get("/api/users/dashboard", headers=auth_headers)
        assert dashboard_response.status_code == 200


@pytest.mark.e2e
class TestOnboardingIntegration:
    """Test onboarding integration with other system components"""

    def test_onboarding_triggers_background_tasks(self, client, sample_user_data, sample_business_profile):
        """Test that onboarding triggers appropriate background tasks"""
        
        # Complete basic onboarding
        register_response = client.post("/api/auth/register", json=sample_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        profile_response = client.post(
            "/api/business-profiles",
            json=sample_business_profile,
            headers=auth_headers
        )
        business_profile_id = profile_response.json()["id"]
        
        # Start assessment which should trigger background analysis
        assessment_response = client.post(
            "/api/assessments",
            json={"business_profile_id": business_profile_id},
            headers=auth_headers
        )
        assessment_id = assessment_response.json()["session_id"]
        
        # Complete assessment
        client.post(
            f"/api/assessments/{assessment_id}/responses",
            json={"question_id": "data_processing", "response": "yes", "move_to_next_stage": True},
            headers=auth_headers
        )
        
        complete_response = client.post(
            f"/api/assessments/{assessment_id}/complete",
            headers=auth_headers
        )
        assert complete_response.status_code == 200
        
        # Check that background tasks were scheduled
        # This would typically check task queues or status endpoints
        tasks_response = client.get("/api/tasks/status", headers=auth_headers)
        if tasks_response.status_code == 200:
            tasks_data = tasks_response.json()
            assert "assessment_analysis" in [task["type"] for task in tasks_data.get("scheduled_tasks", [])]

    def test_onboarding_creates_audit_trail(self, client, sample_user_data, sample_business_profile):
        """Test that onboarding creates proper audit trail"""
        
        # Complete onboarding
        register_response = client.post("/api/auth/register", json=sample_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        profile_response = client.post(
            "/api/business-profiles",
            json=sample_business_profile,
            headers=auth_headers
        )
        
        # Check audit trail
        audit_response = client.get("/api/audit/trail", headers=auth_headers)
        if audit_response.status_code == 200:
            audit_data = audit_response.json()
            
            # Should contain onboarding events
            events = audit_data.get("events", [])
            event_types = [event["event_type"] for event in events]
            
            assert "user_registration" in event_types
            assert "business_profile_created" in event_types
            
            # Events should be timestamped and contain user context
            for event in events:
                assert "timestamp" in event
                assert "user_id" in event
                assert "event_data" in event

    def test_onboarding_sets_user_preferences(self, client, sample_user_data):
        """Test that onboarding properly sets user preferences"""
        
        # Register with preferences
        registration_data = {
            **sample_user_data,
            "preferences": {
                "notifications": {
                    "email_updates": True,
                    "assessment_reminders": True,
                    "compliance_alerts": False
                },
                "dashboard": {
                    "default_view": "overview",
                    "show_tips": True
                }
            }
        }
        
        register_response = client.post("/api/auth/register", json=registration_data)
        assert register_response.status_code == 201
        
        login_response = client.post("/api/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        # Check that preferences were saved
        preferences_response = client.get("/api/users/preferences", headers=auth_headers)
        assert preferences_response.status_code == 200
        
        preferences_data = preferences_response.json()
        assert preferences_data["notifications"]["email_updates"] is True
        assert preferences_data["notifications"]["compliance_alerts"] is False
        assert preferences_data["dashboard"]["default_view"] == "overview"