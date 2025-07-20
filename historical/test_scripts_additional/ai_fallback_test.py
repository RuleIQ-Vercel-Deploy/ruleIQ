import unittest
from unittest.mock import patch, MagicMock
import os

# Set mock environment variable before imports
os.environ['USE_MOCK_AI'] = 'true'

from services.ai.assistant import ComplianceAssistant
from config.ai_config import ModelType

# Attempt to import for spec, but allow it to fail if not installed
try:
    import google.generativeai as genai
except ImportError:
    genai = MagicMock()


class TestAIFallback(unittest.TestCase):

    @patch('services.ai.assistant.get_ai_model')
    @patch('services.ai.assistant.AICircuitBreaker')
    @patch('services.ai.assistant.get_instruction_manager')
    def test_model_fallback_logic(self, mock_get_instruction_manager, mock_circuit_breaker, mock_get_ai_model):
        """
        Test the AI model fallback mechanism by simulating model failures.
        """
        # Arrange
        # 1. Mock the instruction manager to return a primary model
        primary_model = MagicMock(spec=genai.GenerativeModel)
        primary_model.model_name = ModelType.GEMINI_25_PRO.value
        mock_get_instruction_manager.return_value.get_model_with_instruction.return_value = (primary_model, "test_instruction")

        # 2. Mock the circuit breaker to make the primary model unavailable
        mock_circuit_breaker.return_value.is_model_available.side_effect = [
            False,  # Primary model (GEMINI_25_PRO) is unavailable
            True    # Fallback model is available
        ]

        # 3. Mock get_ai_model to return the correctly configured fallback model
        fallback_model = MagicMock(spec=genai.GenerativeModel)
        fallback_model.model_name = ModelType.GEMINI_25_FLASH.value
        mock_get_ai_model.return_value = fallback_model

        # Act
        assistant = ComplianceAssistant(db=MagicMock())
        # This call should now trigger the full fallback logic
        model, instruction_id = assistant._get_task_appropriate_model(task_type="analysis")
        
        # Assert
        # Check that the returned model is the fallback model
        self.assertEqual(model.model_name, ModelType.GEMINI_25_FLASH.value)
        self.assertEqual(instruction_id, "fallback_default")
        
        # Verify that the circuit breaker was checked for both models
        self.assertEqual(mock_circuit_breaker.return_value.is_model_available.call_count, 2)
        
        # Verify that get_ai_model was called once for the fallback
        mock_get_ai_model.assert_called_once()

if __name__ == '__main__':
    unittest.main()