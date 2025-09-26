"""
from __future__ import annotations

Database setup for ruleIQ, including synchronous and asynchronous
configurations. Provides comprehensive database initialization and
management utilities.
"""
import os
import logging
from typing import AsyncGenerator, Dict, Any, Generator, Optional, TYPE_CHECKING
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, MetaData, Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from fastapi import HTTPException
load_dotenv('.env.local', override=True)
load_dotenv('.env', override=False)
logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker as SessionMakerType
    from sqlalchemy.ext.asyncio import async_sessionmaker as AsyncSessionMakerType
    _ENGINE: Optional[Engine] = None
    _SESSION_LOCAL: Optional[SessionMakerType[Session]] = None
    _ASYNC_ENGINE: Optional[AsyncEngine] = None
    _ASYNC_SESSION_LOCAL: Optional[AsyncSessionMakerType[AsyncSession]] = None
else:
    _ENGINE: Optional[Engine] = None
    _SESSION_LOCAL: Optional[Any] = None
    _ASYNC_ENGINE: Optional[AsyncEngine] = None
    _ASYNC_SESSION_LOCAL: Optional[Any] = None
naming_convention = {'ix': 'ix_%(column_0_label)s', 'uq':
    'uq_%(table_name)s_%(column_0_name)s', 'ck':
    'ck_%(table_name)s_%(constraint_name)s', 'fk':
    'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s', 'pk':
    'pk_%(table_name)s'}
metadata = MetaData(naming_convention=naming_convention)
Base = declarative_base(metadata=metadata)


class DatabaseConfig:
    """Database configuration class for managing connection settings."""

    @staticmethod
    def validate_environment() ->None:
        """Validate that required environment variables are set."""
        required_vars = ['DATABASE_URL']
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        if missing_vars:
            error_msg = f"""Missing required environment variables: {', '.join(missing_vars)}
Please copy env.template to .env.local and configure the variables."""
            logger.error(error_msg)
            raise OSError(error_msg)
        if os.path.exists('.env.local'):
            logger.info('Loaded configuration from .env.local')
        elif os.path.exists('.env'):
            logger.info('Loaded configuration from .env')
        else:
            logger.info('Using system environment variables')

    @staticmethod
    def get_database_urls() ->tuple[str, str, str]:
        """
        Retrieves and processes DATABASE_URL from environment variables.
        Returns tuple of (original_url, sync_url, async_url)
        """
        DatabaseConfig.validate_environment()
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            error_msg = 'DATABASE_URL environment variable not set. Please set it in your .env file or environment.'
            logger.error(error_msg)
            raise OSError(error_msg)
        safe_url = db_url.split('@')[1] if '@' in db_url else db_url
        logger.info('Connecting to database: %s' % safe_url)
        sync_db_url = db_url
        if '+asyncpg' in sync_db_url:
            sync_db_url = sync_db_url.replace('+asyncpg', '+psycopg2')
        elif 'postgresql://' in sync_db_url and '+psycopg2' not in sync_db_url:
            sync_db_url = sync_db_url.replace('postgresql://',
                'postgresql+psycopg2://', 1)
        async_db_url = db_url
        try:
            import asyncpg  # noqa: F401
            if 'postgresql://' in async_db_url and '+asyncpg' not in async_db_url:
                async_db_url = async_db_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        except ImportError:
            logger.warning('asyncpg not available, falling back to psycopg for async connections')
            # Fallback to psycopg for async connections (psycopg v3 supports async)
            if 'postgresql://' in async_db_url and '+psycopg' not in async_db_url:
                async_db_url = async_db_url.replace('postgresql://', 'postgresql+psycopg://', 1)
            elif '+asyncpg' in async_db_url:
                async_db_url = async_db_url.replace('+asyncpg', '+psycopg')
        return db_url, sync_db_url, async_db_url

    @staticmethod
    def get_engine_kwargs(is_async: bool=False) ->Dict[str, Any]:
        """Get optimized engine configuration based on sync/async mode."""
        # Import the enhanced pool configuration
        try:
            from config.database_pool_config import ConnectionPoolConfig
            is_production = os.getenv('ENVIRONMENT', 'development').lower() == 'production'

            if is_async:
                return ConnectionPoolConfig.get_async_pool_settings(is_production)
            else:
                return ConnectionPoolConfig.get_pool_settings(is_production)
        except ImportError:
            # Fallback to original configuration if new config not available
            logger.warning("Using fallback database pool configuration")
            try:
                base_kwargs = {'echo': os.getenv('SQLALCHEMY_ECHO', 'false').
                    lower() == 'true', 'pool_size': int(os.getenv(
                    'DB_POOL_SIZE', '10')), 'max_overflow': int(os.getenv(
                    'DB_MAX_OVERFLOW', '20')), 'pool_pre_ping': True,
                    'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '1800')),
                    'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '30'))}
            except ValueError as e:
                logger.error('Invalid database configuration value: %s' % e)
                raise ValueError(f'Invalid database configuration: {e}')
            if is_async:
                async_kwargs = {**base_kwargs, 'pool_reset_on_return': 'commit'}
                db_url = os.getenv('DATABASE_URL', '')
                connect_args = {'server_settings': {'jit': 'off',
                    'application_name': 'ruleIQ_backend'}}
                if 'sslmode=require' in db_url:
                    connect_args['ssl'] = True
                async_kwargs['connect_args'] = connect_args
                return async_kwargs
            else:
                sync_kwargs = {**base_kwargs, 'connect_args': {'keepalives': 1,
                    'keepalives_idle': 30, 'keepalives_interval': 10,
                    'keepalives_count': 5, 'connect_timeout': 10}}
                return sync_kwargs


def _init_sync_db() ->None:
    """Initializes synchronous database engine and session maker if not already initialized."""
    global _ENGINE, _SESSION_LOCAL
    if _ENGINE is None:
        try:
            _, sync_db_url, _ = DatabaseConfig.get_database_urls()
            engine_kwargs = DatabaseConfig.get_engine_kwargs(is_async=False)
            _ENGINE = create_engine(sync_db_url, **engine_kwargs)
            _SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False,
                bind=_ENGINE)
            logger.info('Synchronous database engine initialized successfully')
        except Exception as e:
            logger.error(
                'Failed to initialize synchronous database engine: %s' % e)
            raise


