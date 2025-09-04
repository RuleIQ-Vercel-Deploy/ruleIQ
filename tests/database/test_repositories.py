"""
Test suite for Database Repositories
P3 Task: Test Coverage Enhancement - Day 2
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from uuid import uuid4

# Note: Repository classes not found in current database structure
# from database.base import BaseRepository
# from database.repositories.assessment_repository import AssessmentRepository  
# from database.repositories.policy_repository import PolicyRepository
# Note: Repository classes not found in current database structure
# from database.repositories.evidence_repository import EvidenceRepository
# from database.repositories.framework_repository import FrameworkRepository
# from database.repositories.user_repository import UserRepository
# from database.models import Assessment, Policy, Evidence, Framework, User


class TestBaseRepository:
    """Test suite for BaseRepository functionality"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        mock = AsyncMock(spec=AsyncSession)
        mock.execute = AsyncMock()
        mock.commit = AsyncMock()
        mock.rollback = AsyncMock()
        mock.refresh = AsyncMock()
        return mock
    
    @pytest.fixture
    def base_repository(self, mock_db):
        """Create base repository instance"""
        repo = BaseRepository(model=Assessment)
        repo.db = mock_db
        return repo
    
    @pytest.mark.asyncio
    async def test_create_entity(self, base_repository, mock_db):
        """Test creating a new entity"""
        # Arrange
        entity_data = {
            "name": "Test Assessment",
            "description": "Test Description"
        }
        mock_db.execute.return_value.scalar_one_or_none.return_value = Assessment(**entity_data)
        
        # Act
        result = await base_repository.create(entity_data)
        
        # Assert
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, base_repository, mock_db):
        """Test retrieving entity by ID"""
        # Arrange
        entity_id = str(uuid4())
        mock_entity = Assessment(id=entity_id, name="Test")
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_entity
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await base_repository.get(entity_id)
        
        # Assert
        assert result == mock_entity
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, base_repository, mock_db):
        """Test retrieving all entities with pagination"""
        # Arrange
        mock_entities = [
            Assessment(id=str(uuid4()), name=f"Test {i}")
            for i in range(5)
        ]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_entities
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await base_repository.get_all(skip=0, limit=10)
        
        # Assert
        assert len(result) == 5
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_entity(self, base_repository, mock_db):
        """Test updating an entity"""
        # Arrange
        entity_id = str(uuid4())
        update_data = {"name": "Updated Name"}
        mock_entity = Assessment(id=entity_id, name="Original")
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_entity
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await base_repository.update(entity_id, update_data)
        
        # Assert
        assert result == mock_entity
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_entity(self, base_repository, mock_db):
        """Test deleting an entity"""
        # Arrange
        entity_id = str(uuid4())
        mock_entity = Assessment(id=entity_id)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_entity
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await base_repository.delete(entity_id)
        
        # Assert
        assert result is True
        mock_db.delete.assert_called_once_with(mock_entity)
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_entities(self, base_repository, mock_db):
        """Test counting entities"""
        # Arrange
        mock_result = Mock()
        mock_result.scalar.return_value = 42
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await base_repository.count()
        
        # Assert
        assert result == 42
        mock_db.execute.assert_called_once()


