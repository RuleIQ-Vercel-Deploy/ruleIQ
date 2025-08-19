"""
Configuration for AI output consistency tests

Provides shared fixtures and test configuration for consistency testing.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock
import os
import sys

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for testing"""
    client = AsyncMock()
    client.generate_content = AsyncMock()
    return client


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    client = AsyncMock()
    client.chat.completions.create = AsyncMock()
    return client


# Test data for consistency validation
TEST_FRAMEWORKS = ["gdpr", "iso27001", "soc2", "hipaa", "ccpa"]

TEST_QUERIES = {
    "simple": ["What is GDPR?", "Define ISO 27001", "Explain SOC 2 compliance"],
    "complex": [
        "Compare GDPR and CCPA privacy requirements with implementation examples",
        "Analyze ISO 27001 Annex A controls vs SOC 2 trust service criteria",
        "Describe cross-border data transfer mechanisms under multiple frameworks",
    ],
    "technical": [
        "GDPR Article 32 technical and organisational measures",
        "ISO 27001 A.12.6.1 management of technical vulnerabilities",
        "SOC 2 CC6.1 logical and physical access controls",
    ],
}

EXPECTED_RESPONSE_STRUCTURE = {
    "response": str,
    "confidence": float,
    "sources": list,
    "compliance_score": (int, float),
    "metadata": dict,
    "timestamp": str,
}

# Performance benchmarks
PERFORMANCE_THRESHOLDS = {
    "max_response_time": 5.0,  # seconds
    "min_confidence": 0.7,
    "min_compliance_score": 70,
    "max_memory_growth": 50 * 1024 * 1024,  # 50MB
    "max_response_time_variation": 0.5,  # coefficient of variation
}
