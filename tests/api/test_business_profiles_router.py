"""
Comprehensive tests for the business profiles API router.
QA Specialist - Day 4 Coverage Enhancement
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.user import User


@pytest.fixture
def mock_user():
    """Create a mock authenticated user."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.email = "test@example.com"
    user.is_active = True
    user.company_name = "Test Company"
    return user


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_business_profile():
    """Create a sample business profile."""
    return {
        "id": str(uuid4()),
        "company_name": "Test Company",
        "industry": "Technology",
        "company_size": "50-250",
        "location": "United States",
        "description": "A test company description",
        "website": "https://example.com",
        "founded_year": 2020,
        "compliance_frameworks": ["GDPR", "CCPA"],
        "risk_level": "Medium",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }


@pytest.fixture
def business_profile_create_request():
    """Create a business profile creation request."""
    return {
        "company_name": "New Company",
        "industry": "Healthcare",
        "company_size": "10-50",
        "location": "Canada",
        "description": "Healthcare technology company",
        "website": "https://newcompany.com",
        "founded_year": 2022,
        "compliance_frameworks": ["HIPAA", "GDPR"]
    }


class TestBusinessProfilesRouter:
    """Test cases for business profiles API endpoints."""

    @pytest.mark.asyncio
    async def test_get_business_profile_success(
        self, mock_user, mock_db_session, sample_business_profile
    ):
        """Test successful retrieval of business profile."""
        from api.routers.business_profiles import get_business_profile
        
        with patch('api.routers.business_profiles.get_profile_by_user_id', 
                   new_callable=AsyncMock) as mock_get_profile:
            mock_get_profile.return_value = sample_business_profile
            
            result = await get_business_profile(
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == sample_business_profile
            mock_get_profile.assert_called_once_with(
                mock_db_session,
                mock_user.id
            )

    @pytest.mark.asyncio
    async def test_get_business_profile_not_found(
        self, mock_user, mock_db_session
    ):
        """Test retrieving business profile when none exists."""
        from api.routers.business_profiles import get_business_profile
        
        with patch('api.routers.business_profiles.get_profile_by_user_id', 
                   new_callable=AsyncMock) as mock_get_profile:
            mock_get_profile.return_value = None
            
            result = await get_business_profile(
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result is None

    @pytest.mark.asyncio
    async def test_create_business_profile_success(
        self, mock_user, mock_db_session, business_profile_create_request, sample_business_profile
    ):
        """Test successful creation of business profile."""
        from api.routers.business_profiles import create_business_profile
        
        with patch('api.routers.business_profiles.create_profile', 
                   new_callable=AsyncMock) as mock_create:
            mock_create.return_value = sample_business_profile
            
            result = await create_business_profile(
                profile_data=business_profile_create_request,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == sample_business_profile
            mock_create.assert_called_once_with(
                mock_db_session,
                mock_user.id,
                business_profile_create_request
            )

    @pytest.mark.asyncio
    async def test_create_business_profile_duplicate(
        self, mock_user, mock_db_session, business_profile_create_request
    ):
        """Test creating business profile when one already exists."""
        from api.routers.business_profiles import create_business_profile
        
        with patch('api.routers.business_profiles.create_profile', 
                   new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = ValueError("Profile already exists")
            
            with pytest.raises(ValueError) as exc_info:
                await create_business_profile(
                    profile_data=business_profile_create_request,
                    current_user=mock_user,
                    db=mock_db_session
                )
            
            assert "Profile already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_business_profile_success(
        self, mock_user, mock_db_session, sample_business_profile
    ):
        """Test successful update of business profile."""
        from api.routers.business_profiles import update_business_profile
        
        update_data = {
            "industry": "Financial Services",
            "company_size": "250-1000"
        }
        
        updated_profile = {**sample_business_profile, **update_data}
        
        with patch('api.routers.business_profiles.update_profile', 
                   new_callable=AsyncMock) as mock_update:
            mock_update.return_value = updated_profile
            
            result = await update_business_profile(
                profile_data=update_data,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == updated_profile
            assert result["industry"] == "Financial Services"
            assert result["company_size"] == "250-1000"

    @pytest.mark.asyncio
    async def test_update_business_profile_not_found(
        self, mock_user, mock_db_session
    ):
        """Test updating non-existent business profile."""
        from api.routers.business_profiles import update_business_profile
        
        update_data = {"industry": "Technology"}
        
        with patch('api.routers.business_profiles.update_profile', 
                   new_callable=AsyncMock) as mock_update:
            mock_update.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await update_business_profile(
                    profile_data=update_data,
                    current_user=mock_user,
                    db=mock_db_session
                )
            
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_business_profile_success(
        self, mock_user, mock_db_session
    ):
        """Test successful deletion of business profile."""
        from api.routers.business_profiles import delete_business_profile_by_id as delete_business_profile
        
        with patch('api.routers.business_profiles.delete_profile', 
                   new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = True
            
            result = await delete_business_profile(
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == {"message": "Business profile deleted successfully"}
            mock_delete.assert_called_once_with(
                mock_db_session,
                mock_user.id
            )

    @pytest.mark.asyncio
    async def test_delete_business_profile_not_found(
        self, mock_user, mock_db_session
    ):
        """Test deleting non-existent business profile."""
        from api.routers.business_profiles import delete_business_profile_by_id as delete_business_profile
        
        with patch('api.routers.business_profiles.delete_profile', 
                   new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = False
            
            with pytest.raises(HTTPException) as exc_info:
                await delete_business_profile(
                    current_user=mock_user,
                    db=mock_db_session
                )
            
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_compliance_frameworks_success(
        self, mock_user, mock_db_session
    ):
        """Test retrieving compliance frameworks for a business."""
        from api.routers.business_profiles import get_compliance_frameworks
        
        frameworks = ["GDPR", "CCPA", "HIPAA", "SOC2"]
        
        with patch('api.routers.business_profiles.get_frameworks_for_profile', 
                   new_callable=AsyncMock) as mock_get_frameworks:
            mock_get_frameworks.return_value = frameworks
            
            result = await get_compliance_frameworks(
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == {"frameworks": frameworks}
            assert len(result["frameworks"]) == 4

    @pytest.mark.asyncio
    async def test_update_compliance_frameworks_success(
        self, mock_user, mock_db_session
    ):
        """Test updating compliance frameworks."""
        from api.routers.business_profiles import update_compliance_frameworks
        
        new_frameworks = ["ISO27001", "PCI-DSS"]
        
        with patch('api.routers.business_profiles.update_frameworks', 
                   new_callable=AsyncMock) as mock_update:
            mock_update.return_value = new_frameworks
            
            result = await update_compliance_frameworks(
                frameworks=new_frameworks,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == {"frameworks": new_frameworks, "message": "Frameworks updated"}

    @pytest.mark.asyncio
    async def test_get_risk_assessment_success(
        self, mock_user, mock_db_session
    ):
        """Test retrieving risk assessment for business profile."""
        from api.routers.business_profiles import get_risk_assessment
        
        risk_data = {
            "risk_level": "High",
            "risk_score": 75,
            "risk_factors": [
                "Large data processing",
                "International operations",
                "Sensitive data handling"
            ],
            "recommendations": [
                "Implement data encryption",
                "Conduct regular audits",
                "Update privacy policies"
            ]
        }
        
        with patch('api.routers.business_profiles.calculate_risk_assessment', 
                   new_callable=AsyncMock) as mock_risk:
            mock_risk.return_value = risk_data
            
            result = await get_risk_assessment(
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == risk_data
            assert result["risk_level"] == "High"
            assert result["risk_score"] == 75

    @pytest.mark.asyncio
    async def test_validate_business_profile_success(
        self, mock_user, mock_db_session, sample_business_profile
    ):
        """Test business profile validation."""
        from api.routers.business_profiles import validate_business_profile
        
        validation_result = {
            "is_valid": True,
            "completeness": 95,
            "missing_fields": ["tax_id"],
            "warnings": []
        }
        
        with patch('api.routers.business_profiles.validate_profile', 
                   new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = validation_result
            
            result = await validate_business_profile(
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == validation_result
            assert result["is_valid"] is True
            assert result["completeness"] == 95

    @pytest.mark.asyncio
    async def test_export_business_profile_json(
        self, mock_user, mock_db_session, sample_business_profile
    ):
        """Test exporting business profile as JSON."""
        from api.routers.business_profiles import export_business_profile
        
        with patch('api.routers.business_profiles.get_profile_by_user_id', 
                   new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_business_profile
            
            result = await export_business_profile(
                format="json",
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == sample_business_profile
            assert "company_name" in result

    @pytest.mark.asyncio
    async def test_business_profile_history(
        self, mock_user, mock_db_session
    ):
        """Test retrieving business profile change history."""
        from api.routers.business_profiles import get_profile_history
        
        history = [
            {
                "change_id": str(uuid4()),
                "field": "industry",
                "old_value": "Technology",
                "new_value": "Healthcare",
                "changed_at": datetime.utcnow().isoformat(),
                "changed_by": mock_user.id
            },
            {
                "change_id": str(uuid4()),
                "field": "company_size",
                "old_value": "10-50",
                "new_value": "50-250",
                "changed_at": datetime.utcnow().isoformat(),
                "changed_by": mock_user.id
            }
        ]
        
        with patch('api.routers.business_profiles.get_change_history', 
                   new_callable=AsyncMock) as mock_history:
            mock_history.return_value = history
            
            result = await get_profile_history(
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == {"history": history}
            assert len(result["history"]) == 2

    @pytest.mark.asyncio
    async def test_business_profile_analytics(
        self, mock_user, mock_db_session
    ):
        """Test retrieving business profile analytics."""
        from api.routers.business_profiles import get_profile_analytics
        
        analytics = {
            "profile_completeness": 85,
            "compliance_readiness": 72,
            "risk_score": 45,
            "industry_benchmark": {
                "average_compliance": 68,
                "your_position": "Above Average"
            },
            "recommendations_count": 8,
            "pending_tasks": 3
        }
        
        with patch('api.routers.business_profiles.calculate_analytics', 
                   new_callable=AsyncMock) as mock_analytics:
            mock_analytics.return_value = analytics
            
            result = await get_profile_analytics(
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == analytics
            assert result["profile_completeness"] == 85