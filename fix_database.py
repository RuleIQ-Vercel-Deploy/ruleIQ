#!/usr/bin/env python3
"""
Fix database by creating tables directly
"""
import os
import asyncio

# Set test environment variables FIRST
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
os.environ["SECRET_KEY"] = "test_secret_key_for_pytest_sessions"
os.environ["GOOGLE_API_KEY"] = "test_google_api_key"

async def fix_database():
    """Create database tables directly."""
    print("🔧 Fixing database by creating tables...")
    
    try:
        # Import all models to register them with Base
        print("📦 Importing models...")
        from database.db_setup import Base
        from database.user import User
        from database.business_profile import BusinessProfile
        from database.compliance_framework import ComplianceFramework
        from database.evidence_item import EvidenceItem
        from database.generated_policy import GeneratedPolicy
        from database.implementation_plan import ImplementationPlan
        from database.assessment_session import AssessmentSession
        from database.readiness_assessment import ReadinessAssessment
        from database.chat_conversation import ChatConversation
        from database.chat_message import ChatMessage
        from database.integration_configuration import IntegrationConfiguration
        from database.report_schedule import ReportSchedule
        
        print("✅ Models imported")
        
        # Create engine directly (bypassing the broken _init_async_db)
        print("🔌 Creating database engine...")
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        # Use the working connection string
        db_url = "postgresql+asyncpg://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb"
        
        engine = create_async_engine(
            db_url,
            connect_args={"ssl": True},
            echo=False
        )
        
        print("✅ Engine created")
        
        # Create all tables
        print("🏗️  Creating tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        print("✅ Tables created successfully!")
        
        # Test the connection
        print("🧪 Testing connection...")
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Connection test: {row}")
            
        # Test that tables exist
        print("📋 Checking tables...")
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = result.fetchall()
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")
                
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function."""
    print("🚀 NexCompli Database Fix")
    print("=" * 30)
    
    success = await fix_database()
    
    if success:
        print("\n🎉 Database fixed successfully!")
        print("✅ Ready to run tests!")
    else:
        print("\n💥 Database fix failed!")

if __name__ == "__main__":
    asyncio.run(main())
