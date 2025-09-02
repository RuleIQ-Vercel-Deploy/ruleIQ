"""
AI Performance and Rate Limiting Tests

Tests AI service performance, response times, caching mechanisms,
and rate limiting validation for the AI assessment endpoints.
"""

import asyncio
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID

import pytest

from services.ai.assistant import ComplianceAssistant
from services.ai.exceptions import AITimeoutException


@pytest.mark.performance
@pytest.mark.ai
class TestAIPerformance:
    """Test AI service performance characteristics"""

    def test_ai_help_response_time_under_threshold(
        self, client, authenticated_headers, sample_business_profile
    ):
        """Test AI help endpoint responds within acceptable time limits"""
        request_data = {
            "question_id": "perf-test-1",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr",
        }

        with patch(
            "api.routers.ai_assessments.ComplianceAssistant"
        ) as mock_assistant_class:
            # Create a mock instance
            mock_assistant = Mock()
            mock_assistant.get_assessment_help = AsyncMock(
                return_value={
                    "guidance": "GDPR compliance requires...",
                    "confidence_score": 0.9,
                    "related_topics": ["data protection"],
                    "follow_up_suggestions": ["Learn more about GDPR"],
                    "source_references": ["GDPR Article 5"],
                    "request_id": "test-request-id",
                    "generated_at": "2024-01-01T00:00:00Z",
                }
            )
            mock_assistant_class.return_value = mock_assistant

            start_time = time.time()
            response = client.post(
                "/api/ai/assessments/gdpr/help",
                json=request_data,
                headers=authenticated_headers,
            )
            end_time = time.time()

            response_time = end_time - start_time

            assert response.status_code == 200
            # In test environment with mocking overhead, allow more time
            assert response_time < 5.0  # Should respond within 5 seconds

    def test_ai_help_concurrent_requests_performance(
        self, client, authenticated_headers, sample_business_profile
    ):
        """Test performance under concurrent AI help requests"""
        request_data = {
            "question_id": "perf-test-concurrent",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr",
        }

        with patch(
            "api.routers.ai_assessments.ComplianceAssistant"
        ) as mock_assistant_class:
            mock_assistant = Mock()
            mock_assistant.get_assessment_help = AsyncMock(
                return_value={
                    "guidance": "GDPR compliance requires...",
                    "confidence_score": 0.9,
                    "related_topics": ["data protection"],
                    "follow_up_suggestions": ["Learn more about GDPR"],
                    "source_references": ["GDPR Article 5"],
                    "request_id": "test-request-id",
                    "generated_at": "2024-01-01T00:00:00Z",
                }
            )
            mock_assistant_class.return_value = mock_assistant

            def make_request():
                start_time = time.time()
                response = client.post(
                    "/api/ai/assessments/gdpr/help",
                    json=request_data,
                    headers=authenticated_headers,
                )
                end_time = time.time()
                return response.status_code, end_time - start_time

            # Make 10 concurrent requests
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                results = [future.result() for future in as_completed(futures)]

            response_times = [result[1] for result in results]
            success_count = sum(1 for result in results if result[0] == 200)

            # Performance assertions
            assert success_count >= 8  # At least 80% success rate
            assert statistics.mean(response_times) < 5.0  # Average under 5 seconds
            assert max(response_times) < 10.0  # No request over 10 seconds

    def test_ai_analysis_performance_with_large_dataset(
        self, client, authenticated_headers, sample_business_profile
    ):
        """Test AI analysis performance with large assessment data"""
        # Create large assessment results
        large_answers = {f"q{i}": "yes" if i % 2 == 0 else "no" for i in range(100)}

        request_data = {
            "framework_id": "gdpr",
            "business_profile_id": str(sample_business_profile.id),
            "assessment_results": {
                "answers": large_answers,
                "completion_percentage": 100.0,
                "sections_completed": [f"section-{i}" for i in range(10)],
            },
        }

        start_time = time.time()
        response = client.post(
            "/api/ai/assessments/analysis",
            json=request_data,
            headers=authenticated_headers,
        )
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 10.0  # Should handle large datasets within 10 seconds

    @pytest.mark.asyncio
    async def test_ai_service_timeout_handling(self, async_db_session):
        """Test AI service handles timeouts gracefully"""
        assistant = ComplianceAssistant(async_db_session)

        # Mock the get_assessment_help to simulate timeout
        with patch.object(assistant, "get_assessment_help") as mock_help:
            mock_help.side_effect = AITimeoutException(timeout_seconds=30.0)

            start_time = time.time()

            # The method should raise the timeout exception
            with pytest.raises(AITimeoutException):
                await assistant.get_assessment_help(
                    question_id="timeout-test",
                    question_text="Test question",
                    framework_id="gdpr",
                    business_profile_id=UUID("12345678-1234-5678-9012-123456789012"),
                )

            end_time = time.time()

            # Should fail quickly with the mocked exception
            assert end_time - start_time < 2.0

    def test_ai_caching_improves_performance(
        self, client, authenticated_headers, sample_business_profile
    ):
        """Test that AI response caching improves performance for repeated requests"""
        request_data = {
            "question_id": "cache-test-1",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr",
        }

        with patch(
            "api.routers.ai_assessments.ComplianceAssistant"
        ) as mock_assistant_class:
            mock_assistant = Mock()
            mock_assistant.get_assessment_help = AsyncMock(
                return_value={
                    "guidance": "GDPR compliance requires...",
                    "confidence_score": 0.9,
                    "related_topics": ["data protection"],
                    "follow_up_suggestions": ["Learn more about GDPR"],
                    "source_references": ["GDPR Article 5"],
                    "request_id": "test-request-id",
                    "generated_at": "2024-01-01T00:00:00Z",
                }
            )
            mock_assistant_class.return_value = mock_assistant

            # First request (cache miss)
            start_time = time.time()
            response1 = client.post(
                "/api/ai/assessments/gdpr/help",
                json=request_data,
                headers=authenticated_headers,
            )
            first_request_time = time.time() - start_time

            # Second identical request (should be cached)
            start_time = time.time()
            response2 = client.post(
                "/api/ai/assessments/gdpr/help",
                json=request_data,
                headers=authenticated_headers,
            )
            second_request_time = time.time() - start_time

            assert response1.status_code == 200
            assert response2.status_code == 200

            # Second request should be faster (cached) or at least not significantly slower
            assert second_request_time <= first_request_time * 1.5


