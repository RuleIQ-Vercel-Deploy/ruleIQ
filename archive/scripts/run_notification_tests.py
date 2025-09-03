#!/usr/bin/env python
"""
Direct test runner for notification migration TDD tests
"""
import logging
logger = logging.getLogger(__name__)

import sys
import unittest
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import test modules
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
    TestComplianceAndSecurity,
)

def run_tests():
    """Run all notification migration TDD tests"""

    # Create test suite
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestNotificationStateTransitions,
        TestEmailSMSDeliveryMocking,
        TestRetryLogicAndErrorHandling,
        TestBatchNotificationProcessing,
        TestNotificationChannelIntegration,
        TestNotificationPrioritization,
        TestObservabilityAndMetrics,
        TestStatePersistenceAndRecovery,
        TestCostGovernance,
        TestComplianceAndSecurity,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    logger.info(f"Skipped: {len(result.skipped)}")

    # Print coverage info
    if result.testsRun > 0:
        success_rate = (
            (result.testsRun - len(result.failures) - len(result.errors))
            / result.testsRun
        ) * 100
        logger.info(f"Success rate: {success_rate:.1f}%")

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
