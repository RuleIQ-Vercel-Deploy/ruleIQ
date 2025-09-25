"""
Database provider interface and implementations.

This module provides the core database provider abstractions and concrete
implementations for PostgreSQL and Neo4j databases with dependency injection support.
"""
import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
import neo4j
from neo4j import GraphDatabase
from neo4j.exceptions import ClientError

from config.database_pool_config import ConnectionPoolConfig

logger = logging.getLogger(__name__)


@dataclass
class ConnectionHealth:
    """Represents the health status of a database connection."""
    status: str  # "healthy", "unhealthy", "degraded"
    details: Dict[str, Any]
    timestamp: Optional[float] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class DatabaseError(Exception):
    """Custom exception for database operations."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.details = details or {}
        self.cause = cause


class DatabaseProvider(ABC):
    """Abstract base class for database providers."""

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the database connection."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    async def health_check(self) -> ConnectionHealth:
        """Check the health of the database connection."""
        pass

    @abstractmethod
    async def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        pass

    @abstractmethod
    async def execute_transaction(self, queries: List[Dict[str, Any]]) -> bool:
        """Execute multiple queries in a transaction."""
        pass


class DatabaseConfig:
    """Configuration for database providers."""

    @staticmethod
    def get_provider(provider_type: str) -> DatabaseProvider:
        """Factory method to create database providers."""
        if provider_type == "postgres":
            return PostgreSQLProvider()
        elif provider_type == "neo4j":
            return Neo4jProvider()
        else:
            raise ValueError(
                "Unsupported provider type: %s" % provider_type
            )


class PostgreSQLProvider(DatabaseProvider):
    """PostgreSQL database provider implementation."""

    def __init__(self):
        self.engine = None
        self.session_maker = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize PostgreSQL connection using existing pool config."""
        try:
            if self._initialized:
                return True

            # Use existing database setup configuration
            from database.db_setup import DatabaseConfig as ExistingConfig

            # Get database URLs
            _, _, async_db_url = ExistingConfig.get_database_urls()

            # Get optimized pool settings
            pool_kwargs = ExistingConfig.get_engine_kwargs(is_async=True)

            # Create async engine
            self.engine = create_async_engine(async_db_url, **pool_kwargs)

            # Create session maker
            self.session_maker = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False
            )

            self._initialized = True
            logger.info("PostgreSQL provider initialized successfully")
            return True

        except (ImportError, ConnectionError, ValueError) as e:
            logger.exception(
                "Failed to initialize PostgreSQL provider"
            )
            return False

    async def close(self) -> None:
        """Close PostgreSQL connection."""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_maker = None
            self._initialized = False
            logger.info("PostgreSQL provider closed")

    async def health_check(self) -> ConnectionHealth:
        """Check PostgreSQL connection health."""
        if not self._initialized:
            return ConnectionHealth(
                status="unhealthy",
                details={"error": "Not initialized"}
            )

        start_time = time.time()
        try:
            async with self.session_maker() as session:
                # Simple health check query
                result = await session.execute(text("SELECT 1 as health_check"))
                row = result.first()
                response_time = time.time() - start_time

                if row and row.health_check == 1:
                    # Check connection pool stats
                    pool_details = {}
                    if hasattr(self.engine, 'pool'):
                        pool = self.engine.pool
                        pool_details = {
                            "pool_size": getattr(pool, 'size', lambda: 0)(),
                            "checked_in": getattr(pool, 'checkedin', lambda: 0)(),
                            "checked_out": getattr(pool, 'checkedout', lambda: 0)(),
                            "overflow": getattr(pool, 'overflow', lambda: 0)(),
                        }

                    return ConnectionHealth(
                        status="healthy",
                        details={
                            "response_time": response_time,
                            "pool_stats": pool_details
                        }
                    )
                else:
                    return ConnectionHealth(
                        status="unhealthy",
                        details={"error": "Health check query failed"}
                    )

        except (ConnectionError, TimeoutError, ValueError) as e:
            response_time = time.time() - start_time
            return ConnectionHealth(
                status="unhealthy",
                details={
                    "error": str(e),
                    "response_time": response_time
                }
            )

    async def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a PostgreSQL query."""
        if not self._initialized:
            raise DatabaseError("PostgreSQL provider not initialized")

        try:
            async with self.session_maker() as session:
                result = await session.execute(text(query), params or {})
                rows = result.fetchall()

                # Convert to list of dictionaries
                return [dict(row._mapping) for row in rows]

        except (ConnectionError, TimeoutError, ValueError) as e:
            logger.exception(
                "PostgreSQL query execution failed: %s", e
            )
            raise DatabaseError(
                "Query execution failed: %s" % e,
                {"query": query, "params": params},
                e
            )

    async def execute_transaction(self, queries: List[Dict[str, Any]]) -> bool:
        """Execute multiple PostgreSQL queries in a transaction."""
        if not self._initialized:
            raise DatabaseError("PostgreSQL provider not initialized")

        try:
            async with self.session_maker() as session:
                async with session.begin():
                    for query_data in queries:
                        query = query_data["query"]
                        params = query_data.get("params", {})
                        await session.execute(text(query), params)

                await session.commit()
                return True

        except (ConnectionError, TimeoutError, ValueError) as e:
            logger.exception(
                "PostgreSQL transaction failed: %s", e
            )
            raise DatabaseError(
                "Transaction failed: %s" % e,
                {"queries": queries},
                e
            )


class Neo4jProvider(DatabaseProvider):
    """Neo4j graph database provider implementation."""

    def __init__(self):
        self.driver = None
        self._initialized = False
        self._executor = None

    async def initialize(self) -> bool:
        """Initialize Neo4j connection."""
        try:
            if self._initialized:
                return True

            # Get Neo4j configuration from environment
            import os
            uri = os.getenv('NEO4J_URI', 'neo4j+s://12e71bc4.databases.neo4j.io')
            username = os.getenv('NEO4J_USERNAME', 'neo4j')
            password = os.getenv('NEO4J_PASSWORD', 'ruleiq123')
            database = os.getenv('NEO4J_DATABASE', 'neo4j')

            # Create Neo4j driver with optimized settings
            self.driver = GraphDatabase.driver(
                uri,
                auth=(username, password),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_acquisition_timeout=60
            )

            # Create thread pool executor for async operations
            import concurrent.futures
            self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

            # Test connection
            if not await self._test_connection():
                raise ConnectionError("Neo4j connection test failed")

            self._initialized = True
            logger.info("Neo4j provider initialized successfully")
            return True

        except (ImportError, ConnectionError, neo4j.exceptions.Neo4jError) as e:
            logger.exception(
                "Failed to initialize Neo4j provider"
            )
            return False

    async def _test_connection(self) -> bool:
        """Test Neo4j connection."""
        if not self.driver or not self._executor:
            return False

        try:
            def _test():
                with self.driver.session() as session:
                    result = session.run("RETURN 1 as test")
                    record = result.single()
                    return record and record["test"] == 1

            return await asyncio.get_event_loop().run_in_executor(self._executor, _test)

        except (neo4j.exceptions.Neo4jError, ConnectionError) as e:
            logger.exception("Neo4j connection test failed")
            return False

    async def close(self) -> None:
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.driver = None

        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None

        self._initialized = False
        logger.info("Neo4j provider closed")

    async def health_check(self) -> ConnectionHealth:
        """Check Neo4j connection health."""
        if not self._initialized:
            return ConnectionHealth(
                status="unhealthy",
                details={"error": "Not initialized"}
            )

        start_time = time.time()
        try:
            def _health_check():
                with self.driver.session() as session:
                    result = session.run("RETURN 1 as health_check")
                    record = result.single()
                    return record and record["health_check"] == 1

            success = await asyncio.get_event_loop().run_in_executor(
                self._executor, _health_check
            )
            response_time = time.time() - start_time

            if success:
                return ConnectionHealth(
                    status="healthy",
                    details={"response_time": response_time}
                )
            else:
                return ConnectionHealth(
                    status="unhealthy",
                    details={"error": "Health check query failed"}
                )

        except (ConnectionError, TimeoutError, ValueError) as e:
            response_time = time.time() - start_time
            return ConnectionHealth(
                status="unhealthy",
                details={
                    "error": str(e),
                    "response_time": response_time
                }
            )

    async def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a Neo4j Cypher query."""
        if not self._initialized:
            raise DatabaseError("Neo4j provider not initialized")

        try:
            def _execute():
                with self.driver.session() as session:
                    result = session.run(query, params or {})
                    return [record.data() for record in result]

            return await asyncio.get_event_loop().run_in_executor(
                self._executor, _execute
            )

        except (neo4j.exceptions.Neo4jError, ConnectionError) as e:
            logger.exception(
                "Neo4j query execution failed: %s", e
            )
            raise DatabaseError(
                "Query execution failed: %s" % e,
                {"query": query, "params": params},
                e
            )

    async def execute_transaction(self, queries: List[Dict[str, Any]]) -> bool:
        """Execute multiple Neo4j queries in a transaction."""
        if not self._initialized:
            raise DatabaseError("Neo4j provider not initialized")

        try:
            def _execute_transaction():
                with self.driver.session() as session:
                    with session.begin_transaction() as tx:
                        for query_data in queries:
                            query = query_data["query"]
                            params = query_data.get("params", {})
                            tx.run(query, params)
                        tx.commit()
                        return True

            return await asyncio.get_event_loop().run_in_executor(
                self._executor, _execute_transaction
            )

        except (neo4j.exceptions.Neo4jError, ConnectionError) as e:
            logger.exception(
                "Neo4j transaction failed: %s", e
            )
            raise DatabaseError(
                "Transaction failed: %s" % e,
                {"queries": queries},
                e
            )


# Global provider instances for backward compatibility
_postgres_provider: Optional[PostgreSQLProvider] = None
_neo4j_provider: Optional[Neo4jProvider] = None


async def get_postgres_provider() -> PostgreSQLProvider:
    """Get or create global PostgreSQL provider instance."""
    global _postgres_provider
    if _postgres_provider is None:
        _postgres_provider = PostgreSQLProvider()
        await _postgres_provider.initialize()
    return _postgres_provider


async def get_neo4j_provider() -> Neo4jProvider:
    """Get or create global Neo4j provider instance."""
    global _neo4j_provider
    if _neo4j_provider is None:
        _neo4j_provider = Neo4jProvider()
        await _neo4j_provider.initialize()
    return _neo4j_provider


async def initialize_providers() -> None:
    """Initialize all database providers."""
    await get_postgres_provider()
    await get_neo4j_provider()


async def close_providers() -> None:
    """Close all database providers."""
    global _postgres_provider, _neo4j_provider

    if _postgres_provider:
        await _postgres_provider.close()
        _postgres_provider = None

    if _neo4j_provider:
        await _neo4j_provider.close()
        _neo4j_provider = None