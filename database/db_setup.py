"""
Database setup for ComplianceGPT, including synchronous and asynchronous configurations.
"""

import os
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# --- Global variables for engines and session makers (initialized lazily) ---
_engine = None
_SessionLocal = None
_async_engine = None
_AsyncSessionLocal = None

Base = declarative_base()

def _get_configured_database_urls():
    """
    Retrieves and processes DATABASE_URL from environment variables.
    This function is called only when a database connection is first needed.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # This print is for immediate feedback if the env var is missing when needed.
        # Logging might not be configured yet, or this might be a CLI script context.
        print("ERROR: DATABASE_URL environment variable not set at the time of database access.")
        raise OSError("DATABASE_URL not configured. Please set it in your .env file or environment.")

    # Derive SYNC_DATABASE_URL
    sync_db_url = db_url
    if "+asyncpg" in sync_db_url: # If it's an asyncpg URL, convert to psycopg2 for sync
        sync_db_url = sync_db_url.replace("+asyncpg", "+psycopg2")
    elif "postgresql://" in sync_db_url and "+psycopg2" not in sync_db_url: # If it's generic, assume psycopg2
        sync_db_url = sync_db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    # If it's already psycopg2 or another dialect, it's used as is or might error later if incompatible.

    # Derive ASYNC_DATABASE_URL
    async_db_url = db_url
    if "+asyncpg" not in async_db_url:
        # Attempt to convert to asyncpg if it's not already
        async_db_url_candidate = async_db_url.replace("+psycopg2", "+asyncpg")
        if "postgresql://" in async_db_url_candidate and "+asyncpg" not in async_db_url_candidate:
            async_db_url = async_db_url_candidate.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif "+asyncpg" in async_db_url_candidate:
            async_db_url = async_db_url_candidate
        # If it's a generic postgresql:// URL without a specified sync driver, default to making it asyncpg
        elif "postgresql://" in async_db_url and "+psycopg2" not in async_db_url and "+asyncpg" not in async_db_url:
            async_db_url = async_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    return db_url, sync_db_url, async_db_url

def _init_sync_db():
    """Initializes synchronous database engine and session maker if not already initialized."""
    global _engine, _SessionLocal
    if _engine is None:
        _, sync_db_url, _ = _get_configured_database_urls()

        # Connection pool configuration for sync engine
        engine_kwargs = {
            "echo": os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true",
            "pool_size": 20,  # Number of connections to maintain in the pool
            "max_overflow": 30,  # Additional connections beyond pool_size
            "pool_pre_ping": True,  # Validate connections before use
            "pool_recycle": 3600,  # Recycle connections after 1 hour
            "pool_timeout": 30,  # Timeout when getting connection from pool
        }

        _engine = create_engine(sync_db_url, **engine_kwargs)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

def _init_async_db():
    """Initializes asynchronous database engine and session maker if not already initialized."""
    global _async_engine, _AsyncSessionLocal
    if _async_engine is None:
        _, _, async_db_url = _get_configured_database_urls()

        # Handle SSL configuration for asyncpg
        engine_kwargs = {
            "echo": os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true",
            # Connection pool configuration to prevent "another operation is in progress" errors
            "pool_size": 20,  # Number of connections to maintain in the pool
            "max_overflow": 30,  # Additional connections beyond pool_size
            "pool_pre_ping": True,  # Validate connections before use
            "pool_recycle": 3600,  # Recycle connections after 1 hour
            "pool_timeout": 30,  # Timeout when getting connection from pool
            # Async-specific pool settings
            "pool_reset_on_return": "commit",  # Reset connection state on return
        }

        # If the URL contains sslmode=require, remove it and add ssl=True to engine kwargs
        if "sslmode=require" in async_db_url:
            async_db_url = async_db_url.replace("?sslmode=require", "").replace("&sslmode=require", "")
            if "connect_args" not in engine_kwargs:
                engine_kwargs["connect_args"] = {}
            engine_kwargs["connect_args"]["ssl"] = True

        _async_engine = create_async_engine(async_db_url, **engine_kwargs)
        _AsyncSessionLocal = sessionmaker(
            bind=_async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

# --- Dependency for Synchronous Database Session (Legacy/Transition) ---
def get_db():
    """
    Provides a synchronous database session and ensures it's closed afterwards.
    Marked for deprecation.
    """
    _init_sync_db() # Ensure engine and SessionLocal are initialized
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """
    Generator function for database sessions.
    Provides a synchronous database session and ensures it's closed afterwards.
    """
    _init_sync_db() # Ensure engine and SessionLocal are initialized
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Dependency for Asynchronous Database Session ---
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an asynchronous database session and ensures it's closed afterwards.
    """
    _init_async_db() # Ensure async_engine and AsyncSessionLocal are initialized
    async with _AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        # The 'async with' block handles session.close()

async def create_db_and_tables():
    """Creates all database tables asynchronously."""
    _init_async_db()
    async with _async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def cleanup_db_connections():
    """Cleanup database connections and dispose engines."""
    global _engine, _async_engine

    if _async_engine:
        await _async_engine.dispose()
        _async_engine = None

    if _engine:
        _engine.dispose()
        _engine = None

def get_engine_info():
    """Get information about current database engines for debugging."""
    info = {
        "sync_engine_initialized": _engine is not None,
        "async_engine_initialized": _async_engine is not None,
    }

    if _async_engine:
        pool = _async_engine.pool
        info.update({
            "async_pool_size": pool.size(),
            "async_pool_checked_in": pool.checkedin(),
            "async_pool_checked_out": pool.checkedout(),
            "async_pool_overflow": pool.overflow(),
        })

    if _engine:
        pool = _engine.pool
        info.update({
            "sync_pool_size": pool.size(),
            "sync_pool_checked_in": pool.checkedin(),
            "sync_pool_checked_out": pool.checkedout(),
            "sync_pool_overflow": pool.overflow(),
        })

    return info
