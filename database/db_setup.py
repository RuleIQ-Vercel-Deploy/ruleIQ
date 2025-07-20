"""
Database setup for ruleIQ, including synchronous and asynchronous
configurations. Provides comprehensive database initialization and
management utilities.
"""

import os
import logging
from typing import AsyncGenerator, Dict, Any
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, text, MetaData, Engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Load environment variables
# Priority order: .env.local (dev) > .env (production) > system environment
load_dotenv(".env.local", override=True)  # Local development takes precedence
load_dotenv(".env", override=False)  # Production config as fallback

# Configure logging
logger = logging.getLogger(__name__)

# --- Global variables for engines and session makers (initialized lazily) ---
_ENGINE: Engine | None = None
_SESSION_LOCAL: sessionmaker[Session] | None = None
_ASYNC_ENGINE: AsyncEngine | None = None
_ASYNC_SESSION_LOCAL: async_sessionmaker[AsyncSession] | None = None

# Define a naming convention for database constraints
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Create a metadata object with the naming convention
metadata = MetaData(naming_convention=naming_convention)

# Define the base class for declarative models
Base = declarative_base(metadata=metadata)


class DatabaseConfig:
    """Database configuration class for managing connection settings."""
    
    @staticmethod
    def validate_environment() -> None:
        """Validate that required environment variables are set."""
        required_vars = ["DATABASE_URL"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            error_msg = (
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please copy env.template to .env.local and configure the variables."
            )
            logger.error(error_msg)
            raise OSError(error_msg)
        
        # Log configuration source
        if os.path.exists(".env.local"):
            logger.info("Loaded configuration from .env.local")
        elif os.path.exists(".env"):
            logger.info("Loaded configuration from .env")
        else:
            logger.info("Using system environment variables")
    
    @staticmethod
    def get_database_urls() -> tuple[str, str, str]:
        """
        Retrieves and processes DATABASE_URL from environment variables.
        Returns tuple of (original_url, sync_url, async_url)
        """
        # Validate environment first
        DatabaseConfig.validate_environment()
        
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            error_msg = "DATABASE_URL environment variable not set. Please set it in your .env file or environment."
            logger.error(error_msg)
            raise OSError(error_msg)

        # Log database connection info (without password)
        safe_url = db_url.split('@')[1] if '@' in db_url else db_url
        logger.info(f"Connecting to database: {safe_url}")

        # Derive SYNC_DATABASE_URL
        sync_db_url = db_url
        if "+asyncpg" in sync_db_url:  # If it's an asyncpg URL, convert to psycopg2 for sync
            sync_db_url = sync_db_url.replace("+asyncpg", "+psycopg2")
        elif (
            "postgresql://" in sync_db_url and "+psycopg2" not in sync_db_url
        ):  # If it's generic, assume psycopg2
            sync_db_url = sync_db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

        # Derive ASYNC_DATABASE_URL
        async_db_url = db_url
        if "+asyncpg" not in async_db_url:
            # Attempt to convert to asyncpg if it's not already
            async_db_url_candidate = async_db_url.replace("+psycopg2", "+asyncpg")
            if "postgresql://" in async_db_url_candidate and "+asyncpg" not in async_db_url_candidate:
                async_db_url = async_db_url_candidate.replace(
                    "postgresql://", "postgresql+asyncpg://", 1
                )
            elif "+asyncpg" in async_db_url_candidate:
                async_db_url = async_db_url_candidate
            # If it's a generic postgresql:// URL without a specified sync driver, default to making it asyncpg
            elif (
                "postgresql://" in async_db_url
                and "+psycopg2" not in async_db_url
                and "+asyncpg" not in async_db_url
            ):
                async_db_url = async_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
            # Remove sslmode from async_db_url to avoid conflicts with connect_args
            if "sslmode=require" in async_db_url:
                # A more robust way to remove the parameter
                from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
                parts = urlparse(async_db_url)
                query_params = parse_qs(parts.query)
                query_params.pop('sslmode', None)
                query_params.pop('channel_binding', None)
                new_query = urlencode(query_params, doseq=True)
                async_db_url = urlunparse(parts._replace(query=new_query))
    
            return db_url, sync_db_url, async_db_url

    @staticmethod
    def get_engine_kwargs(is_async: bool = False) -> Dict[str, Any]:
        """Get optimized engine configuration based on sync/async mode."""
        try:
            base_kwargs = {
                "echo": os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true",
                "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
                "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
                "pool_pre_ping": True,
                "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "1800")),
                "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
            }
        except ValueError as e:
            logger.error(f"Invalid database configuration value: {e}")
            raise ValueError(f"Invalid database configuration: {e}")

        if is_async:
            async_kwargs = {
                **base_kwargs,
                "pool_reset_on_return": "commit",
            }
            
            # Handle SSL configuration for asyncpg explicitly
            db_url = os.getenv("DATABASE_URL", "")
            connect_args = {
                "server_settings": {
                    "jit": "off",
                    "application_name": "ruleIQ_backend",
                }
            }
            if "sslmode=require" in db_url:
                connect_args["ssl"] = True
            
            async_kwargs["connect_args"] = connect_args
            return async_kwargs
        else:
            # Sync engine configuration
            sync_kwargs = {
                **base_kwargs,
                "connect_args": {
                    "keepalives": 1,
                    "keepalives_idle": 30,
                    "keepalives_interval": 10,
                    "keepalives_count": 5,
                    "connect_timeout": 10,
                },
            }
            return sync_kwargs


def _init_sync_db():
    """Initializes synchronous database engine and session maker if not already initialized."""
    global _ENGINE, _SESSION_LOCAL
    if _ENGINE is None:
        try:
            _, sync_db_url, _ = DatabaseConfig.get_database_urls()
            engine_kwargs = DatabaseConfig.get_engine_kwargs(is_async=False)
            
            _ENGINE = create_engine(sync_db_url, **engine_kwargs)
            _SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=_ENGINE)
            logger.info("Synchronous database engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize synchronous database engine: {e}")
            raise


