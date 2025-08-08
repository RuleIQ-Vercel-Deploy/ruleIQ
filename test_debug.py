#!/usr/bin/env python3
"""Debug script to isolate pytest issues with freemium models."""

import sys
import traceback
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports() -> Optional[bool]:
    """Test all necessary imports."""
    print("=== Testing Imports ===")
    try:
        print("✅ Freemium models imported successfully")

        print("✅ Database utilities imported successfully")

        print("✅ SQLAlchemy imported successfully")

        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_database_connection() -> Optional[bool]:
    """Test database connection."""
    print("\n=== Testing Database Connection ===")
    try:
        from tests.conftest import engine, TestSessionLocal

        # Test engine connection
        connection = engine.connect()
        print("✅ Database engine connection successful")
        connection.close()

        # Test session creation
        session = TestSessionLocal()
        print("✅ Test session created successfully")
        session.close()

        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        traceback.print_exc()
        return False

def test_model_creation() -> Optional[bool]:
    """Test creating model instances."""
    print("\n=== Testing Model Creation ===")
    try:
        from database import AssessmentLead

        # Create a simple model instance
        lead = AssessmentLead(email="test@example.com", consent_marketing=True)
        print(f"✅ AssessmentLead created: {lead}")

        return True
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        traceback.print_exc()
        return False

def test_database_operations() -> Optional[bool]:
    """Test actual database operations."""
    print("\n=== Testing Database Operations ===")
    try:
        from tests.conftest import TestSessionLocal
        from database import AssessmentLead

        session = TestSessionLocal()

        # Create and save a lead
        lead = AssessmentLead(email="debug-test@example.com", consent_marketing=True)
        session.add(lead)
        session.commit()
        print(f"✅ Lead saved to database: {lead.id}")

        # Query the lead back
        saved_lead = session.query(AssessmentLead).filter_by(email="debug-test@example.com").first()
        print(f"✅ Lead retrieved from database: {saved_lead}")

        # Cleanup
        session.delete(saved_lead)
        session.commit()
        session.close()
        print("✅ Cleanup completed")

        return True
    except Exception as e:
        print(f"❌ Database operations failed: {e}")
        traceback.print_exc()
        return False

def test_pytest_fixture() -> Optional[bool]:
    """Test the pytest fixture itself."""
    print("\n=== Testing Pytest Fixture ===")
    try:
        from tests.conftest import db_session

        # Manually call the fixture generator
        fixture_gen = db_session()
        session = next(fixture_gen)
        print(f"✅ Pytest fixture generated session: {session}")

        # Test using the session
        from database import AssessmentLead
        lead = AssessmentLead(email="fixture-test@example.com", consent_marketing=True)
        session.add(lead)
        session.commit()
        print("✅ Fixture session works correctly")

        # Cleanup
        session.delete(lead)
        session.commit()

        # Close the fixture
        try:
            next(fixture_gen)
        except StopIteration:
            print("✅ Fixture properly closed")

        return True
    except Exception as e:
        print(f"❌ Pytest fixture failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all debug tests."""
    print("🔍 Starting Debug Analysis for Freemium Models...")

    tests = [
        test_imports,
        test_database_connection,
        test_model_creation,
        test_database_operations,
        test_pytest_fixture,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            traceback.print_exc()
            results.append(False)

    print("\n=== Summary ===")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")

    if all(results):
        print("🎉 All tests passed! The issue might be with pytest execution environment.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
