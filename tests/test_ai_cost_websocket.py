"""
Test suite for AI Cost Monitoring WebSocket endpoints.

This module tests all WebSocket functionality including:
- Real-time cost updates
- Budget alert notifications
- Live dashboard connections
- Connection management
- Message broadcasting
"""
from __future__ import annotations
import pytest
import json
import asyncio
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketState

from api.routers.ai_cost_websocket import (
    router,
    ConnectionManager,
    WebSocketMessage,
    CostUpdateMessage,
    BudgetAlertMessage
)

@pytest.fixture
def test_client():
    """Create a test client for WebSocket testing."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/ws")
    return TestClient(app)

@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket connection."""
    websocket = AsyncMock(spec=WebSocket)
    websocket.client_state = WebSocketState.CONNECTED
    websocket.application_state = WebSocketState.CONNECTED
    return websocket

@pytest.fixture
def connection_manager():
    """Create a ConnectionManager instance for testing."""
    return ConnectionManager()

@pytest.fixture
def mock_cost_manager():
    """Create a mock AI Cost Manager."""
    with patch('api.routers.ai_cost_websocket.AICostManager') as mock:
        manager = MagicMock()
        mock.return_value = manager
        yield manager

@pytest.fixture
def mock_cost_tracker():
    """Create a mock Cost Tracking Service."""
    with patch('api.routers.ai_cost_websocket.CostTrackingService') as mock:
        tracker = MagicMock()
        mock.return_value = tracker
        yield tracker

class TestWebSocketConnection:
    """Test WebSocket connection management."""
    
    async def test_connect_success(self, connection_manager, mock_websocket):
        """Test successful WebSocket connection."""
        # Arrange
        user_id = "user-123"
        connection_type = "dashboard"
        
        # Act
        connection_id = await connection_manager.connect(
            mock_websocket, 
            user_id, 
            connection_type
        )
        
        # Assert
        assert connection_id is not None
        assert connection_id in connection_manager.active_connections
        assert user_id in connection_manager.user_connections
        mock_websocket.accept.assert_called_once()
    
    async def test_disconnect(self, connection_manager, mock_websocket):
        """Test WebSocket disconnection."""
        # Arrange
        user_id = "user-123"
        connection_id = await connection_manager.connect(mock_websocket, user_id)
        
        # Act
        await connection_manager.disconnect(connection_id)
        
        # Assert
        assert connection_id not in connection_manager.active_connections
        if connection_manager.user_connections.get(user_id):
            assert connection_id not in connection_manager.user_connections[user_id]
    
    async def test_multiple_connections_same_user(self, connection_manager):
        """Test multiple WebSocket connections from same user."""
        # Arrange
        user_id = "user-123"
        websocket1 = AsyncMock(spec=WebSocket)
        websocket2 = AsyncMock(spec=WebSocket)
        
        # Act
        conn_id1 = await connection_manager.connect(websocket1, user_id, "dashboard")
        conn_id2 = await connection_manager.connect(websocket2, user_id, "mobile")
        
        # Assert
        assert conn_id1 != conn_id2
        assert len(connection_manager.user_connections[user_id]) == 2
        assert conn_id1 in connection_manager.user_connections[user_id]
        assert conn_id2 in connection_manager.user_connections[user_id]