def _init_async_db():
    """Initializes asynchronous database engine and session maker if not already initialized."""
    global _ASYNC_ENGINE, _ASYNC_SESSION_LOCAL
    if _ASYNC_ENGINE is None:
        try:
            _, _, async_db_url = DatabaseConfig.get_database_urls()
            engine_kwargs = DatabaseConfig.get_engine_kwargs(is_async=True)
            
            _ASYNC_ENGINE = create_async_engine(async_db_url, **engine_kwargs)
            _ASYNC_SESSION_LOCAL = async_sessionmaker(
                bind=_ASYNC_ENGINE,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
            logger.info("Asynchronous database engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize asynchronous database engine: {e}")
            raise


def init_db() -> bool:
    """
    Initialize database with proper error handling and logging.
    This function can be called during application startup.
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        logger.info("Initializing database...")
        
        # Initialize both sync and async engines
        _init_sync_db()
        _init_async_db()
        
        # Verify database connection
        if not test_database_connection():
            return False
            
            
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        return False


def test_database_connection() -> bool:
    """Test database connection synchronously."""
    try:
        _init_sync_db()
        from database.db_setup import _ENGINE
        
        with _ENGINE.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


async def test_async_database_connection() -> bool:
    """Test database connection asynchronously."""
    try:
        _init_async_db()
        from database.db_setup import _ASYNC_ENGINE
        
        async with _ASYNC_ENGINE.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("Async database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Async database connection test failed: {e}")
        return False




# --- Dependency for Synchronous Database Session (Legacy/Transition) ---
def get_db():
    """
    Provides a synchronous database session and ensures it's closed afterwards.
    Marked for deprecation.
    """
    _init_sync_db()
    db = _SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """
    Generator function for database sessions.
    Provides a synchronous database session and ensures it's closed afterwards.
    """
    _init_sync_db()
    db = _SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()


# --- Dependency for Asynchronous Database Session ---
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an asynchronous database session and ensures it's closed afterwards.
    """
    _init_async_db()
    async with _ASYNC_SESSION_LOCAL() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        # The 'async with' block handles session.close()


# --- Database Utilities ---
@contextmanager
def get_db_context():
    """Context manager for synchronous database sessions."""
    _init_sync_db()
    db = _SESSION_LOCAL()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def cleanup_db_connections():
    """Cleanup database connections and dispose engines."""
    global _ENGINE, _ASYNC_ENGINE

    if _ASYNC_ENGINE:
        await _ASYNC_ENGINE.dispose()
        _ASYNC_ENGINE = None
        logger.info("Async database engine disposed")

    if _ENGINE:
        _ENGINE.dispose()
        _ENGINE = None
        logger.info("Sync database engine disposed")


def get_engine_info() -> Dict[str, Any]:
    """Get information about current database engines for debugging."""
    info = {
        "sync_engine_initialized": _ENGINE is not None,
        "async_engine_initialized": _ASYNC_ENGINE is not None,
    }

    if _ASYNC_ENGINE:
        pool = _ASYNC_ENGINE.pool
        info.update(
            {
                "async_pool_size": pool.size(),
                "async_pool_checked_in": pool.checkedin(),
                "async_pool_checked_out": pool.checkedout(),
                "async_pool_overflow": pool.overflow(),
            }
        )

    if _ENGINE:
        pool = _ENGINE.pool
        info.update(
            {
                "sync_pool_size": pool.size(),
                "sync_pool_checked_in": pool.checkedin(),
                "sync_pool_checked_out": pool.checkedout(),
                "sync_pool_overflow": pool.overflow(),
            }
        )

    return info


# Backward compatibility aliases
_get_configured_database_urls = DatabaseConfig.get_database_urls
_init_sync_db = _init_sync_db  # Keep for backward compatibility
_init_async_db = _init_async_db  # Keep for backward compatibility
