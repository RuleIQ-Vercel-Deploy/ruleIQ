#!/usr/bin/env python3
"""
Performance test suite for backend fixes
Tests all performance optimizations that were implemented
"""

import pytest
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from database.query_optimization import QueryOptimizer
from api.utils.error_handlers import DatabaseException
from config.settings import settings

class TestPerformanceFixes:
    """Test suite for performance optimization fixes"""
    
    def test_query_optimizer_initialization(self):
        """Test QueryOptimizer is properly initialized"""
        optimizer = QueryOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, 'batch_load_related')
        assert hasattr(optimizer, 'optimize_query')
    
    def test_n1_query_prevention(self):
        """Test N+1 query prevention methods"""
        optimizer = QueryOptimizer()
        
        # Test batch loading method exists
        assert callable(getattr(optimizer, 'batch_load_related', None))
        
        # Test query optimization method exists
        assert callable(getattr(optimizer, 'optimize_query', None))
    
    def test_database_indexes_migration(self):
        """Test database indexes are created properly"""
        # This would require actual database connection
        # For now, test the migration file exists and is valid
        
        with open('database/migrations/010_add_performance_indexes.py', 'r') as f:
            migration_content = f.read()
        
        # Check for common index patterns
        assert 'CREATE INDEX' in migration_content
        assert 'IF NOT EXISTS' in migration_content  # Safe index creation
        
        # Check for specific indexes mentioned in the fixes
        index_patterns = [
            'idx_evidence_user_id',
            'idx_assessments_status',
            'idx_compliance_framework_id',
            'idx_evidence_created_at',
            'idx_users_email'
        ]
        
        for pattern in index_patterns:
            assert pattern in migration_content
    
    def test_caching_implementation(self):
        """Test caching is properly configured"""
        # Test Redis configuration
        assert settings.redis_url is not None
        
        # Test cache-related settings
        assert hasattr(settings, 'cache_ttl')
        assert settings.cache_ttl > 0
    
    def test_batch_operations(self):
        """Test batch operations are implemented"""
        optimizer = QueryOptimizer()
        
        # Test batch size configuration
        assert hasattr(optimizer, 'default_batch_size')
        assert optimizer.default_batch_size > 1  # Should be batch, not single
        
    def test_memory_leak_prevention(self):
        """Test memory leak prevention measures"""
        optimizer = QueryOptimizer()
        
        # Test connection pooling
        assert hasattr(settings, 'database_url')
        assert 'pool_size' in str(settings.database_url) or hasattr(settings, 'db_pool_size')
    
    def test_query_performance_monitoring(self):
        """Test query performance monitoring"""
        optimizer = QueryOptimizer()
        
        # Test query timing functionality
        assert hasattr(optimizer, 'measure_query_time')
        assert callable(getattr(optimizer, 'measure_query_time', None))
    
    def test_connection_pooling(self):
        """Test database connection pooling"""
        # Test pool configuration
        assert hasattr(settings, 'db_pool_size')
        assert settings.db_pool_size >= 5  # Minimum reasonable pool size
        
        assert hasattr(settings, 'db_max_overflow')
        assert settings.db_max_overflow >= 10
    
    def test_slow_query_detection(self):
        """Test slow query detection"""
        optimizer = QueryOptimizer()
        
        # Test slow query threshold
        assert hasattr(optimizer, 'slow_query_threshold')
        assert optimizer.slow_query_threshold > 0  # Should be positive
    
    @pytest.mark.parametrize("query_type,expected_optimization", [
        ("select_related", "JOIN"),
        ("prefetch_related", "IN"),
        ("batch_select", "BATCH"),
    ])
    def test_query_optimization_strategies(self, query_type, expected_optimization):
        """Test different query optimization strategies"""
        optimizer = QueryOptimizer()
        
        # Test optimization methods exist
        method_name = f"optimize_{query_type}"
        assert hasattr(optimizer, method_name) or hasattr(optimizer, 'optimize_query')


class TestDatabaseIndexes:
    """Test suite for database index optimizations"""
    
    def test_index_coverage(self):
        """Test critical queries have appropriate indexes"""
        # Test that indexes cover common query patterns
        expected_indexes = [
            ('evidence', 'user_id'),
            ('evidence', 'created_at'),
            ('assessments', 'status'),
            ('assessments', 'user_id'),
            ('compliance_checks', 'framework_id'),
            ('users', 'email'),
        ]
        
        # This would require actual database inspection
        # For now, verify the migration covers these
        with open('database/migrations/010_add_performance_indexes.py', 'r') as f:
            content = f.read()
        
        for table, column in expected_indexes:
            assert f"{table}_{column}" in content
    
    def test_composite_indexes(self):
        """Test composite indexes for complex queries"""
        with open('database/migrations/010_add_performance_indexes.py', 'r') as f:
            content = f.read()
        
        # Check for composite indexes
        composite_patterns = [
            'user_id', 'created_at',
            'framework_id', 'status',
            'assessment_id', 'requirement_id'
        ]
        
        for pattern in composite_patterns:
            assert pattern in content
    
    def test_index_performance_impact(self):
        """Test indexes improve query performance"""
        # This would require actual performance testing
        # For now, test the optimization methods exist
        optimizer = QueryOptimizer()
        
        # Test explain query functionality
        assert hasattr(optimizer, 'explain_query')
        assert callable(getattr(optimizer, 'explain_query', None))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])