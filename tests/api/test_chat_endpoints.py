"""Tests for the chat and AI chat API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, UTC
from uuid import uuid4
import json

from api.main import app


class TestChatEndpoints:
    """Test suite for chat API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """Create authentication headers."""
        return {"Authorization": "Bearer test-token"}

    @pytest.fixture
    def mock_current_user(self):
        """Mock current user for authentication."""
        return {
            "user_id": str(uuid4()),
            "email": "test@example.com",
            "organization_id": str(uuid4()),
            "role": "user"
        }

    @pytest.fixture
    def sample_chat_message(self):
        """Create a sample chat message."""
        return {
            "message": "What are the key requirements for ISO 27001?",
            "conversation_id": str(uuid4()),
            "context": {
                "framework": "ISO 27001",
                "assessment_id": str(uuid4())
            }
        }

    def test_send_chat_message(self, client, auth_headers, sample_chat_message, mock_current_user):
        """Test sending a chat message."""
        with patch('api.dependencies.auth.get_current_user', return_value=mock_current_user):
            with patch('services.ai.assistant.process_message') as mock_process:
                mock_process.return_value = {
                    "response": "ISO 27001 requires implementing an ISMS...",
                    "message_id": str(uuid4()),
                    "suggestions": ["View requirements", "Start assessment"]
                }
                
                response = client.post(
                    "/api/v1/chat/message",
                    json=sample_chat_message,
                    headers=auth_headers
                )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "message_id" in data
        assert len(data["suggestions"]) > 0

    def test_get_chat_history(self, client, auth_headers, mock_current_user):
        """Test retrieving chat history."""
        conversation_id = str(uuid4())
        
        with patch('api.dependencies.auth.get_current_user', return_value=mock_current_user):
            with patch('services.iq_agent.get_conversation_history') as mock_history:
                mock_history.return_value = [
                    {
                        "message_id": str(uuid4()),
                        "role": "user",
                        "content": "Hello",
                        "timestamp": datetime.now(UTC).isoformat()
                    },
                    {
                        "message_id": str(uuid4()),
                        "role": "assistant",
                        "content": "Hello! How can I help?",
                        "timestamp": datetime.now(UTC).isoformat()
                    }
                ]
                
                response = client.get(
                    f"/api/v1/chat/history/{conversation_id}",
                    headers=auth_headers
                )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["role"] == "user"
        assert data[1]["role"] == "assistant"

    def test_create_conversation(self, client, auth_headers, mock_current_user):
        """Test creating a new conversation."""
        payload = {
            "title": "ISO 27001 Consultation",
            "type": "compliance_guidance",
            "metadata": {"framework": "ISO 27001"}
        }
        
        with patch('api.dependencies.auth.get_current_user', return_value=mock_current_user):
            with patch('services.iq_agent.create_conversation') as mock_create:
                mock_create.return_value = {
                    "conversation_id": str(uuid4()),
                    "title": payload["title"],
                    "created_at": datetime.now(UTC).isoformat()
                }
                
                response = client.post(
                    "/api/v1/chat/conversation",
                    json=payload,
                    headers=auth_headers
                )
        
        assert response.status_code == 201
        data = response.json()
        assert "conversation_id" in data
        assert data["title"] == "ISO 27001 Consultation"

    def test_list_conversations(self, client, auth_headers, mock_current_user):
        """Test listing user conversations."""
        with patch('api.dependencies.auth.get_current_user', return_value=mock_current_user):
            with patch('services.iq_agent.list_conversations') as mock_list:
                mock_list.return_value = [
                    {
                        "conversation_id": str(uuid4()),
                        "title": "GDPR Compliance",
                        "last_message": "How to handle data deletion?",
                        "updated_at": datetime.now(UTC).isoformat()
                    },
                    {
                        "conversation_id": str(uuid4()),
                        "title": "SOC 2 Preparation",
                        "last_message": "What controls are needed?",
                        "updated_at": datetime.now(UTC).isoformat()
                    }
                ]
                
                response = client.get(
                    "/api/v1/chat/conversations",
                    headers=auth_headers
                )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "GDPR Compliance"

    def test_delete_conversation(self, client, auth_headers, mock_current_user):
        """Test deleting a conversation."""
        conversation_id = str(uuid4())
        
        with patch('api.dependencies.auth.get_current_user', return_value=mock_current_user):
            with patch('services.iq_agent.delete_conversation') as mock_delete:
                mock_delete.return_value = True
                
                response = client.delete(
                    f"/api/v1/chat/conversation/{conversation_id}",
                    headers=auth_headers
                )
        
        assert response.status_code == 204

    def test_ai_chat_streaming(self, client, auth_headers, mock_current_user):
        """Test AI chat with streaming response."""
        payload = {
            "message": "Explain GDPR Article 17",
            "stream": True
        }
        
        with patch('api.dependencies.auth.get_current_user', return_value=mock_current_user):
            with patch('services.ai.assistant.stream_response') as mock_stream:
                mock_stream.return_value = iter([
                    "GDPR Article 17 ",
                    "covers the right ",
                    "to erasure..."
                ])
                
                response = client.post(
                    "/api/v1/chat/ai/stream",
                    json=payload,
                    headers=auth_headers
                )
        
        assert response.status_code == 200
        # Streaming responses tested differently

    def test_ai_suggestions(self, client, auth_headers, mock_current_user):
        """Test getting AI-powered suggestions."""
        context = {
            "current_page": "assessment",
            "framework": "ISO 27001",
            "completion": 45
        }
        
        with patch('api.dependencies.auth.get_current_user', return_value=mock_current_user):
            with patch('services.ai.assistant.get_suggestions') as mock_suggest:
                mock_suggest.return_value = [
                    {"action": "Complete risk assessment", "priority": "high"},
                    {"action": "Review security policies", "priority": "medium"},
                    {"action": "Schedule internal audit", "priority": "low"}
                ]
                
                response = client.post(
                    "/api/v1/chat/ai/suggestions",
                    json=context,
                    headers=auth_headers
                )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["priority"] == "high"

    def test_chat_search(self, client, auth_headers, mock_current_user):
        """Test searching through chat history."""
        query = "data protection"
        
        with patch('api.dependencies.auth.get_current_user', return_value=mock_current_user):
            with patch('services.iq_agent.search_conversations') as mock_search:
                mock_search.return_value = [
                    {
                        "conversation_id": str(uuid4()),
                        "message": "Data protection requires encryption...",
                        "relevance_score": 0.95
                    },
                    {
                        "conversation_id": str(uuid4()),
                        "message": "GDPR data protection principles...",
                        "relevance_score": 0.88
                    }
                ]
                
                response = client.get(
                    f"/api/v1/chat/search?q={query}",
                    headers=auth_headers
                )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["relevance_score"] > data[1]["relevance_score"]

    def test_export_conversation(self, client, auth_headers, mock_current_user):
        """Test exporting a conversation."""
        conversation_id = str(uuid4())
        
        with patch('api.dependencies.auth.get_current_user', return_value=mock_current_user):
            with patch('services.iq_agent.export_conversation') as mock_export:
                mock_export.return_value = {
                    "format": "pdf",
                    "content": b"PDF content here",
                    "filename": f"conversation_{conversation_id}.pdf"
                }
                
                response = client.get(
                    f"/api/v1/chat/export/{conversation_id}?format=pdf",
                    headers=auth_headers
                )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    def test_chat_feedback(self, client, auth_headers, mock_current_user):
        """Test submitting feedback for chat responses."""
        payload = {
            "message_id": str(uuid4()),
            "rating": 5,
            "feedback": "Very helpful response!",
            "tags": ["accurate", "detailed"]
        }
        
        with patch('api.dependencies.auth.get_current_user', return_value=mock_current_user):
            with patch('services.iq_agent.submit_feedback') as mock_feedback:
                mock_feedback.return_value = {"success": True}
                
                response = client.post(
                    "/api/v1/chat/feedback",
                    json=payload,
                    headers=auth_headers
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_chat_context_management(self, client, auth_headers, mock_current_user):
        """Test managing chat context."""
        conversation_id = str(uuid4())
        context_update = {
            "framework": "SOC 2",
            "assessment_id": str(uuid4()),
            "focus_area": "security"
        }
        
        with patch('api.dependencies.auth.get_current_user', return_value=mock_current_user):
            with patch('services.iq_agent.update_context') as mock_update:
                mock_update.return_value = {"success": True}
                
                response = client.put(
                    f"/api/v1/chat/context/{conversation_id}",
                    json=context_update,
                    headers=auth_headers
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_ai_compliance_advisor(self, client, auth_headers, mock_current_user):
        """Test AI compliance advisor endpoint."""
        query = {
            "question": "What are the penalties for GDPR violations?",
            "context": {
                "organization_size": "enterprise",
                "industry": "healthcare"
            }
        }
        
        with patch('api.dependencies.auth.get_current_user', return_value=mock_current_user):
            with patch('services.ai.assistant.answer_question') as mock_advisor:
                mock_advisor.return_value = {
                    "answer": "GDPR penalties can reach up to €20 million or 4% of annual turnover...",
                    "confidence": 0.92,
                    "sources": ["Article 83", "EDPB Guidelines"],
                    "related_questions": [
                        "How to avoid GDPR penalties?",
                        "What constitutes a GDPR violation?"
                    ]
                }
                
                response = client.post(
                    "/api/v1/chat/ai/advisor",
                    json=query,
                    headers=auth_headers
                )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["confidence"] > 0.9
        assert len(data["sources"]) > 0

    def test_chat_rate_limiting(self, client, auth_headers, mock_current_user):
        """Test rate limiting for chat endpoints."""
        with patch('api.dependencies.auth.get_current_user', return_value=mock_current_user):
            with patch('api.middleware.rate_limiter.general_limiter.check_rate_limit') as mock_limit:
                mock_limit.return_value = {"allowed": False, "retry_after": 60}
                
                response = client.post(
                    "/api/v1/chat/message",
                    json={"message": "test"},
                    headers=auth_headers
                )
        
        assert response.status_code == 429
        assert "Retry-After" in response.headers

    def test_chat_with_attachments(self, client, auth_headers, mock_current_user):
        """Test sending chat message with attachments."""
        with patch('api.dependencies.auth.get_current_user', return_value=mock_current_user):
            with patch('services.iq_agent.process_with_attachment') as mock_process:
                mock_process.return_value = {
                    "response": "I've analyzed the document...",
                    "extracted_info": {"type": "policy", "pages": 10}
                }
                
                files = {"file": ("document.pdf", b"PDF content", "application/pdf")}
                data = {"message": "Please review this policy document"}
                
                response = client.post(
                    "/api/v1/chat/message/attachment",
                    files=files,
                    data=data,
                    headers=auth_headers
                )
        
        assert response.status_code == 200
        result = response.json()
        assert "extracted_info" in result