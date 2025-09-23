"""
Pytest integration tests for database health checks.

These tests verify the database health check functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.diagnostics.database_health_check import DatabaseHealthChecker


class TestDatabaseHealthCheck:
    """Test suite for database health checks."""

    @pytest.fixture
    async def checker(self):
        """Create a health checker instance."""
        return DatabaseHealthChecker()

    @pytest.mark.asyncio
    async def test_check_database_connectivity_success(self, checker):
        """Test successful database connectivity check."""
        mock_engine_info = {'async_engine_initialized': True}
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = "PostgreSQL 14.5"
        mock_db.execute.return_value = mock_result

        async def mock_get_async_db():
            yield mock_db

        with patch('scripts.diagnostics.database_health_check.get_engine_info',
                   return_value=mock_engine_info), \
             patch('scripts.diagnostics.database_health_check.get_async_db',
                   mock_get_async_db):
            result = await checker.check_database_connectivity()

        assert result is True
        assert checker.results['connectivity']['status'] == 'connected'
        assert 'PostgreSQL' in checker.results['connectivity']['database_version']

    @pytest.mark.asyncio
    async def test_check_database_connectivity_not_initialized(self, checker):
        """Test database connectivity check when engine not initialized."""
        mock_engine_info = {'async_engine_initialized': False}

        with patch('scripts.diagnostics.database_health_check.get_engine_info',
                   return_value=mock_engine_info):
            result = await checker.check_database_connectivity()

        assert result is False
        assert checker.results['connectivity']['status'] == 'failed'
        assert len(checker.issues) > 0

    @pytest.mark.asyncio
    async def test_check_connection_pool_health(self, checker):
        """Test connection pool health monitoring."""
        mock_monitor = MagicMock()
        mock_monitor.get_monitoring_summary.return_value = {
            'current_metrics': {
                'async': {
                    'size': 10,
                    'checked_out_connections': 3,
                    'overflow': 0,
                    'utilization_percent': 30
                }
            }
        }

        with patch('scripts.diagnostics.database_health_check.get_database_monitor',
                   return_value=mock_monitor):
            result = await checker.check_connection_pool_health()

        assert result['status'] == 'healthy'
        assert result['metrics']['async']['utilization_percent'] == 30

    @pytest.mark.asyncio
    async def test_check_connection_pool_high_utilization(self, checker):
        """Test connection pool with high utilization."""
        mock_monitor = MagicMock()
        mock_monitor.get_monitoring_summary.return_value = {
            'current_metrics': {
                'async': {
                    'size': 10,
                    'checked_out_connections': 9,
                    'overflow': 2,
                    'utilization_percent': 92
                }
            }
        }

        with patch('scripts.diagnostics.database_health_check.get_database_monitor',
                   return_value=mock_monitor):
            result = await checker.check_connection_pool_health()

        assert result['status'] == 'warning'
        assert len(checker.warnings) > 0

    @pytest.mark.asyncio
    async def test_check_connection_pool_critical(self, checker):
        """Test connection pool with critical utilization."""
        mock_monitor = MagicMock()
        mock_monitor.get_monitoring_summary.return_value = {
            'current_metrics': {
                'async': {
                    'size': 10,
                    'checked_out_connections': 10,
                    'overflow': 5,
                    'utilization_percent': 96
                }
            }
        }

        with patch('scripts.diagnostics.database_health_check.get_database_monitor',
                   return_value=mock_monitor):
            result = await checker.check_connection_pool_health()

        assert result['status'] == 'critical'
        assert len(checker.issues) > 0

    @pytest.mark.asyncio
    async def test_check_table_statistics(self, checker):
        """Test table statistics analysis."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ('public', 'users', '1.5 MB', '1.2 MB', 1000, 50,
             datetime.now() - timedelta(days=1), datetime.now()),
            ('public', 'assessments', '500 KB', '400 KB', 500, 10,
             datetime.now() - timedelta(hours=6), datetime.now())
        ]
        mock_db.execute.return_value = mock_result

        async def mock_get_async_db():
            yield mock_db

        with patch('scripts.diagnostics.database_health_check.get_async_db',
                   mock_get_async_db):
            result = await checker.check_table_statistics()

        assert 'public.users' in result
        assert result['public.users']['row_count'] == 1000
        assert result['public.users']['dead_rows'] == 50

    @pytest.mark.asyncio
    async def test_check_table_statistics_high_dead_rows(self, checker):
        """Test table statistics with high dead row ratio."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ('public', 'users', '1.5 MB', '1.2 MB', 1000, 300, None, None)
        ]
        mock_db.execute.return_value = mock_result

        async def mock_get_async_db():
            yield mock_db

        with patch('scripts.diagnostics.database_health_check.get_async_db',
                   mock_get_async_db):
            await checker.check_table_statistics()

        assert len(checker.warnings) > 0
        assert len(checker.recommendations) > 0
        assert any('VACUUM' in rec for rec in checker.recommendations)

    @pytest.mark.asyncio
    async def test_check_index_usage(self, checker):
        """Test index usage analysis."""
        mock_db = AsyncMock()

        # Mock unused indexes result
        unused_result = MagicMock()
        unused_result.fetchall.return_value = [
            ('public', 'users', 'idx_unused', '100 KB', 0)
        ]

        # Mock sequential scan result
        seq_scan_result = MagicMock()
        seq_scan_result.fetchall.return_value = [
            ('public', 'large_table', 10000, 1000000, 100, 5000)
        ]

        mock_db.execute = AsyncMock(side_effect=[unused_result, seq_scan_result])

        async def mock_get_async_db():
            yield mock_db

        with patch('scripts.diagnostics.database_health_check.get_async_db',
                   mock_get_async_db):
            result = await checker.check_index_usage()

        assert len(result['unused_indexes']) == 1
        assert result['unused_indexes'][0]['index'] == 'idx_unused'
        assert len(checker.warnings) > 0

    @pytest.mark.asyncio
    async def test_check_active_queries(self, checker):
        """Test active query monitoring."""
        mock_db = AsyncMock()
        mock_result = MagicMock()

        # Create a query that's been running for 10 minutes
        query_start = datetime.now() - timedelta(minutes=10)
        mock_result.fetchall.return_value = [
            (123, 'user1', 'app1', 'active', query_start, datetime.now(),
             'Client', 'ClientRead', 'SELECT * FROM large_table')
        ]
        mock_db.execute.return_value = mock_result

        async def mock_get_async_db():
            yield mock_db

        with patch('scripts.diagnostics.database_health_check.get_async_db',
                   mock_get_async_db):
            result = await checker.check_active_queries()

        assert len(result) == 1
        assert result[0]['pid'] == 123
        assert len(checker.warnings) > 0  # Should warn about long-running query

    @pytest.mark.asyncio
    async def test_check_lock_status_no_blocks(self, checker):
        """Test lock status check with no blocking locks."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.execute.return_value = mock_result

        async def mock_get_async_db():
            yield mock_db

        with patch('scripts.diagnostics.database_health_check.get_async_db',
                   mock_get_async_db):
            result = await checker.check_lock_status()

        assert result['lock_count'] == 0
        assert len(result['blocking_locks']) == 0
        assert len(checker.issues) == 0

    @pytest.mark.asyncio
    async def test_check_lock_status_with_blocks(self, checker):
        """Test lock status check with blocking locks."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (456, 'user1', 123, 'user2', 'app1', 'app2',
             datetime.now() - timedelta(minutes=2),
             'UPDATE users SET...', 'SELECT * FROM users...')
        ]
        mock_db.execute.return_value = mock_result

        async def mock_get_async_db():
            yield mock_db

        with patch('scripts.diagnostics.database_health_check.get_async_db',
                   mock_get_async_db):
            result = await checker.check_lock_status()

        assert result['lock_count'] == 1
        assert len(result['blocking_locks']) == 1
        assert result['blocking_locks'][0]['blocking_pid'] == 123
        assert len(checker.issues) > 0

    @pytest.mark.asyncio
    async def test_check_redis_health_not_configured(self, checker):
        """Test Redis health check when not configured."""
        with patch('os.getenv', return_value=None):
            result = await checker.check_redis_health()

        assert result['status'] == 'not_configured'

    @pytest.mark.asyncio
    async def test_check_redis_health_success(self, checker):
        """Test successful Redis health check."""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_redis.info = AsyncMock(return_value={
            'redis_version': '6.2.6',
            'uptime_in_seconds': 86400,
            'connected_clients': 5,
            'used_memory_human': '100M',
            'used_memory_peak_human': '150M'
        })

        with patch('os.getenv', return_value='redis://localhost:6379'), \
             patch('scripts.diagnostics.database_health_check.get_redis_client',
                   AsyncMock(return_value=mock_redis)):
            result = await checker.check_redis_health()

        assert result['status'] == 'healthy'
        assert result['connected'] is True
        assert result['version'] == '6.2.6'

    @pytest.mark.asyncio
    async def test_generate_health_report_healthy(self, checker):
        """Test health report generation when everything is healthy."""
        checker.results = {
            'connectivity': {'status': 'connected'},
            'connection_pool': {'status': 'healthy'},
            'table_statistics': {'status': 'analyzed'},
            'index_analysis': {'status': 'analyzed'},
            'active_queries': {'count': 2},
            'lock_status': {'lock_count': 0},
            'redis': {'status': 'healthy'}
        }
        checker.issues = []
        checker.warnings = []
        checker.recommendations = []

        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = await checker.generate_health_report()

        assert result is True
        mock_file.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_health_report_with_issues(self, checker):
        """Test health report generation with critical issues."""
        checker.results = {
            'connectivity': {'status': 'failed'},
            'connection_pool': {'status': 'critical'}
        }
        checker.issues = ["Database connection failed", "Pool exhausted"]
        checker.warnings = ["High dead row ratio"]
        checker.recommendations = ["Run VACUUM"]

        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = await checker.generate_health_report()

        assert result is False  # Critical issues present
        mock_file.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_health_check_full(self, checker):
        """Test full health check execution."""
        # Mock all check methods
        checker.check_database_connectivity = AsyncMock(return_value=True)
        checker.check_connection_pool_health = AsyncMock(return_value={'status': 'healthy'})
        checker.check_table_statistics = AsyncMock(return_value={})
        checker.check_index_usage = AsyncMock(return_value={})
        checker.check_active_queries = AsyncMock(return_value=[])
        checker.check_lock_status = AsyncMock(return_value={'lock_count': 0})
        checker.check_redis_health = AsyncMock(return_value={'status': 'healthy'})
        checker.generate_health_report = AsyncMock(return_value=True)

        result = await checker.run_health_check()

        assert result is True
        checker.check_database_connectivity.assert_called_once()
        checker.generate_health_report.assert_called_once()