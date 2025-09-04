"""
Comprehensive tests for policy generation API endpoints.
Tests AI policy generation, templates, and customization.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient
import json

from api.main import app


@pytest.mark.unit
class TestPolicyEndpoints:
    """Unit tests for policy endpoints"""
    
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
    def policy_request_data(self):
        """Sample policy generation request"""
        return {
            "policy_type": "privacy_policy",
            "framework": "GDPR",
            "business_context": {
                "company_name": "TechCorp Ltd",
                "industry": "technology",
                "company_size": "medium",
                "regions": ["EU", "UK"],
                "data_types": ["personal", "financial"],
                "purposes": ["service_provision", "marketing"]
            },
            "customizations": {
                "tone": "professional",
                "length": "comprehensive",
                "language": "en-GB"
            }
        }
    
    @pytest.mark.asyncio
    async def test_generate_policy_ai(self, client, auth_headers, policy_request_data):
        """Test AI-powered policy generation"""
        with patch('services.ai.ai_policy.generate_policy') as mock_generate:
            mock_generate.return_value = {
                "policy_content": "# Privacy Policy\n\nThis is the generated policy...",
                "sections": ["Introduction", "Data Collection", "Data Use"],
                "compliance_score": 95.0,
                "recommendations": []
            }
            
            response = client.post(
                "/api/v1/ai/policies/generate",
                json=policy_request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            assert "policy_content" in data
            assert "compliance_score" in data
            assert data["compliance_score"] == 95.0
    
    @pytest.mark.asyncio
    async def test_list_policy_templates(self, client, auth_headers):
        """Test listing available policy templates"""
        response = client.get(
            "/api/v1/policies/templates",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify template structure
        template = data[0]
        assert "id" in template
        assert "name" in template
        assert "description" in template
        assert "framework" in template
    
    @pytest.mark.asyncio
    async def test_get_policy_template(self, client, auth_headers):
        """Test retrieving specific policy template"""
        template_id = "privacy-policy-gdpr"
        
        response = client.get(
            f"/api/v1/policies/templates/{template_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == template_id
        assert "content" in data
        assert "variables" in data
    
    @pytest.mark.asyncio
    async def test_create_policy_from_template(self, client, auth_headers):
        """Test creating policy from template"""
        request_data = {
            "template_id": "privacy-policy-gdpr",
            "variables": {
                "company_name": "TestCorp",
                "contact_email": "privacy@testcorp.com",
                "data_controller": "TestCorp Ltd",
                "dpo_email": "dpo@testcorp.com"
            }
        }
        
        response = client.post(
            "/api/v1/policies/from-template",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "content" in data
        assert "TestCorp" in data["content"]
    
    @pytest.mark.asyncio
    async def test_list_user_policies(self, client, auth_headers):
        """Test listing user's generated policies"""
        response = client.get(
            "/api/v1/policies",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_policy_by_id(self, client, auth_headers):
        """Test retrieving specific policy"""
        policy_id = str(uuid4())
        
        with patch('api.routers.policies.get_policy') as mock_get:
            mock_get.return_value = {
                "id": policy_id,
                "name": "Privacy Policy",
                "type": "privacy_policy",
                "content": "Policy content here...",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            response = client.get(
                f"/api/v1/policies/{policy_id}",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == policy_id
    
    @pytest.mark.asyncio
    async def test_update_policy(self, client, auth_headers):
        """Test updating policy content"""
        policy_id = str(uuid4())
        update_data = {
            "name": "Updated Privacy Policy",
            "content": "Updated content...",
            "version": "2.0"
        }
        
        response = client.put(
            f"/api/v1/policies/{policy_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["version"] == "2.0"
    
    @pytest.mark.asyncio
    async def test_delete_policy(self, client, auth_headers):
        """Test deleting policy"""
        policy_id = str(uuid4())
        
        response = client.delete(
            f"/api/v1/policies/{policy_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_policy_validation(self, client, auth_headers):
        """Test policy compliance validation"""
        validation_request = {
            "policy_content": "This is our privacy policy...",
            "framework": "GDPR",
            "policy_type": "privacy_policy"
        }
        
        with patch('services.compliance.validate_policy') as mock_validate:
            mock_validate.return_value = {
                "is_compliant": False,
                "score": 65.0,
                "issues": [
                    {"severity": "high", "issue": "Missing data retention period"},
                    {"severity": "medium", "issue": "No mention of user rights"}
                ],
                "suggestions": ["Add section on data retention", "Include GDPR user rights"]
            }
            
            response = client.post(
                "/api/v1/policies/validate",
                json=validation_request,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_compliant"] is False
            assert data["score"] == 65.0
            assert len(data["issues"]) == 2
    
    @pytest.mark.asyncio
    async def test_policy_comparison(self, client, auth_headers):
        """Test comparing policies for changes"""
        comparison_request = {
            "policy_id_1": str(uuid4()),
            "policy_id_2": str(uuid4())
        }
        
        response = client.post(
            "/api/v1/policies/compare",
            json=comparison_request,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "differences" in data
        assert "similarity_score" in data
    
    @pytest.mark.asyncio
    async def test_policy_export(self, client, auth_headers):
        """Test exporting policy in different formats"""
        policy_id = str(uuid4())
        
        # Export as PDF
        response = client.get(
            f"/api/v1/policies/{policy_id}/export?format=pdf",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        
        # Export as DOCX
        response = client.get(
            f"/api/v1/policies/{policy_id}/export?format=docx",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "application/vnd.openxmlformats" in response.headers["content-type"]
    
    @pytest.mark.asyncio
    async def test_policy_version_history(self, client, auth_headers):
        """Test retrieving policy version history"""
        policy_id = str(uuid4())
        
        response = client.get(
            f"/api/v1/policies/{policy_id}/versions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_policy_approval_workflow(self, client, auth_headers):
        """Test policy approval workflow"""
        policy_id = str(uuid4())
        
        # Submit for approval
        response = client.post(
            f"/api/v1/policies/{policy_id}/submit-approval",
            json={"approvers": ["legal@company.com", "compliance@company.com"]},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending_approval"
    
    @pytest.mark.asyncio
    async def test_policy_publish(self, client, auth_headers):
        """Test publishing policy"""
        policy_id = str(uuid4())
        
        response = client.post(
            f"/api/v1/policies/{policy_id}/publish",
            json={"effective_date": "2024-02-01"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "published"
        assert "published_url" in data
    
    @pytest.mark.asyncio
    async def test_batch_policy_generation(self, client, auth_headers):
        """Test generating multiple policies at once"""
        batch_request = {
            "policies": [
                {"type": "privacy_policy", "framework": "GDPR"},
                {"type": "cookie_policy", "framework": "GDPR"},
                {"type": "terms_of_service", "framework": "general"}
            ],
            "business_context": {
                "company_name": "BatchCorp",
                "industry": "technology"
            }
        }
        
        response = client.post(
            "/api/v1/ai/policies/batch-generate",
            json=batch_request,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "policies" in data
        assert len(data["policies"]) == 3
    
    @pytest.mark.asyncio
    async def test_policy_ai_enhancement(self, client, auth_headers):
        """Test AI enhancement of existing policy"""
        enhancement_request = {
            "policy_id": str(uuid4()),
            "enhancements": ["improve_clarity", "add_examples", "strengthen_compliance"],
            "target_framework": "GDPR"
        }
        
        response = client.post(
            "/api/v1/ai/policies/enhance",
            json=enhancement_request,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "enhanced_content" in data
        assert "improvements" in data
        assert "new_compliance_score" in data
    
    @pytest.mark.asyncio
    async def test_policy_translation(self, client, auth_headers):
        """Test policy translation"""
        policy_id = str(uuid4())
        
        response = client.post(
            f"/api/v1/policies/{policy_id}/translate",
            json={"target_language": "es-ES"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "es-ES"
        assert "translated_content" in data
    
    @pytest.mark.asyncio
    async def test_policy_search(self, client, auth_headers):
        """Test searching policies"""
        response = client.get(
            "/api/v1/policies/search?q=data+retention&type=privacy_policy",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total_count" in data
    
    @pytest.mark.asyncio
    async def test_policy_compliance_monitoring(self, client, auth_headers):
        """Test policy compliance monitoring setup"""
        policy_id = str(uuid4())
        monitoring_config = {
            "check_frequency": "monthly",
            "frameworks": ["GDPR", "CCPA"],
            "alert_email": "compliance@company.com"
        }
        
        response = client.post(
            f"/api/v1/policies/{policy_id}/monitoring",
            json=monitoring_config,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["monitoring_enabled"] is True
        assert data["next_check"] is not None


@pytest.mark.integration
class TestPolicyIntegration:
    """Integration tests for policy workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_policy_workflow(self, client, auth_headers, db_session):
        """Test complete policy generation and management workflow"""
        # 1. Generate policy with AI
        generation_request = {
            "policy_type": "privacy_policy",
            "framework": "GDPR",
            "business_context": {
                "company_name": "WorkflowTest Inc",
                "industry": "saas"
            }
        }
        
        generate_response = client.post(
            "/api/v1/ai/policies/generate",
            json=generation_request,
            headers=auth_headers
        )
        assert generate_response.status_code == 201
        policy = generate_response.json()
        policy_id = policy["id"]
        
        # 2. Validate policy compliance
        validate_response = client.post(
            "/api/v1/policies/validate",
            json={
                "policy_content": policy["policy_content"],
                "framework": "GDPR"
            },
            headers=auth_headers
        )
        assert validate_response.status_code == 200
        validation = validate_response.json()
        
        # 3. Enhance policy if needed
        if validation["score"] < 90:
            enhance_response = client.post(
                "/api/v1/ai/policies/enhance",
                json={
                    "policy_id": policy_id,
                    "enhancements": ["strengthen_compliance"]
                },
                headers=auth_headers
            )
            assert enhance_response.status_code == 200
        
        # 4. Submit for approval
        approval_response = client.post(
            f"/api/v1/policies/{policy_id}/submit-approval",
            json={"approvers": ["legal@test.com"]},
            headers=auth_headers
        )
        assert approval_response.status_code == 200
        
        # 5. Publish policy
        publish_response = client.post(
            f"/api/v1/policies/{policy_id}/publish",
            json={"effective_date": "2024-01-15"},
            headers=auth_headers
        )
        assert publish_response.status_code == 200
        
        # 6. Export policy
        export_response = client.get(
            f"/api/v1/policies/{policy_id}/export?format=pdf",
            headers=auth_headers
        )
        assert export_response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_multi_framework_policy_generation(self, client, auth_headers):
        """Test generating policy compliant with multiple frameworks"""
        request_data = {
            "policy_type": "privacy_policy",
            "frameworks": ["GDPR", "CCPA", "LGPD"],
            "business_context": {
                "company_name": "GlobalCorp",
                "regions": ["EU", "US", "Brazil"]
            }
        }
        
        response = client.post(
            "/api/v1/ai/policies/multi-framework",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify policy covers all frameworks
        assert "gdpr" in data["policy_content"].lower()
        assert "ccpa" in data["policy_content"].lower()
        assert "lgpd" in data["policy_content"].lower()
        
        # Check compliance scores for each framework
        assert "compliance_scores" in data
        assert len(data["compliance_scores"]) == 3