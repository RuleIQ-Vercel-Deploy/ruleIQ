#!/usr/bin/env python3
"""
Test database connection and identify issues with async/sync mixing.
"""

import asyncio
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Set up environment
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"

def test_sync_connection():
    """Test synchronous database connection."""
    print("Testing synchronous connection...")
    
    db_url = os.environ["DATABASE_URL"]
    sync_url = db_url.replace("postgresql://", "postgresql+psycopg2://")
    
    try:
        engine = create_engine(sync_url, poolclass=NullPool, echo=False)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"Sync connection successful: {result.scalar()}")
        engine.dispose()
        return True
    except Exception as e:
        print(f"Sync connection failed: {e}")
        return False

async def test_async_connection():
    """Test asynchronous database connection."""
    print("\nTesting asynchronous connection...")
    
    db_url = os.environ["DATABASE_URL"]
    async_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    
    # Remove sslmode for asyncpg
    if "sslmode=require" in async_url:
        async_url = async_url.replace("?sslmode=require", "")
        ssl_config = {"ssl": "require"}
    else:
        ssl_config = {}
    
    try:
        engine = create_async_engine(
            async_url, 
            poolclass=NullPool, 
            echo=False,
            connect_args=ssl_config
        )
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"Async connection successful: {result.scalar()}")
        
        await engine.dispose()
        return True
    except Exception as e:
        print(f"Async connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_table_creation():
    """Test table creation in test database."""
    print("\nTesting table operations...")
    
    db_url = os.environ["DATABASE_URL"]
    async_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    
    if "sslmode=require" in async_url:
        async_url = async_url.replace("?sslmode=require", "")
        ssl_config = {"ssl": "require"}
    else:
        ssl_config = {}
    
    try:
        engine = create_async_engine(
            async_url,
            poolclass=NullPool,
            echo=False,
            connect_args=ssl_config
        )
        
        # Check if tables exist
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"Found {len(tables)} tables: {', '.join(tables[:5])}...")
        
        await engine.dispose()
        return True
    except Exception as e:
        print(f"Table operations failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Database Connection Test Suite")
    print("=" * 50)
    
    # Test sync connection
    sync_ok = test_sync_connection()
    
    # Test async connection
    async_ok = asyncio.run(test_async_connection())
    
    # Test table operations
    tables_ok = asyncio.run(test_table_creation())
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"  Sync Connection: {'✓' if sync_ok else '✗'}")
    print(f"  Async Connection: {'✓' if async_ok else '✗'}")
    print(f"  Table Operations: {'✓' if tables_ok else '✗'}")
    
    if all([sync_ok, async_ok, tables_ok]):
        print("\nAll tests passed! Database connectivity is working.")
        return 0
    else:
        print("\nSome tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())