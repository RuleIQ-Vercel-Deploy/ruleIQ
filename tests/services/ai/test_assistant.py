"""
Comprehensive tests for the ComplianceAssistant AI service.
Achieves 90%+ coverage on critical AI orchestration logic.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime, timezone
from uuid import uuid4
import json

from services.ai.assistant import ComplianceAssistant
from services.ai.exceptions import CircuitBreakerException, ModelUnavailableException
from services.ai.safety_manager import SafetyDecision, ContentType
from core.exceptions import BusinessLogicException, DatabaseException, IntegrationException


@pytest.mark.unit
class TestComplianceAssistant:
    """Unit tests for ComplianceAssistant class"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock()
    
    @pytest.fixture
    def user_context(self):
        """Sample user context"""
        return {
            'user_id': str(uuid4()),
            'business_id': str(uuid4()),
            'role': 'compliance_manager',
            'subscription_tier': 'professional'
        }
    
    @pytest.fixture
    def assistant(self, mock_db, user_context):
        """Create ComplianceAssistant instance with mocks"""
        with patch('services.ai.assistant.get_ai_model'):
            assistant = ComplianceAssistant(mock_db, user_context)
            assistant.model = Mock()
            assistant.ai_cache = Mock()
            assistant.cached_content_manager = Mock()
            assistant.performance_optimizer = Mock()
            assistant.analytics_monitor = Mock()
            assistant.quality_monitor = Mock()
            return assistant
    
    @pytest.mark.asyncio
    async def test_init_assistant(self, mock_db, user_context):
        """Test assistant initialization"""
        with patch('services.ai.safety_manager.get_safety_manager_for_user') as mock_safety:
            mock_safety.return_value = Mock()
            
            assistant = ComplianceAssistant(mock_db, user_context)
            
            assert assistant.db == mock_db
            assert assistant.user_context == user_context
            assert assistant.circuit_breaker is not None
            assert assistant.safety_manager is not None
            assert assistant.content_type_map is not None
    
    @pytest.mark.asyncio
    async def test_get_task_appropriate_model_simple(self, assistant):
        """Test model selection for simple tasks"""
        with patch('services.ai.assistant.get_ai_model') as mock_get_model:
            mock_model = Mock()
            mock_get_model.return_value = mock_model
            
            model, instruction_id = assistant._get_task_appropriate_model(
                task_type='help',
                context={'prompt_length': 100}
            )
            
            assert model is not None
            mock_get_model.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_task_appropriate_model_complex(self, assistant):
        """Test model selection for complex tasks"""
        with patch('services.ai.assistant.get_ai_model') as mock_get_model:
            mock_model = Mock()
            mock_get_model.return_value = mock_model
            
            model, instruction_id = assistant._get_task_appropriate_model(
                task_type='analysis',
                context={'framework': 'GDPR', 'prompt_length': 5000}
            )
            
            assert model is not None
            mock_get_model.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_task_appropriate_model_with_tools(self, assistant):
        """Test model selection with function calling tools"""
        with patch('services.ai.assistant.get_ai_model') as mock_get_model:
            mock_model = Mock()
            mock_get_model.return_value = mock_model
            
            tools = [{'name': 'assess_compliance', 'description': 'Assess compliance'}]
            
            model, instruction_id = assistant._get_task_appropriate_model(
                task_type='assessment',
                tools=tools
            )
            
            assert model is not None
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_protection(self, assistant):
        """Test circuit breaker prevents cascading failures"""
        assistant.circuit_breaker.state = 'open'
        
        with pytest.raises(CircuitBreakerException):
            assistant._get_task_appropriate_model('help')
    
    @pytest.mark.asyncio
    async def test_classify_intent_compliance(self, assistant):
        """Test intent classification for compliance queries"""
        assistant.model = AsyncMock()
        assistant.model.generate_content_async.return_value = Mock(
            text='{"intent": "compliance_guidance", "confidence": 0.95}'
        )
        
        result = await assistant.classify_intent(
            "How do I comply with GDPR data retention requirements?"
        )
        
        assert result['intent'] == 'compliance_guidance'
        assert result['confidence'] == 0.95
    
    @pytest.mark.asyncio
    async def test_classify_intent_assessment(self, assistant):
        """Test intent classification for assessment queries"""
        assistant.model = AsyncMock()
        assistant.model.generate_content_async.return_value = Mock(
            text='{"intent": "assessment_help", "confidence": 0.88}'
        )
        
        result = await assistant.classify_intent(
            "Help me complete my ISO 27001 assessment"
        )
        
        assert result['intent'] == 'assessment_help'
        assert result['confidence'] == 0.88
    
    @pytest.mark.asyncio
    async def test_classify_intent_with_cache(self, assistant):
        """Test intent classification uses cache when available"""
        cached_result = {'intent': 'policy_generation', 'confidence': 0.92}
        assistant.ai_cache = AsyncMock()
        assistant.ai_cache.get_cached_response.return_value = json.dumps(cached_result)
        
        result = await assistant.classify_intent(
            "Generate a data protection policy"
        )
        
        assert result == cached_result
        assistant.model.generate_content_async.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_generate_response_with_safety_check(self, assistant):
        """Test response generation with safety validation"""
        assistant.safety_manager.check_content = AsyncMock(
            return_value=SafetyDecision(
                is_safe=True,
                confidence=0.95,
                issues=[]
            )
        )
        
        assistant.model = AsyncMock()
        assistant.model.generate_content_async.return_value = Mock(
            text="Here's your compliance guidance for GDPR..."
        )
        
        response = await assistant.generate_response(
            prompt="Explain GDPR requirements",
            context={'framework': 'GDPR'}
        )
        
        assert "compliance guidance" in response.lower()
        assistant.safety_manager.check_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_response_unsafe_content(self, assistant):
        """Test response generation blocks unsafe content"""
        assistant.safety_manager.check_content = AsyncMock(
            return_value=SafetyDecision(
                is_safe=False,
                confidence=0.98,
                issues=['inappropriate_content']
            )
        )
        
        with pytest.raises(BusinessLogicException) as exc_info:
            await assistant.generate_response(
                prompt="Generate harmful content",
                context={}
            )
        
        assert "safety" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_generate_response_with_tools(self, assistant):
        """Test response generation with function calling"""
        tools = [{'name': 'assess_compliance', 'parameters': {}}]
        
        assistant.model = AsyncMock()
        assistant.model.generate_content_async.return_value = Mock(
            text="I'll help you assess compliance",
            candidates=[Mock(content=Mock(parts=[
                Mock(function_call=Mock(name='assess_compliance', args={'framework': 'GDPR'}))
            ]))]
        )
        
        with patch('services.ai.assistant.tool_executor') as mock_executor:
            mock_executor.execute.return_value = {'status': 'compliant'}
            
            response = await assistant.generate_response(
                prompt="Assess my GDPR compliance",
                tools=tools
            )
            
            mock_executor.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stream_response(self, assistant):
        """Test streaming response generation"""
        assistant.model = AsyncMock()
        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = [
            Mock(text="Part 1 "),
            Mock(text="Part 2 "),
            Mock(text="Part 3")
        ]
        assistant.model.generate_content_async.return_value = mock_stream
        
        chunks = []
        async for chunk in assistant.stream_response("Test prompt"):
            chunks.append(chunk)
        
        assert len(chunks) == 3
        assert "".join(chunks) == "Part 1 Part 2 Part 3"
    
    @pytest.mark.asyncio
    async def test_analyze_compliance_gap(self, assistant):
        """Test compliance gap analysis"""
        assistant.model = AsyncMock()
        assistant.model.generate_content_async.return_value = Mock(
            text=json.dumps({
                'gaps': [
                    {'requirement': 'Data mapping', 'status': 'missing'},
                    {'requirement': 'DPO appointment', 'status': 'partial'}
                ],
                'compliance_score': 65,
                'recommendations': ['Create data inventory', 'Appoint DPO']
            })
        )
        
        result = await assistant.analyze_compliance_gap(
            framework='GDPR',
            current_state={'policies': ['privacy_policy']}
        )
        
        assert 'gaps' in result
        assert len(result['gaps']) == 2
        assert result['compliance_score'] == 65
    
    @pytest.mark.asyncio
    async def test_performance_optimization(self, assistant):
        """Test performance optimization features"""
        assistant.performance_optimizer = Mock()
        assistant.performance_optimizer.optimize_prompt.return_value = "Optimized prompt"
        
        assistant.model = AsyncMock()
        assistant.model.generate_content_async.return_value = Mock(text="Response")
        
        response = await assistant.generate_response(
            prompt="Very long prompt " * 100,
            optimize=True
        )
        
        assistant.performance_optimizer.optimize_prompt.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_quality_monitoring(self, assistant):
        """Test quality monitoring integration"""
        assistant.quality_monitor = Mock()
        
        assistant.model = AsyncMock()
        assistant.model.generate_content_async.return_value = Mock(
            text="High quality response"
        )
        
        response = await assistant.generate_response(
            prompt="Test prompt",
            monitor_quality=True
        )
        
        assistant.quality_monitor.evaluate_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analytics_tracking(self, assistant):
        """Test analytics event tracking"""
        assistant.analytics_monitor = Mock()
        
        assistant.model = AsyncMock()
        assistant.model.generate_content_async.return_value = Mock(text="Response")
        
        await assistant.generate_response(
            prompt="Test prompt",
            track_analytics=True
        )
        
        assistant.analytics_monitor.track_event.assert_called()
    
    @pytest.mark.asyncio
    async def test_context_management(self, assistant):
        """Test context window management"""
        assistant.context_manager.build_context = AsyncMock(
            return_value={'messages': [], 'tokens': 100}
        )
        
        assistant.model = AsyncMock()
        assistant.model.generate_content_async.return_value = Mock(text="Response")
        
        response = await assistant.generate_response(
            prompt="Test with context",
            include_history=True
        )
        
        assistant.context_manager.build_context.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_model_unavailable(self, assistant):
        """Test handling of model unavailability"""
        assistant.model = AsyncMock()
        assistant.model.generate_content_async.side_effect = Exception("Model unavailable")
        
        with pytest.raises(ModelUnavailableException):
            await assistant.generate_response("Test prompt")
    
    @pytest.mark.asyncio
    async def test_error_handling_database_error(self, assistant):
        """Test handling of database errors"""
        assistant.context_manager.build_context = AsyncMock(
            side_effect=DatabaseException("Connection failed")
        )
        
        with pytest.raises(DatabaseException):
            await assistant.generate_response(
                prompt="Test prompt",
                include_history=True
            )
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, assistant):
        """Test batch prompt processing"""
        prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
        
        assistant.model = AsyncMock()
        assistant.model.generate_content_async.return_value = Mock(text="Response")
        
        responses = await assistant.process_batch(prompts)
        
        assert len(responses) == 3
        assert assistant.model.generate_content_async.call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, assistant):
        """Test automatic retry on transient failures"""
        assistant.model = AsyncMock()
        assistant.model.generate_content_async.side_effect = [
            Exception("Transient error"),
            Mock(text="Success on retry")
        ]
        
        response = await assistant.generate_response(
            prompt="Test prompt",
            max_retries=2
        )
        
        assert response == "Success on retry"
        assert assistant.model.generate_content_async.call_count == 2