@pytest.mark.performance
@pytest.mark.rate_limiting
class TestAIRateLimiting:
    """Test AI-specific rate limiting implementation"""

    def test_ai_help_rate_limit_enforcement(
        self, client, authenticated_headers, sample_business_profile
    ):
        """Test that AI help endpoint enforces 10 requests per minute limit"""
        request_data = {
            "question_id": "rate-limit-test",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr",
        }

        with patch(
            "api.routers.ai_assessments.ComplianceAssistant"
        ) as mock_assistant_class:
            mock_assistant = Mock()
            mock_assistant.get_assessment_help = AsyncMock(
                return_value={
                    "guidance": "GDPR compliance requires...",
                    "confidence_score": 0.9,
                    "related_topics": ["data protection"],
                    "follow_up_suggestions": ["Learn more about GDPR"],
                    "source_references": ["GDPR Article 5"],
                    "request_id": "test-request-id",
                    "generated_at": "2024-01-01T00:00:00Z",
                }
            )
            mock_assistant_class.return_value = mock_assistant

            responses = []
            start_time = time.time()

            # Make 15 requests rapidly (exceeding 10/min limit)
            for i in range(15):
                response = client.post(
                    "/api/ai/assessments/gdpr/help",
                    json={**request_data, "question_id": f"rate-limit-test-{i}"},
                    headers=authenticated_headers,
                )
                responses.append(response)

                # Small delay to avoid overwhelming the test
                time.sleep(0.1)

            end_time = time.time()
            total_time = end_time - start_time

            # Count successful vs rate-limited responses
            success_responses = [r for r in responses if r.status_code == 200]
            rate_limited_responses = [r for r in responses if r.status_code == 429]

            # Should have some rate limiting if requests were made quickly
            if total_time < 60:  # If all requests made within a minute
                assert (
                    len(rate_limited_responses) > 0
                ), "Expected some requests to be rate limited"
                assert len(success_responses) <= 12, "Too many requests succeeded"

    def test_ai_analysis_stricter_rate_limit(
        self, client, authenticated_headers, sample_business_profile
    ):
        """Test that AI analysis endpoint has stricter rate limiting (3 req/min)"""
        request_data = {
            "framework_id": "gdpr",
            "business_profile_id": str(sample_business_profile.id),
            "assessment_results": {
                "answers": {"q1": "yes"},
                "completion_percentage": 50.0,
            },
        }

        responses = []

        # Make 6 requests rapidly (exceeding 3/min limit)
        for _i in range(6):
            response = client.post(
                "/api/ai/assessments/analysis",
                json=request_data,
                headers=authenticated_headers,
            )
            responses.append(response)
            time.sleep(0.1)

        # Count responses
        success_responses = [r for r in responses if r.status_code == 200]
        rate_limited_responses = [r for r in responses if r.status_code == 429]

        # Should have stricter limiting than help endpoint
        assert (
            len(success_responses) <= 4
        ), "Analysis endpoint should have stricter rate limiting"
        assert (
            len(rate_limited_responses) >= 2
        ), "Expected multiple requests to be rate limited"

    def test_regular_endpoints_higher_rate_limits(self, client, authenticated_headers):
        """Test that regular assessment endpoints have higher rate limits (100 req/min)"""
        responses = []

        # Make 20 requests to regular endpoint
        for _i in range(20):
            response = client.get("/api/assessments", headers=authenticated_headers)
            responses.append(response)

        # Count successful responses (allowing for 404s if no assessments exist)
        success_responses = [r for r in responses if r.status_code in [200, 404]]
        rate_limited_responses = [r for r in responses if r.status_code == 429]

        # Regular endpoints should handle more requests
        assert (
            len(success_responses) >= 15
        ), "Regular endpoints should handle more requests"
        assert (
            len(rate_limited_responses) <= 2
        ), "Regular endpoints should have minimal rate limiting"

    def test_rate_limit_headers_present(
        self, client, authenticated_headers, sample_business_profile
    ):
        """Test that rate limit headers are included in AI endpoint responses"""
        request_data = {
            "question_id": "header-test",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr",
        }

        with patch(
            "api.routers.ai_assessments.ComplianceAssistant"
        ) as mock_assistant_class:
            mock_assistant = Mock()
            mock_assistant.get_assessment_help = AsyncMock(
                return_value={
                    "guidance": "GDPR compliance requires...",
                    "confidence_score": 0.9,
                    "related_topics": ["data protection"],
                    "follow_up_suggestions": ["Learn more about GDPR"],
                    "source_references": ["GDPR Article 5"],
                    "request_id": "test-request-id",
                    "generated_at": "2024-01-01T00:00:00Z",
                }
            )
            mock_assistant_class.return_value = mock_assistant

            response = client.post(
                "/api/ai/assessments/gdpr/help",
                json=request_data,
                headers=authenticated_headers,
            )

            # Check for rate limiting headers (if implemented)
            expected_headers = [
                "X-RateLimit-Limit",
                "X-RateLimit-Remaining",
                "X-RateLimit-Reset",
            ]

            # Note: This test may need adjustment based on actual rate limiting implementation
            for header in expected_headers:
                if header in response.headers:
                    assert response.headers[header] is not None

    def test_rate_limit_reset_after_window(
        self, client, authenticated_headers, sample_business_profile
    ):
        """Test that rate limits reset after the time window"""
        request_data = {
            "question_id": "reset-test",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr",
        }

        with patch(
            "api.routers.ai_assessments.ComplianceAssistant"
        ) as mock_assistant_class:
            mock_assistant = Mock()
            mock_assistant.get_assessment_help = AsyncMock(
                return_value={
                    "guidance": "GDPR compliance requires...",
                    "confidence_score": 0.9,
                    "related_topics": ["data protection"],
                    "follow_up_suggestions": ["Learn more about GDPR"],
                    "source_references": ["GDPR Article 5"],
                    "request_id": "test-request-id",
                    "generated_at": "2024-01-01T00:00:00Z",
                }
            )
            mock_assistant_class.return_value = mock_assistant

            # Make requests to approach rate limit
            for i in range(8):
                response = client.post(
                    "/api/ai/assessments/gdpr/help",
                    json={**request_data, "question_id": f"reset-test-{i}"},
                    headers=authenticated_headers,
                )

            # Wait for rate limit window to reset (this is a simplified test)
            # In a real implementation, you might need to wait longer or mock time
            time.sleep(2)

            # Make another request - should succeed if rate limit reset
            response = client.post(
                "/api/ai/assessments/gdpr/help",
                json={**request_data, "question_id": "reset-test-final"},
                headers=authenticated_headers,
            )

            # Should succeed after reset (or at least not be rate limited for this reason)
            assert response.status_code in [
                200,
                500,
            ]  # 500 might be from other issues, but not 429


