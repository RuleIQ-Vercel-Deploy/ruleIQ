"""
AI Configuration and Model Setup for ComplianceGPT

This module handles configuration and initialization of AI models,
primarily Google Generative AI for compliance content generation.
"""

## GOOGLE API

import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import google.generativeai as genai
else:
    try:
        import google.generativeai as genai
    except ImportError:
        genai = None

from dotenv import load_dotenv

# Import at top level
# Moved to local import to avoid circular import
# Moved to local import to avoid circular import
from config.logging_config import get_logger

load_dotenv()

# Constants for magic numbers
LARGE_PROMPT_THRESHOLD = 2000
MEDIUM_PROMPT_THRESHOLD = 1000
ENTERPRISE_EMPLOYEE_THRESHOLD = 1000
SIMPLE_COMPLEXITY_THRESHOLD = 0.3
COMPLEX_COMPLEXITY_THRESHOLD = 0.7


class ModelType(Enum):
    """Available AI model types"""

    # Legacy model for compatibility
    GEMINI_FLASH = "gemini-2.5-flash-preview-05-20"

    # New optimized model options
    GEMINI_25_PRO = "gemini-2.5-pro"
    GEMINI_25_FLASH = "gemini-2.5-flash"
    GEMMA_3 = "gemma-3-8b-it"


@dataclass
class ModelMetadata:
    """Metadata for AI model capabilities and characteristics"""

    name: str
    cost_score: float  # Lower is cheaper (1-10 scale)
    speed_score: float  # Higher is faster (1-10 scale)
    capability_score: float  # Higher is more capable (1-10 scale)
    max_tokens: int
    timeout_seconds: float

    @property
    def efficiency_score(self) -> float:
        """Calculate efficiency as capability/cost ratio"""
        return self.capability_score / self.cost_score if self.cost_score > 0 else 0


# Model fallback chain - order matters (best to worst)
MODEL_FALLBACK_CHAIN = [
    ModelType.GEMINI_25_PRO,
    ModelType.GEMINI_25_FLASH,
    ModelType.GEMMA_3,
]

# Model metadata mapping
MODEL_METADATA = {
    ModelType.GEMINI_25_PRO: ModelMetadata(
        name=ModelType.GEMINI_25_PRO.value,
        cost_score=8.0,
        speed_score=6.0,
        capability_score=10.0,
        max_tokens=8192,
        timeout_seconds=45.0,
    ),
    ModelType.GEMINI_25_FLASH: ModelMetadata(
        name=ModelType.GEMINI_25_FLASH.value,
        cost_score=4.0,
        speed_score=9.0,
        capability_score=8.0,
        max_tokens=4096,
        timeout_seconds=30.0,
    ),
    ModelType.GEMMA_3: ModelMetadata(
        name=ModelType.GEMMA_3.value,
        cost_score=1.0,
        speed_score=8.0,
        capability_score=5.0,
        max_tokens=2048,
        timeout_seconds=15.0,
    ),
    # Legacy model
    ModelType.GEMINI_FLASH: ModelMetadata(
        name=ModelType.GEMINI_FLASH.value,
        cost_score=4.0,
        speed_score=8.0,
        capability_score=7.0,
        max_tokens=2048,
        timeout_seconds=30.0,
    ),
}


