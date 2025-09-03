#!/usr/bin/env python3
"""Debug test to find the actual pytest issue."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pytest

from services.ai.assistant import ComplianceAssistant

@pytest.mark.asyncio
async def test_simple_debug(
    async_db_session, async_sample_user, async_sample_business_profile
) -> None:
    """Simple debug test to see what's failing."""
    try:
        print(f"✓ Got async_db_session: {type(async_db_session)}")
        print(f"✓ Got async_sample_user: {async_sample_user.id}")
        print(
            f"✓ Got async_sample_business_profile: {async_sample_business_profile.id}"
        )

        # Create assistant
        assistant = ComplianceAssistant(async_db_session)
        print(f"✓ Created assistant: {type(assistant)}")

        # Load golden dataset
        dataset_path = (
            Path(__file__).parent
            / "tests"
            / "ai"
            / "golden_datasets"
            / "gdpr_questions.json"
        )
        with open(dataset_path) as f:
            data = json.load(f)
        basic_questions = [q for q in data if q.get("difficulty") == "basic"]
        print(f"✓ Loaded {len(basic_questions)} basic questions")

        # Test one question without mocking first
        question = basic_questions[0]
        print(f"Testing question: {question['question'][:50]}...")

        result = await assistant.process_message(
            conversation_id=uuid4(),
            user=async_sample_user,
            message=question["question"],
            business_profile_id=async_sample_business_profile.id,
        )
        print(f"✓ Got result: {type(result)}")
        print(f"✓ Result tuple length: {len(result)}")

        response, metadata = result
        print(f"✓ Response type: {type(response)}")
        print(f"✓ Metadata type: {type(metadata)}")
        print(f"✓ Response length: {len(response)}")

        assert isinstance(response, str)
        assert isinstance(metadata, dict)
        assert len(response) > 0

        print("✓ Simple test passed!")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        raise