class TestAssessmentRepository:
    """Test suite for AssessmentRepository"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        mock = AsyncMock(spec=AsyncSession)
        mock.execute = AsyncMock()
        mock.commit = AsyncMock()
        return mock
    
    @pytest.fixture
    def assessment_repo(self, mock_db):
        """Create assessment repository instance"""
        repo = AssessmentRepository(mock_db)
        return repo
    
    @pytest.mark.asyncio
    async def test_get_by_organization(self, assessment_repo, mock_db):
        """Test getting assessments by organization"""
        # Arrange
        org_id = "org-123"
        mock_assessments = [
            Assessment(id=str(uuid4()), organization_id=org_id, name=f"Assessment {i}")
            for i in range(3)
        ]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_assessments
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await assessment_repo.get_by_organization(org_id)
        
        # Assert
        assert len(result) == 3
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_status(self, assessment_repo, mock_db):
        """Test getting assessments by status"""
        # Arrange
        status = "in_progress"
        mock_assessments = [
            Assessment(id=str(uuid4()), status=status)
            for _ in range(2)
        ]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_assessments
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await assessment_repo.get_by_status(status)
        
        # Assert
        assert len(result) == 2
        assert all(a.status == status for a in result)
    
    @pytest.mark.asyncio
    async def test_get_with_framework(self, assessment_repo, mock_db):
        """Test getting assessments with framework details"""
        # Arrange
        assessment_id = str(uuid4())
        mock_assessment = Assessment(
            id=assessment_id,
            framework_id="fw-123",
            framework=Framework(id="fw-123", name="ISO 27001")
        )
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_assessment
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await assessment_repo.get_with_framework(assessment_id)
        
        # Assert
        assert result.framework.name == "ISO 27001"
    
    @pytest.mark.asyncio
    async def test_update_progress(self, assessment_repo, mock_db):
        """Test updating assessment progress"""
        # Arrange
        assessment_id = str(uuid4())
        progress = 75.5
        mock_assessment = Assessment(id=assessment_id, progress=0)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_assessment
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await assessment_repo.update_progress(assessment_id, progress)
        
        # Assert
        assert result.progress == progress
        mock_db.commit.assert_called_once()


class TestPolicyRepository:
    """Test suite for PolicyRepository"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        mock = AsyncMock(spec=AsyncSession)
        mock.execute = AsyncMock()
        mock.commit = AsyncMock()
        return mock
    
    @pytest.fixture
    def policy_repo(self, mock_db):
        """Create policy repository instance"""
        repo = PolicyRepository(mock_db)
        return repo
    
    @pytest.mark.asyncio
    async def test_get_approved_policies(self, policy_repo, mock_db):
        """Test getting approved policies"""
        # Arrange
        mock_policies = [
            Policy(id=str(uuid4()), status="approved", name=f"Policy {i}")
            for i in range(3)
        ]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_policies
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await policy_repo.get_approved_policies()
        
        # Assert
        assert len(result) == 3
        assert all(p.status == "approved" for p in result)
    
    @pytest.mark.asyncio
    async def test_get_by_category(self, policy_repo, mock_db):
        """Test getting policies by category"""
        # Arrange
        category = "Security"
        mock_policies = [
            Policy(id=str(uuid4()), category=category)
            for _ in range(2)
        ]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_policies
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await policy_repo.get_by_category(category)
        
        # Assert
        assert len(result) == 2
        assert all(p.category == category for p in result)
    
    @pytest.mark.asyncio
    async def test_search_policies(self, policy_repo, mock_db):
        """Test searching policies by keyword"""
        # Arrange
        keyword = "data protection"
        mock_policies = [
            Policy(id=str(uuid4()), name="Data Protection Policy"),
            Policy(id=str(uuid4()), description="Policy for data protection")
        ]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_policies
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await policy_repo.search(keyword)
        
        # Assert
        assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_clone_policy(self, policy_repo, mock_db):
        """Test cloning a policy"""
        # Arrange
        original_id = str(uuid4())
        original_policy = Policy(
            id=original_id,
            name="Original Policy",
            content="Policy content",
            category="Security"
        )
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = original_policy
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await policy_repo.clone(original_id, "Cloned Policy")
        
        # Assert
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestEvidenceRepository:
    """Test suite for EvidenceRepository"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        mock = AsyncMock(spec=AsyncSession)
        mock.execute = AsyncMock()
        mock.commit = AsyncMock()
        return mock
    
    @pytest.fixture
    def evidence_repo(self, mock_db):
        """Create evidence repository instance"""
        repo = EvidenceRepository(mock_db)
        return repo
    
    @pytest.mark.asyncio
    async def test_get_by_assessment(self, evidence_repo, mock_db):
        """Test getting evidence by assessment"""
        # Arrange
        assessment_id = str(uuid4())
        mock_evidence = [
            Evidence(id=str(uuid4()), assessment_id=assessment_id)
            for _ in range(3)
        ]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_evidence
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await evidence_repo.get_by_assessment(assessment_id)
        
        # Assert
        assert len(result) == 3
        assert all(e.assessment_id == assessment_id for e in result)
    
    @pytest.mark.asyncio
    async def test_get_validated_evidence(self, evidence_repo, mock_db):
        """Test getting validated evidence"""
        # Arrange
        mock_evidence = [
            Evidence(id=str(uuid4()), validated=True)
            for _ in range(2)
        ]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_evidence
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await evidence_repo.get_validated()
        
        # Assert
        assert len(result) == 2
        assert all(e.validated for e in result)
    
    @pytest.mark.asyncio
    async def test_validate_evidence(self, evidence_repo, mock_db):
        """Test validating evidence"""
        # Arrange
        evidence_id = str(uuid4())
        validator_id = "user-123"
        mock_evidence = Evidence(id=evidence_id, validated=False)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_evidence
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await evidence_repo.validate(evidence_id, validator_id, "Validated")
        
        # Assert
        assert result.validated is True
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_expiry(self, evidence_repo, mock_db):
        """Test checking evidence expiry"""
        # Arrange
        expired_evidence = [
            Evidence(
                id=str(uuid4()),
                name="Expired Cert",
                expiry_date=datetime.now(UTC).replace(year=2023)
            )
        ]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = expired_evidence
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await evidence_repo.get_expired()
        
        # Assert
        assert len(result) == 1
        assert result[0].name == "Expired Cert"


class TestUserRepository:
    """Test suite for UserRepository"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        mock = AsyncMock(spec=AsyncSession)
        mock.execute = AsyncMock()
        mock.commit = AsyncMock()
        return mock
    
    @pytest.fixture
    def user_repo(self, mock_db):
        """Create user repository instance"""
        repo = UserRepository(mock_db)
        return repo
    
    @pytest.mark.asyncio
    async def test_get_by_email(self, user_repo, mock_db):
        """Test getting user by email"""
        # Arrange
        email = "test@example.com"
        mock_user = User(id=str(uuid4()), email=email)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await user_repo.get_by_email(email)
        
        # Assert
        assert result.email == email
    
    @pytest.mark.asyncio
    async def test_get_active_users(self, user_repo, mock_db):
        """Test getting active users"""
        # Arrange
        mock_users = [
            User(id=str(uuid4()), is_active=True)
            for _ in range(3)
        ]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_users
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await user_repo.get_active_users()
        
        # Assert
        assert len(result) == 3
        assert all(u.is_active for u in result)
    
    @pytest.mark.asyncio
    async def test_update_last_login(self, user_repo, mock_db):
        """Test updating user last login"""
        # Arrange
        user_id = str(uuid4())
        mock_user = User(id=user_id, last_login=None)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await user_repo.update_last_login(user_id)
        
        # Assert
        assert result.last_login is not None
        mock_db.commit.assert_called_once()