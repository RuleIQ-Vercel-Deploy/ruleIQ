"""
Comprehensive tests for the policies API router.
QA Specialist - Day 4 Coverage Enhancement
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.routers.policies import (
    generate_policy,
    list_policies,
    get_policy
)
from api.schemas.models import PolicyGenerateRequest
from database.user import User


@pytest.fixture
def mock_user():
    """Create a mock authenticated user."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.email = "test@example.com"
    user.is_active = True
    return user


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_policy_request():
    """Create a sample policy generation request."""
    return PolicyGenerateRequest(
        framework_id=uuid4(),
        policy_type="comprehensive",
        custom_requirements=["Requirement 1", "Requirement 2"]
    )


@pytest.fixture
def sample_policy():
    """Create a sample policy object."""
    return MagicMock(
        id=uuid4(),
        policy_name="Test Policy",
        policy_content="Policy content here",
        framework_name="GDPR",
        policy_type="comprehensive",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        sections=["Section 1", "Section 2"]
    )


class TestPoliciesRouter:
    """Test cases for policies API endpoints."""

    @pytest.mark.asyncio
    async def test_generate_policy_success(
        self, mock_user, mock_db_session, sample_policy_request, sample_policy
    ):
        """Test successful policy generation."""
        with patch('api.routers.policies.generate_compliance_policy', 
                   new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = sample_policy
            
            result = await generate_policy(
                request=sample_policy_request,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result['id'] == sample_policy.id
            assert result['policy_name'] == sample_policy.policy_name
            assert result['content'] == sample_policy.policy_content
            assert result['status'] == 'draft'
            assert result['success_message'] == 'Your compliance policy has been generated and is ready for review'
            assert len(result['next_steps']) == 4
            assert len(result['recommended_actions']) == 3
            
            mock_generate.assert_called_once_with(
                mock_db_session,
                mock_user.id,
                sample_policy_request.framework_id,
                sample_policy_request.policy_type,
                sample_policy_request.custom_requirements
            )

    @pytest.mark.asyncio
    async def test_generate_policy_without_optional_fields(
        self, mock_user, mock_db_session, sample_policy
    ):
        """Test policy generation without optional fields."""
        request = MagicMock()
        request.framework_id = uuid4()
        # Don't set policy_type or custom_requirements
        
        with patch('api.routers.policies.generate_compliance_policy', 
                   new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = sample_policy
            
            result = await generate_policy(
                request=request,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result['id'] == sample_policy.id
            mock_generate.assert_called_once_with(
                mock_db_session,
                mock_user.id,
                request.framework_id,
                'comprehensive',  # Default value
                []  # Default empty list
            )

    @pytest.mark.asyncio
    async def test_generate_policy_service_error(
        self, mock_user, mock_db_session, sample_policy_request
    ):
        """Test policy generation when service raises an error."""
        with patch('api.routers.policies.generate_compliance_policy', 
                   new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = Exception("Service error")
            
            with pytest.raises(Exception) as exc_info:
                await generate_policy(
                    request=sample_policy_request,
                    current_user=mock_user,
                    db=mock_db_session
                )
            
            assert str(exc_info.value) == "Service error"

    @pytest.mark.asyncio
    async def test_list_policies_success(self, mock_user, mock_db_session):
        """Test successful listing of user policies."""
        mock_policies = [
            MagicMock(id=uuid4(), policy_name="Policy 1"),
            MagicMock(id=uuid4(), policy_name="Policy 2"),
            MagicMock(id=uuid4(), policy_name="Policy 3")
        ]
        
        with patch('api.routers.policies.get_user_policies', 
                   new_callable=AsyncMock) as mock_get_policies:
            mock_get_policies.return_value = mock_policies
            
            result = await list_policies(
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert 'policies' in result
            assert len(result['policies']) == 3
            assert result['policies'] == mock_policies
            
            mock_get_policies.assert_called_once_with(
                mock_db_session,
                mock_user.id
            )

    @pytest.mark.asyncio
    async def test_list_policies_empty(self, mock_user, mock_db_session):
        """Test listing policies when user has none."""
        with patch('api.routers.policies.get_user_policies', 
                   new_callable=AsyncMock) as mock_get_policies:
            mock_get_policies.return_value = []
            
            result = await list_policies(
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert 'policies' in result
            assert len(result['policies']) == 0

    @pytest.mark.asyncio
    async def test_get_policy_success(self, mock_user, mock_db_session, sample_policy):
        """Test successful retrieval of a specific policy."""
        policy_id = uuid4()
        
        with patch('api.routers.policies.get_policy_by_id', 
                   new_callable=AsyncMock) as mock_get_policy:
            mock_get_policy.return_value = sample_policy
            
            result = await get_policy(
                policy_id=policy_id,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == sample_policy
            mock_get_policy.assert_called_once_with(
                mock_db_session,
                policy_id,
                mock_user.id
            )

    @pytest.mark.asyncio
    async def test_get_policy_not_found(self, mock_user, mock_db_session):
        """Test retrieving a non-existent policy."""
        policy_id = uuid4()
        
        with patch('api.routers.policies.get_policy_by_id', 
                   new_callable=AsyncMock) as mock_get_policy:
            mock_get_policy.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await get_policy(
                    policy_id=policy_id,
                    current_user=mock_user,
                    db=mock_db_session
                )
            
            assert exc_info.value.status_code == 404
            assert "Policy not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_policy_unauthorized(self, mock_user, mock_db_session):
        """Test retrieving a policy user doesn't own."""
        policy_id = uuid4()
        
        with patch('api.routers.policies.get_policy_by_id', 
                   new_callable=AsyncMock) as mock_get_policy:
            # Simulate unauthorized access by returning None
            mock_get_policy.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await get_policy(
                    policy_id=policy_id,
                    current_user=mock_user,
                    db=mock_db_session
                )
            
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_generate_policy_with_validation_error(
        self, mock_user, mock_db_session
    ):
        """Test policy generation with invalid request data."""
        # Create request with missing required field
        request = MagicMock()
        # Don't set framework_id
        
        with pytest.raises(AttributeError):
            await generate_policy(
                request=request,
                current_user=mock_user,
                db=mock_db_session
            )

    @pytest.mark.asyncio
    async def test_generate_policy_database_error(
        self, mock_user, mock_db_session, sample_policy_request
    ):
        """Test policy generation when database error occurs."""
        with patch('api.routers.policies.generate_compliance_policy', 
                   new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = Exception("Database connection failed")
            
            with pytest.raises(Exception) as exc_info:
                await generate_policy(
                    request=sample_policy_request,
                    current_user=mock_user,
                    db=mock_db_session
                )
            
            assert "Database connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_policies_database_error(self, mock_user, mock_db_session):
        """Test listing policies when database error occurs."""
        with patch('api.routers.policies.get_user_policies', 
                   new_callable=AsyncMock) as mock_get_policies:
            mock_get_policies.side_effect = Exception("Database error")
            
            with pytest.raises(Exception) as exc_info:
                await list_policies(
                    current_user=mock_user,
                    db=mock_db_session
                )
            
            assert "Database error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_policy_with_large_requirements(
        self, mock_user, mock_db_session, sample_policy
    ):
        """Test policy generation with many custom requirements."""
        request = PolicyGenerateRequest(
            framework_id=uuid4(),
            policy_type="comprehensive",
            custom_requirements=[f"Requirement {i}" for i in range(100)]
        )
        
        with patch('api.routers.policies.generate_compliance_policy', 
                   new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = sample_policy
            
            result = await generate_policy(
                request=request,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result['id'] == sample_policy.id
            # Verify all 100 requirements were passed
            call_args = mock_generate.call_args
            assert len(call_args[0][4]) == 100

    @pytest.mark.asyncio
    async def test_generate_policy_response_structure(
        self, mock_user, mock_db_session, sample_policy_request, sample_policy
    ):
        """Test that generated policy response has correct structure."""
        with patch('api.routers.policies.generate_compliance_policy', 
                   new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = sample_policy
            
            result = await generate_policy(
                request=sample_policy_request,
                current_user=mock_user,
                db=mock_db_session
            )
            
            # Check all required fields are present
            required_fields = [
                'id', 'policy_name', 'content', 'status',
                'framework_name', 'policy_type', 'created_at',
                'updated_at', 'sections', 'message', 'success_message',
                'next_steps', 'recommended_actions'
            ]
            
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"

    @pytest.mark.asyncio
    async def test_list_policies_with_pagination(self, mock_user, mock_db_session):
        """Test listing policies with pagination support."""
        # Create many mock policies
        mock_policies = [
            MagicMock(id=uuid4(), policy_name=f"Policy {i}")
            for i in range(50)
        ]
        
        with patch('api.routers.policies.get_user_policies', 
                   new_callable=AsyncMock) as mock_get_policies:
            mock_get_policies.return_value = mock_policies
            
            result = await list_policies(
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert len(result['policies']) == 50