def _init_async_db() -> None:
    """Initializes asynchronous database engine and session maker if not already initialized."""
    global _ASYNC_ENGINE, _ASYNC_SESSION_LOCAL
    if _ASYNC_ENGINE is None:
        # Check for Cloud Run environment
        is_cloud_run = bool(os.getenv('K_SERVICE') or os.getenv('CLOUD_RUN_JOB'))
        
        try:
            # Get database URLs, which handles driver fallback internally
            _, _, async_db_url = DatabaseConfig.get_database_urls()
            if async_db_url is None:
                logger.warning('Async database URL is None - no async driver available')
                return  # Cannot create async engine without a driver
            
            # Extract driver from URL for logging
            driver_name = 'asyncpg' if 'asyncpg' in async_db_url else 'psycopg' if 'psycopg' in async_db_url else 'unknown'
            logger.debug(f'Using async driver: {driver_name}')
            
            # Create async engine with the appropriate driver
            engine_kwargs = DatabaseConfig.get_engine_kwargs(is_async=True)
            _ASYNC_ENGINE = create_async_engine(async_db_url, **engine_kwargs)
            _ASYNC_SESSION_LOCAL = async_sessionmaker(
                bind=_ASYNC_ENGINE,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False
            )
            
            if is_cloud_run:
                logger.info(f'🌩️ Cloud Run: Asynchronous database engine initialized successfully with {driver_name}')
            else:
                logger.info(f'Asynchronous database engine initialized successfully with {driver_name}')
                
        except Exception as e:
            error_msg = f'Failed to initialize asynchronous database engine: {e}'
            if is_cloud_run:
                logger.warning(f'🌩️ Cloud Run: {error_msg} - will retry on demand')
                return  # Allow graceful degradation in Cloud Run
            else:
                logger.error(error_msg)
                raise


