#!/usr/bin/env python
"""
Comprehensive test runner for notification migration tests
Runs all test methods directly to bypass pytest collection issues
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock
import json

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from langgraph_agent.nodes.notification_nodes import EnhancedNotificationNode
from tests.test_notification_migration_tdd import (
    TestNotificationStateTransitions,
    TestEmailSMSDeliveryMocking,
    TestRetryLogicAndErrorHandling,
    TestBatchNotificationProcessing,
    TestNotificationChannelIntegration,
    TestNotificationPrioritization,
    TestObservabilityAndMetrics,
    TestStatePersistenceAndRecovery,
    TestCostGovernance,
    TestComplianceAndSecurity
)

class TestRunner:
    """Run all notification migration tests"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def create_base_state(self):
        """Create base test state"""
        return {
            "task_id": "test-123",
            "task_name": "test_notification",
            "task_type": "notification",
            "task_status": "pending",
            "task_params": {
                "recipients": ["test@example.com"],
                "message": "Test message",
                "channel": "email"
            },
            "retry_count": 0,
            "max_retries": 3,
            "task_result": None,
            "metadata": {},
            "checkpoints": []
        }
    
    async def run_test_class(self, test_class, class_name):
        """Run all test methods in a test class"""
        print(f"\n{'='*60}")
        print(f"Running {class_name}")
        print(f"{'='*60}")
        
        test_instance = test_class()
        node = EnhancedNotificationNode()
        base_state = self.create_base_state()
        
        # Get all test methods
        test_methods = [m for m in dir(test_instance) if m.startswith('test_')]
        
        for method_name in test_methods:
            method = getattr(test_instance, method_name)
            print(f"\n  Testing: {method_name.replace('test_', '').replace('_', ' ')}")
            
            try:
                # Check method signature to determine parameters
                import inspect
                sig = inspect.signature(method)
                params = list(sig.parameters.keys())
                
                # Call with appropriate parameters
                if 'notification_node' in params and 'base_state' in params:
                    await method(node, base_state.copy())
                elif 'notification_node' in params:
                    await method(node)
                else:
                    await method()
                    
                print(f"    ✅ PASSED")
                self.passed += 1
            except Exception as e:
                print(f"    ❌ FAILED: {str(e)}")
                self.failed += 1
                self.errors.append({
                    'class': class_name,
                    'method': method_name,
                    'error': str(e)
                })
    
    async def run_all_tests(self):
        """Run all test classes"""
        print("="*70)
        print("NOTIFICATION MIGRATION TEST SUITE")
        print("="*70)
        
        test_classes = [
            (TestNotificationStateTransitions, "State Transitions"),
            (TestEmailSMSDeliveryMocking, "Email/SMS Delivery"),
            (TestRetryLogicAndErrorHandling, "Retry Logic"),
            (TestBatchNotificationProcessing, "Batch Processing"),
            (TestNotificationChannelIntegration, "Channel Integration"),
            (TestNotificationPrioritization, "Prioritization"),
            (TestObservabilityAndMetrics, "Observability"),
            (TestStatePersistenceAndRecovery, "State Persistence"),
            (TestCostGovernance, "Cost Governance"),
            (TestComplianceAndSecurity, "Compliance & Security")
        ]
        
        for test_class, name in test_classes:
            await self.run_test_class(test_class, name)
        
        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Total: {self.passed + self.failed}")
        print(f"🎯 Success Rate: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        
        if self.errors:
            print("\n" + "="*70)
            print("FAILED TEST DETAILS")
            print("="*70)
            for error in self.errors:
                print(f"\n{error['class']}.{error['method']}")
                print(f"  Error: {error['error']}")
        
        return self.failed == 0

async def main():
    """Main entry point"""
    runner = TestRunner()
    success = await runner.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️ SOME TESTS FAILED - Review implementation")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
