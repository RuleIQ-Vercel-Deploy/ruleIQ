from __future__ import annotations

import pytest
from sqlalchemy import select

from services.assessment_service import AssessmentService
from database.assessment_session import AssessmentSession


@pytest.mark.unit
@pytest.mark.regression
@pytest.mark.asyncio
async def test_start_assessment_session_persists_business_profile_id(
    async_db_session, sample_user, sample_business_profile
):
    service = AssessmentService()

    # Explicitly pass the business_profile_id to ensure it's persisted
    session = await service.start_assessment_session(
        db=async_db_session,
        user=sample_user,
        session_type="compliance_scoping",
        business_profile_id=sample_business_profile.id,
    )

    assert session is not None
    assert session.user_id == sample_user.id
    assert session.business_profile_id == sample_business_profile.id

    # Re-fetch from the database to verify persistence
    result = await async_db_session.execute(
        select(AssessmentSession).where(AssessmentSession.id == session.id)
    )
    persisted = result.scalars().first()
    assert persisted is not None
    assert persisted.business_profile_id == sample_business_profile.id