"""
The primary AI service that orchestrates the conversational flow, classifies user intent,
and generates intelligent responses asynchronously.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import requests
from google.generativeai.types import HarmBlockThreshold, HarmCategory
from sqlalchemy.ext.asyncio import AsyncSession

from config.ai_config import get_ai_model
from config.logging_config import get_logger
from core.exceptions import BusinessLogicException, DatabaseException, IntegrationException, NotFoundException
from database.user import User

from .analytics_monitor import MetricType, get_analytics_monitor
from .cached_content import CacheContentType, get_cached_content_manager
from .circuit_breaker import AICircuitBreaker
from .context_manager import ContextManager
from .exceptions import CircuitBreakerException, ModelUnavailableException
from .instruction_integration import get_instruction_manager
from .performance_optimizer import get_performance_optimizer
from .prompt_templates import PromptTemplates
from .quality_monitor import get_quality_monitor
from .response_cache import get_ai_cache
from .safety_manager import ContentType, SafetyDecision, get_safety_manager_for_user
from .tools import get_tool_schemas, tool_executor

logger = get_logger(__name__)


class ComplianceAssistant:
    """AI-powered compliance assistant using Google Gemini, with full async support."""

    def __init__(self, db: AsyncSession, user_context: Optional[Dict[str, Any]] = None) -> None:
        self.db = db
        self.user_context = user_context or {}
        self.model = None
        self.context_manager = ContextManager(db)
        self.prompt_templates = PromptTemplates()
        self.instruction_manager = get_instruction_manager()
        self.ai_cache = None
        self.cached_content_manager = None
        self.performance_optimizer = None
        self.analytics_monitor = None
        self.quality_monitor = None
        self.circuit_breaker = AICircuitBreaker()
        self.safety_manager = get_safety_manager_for_user(self.user_context)
        self.content_type_map = {
            "assessment_help": ContentType.ASSESSMENT_GUIDANCE,
            "evidence_recommendations": ContentType.EVIDENCE_CLASSIFICATION,
            "policy_generation": ContentType.POLICY_GENERATION,
            "compliance_analysis": ContentType.COMPLIANCE_ANALYSIS,
            "general": ContentType.GENERAL_QUESTION,
        }
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

    def _get_task_appropriate_model(
        self,
        task_type: str,
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        cached_content=None,
    ) -> Tuple[Any, str]:
        """
        Get the most appropriate model for the given task type with system instructions and circuit breaker protection

        Args:
            task_type: Type of task (help, analysis, recommendations, etc.)
            context: Additional context for model selection
            tools: List of tool schemas for function calling
            cached_content: Optional Google CachedContent for improved performance

        Returns:
            Tuple of (configured AI model instance, instruction_id)

        Raises:
            ModelUnavailableException: If no models are available
        """
        model_context = {
            "task_type": task_type,
            "prompt_length": context.get("prompt_length", 0) if context else 0,
            "framework": context.get("framework") if context else None,
            "business_context": context.get("business_context", {}) if context else {},
        }
        if task_type in ["help", "guidance"]:
            complexity = "simple"
            prefer_speed = True
        elif task_type in ["analysis", "assessment", "gap_analysis"]:
            complexity = "complex"
            prefer_speed = False
        elif task_type in ["recommendations", "followup"]:
            complexity = "medium"
            prefer_speed = False
        else:
            complexity = "auto"
            prefer_speed = False
        from config.ai_config import MODEL_METADATA, AIModelType

        if not self.circuit_breaker.can_make_request():
            logger.warning("Circuit breaker is open - using fallback models")
            fallback_models = [AIModelType.GEMMA_8B, AIModelType.FLASH_8B]
            for model_type in fallback_models:
                if self.circuit_breaker.can_make_request(model_type.value):
                    logger.info("Using fallback model: %s" % model_type.value)
                    break
            else:
                raise ModelUnavailableException("All models unavailable")
        if cached_content and hasattr(cached_content, "model"):
            logger.info("Using model from cached content")
            model = cached_content.model
            instruction_id = "cached_content"
        else:
            if prefer_speed:
                available_models = [AIModelType.FLASH_8B, AIModelType.FLASH, AIModelType.PRO]
            elif complexity == "complex":
                available_models = [AIModelType.PRO, AIModelType.FLASH]
            else:
                available_models = [AIModelType.FLASH, AIModelType.PRO, AIModelType.FLASH_8B]
            selected_model_type = None
            for model_type in available_models:
                if self.circuit_breaker.can_make_request(model_type.value):
                    selected_model_type = model_type
                    break
            if not selected_model_type:
                raise ModelUnavailableException("No suitable models available for task")
            model_metadata = MODEL_METADATA[selected_model_type]
            logger.info("Selected model %s for task %s" % (selected_model_type.value, task_type))
            instruction_id = self.instruction_manager.get_instruction_id(
                task_type=task_type,
                complexity=complexity,
                business_context=self.user_context.get("business_context", {}),
            )
            system_instruction = self.instruction_manager.get_instruction(instruction_id)
            logger.debug("Using instruction template: %s" % instruction_id)
            try:
                model = get_ai_model(
                    model_type=selected_model_type,
                    system_instruction=system_instruction,
                    tools=tools,
                    safety_settings=self.safety_settings,
                )
            except Exception as e:
                logger.error("Failed to initialize model %s: %s" % (selected_model_type.value, e))
                self.circuit_breaker.record_failure(selected_model_type.value)
                for fallback_type in available_models:
                    if fallback_type != selected_model_type and self.circuit_breaker.can_make_request(
                        fallback_type.value
                    ):
                        try:
                            logger.info("Attempting fallback to %s" % fallback_type.value)
                            model = get_ai_model(
                                model_type=fallback_type,
                                system_instruction=system_instruction,
                                tools=tools,
                                safety_settings=self.safety_settings,
                            )
                            selected_model_type = fallback_type
                            break
                        except Exception as fallback_error:
                            logger.error("Fallback to %s failed: %s" % (fallback_type.value, fallback_error))
                            self.circuit_breaker.record_failure(fallback_type.value)
                else:
                    raise ModelUnavailableException("All model initialization attempts failed")
        return model, instruction_id

    async def initialize(self) -> None:
        """Asynchronously initialize services that require async setup."""
        if self.ai_cache is None:
            self.ai_cache = await get_ai_cache()
        if self.cached_content_manager is None:
            self.cached_content_manager = await get_cached_content_manager()
        if self.performance_optimizer is None:
            self.performance_optimizer = await get_performance_optimizer()
        if self.analytics_monitor is None:
            self.analytics_monitor = await get_analytics_monitor()
        if self.quality_monitor is None:
            self.quality_monitor = await get_quality_monitor()

    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[UUID] = None,
        conversation_id: Optional[UUID] = None,
        stream: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> AsyncIterator[str]:
        """
        Generate a response with async support and streaming capability.

        Args:
            prompt: The user's input prompt
            context: Optional context including business info, framework, etc.
            user_id: Optional user ID for personalization
            conversation_id: Optional conversation ID for context
            stream: Whether to stream the response
            tools: Optional list of tool schemas for function calling

        Yields:
            Response chunks if streaming, otherwise returns complete response
        """
        await self.initialize()
        start_time = asyncio.get_event_loop().time()
        task_type = await self._classify_intent(prompt, context)
        content_type = self.content_type_map.get(task_type, ContentType.GENERAL_QUESTION)
        safety_decision = await self.safety_manager.check_content(
            content=prompt, content_type=content_type, user_id=user_id
        )
        if safety_decision.action == "block":
            error_response = "I cannot process this request as it may violate content guidelines. " + (
                safety_decision.message or "Please rephrase your question."
            )
            yield error_response
        cache_key = self.ai_cache.generate_cache_key(prompt=prompt, context=context, task_type=task_type)
        if not stream:
            cached_response = await self.ai_cache.get(cache_key)
            if cached_response:
                logger.info("Cache hit for prompt (key: %s)" % cache_key[:16])
                await self.analytics_monitor.track_metric(MetricType.CACHE_HIT_RATE, 1.0, {"task_type": task_type})
                yield cached_response
        try:
            cached_content = None
            if self.cached_content_manager and task_type in ["assessment_help", "compliance_analysis"] and context:
                content_type_enum = (
                    CacheContentType.FRAMEWORK_GUIDANCE if "framework" in context else CacheContentType.GENERAL
                )
                cached_content = await self.cached_content_manager.get_or_create(
                    content_type=content_type_enum, context=context or {}, user_context=self.user_context
                )
            enhanced_context = await self.context_manager.get_enhanced_context(
                user_id=user_id, conversation_id=conversation_id, business_context=context
            )
            model, instruction_id = self._get_task_appropriate_model(
                task_type=task_type, context=enhanced_context, tools=tools, cached_content=cached_content
            )
            formatted_prompt = self.prompt_templates.format_prompt(
                template_name=task_type, context={"user_query": prompt, **enhanced_context}
            )
            if cached_content:
                logger.info("Using cached content for improved performance")
                full_prompt = formatted_prompt
            else:
                full_prompt = formatted_prompt
            generation_config = {
                "temperature": 0.7 if task_type in ["creative", "recommendations"] else 0.3,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048 if task_type in ["analysis", "assessment"] else 1024,
            }
            if stream:
                response_stream = model.generate_content(
                    full_prompt,
                    generation_config=generation_config,
                    stream=True,
                    safety_settings=self.safety_settings,
                    tools=tools if tools else None,
                )
                full_response = []
                async for chunk in self._async_stream_wrapper(response_stream):
                    if chunk.text:
                        full_response.append(chunk.text)
                        yield chunk.text
                complete_response = "".join(full_response)
                asyncio.create_task(
                    self._post_generation_tasks(
                        complete_response, cache_key, task_type, user_id, conversation_id, start_time, instruction_id
                    )
                )
            else:
                response = model.generate_content(
                    full_prompt,
                    generation_config=generation_config,
                    safety_settings=self.safety_settings,
                    tools=tools if tools else None,
                )
                response_text = response.text
                await self._post_generation_tasks(
                    response_text, cache_key, task_type, user_id, conversation_id, start_time, instruction_id
                )
                yield response_text
            self.circuit_breaker.record_success(model._model_name if hasattr(model, "_model_name") else "unknown")
        except CircuitBreakerException as e:
            logger.error("Circuit breaker exception: %s" % str(e))
            fallback_response = await self._generate_fallback_response(task_type, prompt)
            yield fallback_response
        except Exception as e:
            logger.error("Error generating response: %s" % str(e), exc_info=True)
            if hasattr(model, "_model_name"):
                self.circuit_breaker.record_failure(model._model_name)
            error_response = await self._handle_generation_error(e, task_type)
            yield error_response

    async def _async_stream_wrapper(self, sync_stream):
        """Wrap synchronous streaming response for async iteration."""
        loop = asyncio.get_event_loop()
        for chunk in sync_stream:
            yield chunk
            await asyncio.sleep(0)

    async def _post_generation_tasks(
        self,
        response: str,
        cache_key: str,
        task_type: str,
        user_id: Optional[UUID],
        conversation_id: Optional[UUID],
        start_time: float,
        instruction_id: str,
    ) -> None:
        """Handle post-generation tasks like caching and analytics."""
        await self.ai_cache.set(cache_key, response)
        generation_time = asyncio.get_event_loop().time() - start_time
        await self.analytics_monitor.track_metric(
            MetricType.RESPONSE_TIME, generation_time, {"task_type": task_type, "instruction_id": instruction_id}
        )
        quality_score = await self.quality_monitor.evaluate_response(response=response, task_type=task_type)
        await self.analytics_monitor.track_metric(MetricType.QUALITY_SCORE, quality_score, {"task_type": task_type})
        if user_id and conversation_id:
            await self.context_manager.add_to_conversation(
                conversation_id=conversation_id, role="assistant", content=response
            )

    async def _classify_intent(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Classify the user's intent to determine appropriate response strategy.

        Args:
            prompt: The user's input
            context: Additional context

        Returns:
            Intent classification (e.g., 'assessment_help', 'policy_generation')
        """
        prompt_lower = prompt.lower()
        if any((keyword in prompt_lower for keyword in ["assessment", "readiness", "evaluate", "score"])):
            return "assessment_help"
        elif any((keyword in prompt_lower for keyword in ["evidence", "document", "proof", "artifact"])):
            return "evidence_recommendations"
        elif any((keyword in prompt_lower for keyword in ["policy", "procedure", "guideline", "standard"])):
            return "policy_generation"
        elif any((keyword in prompt_lower for keyword in ["gap", "missing", "analysis", "compliance"])):
            return "gap_analysis"
        elif any((keyword in prompt_lower for keyword in ["recommend", "suggest", "improve", "next"])):
            return "recommendations"
        elif any((keyword in prompt_lower for keyword in ["help", "how", "what", "explain"])):
            return "help"
        elif context and "followup" in context:
            return "followup"
        else:
            return "general"

    async def _generate_fallback_response(self, task_type: str, prompt: str) -> str:
        """Generate a fallback response when the primary model fails."""
        fallback_responses = {
            "assessment_help": "I apologize, but I'm currently experiencing technical difficulties. For assessment help, please review your framework requirements and current evidence documentation.",
            "evidence_recommendations": "I'm temporarily unable to provide specific recommendations. Please ensure you have documentation covering policies, procedures, and implementation evidence.",
            "policy_generation": "Policy generation is temporarily unavailable. Consider starting with a template that covers: Purpose, Scope, Responsibilities, Procedures, and Compliance requirements.",
            "general": "I'm experiencing technical issues at the moment. Please try again in a few moments or contact support if the issue persists.",
        }
        return fallback_responses.get(task_type, fallback_responses["general"])

    async def _handle_generation_error(self, error: Exception, task_type: str) -> str:
        """Handle errors during response generation."""
        if isinstance(error, IntegrationException):
            return "I encountered an issue connecting to external services. Please try again."
        elif isinstance(error, BusinessLogicException):
            return f"There was an issue processing your request: {str(error)}"
        else:
            logger.error("Unexpected error in generation: %s" % str(error))
            return await self._generate_fallback_response(task_type, "")

    async def close(self) -> None:
        """Clean up resources."""
        if self.ai_cache:
            await self.ai_cache.close()
        if self.cached_content_manager:
            await self.cached_content_manager.cleanup()
        if self.performance_optimizer:
            await self.performance_optimizer.shutdown()
        if self.analytics_monitor:
            await self.analytics_monitor.close()
