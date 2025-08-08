#!/usr/bin/env python3
"""Manual test to verify freemium models work with the exact test setup."""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set test environment exactly like conftest.py
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = (
    "postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
)
os.environ["SECRET_KEY"] = "test_secret_key_for_pytest_sessions"

# Initialize the exact same way as tests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Optional

# Get database URL and convert to sync (same as conftest.py)
db_url = os.environ["DATABASE_URL"]
if "+asyncpg" in db_url:
    db_url = db_url.replace("+asyncpg", "+psycopg2")
elif "postgresql://" in db_url and "+psycopg2" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# Create engine with proper settings for tests (same as conftest.py)
engine = create_engine(
    db_url,
    poolclass=StaticPool,
    echo=False,
    connect_args={"connect_timeout": 10},
)

# Create session factory (same as conftest.py)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_with_exact_setup() -> Optional[bool]:
    """Test using the exact same setup as pytest conftest."""
    print("=== Using Exact Test Setup ===")

    # Import models and ensure tables exist
    from database import Base, AssessmentLead
    print("✅ Models imported")

    # Create all tables (this is what we added to conftest)
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")

    # Create a test session
    session = TestSessionLocal()
    print("✅ Test session created")

    try:
        # Test basic model creation
        lead = AssessmentLead(email="manual-test@example.com", consent_marketing=True)
        session.add(lead)
        session.commit()
        print(f"✅ Lead saved: {lead.id}")

        # Test querying
        saved_lead = session.query(AssessmentLead).filter_by(email="manual-test@example.com").first()
        print(f"✅ Lead retrieved: {saved_lead}")

        # Cleanup
        session.delete(saved_lead)
        session.commit()
        print("✅ Cleanup completed")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

def simulate_pytest_test() -> Optional[bool]:
    """Simulate the exact pytest test that's failing."""
    print("\n=== Simulating Pytest Test ===")

    try:
        from database import AssessmentLead

        # Simulate the db_session fixture
        session = TestSessionLocal()

        try:
            # This is the exact test content
            email = "test@example.com"

            # Act
            lead = AssessmentLead(
                email=email,
                consent_marketing=True
            )
            session.add(lead)
            session.commit()

            # Assert
            assert lead.id is not None
            assert lead.email == email
            assert lead.consent_marketing is True
            assert lead.lead_score == 0
            assert lead.created_at is not None
            assert lead.updated_at is not None

            print("✅ Pytest simulation PASSED!")

            # Cleanup
            session.delete(lead)
            session.commit()

            return True

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    except Exception as e:
        print(f"❌ Pytest simulation FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Manual Test with Exact Setup")

    success1 = test_with_exact_setup()
    success2 = simulate_pytest_test()

    if success1 and success2:
        print("\n🎉 Both tests PASSED! The models work correctly.")
        print("The issue might be with pytest configuration or environment.")
    else:
        print("\n❌ Tests failed. Check errors above.")

    sys.exit(0 if (success1 and success2) else 1)
