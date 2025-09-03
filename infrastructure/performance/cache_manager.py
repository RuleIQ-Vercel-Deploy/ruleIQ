"""
Redis Cache Manager for RuleIQ performance optimization.

Provides efficient caching strategies for frequently accessed data.
"""

import json
import hashlib
import logging
from typing import Any, Optional, Union, Callable, Dict
from datetime import timedelta
from functools import wraps
import redis.asyncio as redis
from redis.asyncio import ConnectionPool
from redis.exceptions import RedisError
from config.settings import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages Redis caching with connection pooling and optimized strategies.
    """
    
    def __init__(self):
        """Initialize cache manager with connection pool."""
        self._pool: Optional[ConnectionPool] = None
        self._redis_client: Optional[redis.Redis] = None
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize Redis connection pool."""
        if self._initialized:
            return
            
        try:
            # Create optimized connection pool
            self._pool = ConnectionPool.from_url(
                settings.redis_url,
                max_connections=settings.redis_max_connections,
                socket_keepalive=settings.redis_socket_keepalive,
                socket_keepalive_options=settings.redis_socket_keepalive_options,
                health_check_interval=30,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                decode_responses=True
            )
            
            self._redis_client = redis.Redis(connection_pool=self._pool)
            
            # Test connection
            await self._redis_client.ping()
            self._initialized = True
            logger.info("Redis cache manager initialized successfully")
            
        except RedisError as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            self._redis_client = None
            self._initialized = False
            
    async def close(self) -> None:
        """Close Redis connections."""
        if self._redis_client:
            await self._redis_client.close()
        if self._pool:
            await self._pool.disconnect()
        self._initialized = False
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._redis_client:
            return None
            
        try:
            value = await self._redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None
            
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        if not self._redis_client:
            return False
            
        try:
            serialized = json.dumps(value, default=str)
            if ttl:
                await self._redis_client.setex(key, ttl, serialized)
            else:
                await self._redis_client.set(key, serialized)
            return True
        except (RedisError, TypeError) as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._redis_client:
            return False
            
        try:
            await self._redis_client.delete(key)
            return True
        except RedisError as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
            
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self._redis_client:
            return 0
            
        try:
            keys = []
            async for key in self._redis_client.scan_iter(pattern):
                keys.append(key)
            
            if keys:
                return await self._redis_client.delete(*keys)
            return 0
        except RedisError as e:
            logger.warning(f"Cache delete pattern error for {pattern}: {e}")
            return 0
            
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._redis_client:
            return False
            
        try:
            return await self._redis_client.exists(key) > 0
        except RedisError as e:
            logger.warning(f"Cache exists error for key {key}: {e}")
            return False
            
    async def ttl(self, key: str) -> Optional[int]:
        """Get TTL for a key."""
        if not self._redis_client:
            return None
            
        try:
            ttl = await self._redis_client.ttl(key)
            return ttl if ttl >= 0 else None
        except RedisError as e:
            logger.warning(f"Cache TTL error for key {key}: {e}")
            return None
            
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for a key."""
        if not self._redis_client:
            return False
            
        try:
            return await self._redis_client.expire(key, ttl)
        except RedisError as e:
            logger.warning(f"Cache expire error for key {key}: {e}")
            return False
            
    # Batch operations for performance
    async def mget(self, keys: list[str]) -> Dict[str, Any]:
        """Get multiple values from cache."""
        if not self._redis_client:
            return {}
            
        try:
            values = await self._redis_client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    try:
                        result[key] = json.loads(value)
                    except json.JSONDecodeError:
                        pass
            return result
        except RedisError as e:
            logger.warning(f"Cache mget error: {e}")
            return {}
            
    async def mset(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache."""
        if not self._redis_client:
            return False
            
        try:
            # Serialize all values
            serialized_mapping = {
                k: json.dumps(v, default=str) for k, v in mapping.items()
            }
            
            if ttl:
                # Use pipeline for atomic operations with TTL
                pipe = self._redis_client.pipeline()
                for key, value in serialized_mapping.items():
                    pipe.setex(key, ttl, value)
                await pipe.execute()
            else:
                await self._redis_client.mset(serialized_mapping)
            return True
        except (RedisError, TypeError) as e:
            logger.warning(f"Cache mset error: {e}")
            return False


def cache_key_builder(
    prefix: str,
    *args,
    **kwargs
) -> str:
    """
    Build a cache key from prefix and parameters.
    
    Args:
        prefix: Cache key prefix
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
        
    Returns:
        Formatted cache key
    """
    parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        if arg is not None:
            parts.append(str(arg))
    
    # Add keyword arguments
    if kwargs:
        # Sort kwargs for consistent keys
        sorted_kwargs = sorted(kwargs.items())
        for key, value in sorted_kwargs:
            if value is not None:
                parts.append(f"{key}:{value}")
    
    # Create key with separator
    key = ":".join(parts)
    
    # Hash if too long
    if len(key) > 200:
        hash_suffix = hashlib.md5(key.encode()).hexdigest()[:8]
        key = f"{key[:150]}:{hash_suffix}"
    
    return key


def cached(
    ttl: Union[int, timedelta] = 3600,
    prefix: Optional[str] = None,
    key_builder: Optional[Callable] = None
):
    """
    Decorator for caching async function results.
    
    Args:
        ttl: Time to live in seconds or timedelta
        prefix: Cache key prefix (defaults to function name)
        key_builder: Custom key builder function
    """
    if isinstance(ttl, timedelta):
        ttl = int(ttl.total_seconds())
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip caching if disabled
            if not hasattr(wrapper, '_cache_manager'):
                wrapper._cache_manager = CacheManager()
                await wrapper._cache_manager.initialize()
            
            cache_manager = wrapper._cache_manager
            
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                func_prefix = prefix or f"func:{func.__name__}"
                # Skip 'self' for instance methods
                cache_args = args[1:] if args and hasattr(args[0], '__class__') else args
                cache_key = cache_key_builder(func_prefix, *cache_args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {cache_key} with TTL {ttl}s")
            
            return result
        
        # Add cache control methods
        wrapper.invalidate = lambda *args, **kwargs: _invalidate_cache(
            prefix or f"func:{func.__name__}", *args, **kwargs
        )
        
        return wrapper
    return decorator


async def _invalidate_cache(prefix: str, *args, **kwargs) -> bool:
    """Invalidate cached result for specific arguments."""
    cache_manager = CacheManager()
    await cache_manager.initialize()
    
    cache_key = cache_key_builder(prefix, *args, **kwargs)
    return await cache_manager.delete(cache_key)


# Singleton instance
_cache_manager_instance: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """Get or create cache manager singleton."""
    global _cache_manager_instance
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager()
        await _cache_manager_instance.initialize()
    return _cache_manager_instance