"""
Comprehensive tests for user repository.
QA Specialist - Day 4 Coverage Enhancement
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import bcrypt

from database.user import User


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def sample_user():
    """Create a sample user object."""
    user = User()
    user.id = uuid4()
    user.email = "test@example.com"
    user.hashed_password = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode()
    user.full_name = "Test User"
    user.is_active = True
    user.is_verified = True
    user.created_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    user.company_name = "Test Company"
    user.role = "user"
    return user


@pytest.fixture
def user_repository():
    """Create user repository instance."""
    return UserRepository()


class TestUserRepository:
    """Test cases for user repository."""

    @pytest.mark.asyncio
    async def test_create_user_success(
        self, mock_db_session, user_repository
    ):
        """Test successful user creation."""
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User",
            "company_name": "New Company"
        }
        
        with patch.object(user_repository, 'get_by_email', 
                         return_value=None):  # User doesn't exist
            
            result = await user_repository.create(
                mock_db_session,
                user_data
            )
            
            assert result is not None
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()
            mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(
        self, mock_db_session, user_repository, sample_user
    ):
        """Test creating user with duplicate email."""
        user_data = {
            "email": sample_user.email,
            "password": "Password123!",
            "full_name": "Duplicate User"
        }
        
        mock_db_session.add.side_effect = IntegrityError("", "", "")
        
        with pytest.raises(IntegrityError):
            await user_repository.create(
                mock_db_session,
                user_data
            )
        
        mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(
        self, mock_db_session, user_repository, sample_user
    ):
        """Test retrieving user by ID."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_user)
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.get_by_id(
            mock_db_session,
            sample_user.id
        )
        
        assert result == sample_user
        assert result.email == sample_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(
        self, mock_db_session, user_repository
    ):
        """Test retrieving non-existent user by ID."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.get_by_id(
            mock_db_session,
            uuid4()
        )
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(
        self, mock_db_session, user_repository, sample_user
    ):
        """Test retrieving user by email."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_user)
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.get_by_email(
            mock_db_session,
            sample_user.email
        )
        
        assert result == sample_user
        assert result.id == sample_user.id

    @pytest.mark.asyncio
    async def test_get_user_by_email_case_insensitive(
        self, mock_db_session, user_repository, sample_user
    ):
        """Test email lookup is case-insensitive."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_user)
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.get_by_email(
            mock_db_session,
            sample_user.email.upper()  # Test with uppercase
        )
        
        assert result == sample_user

    @pytest.mark.asyncio
    async def test_update_user_success(
        self, mock_db_session, user_repository, sample_user
    ):
        """Test updating user information."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_user)
        mock_db_session.execute.return_value = mock_result
        
        update_data = {
            "full_name": "Updated Name",
            "company_name": "Updated Company"
        }
        
        result = await user_repository.update(
            mock_db_session,
            sample_user.id,
            update_data
        )
        
        assert result is not None
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_password(
        self, mock_db_session, user_repository, sample_user
    ):
        """Test updating user password."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_user)
        mock_db_session.execute.return_value = mock_result
        
        new_password = "NewSecurePass123!"
        
        result = await user_repository.update_password(
            mock_db_session,
            sample_user.id,
            new_password
        )
        
        assert result is True
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_success(
        self, mock_db_session, user_repository, sample_user
    ):
        """Test deleting user."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_user)
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.delete(
            mock_db_session,
            sample_user.id
        )
        
        assert result is True
        mock_db_session.delete.assert_called_once_with(sample_user)
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_not_found(
        self, mock_db_session, user_repository
    ):
        """Test deleting non-existent user."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.delete(
            mock_db_session,
            uuid4()
        )
        
        assert result is False
        mock_db_session.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_verify_user_email(
        self, mock_db_session, user_repository, sample_user
    ):
        """Test verifying user email."""
        mock_result = MagicMock()
        sample_user.is_verified = False
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_user)
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.verify_email(
            mock_db_session,
            sample_user.id
        )
        
        assert result is True
        assert sample_user.is_verified is True
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_users_with_pagination(
        self, mock_db_session, user_repository
    ):
        """Test listing users with pagination."""
        users = [MagicMock(spec=User) for _ in range(5)]
        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=users)))
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.list_users(
            mock_db_session,
            limit=10,
            offset=0
        )
        
        assert len(result) == 5
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_users_with_filter(
        self, mock_db_session, user_repository
    ):
        """Test listing users with filters."""
        active_users = [
            MagicMock(spec=User, is_active=True) for _ in range(3)
        ]
        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=active_users)))
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.list_users(
            mock_db_session,
            is_active=True,
            limit=10,
            offset=0
        )
        
        assert len(result) == 3
        assert all(u.is_active for u in result)

    @pytest.mark.asyncio
    async def test_authenticate_user_success(
        self, mock_db_session, user_repository, sample_user
    ):
        """Test successful user authentication."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_user)
        mock_db_session.execute.return_value = mock_result
        
        # Use the correct password
        result = await user_repository.authenticate(
            mock_db_session,
            sample_user.email,
            "password123"  # This should match what was hashed in sample_user
        )
        
        assert result == sample_user

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(
        self, mock_db_session, user_repository, sample_user
    ):
        """Test authentication with wrong password."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_user)
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.authenticate(
            mock_db_session,
            sample_user.email,
            "wrong_password"
        )
        
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(
        self, mock_db_session, user_repository, sample_user
    ):
        """Test authentication of inactive user."""
        sample_user.is_active = False
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_user)
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.authenticate(
            mock_db_session,
            sample_user.email,
            "password123"
        )
        
        assert result is None

    @pytest.mark.asyncio
    async def test_update_last_login(
        self, mock_db_session, user_repository, sample_user
    ):
        """Test updating user's last login timestamp."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_user)
        mock_db_session.execute.return_value = mock_result
        
        old_login = sample_user.last_login
        
        result = await user_repository.update_last_login(
            mock_db_session,
            sample_user.id
        )
        
        assert result is True
        assert sample_user.last_login is not None
        assert sample_user.last_login != old_login
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_users_by_name(
        self, mock_db_session, user_repository
    ):
        """Test searching users by name."""
        search_results = [
            MagicMock(spec=User, full_name="John Doe"),
            MagicMock(spec=User, full_name="John Smith")
        ]
        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=search_results)))
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.search_by_name(
            mock_db_session,
            "John"
        )
        
        assert len(result) == 2
        assert all("John" in u.full_name for u in result)

    @pytest.mark.asyncio
    async def test_count_users(
        self, mock_db_session, user_repository
    ):
        """Test counting total users."""
        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=42)
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.count_users(mock_db_session)
        
        assert result == 42

    @pytest.mark.asyncio
    async def test_bulk_create_users(
        self, mock_db_session, user_repository
    ):
        """Test bulk user creation."""
        users_data = [
            {"email": f"user{i}@example.com", "password": f"Pass{i}!", "full_name": f"User {i}"}
            for i in range(5)
        ]
        
        result = await user_repository.bulk_create(
            mock_db_session,
            users_data
        )
        
        assert result == 5
        assert mock_db_session.add.call_count == 5
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_database_error_handling(
        self, mock_db_session, user_repository
    ):
        """Test handling of database errors."""
        mock_db_session.execute.side_effect = SQLAlchemyError("Database connection lost")
        
        with pytest.raises(SQLAlchemyError) as exc_info:
            await user_repository.get_by_id(mock_db_session, uuid4())
        
        assert "Database connection lost" in str(exc_info.value)
        mock_db_session.rollback.assert_called()