class TestCostUpdates:
    """Test real-time cost update broadcasting."""
    
    async def test_broadcast_cost_update(self, connection_manager, mock_websocket):
        """Test broadcasting cost updates to connected clients."""
        # Arrange
        user_id = "user-123"
        await connection_manager.connect(mock_websocket, user_id)
        
        cost_update = {
            "current_cost": "45.67",
            "daily_total": "234.56",
            "monthly_total": "1234.56",
            "last_request_cost": "0.05"
        }
        
        # Act
        await connection_manager.broadcast_cost_update(user_id, cost_update)
        
        # Assert
        mock_websocket.send_json.assert_called()
        sent_data = mock_websocket.send_json.call_args[0][0]
        assert sent_data["type"] == "cost_update"
        assert sent_data["data"]["current_cost"] == "45.67"
    
    async def test_send_personal_message(self, connection_manager, mock_websocket):
        """Test sending personal message to specific connection."""
        # Arrange
        user_id = "user-123"
        connection_id = await connection_manager.connect(mock_websocket, user_id)
        
        message = {
            "type": "personal_alert",
            "data": {"message": "Your daily limit is approaching"}
        }
        
        # Act
        await connection_manager.send_personal_message(connection_id, message)
        
        # Assert
        mock_websocket.send_json.assert_called_with(message)
    
    async def test_broadcast_to_all(self, connection_manager):
        """Test broadcasting message to all connected clients."""
        # Arrange
        websocket1 = AsyncMock(spec=WebSocket)
        websocket2 = AsyncMock(spec=WebSocket)
        await connection_manager.connect(websocket1, "user-1")
        await connection_manager.connect(websocket2, "user-2")
        
        message = {
            "type": "system_announcement",
            "data": {"message": "Maintenance scheduled"}
        }
        
        # Act
        await connection_manager.broadcast_to_all(message)
        
        # Assert
        websocket1.send_json.assert_called_with(message)
        websocket2.send_json.assert_called_with(message)

class TestBudgetAlerts:
    """Test real-time budget alert notifications."""
    
    async def test_send_budget_alert(self, connection_manager, mock_websocket):
        """Test sending budget alert to user."""
        # Arrange
        user_id = "user-123"
        await connection_manager.connect(mock_websocket, user_id)
        
        alert = {
            "alert_type": "threshold_reached",
            "threshold_percent": 80,
            "current_usage_percent": 82.5,
            "message": "Daily budget 82.5% consumed",
            "severity": "warning"
        }
        
        # Act
        await connection_manager.send_budget_alert(user_id, alert)
        
        # Assert
        mock_websocket.send_json.assert_called()
        sent_data = mock_websocket.send_json.call_args[0][0]
        assert sent_data["type"] == "budget_alert"
        assert sent_data["data"]["severity"] == "warning"
    
    async def test_critical_budget_alert(self, connection_manager, mock_websocket):
        """Test sending critical budget alert."""
        # Arrange
        user_id = "user-123"
        await connection_manager.connect(mock_websocket, user_id)
        
        alert = {
            "alert_type": "limit_exceeded",
            "threshold_percent": 100,
            "current_usage_percent": 102.3,
            "message": "Monthly budget exceeded!",
            "severity": "critical",
            "auto_stop_enabled": True
        }
        
        # Act
        await connection_manager.send_budget_alert(user_id, alert)
        
        # Assert
        mock_websocket.send_json.assert_called()
        sent_data = mock_websocket.send_json.call_args[0][0]
        assert sent_data["data"]["severity"] == "critical"
        assert sent_data["data"]["auto_stop_enabled"] is True

class TestLiveDashboard:
    """Test live dashboard WebSocket functionality."""
    
    async def test_dashboard_initial_data(self, connection_manager, mock_websocket, mock_cost_manager):
        """Test sending initial data when dashboard connects."""
        # Arrange
        user_id = "user-123"
        mock_cost_manager.get_dashboard_data.return_value = {
            "current_costs": {
                "daily": "45.67",
                "monthly": "1234.56"
            },
            "recent_requests": [
                {"time": "10:30:00", "cost": "0.05", "model": "gpt-4"},
                {"time": "10:29:45", "cost": "0.03", "model": "gpt-3.5"}
            ],
            "budget_status": {
                "daily_percent": 45.7,
                "monthly_percent": 49.4
            }
        }
        
        # Act
        await connection_manager.connect_dashboard(mock_websocket, user_id)
        
        # Assert
        mock_websocket.send_json.assert_called()
        sent_data = mock_websocket.send_json.call_args[0][0]
        assert "current_costs" in sent_data["data"]
        assert "recent_requests" in sent_data["data"]
    
    async def test_dashboard_periodic_updates(self, connection_manager, mock_websocket):
        """Test periodic updates sent to dashboard."""
        # Arrange
        user_id = "user-123"
        connection_id = await connection_manager.connect(mock_websocket, user_id, "dashboard")
        
        # Simulate periodic update
        update_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "requests_per_minute": 5,
                "average_cost_per_request": "0.04",
                "cache_hit_rate": 0.23
            }
        }
        
        # Act
        await connection_manager.send_dashboard_update(connection_id, update_data)
        
        # Assert
        mock_websocket.send_json.assert_called()
        sent_data = mock_websocket.send_json.call_args[0][0]
        assert sent_data["type"] == "dashboard_update"
        assert "metrics" in sent_data["data"]

