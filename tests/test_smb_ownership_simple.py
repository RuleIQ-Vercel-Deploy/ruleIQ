"""
Simple test to verify SMB ownership logic without database.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from fastapi import HTTPException
from services.data_access import DataAccess
from database.user import User

class TestDataAccessOwnership:
    """Test the DataAccess ownership utilities."""
    
    def test_ensure_owner_success(self):
        """Test that owner can access their own resource."""
        # Create mock objects
        user_id = uuid4()
        resource_id = uuid4()
        
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        
        mock_resource = Mock()
        mock_resource.id = resource_id
        mock_resource.user_id = user_id  # Same user owns resource
        
        # Mock model class with id attribute
        mock_model = Mock()
        mock_model.id = Mock()
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_resource
        
        # Should not raise exception
        result = DataAccess.ensure_owner(
            mock_db, mock_model, resource_id, mock_user, "test resource"
        )
        
        assert result == mock_resource
    
    def test_ensure_owner_forbidden(self):
        """Test that non-owner is rejected."""
        # Create mock objects with different user IDs
        owner_id = uuid4()
        other_user_id = uuid4()
        resource_id = uuid4()
        
        mock_user = Mock(spec=User)
        mock_user.id = other_user_id  # Different user
        
        mock_resource = Mock()
        mock_resource.id = resource_id
        mock_resource.user_id = owner_id  # Different owner
        
        # Mock model class with id attribute
        mock_model = Mock()
        mock_model.id = Mock()
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_resource
        
        # Should raise 403 Forbidden
        with pytest.raises(HTTPException) as exc_info:
            DataAccess.ensure_owner(
                mock_db, mock_model, resource_id, mock_user, "test resource"
            )
        
        assert exc_info.value.status_code == 403
        assert "don't have access" in exc_info.value.detail
    
    def test_ensure_owner_not_found(self):
        """Test that missing resource raises 404."""
        user_id = uuid4()
        resource_id = uuid4()
        
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        
        # Mock model class with id attribute
        mock_model = Mock()
        mock_model.id = Mock()
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None  # Not found
        
        # Should raise 404 Not Found
        with pytest.raises(HTTPException) as exc_info:
            DataAccess.ensure_owner(
                mock_db, mock_model, resource_id, mock_user, "test resource"
            )
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
    
    @pytest.mark.asyncio
    async def test_ensure_owner_async_success(self):
        """Test async version of ensure_owner for valid owner."""
        user_id = uuid4()
        resource_id = uuid4()
        
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        
        mock_resource = Mock()
        mock_resource.id = resource_id
        mock_resource.user_id = user_id  # Same user owns resource
        
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_resource
        
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Patch the select function
        with patch('services.data_access.select') as mock_select:
            mock_stmt = Mock()
            mock_stmt.where.return_value = mock_stmt
            mock_select.return_value = mock_stmt
            
            # Mock model with id attribute
            mock_model = Mock()
            mock_model.id = Mock()
            
            # Should not raise exception
            result = await DataAccess.ensure_owner_async(
                mock_db, mock_model, resource_id, mock_user, "test resource"
            )
            
            assert result == mock_resource
    
    @pytest.mark.asyncio
    async def test_ensure_owner_async_forbidden(self):
        """Test async version rejects non-owner."""
        owner_id = uuid4()
        other_user_id = uuid4()
        resource_id = uuid4()
        
        mock_user = Mock(spec=User)
        mock_user.id = other_user_id  # Different user
        
        mock_resource = Mock()
        mock_resource.id = resource_id
        mock_resource.user_id = owner_id  # Different owner
        
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_resource
        
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Patch the select function
        with patch('services.data_access.select') as mock_select:
            mock_stmt = Mock()
            mock_stmt.where.return_value = mock_stmt
            mock_select.return_value = mock_stmt
            
            # Mock model with id attribute
            mock_model = Mock()
            mock_model.id = Mock()
            
            # Should raise 403 Forbidden
            with pytest.raises(HTTPException) as exc_info:
                await DataAccess.ensure_owner_async(
                    mock_db, mock_model, resource_id, mock_user, "test resource"
                )
            
            assert exc_info.value.status_code == 403
            assert "don't have access" in exc_info.value.detail
    
    def test_list_owned_filters_by_user(self):
        """Test that list_owned only returns user's resources."""
        user_id = uuid4()
        
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        
        # Create mock resources
        owned_resource = Mock()
        owned_resource.user_id = user_id
        owned_resource.name = "Owned Resource"
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = [owned_resource]
        
        mock_db = Mock()
        mock_db.query.return_value = mock_query
        
        mock_model = Mock()
        mock_model.user_id = Mock()  # Has user_id attribute
        
        # Call list_owned
        results = DataAccess.list_owned(mock_db, mock_model, mock_user)
        
        # Verify filter was called with correct user_id
        assert len(results) == 1
        assert results[0] == owned_resource
        
        # Check that filter was called
        mock_query.filter.assert_called_once()
    
    def test_create_owned_sets_user_id(self):
        """Test that create_owned automatically sets user_id."""
        user_id = uuid4()
        
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        
        mock_db = Mock()
        
        # Mock model class
        mock_model = Mock()
        mock_model.return_value = Mock()  # Instance
        mock_model.user_id = Mock()  # Has user_id attribute
        
        # Call create_owned
        data = {"name": "Test Resource", "description": "Test"}
        result = DataAccess.create_owned(mock_db, mock_model, mock_user, **data)
        
        # Verify user_id was set in the data
        mock_model.assert_called_once()
        call_args = mock_model.call_args[1]
        assert call_args["user_id"] == user_id
        assert call_args["name"] == "Test Resource"
        
        # Verify resource was added to database
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()