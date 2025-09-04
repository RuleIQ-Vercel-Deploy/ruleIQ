"""
Comprehensive tests for the integrations API router.
QA Specialist - Day 4 Coverage Enhancement
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import json

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
def sample_integration():
    """Create a sample integration."""
    return {
        "id": str(uuid4()),
        "name": "Slack Integration",
        "type": "slack",
        "status": "connected",
        "configuration": {
            "webhook_url": "https://hooks.slack.com/services/XXX",
            "channel": "#compliance",
            "notifications_enabled": True
        },
        "created_at": datetime.utcnow().isoformat(),
        "last_sync": datetime.utcnow().isoformat(),
        "metadata": {
            "messages_sent": 150,
            "last_error": None
        }
    }


@pytest.fixture
def integration_request():
    """Create an integration setup request."""
    return {
        "type": "slack",
        "name": "Slack Notifications",
        "configuration": {
            "webhook_url": "https://hooks.slack.com/services/XXX",
            "channel": "#compliance"
        }
    }


class TestIntegrationsRouter:
    """Test cases for integrations API endpoints."""

    @pytest.mark.asyncio
    async def test_list_integrations_success(
        self, mock_user, mock_db_session
    ):
        """Test listing all user integrations."""
        from api.routers.integrations import list_integrations
        
        integrations = [
            {
                "id": str(uuid4()),
                "name": "Slack",
                "type": "slack",
                "status": "connected"
            },
            {
                "id": str(uuid4()),
                "name": "Google Workspace",
                "type": "google",
                "status": "connected"
            },
            {
                "id": str(uuid4()),
                "name": "Microsoft 365",
                "type": "microsoft",
                "status": "pending"
            }
        ]
        
        with patch('api.routers.integrations.get_user_integrations', 
                   new_callable=AsyncMock) as mock_list:
            mock_list.return_value = integrations
            
            result = await list_integrations(
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert len(result["integrations"]) == 3
            assert result["integrations"][0]["type"] == "slack"

    @pytest.mark.asyncio
    async def test_get_integration_by_id_success(
        self, mock_user, mock_db_session, sample_integration
    ):
        """Test retrieving a specific integration."""
        from api.routers.integrations import get_integration
        
        integration_id = uuid4()
        
        with patch('api.routers.integrations.get_integration_by_id', 
                   new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_integration
            
            result = await get_integration(
                integration_id=integration_id,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == sample_integration
            assert result["type"] == "slack"

    @pytest.mark.asyncio
    async def test_create_integration_success(
        self, mock_user, mock_db_session, integration_request, sample_integration
    ):
        """Test creating a new integration."""
        from api.routers.integrations import create_integration
        
        with patch('api.routers.integrations.setup_integration', 
                   new_callable=AsyncMock) as mock_create:
            mock_create.return_value = sample_integration
            
            result = await create_integration(
                request=integration_request,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == sample_integration
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_integration_duplicate(
        self, mock_user, mock_db_session, integration_request
    ):
        """Test creating duplicate integration."""
        from api.routers.integrations import create_integration
        
        with patch('api.routers.integrations.setup_integration', 
                   new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = ValueError("Integration already exists")
            
            with pytest.raises(ValueError) as exc_info:
                await create_integration(
                    request=integration_request,
                    current_user=mock_user,
                    db=mock_db_session
                )
            
            assert "Integration already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_integration_success(
        self, mock_user, mock_db_session, sample_integration
    ):
        """Test updating integration configuration."""
        from api.routers.integrations import update_integration
        
        integration_id = uuid4()
        update_data = {
            "configuration": {
                "channel": "#alerts",
                "notifications_enabled": False
            }
        }
        
        updated_integration = {
            **sample_integration,
            "configuration": {
                **sample_integration["configuration"],
                **update_data["configuration"]
            }
        }
        
        with patch('api.routers.integrations.update_integration_config', 
                   new_callable=AsyncMock) as mock_update:
            mock_update.return_value = updated_integration
            
            result = await update_integration(
                integration_id=integration_id,
                update_data=update_data,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result["configuration"]["channel"] == "#alerts"
            assert result["configuration"]["notifications_enabled"] is False

    @pytest.mark.asyncio
    async def test_delete_integration_success(
        self, mock_user, mock_db_session
    ):
        """Test deleting an integration."""
        from api.routers.integrations import delete_integration
        
        integration_id = uuid4()
        
        with patch('api.routers.integrations.remove_integration', 
                   new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = True
            
            result = await delete_integration(
                integration_id=integration_id,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == {"message": "Integration deleted successfully"}

    @pytest.mark.asyncio
    async def test_test_integration_connection_success(
        self, mock_user, mock_db_session
    ):
        """Test testing integration connection."""
        from api.routers.integrations import test_integration
        
        integration_id = uuid4()
        test_result = {
            "status": "success",
            "message": "Connection successful",
            "latency_ms": 150,
            "tested_at": datetime.utcnow().isoformat()
        }
        
        with patch('api.routers.integrations.test_connection', 
                   new_callable=AsyncMock) as mock_test:
            mock_test.return_value = test_result
            
            result = await test_integration(
                integration_id=integration_id,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result["status"] == "success"
            assert result["latency_ms"] == 150

    @pytest.mark.asyncio
    async def test_test_integration_connection_failure(
        self, mock_user, mock_db_session
    ):
        """Test failed integration connection test."""
        from api.routers.integrations import test_integration
        
        integration_id = uuid4()
        test_result = {
            "status": "failed",
            "message": "Connection timeout",
            "error": "Unable to reach endpoint",
            "tested_at": datetime.utcnow().isoformat()
        }
        
        with patch('api.routers.integrations.test_connection', 
                   new_callable=AsyncMock) as mock_test:
            mock_test.return_value = test_result
            
            result = await test_integration(
                integration_id=integration_id,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result["status"] == "failed"
            assert "error" in result

    @pytest.mark.asyncio
    async def test_sync_integration_data_success(
        self, mock_user, mock_db_session
    ):
        """Test syncing integration data."""
        from api.routers.integrations import sync_integration
        
        integration_id = uuid4()
        sync_result = {
            "status": "completed",
            "records_synced": 250,
            "duration_seconds": 5.2,
            "next_sync": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        with patch('api.routers.integrations.sync_data', 
                   new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = sync_result
            
            result = await sync_integration(
                integration_id=integration_id,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result["records_synced"] == 250
            assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_integration_logs_success(
        self, mock_user, mock_db_session
    ):
        """Test retrieving integration activity logs."""
        from api.routers.integrations import get_integration_logs
        
        integration_id = uuid4()
        logs = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "info",
                "message": "Sync completed successfully",
                "details": {"records": 100}
            },
            {
                "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "level": "warning",
                "message": "Rate limit approaching",
                "details": {"remaining": 10}
            }
        ]
        
        with patch('api.routers.integrations.get_activity_logs', 
                   new_callable=AsyncMock) as mock_logs:
            mock_logs.return_value = logs
            
            result = await get_integration_logs(
                integration_id=integration_id,
                current_user=mock_user,
                db=mock_db_session,
                limit=10
            )
            
            assert len(result["logs"]) == 2
            assert result["logs"][0]["level"] == "info"

    @pytest.mark.asyncio
    async def test_oauth_callback_success(
        self, mock_user, mock_db_session
    ):
        """Test OAuth callback handling."""
        from api.routers.integrations import oauth_callback
        
        provider = "google"
        code = "auth_code_123"
        state = "state_token_xyz"
        
        oauth_result = {
            "integration_id": str(uuid4()),
            "status": "connected",
            "provider": provider,
            "user_info": {
                "email": "user@gmail.com",
                "name": "Test User"
            }
        }
        
        with patch('api.routers.integrations.complete_oauth', 
                   new_callable=AsyncMock) as mock_oauth:
            mock_oauth.return_value = oauth_result
            
            result = await oauth_callback(
                provider=provider,
                code=code,
                state=state,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result["status"] == "connected"
            assert result["provider"] == "google"

    @pytest.mark.asyncio
    async def test_refresh_integration_token_success(
        self, mock_user, mock_db_session
    ):
        """Test refreshing integration OAuth token."""
        from api.routers.integrations import refresh_token
        
        integration_id = uuid4()
        refresh_result = {
            "status": "success",
            "token_refreshed": True,
            "expires_in": 3600,
            "refreshed_at": datetime.utcnow().isoformat()
        }
        
        with patch('api.routers.integrations.refresh_oauth_token', 
                   new_callable=AsyncMock) as mock_refresh:
            mock_refresh.return_value = refresh_result
            
            result = await refresh_token(
                integration_id=integration_id,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result["token_refreshed"] is True
            assert result["expires_in"] == 3600

    @pytest.mark.asyncio
    async def test_get_available_integrations(
        self, mock_user, mock_db_session
    ):
        """Test getting list of available integration types."""
        from api.routers.integrations import get_available_integrations
        
        available = [
            {
                "type": "slack",
                "name": "Slack",
                "description": "Team communication and notifications",
                "features": ["notifications", "alerts", "reports"],
                "auth_type": "webhook"
            },
            {
                "type": "google",
                "name": "Google Workspace",
                "description": "Google services integration",
                "features": ["drive", "calendar", "gmail"],
                "auth_type": "oauth2"
            },
            {
                "type": "microsoft",
                "name": "Microsoft 365",
                "description": "Microsoft services integration",
                "features": ["teams", "outlook", "sharepoint"],
                "auth_type": "oauth2"
            }
        ]
        
        with patch('api.routers.integrations.list_available', 
                   new_callable=AsyncMock) as mock_available:
            mock_available.return_value = available
            
            result = await get_available_integrations(
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert len(result["integrations"]) == 3
            assert any(i["type"] == "slack" for i in result["integrations"])

    @pytest.mark.asyncio
    async def test_get_integration_webhooks(
        self, mock_user, mock_db_session
    ):
        """Test retrieving integration webhooks."""
        from api.routers.integrations import get_webhooks
        
        integration_id = uuid4()
        webhooks = [
            {
                "id": str(uuid4()),
                "url": "https://example.com/webhook1",
                "events": ["report.generated", "policy.updated"],
                "active": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid4()),
                "url": "https://example.com/webhook2",
                "events": ["assessment.completed"],
                "active": False,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        with patch('api.routers.integrations.get_integration_webhooks', 
                   new_callable=AsyncMock) as mock_webhooks:
            mock_webhooks.return_value = webhooks
            
            result = await get_webhooks(
                integration_id=integration_id,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert len(result["webhooks"]) == 2
            assert result["webhooks"][0]["active"] is True

    @pytest.mark.asyncio
    async def test_create_webhook_success(
        self, mock_user, mock_db_session
    ):
        """Test creating a new webhook for integration."""
        from api.routers.integrations import create_webhook
        
        integration_id = uuid4()
        webhook_request = {
            "url": "https://example.com/new-webhook",
            "events": ["report.generated", "assessment.completed"],
            "secret": "webhook_secret_123"
        }
        
        created_webhook = {
            "id": str(uuid4()),
            **webhook_request,
            "active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        with patch('api.routers.integrations.add_webhook', 
                   new_callable=AsyncMock) as mock_create:
            mock_create.return_value = created_webhook
            
            result = await create_webhook(
                integration_id=integration_id,
                request=webhook_request,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result["url"] == webhook_request["url"]
            assert len(result["events"]) == 2