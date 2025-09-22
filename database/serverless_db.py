"""
Serverless-optimized database configuration for Vercel deployment.
Provides connection management optimized for serverless functions with:
- Connection pooling suited for serverless
- Automatic connection cleanup
- Health checks and fallbacks
"""

import os
import logging
from typing import Optional, Generator
from contextlib import contextmanager
from sqlalchemy import create_engine, text, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import time

logger = logging.getLogger(__name__)

# Environment detection
IS_VERCEL = os.getenv('VERCEL', '').lower() == '1' or os.getenv('VERCEL_ENV') is not None

class ServerlessDatabase:
    """Database manager optimized for serverless environments."""

    def __init__(self, database_url: str = None):
        """Initialize serverless database connection."""
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")

        # Add serverless-optimized connection parameters
        self.database_url = self._optimize_connection_url(self.database_url)

        self.engine = None
        self.SessionLocal = None
        self._last_health_check = 0
        self._health_check_interval = 30  # seconds

        # Initialize connection
        self._initialize_connection()

    def _optimize_connection_url(self, url: str) -> str:
        """Add serverless-optimized parameters to connection URL."""
        if '?' not in url:
            url += '?'
        else:
            url += '&'

        # Serverless-optimized parameters
        params = [
            'sslmode=require',  # Always use SSL in production
            'connect_timeout=10',  # Quick timeout for serverless
            'options=-c statement_timeout=50000',  # 50 second statement timeout
            'application_name=ruleiq_vercel'
        ]

        return url + '&'.join(params)

    def _initialize_connection(self):
        """Initialize database connection with serverless-optimized settings."""
        try:
            # Use NullPool for serverless to avoid connection pooling issues
            if IS_VERCEL:
                self.engine = create_engine(
                    self.database_url,
                    poolclass=pool.NullPool,  # No connection pooling in serverless
                    echo=False,
                    connect_args={
                        'connect_timeout': 10,
                        'options': '-c statement_timeout=50000'
                    }
                )
            else:
                # Use standard pooling for local development
                self.engine = create_engine(
                    self.database_url,
                    pool_size=2,
                    max_overflow=3,
                    pool_timeout=5,
                    pool_recycle=300,
                    pool_pre_ping=True,
                    echo=False
                )

            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # Test connection
            self._test_connection()
            logger.info("Database connection established successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise

    def _test_connection(self):
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.close()
        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {e}")
            raise

    def health_check(self) -> dict:
        """Perform a health check on the database connection."""
        current_time = time.time()

        # Rate limit health checks
        if current_time - self._last_health_check < self._health_check_interval:
            return {"status": "cached", "message": "Using cached health status"}

        self._last_health_check = current_time

        try:
            start = time.time()
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.close()

            latency = (time.time() - start) * 1000  # Convert to milliseconds

            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "pool_size": getattr(self.engine.pool, 'size', 0) if not IS_VERCEL else 0
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions with automatic cleanup.
        Ensures connections are properly closed in serverless environment.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

            # In serverless, explicitly dispose of the connection
            if IS_VERCEL:
                session.bind.dispose()

    def get_db(self) -> Generator[Session, None, None]:
        """
        Dependency injection for FastAPI.
        Provides a database session for request handling.
        """
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

            # In serverless, explicitly dispose of the connection
            if IS_VERCEL and session.bind:
                session.bind.dispose()

    def close(self):
        """Close database connections and cleanup."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")

    def reset_connection(self):
        """Reset database connection (useful for connection issues)."""
        try:
            self.close()
            self._initialize_connection()
            logger.info("Database connection reset successfully")
        except Exception as e:
            logger.error(f"Failed to reset database connection: {e}")
            raise

# Singleton instance
_db_instance: Optional[ServerlessDatabase] = None

def get_serverless_db() -> ServerlessDatabase:
    """Get or create the serverless database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = ServerlessDatabase()
    return _db_instance

def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    db = get_serverless_db()
    return db.get_db()

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database operations."""
    db = get_serverless_db()
    with db.get_session() as session:
        yield session

def test_database_connection() -> bool:
    """Test if database connection is working."""
    try:
        db = get_serverless_db()
        health = db.health_check()
        return health.get("status") == "healthy"
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

def cleanup_connections():
    """Cleanup all database connections (call at end of serverless function)."""
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None

# Export commonly used functions
__all__ = [
    'ServerlessDatabase',
    'get_serverless_db',
    'get_db_session',
    'get_db_context',
    'test_database_connection',
    'cleanup_connections'
]