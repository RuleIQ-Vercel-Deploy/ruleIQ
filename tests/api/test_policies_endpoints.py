"""
Test suite for Policy API endpoints
P3 Task: Test Coverage Enhancement - Day 2
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.routers import policies
from api.schemas.models import (
    GeneratedPolicyResponse as Policy,
    PolicyGenerateRequest as PolicyCreate,
    PolicyGenerateRequest as PolicyUpdate,
    GeneratedPolicyResponse as PolicyResponse,
    PolicyListResponse,
    GeneratedPolicyResponse as PolicyVersion,
    PolicyGenerateRequest as PolicyApproval
)
from database import User


class TestPoliciesEndpoints:
    """Test suite for policy management endpoints"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        mock = AsyncMock(spec=AsyncSession)
        return mock
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return User(
            id="test-user-123",
            email="test@example.com",
            is_active=True,
            organization_id="org-123",
            role="admin"
        )
    
    @pytest.fixture
    def sample_policy(self):
        """Sample policy for testing"""
        return Policy(
            id="policy-123",
            name="Data Protection Policy",
            description="Policy for handling personal data",
            category="Privacy",
            status="draft",
            version="1.0",
            content="Policy content here...",
            organization_id="org-123",
            created_by="test-user-123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
    
    @pytest.fixture
    def policy_create_data(self):
        """Policy creation data"""
        return PolicyCreate(
            name="Information Security Policy",
            description="Company-wide security policy",
            category="Security",
            content="# Information Security Policy\n\n## Purpose\n...",
            framework_id="fw-iso27001",
            requirements=["req-1", "req-2"]
        )
    
    @pytest.mark.asyncio
    async def test_list_policies_success(self, mock_db, mock_user):
        """Test successful policy listing"""
        # Arrange
        with patch('api.routers.policies.get_policy_service') as mock_service:
            mock_service.return_value.list_policies = AsyncMock(
                return_value={
                    "policies": [
                        {
                            "id": "pol-1",
                            "name": "Security Policy",
                            "status": "approved",
                            "version": "2.0"
                        },
                        {
                            "id": "pol-2",
                            "name": "Privacy Policy",
                            "status": "draft",
                            "version": "1.0"
                        }
                    ],
                    "total": 2
                }
            )
            
            # Act
            response = await policies.list_policies(
                db=mock_db,
                current_user=mock_user,
                skip=0,
                limit=10,
                status=None,
                category=None
            )
            
            # Assert
            assert len(response["policies"]) == 2
            assert response["total"] == 2
            mock_service.return_value.list_policies.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_policies_with_filters(self, mock_db, mock_user):
        """Test policy listing with status and category filters"""
        # Arrange
        with patch('api.routers.policies.get_policy_service') as mock_service:
            mock_service.return_value.list_policies = AsyncMock(
                return_value={
                    "policies": [{"id": "pol-1", "status": "approved"}],
                    "total": 1
                }
            )
            
            # Act
            response = await policies.list_policies(
                db=mock_db,
                current_user=mock_user,
                skip=0,
                limit=10,
                status="approved",
                category="Security"
            )
            
            # Assert
            assert len(response["policies"]) == 1
            mock_service.return_value.list_policies.assert_called_with(
                mock_db,
                organization_id=mock_user.organization_id,
                skip=0,
                limit=10,
                status="approved",
                category="Security"
            )
    
    @pytest.mark.asyncio
    async def test_get_policy_by_id_success(self, mock_db, mock_user, sample_policy):
        """Test successful policy retrieval by ID"""
        # Arrange
        with patch('api.routers.policies.get_policy_service') as mock_service:
            mock_service.return_value.get_policy = AsyncMock(
                return_value=sample_policy.dict()
            )
            
            # Act
            response = await policies.get_policy(
                policy_id="policy-123",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["id"] == "policy-123"
            assert response["name"] == "Data Protection Policy"
    
    @pytest.mark.asyncio
    async def test_create_policy_success(self, mock_db, mock_user, policy_create_data):
        """Test successful policy creation"""
        # Arrange
        with patch('api.routers.policies.get_policy_service') as mock_service:
            created_policy = {
                "id": "new-policy-123",
                **policy_create_data.dict(),
                "status": "draft",
                "version": "1.0",
                "created_at": datetime.now(UTC).isoformat()
            }
            mock_service.return_value.create_policy = AsyncMock(
                return_value=created_policy
            )
            
            # Act
            response = await policies.create_policy(
                policy=policy_create_data,
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["id"] == "new-policy-123"
            assert response["status"] == "draft"
    
    @pytest.mark.asyncio
    async def test_generate_policy_with_ai(self, mock_db, mock_user):
        """Test AI-assisted policy generation"""
        # Arrange
        generation_request = {
            "framework_id": "fw-iso27001",
            "requirements": ["req-1", "req-2"],
            "organization_context": "Tech company with 100 employees"
        }
        
        with patch('api.routers.policies.get_ai_service') as mock_ai_service:
            mock_ai_service.return_value.generate_policy = AsyncMock(
                return_value={
                    "name": "Generated Security Policy",
                    "content": "# Security Policy\n\nGenerated content...",
                    "requirements_covered": ["req-1", "req-2"]
                }
            )
            
            # Act
            response = await policies.generate_policy(
                generation_request=generation_request,
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["name"] == "Generated Security Policy"
            assert len(response["requirements_covered"]) == 2
    
    @pytest.mark.asyncio
    async def test_update_policy_success(self, mock_db, mock_user):
        """Test successful policy update"""
        # Arrange
        update_data = PolicyUpdate(
            description="Updated description",
            content="Updated content",
            version="1.1"
        )
        
        with patch('api.routers.policies.get_policy_service') as mock_service:
            updated_policy = {
                "id": "policy-123",
                "description": "Updated description",
                "version": "1.1",
                "updated_at": datetime.now(UTC).isoformat()
            }
            mock_service.return_value.update_policy = AsyncMock(
                return_value=updated_policy
            )
            
            # Act
            response = await policies.update_policy(
                policy_id="policy-123",
                policy_update=update_data,
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["version"] == "1.1"
    
    @pytest.mark.asyncio
    async def test_submit_policy_for_approval(self, mock_db, mock_user):
        """Test submitting policy for approval"""
        # Arrange
        with patch('api.routers.policies.get_policy_service') as mock_service:
            mock_service.return_value.submit_for_approval = AsyncMock(
                return_value={
                    "id": "policy-123",
                    "status": "pending_approval",
                    "submitted_at": datetime.now(UTC).isoformat()
                }
            )
            
            # Act
            response = await policies.submit_for_approval(
                policy_id="policy-123",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["status"] == "pending_approval"
    
    @pytest.mark.asyncio
    async def test_approve_policy_success(self, mock_db, mock_user):
        """Test policy approval"""
        # Arrange
        approval_data = PolicyApproval(
            approved=True,
            comments="Looks good, approved."
        )
        
        with patch('api.routers.policies.get_policy_service') as mock_service:
            mock_service.return_value.approve_policy = AsyncMock(
                return_value={
                    "id": "policy-123",
                    "status": "approved",
                    "approved_by": mock_user.id,
                    "approved_at": datetime.now(UTC).isoformat()
                }
            )
            
            # Act
            response = await policies.approve_policy(
                policy_id="policy-123",
                approval=approval_data,
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_reject_policy_with_comments(self, mock_db, mock_user):
        """Test policy rejection with comments"""
        # Arrange
        approval_data = PolicyApproval(
            approved=False,
            comments="Needs more detail in section 3"
        )
        
        with patch('api.routers.policies.get_policy_service') as mock_service:
            mock_service.return_value.approve_policy = AsyncMock(
                return_value={
                    "id": "policy-123",
                    "status": "rejected",
                    "rejection_comments": "Needs more detail in section 3"
                }
            )
            
            # Act
            response = await policies.approve_policy(
                policy_id="policy-123",
                approval=approval_data,
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["status"] == "rejected"
    
    @pytest.mark.asyncio
    async def test_get_policy_versions(self, mock_db, mock_user):
        """Test getting policy version history"""
        # Arrange
        with patch('api.routers.policies.get_policy_service') as mock_service:
            mock_service.return_value.get_versions = AsyncMock(
                return_value=[
                    {
                        "version": "1.0",
                        "created_at": "2024-01-01T00:00:00",
                        "created_by": "user-1",
                        "changes": "Initial version"
                    },
                    {
                        "version": "1.1",
                        "created_at": "2024-01-15T00:00:00",
                        "created_by": "user-2",
                        "changes": "Updated section 2"
                    }
                ]
            )
            
            # Act
            response = await policies.get_policy_versions(
                policy_id="policy-123",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert len(response) == 2
            assert response[0]["version"] == "1.0"
            assert response[1]["version"] == "1.1"
    
    @pytest.mark.asyncio
    async def test_clone_policy_success(self, mock_db, mock_user):
        """Test policy cloning"""
        # Arrange
        with patch('api.routers.policies.get_policy_service') as mock_service:
            mock_service.return_value.clone_policy = AsyncMock(
                return_value={
                    "id": "cloned-policy-456",
                    "name": "Data Protection Policy (Copy)",
                    "status": "draft",
                    "version": "1.0"
                }
            )
            
            # Act
            response = await policies.clone_policy(
                policy_id="policy-123",
                new_name="Data Protection Policy (Copy)",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["id"] == "cloned-policy-456"
            assert "Copy" in response["name"]
    
    @pytest.mark.asyncio
    async def test_delete_policy_success(self, mock_db, mock_user):
        """Test policy deletion"""
        # Arrange
        with patch('api.routers.policies.get_policy_service') as mock_service:
            mock_service.return_value.delete_policy = AsyncMock(return_value=True)
            
            # Act
            response = await policies.delete_policy(
                policy_id="policy-123",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response == {"message": "Policy deleted successfully"}
    
    @pytest.mark.asyncio
    async def test_export_policy_to_pdf(self, mock_db, mock_user):
        """Test policy export to PDF"""
        # Arrange
        with patch('api.routers.policies.get_policy_service') as mock_service:
            mock_service.return_value.export_policy = AsyncMock(
                return_value={
                    "format": "pdf",
                    "filename": "policy-123.pdf",
                    "content": b"PDF content here"
                }
            )
            
            # Act
            response = await policies.export_policy(
                policy_id="policy-123",
                format="pdf",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["format"] == "pdf"
            assert response["filename"] == "policy-123.pdf"
    
    @pytest.mark.asyncio
    async def test_check_policy_compliance(self, mock_db, mock_user):
        """Test policy compliance check"""
        # Arrange
        with patch('api.routers.policies.get_compliance_service') as mock_compliance:
            mock_compliance.return_value.check_policy_compliance = AsyncMock(
                return_value={
                    "compliance_score": 0.85,
                    "gaps": [
                        {"requirement": "req-3", "status": "missing"},
                        {"requirement": "req-4", "status": "partial"}
                    ],
                    "recommendations": ["Add section on incident response"]
                }
            )
            
            # Act
            response = await policies.check_policy_compliance(
                policy_id="policy-123",
                framework_id="fw-iso27001",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["compliance_score"] == 0.85
            assert len(response["gaps"]) == 2
    
    @pytest.mark.asyncio
    async def test_search_policies(self, mock_db, mock_user):
        """Test policy search functionality"""
        # Arrange
        with patch('api.routers.policies.get_policy_service') as mock_service:
            mock_service.return_value.search_policies = AsyncMock(
                return_value={
                    "results": [
                        {
                            "id": "pol-1",
                            "name": "Data Protection Policy",
                            "relevance_score": 0.95
                        }
                    ],
                    "total": 1
                }
            )
            
            # Act
            response = await policies.search_policies(
                query="data protection",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert len(response["results"]) == 1
            assert response["results"][0]["relevance_score"] == 0.95