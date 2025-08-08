"""
Test configuration and fixtures for AI Optimization tests.

Provides shared fixtures, mocks, and configuration for testing
the AI optimization implementation.
"""

import asyncio
from typing import Any, AsyncIterator, List
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from config.ai_config import ModelType
from services.ai.assistant import ComplianceAssistant
from services.ai.circuit_breaker import AICircuitBreaker, CircuitBreakerConfig
from services.ai.exceptions import AIServiceException


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def circuit_breaker_config():
    """Circuit breaker configuration for testing."""
    return CircuitBreakerConfig(
        failure_threshold=3, timeout_seconds=60, half_open_max_calls=2, success_threshold=2
    )


@pytest.fixture
def mock_circuit_breaker(circuit_breaker_config):
    """Mock circuit breaker for testing."""
    circuit_breaker = Mock(spec=AICircuitBreaker)
    circuit_breaker.config = circuit_breaker_config
    circuit_breaker.is_model_available.return_value = True
    circuit_breaker.record_success.return_value = None
    circuit_breaker.record_failure.return_value = None
    circuit_breaker.get_status.return_value = {
        "overall_state": "CLOSED",
        "model_states": {"gemini-2.5-flash": "CLOSED"},
        "metrics": {"success_rate": 0.95, "total_requests": 100},
    }
    return circuit_breaker


@pytest.fixture
def mock_model_metadata():
    """Mock model metadata for testing - uses central config."""
    from config.ai_config import MODEL_METADATA

    return MODEL_METADATA


@pytest.fixture
def mock_ai_model():
    """Mock AI model for testing."""
    model = Mock()
    model.model_name = ModelType.GEMINI_25_FLASH.value
    model.generate_content.return_value = Mock(text="Mock AI response")
    model.generate_content_stream.return_value = iter(
        [Mock(text="Mock "), Mock(text="streaming "), Mock(text="response")]
    )
    return model


@pytest.fixture
async def mock_compliance_assistant():
    """Mock compliance assistant for testing."""
    from sqlalchemy.ext.asyncio import AsyncSession

    mock_db = Mock(spec=AsyncSession)
    assistant = Mock(spec=ComplianceAssistant)
    assistant.db = mock_db
    assistant.circuit_breaker = Mock(spec=AICircuitBreaker)
    assistant.circuit_breaker.is_model_available.return_value = True

    # Mock streaming methods
    async def mock_stream():
        yield "Mock streaming response"

    assistant.analyze_assessment_results_stream = AsyncMock(return_value=mock_stream())
    assistant.get_assessment_recommendations_stream = AsyncMock(return_value=mock_stream())
    assistant.get_assessment_help_stream = AsyncMock(return_value=mock_stream())

    return assistant


@pytest.fixture
def mock_streaming_chunks():
    """Mock streaming chunks for testing."""

    class MockChunk:
        def __init__(self, text=None, candidates=None) -> None:
            self.text = text
            self.candidates = candidates or []

    return [
        MockChunk(text="This is "),
        MockChunk(text="a test "),
        MockChunk(text="streaming "),
        MockChunk(text="response."),
    ]


@pytest.fixture
def mock_assessment_data():
    """Mock assessment data for testing."""
    return {
        "responses": [
            {"question_id": "q1", "answer": "yes", "confidence": 0.9},
            {"question_id": "q2", "answer": "no", "confidence": 0.8},
            {"question_id": "q3", "answer": "partially", "confidence": 0.7},
        ],
        "framework_id": "gdpr",
        "business_profile_id": str(uuid4()),
        "gaps": [
            {"section": "data_protection", "severity": "high", "score": 0.3},
            {"section": "consent", "severity": "medium", "score": 0.6},
        ],
    }


@pytest.fixture
def mock_business_context():
    """Mock business context for testing."""
    return {
        "business_profile": {
            "industry": "technology",
            "company_size": "small",
            "data_types": ["personal", "financial"],
            "geographic_scope": ["EU", "UK"],
        },
        "framework_context": {
            "framework_id": "gdpr",
            "version": "2018",
            "applicable_sections": ["data_protection", "consent", "breach_notification"],
        },
    }


