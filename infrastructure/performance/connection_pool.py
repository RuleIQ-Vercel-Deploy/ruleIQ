"""
Connection pool management for database and Redis connections.

Optimizes connection usage and prevents connection exhaustion.
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import psutil

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool, StaticPool
from sqlalchemy import event, text
import redis.asyncio as redis
from redis.asyncio import ConnectionPool as RedisPool

from config.settings import settings

logger = logging.getLogger(__name__)


class ConnectionPoolManager:
    """
    Manages database and Redis connection pools with monitoring.
    """
    
    def __init__(self):
        self.db_engine: Optional[AsyncEngine] = None
        self.redis_pool: Optional[RedisPool] = None
        self.session_factory: Optional[sessionmaker] = None
        self._pool_stats: Dict[str, Any] = {}
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize all connection pools."""
        if self._initialized:
            return
            
        try:
            # Initialize database pool
            await self._init_database_pool()
            
            # Initialize Redis pool
            await self._init_redis_pool()
            
            self._initialized = True
            logger.info("Connection pools initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize connection pools: {e}")
            raise
            
    async def _init_database_pool(self) -> None:
        """Initialize optimized database connection pool."""
        
        # Determine optimal pool settings based on system resources
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Calculate pool size based on resources
        base_pool_size = settings.database_pool_size
        max_overflow = settings.database_max_overflow
        
        # Adjust based on system resources
        if cpu_count >= 8 and memory_gb >= 16:
            pool_size = min(base_pool_size * 2, 50)
            max_overflow = min(max_overflow * 2, 100)
        elif cpu_count >= 4 and memory_gb >= 8:
            pool_size = min(int(base_pool_size * 1.5), 30)
            max_overflow = min(int(max_overflow * 1.5), 60)
        else:
            pool_size = base_pool_size
            
        logger.info(f"Configuring DB pool: size={pool_size}, overflow={max_overflow}")
        
        # Create engine with optimized settings
        self.db_engine = create_async_engine(
            settings.database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=settings.database_pool_timeout,
            pool_recycle=settings.database_pool_recycle,
            pool_pre_ping=True,  # Verify connections before use
            echo_pool=settings.debug,  # Log pool checkouts/checkins in debug mode
            connect_args={
                "server_settings": {
                    "application_name": "ruleiq_optimized",
                    "jit": "off",
                    "shared_preload_libraries": "pg_stat_statements",
                },
                "command_timeout": 60,
                "connection_timeout": 10,
            }
        )
        
        # Create session factory
        self.session_factory = sessionmaker(
            self.db_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Add pool event listeners for monitoring
        self._setup_pool_events()
        
        # Test connection
        async with self.db_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            
    def _setup_pool_events(self) -> None:
        """Setup event listeners for pool monitoring."""
        
        @event.listens_for(self.db_engine.sync_engine.pool, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Log new connections."""
            connection_record.info['connect_time'] = datetime.utcnow()
            logger.debug("New database connection established")
            
        @event.listens_for(self.db_engine.sync_engine.pool, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            """Track connection checkouts."""
            self._pool_stats['last_checkout'] = datetime.utcnow()
            self._pool_stats['active_connections'] = \
                self._pool_stats.get('active_connections', 0) + 1
                
        @event.listens_for(self.db_engine.sync_engine.pool, "checkin")
        def receive_checkin(dbapi_conn, connection_record):
            """Track connection checkins."""
            self._pool_stats['last_checkin'] = datetime.utcnow()
            self._pool_stats['active_connections'] = \
                max(0, self._pool_stats.get('active_connections', 1) - 1)
                
    async def _init_redis_pool(self) -> None:
        """Initialize optimized Redis connection pool."""
        
        # Calculate optimal pool size
        max_connections = settings.redis_max_connections
        
        # Create Redis pool with optimized settings
        self.redis_pool = RedisPool.from_url(
            settings.redis_url,
            max_connections=max_connections,
            socket_keepalive=True,
            socket_keepalive_options={
                1: 1,  # TCP_KEEPIDLE
                2: 1,  # TCP_KEEPINTVL
                3: 3,  # TCP_KEEPCNT
            },
            health_check_interval=30,
            retry_on_timeout=True,
            socket_connect_timeout=5,
            decode_responses=True
        )
        
        # Test connection
        redis_client = redis.Redis(connection_pool=self.redis_pool)
        await redis_client.ping()
        await redis_client.close()
        
    @asynccontextmanager
    async def get_db_session(self):
        """Get a database session from the pool."""
        if not self.session_factory:
            await self.initialize()
            
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
                
    @asynccontextmanager
    async def get_redis_client(self):
        """Get a Redis client from the pool."""
        if not self.redis_pool:
            await self.initialize()
            
        client = redis.Redis(connection_pool=self.redis_pool)
        try:
            yield client
        finally:
            await client.close()
            
    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get current pool statistics."""
        stats = {
            'timestamp': datetime.utcnow().isoformat(),
            'database': {},
            'redis': {},
            'system': {}
        }
        
        # Database pool stats
        if self.db_engine:
            pool = self.db_engine.pool
            stats['database'] = {
                'size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'total': pool.total(),
                **self._pool_stats
            }
            
        # Redis pool stats
        if self.redis_pool:
            stats['redis'] = {
                'created_connections': self.redis_pool.created_connections,
                'available_connections': len(self.redis_pool._available_connections),
                'in_use_connections': len(self.redis_pool._in_use_connections),
                'max_connections': self.redis_pool.max_connections
            }
            
        # System resource stats
        stats['system'] = {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'connections': len(psutil.net_connections())
        }
        
        return stats
        
    async def health_check(self) -> Dict[str, bool]:
        """Perform health check on all pools."""
        health = {
            'database': False,
            'redis': False
        }
        
        # Check database
        try:
            async with self.get_db_session() as session:
                await session.execute(text("SELECT 1"))
            health['database'] = True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            
        # Check Redis
        try:
            async with self.get_redis_client() as client:
                await client.ping()
            health['redis'] = True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            
        return health
        
    async def optimize_pools(self) -> Dict[str, Any]:
        """Dynamically optimize pool sizes based on usage."""
        stats = await self.get_pool_stats()
        optimizations = {}
        
        # Check database pool usage
        if self.db_engine:
            db_stats = stats['database']
            utilization = db_stats['checked_out'] / db_stats['size'] if db_stats['size'] > 0 else 0
            
            if utilization > 0.8:
                # High utilization - consider increasing pool
                optimizations['database'] = {
                    'action': 'increase_pool',
                    'reason': f'High utilization: {utilization:.1%}',
                    'current_size': db_stats['size'],
                    'recommended_size': min(db_stats['size'] + 5, 100)
                }
            elif utilization < 0.2 and db_stats['size'] > 10:
                # Low utilization - consider decreasing pool
                optimizations['database'] = {
                    'action': 'decrease_pool',
                    'reason': f'Low utilization: {utilization:.1%}',
                    'current_size': db_stats['size'],
                    'recommended_size': max(db_stats['size'] - 5, 10)
                }
                
        # Check Redis pool usage
        if self.redis_pool:
            redis_stats = stats['redis']
            redis_utilization = (
                redis_stats['in_use_connections'] / redis_stats['max_connections']
                if redis_stats['max_connections'] > 0 else 0
            )
            
            if redis_utilization > 0.8:
                optimizations['redis'] = {
                    'action': 'increase_pool',
                    'reason': f'High utilization: {redis_utilization:.1%}',
                    'current_size': redis_stats['max_connections'],
                    'recommended_size': min(redis_stats['max_connections'] + 10, 100)
                }
                
        return optimizations
        
    async def cleanup(self) -> None:
        """Cleanup and close all pools."""
        if self.db_engine:
            await self.db_engine.dispose()
            
        if self.redis_pool:
            await self.redis_pool.disconnect()
            
        self._initialized = False
        logger.info("Connection pools cleaned up")


# Singleton instance
_pool_manager: Optional[ConnectionPoolManager] = None


async def get_pool_manager() -> ConnectionPoolManager:
    """Get or create the pool manager singleton."""
    global _pool_manager
    if _pool_manager is None:
        _pool_manager = ConnectionPoolManager()
        await _pool_manager.initialize()
    return _pool_manager