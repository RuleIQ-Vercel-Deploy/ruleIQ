"""
Pytest integration tests for endpoint validation.

These tests verify the endpoint validation script functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import httpx

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.diagnostics.validate_endpoints import EndpointValidator


class TestEndpointValidation:
    """Test suite for endpoint validation."""

    @pytest.fixture
    async def validator(self):
        """Create a validator instance."""
        return EndpointValidator(base_url="http://localhost:8000")

    @pytest.mark.asyncio
    async def test_setup_test_user_create_success(self, validator):
        """Test successful test user creation."""
        mock_response_register = AsyncMock()
        mock_response_register.status_code = 201

        mock_response_login = AsyncMock()
        mock_response_login.status_code = 200
        mock_response_login.json.return_value = {"access_token": "test-token"}

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=[mock_response_register, mock_response_login])

        with patch('httpx.AsyncClient', return_value=mock_client):
            result = await validator.setup_test_user()

        assert result is True
        assert validator.auth_token == "test-token"

    @pytest.mark.asyncio
    async def test_setup_test_user_already_exists(self, validator):
        """Test test user setup when user already exists."""
        mock_response_register = AsyncMock()
        mock_response_register.status_code = 400  # User already exists

        mock_response_login = AsyncMock()
        mock_response_login.status_code = 200
        mock_response_login.json.return_value = {"access_token": "test-token"}

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=[mock_response_register, mock_response_login])

        with patch('httpx.AsyncClient', return_value=mock_client):
            result = await validator.setup_test_user()

        assert result is True
        assert validator.auth_token == "test-token"

    @pytest.mark.asyncio
    async def test_authenticate_success(self, validator):
        """Test successful authentication."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test-token"}

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            result = await validator.authenticate()

        assert result is True
        assert validator.auth_token == "test-token"

    @pytest.mark.asyncio
    async def test_authenticate_failure(self, validator):
        """Test authentication failure."""
        mock_response = AsyncMock()
        mock_response.status_code = 401

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            result = await validator.authenticate()

        assert result is False
        assert validator.auth_token is None

    @pytest.mark.asyncio
    async def test_check_endpoint_success(self, validator):
        """Test successful endpoint check."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            success, message, status = await validator.check_endpoint(
                "GET", "/api/v1/health", False
            )

        assert success is True
        assert status == 200
        assert "Valid JSON response" in message

    @pytest.mark.asyncio
    async def test_check_endpoint_with_auth(self, validator):
        """Test endpoint check with authentication."""
        validator.auth_token = "test-token"

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "protected"}

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            success, message, status = await validator.check_endpoint(
                "GET", "/api/v1/users/me", True
            )

        assert success is True
        assert status == 200
        # Verify auth header was included
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert "Authorization" in call_args.kwargs["headers"]
        assert call_args.kwargs["headers"]["Authorization"] == "Bearer test-token"

    @pytest.mark.asyncio
    async def test_check_endpoint_timeout(self, validator):
        """Test endpoint check timeout handling."""
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        with patch('httpx.AsyncClient', return_value=mock_client):
            success, message, status = await validator.check_endpoint(
                "GET", "/api/v1/health", False
            )

        assert success is False
        assert message == "Timeout"
        assert status == 0

    @pytest.mark.asyncio
    async def test_check_endpoint_connection_error(self, validator):
        """Test endpoint check connection error handling."""
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))

        with patch('httpx.AsyncClient', return_value=mock_client):
            success, message, status = await validator.check_endpoint(
                "GET", "/api/v1/health", False
            )

        assert success is False
        assert message == "Connection failed"
        assert status == 0

    @pytest.mark.asyncio
    async def test_check_endpoint_invalid_json(self, validator):
        """Test endpoint check with invalid JSON response."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            success, message, status = await validator.check_endpoint(
                "GET", "/api/v1/health", False
            )

        assert success is False
        assert "Invalid JSON response" in message

    @pytest.mark.asyncio
    async def test_validate_health_endpoints(self, validator):
        """Test health endpoint validation."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            await validator.validate_health_endpoints()

        assert "health:/api/v1/health" in validator.results
        assert validator.results["health:/api/v1/health"]["success"] is True
        assert validator.results["health:/api/v1/health"]["critical"] is True

    @pytest.mark.asyncio
    async def test_validate_websocket_endpoints(self, validator):
        """Test WebSocket endpoint validation."""
        mock_response = AsyncMock()
        mock_response.status_code = 426  # Upgrade Required

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            await validator.validate_websocket_endpoints()

        assert "websocket:/ws/chat" in validator.results
        assert validator.results["websocket:/ws/chat"]["success"] is True
        assert validator.results["websocket:/ws/chat"]["message"] == "WebSocket endpoint exists"

    @pytest.mark.asyncio
    async def test_generate_report_all_passed(self, validator):
        """Test report generation when all endpoints pass."""
        validator.results = {
            "health:/api/v1/health": {
                "success": True,
                "message": "Status: 200",
                "status": 200,
                "critical": True
            },
            "auth:/api/v1/auth/login": {
                "success": True,
                "message": "Status: 200",
                "status": 200,
                "critical": True
            }
        }

        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = await validator.generate_report()

        assert result is True
        mock_file.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_report_with_failures(self, validator):
        """Test report generation with critical failures."""
        validator.results = {
            "health:/api/v1/health": {
                "success": False,
                "message": "Connection failed",
                "status": 0,
                "critical": True
            },
            "business:/api/v1/assessments": {
                "success": False,
                "message": "Status: 404",
                "status": 404,
                "critical": False
            }
        }

        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = await validator.generate_report()

        assert result is False  # Critical failure present
        mock_file.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_validation_server_not_running(self, validator):
        """Test validation when server is not running."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Cannot connect"))

        with patch('httpx.AsyncClient', return_value=mock_client):
            result = await validator.run_validation()

        assert result is False

    @pytest.mark.asyncio
    async def test_run_validation_full_success(self, validator):
        """Test full validation success."""
        # Mock server health check
        mock_health_response = AsyncMock()
        mock_health_response.status_code = 200

        # Mock all validation methods
        validator.setup_test_user = AsyncMock(return_value=True)
        validator.validate_health_endpoints = AsyncMock()
        validator.validate_auth_endpoints = AsyncMock()
        validator.validate_business_endpoints = AsyncMock()
        validator.validate_admin_endpoints = AsyncMock()
        validator.validate_websocket_endpoints = AsyncMock()
        validator.generate_report = AsyncMock(return_value=True)

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_health_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            result = await validator.run_validation()

        assert result is True
        validator.setup_test_user.assert_called_once()
        validator.generate_report.assert_called_once()