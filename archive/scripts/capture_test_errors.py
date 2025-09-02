#!/usr/bin/env python
import os
import sys
import traceback

# Force test database
os.environ["DATABASE_URL"] = (
    os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/compliance_test")
)
os.environ["TEST_DATABASE_URL"] = (
    os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/compliance_test")
)

# Remove Doppler
for key in list(os.environ.keys()):
    if "DOPPLER" in key:
        del os.environ[key]

sys.path.insert(0, ".")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import (
    Base,
    AssessmentLead,
    FreemiumAssessmentSession,
    AIQuestionBank,
    LeadScoringEvent,
    ConversionEvent,
)
from datetime import datetime, timedelta, timezone
from decimal import Decimal

engine = create_engine(os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/compliance_test"))
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_session_creation():
    session = SessionLocal()
    try:
        # Clean up
        session.query(FreemiumAssessmentSession).delete()
        session.query(AssessmentLead).delete()
        session.commit()

        lead = AssessmentLead(email="session.test@example.com", marketing_consent=True)
        session.add(lead)
        session.commit()

        sess = FreemiumAssessmentSession(
            lead_id=lead.id, assessment_type="technology_compliance", status="started"
        )
        session.add(sess)
        session.commit()

        # Check assertions
        assert sess.id is not None, "Session ID is None"
        assert sess.lead_id == lead.id, f"Lead ID mismatch: {sess.lead_id} != {lead.id}"
        assert (
            sess.assessment_type == "technology_compliance"
        ), f"Type mismatch: {sess.assessment_type}"
        assert sess.status == "started", f"Status mismatch: {sess.status}"
        assert sess.session_token is not None, "Session token is None"
        assert (
            len(sess.session_token) >= 32
        ), f"Token too short: {len(sess.session_token)}"
        assert sess.expires_at is not None, "Expires_at is None"
        assert (
            sess.expires_at > datetime.now(timezone.utc)
        ), f"Already expired: {sess.expires_at} <= {datetime.now(timezone.utc)}"

        print("✓ test_create_assessment_session")
        return True
    except AssertionError as e:
        print(f"✗ test_create_assessment_session: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"✗ test_create_assessment_session error: {e}")
        traceback.print_exc()
        return False
    finally:
        session.rollback()
        session.close()


def test_ai_question():
    session = SessionLocal()
    try:
        # Clean up
        session.query(AIQuestionBank).delete()
        session.commit()

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

        assert question.id is not None
        assert question.category == "data_protection"
        assert question.question_type == "multiple_choice"
        assert len(question.options) == 4
        assert "gdpr" in question.context_tags

        print("✓ test_create_ai_question")
        return True
    except Exception as e:
        print(f"✗ test_create_ai_question: {e}")
        traceback.print_exc()
        return False
    finally:
        session.rollback()
        session.close()


def test_lead_scoring_event():
    session = SessionLocal()
    try:
        # Clean up
        session.query(LeadScoringEvent).delete()
        session.query(AssessmentLead).delete()
        session.commit()

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

        assert event.lead_id == lead.id
        assert event.event_type == "assessment_start"
        assert event.score_impact == 10
        assert event.created_at is not None

        print("✓ test_create_lead_scoring_event")
        return True
    except Exception as e:
        print(f"✗ test_create_lead_scoring_event: {e}")
        traceback.print_exc()
        return False
    finally:
        session.rollback()
        session.close()


def test_conversion_event():
    session = SessionLocal()
    try:
        # Clean up
        session.query(ConversionEvent).delete()
        session.query(FreemiumAssessmentSession).delete()
        session.query(AssessmentLead).delete()
        session.commit()

        lead = AssessmentLead(email="convert.test@example.com", marketing_consent=True)
        session.add(lead)
        session.commit()

        sess = FreemiumAssessmentSession(lead_id=lead.id, assessment_type="retail")
        session.add(sess)
        session.commit()

        conversion = ConversionEvent(
            lead_id=lead.id,
            session_id=sess.id,
            conversion_type="trial_signup",
            conversion_value=Decimal("99.00"),
            conversion_source="freemium_results_page",
        )
        session.add(conversion)
        session.commit()

        assert conversion.lead_id == lead.id
        assert conversion.session_id == sess.id
        assert conversion.conversion_type == "trial_signup"
        assert conversion.conversion_value == Decimal("99.00")
        assert conversion.conversion_source == "freemium_results_page"
        assert conversion.created_at is not None

        print("✓ test_create_conversion_event")
        return True
    except Exception as e:
        print(f"✗ test_create_conversion_event: {e}")
        traceback.print_exc()
        return False
    finally:
        session.rollback()
        session.close()


if __name__ == "__main__":
    failures = 0

    if not test_session_creation():
        failures += 1
    if not test_ai_question():
        failures += 1
    if not test_lead_scoring_event():
        failures += 1
    if not test_conversion_event():
        failures += 1

    print(f"\nResults: {4 - failures} passed, {failures} failed")
    sys.exit(failures)
