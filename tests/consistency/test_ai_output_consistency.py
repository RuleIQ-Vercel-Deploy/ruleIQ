"""
AI Output Consistency Testing Suite

Tests AI system output consistency across multiple scenarios to ensure
reliable and predictable responses in the UI.

This suite validates:
- Response consistency across identical requests
- Cross-framework consistency (GDPR, ISO27001, SOC2)
- UI format consistency and structure
- Edge case handling consistency
- Performance consistency under load
"""

import asyncio
import pytest
import json
import time
from typing import Dict, List, Any, Tuple
from unittest.mock import AsyncMock, patch
import statistics
from datetime import datetime

from services.ai.assistant import ComplianceAssistant
from services.ai.circuit_breaker import AICircuitBreaker
from services.ai.response_cache import AIResponseCache
from services.ai.performance_optimizer import AIPerformanceOptimizer


class TestAIOutputConsistency:
    """Test AI output consistency across various scenarios"""

    @pytest.fixture(scope="class")
    async def ai_assistant(self):
        """Initialize AI assistant for testing"""
        assistant = ComplianceAssistant(
            gemini_client=AsyncMock(),
            openai_client=AsyncMock(),
            circuit_breaker=AICircuitBreaker(),
            cache=AIResponseCache(),
            optimizer=AIPerformanceOptimizer(),
        )
        return assistant

    @pytest.fixture
    def sample_queries(self):
        """Standard test queries for consistency validation"""
        return {
            "simple": "What are the key GDPR requirements?",
            "complex": "Compare ISO 27001 and SOC 2 security controls with specific implementation examples",
            "technical": "Explain data retention policies under GDPR Article 5(1)(e)",
            "multi_framework": "How do GDPR, SOC 2, and ISO 27001 address encryption requirements?",
            "edge_case": "What happens if a company operates in multiple jurisdictions with conflicting privacy laws?",
        }

    @pytest.mark.asyncio
    async def test_identical_query_consistency(self, ai_assistant, sample_queries):
        """Test that identical queries produce consistent responses"""
        query = sample_queries["simple"]
        responses = []

        # Mock consistent AI responses
        mock_response = {
            "response": "GDPR key requirements include: 1) Lawful basis for processing, 2) Data subject rights, 3) Privacy by design, 4) Data protection officer appointment when required, 5) Breach notification within 72 hours",
            "confidence": 0.92,
            "sources": ["GDPR Article 6", "GDPR Article 7", "GDPR Article 25"],
            "compliance_score": 95,
        }

        with patch.object(ai_assistant, "_generate_gemini_response", return_value=mock_response):
            # Run same query 5 times
            for i in range(5):
                response = await ai_assistant.process_message(
                    message=query, framework="gdpr", user_id="test_user_consistency"
                )
                responses.append(response)

        # Validate consistency
        assert len(responses) == 5

        # Check response structure consistency
        for response in responses:
            assert "response" in response
            assert "confidence" in response
            assert "sources" in response
            assert "compliance_score" in response
            assert isinstance(response["confidence"], float)
            assert isinstance(response["compliance_score"], (int, float))

        # Check content consistency (should be identical for cached responses)
        first_response = responses[0]
        for response in responses[1:]:
            assert response["response"] == first_response["response"]
            assert response["confidence"] == first_response["confidence"]
            assert response["sources"] == first_response["sources"]

    @pytest.mark.asyncio
    async def test_cross_framework_consistency(self, ai_assistant):
        """Test consistent behavior across different compliance frameworks"""
        query = "What are the data encryption requirements?"
        frameworks = ["gdpr", "iso27001", "soc2"]
        responses = {}

        # Mock framework-specific responses
        mock_responses = {
            "gdpr": {
                "response": "GDPR requires appropriate technical measures including encryption of personal data (Article 32)",
                "confidence": 0.89,
                "sources": ["GDPR Article 32"],
                "compliance_score": 88,
            },
            "iso27001": {
                "response": "ISO 27001 requires cryptographic controls as specified in Annex A.10",
                "confidence": 0.91,
                "sources": ["ISO 27001 Annex A.10"],
                "compliance_score": 92,
            },
            "soc2": {
                "response": "SOC 2 Type II requires encryption controls for data in transit and at rest (CC6.1)",
                "confidence": 0.87,
                "sources": ["SOC 2 CC6.1"],
                "compliance_score": 85,
            },
        }

        for framework in frameworks:
            with patch.object(
                ai_assistant, "_generate_gemini_response", return_value=mock_responses[framework]
            ):
                response = await ai_assistant.process_message(
                    message=query, framework=framework, user_id="test_user_cross_framework"
                )
                responses[framework] = response

        # Validate consistent structure across frameworks
        for framework, response in responses.items():
            assert "response" in response
            assert "confidence" in response
            assert "sources" in response
            assert "compliance_score" in response

            # Validate confidence range consistency
            assert 0.5 <= response["confidence"] <= 1.0
            assert 0 <= response["compliance_score"] <= 100

            # Validate sources format consistency
            assert isinstance(response["sources"], list)
            assert len(response["sources"]) > 0

    @pytest.mark.asyncio
    async def test_ui_format_consistency(self, ai_assistant, sample_queries):
        """Test that responses maintain consistent format for UI consumption"""
        expected_fields = {
            "response": str,
            "confidence": float,
            "sources": list,
            "compliance_score": (int, float),
            "metadata": dict,
            "timestamp": str,
        }

        # Mock response with all expected fields
        mock_response = {
            "response": "Test response content",
            "confidence": 0.85,
            "sources": ["Test Source 1", "Test Source 2"],
            "compliance_score": 82,
            "metadata": {"model_used": "gemini-pro", "processing_time": 1.2, "cache_hit": False},
            "timestamp": datetime.now().isoformat(),
        }

        with patch.object(ai_assistant, "_generate_gemini_response", return_value=mock_response):
            for query_type, query in sample_queries.items():
                response = await ai_assistant.process_message(
                    message=query, framework="gdpr", user_id=f"test_user_format_{query_type}"
                )

                # Validate all expected fields are present
                for field, field_type in expected_fields.items():
                    assert field in response, f"Missing field: {field} in {query_type}"
                    assert isinstance(response[field], field_type), (
                        f"Wrong type for {field} in {query_type}: expected {field_type}, got {type(response[field])}"
                    )

                # Validate specific UI requirements
                assert len(response["response"]) > 0, f"Empty response for {query_type}"
                assert 0 <= response["confidence"] <= 1, f"Invalid confidence for {query_type}"
                assert 0 <= response["compliance_score"] <= 100, (
                    f"Invalid compliance score for {query_type}"
                )

    @pytest.mark.asyncio
    async def test_edge_case_consistency(self, ai_assistant):
        """Test consistent handling of edge cases and error scenarios"""
        edge_cases = [
            {"query": "", "expected_error": "empty_query"},
            {"query": "x" * 10000, "expected_error": "query_too_long"},
            {"query": "What is the meaning of life?", "expected_behavior": "off_topic_response"},
            {"query": "Invalid unicode: \udcff\udcfe", "expected_behavior": "unicode_handling"},
        ]

        for case in edge_cases:
            query = case["query"]

            # Mock appropriate responses for edge cases
            if case.get("expected_error") == "empty_query":
                mock_response = {
                    "error": "Query cannot be empty",
                    "response": "Please provide a specific compliance question.",
                    "confidence": 0.0,
                    "sources": [],
                    "compliance_score": 0,
                }
            elif case.get("expected_error") == "query_too_long":
                mock_response = {
                    "error": "Query too long",
                    "response": "Please provide a more concise question.",
                    "confidence": 0.0,
                    "sources": [],
                    "compliance_score": 0,
                }
            else:
                mock_response = {
                    "response": "I can only assist with compliance-related questions.",
                    "confidence": 0.1,
                    "sources": [],
                    "compliance_score": 0,
                }

            with patch.object(
                ai_assistant, "_generate_gemini_response", return_value=mock_response
            ):
                response = await ai_assistant.process_message(
                    message=query, framework="gdpr", user_id="test_user_edge_case"
                )

                # Validate consistent error handling structure
                assert "response" in response
                assert "confidence" in response
                assert "sources" in response
                assert "compliance_score" in response

                # Edge cases should have low confidence
                if (
                    case.get("expected_error")
                    or case.get("expected_behavior") == "off_topic_response"
                ):
                    assert response["confidence"] <= 0.2

    @pytest.mark.asyncio
    async def test_concurrent_request_consistency(self, ai_assistant):
        """Test consistency under concurrent load"""
        query = "What are GDPR data subject rights?"
        concurrent_requests = 10

        # Mock consistent response
        mock_response = {
            "response": "GDPR data subject rights include: access, rectification, erasure, portability, restriction of processing, objection, and rights related to automated decision-making.",
            "confidence": 0.94,
            "sources": ["GDPR Articles 15-22"],
            "compliance_score": 96,
        }

        async def make_request(request_id: int):
            with patch.object(
                ai_assistant, "_generate_gemini_response", return_value=mock_response
            ):
                return await ai_assistant.process_message(
                    message=query, framework="gdpr", user_id=f"test_user_concurrent_{request_id}"
                )

        # Execute concurrent requests
        tasks = [make_request(i) for i in range(concurrent_requests)]
        responses = await asyncio.gather(*tasks)

        # Validate all requests completed successfully
        assert len(responses) == concurrent_requests

        # Validate response consistency
        first_response = responses[0]
        for i, response in enumerate(responses[1:], 1):
            assert response["response"] == first_response["response"], (
                f"Response {i} differs from first"
            )
            assert response["confidence"] == first_response["confidence"], (
                f"Confidence {i} differs from first"
            )
            assert response["sources"] == first_response["sources"], (
                f"Sources {i} differ from first"
            )


