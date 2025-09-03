"""
Performance optimization infrastructure for RuleIQ.

This module provides comprehensive performance enhancements including:
- Database query optimization
- Redis caching layer
- Connection pooling
- Query result caching
- Response compression
- N+1 query prevention
- Lazy loading strategies
- Query batching
- JSON serialization optimization
"""

from .cache_manager import CacheManager, cache_key_builder
from .db_optimizer import DatabaseOptimizer, QueryAnalyzer
from .query_cache import QueryCache, cached_query
from .response_compression import ResponseCompressor
from .connection_pool import ConnectionPoolManager
from .metrics_collector import PerformanceMetrics

__all__ = [
    'CacheManager',
    'cache_key_builder',
    'DatabaseOptimizer',
    'QueryAnalyzer',
    'QueryCache',
    'cached_query',
    'ResponseCompressor',
    'ConnectionPoolManager',
    'PerformanceMetrics',
]