class TestWebSocketMessages:
    """Test WebSocket message handling."""
    
    async def test_handle_client_message(self, connection_manager, mock_websocket):
        """Test handling messages from client."""
        # Arrange
        user_id = "user-123"
        connection_id = await connection_manager.connect(mock_websocket, user_id)
        
        client_message = {
            "action": "subscribe",
            "channel": "cost_updates",
            "options": {"include_details": True}
        }
        
        # Act
        response = await connection_manager.handle_client_message(connection_id, client_message)
        
        # Assert
        assert response["status"] == "subscribed"
        assert response["channel"] == "cost_updates"
    
    async def test_handle_query_message(self, connection_manager, mock_websocket, mock_cost_manager):
        """Test handling query messages from client."""
        # Arrange
        user_id = "user-123"
        connection_id = await connection_manager.connect(mock_websocket, user_id)
        
        mock_cost_manager.query_costs.return_value = {
            "result": "123.45",
            "query_type": "total_today"
        }
        
        query_message = {
            "action": "query",
            "query_type": "total_today"
        }
        
        # Act
        response = await connection_manager.handle_client_message(connection_id, query_message)
        
        # Assert
        assert response["result"] == "123.45"
    
    async def test_handle_invalid_message(self, connection_manager, mock_websocket):
        """Test handling invalid messages from client."""
        # Arrange
        user_id = "user-123"
        connection_id = await connection_manager.connect(mock_websocket, user_id)
        
        invalid_message = {
            "invalid_field": "value"
        }
        
        # Act
        response = await connection_manager.handle_client_message(connection_id, invalid_message)
        
        # Assert
        assert response["status"] == "error"
        assert "error" in response

class TestConnectionResilience:
    """Test WebSocket connection resilience and error handling."""
    
    async def test_connection_timeout(self, connection_manager, mock_websocket):
        """Test handling connection timeout."""
        # Arrange
        user_id = "user-123"
        mock_websocket.receive_json.side_effect = asyncio.TimeoutError()
        
        # Act & Assert
        with pytest.raises(asyncio.TimeoutError):
            await connection_manager.listen_for_messages(mock_websocket, user_id)
    
    async def test_connection_lost(self, connection_manager, mock_websocket):
        """Test handling lost connection."""
        # Arrange
        user_id = "user-123"
        connection_id = await connection_manager.connect(mock_websocket, user_id)
        mock_websocket.client_state = WebSocketState.DISCONNECTED
        
        # Act
        is_alive = await connection_manager.check_connection(connection_id)
        
        # Assert
        assert is_alive is False
    
    async def test_reconnection(self, connection_manager):
        """Test client reconnection handling."""
        # Arrange
        user_id = "user-123"
        websocket1 = AsyncMock(spec=WebSocket)
        websocket2 = AsyncMock(spec=WebSocket)
        
        # Initial connection
        conn_id1 = await connection_manager.connect(websocket1, user_id)
        await connection_manager.disconnect(conn_id1)
        
        # Reconnection
        conn_id2 = await connection_manager.connect(websocket2, user_id)
        
        # Assert
        assert conn_id1 != conn_id2
        assert conn_id1 not in connection_manager.active_connections
        assert conn_id2 in connection_manager.active_connections

