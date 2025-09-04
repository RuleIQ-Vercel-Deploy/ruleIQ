"""Tests for the integration service module."""

import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from uuid import uuid4
import json
from typing import Dict, List, Any
import aiohttp

from services.integration_service import (
    IntegrationService,
    WebhookService, 
    APIConnector,
    DataSyncService,
    EventBus,
    MessageQueue,
    ExternalAPIClient,
    OAuthProvider,
    WebSocketManager,
    IntegrationConfig
)


class TestIntegrationService:
    """Test suite for IntegrationService."""

    @pytest.fixture
    def integration_service(self):
        """Create an integration service instance."""
        return IntegrationService()

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def sample_integration_config(self):
        """Create sample integration configuration."""
        return IntegrationConfig(
            name="Slack Integration",
            type="webhook",
            endpoint="https://hooks.slack.com/services/xxx",
            auth_type="bearer",
            auth_token="xoxb-token",
            headers={"Content-Type": "application/json"},
            active=True
        )

    @pytest.fixture
    def sample_webhook_payload(self):
        """Create sample webhook payload."""
        return {
            "event": "assessment.completed",
            "timestamp": datetime.now(UTC).isoformat(),
            "data": {
                "assessment_id": str(uuid4()),
                "organization_id": str(uuid4()),
                "score": 85.5,
                "status": "completed"
            }
        }

    @pytest.mark.asyncio
    async def test_register_integration(self, integration_service, sample_integration_config, mock_db):
        """Test registering a new integration."""
        # Act
        result = await integration_service.register_integration(
            sample_integration_config, mock_db
        )
        
        # Assert
        assert result.integration_id is not None
        assert result.status == "active"
        assert result.name == "Slack Integration"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_webhook(self, integration_service, sample_webhook_payload):
        """Test sending webhook notification."""
        # Arrange
        webhook_url = "https://example.com/webhook"
        webhook_service = WebhookService()
        
        # Act
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"success": True})
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await webhook_service.send_webhook(
                webhook_url, sample_webhook_payload
            )
        
        # Assert
        assert result.success is True
        assert result.status_code == 200
        mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_webhook_retry_logic(self, integration_service):
        """Test webhook retry logic on failure."""
        # Arrange
        webhook_url = "https://example.com/webhook"
        payload = {"test": "data"}
        webhook_service = WebhookService()
        
        # Act
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await webhook_service.send_with_retry(
                webhook_url, payload, max_retries=3
            )
        
        # Assert
        assert result.success is False
        assert result.retry_count == 3
        assert mock_post.call_count == 3

    @pytest.mark.asyncio
    async def test_api_connector(self, integration_service):
        """Test API connector for external services."""
        # Arrange
        connector = APIConnector(
            base_url="https://api.example.com",
            auth_token="secret_token"
        )
        
        # Act
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"data": "test"})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await connector.get("/resources")
        
        # Assert
        assert result["data"] == "test"
        mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_data_sync_service(self, integration_service, mock_db):
        """Test data synchronization service."""
        # Arrange
        sync_service = DataSyncService()
        source_data = [
            {"id": "1", "name": "Item 1", "updated_at": datetime.now(UTC)},
            {"id": "2", "name": "Item 2", "updated_at": datetime.now(UTC)}
        ]
        
        # Act
        with patch.object(sync_service, '_fetch_source_data') as mock_fetch:
            mock_fetch.return_value = source_data
            result = await sync_service.sync_data(
                source="external_api",
                target="database",
                db=mock_db
            )
        
        # Assert
        assert result.records_synced == 2
        assert result.status == "success"
        mock_fetch.assert_called_once()

    def test_event_bus_publish(self, integration_service):
        """Test publishing events to event bus."""
        # Arrange
        event_bus = EventBus()
        event = {
            "type": "user.created",
            "data": {"user_id": str(uuid4()), "email": "user@example.com"}
        }
        
        # Act
        result = event_bus.publish(event)
        
        # Assert
        assert result.event_id is not None
        assert result.published_at is not None

    def test_event_bus_subscribe(self, integration_service):
        """Test subscribing to events."""
        # Arrange
        event_bus = EventBus()
        handler_called = False
        
        def event_handler(event):
            nonlocal handler_called
            handler_called = True
        
        # Act
        event_bus.subscribe("user.created", event_handler)
        event_bus.publish({"type": "user.created", "data": {}})
        
        # Assert
        assert handler_called is True

    @pytest.mark.asyncio
    async def test_message_queue_operations(self, integration_service):
        """Test message queue operations."""
        # Arrange
        queue = MessageQueue("test_queue")
        messages = [
            {"id": "1", "content": "Message 1"},
            {"id": "2", "content": "Message 2"},
            {"id": "3", "content": "Message 3"}
        ]
        
        # Act
        for msg in messages:
            await queue.enqueue(msg)
        
        dequeued = await queue.dequeue()
        queue_size = await queue.size()
        
        # Assert
        assert dequeued["id"] == "1"
        assert queue_size == 2

    @pytest.mark.asyncio
    async def test_oauth_provider_authentication(self, integration_service):
        """Test OAuth provider authentication."""
        # Arrange
        provider = OAuthProvider(
            name="google",
            client_id="test_client_id",
            client_secret="test_secret",
            redirect_uri="https://example.com/callback"
        )
        
        # Act
        auth_url = provider.get_authorization_url(state="random_state")
        
        # Assert
        assert "oauth2/authorize" in auth_url
        assert "client_id=test_client_id" in auth_url
        assert "state=random_state" in auth_url

    @pytest.mark.asyncio
    async def test_oauth_token_exchange(self, integration_service):
        """Test OAuth token exchange."""
        # Arrange
        provider = OAuthProvider(
            name="google",
            client_id="test_client_id",
            client_secret="test_secret"
        )
        auth_code = "test_auth_code"
        
        # Act
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "access_token": "access_123",
                "refresh_token": "refresh_456",
                "expires_in": 3600
            })
            mock_post.return_value.__aenter__.return_value = mock_response
            
            tokens = await provider.exchange_code_for_token(auth_code)
        
        # Assert
        assert tokens["access_token"] == "access_123"
        assert tokens["refresh_token"] == "refresh_456"

    @pytest.mark.asyncio
    async def test_websocket_connection(self, integration_service):
        """Test WebSocket connection management."""
        # Arrange
        ws_manager = WebSocketManager()
        client_id = str(uuid4())
        
        # Act
        with patch('websockets.connect') as mock_connect:
            mock_ws = AsyncMock()
            mock_connect.return_value = mock_ws
            
            await ws_manager.connect(client_id, "wss://example.com/ws")
            is_connected = ws_manager.is_connected(client_id)
        
        # Assert
        assert is_connected is True
        mock_connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_websocket_message_broadcast(self, integration_service):
        """Test broadcasting messages via WebSocket."""
        # Arrange
        ws_manager = WebSocketManager()
        clients = ["client1", "client2", "client3"]
        message = {"type": "notification", "data": "Test message"}
        
        # Act
        with patch.object(ws_manager, 'send_to_client') as mock_send:
            mock_send.return_value = True
            results = await ws_manager.broadcast(message, clients)
        
        # Assert
        assert len(results) == 3
        assert mock_send.call_count == 3

    def test_integration_health_check(self, integration_service, mock_db):
        """Test checking integration health status."""
        # Arrange
        integration_id = str(uuid4())
        
        # Act
        with patch.object(integration_service, '_ping_endpoint') as mock_ping:
            mock_ping.return_value = {"status": "healthy", "latency": 50}
            health = integration_service.check_health(integration_id, mock_db)
        
        # Assert
        assert health.is_healthy is True
        assert health.latency == 50

    @pytest.mark.asyncio
    async def test_batch_webhook_send(self, integration_service):
        """Test sending webhooks in batch."""
        # Arrange
        webhooks = [
            {"url": "https://hook1.com", "payload": {"data": 1}},
            {"url": "https://hook2.com", "payload": {"data": 2}},
            {"url": "https://hook3.com", "payload": {"data": 3}}
        ]
        
        # Act
        webhook_service = WebhookService()
        with patch.object(webhook_service, 'send_webhook') as mock_send:
            mock_send.return_value = Mock(success=True)
            results = await webhook_service.send_batch(webhooks)
        
        # Assert
        assert len(results) == 3
        assert all(r.success for r in results)

    def test_integration_rate_limiting(self, integration_service):
        """Test rate limiting for integrations."""
        # Arrange
        integration_id = str(uuid4())
        limit = 100
        window = 3600  # 1 hour
        
        # Act
        with patch('services.integration_service.redis_client') as mock_redis:
            mock_redis.incr.return_value = 50
            result = integration_service.check_rate_limit(
                integration_id, limit, window
            )
        
        # Assert
        assert result.is_allowed is True
        assert result.remaining == 50

    def test_transform_data_format(self, integration_service):
        """Test data transformation between formats."""
        # Arrange
        source_data = {
            "firstName": "John",
            "lastName": "Doe",
            "emailAddress": "john@example.com"
        }
        mapping = {
            "firstName": "first_name",
            "lastName": "last_name",
            "emailAddress": "email"
        }
        
        # Act
        transformed = integration_service.transform_data(source_data, mapping)
        
        # Assert
        assert transformed["first_name"] == "John"
        assert transformed["last_name"] == "Doe"
        assert transformed["email"] == "john@example.com"

    @pytest.mark.asyncio
    async def test_external_api_pagination(self, integration_service):
        """Test handling paginated API responses."""
        # Arrange
        client = ExternalAPIClient("https://api.example.com")
        
        # Act
        with patch.object(client, '_make_request') as mock_request:
            mock_request.side_effect = [
                {"data": [1, 2, 3], "next_page": "page2"},
                {"data": [4, 5, 6], "next_page": "page3"},
                {"data": [7, 8], "next_page": None}
            ]
            all_data = await client.fetch_all_pages("/resources")
        
        # Assert
        assert len(all_data) == 8
        assert mock_request.call_count == 3

    def test_integration_error_handling(self, integration_service):
        """Test error handling in integrations."""
        # Arrange
        error_types = [
            "connection_timeout",
            "authentication_failed",
            "rate_limit_exceeded",
            "invalid_payload"
        ]
        
        # Act & Assert
        for error_type in error_types:
            error = integration_service.handle_error(error_type)
            assert error.should_retry is not None
            assert error.retry_after is not None
            assert error.error_message is not None

    def test_integration_metrics_collection(self, integration_service, mock_db):
        """Test collecting integration metrics."""
        # Arrange
        integration_id = str(uuid4())
        
        # Act
        with patch.object(integration_service, '_query_metrics') as mock_query:
            mock_query.return_value = {
                "requests_sent": 1000,
                "requests_failed": 50,
                "average_latency": 150,
                "uptime_percentage": 99.5
            }
            metrics = integration_service.get_metrics(integration_id, mock_db)
        
        # Assert
        assert metrics.success_rate == 0.95
        assert metrics.average_latency == 150
        assert metrics.uptime_percentage == 99.5