class TestAIPerformanceConsistency:
    """Test AI performance consistency and reliability"""

    @pytest.fixture
    async def performance_assistant(self):
        """AI assistant configured for performance testing"""
        return ComplianceAssistant(
            gemini_client=AsyncMock(),
            openai_client=AsyncMock(),
            circuit_breaker=AICircuitBreaker(),
            cache=AIResponseCache(),
            optimizer=AIPerformanceOptimizer(),
        )

    @pytest.mark.asyncio
    async def test_response_time_consistency(self, performance_assistant):
        """Test that response times remain consistent"""
        query = "Explain GDPR lawful bases for processing"
        response_times = []

        mock_response = {
            "response": "GDPR Article 6 defines six lawful bases for processing personal data...",
            "confidence": 0.91,
            "sources": ["GDPR Article 6"],
            "compliance_score": 93,
        }

        with patch.object(
            performance_assistant, "_generate_gemini_response", return_value=mock_response
        ):
            for _ in range(10):
                start_time = time.time()
                await performance_assistant.process_message(
                    message=query, framework="gdpr", user_id="test_user_performance"
                )
                end_time = time.time()
                response_times.append(end_time - start_time)

        # Validate response time consistency
        avg_response_time = statistics.mean(response_times)
        std_deviation = statistics.stdev(response_times)

        # Response times should be consistent (low standard deviation relative to mean)
        coefficient_of_variation = std_deviation / avg_response_time
        assert coefficient_of_variation < 0.5, (
            f"Response times too variable: CV={coefficient_of_variation}"
        )

        # All response times should be reasonable
        assert all(rt < 10.0 for rt in response_times), "Some responses too slow"
        assert all(rt > 0.001 for rt in response_times), "Some responses suspiciously fast"

    @pytest.mark.asyncio
    async def test_memory_usage_consistency(self, performance_assistant):
        """Test that memory usage remains consistent across requests"""
        import psutil
        import os

        query = "Compare ISO 27001 and SOC 2 controls"
        process = psutil.Process(os.getpid())
        memory_usage = []

        mock_response = {
            "response": "Both ISO 27001 and SOC 2 provide comprehensive security frameworks...",
            "confidence": 0.88,
            "sources": ["ISO 27001 Annex A", "SOC 2 Trust Principles"],
            "compliance_score": 90,
        }

        with patch.object(
            performance_assistant, "_generate_gemini_response", return_value=mock_response
        ):
            for _ in range(5):
                initial_memory = process.memory_info().rss

                await performance_assistant.process_message(
                    message=query, framework="iso27001", user_id="test_user_memory"
                )

                final_memory = process.memory_info().rss
                memory_usage.append(final_memory - initial_memory)

        # Memory usage should not grow unbounded
        total_memory_growth = sum(memory_usage)
        assert total_memory_growth < 100 * 1024 * 1024, (
            "Excessive memory growth detected"
        )  # 100MB limit

    @pytest.mark.asyncio
    async def test_error_recovery_consistency(self, performance_assistant):
        """Test consistent error recovery behavior"""
        query = "What are the GDPR penalties?"

        # Test scenario where first request fails, subsequent succeed
        responses = []
        call_count = 0

        def mock_response_with_failure(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Simulated AI service failure")
            return {
                "response": "GDPR penalties can be up to 4% of annual global turnover or €20 million, whichever is higher.",
                "confidence": 0.96,
                "sources": ["GDPR Article 83"],
                "compliance_score": 98,
            }

        with patch.object(
            performance_assistant,
            "_generate_gemini_response",
            side_effect=mock_response_with_failure,
        ):
            # First request should handle error gracefully
            response1 = await performance_assistant.process_message(
                message=query, framework="gdpr", user_id="test_user_error_recovery"
            )
            responses.append(response1)

            # Subsequent requests should succeed
            for _ in range(3):
                response = await performance_assistant.process_message(
                    message=query, framework="gdpr", user_id="test_user_error_recovery"
                )
                responses.append(response)

        # Validate error recovery
        assert len(responses) == 4

        # First response should contain error handling
        assert "response" in responses[0]  # Should have fallback response

        # Subsequent responses should be successful and consistent
        for response in responses[1:]:
            assert response["confidence"] > 0.9
            assert "GDPR penalties" in response["response"]
            assert response["compliance_score"] > 90


class TestAIQualityConsistency:
    """Test AI output quality consistency"""

    @pytest.fixture
    async def quality_assistant(self):
        """AI assistant configured for quality testing"""
        return ComplianceAssistant(
            gemini_client=AsyncMock(),
            openai_client=AsyncMock(),
            circuit_breaker=AICircuitBreaker(),
            cache=AIResponseCache(),
            optimizer=AIPerformanceOptimizer(),
        )

    @pytest.mark.asyncio
    async def test_response_quality_metrics(self, quality_assistant):
        """Test that quality metrics remain consistent"""
        test_queries = [
            "What is GDPR?",
            "Explain ISO 27001 certification process",
            "How to implement SOC 2 controls?",
            "Compare privacy frameworks",
            "Data breach notification requirements",
        ]

        quality_metrics = []

        for i, query in enumerate(test_queries):
            mock_response = {
                "response": f"Comprehensive answer to: {query}. This includes detailed explanations, practical examples, and regulatory references.",
                "confidence": 0.90 + (i * 0.01),  # Slight variation
                "sources": [f"Regulation {i + 1}", f"Standard {i + 1}"],
                "compliance_score": 90 + i,
                "metadata": {
                    "word_count": 150 + (i * 10),
                    "technical_terms": 5 + i,
                    "citations": 2,
                },
            }

            with patch.object(
                quality_assistant, "_generate_gemini_response", return_value=mock_response
            ):
                response = await quality_assistant.process_message(
                    message=query, framework="gdpr", user_id=f"test_user_quality_{i}"
                )

                quality_metrics.append(
                    {
                        "confidence": response["confidence"],
                        "compliance_score": response["compliance_score"],
                        "response_length": len(response["response"]),
                        "source_count": len(response["sources"]),
                        "has_metadata": "metadata" in response,
                    }
                )

        # Validate quality consistency
        confidences = [m["confidence"] for m in quality_metrics]
        compliance_scores = [m["compliance_score"] for m in quality_metrics]

        # Confidence should be consistently high
        assert all(c >= 0.8 for c in confidences), "Some responses have low confidence"
        assert statistics.mean(confidences) >= 0.85, "Average confidence too low"

        # Compliance scores should be consistently good
        assert all(s >= 80 for s in compliance_scores), "Some compliance scores too low"
        assert statistics.mean(compliance_scores) >= 85, "Average compliance score too low"

        # All responses should have sources
        assert all(m["source_count"] > 0 for m in quality_metrics), "Some responses lack sources"

    @pytest.mark.asyncio
    async def test_citation_consistency(self, quality_assistant):
        """Test that citations are consistently formatted and relevant"""
        query = "What are the GDPR data protection principles?"

        # Mock response with properly formatted citations
        mock_response = {
            "response": "GDPR establishes seven data protection principles in Article 5...",
            "confidence": 0.94,
            "sources": [
                "GDPR Article 5(1)(a) - Lawfulness, fairness and transparency",
                "GDPR Article 5(1)(b) - Purpose limitation",
                "GDPR Article 5(1)(c) - Data minimisation",
            ],
            "compliance_score": 96,
            "citations": {
                "primary": ["GDPR Article 5"],
                "secondary": ["ICO Guidance on Principles", "EDPB Guidelines 4/2019"],
            },
        }

        # Test multiple requests to ensure citation consistency
        responses = []
        with patch.object(
            quality_assistant, "_generate_gemini_response", return_value=mock_response
        ):
            for _ in range(5):
                response = await quality_assistant.process_message(
                    message=query, framework="gdpr", user_id="test_user_citations"
                )
                responses.append(response)

        # Validate citation consistency
        first_sources = responses[0]["sources"]
        for response in responses[1:]:
            assert response["sources"] == first_sources, "Citations inconsistent across requests"

            # Validate citation format
            for source in response["sources"]:
                assert isinstance(source, str), "Citations must be strings"
                assert len(source) > 0, "Citations cannot be empty"
                # GDPR citations should reference articles
                if "GDPR" in source:
                    assert "Article" in source, "GDPR citations should reference articles"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
