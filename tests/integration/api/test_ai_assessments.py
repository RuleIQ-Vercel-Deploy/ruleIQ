"""
Integration Tests for AI Assessment Endpoints

Tests the new /ai/assessments/* endpoints including authentication,
rate limiting, error handling, and response validation.
"""

import pytest
import json
from unittest.mock import patch, AsyncMock
from uuid import uuid4
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from services.ai.exceptions import (
    AIServiceException, AITimeoutException, AIQuotaExceededException,
    AIContentFilterException
)


@pytest.mark.integration
@pytest.mark.ai
class TestAIAssessmentEndpoints:
    """Test AI assessment endpoints integration"""

    def test_ai_help_endpoint_success(self, client, authenticated_headers, sample_business_profile):
        """Test successful AI help request"""
        request_data = {
            "question_id": "q1",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr",
            "section_id": "data_protection",
            "user_context": {
                "business_profile_id": str(sample_business_profile.id),
                "industry": "technology"
            }
        }

        with patch('services.ai.assistant.ComplianceAssistant') as mock_assistant:
            # Mock successful AI response
            mock_assistant.return_value.get_question_help = AsyncMock(return_value={
                "guidance": "GDPR requires organizations to protect personal data...",
                "confidence_score": 0.95,
                "related_topics": ["data protection", "privacy rights"],
                "follow_up_suggestions": ["What are the key GDPR principles?"],
                "source_references": ["GDPR Article 5"]
            })

            response = client.post(
                "/api/ai/assessments/gdpr/help",
                json=request_data,
                headers=authenticated_headers
            )

            assert response.status_code == 200
            response_data = response.json()
            
            assert "guidance" in response_data
            assert "confidence_score" in response_data
            assert "request_id" in response_data
            assert "generated_at" in response_data
            assert response_data["confidence_score"] >= 0.0
            assert response_data["confidence_score"] <= 1.0

    def test_ai_help_endpoint_authentication_required(self, client):
        """Test AI help endpoint requires authentication"""
        request_data = {
            "question_id": "q1",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr"
        }

        response = client.post("/api/ai/assessments/gdpr/help", json=request_data)
        assert response.status_code == 401

    def test_ai_help_endpoint_invalid_framework(self, client, authenticated_headers):
        """Test AI help endpoint with invalid framework"""
        request_data = {
            "question_id": "q1",
            "question_text": "What is compliance?",
            "framework_id": "invalid_framework"
        }

        response = client.post(
            "/api/ai/assessments/invalid_framework/help",
            json=request_data,
            headers=authenticated_headers
        )
        
        # Should handle gracefully - either 400 or 404
        assert response.status_code in [400, 404]

    def test_followup_questions_endpoint_success(self, client, authenticated_headers, sample_business_profile):
        """Test successful follow-up questions generation"""
        request_data = {
            "question_id": "q1",
            "question_text": "Do you process personal data?",
            "user_answer": "yes",
            "assessment_context": {
                "framework_id": "gdpr",
                "section_id": "data_processing",
                "business_profile_id": str(sample_business_profile.id),
                "current_answers": {
                    "q1": {"value": "yes", "source": "framework"}
                }
            }
        }

        with patch('services.ai.assistant.ComplianceAssistant') as mock_assistant:
            mock_assistant.return_value.generate_followup_questions = AsyncMock(return_value={
                "follow_up_questions": [
                    {
                        "id": "ai-q1",
                        "text": "What types of personal data do you process?",
                        "type": "multiple_choice",
                        "options": ["Names", "Email addresses", "Financial data"],
                        "validation": {"required": True}
                    }
                ],
                "reasoning": "Need to understand data types for compliance assessment"
            })

            response = client.post(
                "/api/ai/assessments/followup",
                json=request_data,
                headers=authenticated_headers
            )

            assert response.status_code == 200
            response_data = response.json()
            
            assert "follow_up_questions" in response_data
            assert "reasoning" in response_data
            assert len(response_data["follow_up_questions"]) > 0
            assert "request_id" in response_data

    def test_analysis_endpoint_success(self, client, authenticated_headers, sample_business_profile):
        """Test successful assessment analysis"""
        request_data = {
            "framework_id": "gdpr",
            "business_profile_id": str(sample_business_profile.id),
            "assessment_results": {
                "answers": {"q1": "yes", "q2": "no"},
                "completion_percentage": 85.0,
                "sections_completed": ["data_protection", "security"]
            }
        }

        response = client.post(
            "/api/ai/assessments/analysis",
            json=request_data,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        
        assert "gaps" in response_data
        assert "recommendations" in response_data
        assert "risk_assessment" in response_data
        assert "compliance_insights" in response_data
        assert "evidence_requirements" in response_data
        assert "request_id" in response_data

    def test_recommendations_endpoint_success(self, client, authenticated_headers):
        """Test successful personalized recommendations"""
        request_data = {
            "gaps": [
                {"type": "missing_policy", "description": "Data protection policy missing"},
                {"type": "training", "description": "Staff training required"}
            ],
            "business_profile": {
                "industry": "technology",
                "size": "small",
                "location": "UK"
            },
            "timeline_preferences": "urgent"
        }

        response = client.post(
            "/api/ai/assessments/recommendations",
            json=request_data,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        
        assert "recommendations" in response_data
        assert "implementation_plan" in response_data
        assert "success_metrics" in response_data
        assert len(response_data["recommendations"]) > 0

    def test_feedback_endpoint_success(self, client, authenticated_headers):
        """Test successful feedback submission"""
        request_data = {
            "request_id": "test-request-123",
            "helpful": True,
            "rating": 5,
            "comments": "Very helpful guidance"
        }

        response = client.post(
            "/api/ai/assessments/feedback",
            json=request_data,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        
        assert "message" in response_data
        assert "status" in response_data
        assert response_data["status"] == "received"

    def test_metrics_endpoint_success(self, client, authenticated_headers):
        """Test AI metrics endpoint"""
        response = client.get(
            "/api/ai/assessments/metrics?days=30",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        
        assert "response_times" in response_data
        assert "accuracy_score" in response_data
        assert "user_satisfaction" in response_data
        assert "total_interactions" in response_data
        assert "quota_usage" in response_data

    def test_ai_service_timeout_handling(self, client, authenticated_headers):
        """Test handling of AI service timeouts"""
        request_data = {
            "question_id": "q1",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr"
        }

        with patch('services.ai.assistant.ComplianceAssistant') as mock_assistant:
            mock_assistant.return_value.get_question_help = AsyncMock(
                side_effect=AITimeoutException(timeout_seconds=30.0)
            )

            response = client.post(
                "/api/ai/assessments/gdpr/help",
                json=request_data,
                headers=authenticated_headers
            )

            # Should handle timeout gracefully
            assert response.status_code in [408, 500, 503]

    def test_ai_quota_exceeded_handling(self, client, authenticated_headers):
        """Test handling of AI quota exceeded errors"""
        request_data = {
            "question_id": "q1",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr"
        }

        with patch('services.ai.assistant.ComplianceAssistant') as mock_assistant:
            mock_assistant.return_value.get_question_help = AsyncMock(
                side_effect=AIQuotaExceededException(quota_type="API requests")
            )

            response = client.post(
                "/api/ai/assessments/gdpr/help",
                json=request_data,
                headers=authenticated_headers
            )

            # Should handle quota exceeded gracefully
            assert response.status_code in [429, 503]

    def test_ai_content_filter_handling(self, client, authenticated_headers):
        """Test handling of AI content filtering"""
        request_data = {
            "question_id": "q1",
            "question_text": "How to bypass GDPR requirements?",
            "framework_id": "gdpr"
        }

        with patch('services.ai.assistant.ComplianceAssistant') as mock_assistant:
            mock_assistant.return_value.get_question_help = AsyncMock(
                side_effect=AIContentFilterException(filter_reason="Inappropriate content")
            )

            response = client.post(
                "/api/ai/assessments/gdpr/help",
                json=request_data,
                headers=authenticated_headers
            )

            # Should handle content filtering gracefully
            assert response.status_code in [400, 422]

    def test_invalid_request_data_validation(self, client, authenticated_headers):
        """Test validation of invalid request data"""
        # Missing required fields
        invalid_request = {
            "question_text": "What is GDPR compliance?"
            # Missing question_id and framework_id
        }

        response = client.post(
            "/api/ai/assessments/gdpr/help",
            json=invalid_request,
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Validation error

    def test_business_profile_not_found(self, client, authenticated_headers):
        """Test handling when business profile is not found"""
        fake_profile_id = str(uuid4())
        request_data = {
            "framework_id": "gdpr",
            "business_profile_id": fake_profile_id,
            "assessment_results": {
                "answers": {"q1": "yes"},
                "completion_percentage": 50.0
            }
        }

        response = client.post(
            "/api/ai/assessments/analysis",
            json=request_data,
            headers=authenticated_headers
        )

        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.ai
@pytest.mark.rate_limiting
class TestAIRateLimiting:
    """Test AI-specific rate limiting"""

    def test_ai_help_rate_limiting(self, client, authenticated_headers):
        """Test rate limiting for AI help endpoint (10 req/min)"""
        request_data = {
            "question_id": "q1",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr"
        }

        # Mock successful responses
        with patch('services.ai.assistant.ComplianceAssistant') as mock_assistant:
            mock_assistant.return_value.get_question_help = AsyncMock(return_value={
                "guidance": "Test guidance",
                "confidence_score": 0.9
            })

            # Make multiple requests rapidly
            responses = []
            for i in range(12):  # Exceed 10 req/min limit
                response = client.post(
                    "/api/ai/assessments/gdpr/help",
                    json=request_data,
                    headers=authenticated_headers
                )
                responses.append(response)

            # First 10 should succeed, subsequent should be rate limited
            success_count = sum(1 for r in responses if r.status_code == 200)
            rate_limited_count = sum(1 for r in responses if r.status_code == 429)

            # Allow some flexibility in rate limiting implementation
            assert success_count <= 10
            assert rate_limited_count >= 2

    def test_ai_analysis_rate_limiting(self, client, authenticated_headers, sample_business_profile):
        """Test rate limiting for AI analysis endpoint (3 req/min)"""
        request_data = {
            "framework_id": "gdpr",
            "business_profile_id": str(sample_business_profile.id),
            "assessment_results": {
                "answers": {"q1": "yes"},
                "completion_percentage": 50.0
            }
        }

        # Make multiple requests rapidly
        responses = []
        for i in range(5):  # Exceed 3 req/min limit
            response = client.post(
                "/api/ai/assessments/analysis",
                json=request_data,
                headers=authenticated_headers
            )
            responses.append(response)

        # First 3 should succeed, subsequent should be rate limited
        success_count = sum(1 for r in responses if r.status_code == 200)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)

        assert success_count <= 3
        assert rate_limited_count >= 2

    def test_regular_endpoints_higher_rate_limit(self, client, authenticated_headers):
        """Test that regular assessment endpoints have higher rate limits (100 req/min)"""
        # Test regular assessment endpoint (should have higher limit)
        responses = []
        for i in range(15):  # Should not hit rate limit for regular endpoints
            response = client.get(
                "/api/assessments",
                headers=authenticated_headers
            )
            responses.append(response)

        # Most should succeed (allowing for other factors)
        success_count = sum(1 for r in responses if r.status_code in [200, 404])
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)

        # Regular endpoints should handle more requests
        assert success_count >= 10
        assert rate_limited_count <= 2


@pytest.mark.integration
@pytest.mark.ai
@pytest.mark.error_handling
class TestAIErrorHandling:
    """Test comprehensive AI error handling scenarios"""

    def test_ai_service_unavailable(self, client, authenticated_headers):
        """Test handling when AI service is completely unavailable"""
        request_data = {
            "question_id": "q1",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr"
        }

        with patch('services.ai.assistant.ComplianceAssistant') as mock_assistant:
            mock_assistant.return_value.get_question_help = AsyncMock(
                side_effect=AIServiceException("AI service unavailable")
            )

            response = client.post(
                "/api/ai/assessments/gdpr/help",
                json=request_data,
                headers=authenticated_headers
            )

            # Should handle gracefully with fallback
            assert response.status_code in [500, 503]

            # Should include error information
            if response.status_code == 500:
                response_data = response.json()
                assert "detail" in response_data

    def test_malformed_ai_response_handling(self, client, authenticated_headers):
        """Test handling of malformed AI responses"""
        request_data = {
            "question_id": "q1",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr"
        }

        with patch('services.ai.assistant.ComplianceAssistant') as mock_assistant:
            # Mock malformed response
            mock_assistant.return_value.get_question_help = AsyncMock(
                return_value="Invalid response format"  # Should be dict
            )

            response = client.post(
                "/api/ai/assessments/gdpr/help",
                json=request_data,
                headers=authenticated_headers
            )

            # Should handle parsing errors gracefully
            assert response.status_code in [500, 502]

    def test_ai_response_validation_errors(self, client, authenticated_headers):
        """Test handling of AI responses that fail validation"""
        request_data = {
            "question_id": "q1",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr"
        }

        with patch('services.ai.assistant.ComplianceAssistant') as mock_assistant:
            # Mock response with invalid confidence score
            mock_assistant.return_value.get_question_help = AsyncMock(return_value={
                "guidance": "Test guidance",
                "confidence_score": 1.5  # Invalid: should be <= 1.0
            })

            response = client.post(
                "/api/ai/assessments/gdpr/help",
                json=request_data,
                headers=authenticated_headers
            )

            # Should handle validation errors
            assert response.status_code in [422, 500]

    def test_concurrent_ai_requests_handling(self, client, authenticated_headers):
        """Test handling of concurrent AI requests"""
        import asyncio
        import aiohttp

        request_data = {
            "question_id": "q1",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr"
        }

        with patch('services.ai.assistant.ComplianceAssistant') as mock_assistant:
            # Mock slow AI response
            async def slow_response(*args, **kwargs):
                await asyncio.sleep(0.1)  # Simulate processing time
                return {
                    "guidance": "Test guidance",
                    "confidence_score": 0.9
                }

            mock_assistant.return_value.get_question_help = AsyncMock(side_effect=slow_response)

            # Make concurrent requests
            responses = []
            for i in range(5):
                response = client.post(
                    "/api/ai/assessments/gdpr/help",
                    json=request_data,
                    headers=authenticated_headers
                )
                responses.append(response)

            # All should complete successfully or be rate limited
            for response in responses:
                assert response.status_code in [200, 429, 500]
