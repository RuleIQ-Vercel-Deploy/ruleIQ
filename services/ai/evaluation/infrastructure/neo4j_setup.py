"""Neo4j Community Edition setup and connection management."""

print("[MODULE LOAD] neo4j_setup.py is being loaded...")
print(f"[MODULE LOAD] __file__ = {__file__}")
import os
import time
import docker
from typing import Optional, Dict, Any
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable


class Neo4jConnection:
    """Singleton Neo4j connection wrapper."""

    _instance: Optional["Neo4jConnection"] = None
    _driver: Optional[Driver] = None

    def __new__(cls) -> "Neo4jConnection":
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize connection parameters."""
        # Only initialize once
        if not hasattr(self, "_initialized"):
            print(f"[Neo4jConnection] Fresh initialization...")
            print(f"[Neo4jConnection] Getting env vars...")
            print(f"[Neo4jConnection] NEO4J_URI from env: {os.getenv('NEO4J_URI')}")
            print(f"[Neo4jConnection] NEO4J_USER from env: {os.getenv('NEO4J_USER')}")
            print(
                f"[Neo4jConnection] NEO4J_PASSWORD from env: {os.getenv('NEO4J_PASSWORD')}"
            )

            self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7688")
            self.user = os.getenv("NEO4J_USER", "neo4j")
            self.password = os.getenv("NEO4J_PASSWORD", "ruleiq123")

            print(f"[Neo4jConnection] After assignment:")
            print(f"[Neo4jConnection]   self.uri = {self.uri}")
            print(f"[Neo4jConnection]   self.user = {self.user}")
            print(f"[Neo4jConnection]   self.password = {self.password}")
            self._initialized = True
        else:
            print(f"[Neo4jConnection] Already initialized - cached values")

    def get_driver(self) -> Driver:
        """Get or create Neo4j driver."""
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
            )
        return self._driver

    def close(self):
        """Close the driver connection."""
        if self._driver:
            self._driver.close()
            self._driver = None

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None):
        """Execute a Cypher query."""
        driver = self.get_driver()
        with driver.session() as session:
            return session.run(query, params)


def setup_neo4j_container() -> docker.models.containers.Container:
    """Set up Neo4j Community Edition container."""
    client = docker.from_env()
    container_name = "ruleiq-neo4j"

    # Check if container already exists
    try:
        container = client.containers.get(container_name)
        if container.status != "running":
            container.start()
            time.sleep(5)
        return container
    except docker.errors.NotFound:
        pass

    # Create new container
    container = client.containers.run(
        "neo4j:5.26.10-community",
        name=container_name,
        ports={"7474/tcp": 7474, "7687/tcp": 7687},
        environment={
            "NEO4J_AUTH": "neo4j/please_change",
            "NEO4J_ACCEPT_LICENSE_AGREEMENT": "yes",
            "NEO4J_dbms_memory_heap_initial__size": "512m",
            "NEO4J_dbms_memory_heap_max__size": "1G",
            "NEO4J_dbms_memory_pagecache_size": "512m",
            "NEO4J_PLUGINS": '["apoc"]',
            "NEO4J_dbms_security_procedures_unrestricted": "*",
            "NEO4J_dbms_security_procedures_allowlist": "*",
        },
        volumes={
            "neo4j_golden_data": {"bind": "/data", "mode": "rw"},
            "neo4j_golden_logs": {"bind": "/logs", "mode": "rw"},
            "neo4j_golden_import": {"bind": "/import", "mode": "rw"},
            "neo4j_golden_plugins": {"bind": "/plugins", "mode": "rw"},
        },
        detach=True,
        remove=False,
    )

    wait_for_neo4j()
    return container


def wait_for_neo4j(max_retries: int = 30) -> bool:
    """Wait for Neo4j to be ready."""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7688")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "ruleiq123")

    for i in range(max_retries):
        try:
            driver = GraphDatabase.driver(uri, auth=(user, password))
            with driver.session() as session:
                session.run("RETURN 1")
            driver.close()
            return True
        except (ServiceUnavailable, Exception):
            if i == max_retries - 1:
                return False
            time.sleep(2)

    return False


def create_vector_indexes(connection: Neo4jConnection):
    """Create vector indexes for documents and chunks."""
    # Check if indexes exist first
    check_query = "SHOW INDEXES"
    result = connection.execute_query(check_query)

    # Handle both real results and mocks
    existing_indexes = set()
    if result:
        try:
            for record in result:
                if hasattr(record, "get") and record.get("name"):
                    existing_indexes.add(record["name"])
        except TypeError:
            # Mock object or empty result
            pass

    # Create document embedding index
    if "document_embedding_index" not in existing_indexes:
        doc_index_query = """
        CREATE VECTOR INDEX document_embedding_index IF NOT EXISTS
        FOR (d:Document)
        ON (d.embedding)
        OPTIONS {
            indexConfig: {
                `vector.dimensions`: 384,
                `vector.similarity_function`: 'cosine'
            }
        }
        """
        try:
            connection.execute_query(doc_index_query)
        except Exception as e:
            # Index might already exist or vector indexes not supported
            print(f"Could not create document index: {e}")

    # Create chunk embedding index
    if "chunk_embedding_index" not in existing_indexes:
        chunk_index_query = """
        CREATE VECTOR INDEX chunk_embedding_index IF NOT EXISTS
        FOR (c:Chunk)
        ON (c.embedding)
        OPTIONS {
            indexConfig: {
                `vector.dimensions`: 384,
                `vector.similarity_function`: 'cosine'
            }
        }
        """
        try:
            connection.execute_query(chunk_index_query)
        except Exception as e:
            # Index might already exist or vector indexes not supported
            print(f"Could not create chunk index: {e}")


def get_neo4j_driver() -> Driver:
    """Get Neo4j driver instance."""
    connection = Neo4jConnection()
    return connection.get_driver()