@pytest.fixture
def performance_test_config():
    """Performance test configuration."""
    return {
        "max_response_time": 3.0,
        "min_throughput": 10,
        "max_memory_mb": 500,
        "target_success_rate": 0.95,
        "concurrent_users": [1, 5, 10],
        "test_duration": 10,
    }


class MockStreamingResponse:
    """Mock streaming response iterator for testing."""

    def __init__(self, chunks: List[Any], fail_at: int = -1) -> None:
        self.chunks = chunks
        self.fail_at = fail_at
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current == self.fail_at:
            raise AIServiceException("Simulated streaming failure")

        if self.current >= len(self.chunks):
            raise StopIteration

        chunk = self.chunks[self.current]
        self.current += 1
        return chunk


@pytest.fixture
def mock_streaming_response_factory():
    """Factory for creating mock streaming responses."""
    return MockStreamingResponse


async def async_generator_from_list(items: List[str]) -> AsyncIterator[str]:
    """Convert a list to an async generator for testing."""
    for item in items:
        yield item


@pytest.fixture
def async_generator_factory():
    """Factory for creating async generators from lists."""
    return async_generator_from_list


@pytest.fixture
def mock_prompt_templates():
    """Mock prompt templates for testing."""
    templates = Mock()
    templates.get_assessment_analysis_prompt.return_value = {
        "system": "You are ComplianceGPT analyzing assessment results.",
        "user": "Analyze the following assessment responses...",
    }
    templates.get_assessment_recommendations_prompt.return_value = {
        "system": "You are ComplianceGPT providing recommendations.",
        "user": "Based on the gaps identified, provide recommendations...",
    }
    templates.get_assessment_help_prompt.return_value = {
        "system": "You are ComplianceGPT providing contextual help.",
        "user": "Help the user understand this compliance question...",
    }
    return templates


@pytest.fixture
def mock_context_manager():
    """Mock context manager for testing."""
    context_manager = Mock()
    context_manager.get_conversation_context = AsyncMock(
        return_value={"business_profile": {"industry": "technology", "company_size": "small"}}
    )
    context_manager.get_business_context = AsyncMock(
        return_value={"business_profile": {"industry": "technology", "company_size": "small"}}
    )
    return context_manager


@pytest.fixture(autouse=True)
def mock_ai_dependencies():
    """Auto-use fixture to mock AI dependencies."""
    with patch("services.ai.assistant.get_ai_model") as mock_get_model, patch(
        "services.ai.assistant.AICircuitBreaker"
    ) as mock_circuit_breaker_class:
        # Mock model
        from config.ai_config import ModelType

        mock_model = Mock()
        mock_model.model_name = ModelType.GEMINI_25_FLASH.value
        mock_model.generate_content.return_value = Mock(text="Mock response")
        mock_model.generate_content_stream.return_value = iter(
            [Mock(text="Mock "), Mock(text="response")]
        )
        mock_get_model.return_value = mock_model

        # Mock circuit breaker
        mock_circuit_breaker = Mock()
        mock_circuit_breaker.is_model_available.return_value = True
        mock_circuit_breaker.record_success.return_value = None
        mock_circuit_breaker.record_failure.return_value = None
        mock_circuit_breaker_class.return_value = mock_circuit_breaker

        yield {"model": mock_model, "circuit_breaker": mock_circuit_breaker}


@pytest.fixture
def test_task_contexts():
    """Various task contexts for testing model selection."""
    return {
        "simple_help": {"task_type": "help", "prompt_length": 100, "complexity": "simple"},
        "complex_analysis": {
            "task_type": "analysis",
            "prompt_length": 2000,
            "framework": "gdpr",
            "complexity": "complex",
        },
        "medium_recommendations": {
            "task_type": "recommendations",
            "prompt_length": 800,
            "framework": "iso27001",
            "complexity": "medium",
        },
    }


@pytest.fixture
def mock_database_session():
    """Mock database session for testing."""
    from sqlalchemy.ext.asyncio import AsyncSession

    session = Mock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session
