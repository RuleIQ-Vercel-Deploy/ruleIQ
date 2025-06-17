"""
AI Configuration and Model Setup for ComplianceGPT

This module handles configuration and initialization of AI models,
primarily Google Generative AI for compliance content generation.
"""

## GOOGLE API

import os
from enum import Enum
from typing import Any, Dict, Optional

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class ModelType(Enum):
    """Available AI model types"""
    GEMINI_FLASH = "gemini-2.5-flash-preview-05-20"


class AIConfig:
    """AI Configuration Manager"""

    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.default_model = ModelType.GEMINI_FLASH.value
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]

        self._initialize_google_ai()

    def _initialize_google_ai(self):
        """Initialize Google Generative AI with API key"""
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        genai.configure(api_key=self.google_api_key)

    def get_model(self, model_type: Optional[ModelType] = None) -> genai.GenerativeModel:
        """Get configured AI model instance"""
        model_name = model_type.value if model_type else self.default_model

        return genai.GenerativeModel(
            model_name=model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )

    def update_generation_config(self, **kwargs):
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


# Global AI configuration instance
ai_config = AIConfig()


def get_ai_model(model_type: Optional[ModelType] = None) -> genai.GenerativeModel:
    """Convenience function to get AI model instance"""
    return ai_config.get_model(model_type)


def generate_compliance_content(prompt: str, model_type: Optional[ModelType] = None) -> str:
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


def generate_creative_content(prompt: str, model_type: Optional[ModelType] = None) -> str:
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
