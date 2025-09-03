#!/usr/bin/env python3
"""
Test Database Setup and Verification Script
Task 2ef17163: Configure test DB & connections

This script ensures test databases are properly configured and accessible.
"""

import os
import sys
import subprocess
import psycopg2
import redis
import time
from typing import Optional, Tuple
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_docker_services() -> bool:
    """Check if Docker test services are running."""
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", "docker-compose.test.yml", "ps"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            logger.warning("Docker compose test services not running")
            return False
        
        # Check if test-db and test-redis are running
        output = result.stdout
        if "test-db" in output and "test-redis" in output:
            logger.info("✓ Docker test services are running")
            return True
        
        return False
    except FileNotFoundError:
        logger.error("Docker not found. Please ensure Docker is installed.")
        return False

def start_docker_services() -> bool:
    """Start Docker test services if not running."""
    logger.info("Starting Docker test services...")
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", "docker-compose.test.yml", "up", "-d", "test-db", "test-redis"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            logger.error(f"Failed to start Docker services: {result.stderr}")
            return False
        
        logger.info("Docker test services started. Waiting for them to be ready...")
        time.sleep(5)  # Give services time to start
        return True
    except Exception as e:
        logger.error(f"Failed to start Docker services: {e}")
        return False

def wait_for_postgres(host: str, port: int, user: str, password: str, database: str, max_retries: int = 30) -> bool:
    """Wait for PostgreSQL to be ready."""
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            conn.close()
            logger.info(f"✓ PostgreSQL is ready on port {port}")
            return True
        except psycopg2.OperationalError:
            if i < max_retries - 1:
                logger.info(f"Waiting for PostgreSQL... ({i+1}/{max_retries})")
                time.sleep(1)
            else:
                logger.error(f"PostgreSQL failed to start on port {port}")
                return False
    return False

def wait_for_redis(host: str, port: int, max_retries: int = 30) -> bool:
    """Wait for Redis to be ready."""
    for i in range(max_retries):
        try:
            r = redis.Redis(host=host, port=port, decode_responses=True)
            r.ping()
            logger.info(f"✓ Redis is ready on port {port}")
            return True
        except redis.ConnectionError:
            if i < max_retries - 1:
                logger.info(f"Waiting for Redis... ({i+1}/{max_retries})")
                time.sleep(1)
            else:
                logger.error(f"Redis failed to start on port {port}")
                return False
    return False

def setup_test_database(conn_params: dict) -> bool:
    """Create test database and run migrations."""
    try:
        # Connect to postgres database to create test database
        admin_conn = psycopg2.connect(
            host=conn_params['host'],
            port=conn_params['port'],
            user=conn_params['user'],
            password=conn_params['password'],
            database='postgres'
        )
        admin_conn.autocommit = True
        
        with admin_conn.cursor() as cursor:
            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (conn_params['database'],)
            )
            if not cursor.fetchone():
                cursor.execute(f"CREATE DATABASE {conn_params['database']}")
                logger.info(f"✓ Created database {conn_params['database']}")
            else:
                logger.info(f"✓ Database {conn_params['database']} already exists")
        
        admin_conn.close()
        
        # Connect to test database
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        
        with conn.cursor() as cursor:
            # Create extensions if needed
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
            cursor.execute("CREATE EXTENSION IF NOT EXISTS uuid-ossp")
            logger.info("✓ Database extensions created")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup database: {e}")
        return False

def run_alembic_migrations() -> bool:
    """Run Alembic migrations on test database."""
    try:
        # Set test database URL for Alembic
        test_db_url = "postgresql://test_user:test_password@localhost:5433/ruleiq_test"
        env = os.environ.copy()
        env['DATABASE_URL'] = test_db_url
        env['TESTING'] = 'true'
        
        # Check if alembic.ini exists
        if not os.path.exists('alembic.ini'):
            logger.warning("alembic.ini not found, skipping migrations")
            return True
        
        # Run migrations
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            env=env,
            check=False
        )
        
        if result.returncode != 0:
            logger.error(f"Alembic migrations failed: {result.stderr}")
            # This is not critical if tables are created by SQLAlchemy
            logger.info("Will rely on SQLAlchemy to create tables")
        else:
            logger.info("✓ Alembic migrations completed")
        
        return True
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")
        return True  # Not critical

