"""
Comprehensive tests for assessment API endpoints.
Tests CRUD operations, AI assistance, and compliance scoring.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient
import json

from api.main import app


@pytest.mark.unit
class TestAssessmentEndpoints:
    """Unit tests for assessment endpoints"""
    
    @pytest.fixture
    def client(self):
        """Test client for FastAPI app"""
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self, sample_user):
        """Authenticated request headers"""
        from utils.auth import create_access_token
        token = create_access_token(data={"sub": sample_user.email})
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture
    def assessment_data(self):
        """Sample assessment creation data"""
        return {
            "framework_id": 1,
            "name": "Q1 2024 GDPR Assessment",
            "description": "Quarterly GDPR compliance assessment",
            "business_profile_id": str(uuid4())
        }
    
    @pytest.mark.asyncio
    async def test_create_assessment(self, client, auth_headers, assessment_data):
        """Test creating new assessment"""
        response = client.post(
            "/api/v1/assessments",
            json=assessment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == assessment_data["name"]
        assert data["framework_id"] == assessment_data["framework_id"]
        assert data["status"] == "draft"
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_assessment_invalid_framework(self, client, auth_headers):
        """Test creating assessment with invalid framework"""
        data = {
            "framework_id": 99999,  # Non-existent framework
            "name": "Invalid Assessment"
        }
        
        response = client.post(
            "/api/v1/assessments",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "framework not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_assessment(self, client, auth_headers):
        """Test retrieving assessment by ID"""
        assessment_id = str(uuid4())
        
        with patch('api.routers.assessments.get_assessment_by_id') as mock_get:
            mock_get.return_value = {
                "id": assessment_id,
                "name": "Test Assessment",
                "status": "in_progress",
                "score": 75.0
            }
            
            response = client.get(
                f"/api/v1/assessments/{assessment_id}",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == assessment_id
            assert data["score"] == 75.0
    
    @pytest.mark.asyncio
    async def test_get_assessment_not_found(self, client, auth_headers):
        """Test retrieving non-existent assessment"""
        response = client.get(
            f"/api/v1/assessments/{uuid4()}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_list_assessments(self, client, auth_headers):
        """Test listing user's assessments"""
        with patch('api.routers.assessments.get_user_assessments') as mock_list:
            mock_list.return_value = [
                {"id": str(uuid4()), "name": "Assessment 1", "status": "completed"},
                {"id": str(uuid4()), "name": "Assessment 2", "status": "in_progress"}
            ]
            
            response = client.get(
                "/api/v1/assessments",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["name"] == "Assessment 1"
    
    @pytest.mark.asyncio
    async def test_list_assessments_with_filters(self, client, auth_headers):
        """Test listing assessments with filters"""
        response = client.get(
            "/api/v1/assessments?status=completed&framework_id=1",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        # Results should be filtered
    
    @pytest.mark.asyncio
    async def test_update_assessment(self, client, auth_headers):
        """Test updating assessment"""
        assessment_id = str(uuid4())
        update_data = {
            "name": "Updated Assessment Name",
            "description": "Updated description"
        }
        
        response = client.put(
            f"/api/v1/assessments/{assessment_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
    
    @pytest.mark.asyncio
    async def test_delete_assessment(self, client, auth_headers):
        """Test deleting assessment"""
        assessment_id = str(uuid4())
        
        response = client.delete(
            f"/api/v1/assessments/{assessment_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_submit_assessment_response(self, client, auth_headers):
        """Test submitting response to assessment question"""
        assessment_id = str(uuid4())
        response_data = {
            "requirement_id": "GDPR-1",
            "compliant": True,
            "evidence": ["privacy_policy.pdf", "data_map.xlsx"],
            "notes": "Fully compliant with lawful basis requirement",
            "implementation_status": "implemented"
        }
        
        response = client.post(
            f"/api/v1/assessments/{assessment_id}/responses",
            json=response_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["requirement_id"] == response_data["requirement_id"]
        assert data["compliant"] == response_data["compliant"]
    
    @pytest.mark.asyncio
    async def test_bulk_submit_responses(self, client, auth_headers):
        """Test submitting multiple responses at once"""
        assessment_id = str(uuid4())
        responses_data = {
            "responses": [
                {
                    "requirement_id": "GDPR-1",
                    "compliant": True,
                    "evidence": ["doc1.pdf"]
                },
                {
                    "requirement_id": "GDPR-2",
                    "compliant": False,
                    "notes": "In progress"
                },
                {
                    "requirement_id": "GDPR-3",
                    "compliant": True,
                    "evidence": ["doc2.pdf", "doc3.pdf"]
                }
            ]
        }
        
        response = client.post(
            f"/api/v1/assessments/{assessment_id}/responses/bulk",
            json=responses_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["processed"]) == 3
    
    @pytest.mark.asyncio
    async def test_get_assessment_score(self, client, auth_headers):
        """Test getting assessment compliance score"""
        assessment_id = str(uuid4())
        
        with patch('api.routers.assessments.calculate_score') as mock_score:
            mock_score.return_value = {
                "overall_score": 82.5,
                "category_scores": {
                    "technical": 90.0,
                    "organizational": 75.0,
                    "legal": 82.5
                },
                "compliant_requirements": 33,
                "total_requirements": 40,
                "gaps": 7
            }
            
            response = client.get(
                f"/api/v1/assessments/{assessment_id}/score",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["overall_score"] == 82.5
            assert data["compliant_requirements"] == 33
    
    @pytest.mark.asyncio
    async def test_get_assessment_gaps(self, client, auth_headers):
        """Test identifying assessment gaps"""
        assessment_id = str(uuid4())
        
        response = client.get(
            f"/api/v1/assessments/{assessment_id}/gaps",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "gaps" in data
        assert isinstance(data["gaps"], list)
    
    @pytest.mark.asyncio
    async def test_generate_assessment_report(self, client, auth_headers):
        """Test generating assessment report"""
        assessment_id = str(uuid4())
        
        response = client.post(
            f"/api/v1/assessments/{assessment_id}/report",
            json={"format": "pdf"},
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201]
        # Should return report URL or document
    
    @pytest.mark.asyncio
    async def test_complete_assessment(self, client, auth_headers):
        """Test marking assessment as complete"""
        assessment_id = str(uuid4())
        
        response = client.post(
            f"/api/v1/assessments/{assessment_id}/complete",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "completed_at" in data
    
    @pytest.mark.asyncio
    async def test_ai_assessment_assistance(self, client, auth_headers):
        """Test AI assistance for assessment"""
        assessment_id = str(uuid4())
        ai_request = {
            "requirement_id": "GDPR-1",
            "question": "How do I document lawful basis for processing?",
            "context": {
                "business_type": "SaaS",
                "data_types": ["personal", "financial"]
            }
        }
        
        with patch('services.ai.assistant.ComplianceAssistant') as mock_ai:
            mock_ai.return_value.generate_response = AsyncMock(
                return_value="To document lawful basis, you should..."
            )
            
            response = client.post(
                f"/api/v1/assessments/{assessment_id}/ai-assist",
                json=ai_request,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "lawful basis" in data["response"].lower()
    
    @pytest.mark.asyncio
    async def test_assessment_evidence_upload(self, client, auth_headers):
        """Test uploading evidence for assessment"""
        assessment_id = str(uuid4())
        requirement_id = "GDPR-1"
        
        # Simulate file upload
        files = {
            "file": ("privacy_policy.pdf", b"PDF content here", "application/pdf")
        }
        
        response = client.post(
            f"/api/v1/assessments/{assessment_id}/requirements/{requirement_id}/evidence",
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "privacy_policy.pdf"
    
    @pytest.mark.asyncio
    async def test_assessment_collaboration(self, client, auth_headers):
        """Test adding collaborators to assessment"""
        assessment_id = str(uuid4())
        collaborator_data = {
            "email": "collaborator@example.com",
            "role": "reviewer",
            "permissions": ["view", "comment"]
        }
        
        response = client.post(
            f"/api/v1/assessments/{assessment_id}/collaborators",
            json=collaborator_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == collaborator_data["email"]
        assert data["role"] == collaborator_data["role"]
    
    @pytest.mark.asyncio
    async def test_assessment_history(self, client, auth_headers):
        """Test getting assessment change history"""
        assessment_id = str(uuid4())
        
        response = client.get(
            f"/api/v1/assessments/{assessment_id}/history",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "changes" in data
        assert isinstance(data["changes"], list)
    
    @pytest.mark.asyncio
    async def test_assessment_export(self, client, auth_headers):
        """Test exporting assessment data"""
        assessment_id = str(uuid4())
        
        response = client.get(
            f"/api/v1/assessments/{assessment_id}/export?format=json",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "assessment" in data
        assert "responses" in data
        assert "score" in data
    
    @pytest.mark.asyncio
    async def test_assessment_import(self, client, auth_headers):
        """Test importing assessment from template"""
        import_data = {
            "template_id": "gdpr-standard",
            "customize": {
                "name": "Imported GDPR Assessment",
                "exclude_categories": ["marketing"]
            }
        }
        
        response = client.post(
            "/api/v1/assessments/import",
            json=import_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == import_data["customize"]["name"]


@pytest.mark.integration
class TestAssessmentIntegration:
    """Integration tests for assessment workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_assessment_workflow(self, client, auth_headers, db_session):
        """Test complete assessment lifecycle"""
        # 1. Create assessment
        create_data = {
            "framework_id": 1,
            "name": "Integration Test Assessment"
        }
        
        create_response = client.post(
            "/api/v1/assessments",
            json=create_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        assessment_id = create_response.json()["id"]
        
        # 2. Submit responses
        responses = [
            {"requirement_id": f"REQ-{i}", "compliant": i % 2 == 0}
            for i in range(10)
        ]
        
        for response in responses:
            resp = client.post(
                f"/api/v1/assessments/{assessment_id}/responses",
                json=response,
                headers=auth_headers
            )
            assert resp.status_code == 201
        
        # 3. Get score
        score_response = client.get(
            f"/api/v1/assessments/{assessment_id}/score",
            headers=auth_headers
        )
        assert score_response.status_code == 200
        assert score_response.json()["overall_score"] == 50.0  # 5/10 compliant
        
        # 4. Identify gaps
        gaps_response = client.get(
            f"/api/v1/assessments/{assessment_id}/gaps",
            headers=auth_headers
        )
        assert gaps_response.status_code == 200
        assert len(gaps_response.json()["gaps"]) == 5
        
        # 5. Complete assessment
        complete_response = client.post(
            f"/api/v1/assessments/{assessment_id}/complete",
            headers=auth_headers
        )
        assert complete_response.status_code == 200
        
        # 6. Generate report
        report_response = client.post(
            f"/api/v1/assessments/{assessment_id}/report",
            json={"format": "json"},
            headers=auth_headers
        )
        assert report_response.status_code in [200, 201]