#!/usr/bin/env python3
"""
Database Health Check Script

This script validates connectivity and basic operations for PostgreSQL and Redis.
Reads connection strings from environment variables and performs health checks.

Environment Variables:
- DATABASE_URL: PostgreSQL connection string
- REDIS_URL: Redis connection string
- VERBOSE: Set to "true" for detailed output
- TIMEOUT: Connection timeout in seconds (default: 10)
"""

import os
import sys
import time
import traceback
import argparse
from typing import Dict, Any, Optional

# PostgreSQL health check
def check_postgresql(database_url: str, timeout: int = 10, verbose: bool = False) -> Dict[str, Any]:
    """Test PostgreSQL connectivity and basic operations."""
    result = {
        "service": "PostgreSQL",
        "status": "unknown",
        "time_ms": 0,
        "error": None,
        "details": {}
    }

    if not database_url:
        result["status"] = "failed"
        result["error"] = "DATABASE_URL not set"
        return result

    start_time = time.time()

    try:
        import psycopg
        from psycopg import sql
    except ImportError:
        try:
            import psycopg2 as psycopg
            from psycopg2 import sql
        except ImportError as e:
            result["status"] = "failed"
            result["error"] = f"psycopg/psycopg2 not installed: {e}"
            result["time_ms"] = int((time.time() - start_time) * 1000)
            return result

    try:
        # Connect to database
        if verbose:
            print(f"  📡 Connecting to PostgreSQL...")

        if "psycopg2" in str(psycopg.__name__):
            conn = psycopg.connect(database_url, connect_timeout=timeout)
        else:
            conn = psycopg.connect(database_url, connect_timeout=timeout)

        result["details"]["connected"] = True

        # Create cursor
        cur = conn.cursor()

        # Test 1: Simple SELECT
        if verbose:
            print(f"  🔍 Testing SELECT 1...")
        cur.execute("SELECT 1")
        row = cur.fetchone()
        if row and row[0] == 1:
            result["details"]["select_test"] = "passed"
        else:
            result["details"]["select_test"] = "failed"

        # Test 2: Get database version
        cur.execute("SELECT version()")
        version = cur.fetchone()
        if version:
            result["details"]["version"] = version[0].split()[0:2]

        # Test 3: Transaction test
        if verbose:
            print(f"  🔄 Testing transaction...")

        # Begin transaction
        conn.begin() if hasattr(conn, 'begin') else cur.execute("BEGIN")

        # Create temporary table
        temp_table = f"health_check_{int(time.time())}"
        cur.execute(
            sql.SQL("CREATE TEMP TABLE {} (id INTEGER PRIMARY KEY, test_value TEXT)").format(
                sql.Identifier(temp_table)
            )
        )

        # Insert test data
        cur.execute(
            sql.SQL("INSERT INTO {} (id, test_value) VALUES (%s, %s)").format(
                sql.Identifier(temp_table)
            ),
            (1, "health_check_test")
        )

        # Select test data
        cur.execute(
            sql.SQL("SELECT test_value FROM {} WHERE id = %s").format(
                sql.Identifier(temp_table)
            ),
            (1,)
        )
        test_row = cur.fetchone()

        if test_row and test_row[0] == "health_check_test":
            result["details"]["transaction_test"] = "passed"
        else:
            result["details"]["transaction_test"] = "failed"

        # Rollback transaction
        conn.rollback()
        result["details"]["rollback_test"] = "passed"

        # Close connections
        cur.close()
        conn.close()

        # Calculate elapsed time
        result["time_ms"] = int((time.time() - start_time) * 1000)

        # Determine overall status
        if all(v == "passed" for k, v in result["details"].items() if k.endswith("_test")):
            result["status"] = "healthy"
        else:
            result["status"] = "degraded"

    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        result["time_ms"] = int((time.time() - start_time) * 1000)
        if verbose:
            traceback.print_exc()

    return result