def init_db() ->bool:
    """
    Initialize database with proper error handling and logging.
    This function can be called during application startup.

    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        logger.info('Initializing database...')
        _init_sync_db()
        _init_async_db()

        if not test_database_connection():
            return False
        logger.info('Database initialization completed successfully')
        return True
    except Exception as e:
        logger.error('Database initialization failed: %s' % e, exc_info=True)
        return False


def test_database_connection() ->bool:
    """Test database connection synchronously."""
    try:
        _init_sync_db()
        global _ENGINE
        with _ENGINE.connect() as conn:
            conn.execute(text('SELECT 1'))
            logger.info('Database connection test successful')
            return True
    except Exception as e:
        logger.error('Database connection test failed: %s' % e)
        return False


async def test_async_database_connection() ->bool:
    """Test database connection asynchronously."""
    is_cloud_run = bool(os.getenv('K_SERVICE') or os.getenv('CLOUD_RUN_JOB'))
    
    try:
        # Try to get the session maker (which will initialize if needed)
        session_maker = get_async_session_maker()
        if session_maker is None:
            if is_cloud_run:
                logger.warning('🌩️ Cloud Run: Async database not available - skipping connection test')
                return False
            else:
                logger.error('Async database session maker not available')
                return False
        
        # Test the connection using the global engine
        if _ASYNC_ENGINE is None:
            logger.error('Async database engine not initialized')
            return False
            
        async with _ASYNC_ENGINE.connect() as conn:
            await conn.execute(text('SELECT 1'))
            if is_cloud_run:
                logger.info('🌩️ Cloud Run: Async database connection test successful')
            else:
                logger.info('Async database connection test successful')
            return True
    except ImportError as e:
        if is_cloud_run:
            logger.warning(f'🌩️ Cloud Run: Async database connection test skipped due to missing dependencies: {e}')
            return False
        else:
            logger.error(f'Async database connection test failed due to missing dependencies: {e}')
            return False
    except Exception as e:
        if is_cloud_run:
            logger.warning(f'🌩️ Cloud Run: Async database connection test failed: {e}')
        else:
            logger.error(f'Async database connection test failed: {e}')
        return False


def get_db() ->Generator[Any, None, None]:
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


def get_db_session() ->Generator[Any, None, None]:
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


async def get_async_db() ->AsyncGenerator[AsyncSession, None]:
    """
    Provides an asynchronous database session and ensures it's closed afterwards.
    """
    session_maker = get_async_session_maker()
    if session_maker is None:
        is_cloud_run = bool(os.getenv('K_SERVICE') or os.getenv('CLOUD_RUN_JOB'))
        error_msg = 'Async database session maker not available'
        if is_cloud_run:
            logger.warning(f'🌩️ Cloud Run: {error_msg} - async database operations not supported')
        raise HTTPException(status_code=503, detail=f'{error_msg} - check database configuration and asyncpg installation')
    
    async with session_maker() as session:
        try:
            yield session
        except (ValueError, TypeError):
            await session.rollback()
            raise


@contextmanager
def get_db_context() ->Generator[Any, None, None]:
    """Context manager for synchronous database sessions."""
    _init_sync_db()
    db = _SESSION_LOCAL()
    try:
        yield db
        db.commit()
    except (ValueError, TypeError):
        db.rollback()
        raise
    finally:
        db.close()


async def cleanup_db_connections() ->None:
    """Cleanup database connections and dispose engines."""
    global _ENGINE, _ASYNC_ENGINE
    if _ASYNC_ENGINE:
        await _ASYNC_ENGINE.dispose()
        _ASYNC_ENGINE = None
        logger.info('Async database engine disposed')
    if _ENGINE:
        _ENGINE.dispose()
        _ENGINE = None
        logger.info('Sync database engine disposed')


def get_engine_info() ->Dict[str, Any]:
    """Get information about current database engines for debugging."""
    info = {'sync_engine_initialized': _ENGINE is not None,
        'async_engine_initialized': _ASYNC_ENGINE is not None}
    if _ASYNC_ENGINE:
        try:
            pool = _ASYNC_ENGINE.pool
            info.update({
                'async_pool_size': getattr(pool, 'size', lambda: 0)() if hasattr(pool, 'size') else 0,
                'async_pool_checked_in': getattr(pool, 'checkedin', lambda: 0)() if hasattr(pool, 'checkedin') else 0,
                'async_pool_checked_out': getattr(pool, 'checkedout', lambda: 0)() if hasattr(pool, 'checkedout') else 0,
                'async_pool_overflow': getattr(pool, 'overflow', lambda: 0)() if hasattr(pool, 'overflow') else 0
            })
        except Exception as e:
            logger.debug(f'Could not get async pool info: {e}')
    if _ENGINE:
        try:
            pool = _ENGINE.pool
            info.update({
                'sync_pool_size': getattr(pool, 'size', lambda: 0)() if hasattr(pool, 'size') else 0,
                'sync_pool_checked_in': getattr(pool, 'checkedin', lambda: 0)() if hasattr(pool, 'checkedin') else 0,
                'sync_pool_checked_out': getattr(pool, 'checkedout', lambda: 0)() if hasattr(pool, 'checkedout') else 0,
                'sync_pool_overflow': getattr(pool, 'overflow', lambda: 0)() if hasattr(pool, 'overflow') else 0
            })
        except Exception as e:
            logger.debug(f'Could not get sync pool info: {e}')
    return info


_get_configured_database_urls = DatabaseConfig.get_database_urls
_init_sync_db = _init_sync_db
_init_async_db = _init_async_db
def get_async_session_maker():
    """Get the async session maker, initializing if needed."""
    global _ASYNC_SESSION_LOCAL
    
    if _ASYNC_SESSION_LOCAL is None:
        is_cloud_run = bool(os.getenv('K_SERVICE') or os.getenv('CLOUD_RUN_JOB'))
        
        try:
            _init_async_db()
        except ImportError as e:
            if is_cloud_run:
                logger.warning(f'🌩️ Cloud Run: Async database initialization failed due to missing dependencies: {e}')
                logger.warning('🌩️ Cloud Run: Returning None - async operations will not be available')
                return None
            else:
                logger.error(f'Failed to initialize async database: {e}')
                raise
        except Exception as e:
            if is_cloud_run:
                logger.warning(f'🌩️ Cloud Run: Async database initialization failed: {e}')
                logger.warning('🌩️ Cloud Run: Returning None - will retry later')
                return None
            else:
                logger.error(f'Failed to get async session maker: {e}')
                raise
    
    return _ASYNC_SESSION_LOCAL

# For backward compatibility - but make it lazy to prevent eager initialization
# This will be None initially and only populated when get_async_session_maker() is called
async_session_maker = None
