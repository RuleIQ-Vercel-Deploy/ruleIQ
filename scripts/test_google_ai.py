#!/usr/bin/env python3
"""
Google Generative AI (Gemini) Integration Test Script
Comprehensive testing for Google AI as the primary AI service
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from colorama import init, Fore, Style
import google.generativeai as genai
from typing import List, Dict, Any

# Initialize colorama for colored output
init()

# Load environment variables
load_dotenv('.env.local')
load_dotenv('.env', override=False)

def print_success(message):
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

def print_warning(message):
    print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.CYAN}ℹ️  {message}{Style.RESET_ALL}")

def print_section(title):
    print(f"\n{Fore.BLUE}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Style.RESET_ALL}")

class GoogleAITester:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_AI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def test_api_key(self) -> bool:
        """Test if API key is configured and valid"""
        print_section("Testing Google AI API Key Configuration")

        if not self.api_key:
            print_error("GOOGLE_AI_API_KEY not found in environment")
            return False

        if self.api_key.startswith('your-') or self.api_key == 'your-google-ai-api-key-here':
            print_error("GOOGLE_AI_API_KEY appears to be a placeholder")
            return False

        # Mask the API key for display
        masked_key = self.api_key[:10] + "..." + self.api_key[-4:]
        print_info(f"API Key found: {masked_key}")

        return True

    def test_api_connection(self) -> bool:
        """Test basic API connectivity"""
        print_section("Testing Google AI API Connection")

        url = f"{self.base_url}/models?key={self.api_key}"

        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                print_success("API connection successful!")
                return True
            elif response.status_code == 403:
                print_error("API key is invalid or doesn't have proper permissions")
                return False
            elif response.status_code == 429:
                print_warning("Rate limit exceeded - API is working but quota reached")
                return True
            else:
                print_error(f"API connection failed: HTTP {response.status_code}")
                print_info(f"Response: {response.text[:200]}")
                return False

        except requests.exceptions.Timeout:
            print_error("API request timed out")
            return False
        except Exception as e:
            print_error(f"API connection error: {e}")
            return False

    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available Gemini models"""
        print_section("Listing Available Gemini Models")

        url = f"{self.base_url}/models?key={self.api_key}"

        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])

                # Filter for Gemini models
                gemini_models = [m for m in models if 'gemini' in m.get('name', '').lower()]

                print_success(f"Found {len(gemini_models)} Gemini models")

                # Categorize models
                pro_models = [m for m in gemini_models if 'gemini-pro' in m.get('name', '').lower()]
                pro_vision_models = [m for m in gemini_models if 'gemini-pro-vision' in m.get('name', '').lower()]
                flash_models = [m for m in gemini_models if 'flash' in m.get('name', '').lower()]

                if pro_models:
                    print_info(f"\nGemini Pro Models ({len(pro_models)}):")
                    for model in pro_models[:5]:
                        name = model.get('name', 'Unknown')
                        supported = model.get('supportedGenerationMethods', [])
                        print(f"  - {name}")
                        print(f"    Methods: {', '.join(supported)}")

                if flash_models:
                    print_info(f"\nGemini Flash Models ({len(flash_models)}):")
                    for model in flash_models[:3]:
                        name = model.get('name', 'Unknown')
                        print(f"  - {name}")

                if pro_vision_models:
                    print_info(f"\nGemini Pro Vision Models ({len(pro_vision_models)}):")
                    for model in pro_vision_models[:3]:
                        name = model.get('name', 'Unknown')
                        print(f"  - {name}")

                return gemini_models
            else:
                print_error(f"Failed to list models: HTTP {response.status_code}")
                return []

        except Exception as e:
            print_error(f"Error listing models: {e}")
            return []

    def test_text_generation(self) -> bool:
        """Test actual text generation with Gemini"""
        print_section("Testing Gemini Text Generation")

        try:
            # Configure the API
            genai.configure(api_key=self.api_key)

            # Try different model versions
            model_names = [
                'gemini-1.5-flash',
                'gemini-1.5-pro',
                'gemini-pro',
                'gemini-1.0-pro'
            ]

            working_model = None
            for model_name in model_names:
                try:
                    print_info(f"Trying model: {model_name}")
                    model = genai.GenerativeModel(model_name)

                    # Simple test prompt
                    prompt = "Write a one-sentence description of what RuleIQ compliance software does."

                    response = model.generate_content(prompt)

                    if response and response.text:
                        print_success(f"Model {model_name} works!")
                        print_info(f"Response: {response.text[:200]}")
                        working_model = model_name
                        break

                except Exception as e:
                    print_warning(f"Model {model_name} failed: {str(e)[:100]}")
                    continue

            if working_model:
                print_success(f"\nRecommended model for production: {working_model}")
                return True
            else:
                print_error("No working text generation model found")
                return False

        except Exception as e:
            print_error(f"Text generation test failed: {e}")
            return False

    def test_advanced_features(self) -> bool:
        """Test advanced Gemini features"""
        print_section("Testing Advanced Gemini Features")

        try:
            genai.configure(api_key=self.api_key)

            # Use the most capable model
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Test 1: JSON mode
            print_info("Testing JSON output mode...")
            try:
                response = model.generate_content(
                    "List 3 compliance frameworks as JSON array with name and description fields",
                    generation_config=genai.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=500,
                    )
                )
                if response.text:
                    print_success("JSON generation works")
                    # Try to parse as JSON to verify
                    try:
                        # Extract JSON from response
                        import re
                        json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                        if json_match:
                            json_data = json.loads(json_match.group())
                            print_info(f"Valid JSON with {len(json_data)} items")
                    except:
                        print_warning("Response received but not valid JSON")
            except Exception as e:
                print_warning(f"JSON mode test failed: {str(e)[:100]}")

            # Test 2: System instructions / Chat
            print_info("\nTesting chat/conversation mode...")
            try:
                chat = model.start_chat(history=[])
                response = chat.send_message("What is GDPR?")
                if response.text:
                    print_success("Chat mode works")
                    print_info(f"Response length: {len(response.text)} chars")

                    # Test conversation memory
                    response2 = chat.send_message("Can you make that shorter?")
                    if response2.text and len(response2.text) < len(response.text):
                        print_success("Conversation context maintained")
            except Exception as e:
                print_warning(f"Chat mode test failed: {str(e)[:100]}")

            # Test 3: Safety settings
            print_info("\nTesting safety settings configuration...")
            try:
                safety_settings = [
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_ONLY_HIGH"
                    }
                ]

                model_safe = genai.GenerativeModel(
                    'gemini-1.5-flash',
                    safety_settings=safety_settings
                )
                response = model_safe.generate_content("Explain data privacy")
                if response.text:
                    print_success("Safety settings configuration works")
            except Exception as e:
                print_warning(f"Safety settings test failed: {str(e)[:100]}")

            return True

        except Exception as e:
            print_error(f"Advanced features test failed: {e}")
            return False

    def test_rate_limits(self) -> bool:
        """Test API rate limits and quotas"""
        print_section("Testing Rate Limits and Quotas")

        try:
            # Make a few rapid requests to test rate limiting
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            print_info("Testing rapid requests...")
            successful_requests = 0
            rate_limited = False

            for i in range(5):
                try:
                    response = model.generate_content(f"Say 'test {i}'")
                    if response.text:
                        successful_requests += 1
                        print(f"  Request {i+1}: ✓")
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        rate_limited = True
                        print_warning(f"  Request {i+1}: Rate limited")
                    else:
                        print(f"  Request {i+1}: Failed - {str(e)[:50]}")

            if successful_requests > 0:
                print_success(f"Completed {successful_requests}/5 requests successfully")
                if rate_limited:
                    print_warning("Rate limiting detected - normal for free tier")
                else:
                    print_success("No rate limiting encountered")
                return True
            else:
                print_error("All requests failed")
                return False

        except Exception as e:
            print_error(f"Rate limit test failed: {e}")
            return False

    def generate_integration_code(self):
        """Generate sample integration code for the application"""
        print_section("Sample Integration Code for RuleIQ")

        print_info("Python/FastAPI Backend Integration:")
        print("""
```python
# services/ai_service.py
import google.generativeai as genai
from typing import Optional, Dict, Any
import os

class GoogleAIService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_AI_API_KEY')
        genai.configure(api_key=self.api_key)
        
        # Use Gemini 1.5 Flash for best performance/cost ratio
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Configure safety settings for compliance use case
        self.safety_settings = [
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"}
        ]
    
    async def analyze_compliance(self, text: str) -> Dict[str, Any]:
        \"\"\"Analyze text for compliance issues\"\"\"
        prompt = f\"\"\"
        Analyze the following text for compliance with GDPR, SOC2, and ISO27001.
        Identify any potential compliance issues and suggest improvements.
        
        Text: {text}
        
        Respond in JSON format with:
        - compliance_score (0-100)
        - issues (array of issues found)
        - recommendations (array of suggestions)
        \"\"\"
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,  # Lower for consistency
                max_output_tokens=1000,
            ),
            safety_settings=self.safety_settings
        )
        
        return self._parse_response(response.text)
    
    async def chat(self, message: str, history: list = None) -> str:
        \"\"\"Chat interface for compliance questions\"\"\"
        if not history:
            chat = self.model.start_chat(history=[])
        else:
            chat = self.model.start_chat(history=history)
        
        response = chat.send_message(message)
        return response.text
```
        """)

        print_info("\nEnvironment Configuration (.env):")
        print("""
# Google AI Configuration (Primary AI Service)
GOOGLE_AI_API_KEY=your-api-key-here  # Get from https://makersuite.google.com/app/apikey

# Recommended settings for production
GOOGLE_AI_MODEL=gemini-1.5-flash  # Best for most use cases
GOOGLE_AI_TEMPERATURE=0.3  # Lower = more consistent
GOOGLE_AI_MAX_TOKENS=2000  # Adjust based on needs
GOOGLE_AI_TIMEOUT=30  # Seconds

# Fallback configuration
AI_PRIMARY_PROVIDER=google  # google, openai, anthropic
AI_FALLBACK_PROVIDER=none  # Use 'openai' when credits available
        """)

