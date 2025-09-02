#!/usr/bin/env python3
"""Test database connection with current settings."""

import os
import sys
from urllib.parse import urlparse
import psycopg2
from psycopg2 import OperationalError


def test_connection():
    """Test the database connection using the DATABASE_URL from .env"""
    # Load .env file
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        return False

    print(f"Testing connection to: {database_url}")

    # Parse the database URL
    try:
        parsed = urlparse(database_url)
        connection_params = {
            "host": parsed.hostname,
            "port": parsed.port or 5432,
            "user": parsed.username,
            "password": parsed.password,
            "database": parsed.path.lstrip("/"),
        }

        print("\nConnection parameters:")
        print(f"  Host: {connection_params['host']}")
        print(f"  Port: {connection_params['port']}")
        print(f"  User: {connection_params['user']}")
        print(f"  Database: {connection_params['database']}")
        print(
            f"  Password: {'*' * len(connection_params['password']) if connection_params['password'] else 'None'}",
        )

        # Try to connect
        print("\nAttempting connection...")
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print("\nSUCCESS! Connected to PostgreSQL")
        print(f"PostgreSQL version: {version[0]}")

        # Check if database exists
        cursor.execute("SELECT current_database();")
        current_db = cursor.fetchone()
        print(f"Current database: {current_db[0]}")

        cursor.close()
        conn.close()
        return True

    except OperationalError as e:
        print("\nERROR: Failed to connect to database")
        print(f"Error details: {e}")
        print("\nPossible solutions:")
        print("1. Check if PostgreSQL is running: systemctl status postgresql")
        print("2. Verify the password is correct")
        print("3. Run the setup script: ./scripts/fix_database_auth.sh")
        print("4. Check pg_hba.conf for authentication settings")
        return False
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
