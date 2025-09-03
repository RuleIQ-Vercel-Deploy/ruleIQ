#!/usr/bin/env python3
"""Test if fixtures work."""

from __future__ import annotations

import pytest

@pytest.mark.asyncio
async def test_fixtures_work(
    async_db_session, async_sample_user, async_sample_business_profile
) -> None:
    """Test if the fixtures work."""
    print(f"✓ async_db_session: {type(async_db_session)}")
    print(f"✓ async_sample_user: {async_sample_user.id}")
    print(f"✓ async_sample_business_profile: {async_sample_business_profile.id}")
    assert True
