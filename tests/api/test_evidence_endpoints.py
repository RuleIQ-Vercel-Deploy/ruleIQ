"""
Test suite for Evidence API endpoints
P3 Task: Test Coverage Enhancement - Day 2
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import io

from api.routers import evidence
from api.schemas.models import (
    EvidenceResponse as Evidence,
    EvidenceCreate,
    EvidenceUpdate,
    EvidenceResponse,
    EvidenceListResponse,
    EvidenceStatusUpdate as EvidenceValidation
)
from database import User


class TestEvidenceEndpoints:
    """Test suite for evidence management endpoints"""
    
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
    def sample_evidence(self):
        """Sample evidence for testing"""
        return Evidence(
            id="evidence-123",
            name="Security Audit Report 2024",
            description="Annual security audit findings",
            type="document",
            category="audit",
            file_path="uploads/evidence/audit-2024.pdf",
            file_size=1024000,
            mime_type="application/pdf",
            assessment_id="assessment-456",
            requirement_id="req-789",
            organization_id="org-123",
            uploaded_by="test-user-123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            validated=False
        )
    
    @pytest.fixture
    def evidence_create_data(self):
        """Evidence creation data"""
        return EvidenceCreate(
            name="Penetration Test Results",
            description="Q4 2024 penetration testing results",
            type="report",
            category="security",
            assessment_id="assessment-789",
            requirement_id="req-sec-001",
            tags=["security", "pentest", "q4-2024"]
        )
    
    @pytest.fixture
    def mock_upload_file(self):
        """Mock file upload"""
        file_content = b"Test file content"
        file = MagicMock(spec=UploadFile)
        file.filename = "test_document.pdf"
        file.content_type = "application/pdf"
        file.size = len(file_content)
        file.read = AsyncMock(return_value=file_content)
        file.seek = AsyncMock()
        return file
    
    @pytest.mark.asyncio
    async def test_list_evidence_success(self, mock_db, mock_user):
        """Test successful evidence listing"""
        # Arrange
        with patch('api.routers.evidence.get_evidence_service') as mock_service:
            mock_service.return_value.list_evidence = AsyncMock(
                return_value={
                    "evidence": [
                        {
                            "id": "ev-1",
                            "name": "Audit Report",
                            "type": "document",
                            "validated": True
                        },
                        {
                            "id": "ev-2",
                            "name": "Test Results",
                            "type": "report",
                            "validated": False
                        }
                    ],
                    "total": 2
                }
            )
            
            # Act
            response = await evidence.list_evidence(
                db=mock_db,
                current_user=mock_user,
                skip=0,
                limit=10,
                assessment_id=None,
                type=None,
                validated=None
            )
            
            # Assert
            assert len(response["evidence"]) == 2
            assert response["total"] == 2
    
    @pytest.mark.asyncio
    async def test_list_evidence_with_filters(self, mock_db, mock_user):
        """Test evidence listing with filters"""
        # Arrange
        with patch('api.routers.evidence.get_evidence_service') as mock_service:
            mock_service.return_value.list_evidence = AsyncMock(
                return_value={
                    "evidence": [{"id": "ev-1", "validated": True}],
                    "total": 1
                }
            )
            
            # Act
            response = await evidence.list_evidence(
                db=mock_db,
                current_user=mock_user,
                skip=0,
                limit=10,
                assessment_id="assessment-456",
                type="document",
                validated=True
            )
            
            # Assert
            assert len(response["evidence"]) == 1
            assert response["evidence"][0]["validated"] is True
    
    @pytest.mark.asyncio
    async def test_get_evidence_by_id_success(self, mock_db, mock_user, sample_evidence):
        """Test successful evidence retrieval by ID"""
        # Arrange
        with patch('api.routers.evidence.get_evidence_service') as mock_service:
            mock_service.return_value.get_evidence = AsyncMock(
                return_value=sample_evidence.dict()
            )
            
            # Act
            response = await evidence.get_evidence(
                evidence_id="evidence-123",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["id"] == "evidence-123"
            assert response["name"] == "Security Audit Report 2024"
    
    @pytest.mark.asyncio
    async def test_upload_evidence_success(self, mock_db, mock_user, mock_upload_file, evidence_create_data):
        """Test successful evidence upload"""
        # Arrange
        with patch('api.routers.evidence.get_evidence_service') as mock_service:
            created_evidence = {
                "id": "new-evidence-123",
                **evidence_create_data.dict(),
                "file_path": "uploads/evidence/new-file.pdf",
                "file_size": 1024,
                "mime_type": "application/pdf",
                "created_at": datetime.now(UTC).isoformat()
            }
            mock_service.return_value.upload_evidence = AsyncMock(
                return_value=created_evidence
            )
            
            # Act
            response = await evidence.upload_evidence(
                file=mock_upload_file,
                evidence_data=evidence_create_data,
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["id"] == "new-evidence-123"
            assert response["file_path"] == "uploads/evidence/new-file.pdf"
    
    @pytest.mark.asyncio
    async def test_upload_evidence_invalid_file_type(self, mock_db, mock_user, evidence_create_data):
        """Test evidence upload with invalid file type"""
        # Arrange
        invalid_file = MagicMock(spec=UploadFile)
        invalid_file.filename = "malicious.exe"
        invalid_file.content_type = "application/x-executable"
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await evidence.upload_evidence(
                file=invalid_file,
                evidence_data=evidence_create_data,
                db=mock_db,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == 400
        assert "Invalid file type" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_upload_evidence_file_too_large(self, mock_db, mock_user, evidence_create_data):
        """Test evidence upload with file exceeding size limit"""
        # Arrange
        large_file = MagicMock(spec=UploadFile)
        large_file.filename = "large_file.pdf"
        large_file.content_type = "application/pdf"
        large_file.size = 100 * 1024 * 1024  # 100MB
        
        with patch('api.routers.evidence.MAX_FILE_SIZE', 10 * 1024 * 1024):  # 10MB limit
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await evidence.upload_evidence(
                    file=large_file,
                    evidence_data=evidence_create_data,
                    db=mock_db,
                    current_user=mock_user
                )
            
            assert exc_info.value.status_code == 413
    
    @pytest.mark.asyncio
    async def test_update_evidence_metadata(self, mock_db, mock_user):
        """Test updating evidence metadata"""
        # Arrange
        update_data = EvidenceUpdate(
            description="Updated description",
            tags=["updated", "tags"],
            requirement_id="req-new-001"
        )
        
        with patch('api.routers.evidence.get_evidence_service') as mock_service:
            updated_evidence = {
                "id": "evidence-123",
                "description": "Updated description",
                "tags": ["updated", "tags"],
                "updated_at": datetime.now(UTC).isoformat()
            }
            mock_service.return_value.update_evidence = AsyncMock(
                return_value=updated_evidence
            )
            
            # Act
            response = await evidence.update_evidence(
                evidence_id="evidence-123",
                evidence_update=update_data,
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["description"] == "Updated description"
            assert "updated" in response["tags"]
    
    @pytest.mark.asyncio
    async def test_validate_evidence_success(self, mock_db, mock_user):
        """Test evidence validation"""
        # Arrange
        validation_data = EvidenceValidation(
            validated=True,
            validation_notes="Evidence verified and compliant",
            validator_id=mock_user.id
        )
        
        with patch('api.routers.evidence.get_evidence_service') as mock_service:
            mock_service.return_value.validate_evidence = AsyncMock(
                return_value={
                    "id": "evidence-123",
                    "validated": True,
                    "validated_at": datetime.now(UTC).isoformat(),
                    "validated_by": mock_user.id
                }
            )
            
            # Act
            response = await evidence.validate_evidence(
                evidence_id="evidence-123",
                validation=validation_data,
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["validated"] is True
            assert response["validated_by"] == mock_user.id
    
    @pytest.mark.asyncio
    async def test_delete_evidence_success(self, mock_db, mock_user):
        """Test evidence deletion"""
        # Arrange
        with patch('api.routers.evidence.get_evidence_service') as mock_service:
            mock_service.return_value.delete_evidence = AsyncMock(return_value=True)
            
            # Act
            response = await evidence.delete_evidence(
                evidence_id="evidence-123",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response == {"message": "Evidence deleted successfully"}
    
    @pytest.mark.asyncio
    async def test_download_evidence_success(self, mock_db, mock_user):
        """Test evidence file download"""
        # Arrange
        with patch('api.routers.evidence.get_evidence_service') as mock_service:
            mock_service.return_value.get_evidence_file = AsyncMock(
                return_value={
                    "file_path": "/uploads/evidence/document.pdf",
                    "filename": "document.pdf",
                    "mime_type": "application/pdf"
                }
            )
            
            with patch('api.routers.evidence.FileResponse') as mock_file_response:
                # Act
                response = await evidence.download_evidence(
                    evidence_id="evidence-123",
                    db=mock_db,
                    current_user=mock_user
                )
                
                # Assert
                mock_file_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_bulk_upload_evidence(self, mock_db, mock_user, mock_upload_file):
        """Test bulk evidence upload"""
        # Arrange
        files = [mock_upload_file, mock_upload_file]
        
        with patch('api.routers.evidence.get_evidence_service') as mock_service:
            mock_service.return_value.bulk_upload = AsyncMock(
                return_value={
                    "uploaded": 2,
                    "failed": 0,
                    "evidence_ids": ["ev-1", "ev-2"]
                }
            )
            
            # Act
            response = await evidence.bulk_upload_evidence(
                files=files,
                assessment_id="assessment-456",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["uploaded"] == 2
            assert response["failed"] == 0
            assert len(response["evidence_ids"]) == 2
    
    @pytest.mark.asyncio
    async def test_link_evidence_to_requirement(self, mock_db, mock_user):
        """Test linking evidence to requirement"""
        # Arrange
        with patch('api.routers.evidence.get_evidence_service') as mock_service:
            mock_service.return_value.link_to_requirement = AsyncMock(
                return_value={
                    "evidence_id": "evidence-123",
                    "requirement_id": "req-456",
                    "linked": True
                }
            )
            
            # Act
            response = await evidence.link_to_requirement(
                evidence_id="evidence-123",
                requirement_id="req-456",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["linked"] is True
    
    @pytest.mark.asyncio
    async def test_get_evidence_by_assessment(self, mock_db, mock_user):
        """Test getting all evidence for an assessment"""
        # Arrange
        with patch('api.routers.evidence.get_evidence_service') as mock_service:
            mock_service.return_value.get_assessment_evidence = AsyncMock(
                return_value=[
                    {"id": "ev-1", "name": "Evidence 1", "validated": True},
                    {"id": "ev-2", "name": "Evidence 2", "validated": False}
                ]
            )
            
            # Act
            response = await evidence.get_assessment_evidence(
                assessment_id="assessment-456",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert len(response) == 2
            assert response[0]["validated"] is True
    
    @pytest.mark.asyncio
    async def test_search_evidence(self, mock_db, mock_user):
        """Test evidence search functionality"""
        # Arrange
        with patch('api.routers.evidence.get_evidence_service') as mock_service:
            mock_service.return_value.search_evidence = AsyncMock(
                return_value={
                    "results": [
                        {
                            "id": "ev-1",
                            "name": "Security Audit",
                            "relevance_score": 0.9
                        }
                    ],
                    "total": 1
                }
            )
            
            # Act
            response = await evidence.search_evidence(
                query="security audit",
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert len(response["results"]) == 1
            assert response["results"][0]["relevance_score"] == 0.9
    
    @pytest.mark.asyncio
    async def test_evidence_expiry_check(self, mock_db, mock_user):
        """Test checking for expired evidence"""
        # Arrange
        with patch('api.routers.evidence.get_evidence_service') as mock_service:
            mock_service.return_value.check_expiry = AsyncMock(
                return_value={
                    "expired": [
                        {"id": "ev-1", "name": "Old Certificate", "expired_days": 30}
                    ],
                    "expiring_soon": [
                        {"id": "ev-2", "name": "License", "days_until_expiry": 7}
                    ]
                }
            )
            
            # Act
            response = await evidence.check_evidence_expiry(
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert len(response["expired"]) == 1
            assert len(response["expiring_soon"]) == 1