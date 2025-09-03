#!/usr/bin/env python3
"""
from __future__ import annotations

Simple test to debug freemium model issues without pytest configuration interference.
"""
import os
import sys
import traceback
from pathlib import Path
from typing import Optional

# Set environment
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = (
    os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/compliance_test?sslmode=require"),
)

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_freemium_model_directly() -> Optional[bool]:
    """Test freemium models directly without pytest overhead."""
    print("=== Direct Freemium Model Test ===")

    try:
        # Import test fixtures and setup
        sys.path.insert(0, str(project_root / "tests"))
        from conftest import TestSessionLocal

        # Import the freemium models
        from database.assessment_lead import AssessmentLead
        from database.freemium_assessment_session import FreemiumAssessmentSession
        from database.ai_question_bank import AIQuestionBank
        from database.lead_scoring_event import LeadScoringEvent
        from database.conversion_event import ConversionEvent

        print("✅ All freemium models imported successfully")

        # Create session
        session = TestSessionLocal()
        print("✅ Database session created")

        # Test 1: Create AssessmentLead
        print("\n1. Testing AssessmentLead creation...")
        lead = AssessmentLead(email="test@example.com", consent_marketing=True)
        session.add(lead)
        session.commit()
        print(f"✅ AssessmentLead created with ID: {lead.id}")

        # Verify it exists
        found_lead = (
            session.query(AssessmentLead).filter_by(email="test@example.com").first(),
        )
        assert found_lead is not None, "Lead not found in database"
        assert found_lead.email == "test@example.com"
        assert found_lead.consent_marketing is True
        print("✅ AssessmentLead verification passed")

        # Test 2: Create FreemiumAssessmentSession
        print("\n2. Testing FreemiumAssessmentSession creation...")
        from datetime import datetime, timedelta, timezone

        session_obj = FreemiumAssessmentSession(
            lead_id=lead.id,
            business_type="technology",
            company_size="11-50",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        session.add(session_obj)
        session.commit()
        print(f"✅ FreemiumAssessmentSession created with ID: {session_obj.id}")

        # Test 3: Create AIQuestionBank
        print("\n3. Testing AIQuestionBank creation...")
        from decimal import Decimal

        question = AIQuestionBank(
            category="data_protection",
            question_text="How do you currently handle customer data deletion requests?",
            question_type="multiple_choice",
            options=[
                "Manual process",
                "Automated system",
                "No process",
                "Not applicable",
            ],
            context_tags=["gdpr", "data_rights", "deletion"],
            difficulty_level=5,
            compliance_weight=Decimal("0.85"),
        )
        session.add(question)
        session.commit()
        print(f"✅ AIQuestionBank created with ID: {question.id}")

        # Test 4: Create LeadScoringEvent
        print("\n4. Testing LeadScoringEvent creation...")
        event = LeadScoringEvent(
            lead_id=lead.id,
            event_type="assessment_start",
            event_category="engagement",
            event_action="started_assessment",
            score_impact=10,
        )
        session.add(event)
        session.commit()
        print(f"✅ LeadScoringEvent created with ID: {event.id}")

        # Test 5: Create ConversionEvent
        print("\n5. Testing ConversionEvent creation...")
        conversion = ConversionEvent(
            lead_id=lead.id,
            session_id=session_obj.id,
            conversion_type="trial_signup",
            conversion_value=Decimal("99.00"),
            conversion_source="freemium_results_page",
        )
        session.add(conversion)
        session.commit()
        print(f"✅ ConversionEvent created with ID: {conversion.id}")

        # Test 6: Relationships and constraints
        print("\n6. Testing relationships...")
        # Test unique constraint on AssessmentLead email
        try:
            duplicate_lead = AssessmentLead(
                email="test@example.com", consent_marketing=False  # Same email,
            )
            session.add(duplicate_lead)
            session.commit()
            print("❌ Unique constraint test FAILED - duplicate email was allowed")
        except ValueError as e:
            session.rollback()
            print(
                f"✅ Unique constraint test PASSED - duplicate email rejected: {type(e).__name__}",
            )

        # Cleanup
        print("\n7. Cleaning up test data...")
        session.delete(conversion)
        session.delete(event)
        session.delete(question)
        session.delete(session_obj)
        session.delete(lead)
        session.commit()
        session.close()
        print("✅ All test data cleaned up")

        print("\n🎉 ALL FREEMIUM MODEL TESTS PASSED!")
        return True

    except ValueError as e:
        print(f"\n❌ Test failed with error: {e}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()

        # Try to cleanup
        try:
            session.rollback()
            session.close()
        except (ValueError, TypeError):
            pass

        return False


if __name__ == "__main__":
    success = test_freemium_model_directly()
    sys.exit(0 if success else 1)
