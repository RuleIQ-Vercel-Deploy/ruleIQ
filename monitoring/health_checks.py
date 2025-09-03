"""
Health Check System for RuleIQ

Provides comprehensive health checking for all system components including:
- Database connectivity
- Redis cache
- External APIs
- File system
- Background tasks
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from database.db_setup import get_async_db, get_engine_info
from config.cache import get_cache_manager

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentType(str, Enum):
    """System component types."""
    DATABASE = "database"
    CACHE = "cache"
    FILESYSTEM = "filesystem"
    EXTERNAL_API = "external_api"
    BACKGROUND_TASK = "background_task"
    QUEUE = "queue"
    AI_SERVICE = "ai_service"


@dataclass
class ComponentHealth:
    """Health status of a system component."""
    name: str
    type: ComponentType
    status: HealthStatus
    message: str
    response_time_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    last_check: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "message": self.message,
            "response_time_ms": self.response_time_ms,
            "metadata": self.metadata or {},
            "last_check": self.last_check.isoformat() if self.last_check else None
        }


@dataclass
class SystemHealth:
    """Overall system health status."""
    status: HealthStatus
    message: str
    components: List[ComponentHealth]
    timestamp: datetime
    version: str
    environment: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status,
            "message": self.message,
            "components": [c.to_dict() for c in self.components],
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "environment": self.environment
        }


class HealthChecker:
    """Comprehensive health checking system."""
    
    def __init__(self):
        """Initialize health checker."""
        self.last_check_results: Dict[str, ComponentHealth] = {}
        self.check_interval = 30  # seconds
        self.last_full_check = datetime.now(timezone.utc)
    
    async def check_database_health(self, db: AsyncSession) -> ComponentHealth:
        """Check database connectivity and performance."""
        start_time = time.time()
        
        try:
            # Simple query to test connectivity
            result = await db.execute(text("SELECT 1"))
            result.scalar()
            
            # Get connection pool stats
            engine_info = get_engine_info()
            
            response_time = (time.time() - start_time) * 1000
            
            # Check pool utilization
            pool_size = engine_info.get("async_pool_size", 0)
            checked_out = engine_info.get("async_pool_checked_out", 0)
            utilization = (checked_out / pool_size * 100) if pool_size > 0 else 0
            
            # Determine status based on utilization
            if utilization > 90:
                status = HealthStatus.DEGRADED
                message = f"High connection pool utilization: {utilization:.1f}%"
            elif response_time > 1000:
                status = HealthStatus.DEGRADED
                message = f"Slow database response: {response_time:.0f}ms"
            else:
                status = HealthStatus.HEALTHY
                message = "Database operational"
            
            return ComponentHealth(
                name="PostgreSQL Database",
                type=ComponentType.DATABASE,
                status=status,
                message=message,
                response_time_ms=response_time,
                metadata={
                    "pool_size": pool_size,
                    "connections_active": checked_out,
                    "utilization_percent": utilization
                },
                last_check=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return ComponentHealth(
                name="PostgreSQL Database",
                type=ComponentType.DATABASE,
                status=HealthStatus.UNHEALTHY,
                message=f"Connection failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.now(timezone.utc)
            )
    
    async def check_redis_health(self) -> ComponentHealth:
        """Check Redis cache connectivity and performance."""
        start_time = time.time()
        
        try:
            cache_manager = await get_cache_manager()
            if not cache_manager:
                return ComponentHealth(
                    name="Redis Cache",
                    type=ComponentType.CACHE,
                    status=HealthStatus.UNHEALTHY,
                    message="Cache manager not available",
                    last_check=datetime.now(timezone.utc)
                )
            
            # Test connectivity with ping
            await cache_manager.redis_client.ping()
            
            # Get Redis info
            info = await cache_manager.redis_client.info()
            
            response_time = (time.time() - start_time) * 1000
            
            # Check memory usage
            used_memory = info.get("used_memory", 0)
            max_memory = info.get("maxmemory", 0)
            memory_usage = (used_memory / max_memory * 100) if max_memory > 0 else 0
            
            # Determine status
            if memory_usage > 90:
                status = HealthStatus.DEGRADED
                message = f"High memory usage: {memory_usage:.1f}%"
            elif response_time > 100:
                status = HealthStatus.DEGRADED
                message = f"Slow cache response: {response_time:.0f}ms"
            else:
                status = HealthStatus.HEALTHY
                message = "Cache operational"
            
            return ComponentHealth(
                name="Redis Cache",
                type=ComponentType.CACHE,
                status=status,
                message=message,
                response_time_ms=response_time,
                metadata={
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_mb": used_memory / 1024 / 1024,
                    "memory_usage_percent": memory_usage,
                    "uptime_days": info.get("uptime_in_days", 0)
                },
                last_check=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return ComponentHealth(
                name="Redis Cache",
                type=ComponentType.CACHE,
                status=HealthStatus.UNHEALTHY,
                message=f"Connection failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.now(timezone.utc)
            )
    
    async def check_filesystem_health(self) -> ComponentHealth:
        """Check filesystem availability and disk space."""
        start_time = time.time()
        
        try:
            # Check if required directories exist and are writable
            directories_to_check = [
                settings.upload_directory,
                settings.data_dir,
                settings.report_directory,
                os.path.dirname(settings.log_file_path) if settings.log_file_enabled else None
            ]
            
            for directory in directories_to_check:
                if directory and not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
            
            # Check disk space
            import shutil
            total, used, free = shutil.disk_usage("/")
            disk_usage_percent = (used / total) * 100
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on disk usage
            if disk_usage_percent > settings.disk_critical_threshold:
                status = HealthStatus.UNHEALTHY
                message = f"Critical disk usage: {disk_usage_percent:.1f}%"
            elif disk_usage_percent > settings.disk_warning_threshold:
                status = HealthStatus.DEGRADED
                message = f"High disk usage: {disk_usage_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = "Filesystem healthy"
            
            return ComponentHealth(
                name="Filesystem",
                type=ComponentType.FILESYSTEM,
                status=status,
                message=message,
                response_time_ms=response_time,
                metadata={
                    "disk_usage_percent": disk_usage_percent,
                    "free_space_gb": free / (1024**3),
                    "total_space_gb": total / (1024**3)
                },
                last_check=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Filesystem health check failed: {e}")
            return ComponentHealth(
                name="Filesystem",
                type=ComponentType.FILESYSTEM,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.now(timezone.utc)
            )
    
    async def check_google_ai_health(self) -> ComponentHealth:
        """Check Google AI API connectivity."""
        start_time = time.time()
        
        if not settings.google_api_key or settings.google_api_key == "test-google-api-key":
            return ComponentHealth(
                name="Google AI",
                type=ComponentType.AI_SERVICE,
                status=HealthStatus.UNKNOWN,
                message="API key not configured",
                last_check=datetime.now(timezone.utc)
            )
        
        try:
            import google.generativeai as genai
            
            # Configure the API
            genai.configure(api_key=settings.google_api_key)
            
            # Try to list models as a health check
            models = genai.list_models()
            model_count = sum(1 for _ in models)
            
            response_time = (time.time() - start_time) * 1000
            
            if response_time > 2000:
                status = HealthStatus.DEGRADED
                message = f"Slow API response: {response_time:.0f}ms"
            else:
                status = HealthStatus.HEALTHY
                message = f"API operational, {model_count} models available"
            
            return ComponentHealth(
                name="Google AI",
                type=ComponentType.AI_SERVICE,
                status=status,
                message=message,
                response_time_ms=response_time,
                metadata={
                    "model": settings.gemini_model,
                    "available_models": model_count
                },
                last_check=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Google AI health check failed: {e}")
            return ComponentHealth(
                name="Google AI",
                type=ComponentType.AI_SERVICE,
                status=HealthStatus.UNHEALTHY,
                message=f"API check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.now(timezone.utc)
            )
    
    async def check_external_apis_health(self) -> List[ComponentHealth]:
        """Check connectivity to external APIs."""
        results = []
        
        # Define external APIs to check
        external_apis = [
            {
                "name": "Google OAuth",
                "url": "https://accounts.google.com/.well-known/openid-configuration",
                "timeout": 5
            },
            {
                "name": "Stripe API",
                "url": "https://api.stripe.com/v1/",
                "timeout": 5,
                "enabled": bool(settings.stripe_secret_key)
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for api in external_apis:
                if not api.get("enabled", True):
                    continue
                
                start_time = time.time()
                
                try:
                    async with session.get(
                        api["url"],
                        timeout=aiohttp.ClientTimeout(total=api["timeout"])
                    ) as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status < 400:
                            status = HealthStatus.HEALTHY
                            message = f"API responding (HTTP {response.status})"
                        else:
                            status = HealthStatus.DEGRADED
                            message = f"API returned error (HTTP {response.status})"
                        
                        results.append(ComponentHealth(
                            name=api["name"],
                            type=ComponentType.EXTERNAL_API,
                            status=status,
                            message=message,
                            response_time_ms=response_time,
                            metadata={"http_status": response.status},
                            last_check=datetime.now(timezone.utc)
                        ))
                        
                except asyncio.TimeoutError:
                    results.append(ComponentHealth(
                        name=api["name"],
                        type=ComponentType.EXTERNAL_API,
                        status=HealthStatus.DEGRADED,
                        message="Request timeout",
                        response_time_ms=api["timeout"] * 1000,
                        last_check=datetime.now(timezone.utc)
                    ))
                    
                except Exception as e:
                    results.append(ComponentHealth(
                        name=api["name"],
                        type=ComponentType.EXTERNAL_API,
                        status=HealthStatus.UNHEALTHY,
                        message=f"Connection failed: {str(e)}",
                        response_time_ms=(time.time() - start_time) * 1000,
                        last_check=datetime.now(timezone.utc)
                    ))
        
        return results
    
    async def check_all_components(self) -> SystemHealth:
        """Run all health checks and return system health."""
        components = []
        
        # Check database
        try:
            async for db in get_async_db():
                db_health = await self.check_database_health(db)
                components.append(db_health)
                break
        except Exception as e:
            logger.error(f"Failed to check database health: {e}")
            components.append(ComponentHealth(
                name="PostgreSQL Database",
                type=ComponentType.DATABASE,
                status=HealthStatus.UNKNOWN,
                message=f"Check failed: {str(e)}",
                last_check=datetime.now(timezone.utc)
            ))
        
        # Check Redis
        redis_health = await self.check_redis_health()
        components.append(redis_health)
        
        # Check filesystem
        filesystem_health = await self.check_filesystem_health()
        components.append(filesystem_health)
        
        # Check Google AI
        if settings.ai_policy_generation_enabled:
            ai_health = await self.check_google_ai_health()
            components.append(ai_health)
        
        # Check external APIs
        external_api_results = await self.check_external_apis_health()
        components.extend(external_api_results)
        
        # Store results
        for component in components:
            self.last_check_results[component.name] = component
        
        # Determine overall system status
        unhealthy_count = sum(1 for c in components if c.status == HealthStatus.UNHEALTHY)
        degraded_count = sum(1 for c in components if c.status == HealthStatus.DEGRADED)
        
        if unhealthy_count > 0:
            status = HealthStatus.UNHEALTHY
            message = f"{unhealthy_count} component(s) unhealthy"
        elif degraded_count > 0:
            status = HealthStatus.DEGRADED
            message = f"{degraded_count} component(s) degraded"
        else:
            status = HealthStatus.HEALTHY
            message = "All systems operational"
        
        self.last_full_check = datetime.now(timezone.utc)
        
        return SystemHealth(
            status=status,
            message=message,
            components=components,
            timestamp=self.last_full_check,
            version=settings.version,
            environment=settings.environment
        )
    
    async def get_quick_health(self) -> Dict[str, Any]:
        """Get a quick health status without running full checks."""
        # Use cached results if recent
        time_since_check = (datetime.now(timezone.utc) - self.last_full_check).total_seconds()
        
        if time_since_check > self.check_interval:
            # Run full check if cached results are stale
            system_health = await self.check_all_components()
            return system_health.to_dict()
        
        # Return cached results
        unhealthy_count = sum(
            1 for c in self.last_check_results.values() 
            if c.status == HealthStatus.UNHEALTHY
        )
        degraded_count = sum(
            1 for c in self.last_check_results.values() 
            if c.status == HealthStatus.DEGRADED
        )
        
        if unhealthy_count > 0:
            status = HealthStatus.UNHEALTHY
            message = f"{unhealthy_count} component(s) unhealthy"
        elif degraded_count > 0:
            status = HealthStatus.DEGRADED
            message = f"{degraded_count} component(s) degraded"
        else:
            status = HealthStatus.HEALTHY
            message = "All systems operational"
        
        return {
            "status": status,
            "message": message,
            "last_check": self.last_full_check.isoformat(),
            "time_since_check": time_since_check,
            "cached": True
        }


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get or create the global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


async def run_health_check_loop(interval: int = 30) -> None:
    """Run health checks in a background loop."""
    checker = get_health_checker()
    
    while True:
        try:
            await checker.check_all_components()
            logger.debug("Health check completed successfully")
        except Exception as e:
            logger.error(f"Error in health check loop: {e}")
        
        await asyncio.sleep(interval)