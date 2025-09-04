"""
Test suite for Framework API endpoints
P3 Task: Test Coverage Enhancement - Day 2
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import json

from api.routers import frameworks
from api.schemas.models import (
    ComplianceFrameworkResponse as Framework,
    ComplianceFrameworkResponse as FrameworkCreate,
    ComplianceFrameworkResponse as FrameworkUpdate,
    ComplianceFrameworkResponse as FrameworkResponse,
    PolicyListResponse as FrameworkListResponse,
    ComplianceFrameworkResponse as RequirementResponse,
    ComplianceFrameworkResponse as ControlResponse
)
from database import User


class TestFrameworksEndpoints:
    """Test suite for framework management endpoints"""
    
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
            organization_id="org-123"
        )
    
    @pytest.fixture
    def sample_framework(self):
        """Sample framework for testing"""
        return Framework(
            id="fw-123",
            name="ISO 27001",
            description="Information Security Management",
            version="2022",
            category="Security",
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
    
    @pytest.fixture
    def framework_create_data(self):
        """Framework creation data"""
        return FrameworkCreate(
            name="SOC 2",
            description="Service Organization Control",
            version="Type II",
            category="Compliance",
            requirements=[
                {
                    "code": "CC1.1",
                    "description": "Control Environment",
                    "category": "Common Criteria"
                }
            ]
        )
    
    @pytest.mark.asyncio
    async def test_list_frameworks_success(self, mock_db, mock_user):
        """Test successful framework listing"""
        # Arrange
        with patch('api.routers.frameworks.get_framework_service') as mock_service:
            mock_service.return_value.list_frameworks = AsyncMock(
                return_value={
                    "frameworks": [
                        {"id": "fw-1", "name": "ISO 27001", "category": "Security"},
                        {"id": "fw-2", "name": "GDPR", "category": "Privacy"}
                    ],
                    "total": 2
                }
            )
            
            # Act
            response = await frameworks.list_frameworks(
                db=mock_db,
                current_user=mock_user,
                skip=0,
                limit=10,
                category=None,
                search=None
            )
            
            # Assert
            assert isinstance(response, dict)
            assert len(response["frameworks"]) == 2
            assert response["total"] == 2
            mock_service.return_value.list_frameworks.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_frameworks_with_filters(self, mock_db, mock_user):
        """Test framework listing with category and search filters"""
        # Arrange
        with patch('api.routers.frameworks.get_framework_service') as mock_service:
            mock_service.return_value.list_frameworks = AsyncMock(
                return_value={
                    "frameworks": [{"id": "fw-1", "name": "ISO 27001", "category": "Security"}],
                    "total": 1
                }
            )
            
            # Act
            response = await frameworks.list_frameworks(
                db=mock_db,
                current_user=mock_user,
                skip=0,
                limit=10,
                category="Security",
                search="ISO"
            )
            
            # Assert
            assert len(response["frameworks"]) == 1
            assert response["frameworks"][0]["category"] == "Security"
            mock_service.return_value.list_frameworks.assert_called_with(
                mock_db, 
                organization_id=mock_user.organization_id,
                skip=0,
                limit=10,
                category="Security",
                search="ISO"
            )
    
    @pytest.mark.asyncio
    async def test_get_framework_by_id_success(self, mock_db, mock_user, sample_framework):
        """Test successful framework retrieval by ID"""
        # Arrange
        with patch('api.routers.frameworks.get_framework_service') as mock_service:
            mock_service.return_value.get_framework = AsyncMock(
                return_value=sample_framework.dict()
            )
            
            # Act
            response = await frameworks.get_framework(
                framework_id="fw-123",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["id"] == "fw-123"
            assert response["name"] == "ISO 27001"
            mock_service.return_value.get_framework.assert_called_with(
                mock_db,
                "fw-123",
                mock_user.organization_id
            )
    
    @pytest.mark.asyncio
    async def test_get_framework_not_found(self, mock_db, mock_user):
        """Test framework retrieval with non-existent ID"""
        # Arrange
        with patch('api.routers.frameworks.get_framework_service') as mock_service:
            mock_service.return_value.get_framework = AsyncMock(return_value=None)
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await frameworks.get_framework(
                    framework_id="non-existent",
                    db=mock_db,
                    current_user=mock_user
                )
            
            assert exc_info.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_framework_success(self, mock_db, mock_user, framework_create_data):
        """Test successful framework creation"""
        # Arrange
        with patch('api.routers.frameworks.get_framework_service') as mock_service:
            created_framework = {
                "id": "new-fw-123",
                **framework_create_data.dict(),
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat()
            }
            mock_service.return_value.create_framework = AsyncMock(
                return_value=created_framework
            )
            
            # Act
            response = await frameworks.create_framework(
                framework=framework_create_data,
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["id"] == "new-fw-123"
            assert response["name"] == "SOC 2"
            mock_service.return_value.create_framework.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_framework_duplicate_name(self, mock_db, mock_user, framework_create_data):
        """Test framework creation with duplicate name"""
        # Arrange
        with patch('api.routers.frameworks.get_framework_service') as mock_service:
            mock_service.return_value.create_framework = AsyncMock(
                side_effect=ValueError("Framework with this name already exists")
            )
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await frameworks.create_framework(
                    framework=framework_create_data,
                    db=mock_db,
                    current_user=mock_user
                )
            
            assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_update_framework_success(self, mock_db, mock_user):
        """Test successful framework update"""
        # Arrange
        update_data = FrameworkUpdate(
            description="Updated description",
            version="2023"
        )
        
        with patch('api.routers.frameworks.get_framework_service') as mock_service:
            updated_framework = {
                "id": "fw-123",
                "name": "ISO 27001",
                "description": "Updated description",
                "version": "2023",
                "updated_at": datetime.now(UTC).isoformat()
            }
            mock_service.return_value.update_framework = AsyncMock(
                return_value=updated_framework
            )
            
            # Act
            response = await frameworks.update_framework(
                framework_id="fw-123",
                framework_update=update_data,
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["description"] == "Updated description"
            assert response["version"] == "2023"
    
    @pytest.mark.asyncio
    async def test_delete_framework_success(self, mock_db, mock_user):
        """Test successful framework deletion"""
        # Arrange
        with patch('api.routers.frameworks.get_framework_service') as mock_service:
            mock_service.return_value.delete_framework = AsyncMock(return_value=True)
            
            # Act
            response = await frameworks.delete_framework(
                framework_id="fw-123",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response == {"message": "Framework deleted successfully"}
            mock_service.return_value.delete_framework.assert_called_with(
                mock_db,
                "fw-123",
                mock_user.organization_id
            )
    
    @pytest.mark.asyncio
    async def test_get_framework_requirements(self, mock_db, mock_user):
        """Test getting framework requirements"""
        # Arrange
        with patch('api.routers.frameworks.get_framework_service') as mock_service:
            mock_service.return_value.get_requirements = AsyncMock(
                return_value=[
                    {
                        "id": "req-1",
                        "code": "A.5.1.1",
                        "description": "Information security policy",
                        "category": "Organizational"
                    },
                    {
                        "id": "req-2",
                        "code": "A.5.1.2",
                        "description": "Review of the information security policy",
                        "category": "Organizational"
                    }
                ]
            )
            
            # Act
            response = await frameworks.get_framework_requirements(
                framework_id="fw-123",
                db=mock_db,
                current_user=mock_user,
                category=None
            )
            
            # Assert
            assert len(response) == 2
            assert response[0]["code"] == "A.5.1.1"
    
    @pytest.mark.asyncio
    async def test_get_framework_controls(self, mock_db, mock_user):
        """Test getting framework controls"""
        # Arrange
        with patch('api.routers.frameworks.get_framework_service') as mock_service:
            mock_service.return_value.get_controls = AsyncMock(
                return_value=[
                    {
                        "id": "ctrl-1",
                        "name": "Access Control",
                        "description": "Limit access to authorized users",
                        "implementation_guidance": "Use RBAC",
                        "testing_procedure": "Review access logs"
                    }
                ]
            )
            
            # Act
            response = await frameworks.get_framework_controls(
                framework_id="fw-123",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert len(response) == 1
            assert response[0]["name"] == "Access Control"
    
    @pytest.mark.asyncio
    async def test_map_frameworks_success(self, mock_db, mock_user):
        """Test framework mapping functionality"""
        # Arrange
        with patch('api.routers.frameworks.get_framework_service') as mock_service:
            mock_service.return_value.map_frameworks = AsyncMock(
                return_value={
                    "mappings": [
                        {
                            "source_requirement": "ISO-A.5.1.1",
                            "target_requirement": "NIST-AC-1",
                            "similarity_score": 0.95
                        }
                    ],
                    "coverage": 0.85
                }
            )
            
            # Act
            response = await frameworks.map_frameworks(
                source_framework_id="fw-123",
                target_framework_id="fw-456",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert "mappings" in response
            assert response["coverage"] == 0.85
    
    @pytest.mark.asyncio
    async def test_import_framework_success(self, mock_db, mock_user):
        """Test framework import from file"""
        # Arrange
        import_data = {
            "format": "json",
            "content": json.dumps({
                "name": "Custom Framework",
                "requirements": [{"code": "CF-1", "description": "Custom requirement"}]
            })
        }
        
        with patch('api.routers.frameworks.get_framework_service') as mock_service:
            mock_service.return_value.import_framework = AsyncMock(
                return_value={
                    "id": "imported-fw",
                    "name": "Custom Framework",
                    "requirements_count": 1
                }
            )
            
            # Act
            response = await frameworks.import_framework(
                import_data=import_data,
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["name"] == "Custom Framework"
            assert response["requirements_count"] == 1
    
    @pytest.mark.asyncio
    async def test_export_framework_success(self, mock_db, mock_user):
        """Test framework export to file"""
        # Arrange
        with patch('api.routers.frameworks.get_framework_service') as mock_service:
            mock_service.return_value.export_framework = AsyncMock(
                return_value={
                    "format": "json",
                    "content": '{"name": "ISO 27001", "requirements": []}'
                }
            )
            
            # Act
            response = await frameworks.export_framework(
                framework_id="fw-123",
                format="json",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["format"] == "json"
            assert "ISO 27001" in response["content"]
    
    @pytest.mark.asyncio
    async def test_get_framework_statistics(self, mock_db, mock_user):
        """Test getting framework statistics"""
        # Arrange
        with patch('api.routers.frameworks.get_framework_service') as mock_service:
            mock_service.return_value.get_statistics = AsyncMock(
                return_value={
                    "total_frameworks": 5,
                    "total_requirements": 250,
                    "total_controls": 150,
                    "coverage_by_category": {
                        "Security": 0.9,
                        "Privacy": 0.85,
                        "Compliance": 0.8
                    }
                }
            )
            
            # Act
            response = await frameworks.get_framework_statistics(
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["total_frameworks"] == 5
            assert response["coverage_by_category"]["Security"] == 0.9