"""
Comprehensive tests for compliance framework API endpoints.
Tests framework CRUD, requirements management, and mapping.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient
import json

from api.main import app


@pytest.mark.unit
class TestFrameworkEndpoints:
    """Unit tests for framework endpoints"""
    
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
    def admin_headers(self):
        """Admin authenticated headers"""
        from utils.auth import create_access_token
        token = create_access_token(data={"sub": "admin@example.com", "role": "admin"})
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture
    def framework_data(self):
        """Sample framework data"""
        return {
            "name": "ISO 27001",
            "description": "Information Security Management System",
            "version": "2022",
            "categories": ["Security", "Risk Management"],
            "requirements": [
                {
                    "id": "ISO-4.1",
                    "title": "Understanding the organization and its context",
                    "description": "Determine external and internal issues",
                    "category": "Context",
                    "priority": "high"
                },
                {
                    "id": "ISO-4.2",
                    "title": "Understanding stakeholder needs",
                    "description": "Determine interested parties and requirements",
                    "category": "Context",
                    "priority": "high"
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_list_frameworks(self, client, auth_headers):
        """Test listing available frameworks"""
        response = client.get(
            "/api/v1/frameworks",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should include default frameworks like GDPR, ISO 27001, etc.
    
    @pytest.mark.asyncio
    async def test_get_framework_by_id(self, client, auth_headers):
        """Test retrieving specific framework"""
        framework_id = 1  # Assuming GDPR is ID 1
        
        response = client.get(
            f"/api/v1/frameworks/{framework_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "requirements" in data
    
    @pytest.mark.asyncio
    async def test_get_framework_not_found(self, client, auth_headers):
        """Test retrieving non-existent framework"""
        response = client.get(
            "/api/v1/frameworks/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_create_custom_framework(self, client, admin_headers, framework_data):
        """Test creating custom framework (admin only)"""
        response = client.post(
            "/api/v1/frameworks",
            json=framework_data,
            headers=admin_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == framework_data["name"]
        assert len(data["requirements"]) == 2
    
    @pytest.mark.asyncio
    async def test_create_framework_non_admin(self, client, auth_headers, framework_data):
        """Test non-admin cannot create framework"""
        response = client.post(
            "/api/v1/frameworks",
            json=framework_data,
            headers=auth_headers
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_update_framework(self, client, admin_headers):
        """Test updating framework details"""
        framework_id = 1
        update_data = {
            "description": "Updated description",
            "version": "2024"
        }
        
        response = client.patch(
            f"/api/v1/frameworks/{framework_id}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == update_data["description"]
    
    @pytest.mark.asyncio
    async def test_delete_framework(self, client, admin_headers):
        """Test deleting custom framework"""
        # First create a framework to delete
        framework_data = {"name": "To Delete", "requirements": []}
        
        create_response = client.post(
            "/api/v1/frameworks",
            json=framework_data,
            headers=admin_headers
        )
        framework_id = create_response.json()["id"]
        
        # Now delete it
        response = client.delete(
            f"/api/v1/frameworks/{framework_id}",
            headers=admin_headers
        )
        
        assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_get_framework_requirements(self, client, auth_headers):
        """Test getting framework requirements"""
        framework_id = 1
        
        response = client.get(
            f"/api/v1/frameworks/{framework_id}/requirements",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "id" in data[0]
            assert "title" in data[0]
            assert "category" in data[0]
    
    @pytest.mark.asyncio
    async def test_get_requirement_detail(self, client, auth_headers):
        """Test getting specific requirement details"""
        framework_id = 1
        requirement_id = "GDPR-1"
        
        response = client.get(
            f"/api/v1/frameworks/{framework_id}/requirements/{requirement_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == requirement_id
        assert "title" in data
        assert "description" in data
    
    @pytest.mark.asyncio
    async def test_add_requirement(self, client, admin_headers):
        """Test adding requirement to framework"""
        framework_id = 1
        requirement_data = {
            "id": "GDPR-NEW",
            "title": "New Requirement",
            "description": "New requirement description",
            "category": "Technical",
            "priority": "medium"
        }
        
        response = client.post(
            f"/api/v1/frameworks/{framework_id}/requirements",
            json=requirement_data,
            headers=admin_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == requirement_data["id"]
    
    @pytest.mark.asyncio
    async def test_update_requirement(self, client, admin_headers):
        """Test updating requirement"""
        framework_id = 1
        requirement_id = "GDPR-1"
        update_data = {
            "description": "Updated description",
            "priority": "critical"
        }
        
        response = client.patch(
            f"/api/v1/frameworks/{framework_id}/requirements/{requirement_id}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "critical"
    
    @pytest.mark.asyncio
    async def test_delete_requirement(self, client, admin_headers):
        """Test deleting requirement from framework"""
        framework_id = 1
        requirement_id = "GDPR-TEST"
        
        # First add a requirement
        requirement_data = {
            "id": requirement_id,
            "title": "Test Requirement"
        }
        client.post(
            f"/api/v1/frameworks/{framework_id}/requirements",
            json=requirement_data,
            headers=admin_headers
        )
        
        # Then delete it
        response = client.delete(
            f"/api/v1/frameworks/{framework_id}/requirements/{requirement_id}",
            headers=admin_headers
        )
        
        assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_framework_categories(self, client, auth_headers):
        """Test getting framework categories"""
        framework_id = 1
        
        response = client.get(
            f"/api/v1/frameworks/{framework_id}/categories",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should include categories like Technical, Organizational, etc.
    
    @pytest.mark.asyncio
    async def test_framework_statistics(self, client, auth_headers):
        """Test getting framework statistics"""
        framework_id = 1
        
        response = client.get(
            f"/api/v1/frameworks/{framework_id}/statistics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_requirements" in data
        assert "categories" in data
        assert "priority_breakdown" in data
    
    @pytest.mark.asyncio
    async def test_framework_mapping(self, client, auth_headers):
        """Test framework requirement mapping"""
        response = client.get(
            "/api/v1/frameworks/mapping?from=GDPR&to=ISO27001",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "mappings" in data
        assert isinstance(data["mappings"], list)
    
    @pytest.mark.asyncio
    async def test_framework_export(self, client, auth_headers):
        """Test exporting framework"""
        framework_id = 1
        
        response = client.get(
            f"/api/v1/frameworks/{framework_id}/export?format=json",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "framework" in data
        assert "requirements" in data
    
    @pytest.mark.asyncio
    async def test_framework_import(self, client, admin_headers):
        """Test importing framework"""
        import_data = {
            "source": "template",
            "template_id": "nist-csf",
            "customize": {
                "name": "Custom NIST Framework",
                "exclude_categories": ["Recover"]
            }
        }
        
        response = client.post(
            "/api/v1/frameworks/import",
            json=import_data,
            headers=admin_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Custom NIST Framework"
    
    @pytest.mark.asyncio
    async def test_framework_search(self, client, auth_headers):
        """Test searching frameworks"""
        response = client.get(
            "/api/v1/frameworks/search?q=privacy",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        # Should return frameworks related to privacy (e.g., GDPR)
    
    @pytest.mark.asyncio
    async def test_framework_recommendations(self, client, auth_headers):
        """Test AI-powered framework recommendations"""
        request_data = {
            "industry": "healthcare",
            "company_size": "medium",
            "regions": ["EU", "US"],
            "data_types": ["health", "personal"]
        }
        
        response = client.post(
            "/api/v1/frameworks/recommendations",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "recommended" in data
        assert "reasoning" in data
        # Should recommend HIPAA, GDPR, etc.


@pytest.mark.integration
class TestFrameworkIntegration:
    """Integration tests for framework functionality"""
    
    @pytest.mark.asyncio
    async def test_framework_assessment_integration(self, client, auth_headers, db_session):
        """Test framework integration with assessments"""
        # 1. Get framework
        framework_response = client.get(
            "/api/v1/frameworks/1",
            headers=auth_headers
        )
        assert framework_response.status_code == 200
        framework = framework_response.json()
        
        # 2. Create assessment from framework
        assessment_data = {
            "framework_id": framework["id"],
            "name": f"{framework['name']} Assessment"
        }
        
        assessment_response = client.post(
            "/api/v1/assessments",
            json=assessment_data,
            headers=auth_headers
        )
        assert assessment_response.status_code == 201
        assessment = assessment_response.json()
        
        # 3. Verify requirements match
        requirements_response = client.get(
            f"/api/v1/assessments/{assessment['id']}/requirements",
            headers=auth_headers
        )
        assert requirements_response.status_code == 200
        assessment_reqs = requirements_response.json()
        
        assert len(assessment_reqs) == len(framework.get("requirements", []))
    
    @pytest.mark.asyncio
    async def test_multi_framework_compliance(self, client, auth_headers):
        """Test compliance across multiple frameworks"""
        # Get overlapping requirements between GDPR and ISO 27001
        mapping_response = client.get(
            "/api/v1/frameworks/mapping?from=GDPR&to=ISO27001",
            headers=auth_headers
        )
        assert mapping_response.status_code == 200
        
        mappings = mapping_response.json()["mappings"]
        
        # Verify mapped requirements have similar themes
        for mapping in mappings[:5]:  # Check first 5 mappings
            assert "source_requirement" in mapping
            assert "target_requirement" in mapping
            assert "similarity_score" in mapping
            assert mapping["similarity_score"] > 0.5  # Reasonable similarity