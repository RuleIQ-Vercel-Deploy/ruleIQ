"""
Query result caching for database operations.

Provides decorators and utilities for caching database query results.
"""

import hashlib
import json
import logging
from typing import Any, Optional, Union, Callable, Dict, List
from datetime import timedelta
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query
from sqlalchemy.sql import Select

from .cache_manager import CacheManager, cache_key_builder

logger = logging.getLogger(__name__)


class QueryCache:
    """
    Manages caching of database query results.
    """
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache_manager = cache_manager or CacheManager()
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize the query cache."""
        if not self._initialized:
            await self.cache_manager.initialize()
            self._initialized = True
            
    async def get_cached_result(
        self,
        query_key: str
    ) -> Optional[Any]:
        """Get cached query result."""
        return await self.cache_manager.get(f"query:{query_key}")
        
    async def cache_result(
        self,
        query_key: str,
        result: Any,
        ttl: int = 300
    ) -> bool:
        """Cache a query result."""
        return await self.cache_manager.set(f"query:{query_key}", result, ttl)
        
    async def invalidate_query(self, query_key: str) -> bool:
        """Invalidate a cached query result."""
        return await self.cache_manager.delete(f"query:{query_key}")
        
    async def invalidate_table(self, table_name: str) -> int:
        """Invalidate all cached queries for a table."""
        pattern = f"query:*{table_name}*"
        return await self.cache_manager.delete_pattern(pattern)
        
    def generate_query_key(
        self,
        query: Union[str, Query, Select],
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a cache key for a query."""
        # Convert query to string
        if hasattr(query, 'statement'):
            query_str = str(query.statement.compile(compile_kwargs={"literal_binds": True}))
        else:
            query_str = str(query)
            
        # Include parameters in key
        if params:
            params_str = json.dumps(params, sort_keys=True, default=str)
            query_str = f"{query_str}:{params_str}"
            
        # Hash the query string for a compact key
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()[:16]
        
        # Extract table names for invalidation
        tables = self._extract_table_names(query_str)
        if tables:
            return f"{tables[0]}:{query_hash}"
        return query_hash
        
    def _extract_table_names(self, query_str: str) -> List[str]:
        """Extract table names from query string."""
        tables = []
        query_lower = query_str.lower()
        
        # Simple extraction - can be improved
        for keyword in ['from', 'join', 'into', 'update']:
            if keyword in query_lower:
                idx = query_lower.index(keyword) + len(keyword)
                # Extract next word as potential table name
                remaining = query_lower[idx:].strip()
                if remaining:
                    table = remaining.split()[0].strip('()"\'`')
                    if table and not table in ['select', 'where', 'inner', 'left', 'right']:
                        tables.append(table)
                        
        return list(set(tables))


def cached_query(
    ttl: Union[int, timedelta] = 300,
    key_prefix: Optional[str] = None,
    invalidate_on: Optional[List[str]] = None
):
    """
    Decorator for caching database query results.
    
    Args:
        ttl: Time to live in seconds or timedelta
        key_prefix: Optional prefix for cache key
        invalidate_on: List of table names that invalidate this cache
    """
    if isinstance(ttl, timedelta):
        ttl = int(ttl.total_seconds())
        
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Initialize query cache if needed
            if not hasattr(wrapper, '_query_cache'):
                wrapper._query_cache = QueryCache()
                await wrapper._query_cache.initialize()
                
            query_cache = wrapper._query_cache
            
            # Generate cache key
            # Try to extract session and skip it in cache key
            cache_args = []
            session = None
            
            for arg in args:
                if isinstance(arg, AsyncSession):
                    session = arg
                elif not hasattr(arg, '__class__') or arg.__class__.__name__ not in ['Session', 'AsyncSession']:
                    cache_args.append(str(arg))
                    
            # Build cache key
            prefix = key_prefix or f"query:{func.__name__}"
            cache_key = cache_key_builder(prefix, *cache_args, **kwargs)
            
            # Try to get from cache
            cached_result = await query_cache.get_cached_result(cache_key)
            if cached_result is not None:
                logger.debug(f"Query cache hit for {cache_key}")
                return cached_result
                
            # Execute query
            result = await func(*args, **kwargs)
            
            # Cache the result
            await query_cache.cache_result(cache_key, result, ttl)
            logger.debug(f"Cached query result for {cache_key} with TTL {ttl}s")
            
            # Store invalidation info
            if invalidate_on:
                wrapper._invalidate_tables = invalidate_on
                
            return result
            
        # Add invalidation method
        async def invalidate(*args, **kwargs):
            if hasattr(wrapper, '_query_cache'):
                prefix = key_prefix or f"query:{func.__name__}"
                cache_key = cache_key_builder(prefix, *args, **kwargs)
                return await wrapper._query_cache.invalidate_query(cache_key)
            return False
            
        wrapper.invalidate = invalidate
        
        return wrapper
    return decorator


class CachedQueryBuilder:
    """
    Builder for creating cached queries with automatic invalidation.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.query_cache = QueryCache()
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize the query builder."""
        if not self._initialized:
            await self.query_cache.initialize()
            self._initialized = True
            
    async def execute_cached(
        self,
        query: Union[Query, Select],
        ttl: int = 300,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute a query with caching."""
        await self.initialize()
        
        # Generate cache key
        cache_key = self.query_cache.generate_query_key(query, params)
        
        # Check cache
        cached = await self.query_cache.get_cached_result(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit for query: {cache_key}")
            return cached
            
        # Execute query
        if params:
            result = await self.session.execute(query, params)
        else:
            result = await self.session.execute(query)
            
        # Process result based on type
        if hasattr(result, 'scalars'):
            data = result.scalars().all()
        elif hasattr(result, 'fetchall'):
            data = result.fetchall()
        else:
            data = result
            
        # Cache result
        await self.query_cache.cache_result(cache_key, data, ttl)
        
        return data
        
    async def invalidate_table_cache(self, table_name: str) -> int:
        """Invalidate all cached queries for a table."""
        await self.initialize()
        count = await self.query_cache.invalidate_table(table_name)
        logger.info(f"Invalidated {count} cached queries for table {table_name}")
        return count


# Cache TTL configurations for different query types
CACHE_TTL_CONFIG = {
    'user_profile': 3600,           # 1 hour
    'assessment_session': 1800,      # 30 minutes
    'business_profile': 3600,        # 1 hour
    'compliance_framework': 7200,    # 2 hours (rarely changes)
    'evidence_item': 1800,           # 30 minutes
    'dashboard_stats': 300,          # 5 minutes
    'report_data': 600,             # 10 minutes
    'framework_list': 86400,        # 24 hours (static data)
    'user_session': 900,            # 15 minutes
    'search_results': 60,           # 1 minute
}


def get_ttl_for_query_type(query_type: str) -> int:
    """Get appropriate TTL for a query type."""
    return CACHE_TTL_CONFIG.get(query_type, 300)  # Default 5 minutes