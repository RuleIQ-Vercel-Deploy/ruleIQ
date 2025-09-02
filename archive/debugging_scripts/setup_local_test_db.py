#!/usr/bin/env python3
"""
Setup local test database for pytest.
This creates the test database and user needed for local testing.
"""

import subprocess
import sys
import os
from typing import Optional


def run_sql_command(sql, database="postgres", user="postgres"):
    """Run a SQL command using psql."""
    try:
        cmd = ["sudo", "-u", "postgres", "psql", "-d", database, "-c", sql]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✓ SQL executed successfully: {sql[:50]}...")
            return True, result.stdout
        else:
            print(f"✗ SQL failed: {sql[:50]}...")
            print(f"Error: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"✗ SQL command timed out: {sql[:50]}...")
        return False, "Timeout"
    except Exception as e:
        print(f"✗ SQL command failed: {e}")
        return False, str(e)


def setup_test_database() -> Optional[bool]:
    """Set up the test database and user."""
    print("Setting up local test database for pytest...")
    print("=" * 60)

    # Create test user
    print("\n1. Creating test user...")
    success, output = run_sql_command("CREATE USER test_user WITH PASSWORD 'test_pass';")
    if not success and "already exists" not in output:
        print("Failed to create user")
        return False

    # Create test database
    print("\n2. Creating test database...")
    success, output = run_sql_command("CREATE DATABASE test_compliancegpt OWNER test_user;")
    if not success and "already exists" not in output:
        print("Failed to create database")
        return False

    # Grant privileges
    print("\n3. Granting privileges...")
    success, output = run_sql_command(
        "GRANT ALL PRIVILEGES ON DATABASE test_compliancegpt TO test_user;"
    )
    if not success:
        print("Failed to grant privileges")
        return False

    # Test connection
    print("\n4. Testing connection...")
    try:
        cmd = [
            "psql",
            "-h",
            "localhost",
            "-U",
            "test_user",
            "-d",
            "test_compliancegpt",
            "-c",
            "SELECT 1;",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "PGPASSWORD": "test_pass"},
        )
        if result.returncode == 0:
            print("✓ Test connection successful!")
            return True
        else:
            print(f"✗ Test connection failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Test connection error: {e}")
        return False


if __name__ == "__main__":
    success = setup_test_database()
    if success:
        print("\n" + "=" * 60)
        print("✓ Test database setup completed successfully!")
        print("You can now run pytest tests.")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("✗ Test database setup failed!")
        print("Please check the errors above and try again.")
        sys.exit(1)
