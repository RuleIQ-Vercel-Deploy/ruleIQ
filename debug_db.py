#!/usr/bin/env python3
"""
Debug database connection issues
"""
import os
import asyncio

# Set test environment variables FIRST
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
os.environ["SECRET_KEY"] = "test_secret_key_for_pytest_sessions"
os.environ["GOOGLE_API_KEY"] = "test_google_api_key"

async def debug_connection():
    """Debug the database connection step by step."""
    print("🔍 Debugging database connection...")
    
    try:
        print("1. Checking environment variables...")
        db_url = os.getenv("DATABASE_URL")
        print(f"   DATABASE_URL: {db_url[:50]}...")
        
        print("2. Importing database setup...")
        from database.db_setup import _get_configured_database_urls, _init_async_db, _async_engine
        
        print("3. Getting configured URLs...")
        raw_url, sync_url, async_url = _get_configured_database_urls()
        print(f"   Raw URL: {raw_url[:50]}...")
        print(f"   Sync URL: {sync_url[:50]}...")
        print(f"   Async URL: {async_url[:50]}...")
        
        print("4. Initializing async database...")
        try:
            _init_async_db()
            print("   ✅ _init_async_db() completed without exception")
        except Exception as init_error:
            print(f"   ❌ _init_async_db() failed: {init_error}")
            import traceback
            traceback.print_exc()

        print(f"5. Checking engine: {_async_engine}")

        # Let's try to manually create the engine
        print("6. Manually creating engine...")
        from sqlalchemy.ext.asyncio import create_async_engine

        manual_url = async_url.replace("?sslmode=require", "").replace("&sslmode=require", "")
        print(f"   Manual URL: {manual_url[:50]}...")

        try:
            manual_engine = create_async_engine(
                manual_url,
                connect_args={"ssl": True},
                echo=False
            )
            print(f"   ✅ Manual engine created: {manual_engine}")

            # Test the manual engine
            async with manual_engine.begin() as conn:
                result = await conn.execute("SELECT 1 as test")
                row = result.fetchone()
                print(f"   ✅ Manual engine test successful: {row}")

            await manual_engine.dispose()

        except Exception as manual_error:
            print(f"   ❌ Manual engine failed: {manual_error}")
            import traceback
            traceback.print_exc()
        
        if _async_engine is None:
            print("❌ Engine is still None!")
            return False
        else:
            print("✅ Engine created successfully!")
            return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(debug_connection())