def verify_database_schema() -> bool:
    """Verify that all required tables exist in test database."""
    try:
        # Import settings to ensure test config is loaded
        os.environ['TESTING'] = 'true'
        os.environ['TEST_DATABASE_URL'] = 'postgresql://test_user:test_password@localhost:5433/ruleiq_test'
        
        from database import init_db, test_database_connection, Base, _ENGINE
        
        # Initialize database (creates tables if needed)
        if not init_db():
            logger.error("Failed to initialize database")
            return False
        
        # Test connection
        if not test_database_connection():
            logger.error("Database connection test failed")
            return False
        
        # Verify some critical tables exist
        from sqlalchemy import inspect
        inspector = inspect(_ENGINE)
        tables = inspector.get_table_names()
        
        required_tables = ['users', 'business_profiles', 'compliance_frameworks']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            logger.warning(f"Missing tables: {missing_tables}")
            # Try to create them
            Base.metadata.create_all(bind=_ENGINE)
            logger.info("✓ Created missing tables")
        else:
            logger.info(f"✓ All required tables exist ({len(tables)} tables total)")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to verify schema: {e}")
        return False

def verify_redis_connection() -> bool:
    """Verify Redis test instance is accessible."""
    try:
        r = redis.Redis(host='localhost', port=6380, decode_responses=True)
        
        # Test basic operations
        r.set('test_key', 'test_value', ex=10)
        value = r.get('test_key')
        r.delete('test_key')
        
        if value == 'test_value':
            logger.info("✓ Redis test operations successful")
            return True
        else:
            logger.error("Redis test operations failed")
            return False
            
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False

def setup_test_environment() -> bool:
    """Set up complete test environment."""
    logger.info("=" * 60)
    logger.info("Setting up test database and connections")
    logger.info("=" * 60)
    
    # 1. Check/start Docker services
    if not check_docker_services():
        if not start_docker_services():
            logger.error("Failed to start Docker test services")
            logger.info("Please run: docker compose -f docker-compose.test.yml up -d")
            return False
    
    # 2. PostgreSQL configuration
    pg_config = {
        'host': 'localhost',
        'port': 5433,
        'user': 'test_user',
        'password': 'test_password',
        'database': 'ruleiq_test'
    }
    
    # 3. Wait for PostgreSQL
    if not wait_for_postgres(**pg_config):
        logger.error("PostgreSQL is not accessible")
        return False
    
    # 4. Setup test database
    if not setup_test_database(pg_config):
        logger.error("Failed to setup test database")
        return False
    
    # 5. Run migrations (optional)
    run_alembic_migrations()
    
    # 6. Verify schema
    if not verify_database_schema():
        logger.error("Failed to verify database schema")
        return False
    
    # 7. Wait for Redis
    if not wait_for_redis('localhost', 6380):
        logger.error("Redis is not accessible")
        return False
    
    # 8. Verify Redis
    if not verify_redis_connection():
        logger.error("Redis verification failed")
        return False
    
    # 9. Set environment variables for tests
    os.environ['TESTING'] = 'true'
    os.environ['TEST_DATABASE_URL'] = f"postgresql://{pg_config['user']}:{pg_config['password']}@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
    os.environ['REDIS_URL'] = 'redis://localhost:6380/0'
    
    logger.info("=" * 60)
    logger.info("✓ Test environment setup complete!")
    logger.info("=" * 60)
    logger.info("\nYou can now run tests with:")
    logger.info("  pytest tests/")
    logger.info("\nOr run specific test categories:")
    logger.info("  pytest tests/unit/")
    logger.info("  pytest tests/integration/")
    
    return True

if __name__ == "__main__":
    success = setup_test_environment()
    sys.exit(0 if success else 1)