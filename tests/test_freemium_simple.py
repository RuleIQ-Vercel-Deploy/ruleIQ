#!/usr/bin/env python3
"""
Simple test to verify freemium models work correctly after fixes.
"""

import pytest
from database.assessment_lead import AssessmentLead


def test_assessment_lead_creation(db_session):
    """Test creating an assessment lead with minimal required fields."""
    email = "test.lead@example.com"

    # Create assessment lead
    lead = AssessmentLead(
        email=email,
        marketing_consent=True
    )

    # Add to session and commit
    db_session.add(lead)
    db_session.commit()

    # Verify the lead was created correctly
    assert lead.id is not None
    assert lead.email == email
    assert lead.marketing_consent == True
    assert lead.lead_score == 0
    assert lead.lead_status == "new"
    assert lead.created_at is not None
    assert lead.updated_at is not None


def test_assessment_lead_with_all_fields(db_session):
    """Test creating an assessment lead with all available fields."""
    email = "full.test@example.com"

    # Create assessment lead with all fields
    lead = AssessmentLead(
        email=email,
        first_name="John",
        last_name="Doe",
        company_name="Test Corp",
        company_size="50-100",
        industry="Technology",
        phone="+1234567890",
        utm_source="google",
        utm_medium="cpc",
        utm_campaign="test-campaign",
        marketing_consent=True,
        newsletter_subscribed=True,
        lead_score=10
    )

    # Add to session and commit
    db_session.add(lead)
    db_session.commit()

    # Verify all fields
    assert lead.email == email
    assert lead.first_name == "John"
    assert lead.last_name == "Doe"
    assert lead.company_name == "Test Corp"
    assert lead.utm_source == "google"
    assert lead.marketing_consent == True
    assert lead.lead_score == 10