# Redis health check
def check_redis(redis_url: str, timeout: int = 10, verbose: bool = False) -> Dict[str, Any]:
    """Test Redis connectivity and basic operations."""
    result = {
        "service": "Redis",
        "status": "unknown",
        "time_ms": 0,
        "error": None,
        "details": {}
    }

    if not redis_url:
        result["status"] = "failed"
        result["error"] = "REDIS_URL not set"
        return result

    start_time = time.time()

    try:
        import redis
    except ImportError as e:
        result["status"] = "failed"
        result["error"] = f"redis-py not installed: {e}"
        result["time_ms"] = int((time.time() - start_time) * 1000)
        return result

    try:
        # Parse Redis URL and connect
        if verbose:
            print(f"  📡 Connecting to Redis...")

        client = redis.from_url(redis_url, socket_connect_timeout=timeout)

        # Test 1: PING
        if verbose:
            print(f"  🔍 Testing PING...")
        ping_response = client.ping()
        result["details"]["ping_test"] = "passed" if ping_response else "failed"
        result["details"]["connected"] = True

        # Test 2: SET/GET/DEL
        if verbose:
            print(f"  🔄 Testing SET/GET/DEL...")

        test_key = f"health_check:{int(time.time())}"
        test_value = "redis_health_check_test"

        # SET operation
        set_result = client.set(test_key, test_value, ex=60)  # Expire in 60 seconds
        result["details"]["set_test"] = "passed" if set_result else "failed"

        # GET operation
        get_result = client.get(test_key)
        if get_result:
            get_value = get_result.decode() if isinstance(get_result, bytes) else get_result
            result["details"]["get_test"] = "passed" if get_value == test_value else "failed"
        else:
            result["details"]["get_test"] = "failed"

        # DEL operation
        del_result = client.delete(test_key)
        result["details"]["del_test"] = "passed" if del_result > 0 else "failed"

        # Test 3: Get server info
        try:
            info = client.info()
            result["details"]["version"] = info.get("redis_version", "unknown")
            result["details"]["used_memory_human"] = info.get("used_memory_human", "unknown")
        except Exception:
            # Some Redis configurations might not allow INFO command
            result["details"]["version"] = "unavailable"

        # Close connection
        client.close()

        # Calculate elapsed time
        result["time_ms"] = int((time.time() - start_time) * 1000)

        # Determine overall status
        if all(v == "passed" for k, v in result["details"].items() if k.endswith("_test")):
            result["status"] = "healthy"
        else:
            result["status"] = "degraded"

    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        result["time_ms"] = int((time.time() - start_time) * 1000)
        if verbose:
            traceback.print_exc()

    return result


def print_result(result: Dict[str, Any], verbose: bool = False):
    """Print health check result."""
    icon = {
        "healthy": "✅",
        "degraded": "⚠️",
        "failed": "❌",
        "unknown": "❓"
    }.get(result["status"], "❓")

    print(f"{icon} {result['service']}: {result['status'].upper()} ({result['time_ms']}ms)")

    if result["error"]:
        print(f"   Error: {result['error']}")

    if verbose and result["details"]:
        for key, value in result["details"].items():
            if not key.endswith("_test"):
                print(f"   {key}: {value}")
            else:
                test_icon = "✅" if value == "passed" else "❌"
                print(f"   {test_icon} {key}: {value}")


def main():
    """Main health check function."""
    parser = argparse.ArgumentParser(description="Database Health Check")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--timeout", type=int, default=10, help="Connection timeout in seconds")
    args = parser.parse_args()

    # Also check environment variable for verbose
    verbose = args.verbose or os.environ.get("VERBOSE", "").lower() == "true"
    timeout = args.timeout

    print("🏥 Database Health Check")
    print("=" * 60)

    # Get database URLs from environment
    database_url = os.environ.get("DATABASE_URL")
    redis_url = os.environ.get("REDIS_URL")

    if not database_url and not redis_url:
        print("❌ Neither DATABASE_URL nor REDIS_URL is set!")
        print("   Please set at least one database connection string.")
        sys.exit(1)

    results = []

    # Check PostgreSQL
    if database_url:
        print("\n📊 Checking PostgreSQL...")
        pg_result = check_postgresql(database_url, timeout, verbose)
        print_result(pg_result, verbose)
        results.append(pg_result)

    # Check Redis
    if redis_url:
        print("\n📊 Checking Redis...")
        redis_result = check_redis(redis_url, timeout, verbose)
        print_result(redis_result, verbose)
        results.append(redis_result)

    # Print summary
    print("\n" + "=" * 60)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 60)

    all_healthy = True
    total_time = 0

    for result in results:
        total_time += result["time_ms"]
        status = result["status"]
        
        if status != "healthy":
            all_healthy = False

        icon = {
            "healthy": "✅",
            "degraded": "⚠️",
            "failed": "❌",
            "unknown": "❓"
        }.get(status, "❓")

        print(f"{icon} {result['service']}: {status.upper()}")

    print(f"\n⏱️  Total time: {total_time}ms")

    if all_healthy:
        print("✅ All database health checks passed!")
        sys.exit(0)
    else:
        print("❌ Some database health checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()