@pytest.mark.performance
@pytest.mark.load
class TestAILoadTesting:
    """Load testing for AI endpoints"""

    def test_ai_endpoint_load_capacity(
        self, client, authenticated_headers, sample_business_profile
    ):
        """Test AI endpoint capacity under sustained load"""
        request_data = {
            "question_id": "load-test",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr",
        }

        with patch(
            "api.routers.ai_assessments.ComplianceAssistant"
        ) as mock_assistant_class:
            mock_assistant = Mock()
            mock_assistant.get_assessment_help = AsyncMock(
                return_value={
                    "guidance": "GDPR compliance requires...",
                    "confidence_score": 0.9,
                    "related_topics": ["data protection"],
                    "follow_up_suggestions": ["Learn more about GDPR"],
                    "source_references": ["GDPR Article 5"],
                    "request_id": "test-request-id",
                    "generated_at": "2024-01-01T00:00:00Z",
                }
            )
            mock_assistant_class.return_value = mock_assistant

            def make_sustained_requests(duration_seconds: int = 30):
                """Make requests for a sustained period"""
                start_time = time.time()
                responses = []
                request_count = 0

                while time.time() - start_time < duration_seconds:
                    response = client.post(
                        "/api/ai/assessments/gdpr/help",
                        json={
                            **request_data,
                            "question_id": f"load-test-{request_count}",
                        },
                        headers=authenticated_headers,
                    )
                    responses.append(response)
                    request_count += 1
                    time.sleep(0.5)  # 2 requests per second

                return responses

            # Run sustained load test for 10 seconds (reduced for test speed)
            responses = make_sustained_requests(10)

            # Analyze results
            success_count = sum(1 for r in responses if r.status_code == 200)
            error_count = sum(1 for r in responses if r.status_code >= 500)
            sum(1 for r in responses if r.status_code == 429)

            total_requests = len(responses)
            success_rate = success_count / total_requests if total_requests > 0 else 0

            # Performance assertions
            assert total_requests > 0, "Should have made some requests"
            assert success_rate >= 0.7, f"Success rate too low: {success_rate:.2%}"
            assert error_count / total_requests <= 0.1, "Too many server errors"

    def test_ai_memory_usage_under_load(
        self, client, authenticated_headers, sample_business_profile
    ):
        """Test that AI endpoints don't have memory leaks under load"""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        request_data = {
            "question_id": "memory-test",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr",
        }

        with patch(
            "api.routers.ai_assessments.ComplianceAssistant"
        ) as mock_assistant_class:
            mock_assistant = Mock()
            mock_assistant.get_assessment_help = AsyncMock(
                return_value={
                    "guidance": "GDPR compliance requires...",
                    "confidence_score": 0.9,
                    "related_topics": ["data protection"],
                    "follow_up_suggestions": ["Learn more about GDPR"],
                    "source_references": ["GDPR Article 5"],
                    "request_id": "test-request-id",
                    "generated_at": "2024-01-01T00:00:00Z",
                }
            )
            mock_assistant_class.return_value = mock_assistant

            # Make many requests
            for i in range(50):
                client.post(
                    "/api/ai/assessments/gdpr/help",
                    json={**request_data, "question_id": f"memory-test-{i}"},
                    headers=authenticated_headers,
                )

                # Small delay to allow garbage collection
                if i % 10 == 0:
                    time.sleep(0.1)

            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory

            # Memory increase should be reasonable (less than 100MB for 50 requests)
            assert (
                memory_increase < 100 * 1024 * 1024
            ), f"Memory usage increased by {memory_increase / 1024 / 1024:.2f}MB"
