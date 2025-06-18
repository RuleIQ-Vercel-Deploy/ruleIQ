"""
The primary AI service that orchestrates the conversational flow, classifies user intent,
and generates intelligent responses asynchronously.
"""

from typing import Dict, List, Any, Tuple, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from .context_manager import ContextManager
from .prompt_templates import PromptTemplates
from config.ai_config import get_ai_model
from database.models import User
from core.exceptions import IntegrationException, BusinessLogicException, NotFoundException, DatabaseException
from config.logging_config import get_logger

logger = get_logger(__name__)

class ComplianceAssistant:
    """AI-powered compliance assistant using Google Gemini, with full async support."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = get_ai_model()
        self.context_manager = ContextManager(db)
        self.prompt_templates = PromptTemplates()
        
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

    async def process_message(
        self, 
        conversation_id: UUID, 
        user: User, 
        message: str, 
        business_profile_id: UUID
    ) -> Tuple[str, Dict[str, Any]]:
        """Processes a user's message and generates a contextual response asynchronously."""
        try:
            context = await self.context_manager.get_conversation_context(conversation_id, business_profile_id)
            prompt = self.prompt_templates.get_main_prompt(message, context)
            response_text = await self._generate_gemini_response(prompt)
            
            metadata = {"timestamp": datetime.utcnow().isoformat(), "context_used": True}
            return response_text, metadata
            
        except (NotFoundException, DatabaseException, IntegrationException) as e:
            logger.warning(f"Known exception while processing message for conversation {conversation_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing message for conversation {conversation_id}: {e}", exc_info=True)
            raise BusinessLogicException("An unexpected error occurred while processing your message.") from e

    async def _generate_gemini_response(self, prompt: str) -> str:
        """Sends a prompt to the Gemini model and returns the text response."""
        try:
            response = await self.model.generate_content_async(prompt, safety_settings=self.safety_settings)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}", exc_info=True)
            raise IntegrationException("Failed to communicate with the AI service.") from e

    async def get_evidence_recommendations(
        self, 
        user: User,
        business_profile_id: UUID,
        target_framework: str
    ) -> List[Dict[str, Any]]:
        """Generates evidence collection recommendations based on business context."""
        try:
            context = await self.context_manager.get_conversation_context(UUID(), business_profile_id)
            business_context = context.get('business_profile', {})
            
            prompt = self.prompt_templates.get_evidence_recommendation_prompt(
                target_framework, business_context
            )
            
            response = await self._generate_gemini_response(prompt)
            
            return [{
                'framework': target_framework,
                'recommendations': response,
                'generated_at': datetime.utcnow().isoformat()
            }]
            
        except (NotFoundException, DatabaseException, IntegrationException) as e:
            logger.warning(f"Known exception while generating recommendations for business {business_profile_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating evidence recommendations for business {business_profile_id}: {e}", exc_info=True)
            raise BusinessLogicException("An unexpected error occurred while generating recommendations.") from e
