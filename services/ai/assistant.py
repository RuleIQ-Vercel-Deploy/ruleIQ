"""
The primary AI service that orchestrates the conversational flow,
classifies user intent, and generates intelligent responses.
"""

from typing import Dict, List, Any, Tuple, Optional
from uuid import UUID
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session

# Use Google Generative AI since it's already configured in the project
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from .context_manager import ContextManager
from .prompt_templates import PromptTemplates
from services.evidence_service import get_user_evidence_items
from config.ai_config import get_ai_client

# Set up logging
logger = logging.getLogger(__name__)

class ComplianceAssistant:
    """AI-powered compliance assistant using Google Gemini."""

    def __init__(self, db: Session):
        self.db = db
        self.client = get_ai_client()  # Use the existing AI client
        self.context_manager = ContextManager(db)
        self.prompt_templates = PromptTemplates()
        
        # Configure safety settings for professional use
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

    async def process_message(
        self, 
        conversation_id: UUID, 
        user_id: UUID, 
        message: str, 
        business_profile_id: UUID
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Processes a user's message and generates a contextual response.
        Returns a tuple containing the response text and its metadata.
        """
        try:
            # Get conversation context
            context = await self.context_manager.get_conversation_context(
                conversation_id, business_profile_id
            )
            
            # Classify user intent
            intent = await self._classify_intent(message, context)
            
            # Route to the appropriate handler based on classified intent
            handler_map = {
                'evidence_query': self._handle_evidence_query,
                'compliance_check': self._handle_compliance_check,
                'guidance_request': self._handle_guidance_request,
                'general_query': self._handle_general_query
            }
            
            handler = handler_map.get(
                intent.get('type'), 
                self._handle_general_query
            )
            
            response, metadata = await handler(message, context, intent)
            
            # Add conversation metadata
            metadata.update({
                'conversation_id': str(conversation_id),
                'user_id': str(user_id),
                'business_profile_id': str(business_profile_id),
                'timestamp': datetime.utcnow().isoformat(),
                'model_used': 'gemini-2.5-flash-preview-05-20'
            })
            
            # Store the conversation turn in the database (placeholder)
            # This would be implemented when chat models are ready
            
            return response, metadata
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._get_error_response(), {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def _classify_intent(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Classifies user intent using Gemini."""
        try:
            prompt = self.prompt_templates.get_intent_classification_prompt(message, context)
            
            response = self.client.generate_content(
                f"{prompt['system']}\n\n{prompt['user']}",
                safety_settings=self.safety_settings,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Low temperature for consistent classification
                    max_output_tokens=500
                )
            )
            
            # Parse JSON response
            intent_data = json.loads(response.text)
            return intent_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse intent classification JSON: {e}")
            return {"type": "general_query", "confidence": 0.5, "entities": {}}
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return {"type": "general_query", "confidence": 0.5, "entities": {}}

    async def _handle_evidence_query(
        self, 
        message: str, 
        context: Dict[str, Any], 
        intent: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Handles queries related to finding and understanding evidence."""
        try:
            # Search for relevant evidence
            business_profile_id = UUID(context['business_profile_id'])
            evidence_items = await self.context_manager.get_relevant_evidence(
                business_profile_id, message, limit=10
            )
            
            # Generate response using evidence data
            prompt = self.prompt_templates.get_evidence_query_prompt(
                message, evidence_items, context
            )
            
            response_content = await self._generate_gemini_response(prompt)
            
            metadata = {
                'intent': 'evidence_query',
                'evidence_found': len(evidence_items),
                'evidence_types': list(set([
                    e.evidence_type for e in evidence_items if e.evidence_type
                ])),
                'entities': intent.get('entities', {})
            }
            
            return response_content, metadata
            
        except Exception as e:
            logger.error(f"Error handling evidence query: {e}")
            return self._get_error_response(), {'error': str(e)}

    async def _handle_compliance_check(
        self, 
        message: str, 
        context: Dict[str, Any], 
        intent: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Handles queries about compliance status and scores."""
        try:
            prompt = self.prompt_templates.get_compliance_check_prompt(message, context)
            response_content = await self._generate_gemini_response(prompt)
            
            metadata = {
                'intent': 'compliance_check',
                'overall_score': context.get('compliance_status', {}).get('overall_score', 0),
                'frameworks_assessed': list(context.get('compliance_status', {}).get('framework_scores', {}).keys()),
                'entities': intent.get('entities', {})
            }
            
            return response_content, metadata
            
        except Exception as e:
            logger.error(f"Error handling compliance check: {e}")
            return self._get_error_response(), {'error': str(e)}

    async def _handle_guidance_request(
        self, 
        message: str, 
        context: Dict[str, Any], 
        intent: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Handles requests for compliance guidance and recommendations."""
        try:
            prompt = self.prompt_templates.get_guidance_request_prompt(message, context)
            response_content = await self._generate_gemini_response(prompt)
            
            metadata = {
                'intent': 'guidance_request',
                'frameworks_mentioned': intent.get('entities', {}).get('frameworks', []),
                'guidance_type': 'general',  # Could be enhanced to classify guidance types
                'entities': intent.get('entities', {})
            }
            
            return response_content, metadata
            
        except Exception as e:
            logger.error(f"Error handling guidance request: {e}")
            return self._get_error_response(), {'error': str(e)}

    async def _handle_general_query(
        self, 
        message: str, 
        context: Dict[str, Any], 
        intent: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Handles general, non-specific queries."""
        try:
            history = await self.context_manager.get_conversation_history(
                UUID(context['conversation_id'])
            )
            
            prompt = self.prompt_templates.get_general_query_prompt(
                message, history, context
            )
            
            response_content = await self._generate_gemini_response(prompt)
            
            metadata = {
                'intent': 'general_query',
                'conversation_length': len(history),
                'entities': intent.get('entities', {})
            }
            
            return response_content, metadata
            
        except Exception as e:
            logger.error(f"Error handling general query: {e}")
            return self._get_error_response(), {'error': str(e)}

    async def _generate_gemini_response(self, prompt: Dict[str, str]) -> str:
        """Helper function to generate responses using Gemini."""
        try:
            full_prompt = f"{prompt['system']}\n\n{prompt['user']}"
            
            response = self.client.generate_content(
                full_prompt,
                safety_settings=self.safety_settings,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000,
                    top_p=0.9
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini response generation failed: {e}")
            return "I'm sorry, I encountered an error while processing your request. Please try again."

    def _get_error_response(self) -> str:
        """Returns a standard error response."""
        return "I apologize, but I'm experiencing some technical difficulties right now. Please try your question again, or contact support if the issue persists."

    async def get_evidence_recommendations(
        self, 
        business_profile_id: UUID, 
        framework: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generates evidence collection recommendations."""
        try:
            context = await self.context_manager.get_conversation_context(
                UUID('00000000-0000-0000-0000-000000000000'),  # Dummy conversation ID
                business_profile_id
            )
            
            business_context = context.get('business_profile', {})
            target_framework = framework or business_context.get('frameworks', ['ISO27001'])[0]
            
            prompt = self.prompt_templates.get_evidence_recommendation_prompt(
                target_framework, business_context
            )
            
            response = await self._generate_gemini_response(prompt)
            
            # Parse the response to extract recommendations
            # This is a simplified implementation - you could enhance with structured output
            return [{
                'framework': target_framework,
                'recommendations': response,
                'generated_at': datetime.utcnow().isoformat()
            }]
            
        except Exception as e:
            logger.error(f"Error generating evidence recommendations: {e}")
            return []

    async def analyze_evidence_gap(
        self, 
        business_profile_id: UUID, 
        framework: str
    ) -> Dict[str, Any]:
        """Analyzes gaps in evidence collection for a specific framework."""
        try:
            framework_context = await self.context_manager.get_framework_specific_context(
                business_profile_id, framework
            )
            
            gap_analysis = {
                'framework': framework,
                'completion_percentage': framework_context.get('completion_status', 0),
                'evidence_collected': framework_context.get('evidence_count', 0),
                'evidence_types': framework_context.get('evidence_types', []),
                'recent_activity': framework_context.get('recent_updates', 0),
                'recommendations': await self.get_evidence_recommendations(
                    business_profile_id, framework
                )
            }
            
            return gap_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing evidence gap: {e}")
            return {
                'framework': framework,
                'error': str(e),
                'completion_percentage': 0
            }