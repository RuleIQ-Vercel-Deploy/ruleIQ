#!/usr/bin/env python
"""Debug script to test model creation without Doppler interference."""

import os
import sys

# Force the test database URL before any imports
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5433/compliance_test"
os.environ["TEST_DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5433/compliance_test"

# Remove any Doppler variables
for key in list(os.environ.keys()):
    if "DOPPLER" in key:
        del os.environ[key]

sys.path.insert(0, ".")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import (
    Base,
    AIQuestionBank,
    LeadScoringEvent,
    ConversionEvent,
    AssessmentLead,
    FreemiumAssessmentSession,
)


def test_models():
    """Test creating each model that's failing."""
    # Create engine and session
    engine = create_engine(os.environ["DATABASE_URL"])
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    results = []

    # Test AIQuestionBank
    try:
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
        )
        session.add(question)
        session.commit()
        results.append("✓ AIQuestionBank created successfully")
        session.delete(question)
        session.commit()
    except Exception as e:
        results.append(f"✗ AIQuestionBank error: {e}")
        session.rollback()

    # Test LeadScoringEvent
    try:
        lead = AssessmentLead(email="scoring.test@example.com", marketing_consent=True)
        session.add(lead)
        session.commit()

        event = LeadScoringEvent(
            lead_id=lead.id,
            event_type="assessment_start",
            event_category="engagement",
            event_action="started_assessment",
            score_impact=10,
        )
        session.add(event)
        session.commit()
        results.append("✓ LeadScoringEvent created successfully")

        # Clean up
        session.delete(event)
        session.delete(lead)
        session.commit()
    except Exception as e:
        results.append(f"✗ LeadScoringEvent error: {e}")
        session.rollback()

    # Test ConversionEvent
    try:
        lead = AssessmentLead(email="convert.test@example.com", marketing_consent=True)
        session.add(lead)
        session.commit()

        sess = FreemiumAssessmentSession(lead_id=lead.id, assessment_type="retail")
        session.add(sess)
        session.commit()

        from decimal import Decimal

        conversion = ConversionEvent(
            lead_id=lead.id,
            session_id=sess.id,
            conversion_type="trial_signup",
            conversion_value=Decimal("99.00"),
            conversion_source="freemium_results_page",
        )
        session.add(conversion)
        session.commit()
        results.append("✓ ConversionEvent created successfully")

        # Clean up
        session.delete(conversion)
        session.delete(sess)
        session.delete(lead)
        session.commit()
    except Exception as e:
        results.append(f"✗ ConversionEvent error: {e}")
        session.rollback()

    session.close()

    for result in results:
        print(result)


if __name__ == "__main__":
    test_models()
