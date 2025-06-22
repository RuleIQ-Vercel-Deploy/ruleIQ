#!/usr/bin/env python3
"""
Create database tables for tests
"""
import os
import asyncio
import sys

# Set test environment variables FIRST
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
os.environ["SECRET_KEY"] = "test_secret_key_for_pytest_sessions"
os.environ["GOOGLE_API_KEY"] = "test_google_api_key"

async def create_tables():
    """Create all database tables for tests."""
    print("🔧 Creating test database tables...")
    
    try:
        # Import after setting environment variables
        from database.db_setup import Base, _init_async_db, _async_engine
        
        # Import all models to ensure they're registered with Base
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
        
        print("📦 Models imported successfully")
        
        # Initialize async database
        print("🔌 Initializing database connection...")
        _init_async_db()
        
        if _async_engine is None:
            print("❌ Failed to initialize database engine")
            return False
            
        print("✅ Database engine initialized")
        
        # Create all tables
        print("🏗️  Creating tables...")
        async with _async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        print("✅ All tables created successfully!")
        
        # Test connection
        print("🧪 Testing database connection...")
        from database.db_setup import get_async_db
        async for db in get_async_db():
            from sqlalchemy import text
            result = await db.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Connection test successful: {row}")
            break
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function."""
    print("🚀 NexCompli Test Database Setup")
    print("=" * 40)
    
    success = await create_tables()
    
    if success:
        print("\n🎉 Database setup completed successfully!")
        print("✅ Ready to run tests!")
    else:
        print("\n💥 Database setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