class AIConfig:
    """AI Configuration Manager"""

    def __init__(self) -> None:
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.default_model = ModelType.GEMINI_25_FLASH.value  # Updated default
        self.default_model_type = ModelType.GEMINI_25_FLASH  # For test compatibility
        self.fallback_chain = MODEL_FALLBACK_CHAIN
        self.model_metadata = MODEL_METADATA
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 4096,  # Increased from 2048 for compliance analysis
        }
        # More permissive safety settings for compliance content
        # Compliance discussions may involve sensitive topics that need to be addressed
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH",  # More permissive for compliance discussions
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH",  # More permissive for compliance discussions
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",  # Keep restrictive for explicit content
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH",  # More permissive for compliance risk discussions
            },
        ]

        # Retry configuration
        self.retry_config = {
            "default": {
                "max_attempts": 3,
                "base_delay": 1.0,
                "max_delay": 60.0,
                "strategy": "exponential_backoff",
                "jitter": True,
            },
            "quick_operations": {
                "max_attempts": 2,
                "base_delay": 0.5,
                "max_delay": 10.0,
                "strategy": "linear_backoff",
                "jitter": True,
            },
            "long_operations": {
                "max_attempts": 5,
                "base_delay": 2.0,
                "max_delay": 120.0,
                "strategy": "exponential_backoff",
                "jitter": True,
            },
            "critical_operations": {
                "max_attempts": 7,
                "base_delay": 1.0,
                "max_delay": 60.0,
                "strategy": "fibonacci_backoff",
                "jitter": True,
            },
        }

        # Circuit breaker configuration
        self.circuit_breaker_config = {
            "failure_threshold": 5,
            "recovery_timeout": 60,
            "success_threshold": 3,
            "time_window": 60,
            "model_timeouts": {
                ModelType.GEMINI_25_PRO.value: 45.0,
                ModelType.GEMINI_25_FLASH.value: 30.0,
                ModelType.GEMMA_3.value: 15.0,
                ModelType.GEMINI_FLASH.value: 30.0,  # Legacy
            },
        }

        # Offline mode configuration
        self.offline_config = {
            "mode": os.getenv(
                "AI_OFFLINE_MODE", "enhanced"
            ),  # disabled, basic, enhanced, full
            "database_path": os.getenv("AI_OFFLINE_DB_PATH", "data/offline_ai.db"),
            "cache_ttl_hours": int(os.getenv("AI_OFFLINE_CACHE_TTL", "24")),
            "max_history_size": int(os.getenv("AI_OFFLINE_HISTORY_SIZE", "1000")),
            "enable_request_queuing": os.getenv(
                "AI_OFFLINE_QUEUE_REQUESTS", "true"
            ).lower()
            == "true",
        }

    def _initialize_google_ai(self) -> None:
        """Initialize Google Generative AI with API key"""
        # Skip actual API initialization if using mock AI in tests
        if os.getenv("USE_MOCK_AI", "false").lower() == "true":
            return

        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        if genai is None:
            raise ImportError("google.generativeai package is not installed")

        # Try different configuration methods based on library version
        try:
            genai.configure(api_key=self.google_api_key)
        except AttributeError:
            # Alternative configuration method for newer versions
            import google.ai.generativelanguage as glm

            glm.configure(api_key=self.google_api_key)
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        genai.configure(api_key=self.google_api_key)

    def get_model(
        self,
        model_type: Optional[ModelType] = None,
        system_instruction: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> genai.GenerativeModel:
        """Get configured AI model instance with optional system instruction and tools"""
        # Return mock model in test environment
        if os.getenv("USE_MOCK_AI", "false").lower() == "true":
            from unittest.mock import MagicMock

            mock_model = MagicMock()
            mock_model.generate_content.return_value.text = "Mock AI response"
            return mock_model

        model_name = model_type.value if model_type else self.default_model

        # Build model initialization parameters
        model_params = {
            "model_name": model_name,
            "generation_config": self.generation_config,
            "safety_settings": self.safety_settings,
        }

        # Add system instruction if provided
        if system_instruction:
            model_params["system_instruction"] = system_instruction

        # Add tools if provided
        if tools:
            model_params["tools"] = tools

        try:
            return genai.GenerativeModel(**model_params)
        except Exception:
            # Try once more with the same parameters (for test compatibility)
            return genai.GenerativeModel(**model_params)

    def update_generation_config(self, **kwargs) -> None:
        """Update generation configuration parameters"""
        self.generation_config.update(kwargs)

    def get_compliance_optimized_config(self) -> Dict[str, Any]:
        """Get AI configuration optimized for compliance content generation"""
        return {
            "temperature": 0.3,  # Lower temperature for more consistent, factual content
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 4096,  # Higher token limit for detailed policies
        }

    def get_creative_config(self) -> Dict[str, Any]:
        """Get AI configuration for more creative content generation"""
        return {
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 50,
            "max_output_tokens": 2048,
        }

    def get_structured_output_config(
        self, response_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get AI configuration optimized for structured JSON output"""
        config = {
            "temperature": 0.2,  # Very low temperature for consistent structured output
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 4096,
            "response_mime_type": "application/json",
        }

        # Add response schema if provided
        if response_schema:
            config["response_schema"] = response_schema

        return config

    def get_schema_aware_config(self, schema_type: str) -> Dict[str, Any]:
        """
        Get configuration with appropriate schema for response type

        Args:
            schema_type: Type of response schema (gap_analysis, recommendations, etc.)
        """

        from services.ai.response_formats import get_schema_for_response_type

        schema = get_schema_for_response_type(schema_type)
        return self.get_structured_output_config(schema)

    def get_model_with_schema(
        self,
        model_type: Optional[ModelType] = None,
        system_instruction: Optional[str] = None,
        response_schema_type: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> genai.GenerativeModel:
        """
        Get AI model configured for structured output with schema validation

        Args:
            model_type: Specific model to use
            system_instruction: System instruction
            response_schema_type: Type of response schema to enforce
            tools: List of tool schemas for function calling
        """
        model_name = model_type.value if model_type else self.default_model

        # Get appropriate generation config
        if response_schema_type:
            generation_config = self.get_schema_aware_config(response_schema_type)
        else:
            generation_config = self.generation_config

        # Build model initialization parameters
        model_params = {
            "model_name": model_name,
            "generation_config": generation_config,
            "safety_settings": self.safety_settings,
        }

        # Add system instruction if provided
        if system_instruction:
            model_params["system_instruction"] = system_instruction

        # Add tools if provided
        if tools:
            model_params["tools"] = tools

        return genai.GenerativeModel(**model_params)

    def get_retry_config(self, operation_type: str = "default") -> Dict[str, Any]:
        """
        Get retry configuration for specific operation type

        Args:
            operation_type: Type of operation ("default", "quick_operations",
                          "long_operations", "critical_operations")
        """
        return self.retry_config.get(operation_type, self.retry_config["default"])

    def get_circuit_breaker_config(self) -> Dict[str, Any]:
        """Get circuit breaker configuration"""
        return self.circuit_breaker_config.copy()

    def get_model_timeout(self, model_type: ModelType) -> float:
        """Get timeout for specific model"""
        return self.circuit_breaker_config["model_timeouts"].get(
            model_type.value,
            30.0,  # Default timeout
        )

    def update_retry_config(self, operation_type: str, **kwargs) -> None:
        """Update retry configuration for specific operation type"""
        if operation_type not in self.retry_config:
            self.retry_config[operation_type] = self.retry_config["default"].copy()
        self.retry_config[operation_type].update(kwargs)

    def update_circuit_breaker_config(self, **kwargs) -> None:
        """Update circuit breaker configuration"""
        self.circuit_breaker_config.update(kwargs)

    def get_offline_config(self) -> Dict[str, Any]:
        """Get offline mode configuration"""
        return self.offline_config.copy()

    def update_offline_config(self, **kwargs) -> None:
        """Update offline mode configuration"""
        self.offline_config.update(kwargs)

    def get_model_metadata(self, model_type: ModelType) -> ModelMetadata:
        """Get metadata for a specific model"""
        return MODEL_METADATA.get(model_type, MODEL_METADATA[ModelType.GEMINI_25_FLASH])

    def get_fallback_models(
        self, preferred_model: Optional[ModelType] = None
    ) -> List[ModelType]:
        """Get ordered list of fallback models starting from preferred model"""
        if preferred_model and preferred_model in MODEL_FALLBACK_CHAIN:
            # Start from preferred model and continue with rest of chain
            start_index = MODEL_FALLBACK_CHAIN.index(preferred_model)
            return MODEL_FALLBACK_CHAIN[start_index:]
        else:
            # Return full fallback chain
            return MODEL_FALLBACK_CHAIN.copy()

    def calculate_task_complexity_score(self, task_context: Dict[str, Any]) -> float:
        """
        Calculate task complexity score based on context

        Args:
            task_context: Dictionary containing task information

        Returns:
            Complexity score from 0.0 (simple) to 1.0 (complex)
        """
        score = 0.0

        # Framework complexity scoring
        framework = task_context.get("framework", "")
        if framework in ["GDPR", "HIPAA", "SOX"]:
            score += 0.3  # High regulatory complexity
        elif framework in ["ISO27001", "SOC2"]:
            score += 0.2  # Medium regulatory complexity
        else:
            score += 0.1  # Basic compliance

        # Task type complexity
        task_type = task_context.get("task_type", "")
        if "analysis" in task_type.lower() or "assessment" in task_type.lower():
            score += 0.3
        elif "recommendation" in task_type.lower():
            score += 0.2
        elif "help" in task_type.lower() or "guidance" in task_type.lower():
            score += 0.1

        # Content length indication
        prompt_length = task_context.get("prompt_length", 0)
        if prompt_length > 2000:
            score += 0.2
        elif prompt_length > 1000:
            score += 0.1

        # Business context complexity
        business_context = task_context.get("business_context", {})
        if business_context.get("employee_count", 0) > 1000:
            score += 0.1  # Enterprise complexity

        return min(1.0, score)

    def _calculate_task_complexity(self, task_context: Dict[str, Any]) -> str:
        """
        Calculate task complexity category based on context (for test compatibility)

        Args:
            task_context: Dictionary containing task information

        Returns:
            Complexity category: "simple", "medium", or "complex"
        """
        complexity_score = self.calculate_task_complexity_score(task_context)
        if complexity_score < 0.3:
            return "simple"
        elif complexity_score > 0.7:
            return "complex"
        else:
            return "medium"

    def get_optimal_model(
        self,
        task_complexity: str = "medium",
        prefer_speed: bool = False,
        task_context: Optional[Dict[str, Any]] = None,
    ) -> ModelType:
        """
        Get optimal model based on task complexity and preferences

        Args:
            task_complexity: "simple", "medium", "complex" or "auto" for automatic scoring
            prefer_speed: Whether to prioritize speed over capability
            task_context: Context for automatic complexity calculation
        """

        logger = get_logger(__name__)

        # Auto-calculate complexity if requested
        if task_complexity == "auto" and task_context:
            complexity_score = self.calculate_task_complexity_score(task_context)
            if complexity_score < 0.3:
                task_complexity = "simple"
            elif complexity_score > 0.7:
                task_complexity = "complex"
            else:
                task_complexity = "medium"

            logger.debug(
                f"Auto-calculated task complexity: {task_complexity} (score: {complexity_score:.2f})"
            )

        # Model selection decision tree
        if task_complexity == "simple":
            selected_model = (
                ModelType.GEMINI_25_FLASH_LIGHT
                if prefer_speed
                else ModelType.GEMINI_25_FLASH
            )
        elif task_complexity == "complex":
            selected_model = ModelType.GEMINI_25_PRO
        else:  # medium
            selected_model = ModelType.GEMINI_25_FLASH

        # Log model selection decision
        metadata = self.get_model_metadata(selected_model)
        logger.info(
            f"Model selected: {selected_model.value} for {task_complexity} task (efficiency: {metadata.efficiency_score:.2f})"
        )

        return selected_model

    def select_model_with_fallback(
        self,
        circuit_breaker,
        preferred_model: Optional[ModelType] = None,
        task_complexity: str = "medium",
    ) -> ModelType:
        """
        Select best available model considering circuit breaker state

        Args:
            circuit_breaker: Circuit breaker instance to check model availability
            preferred_model: Preferred model to try first
            task_complexity: Task complexity level

        Returns:
            Available model from fallback chain

        Raises:
            AIServiceException: If no models are available
        """
        # Get fallback chain starting from preferred model
        if preferred_model:
            fallback_models = self.get_fallback_models(preferred_model)
        else:
            # Use optimal model for task complexity as starting point
            optimal_model = self.get_optimal_model(task_complexity)
            fallback_models = self.get_fallback_models(optimal_model)

        # Find first available model
        for model_type in fallback_models:
            if circuit_breaker.is_model_available(model_type.value):
                return model_type

        # If no models available, raise exception

        from services.ai.exceptions import AIServiceException

        raise AIServiceException(
            message="No AI models available - all circuits are open",
            service_name="AI Model Selection",
            error_code="NO_MODELS_AVAILABLE",
            context={"attempted_models": [m.value for m in fallback_models]},
        )


# Global AI configuration instance
ai_config = AIConfig()


def get_ai_model(
    model_type: Optional[ModelType] = None,
    task_complexity: str = "medium",
    prefer_speed: bool = False,
    task_context: Optional[Dict[str, Any]] = None,
    system_instruction: Optional[str] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
) -> genai.GenerativeModel:
    """
    Convenience function to get AI model instance with intelligent selection, system instructions, and tools

    Args:
        model_type: Specific model to use (overrides intelligent selection)
        task_complexity: "simple", "medium", "complex", or "auto"
        prefer_speed: Whether to prioritize speed over capability
        task_context: Context for automatic complexity calculation
        system_instruction: System instruction to use with the model
        tools: List of tool schemas for function calling
    """
    if model_type is None:
        # Use intelligent model selection
        try:
            model_type = ai_config.get_optimal_model(
                task_complexity, prefer_speed, task_context
            )
        except Exception:
            # Fall back to default model if selection fails
            model_type = ai_config.default_model_type

    return ai_config.get_model(
        model_type, system_instruction=system_instruction, tools=tools
    )


def get_structured_ai_model(
    response_schema_type: str,
    model_type: Optional[ModelType] = None,
    task_complexity: str = "medium",
    prefer_speed: bool = False,
    task_context: Optional[Dict[str, Any]] = None,
    system_instruction: Optional[str] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
) -> genai.GenerativeModel:
    """
    Convenience function to get AI model configured for structured output with schema validation

    Args:
        response_schema_type: Type of response schema to enforce (gap_analysis, recommendations, etc.)
        model_type: Specific model to use (overrides intelligent selection)
        task_complexity: "simple", "medium", "complex", or "auto"
        prefer_speed: Whether to prioritize speed over capability
        task_context: Context for automatic complexity calculation
        system_instruction: System instruction to use with the model
        tools: List of tool schemas for function calling
    """
    if model_type is None:
        # Use intelligent model selection
        model_type = ai_config.get_optimal_model(
            task_complexity, prefer_speed, task_context
        )

    return ai_config.get_model_with_schema(
        model_type=model_type,
        system_instruction=system_instruction,
        response_schema_type=response_schema_type,
        tools=tools,
    )


async def generate_compliance_content(
    prompt: str, model_type: Optional[ModelType] = None
) -> str:
    """Generate compliance-focused content using optimized settings"""
    model = get_ai_model(model_type)

    # Temporarily update config for compliance generation
    original_config = ai_config.generation_config.copy()
    ai_config.update_generation_config(**ai_config.get_compliance_optimized_config())

    try:
        response = model.generate_content(prompt)
        return response.text
    finally:
        # Restore original configuration
        ai_config.generation_config = original_config


def generate_creative_content(
    prompt: str, model_type: Optional[ModelType] = None
) -> str:
    """Generate creative content using higher temperature settings"""
    model = get_ai_model(model_type)

    # Temporarily update config for creative generation
    original_config = ai_config.generation_config.copy()
    ai_config.update_generation_config(**ai_config.get_creative_config())

    try:
        response = model.generate_content(prompt)
        return response.text
    finally:
        # Restore original configuration
        ai_config.generation_config = original_config
