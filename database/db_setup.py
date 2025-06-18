"""
Database setup for ComplianceGPT, including synchronous and asynchronous configurations.
"""

import os

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
        _engine = create_engine(sync_db_url)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

def _init_async_db():
    """Initializes asynchronous database engine and session maker if not already initialized."""
    global _async_engine, _AsyncSessionLocal
    if _async_engine is None:
        _, _, async_db_url = _get_configured_database_urls()
        _async_engine = create_async_engine(async_db_url, echo=os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true")
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

# --- Dependency for Asynchronous Database Session ---
async def get_async_db() -> AsyncSession:
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
