"""
Test database connection directly
"""
import os
import asyncio

# Set environment variables first
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"

async def test_neon_connection():
    """Test direct connection to Neon database"""
    print("Testing Neon database connection...")
    
    try:
        from database.db_setup import _init_async_db, _async_engine
        
        print("1. Initializing async database...")
        _init_async_db()
        
        print("2. Checking engine:", _async_engine)
        
        if _async_engine is None:
            print("✗ Engine is None after initialization")
            return False
            
        print("3. Testing connection...")
        async with _async_engine.begin() as conn:
            result = await conn.execute("SELECT 1 as test")
            row = result.fetchone()
            print(f"✓ Connection successful! Result: {row}")
            
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_neon_connection())
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
