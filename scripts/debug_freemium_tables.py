#!/usr/bin/env python3
"""
Debug script to test freemium table creation and database connectivity.
"""
import os
import sys
import traceback
from sqlalchemy import create_engine, text, inspect

# Set environment
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = (
    "postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
)

# Add project to path
sys.path.insert(0, "/home/omar/Documents/ruleIQ")


def main() -> None:
    print("=== Freemium Database Table Debug Script ===")

    try:
        # Test database connection
        print("1. Testing Database Connection...")
        db_url = os.environ["DATABASE_URL"]
        if "+asyncpg" in db_url:
            db_url = db_url.replace("+asyncpg", "+psycopg2")
        elif "postgresql://" in db_url and "+psycopg2" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

        engine = create_engine(db_url, echo=True)

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connected: {version}")

        # Check existing tables
        print("\n2. Checking existing tables...")
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Found {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")

        # Check if freemium tables exist
        freemium_tables = [
            "assessment_leads",
            "freemium_assessment_sessions",
            "ai_question_bank",
            "lead_scoring_events",
            "conversion_events",  # Fixed: should be plural
        ]

        print("\n3. Checking freemium table status...")
        for table in freemium_tables:
            exists = table in tables
            status = "✅ EXISTS" if exists else "❌ MISSING"
            print(f"  {table}: {status}")

        # Try to import freemium models
        print("\n4. Testing model imports...")
        try:
            from database.assessment_lead import AssessmentLead

            print("✅ AssessmentLead imported successfully")
        except Exception as e:
            print(f"❌ AssessmentLead import failed: {e}")
            traceback.print_exc()

        try:
            print("✅ FreemiumAssessmentSession imported successfully")
        except Exception as e:
            print(f"❌ FreemiumAssessmentSession import failed: {e}")
            traceback.print_exc()

        try:
            print("✅ AIQuestionBank imported successfully")
        except Exception as e:
            print(f"❌ AIQuestionBank import failed: {e}")
            traceback.print_exc()

        try:
            print("✅ LeadScoringEvent imported successfully")
        except Exception as e:
            print(f"❌ LeadScoringEvent import failed: {e}")
            traceback.print_exc()

        try:
            print("✅ ConversionEvent imported successfully")
        except Exception as e:
            print(f"❌ ConversionEvent import failed: {e}")
            traceback.print_exc()

        # Test creating tables with Base.metadata.create_all
        print("\n5. Testing Base.metadata.create_all...")
        try:
            from database.db_setup import Base

            Base.metadata.create_all(bind=engine)
            print("✅ Base.metadata.create_all executed without error")
        except Exception as e:
            print(f"❌ Base.metadata.create_all failed: {e}")
            traceback.print_exc()

        # Re-check tables after create_all
        print("\n6. Re-checking tables after create_all...")
        inspector = inspect(engine)
        tables_after = inspector.get_table_names()
        print(f"Found {len(tables_after)} tables after create_all:")

        for table in freemium_tables:
            exists = table in tables_after
            status = "✅ EXISTS" if exists else "❌ STILL MISSING"
            print(f"  {table}: {status}")

        # Test creating a simple record
        print("\n7. Testing record creation...")
        try:
            from database.assessment_lead import AssessmentLead
            from sqlalchemy.orm import sessionmaker

            Session = sessionmaker(bind=engine)
            session = Session()

            # Try to create a test record
            lead = AssessmentLead(email="debug@test.com", consent_marketing=True)
            session.add(lead)
            session.commit()
            print("✅ Test AssessmentLead record created successfully")

            # Clean up
            session.delete(lead)
            session.commit()
            session.close()
            print("✅ Test record cleaned up")

        except Exception as e:
            print(f"❌ Record creation failed: {e}")
            traceback.print_exc()
            try:
                session.rollback()
                session.close()
            except:
                pass

    except Exception as e:
        print(f"❌ Script failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