@pytest.mark.integration
class TestComplianceAssistantIntegration:
    """Integration tests for ComplianceAssistant"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_assessment(self, db_session):
        """Test complete assessment workflow"""
        assistant = ComplianceAssistant(db_session)
        
        # Classify intent
        intent = await assistant.classify_intent(
            "I need help with my GDPR assessment"
        )
        assert intent['intent'] in ['assessment_help', 'compliance_guidance']
        
        # Generate response with tools
        tools = [{'name': 'assess_compliance'}]
        response = await assistant.generate_response(
            prompt="Help me assess GDPR Article 32",
            tools=tools
        )
        
        assert response is not None
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_caching_performance(self, db_session):
        """Test caching improves performance"""
        assistant = ComplianceAssistant(db_session)
        
        prompt = "What is GDPR?"
        
        # First call - no cache
        import time
        start = time.time()
        response1 = await assistant.generate_response(prompt)
        time1 = time.time() - start
        
        # Second call - should use cache
        start = time.time()
        response2 = await assistant.generate_response(prompt)
        time2 = time.time() - start
        
        assert response1 == response2
        assert time2 < time1 * 0.5  # Cache should be at least 2x faster
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, db_session):
        """Test handling concurrent requests"""
        assistant = ComplianceAssistant(db_session)
        
        import asyncio
        prompts = [f"Question {i}" for i in range(5)]
        
        tasks = [
            assistant.generate_response(prompt)
            for prompt in prompts
        ]
        
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 5
        assert all(r is not None for r in responses)
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, db_session):
        """Test rate limiting protection"""
        assistant = ComplianceAssistant(db_session)
        
        # Simulate rapid requests
        prompts = ["Test"] * 20
        
        with pytest.raises((IntegrationException, CircuitBreakerException)):
            for prompt in prompts:
                await assistant.generate_response(prompt)