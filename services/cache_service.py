"""
Cache Service for ruleIQ

Provides a unified caching interface using Redis with fallback to in-memory cache.
Supports TTL, automatic serialization/deserialization, and proper error handling.
"""

import json
import logging
import asyncio
from typing import Any, Optional, Dict, Union
from datetime import timedelta

import redis.asyncio as redis
from config.settings import settings

logger = logging.getLogger(__name__)


class CacheService:
    """
    Unified cache service with Redis backend and in-memory fallback

    Features:
    - Automatic JSON serialization/deserialization
    - TTL support
    - Graceful fallback to in-memory cache when Redis unavailable
    - Connection pooling and health monitoring
    """

    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None
        self._redis_available = (
            None  # None = not tested, True/False = available/unavailable
        )
        self._memory_cache: Dict[str, Dict[str, Any]] = {}  # Fallback in-memory cache
        self._max_memory_items = 1000  # Prevent memory bloat

    async def _get_redis_client(self) -> Optional[redis.Redis]:
        """Get or create Redis client with connection testing."""
        if self._redis_available is False:
            return None

        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(
                    settings.redis_url, decode_responses=True
                )
                # Test the connection
                await self._redis_client.ping()
                self._redis_available = True
                logger.info("Cache service connected to Redis")
            except Exception as e:
                logger.warning(
                    f"Redis unavailable, using in-memory cache fallback: {e}"
                )
                self._redis_available = False
                self._redis_client = None
                return None

        return self._redis_client

    async def set(
        self, key: str, value: Any, ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """
        Set a value in cache with optional TTL

        Args:
            key: Cache key
            value: Value to cache (automatically serialized to JSON)
            ttl: Time to live in seconds or timedelta

        Returns:
            bool: Success status
        """
        try:
            # Convert timedelta to seconds
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())

            # Serialize value
            serialized_value = (
                json.dumps(value) if not isinstance(value, str) else value
            )

            # Try Redis first
            redis_client = await self._get_redis_client()
            if redis_client:
                if ttl:
                    await redis_client.setex(key, ttl, serialized_value)
                else:
                    await redis_client.set(key, serialized_value)
                return True

            # Fallback to memory cache
            import time

            cache_entry = {
                "value": serialized_value,
                "expires_at": time.time() + ttl if ttl else None,
            }

            # Prevent memory bloat
            if len(self._memory_cache) >= self._max_memory_items:
                # Remove oldest entries
                oldest_keys = list(self._memory_cache.keys())[:100]
                for old_key in oldest_keys:
                    del self._memory_cache[old_key]

            self._memory_cache[key] = cache_entry
            return True

        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        try:
            # Try Redis first
            redis_client = await self._get_redis_client()
            if redis_client:
                value = await redis_client.get(key)
                if value:
                    # Try to deserialize JSON, fallback to raw string
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value
                return None

            # Fallback to memory cache
            import time

            cache_entry = self._memory_cache.get(key)
            if not cache_entry:
                return None

            # Check expiration
            if cache_entry["expires_at"] and time.time() > cache_entry["expires_at"]:
                del self._memory_cache[key]
                return None

            # Deserialize value
            value = cache_entry["value"]
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """
        Delete a key from cache

        Args:
            key: Cache key to delete

        Returns:
            bool: Success status
        """
        try:
            success = False

            # Delete from Redis
            redis_client = await self._get_redis_client()
            if redis_client:
                result = await redis_client.delete(key)
                success = result > 0

            # Delete from memory cache
            if key in self._memory_cache:
                del self._memory_cache[key]
                success = True

            return success

        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache

        Args:
            key: Cache key

        Returns:
            bool: True if key exists and not expired
        """
        try:
            # Check Redis first
            redis_client = await self._get_redis_client()
            if redis_client:
                return await redis_client.exists(key) > 0

            # Check memory cache
            import time

            cache_entry = self._memory_cache.get(key)
            if not cache_entry:
                return False

            # Check expiration
            if cache_entry["expires_at"] and time.time() > cache_entry["expires_at"]:
                del self._memory_cache[key]
                return False

            return True

        except Exception as e:
            logger.error(f"Failed to check cache key {key}: {e}")
            return False

    async def clear(self, pattern: Optional[str] = None) -> bool:
        """
        Clear cache entries matching pattern

        Args:
            pattern: Optional pattern to match keys (e.g., "user:*")
                    If None, clears all cache

        Returns:
            bool: Success status
        """
        try:
            # Clear Redis
            redis_client = await self._get_redis_client()
            if redis_client:
                if pattern:
                    keys = await redis_client.keys(pattern)
                    if keys:
                        await redis_client.delete(*keys)
                else:
                    await redis_client.flushdb()

            # Clear memory cache
            if pattern:
                # Simple pattern matching for memory cache
                keys_to_delete = [
                    key
                    for key in self._memory_cache.keys()
                    if pattern.replace("*", "") in key
                ]
                for key in keys_to_delete:
                    del self._memory_cache[key]
            else:
                self._memory_cache.clear()

            return True

        except Exception as e:
            logger.error(f"Failed to clear cache with pattern {pattern}: {e}")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """
        Get cache service health status

        Returns:
            Dict with health information
        """
        try:
            redis_status = "unavailable"
            redis_client = await self._get_redis_client()
            if redis_client:
                await redis_client.ping()
                redis_status = "connected"

            return {
                "redis_status": redis_status,
                "memory_cache_entries": len(self._memory_cache),
                "max_memory_entries": self._max_memory_items,
                "fallback_active": self._redis_available is False,
            }

        except Exception as e:
            logger.error(f"Failed to get cache health status: {e}")
            return {
                "redis_status": "error",
                "memory_cache_entries": len(self._memory_cache),
                "error": str(e),
            }

    async def cleanup_expired(self) -> int:
        """
        Clean up expired entries from memory cache

        Returns:
            int: Number of entries cleaned up
        """
        try:
            import time

            current_time = time.time()
            expired_keys = []

            for key, entry in self._memory_cache.items():
                if entry["expires_at"] and current_time > entry["expires_at"]:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._memory_cache[key]

            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

            return len(expired_keys)

        except Exception as e:
            logger.error(f"Failed to cleanup expired cache entries: {e}")
            return 0


# Global service instance
_cache_service = None


async def get_cache_service() -> CacheService:
    """Get or create the cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


# Helper functions for backwards compatibility and ease of use
async def cache_get(key: str) -> Optional[Any]:
    """Helper function to get from cache"""
    service = await get_cache_service()
    return await service.get(key)


async def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Helper function to set cache"""
    service = await get_cache_service()
    return await service.set(key, value, ttl)


async def cache_delete(key: str) -> bool:
    """Helper function to delete from cache"""
    service = await get_cache_service()
    return await service.delete(key)
