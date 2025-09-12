#!/usr/bin/env python3
"""
Test Database Setup Script
Ensures test database is ready for running security tests
"""
import os
import sys
import subprocess
import time
import psycopg2
from psycopg2 import OperationalError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_docker_running():
    """Check if Docker is running"""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        logger.error("Docker is not installed")
        return False


def is_postgres_running(host="localhost", port=5433):
    """Check if PostgreSQL is accessible"""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user="postgres",
            password="postgres",
            database="postgres",
            connect_timeout=3
        )
        conn.close()
        return True
    except OperationalError:
        return False


def start_test_database():
    """Start test database using Docker"""
    logger.info("Starting test database container...")
    
    # Check if container exists
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", "name=ruleiq-test-db", "--format", "{{.Names}}"],
        capture_output=True,
        text=True
    )
    
    container_exists = "ruleiq-test-db" in result.stdout
    
    if container_exists:
        # Stop and remove existing container
        logger.info("Removing existing test database container...")
        subprocess.run(["docker", "stop", "ruleiq-test-db"], capture_output=True)
        subprocess.run(["docker", "rm", "ruleiq-test-db"], capture_output=True)
    
    # Start new container
    cmd = [
        "docker", "run",
        "--name", "ruleiq-test-db",
        "-e", "POSTGRES_USER=postgres",
        "-e", "POSTGRES_PASSWORD=postgres",
        "-e", "POSTGRES_DB=compliance_test",
        "-p", "5433:5432",
        "-d",
        "postgres:15-alpine"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error(f"Failed to start database: {result.stderr}")
        return False
    
    logger.info("Test database container started")
    
    # Wait for database to be ready
    logger.info("Waiting for database to be ready...")
    for i in range(30):
        if is_postgres_running():
            logger.info("Database is ready!")
            return True
        time.sleep(1)
        if i % 5 == 0:
            logger.info(f"Still waiting... ({i} seconds)")
    
    logger.error("Database failed to start in 30 seconds")
    return False


def start_test_redis():
    """Start test Redis using Docker"""
    logger.info("Starting test Redis container...")
    
    # Check if container exists
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", "name=ruleiq-test-redis", "--format", "{{.Names}}"],
        capture_output=True,
        text=True
    )
    
    container_exists = "ruleiq-test-redis" in result.stdout
    
    if container_exists:
        # Stop and remove existing container
        logger.info("Removing existing test Redis container...")
        subprocess.run(["docker", "stop", "ruleiq-test-redis"], capture_output=True)
        subprocess.run(["docker", "rm", "ruleiq-test-redis"], capture_output=True)
    
    # Start new container
    cmd = [
        "docker", "run",
        "--name", "ruleiq-test-redis",
        "-p", "6380:6379",
        "-d",
        "redis:7-alpine"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error(f"Failed to start Redis: {result.stderr}")
        return False
    
    logger.info("Test Redis container started")
    return True


def setup_test_environment():
    """Setup complete test environment"""
    logger.info("Setting up test environment...")
    
    # Check Docker
    if not check_docker_running():
        logger.error("Docker is not running. Please start Docker first.")
        return False
    
    # Start PostgreSQL
    if not is_postgres_running():
        if not start_test_database():
            return False
    else:
        logger.info("Test database is already running")
    
    # Start Redis
    if not start_test_redis():
        logger.warning("Redis failed to start, but tests can run without it")
    
    # Create test database if needed
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            user="postgres",
            password="postgres",
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = 'compliance_test'"
        )
        if not cursor.fetchone():
            cursor.execute("CREATE DATABASE compliance_test")
            logger.info("Created compliance_test database")
        else:
            logger.info("compliance_test database already exists")
        
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to create test database: {e}")
        return False
    
    # Set environment variables
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5433/compliance_test"
    os.environ["TEST_DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5433/compliance_test"
    os.environ["REDIS_URL"] = "redis://localhost:6380/0"
    
    logger.info("Test environment setup complete!")
    logger.info("\nEnvironment variables set:")
    logger.info("  TESTING=true")
    logger.info("  DATABASE_URL=postgresql://postgres:postgres@localhost:5433/compliance_test")
    logger.info("  REDIS_URL=redis://localhost:6380/0")
    logger.info("\nYou can now run tests with: pytest")
    
    return True


def teardown_test_environment():
    """Teardown test environment"""
    logger.info("Tearing down test environment...")
    
    # Stop containers
    subprocess.run(["docker", "stop", "ruleiq-test-db"], capture_output=True)
    subprocess.run(["docker", "rm", "ruleiq-test-db"], capture_output=True)
    subprocess.run(["docker", "stop", "ruleiq-test-redis"], capture_output=True)
    subprocess.run(["docker", "rm", "ruleiq-test-redis"], capture_output=True)
    
    logger.info("Test environment teardown complete")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup test database environment")
    parser.add_argument(
        "--teardown",
        action="store_true",
        help="Teardown test environment"
    )
    
    args = parser.parse_args()
    
    if args.teardown:
        teardown_test_environment()
    else:
        if setup_test_environment():
            sys.exit(0)
        else:
            sys.exit(1)