"""
Performance optimization integration for FastAPI application.

Provides easy integration of all performance features into the main application.
"""

import logging
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
import time

from .cache_manager import get_cache_manager
from .connection_pool import get_pool_manager
from .metrics_collector import get_metrics
from .response_compression import CompressionMiddleware
from .db_optimizer import DatabaseOptimizer

from config.settings import settings

logger = logging.getLogger(__name__)


class PerformanceIntegration:
    """
    Main integration class for performance optimizations.
    """
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.metrics = get_metrics()
        self.cache_manager = None
        self.pool_manager = None
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize all performance components."""
        if self._initialized:
            return
            
        logger.info("Initializing performance optimizations...")
        
        # Initialize connection pools
        self.pool_manager = await get_pool_manager()
        
        # Initialize cache
        self.cache_manager = await get_cache_manager()
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        self._initialized = True
        logger.info("Performance optimizations initialized successfully")
        
    def _setup_middleware(self) -> None:
        """Setup performance-related middleware."""
        
        # Add compression middleware
        if settings.environment != "development":
            self.app.add_middleware(
                CompressionMiddleware,
                minimum_size=1000,
                exclude_paths={"/health", "/metrics", "/docs", "/redoc"}
            )
        else:
            # Use simpler GZip in development
            self.app.add_middleware(GZipMiddleware, minimum_size=1000)
            
        # Add request timing middleware
        @self.app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            """Add X-Process-Time header and track metrics."""
            start_time = time.perf_counter()
            
            # Track request
            self.metrics.increment_counter("http.requests")
            
            # Process request
            response = await call_next(request)
            
            # Calculate process time
            process_time = time.perf_counter() - start_time
            
            # Add header
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            # Track metrics
            self.metrics.record_time(
                f"http.request",
                process_time,
                {
                    "method": request.method,
                    "path": request.url.path,
                    "status": str(response.status_code)
                }
            )
            
            # Log slow requests
            if process_time > settings.slow_request_threshold:
                logger.warning(
                    f"Slow request: {request.method} {request.url.path} "
                    f"took {process_time:.2f}s"
                )
                self.metrics.increment_counter("http.slow_requests")
                
            return response
            
    def _setup_event_handlers(self) -> None:
        """Setup application event handlers."""
        
        @self.app.on_event("startup")
        async def startup_event():
            """Initialize performance features on startup."""
            await self.initialize()
            
            # Log initial stats
            pool_stats = await self.pool_manager.get_pool_stats()
            logger.info(f"Connection pools initialized: {pool_stats}")
            
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Cleanup on shutdown."""
            logger.info("Shutting down performance components...")
            
            # Save metrics summary
            metrics_summary = self.metrics.get_metrics_summary()
            logger.info(f"Final metrics: {metrics_summary}")
            
            # Cleanup
            if self.cache_manager:
                await self.cache_manager.close()
                
            if self.pool_manager:
                await self.pool_manager.cleanup()
                
            logger.info("Performance components shut down successfully")


def setup_performance_optimizations(app: FastAPI) -> PerformanceIntegration:
    """
    Setup all performance optimizations for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        PerformanceIntegration instance
    """
    integration = PerformanceIntegration(app)
    
    # Add performance monitoring endpoints if enabled
    if settings.enable_performance_monitoring:
        from api.v1.performance import router as performance_router
        app.include_router(
            performance_router,
            prefix="/api/v1",
            tags=["Performance"]
        )
        
    return integration


# Database query optimization helpers
def optimize_sqlalchemy_query(query):
    """
    Apply standard optimizations to a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        
    Returns:
        Optimized query
    """
    from sqlalchemy.orm import selectinload, joinedload
    
    # This is a simplified example - actual implementation would
    # analyze the query and apply appropriate optimizations
    
    # Common optimizations:
    # 1. Use selectinload for one-to-many relationships
    # 2. Use joinedload for many-to-one relationships
    # 3. Add query hints for PostgreSQL
    
    return query


# Caching decorators with performance tracking
def cached_endpoint(ttl: int = 300, key_prefix: Optional[str] = None):
    """
    Decorator for caching FastAPI endpoint responses.
    
    Args:
        ttl: Cache time-to-live in seconds
        key_prefix: Optional cache key prefix
    """
    from functools import wraps
    import hashlib
    import json
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache manager
            cache_manager = await get_cache_manager()
            metrics = get_metrics()
            
            # Build cache key
            if key_prefix:
                cache_key = key_prefix
            else:
                cache_key = f"endpoint:{func.__name__}"
                
            # Add request parameters to key
            if args or kwargs:
                params_str = json.dumps(
                    {"args": args, "kwargs": kwargs},
                    sort_keys=True,
                    default=str
                )
                params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
                cache_key = f"{cache_key}:{params_hash}"
                
            # Try to get from cache
            cached = await cache_manager.get(cache_key)
            if cached is not None:
                metrics.increment_counter("cache.endpoint.hit")
                return cached
                
            # Execute function
            metrics.increment_counter("cache.endpoint.miss")
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache_manager.set(cache_key, result, ttl)
            
            return result
            
        return wrapper
    return decorator


# Batch processing utilities
class BatchProcessor:
    """
    Utilities for batch processing to improve performance.
    """
    
    @staticmethod
    async def process_in_batches(
        items: list,
        batch_size: int,
        process_func,
        *args,
        **kwargs
    ):
        """
        Process items in batches to avoid overwhelming the system.
        
        Args:
            items: List of items to process
            batch_size: Size of each batch
            process_func: Async function to process each batch
            *args, **kwargs: Additional arguments for process_func
            
        Returns:
            List of results from all batches
        """
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = await process_func(batch, *args, **kwargs)
            results.extend(batch_results)
            
        return results
        
    @staticmethod
    async def bulk_insert(db_session, models: list, batch_size: int = 100):
        """
        Bulk insert models into database.
        
        Args:
            db_session: Database session
            models: List of model instances
            batch_size: Size of each batch
        """
        from sqlalchemy import insert
        
        for i in range(0, len(models), batch_size):
            batch = models[i:i + batch_size]
            db_session.add_all(batch)
            
            # Flush periodically to avoid memory issues
            if i % (batch_size * 10) == 0:
                await db_session.flush()
                
        await db_session.commit()


# JSON serialization optimization
class OptimizedJSONResponse:
    """
    Optimized JSON response with faster serialization.
    """
    
    @staticmethod
    def serialize(data: Any) -> str:
        """
        Fast JSON serialization using orjson.
        """
        try:
            import orjson
            return orjson.dumps(
                data,
                option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_SERIALIZE_UUID
            ).decode()
        except ImportError:
            import json
            return json.dumps(data, default=str)
            
    @staticmethod
    def deserialize(data: str) -> Any:
        """
        Fast JSON deserialization.
        """
        try:
            import orjson
            return orjson.loads(data)
        except ImportError:
            import json
            return json.loads(data)