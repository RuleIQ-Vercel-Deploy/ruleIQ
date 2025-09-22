"""
Pytest integration tests for startup validation.

These tests verify that all critical components can be initialized properly.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.diagnostics.test_startup import StartupValidator


class TestStartupValidation:
    """Test suite for startup validation."""

    @pytest.fixture
    async def validator(self):
        """Create a validator instance."""
        return StartupValidator()

    @pytest.mark.asyncio
    async def test_environment_variables_present(self, validator, monkeypatch):
        """Test that environment variable check passes when vars are present."""
        monkeypatch.setenv('DATABASE_URL', 'postgresql://test:test@localhost/test')
        monkeypatch.setenv('JWT_SECRET_KEY', 'test-secret-key')
        monkeypatch.setenv('ENVIRONMENT', 'testing')

        result = await validator.check_environment_variables()

        assert result is True
        assert 'environment' in validator.results
        assert validator.results['environment'][0] is True

    @pytest.mark.asyncio
    async def test_environment_variables_missing(self, validator, monkeypatch):
        """Test that environment variable check fails when vars are missing."""
        # Clear environment variables
        monkeypatch.delenv('DATABASE_URL', raising=False)
        monkeypatch.delenv('JWT_SECRET_KEY', raising=False)

        with patch('scripts.diagnostics.test_startup.os.getenv', return_value=None):
            result = await validator.check_environment_variables()

        assert result is False
        assert 'environment' in validator.results
        assert validator.results['environment'][0] is False

    @pytest.mark.asyncio
    async def test_database_connection_success(self, validator):
        """Test successful database connection."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        mock_db.execute.return_value = mock_result

        async def mock_get_async_db():
            yield mock_db

        with patch('scripts.diagnostics.test_startup.init_db', return_value=True), \
             patch('scripts.diagnostics.test_startup.get_async_db', mock_get_async_db):
            result = await validator.check_database_connection()

        assert result is True
        assert 'database' in validator.results
        assert validator.results['database'][0] is True

    @pytest.mark.asyncio
    async def test_database_connection_failure(self, validator):
        """Test database connection failure."""
        with patch('scripts.diagnostics.test_startup.init_db', return_value=False):
            result = await validator.check_database_connection()

        assert result is False
        assert 'database' in validator.results
        assert validator.results['database'][0] is False
        assert len(validator.critical_failures) > 0

    @pytest.mark.asyncio
    async def test_api_initialization_success(self, validator):
        """Test successful API initialization."""
        mock_app = MagicMock()
        mock_route1 = MagicMock()
        mock_route1.path = '/api/v1/health'
        mock_route2 = MagicMock()
        mock_route2.path = '/api/v1/auth/login'
        mock_route3 = MagicMock()
        mock_route3.path = '/api/v1/assessments'
        mock_route4 = MagicMock()
        mock_route4.path = '/api/v1/compliance'

        mock_app.routes = [mock_route1, mock_route2, mock_route3, mock_route4]

        with patch('scripts.diagnostics.test_startup.app', mock_app):
            result = await validator.check_api_initialization()

        assert result is True
        assert 'api' in validator.results
        assert validator.results['api'][0] is True

    @pytest.mark.asyncio
    async def test_api_initialization_missing_endpoints(self, validator):
        """Test API initialization with missing critical endpoints."""
        mock_app = MagicMock()
        mock_route = MagicMock()
        mock_route.path = '/api/v1/other'
        mock_app.routes = [mock_route]

        with patch('scripts.diagnostics.test_startup.app', mock_app):
            result = await validator.check_api_initialization()

        assert result is False
        assert 'api' in validator.results
        assert validator.results['api'][0] is False

    @pytest.mark.asyncio
    async def test_redis_connection_optional(self, validator, monkeypatch):
        """Test that Redis connection is optional."""
        monkeypatch.delenv('REDIS_URL', raising=False)

        result = await validator.check_redis_connection()

        assert result is True  # Should return True since Redis is optional
        assert 'redis' in validator.results
        assert validator.results['redis'][0] is True

    @pytest.mark.asyncio
    async def test_redis_connection_success(self, validator, monkeypatch):
        """Test successful Redis connection."""
        monkeypatch.setenv('REDIS_URL', 'redis://localhost:6379')

        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)

        with patch('scripts.diagnostics.test_startup.get_redis_client',
                   AsyncMock(return_value=mock_redis)):
            result = await validator.check_redis_connection()

        assert result is True
        assert 'redis' in validator.results
        assert validator.results['redis'][0] is True

    @pytest.mark.asyncio
    async def test_service_initialization_all_success(self, validator):
        """Test all services initialize successfully."""
        with patch('scripts.diagnostics.test_startup.__import__',
                   side_effect=lambda *args, **kwargs: MagicMock()):
            result = await validator.check_service_initialization()

        assert result is True
        assert 'services' in validator.results
        assert validator.results['services'][0] is True

    @pytest.mark.asyncio
    async def test_service_initialization_partial_failure(self, validator):
        """Test partial service initialization failure."""
        def mock_import(name, *args, **kwargs):
            if 'auth_service' in name:
                raise ImportError("Mock import error")
            return MagicMock()

        with patch('scripts.diagnostics.test_startup.__import__', side_effect=mock_import):
            result = await validator.check_service_initialization()

        assert result is False
        assert 'services' in validator.results
        assert validator.results['services'][0] is False

    @pytest.mark.asyncio
    async def test_full_validation_success(self, validator, monkeypatch):
        """Test full validation pass."""
        monkeypatch.setenv('DATABASE_URL', 'postgresql://test:test@localhost/test')
        monkeypatch.setenv('JWT_SECRET_KEY', 'test-secret-key')
        monkeypatch.setenv('ENVIRONMENT', 'testing')

        # Mock all check methods to return True
        validator.check_environment_variables = AsyncMock(return_value=True)
        validator.check_database_connection = AsyncMock(return_value=True)
        validator.check_api_initialization = AsyncMock(return_value=True)
        validator.check_redis_connection = AsyncMock(return_value=True)
        validator.check_service_initialization = AsyncMock(return_value=True)

        # Set results for summary
        validator.results = {
            'environment': (True, "All required environment variables present"),
            'database': (True, "Database connection successful"),
            'api': (True, "API initialized"),
            'redis': (True, "Redis connected"),
            'services': (True, "All services initialized")
        }

        result = await validator.run_validation()

        assert result is True
        assert len(validator.critical_failures) == 0

    @pytest.mark.asyncio
    async def test_full_validation_with_failures(self, validator):
        """Test full validation with some failures."""
        # Mock check methods with mixed results
        validator.check_environment_variables = AsyncMock(return_value=True)
        validator.check_database_connection = AsyncMock(return_value=False)
        validator.check_api_initialization = AsyncMock(return_value=True)
        validator.check_redis_connection = AsyncMock(return_value=True)
        validator.check_service_initialization = AsyncMock(return_value=False)

        # Set results for summary
        validator.results = {
            'environment': (True, "All required environment variables present"),
            'database': (False, "Database connection failed"),
            'api': (True, "API initialized"),
            'redis': (True, "Redis not configured"),
            'services': (False, "Some services failed")
        }
        validator.critical_failures = ["Database initialization failed"]

        result = await validator.run_validation()

        assert result is False
        assert len(validator.critical_failures) > 0