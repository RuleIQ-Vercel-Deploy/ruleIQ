#!/usr/bin/env python3
"""
Test script to verify Neon database connection
Ensures we're connecting to Neon cloud and not local PostgreSQL
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, inspect
from urllib.parse import urlparse

# Load environment variables
load_dotenv(".env.local")


async def test_neon_connection():
    """Test connection to Neon database and verify it's not local PostgreSQL."""

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False

    # Parse the URL to check if it's Neon
    parsed = urlparse(database_url.replace("postgresql+asyncpg://", "postgresql://"))

    print(f"🔍 Database Connection Details:")
    print(f"   Host: {parsed.hostname}")
    print(f"   Port: {parsed.port or 5432}")
    print(f"   Database: {parsed.path.lstrip('/')}")
    print(f"   Username: {parsed.username}")

    # Check if it's a Neon database
    is_neon = "neon.tech" in parsed.hostname if parsed.hostname else False
    is_local = (
        parsed.hostname in ["localhost", "127.0.0.1", "db", "postgres"]
        if parsed.hostname
        else False
    )

    if is_local:
        print("❌ ERROR: Database is pointing to local PostgreSQL!")
        print("   This should be a Neon cloud database.")
        return False

    if not is_neon:
        print("⚠️  WARNING: Database doesn't appear to be a Neon database")
        print(f"   Expected hostname to contain 'neon.tech', got: {parsed.hostname}")
    else:
        print("✅ Database URL points to Neon cloud service")

    # Test actual connection
    try:
        # Fix the database URL for asyncpg - it doesn't support sslmode in the URL
        # Instead, it uses ssl parameter
        if "sslmode=" in database_url:
            # Remove sslmode and channel_binding from URL
            import re

            clean_url = re.sub(r"[?&](sslmode|channel_binding)=[^&]*", "", database_url)
            if "?" not in clean_url and "&" in clean_url:
                clean_url = clean_url.replace("&", "?", 1)

            # For Neon, we need SSL
            connect_args = {
                "ssl": True,
                "server_settings": {"jit": "off"},  # Recommended for Neon
            }
        else:
            clean_url = database_url
            connect_args = {}

        engine = create_async_engine(
            clean_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args=connect_args,
        )

        async with engine.begin() as conn:
            # Test basic query
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"\n✅ Successfully connected to database!")
            print(f"   PostgreSQL version: {version}")

            # Check for Neon-specific settings
            result = await conn.execute(text("SHOW neon.tenant_id"))
            tenant_id = result.scalar()
            print(f"   Neon Tenant ID: {tenant_id}")

            # Get database size
            result = await conn.execute(
                text(
                    """
                SELECT pg_database_size(current_database()) as size,
                       current_database() as db_name
            """
                )
            )
            row = result.fetchone()
            size_mb = row.size / (1024 * 1024)
            print(f"   Database: {row.db_name}")
            print(f"   Size: {size_mb:.2f} MB")

            # List tables
            result = await conn.execute(
                text(
                    """
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """
                )
            )
            tables = [row[0] for row in result.fetchall()]
            print(f"\n📊 Tables in database ({len(tables)} total):")
            for table in tables[:10]:  # Show first 10 tables
                print(f"   - {table}")
            if len(tables) > 10:
                print(f"   ... and {len(tables) - 10} more tables")

            # Check for alembic version (migrations)
            result = await conn.execute(
                text(
                    """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'alembic_version'
                )
            """
                )
            )
            has_migrations = result.scalar()

            if has_migrations:
                result = await conn.execute(
                    text("SELECT version_num FROM alembic_version")
                )
                migration_version = result.scalar()
                print(f"\n🔄 Database migrations:")
                print(f"   Current version: {migration_version}")
            else:
                print(
                    f"\n⚠️  No alembic_version table found - migrations may not be initialized"
                )

        await engine.dispose()

        print("\n✅ Neon database connection verified successfully!")
        print("   The database is properly configured and accessible.")
        return True

    except Exception as e:
        print(f"\n❌ Failed to connect to database:")
        print(f"   Error: {str(e)}")

        if "connection refused" in str(e).lower():
            print(
                "\n💡 This error suggests the DATABASE_URL is pointing to a local database that's not running."
            )
            print(
                "   Please ensure DATABASE_URL in .env.local points to your Neon cloud database."
            )
        elif "authentication failed" in str(e).lower():
            print(
                "\n💡 Authentication failed. Please check your Neon database credentials."
            )
        elif "neon.tenant_id" in str(e).lower():
            print(
                "\n⚠️  The database connected but doesn't appear to be a Neon database."
            )
            print("   The 'neon.tenant_id' setting is not available.")

        return False


async def test_connection_pooling():
    """Test connection pooling configuration."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        return

    print("\n🔄 Testing connection pooling...")

    try:
        # Fix the database URL for asyncpg
        if "sslmode=" in database_url:
            import re

            clean_url = re.sub(r"[?&](sslmode|channel_binding)=[^&]*", "", database_url)
            if "?" not in clean_url and "&" in clean_url:
                clean_url = clean_url.replace("&", "?", 1)

            connect_args = {"ssl": True, "server_settings": {"jit": "off"}}
        else:
            clean_url = database_url
            connect_args = {}

        engine = create_async_engine(
            clean_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args=connect_args,
        )

        # Create multiple concurrent connections
        tasks = []
        for i in range(10):

            async def query_task(task_id):
                async with engine.begin() as conn:
                    result = await conn.execute(
                        text(f"SELECT {task_id} as id, NOW() as time")
                    )
                    return result.fetchone()

            tasks.append(query_task(i))

        results = await asyncio.gather(*tasks)
        print(f"   Successfully executed {len(results)} concurrent queries")

        await engine.dispose()

    except Exception as e:
        print(f"   Connection pooling test failed: {str(e)}")


async def main():
    """Run all database connection tests."""
    print("=" * 60)
    print("🚀 Neon Database Connection Test")
    print("=" * 60)

    success = await test_neon_connection()

    if success:
        await test_connection_pooling()

    print("\n" + "=" * 60)

    if not success:
        print("❌ Database connection test FAILED")
        print("\nNext steps:")
        print("1. Check DATABASE_URL in .env.local")
        print("2. Ensure it points to your Neon database (not localhost)")
        print("3. Verify Neon database credentials are correct")
        print("4. Check if Neon database is active (not suspended)")
        sys.exit(1)
    else:
        print("✅ All database tests PASSED")
        print("\nThe application is correctly configured to use Neon database.")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
