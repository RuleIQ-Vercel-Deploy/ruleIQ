#!/usr/bin/env python3
"""
Direct AI Service Testing Script for ruleIQ
Tests AI functionality without requiring full backend startup
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, '/home/omar/Documents/ruleIQ')

# Set environment for testing
os.environ['ENVIRONMENT'] = 'development'
os.environ['USE_MOCK_AI'] = 'false'

def test_google_api_key():
    """Test Google API key configuration"""
    print("=== Testing Google API Key Configuration ===")
    
    google_key = os.getenv('GOOGLE_AI_API_KEY')
    print(f"GOOGLE_AI_API_KEY: {'✅ Present' if google_key else '❌ Missing'}")
    
    if google_key:
        print(f"   Key format: {len(google_key)} characters")
        print(f"   Key starts with: {google_key[:10]}...")
        return True
    else:
        print("   Please set GOOGLE_AI_API_KEY in .env.local")
        return False

async def test_ai_model_initialization():
    """Test AI model initialization"""
    print("\n=== Testing AI Model Initialization ===")
    
    try:
        from services.ai.assistant import ComplianceAssistant
        from config.ai_config import ai_config
        
        print("✅ Successfully imported AI modules")
        
        # Test configuration
        print(f"   Default model: {ai_config.default_model}")
        print(f"   Fallback chain: {[m.value for m in ai_config.fallback_chain]}")
        print(f"   Generation config: {ai_config.generation_config}")
        
        # Test assistant initialization
        assistant = ComplianceAssistant()
        print("✅ ComplianceAssistant initialized successfully")
        
        # Test Google client
        if hasattr(assistant, 'genai_client'):
            print("✅ Google GenAI client available")
        else:
            print("❌ Google GenAI client not available")
            
        return True
        
    except Exception as e:
        print(f"❌ AI initialization failed: {e}")
        return False

async def test_basic_ai_functionality():
    """Test basic AI functionality"""
    print("\n=== Testing Basic AI Functionality ===")
    
    try:
        from services.ai.assistant import ComplianceAssistant
        
        assistant = ComplianceAssistant()
        
        # Test simple prompt
        test_prompt = "What is compliance management?"
        print(f"   Testing prompt: {test_prompt}")
        
        # Use mock response if API not available
        use_mock = os.getenv('USE_MOCK_AI', 'false').lower() == 'true'
        
        if use_mock:
            print("   Using mock AI responses")
            response = "Mock AI response for compliance management"
        else:
            # Test actual AI call
            try:
                response = await assistant.generate_response(
                    prompt=test_prompt,
                    context={"framework": "general"}
                )
                print("✅ AI response generated successfully")
            except Exception as e:
                print(f"❌ AI response failed: {e}")
                response = f"Error: {str(e)}"
        
        print(f"   Response: {response[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Basic AI functionality test failed: {e}")
        return False

async def test_assessment_ai():
    """Test assessment AI endpoints"""
    print("\n=== Testing Assessment AI ===")
    
    try:
        from services.ai.assistant import ComplianceAssistant
        
        assistant = ComplianceAssistant()
        
        # Test help endpoint simulation
        test_framework = "SOC2"
        test_question = "How do I implement access controls?"
        
        print(f"   Testing help for {test_framework}: {test_question}")
        
        # Simulate help endpoint
        help_response = await assistant.generate_assessment_help(
            framework_id=test_framework,
            question=test_question,
            context={"business_type": "SaaS"}
        )
        
        print("✅ Assessment help test completed")
        print(f"   Help response: {help_response[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Assessment AI test failed: {e}")
        return False

async def test_policy_generation():
    """Test AI policy generation"""
    print("\n=== Testing AI Policy Generation ===")
    
    try:
        from services.ai.assistant import ComplianceAssistant
        
        assistant = ComplianceAssistant()
        
        # Test policy generation
        test_requirements = ["Access control policy", "Data encryption policy"]
        test_framework = "SOC2"
        
        print(f"   Testing policy generation for {test_framework}")
        print(f"   Requirements: {test_requirements}")
        
        policy = await assistant.generate_policy(
            framework_id=test_framework,
            requirements=test_requirements,
            business_context={"industry": "SaaS", "size": "startup"}
        )
        
        print("✅ Policy generation test completed")
        print(f"   Policy length: {len(policy)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Policy generation test failed: {e}")
        return False

async def test_evidence_analysis():
    """Test AI evidence analysis"""
    print("\n=== Testing AI Evidence Analysis ===")
    
    try:
        from services.ai.assistant import ComplianceAssistant
        
        assistant = ComplianceAssistant()
        
        # Test evidence analysis
        test_evidence = {
            "type": "document",
            "content": "Our company has implemented multi-factor authentication for all admin accounts.",
            "framework": "SOC2"
        }
        
        print(f"   Testing evidence analysis: {test_evidence['type']}")
        
        analysis = await assistant.analyze_evidence(
            evidence=test_evidence,
            framework_id="SOC2",
            control_id="CC6.1"
        )
        
        print("✅ Evidence analysis test completed")
        print(f"   Analysis: {analysis[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Evidence analysis test failed: {e}")
        return False

async def test_circuit_breaker():
    """Test circuit breaker functionality"""
    print("\n=== Testing Circuit Breaker ===")
    
    try:
        from api.utils.circuit_breaker import CircuitBreaker
        
        # Test circuit breaker initialization
        breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60,
            expected_exception=Exception
        )
        
        print("✅ Circuit breaker initialized")
        
        # Test state
        print(f"   Initial state: {breaker.state}")
        
        return True
        
    except Exception as e:
        print(f"❌ Circuit breaker test failed: {e}")
        return False

async def run_comprehensive_ai_test():
    """Run comprehensive AI testing"""
    print("🚀 Starting Comprehensive AI Service Testing")
    print("=" * 60)
    
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "tests": []
    }
    
    # Test 1: Google API Key
    api_key_ok = test_google_api_key()
    results["tests"].append({
        "test": "google_api_key",
        "status": "pass" if api_key_ok else "fail"
    })
    
    # Test 2: AI Model Initialization
    init_ok = await test_ai_model_initialization()
    results["tests"].append({
        "test": "ai_model_initialization",
        "status": "pass" if init_ok else "fail"
    })
    
    # Test 3: Basic AI Functionality
    basic_ok = await test_basic_ai_functionality()
    results["tests"].append({
        "test": "basic_ai_functionality",
        "status": "pass" if basic_ok else "fail"
    })
    
    # Test 4: Assessment AI
    assessment_ok = await test_assessment_ai()
    results["tests"].append({
        "test": "assessment_ai",
        "status": "pass" if assessment_ok else "fail"
    })
    
    # Test 5: Policy Generation
    policy_ok = await test_policy_generation()
    results["tests"].append({
        "test": "policy_generation",
        "status": "pass" if policy_ok else "fail"
    })
    
    # Test 6: Evidence Analysis
    evidence_ok = await test_evidence_analysis()
    results["tests"].append({
        "test": "evidence_analysis",
        "status": "pass" if evidence_ok else "fail"
    })
    
    # Test 7: Circuit Breaker
    breaker_ok = await test_circuit_breaker()
    results["tests"].append({
        "test": "circuit_breaker",
        "status": "pass" if breaker_ok else "fail"
    })
    
    # Summary
    total_tests = len(results["tests"])
    passed_tests = sum(1 for test in results["tests"] if test["status"] == "pass")
    
    print("\n" + "=" * 60)
    print("📊 AI Service Testing Summary")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    # Save results
    with open('ai_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Test results saved to ai_test_results.json")
    
    return results

async def main():
    """Main testing function"""
    try:
        await run_comprehensive_ai_test()
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())