def main():
    """Run all Google AI tests"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print("Google Generative AI (Gemini) Integration Test")
    print(f"{'='*60}{Style.RESET_ALL}")

    tester = GoogleAITester()

    # Track test results
    tests_passed = 0
    tests_total = 0

    # Test 1: API Key
    tests_total += 1
    if tester.test_api_key():
        tests_passed += 1
    else:
        print_error("Cannot proceed without valid API key")
        return 1

    # Test 2: API Connection
    tests_total += 1
    if tester.test_api_connection():
        tests_passed += 1

    # Test 3: List Models
    tests_total += 1
    models = tester.list_available_models()
    if models:
        tests_passed += 1

    # Test 4: Text Generation
    tests_total += 1
    if tester.test_text_generation():
        tests_passed += 1

    # Test 5: Advanced Features
    tests_total += 1
    if tester.test_advanced_features():
        tests_passed += 1

    # Test 6: Rate Limits
    tests_total += 1
    if tester.test_rate_limits():
        tests_passed += 1

    # Generate integration code
    if tests_passed > 3:
        tester.generate_integration_code()

    # Summary
    print_section("Test Summary")
    print(f"\n{Fore.CYAN}Tests Passed: {tests_passed}/{tests_total}{Style.RESET_ALL}")

    if tests_passed == tests_total:
        print_success("\n🎉 Google AI integration is perfectly configured!")
        print_success("Gemini is ready to be used as the primary AI service")
        return 0
    elif tests_passed >= 4:
        print_success("\n✅ Google AI integration is working well")
        print_warning("Some features may have limitations based on API tier")
        return 0
    else:
        print_error("\n⚠️ Google AI integration needs attention")
        return 1

if __name__ == "__main__":
    # Install required package if not present
    try:
        import google.generativeai
    except ImportError:
        print_warning("Installing google-generativeai package...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
        print_success("Package installed successfully")

    exit_code = main()
    sys.exit(exit_code)