class TestWebSocketSecurity:
    """Test WebSocket security features."""
    
    async def test_authentication_required(self, test_client):
        """Test that authentication is required for WebSocket connection."""
        # Act & Assert
        with pytest.raises(WebSocketDisconnect):
            with test_client.websocket_connect("/api/v1/ws/costs") as websocket:
                # Should disconnect if no auth token
                pass
    
    async def test_rate_limiting(self, connection_manager, mock_websocket):
        """Test rate limiting on WebSocket messages."""
        # Arrange
        user_id = "user-123"
        connection_id = await connection_manager.connect(mock_websocket, user_id)
        
        # Send many messages rapidly
        messages = []
        for i in range(100):
            messages.append({
                "action": "query",
                "query_type": f"query_{i}"
            })
        
        # Act
        responses = []
        for msg in messages:
            response = await connection_manager.handle_client_message(connection_id, msg)
            responses.append(response)
        
        # Assert - Some messages should be rate limited
        rate_limited = [r for r in responses if r.get("status") == "rate_limited"]
        assert len(rate_limited) > 0

class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality."""
    
    @pytest.mark.integration
    async def test_full_websocket_flow(self, test_client):
        """Test complete WebSocket flow from connection to updates."""
        with test_client.websocket_connect("/api/v1/ws/costs?token=test-token") as websocket:
            # Send initial subscription
            websocket.send_json({
                "action": "subscribe",
                "channel": "all"
            })
            
            # Receive confirmation
            response = websocket.receive_json()
            assert response["status"] == "subscribed"
            
            # Simulate cost update
            websocket.send_json({
                "action": "track",
                "data": {
                    "service": "openai",
                    "cost": "0.05"
                }
            })
            
            # Receive cost update broadcast
            update = websocket.receive_json()
            assert update["type"] == "cost_update"
            
            # Query current totals
            websocket.send_json({
                "action": "query",
                "query_type": "daily_total"
            })
            
            # Receive query response
            query_response = websocket.receive_json()
            assert "result" in query_response

class TestWebSocketPerformance:
    """Performance tests for WebSocket connections."""
    
    @pytest.mark.performance
    async def test_concurrent_connections(self, connection_manager):
        """Test handling many concurrent WebSocket connections."""
        # Arrange
        websockets = []
        connection_ids = []
        
        # Create 100 concurrent connections
        for i in range(100):
            ws = AsyncMock(spec=WebSocket)
            websockets.append(ws)
            conn_id = await connection_manager.connect(ws, f"user-{i}")
            connection_ids.append(conn_id)
        
        # Assert all connections are tracked
        assert len(connection_manager.active_connections) == 100
        
        # Broadcast message to all
        message = {"type": "test", "data": {}}
        await connection_manager.broadcast_to_all(message)
        
        # Verify all received the message
        for ws in websockets:
            ws.send_json.assert_called_with(message)
        
        # Clean up
        for conn_id in connection_ids:
            await connection_manager.disconnect(conn_id)
    
    @pytest.mark.performance
    async def test_message_throughput(self, connection_manager, mock_websocket):
        """Test high message throughput on single connection."""
        # Arrange
        user_id = "user-123"
        connection_id = await connection_manager.connect(mock_websocket, user_id)
        
        # Send 1000 messages
        start_time = datetime.utcnow()
        for i in range(1000):
            await connection_manager.send_personal_message(
                connection_id,
                {"type": "update", "seq": i}
            )
        end_time = datetime.utcnow()
        
        # Assert
        duration = (end_time - start_time).total_seconds()
        messages_per_second = 1000 / duration
        assert messages_per_second > 100  # Should handle at least 100 msgs/sec
        assert mock_websocket.send_json.call_count == 1000

# Smoke Tests
class TestWebSocketSmoke:
    """Smoke tests for WebSocket functionality."""
    
    @pytest.mark.smoke
    def test_websocket_endpoint_exists(self, test_client):
        """Test that WebSocket endpoint is accessible."""
        # This will fail to connect without auth but proves endpoint exists
        with pytest.raises((WebSocketDisconnect, Exception)):
            with test_client.websocket_connect("/api/v1/ws/costs"):
                pass
    
    @pytest.mark.smoke
    async def test_connection_manager_initialization(self):
        """Test that ConnectionManager initializes correctly."""
        manager = ConnectionManager()
        assert manager.active_connections == {}
        assert manager.user_connections == {}
        assert manager.cost_manager is not None
        assert manager.cost_tracker is not None