"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Test runner for the 32 failing tests.
Run this after applying fixes to verify they work.
"""

from typing import Any
import subprocess
import sys
test_files = ['tests/unit/services/test_cache_strategy_optimization.py',
    'tests/unit/services/test_cached_content.py',
    'tests/ai/test_compliance_accuracy.py',
    'tests/performance/test_ai_optimization_performance.py',
    'tests/performance/test_database_performance.py']


def run_tests() ->Any:
    """Run all failing tests and report results."""
    results = {}
    for test_file in test_files:
        logger.info('\nRunning %s...' % test_file)
        cmd = [sys.executable, '-m', 'pytest', test_file, '-v', '--tb=short']
        result = subprocess.run(cmd, capture_output=True, text=True)
        results[test_file] = {'returncode': result.returncode, 'passed':
            result.returncode == 0, 'output': result.stdout + result.stderr}
        if result.returncode == 0:
            logger.info('  ✓ PASSED')
        else:
            logger.info('  ✗ FAILED')
            error_lines = result.stderr.split('\n')[:5]
            for line in error_lines:
                if line.strip():
                    logger.info('    %s' % line)
    logger.info('\n' + '=' * 60)
    logger.info('TEST SUMMARY')
    logger.info('=' * 60)
    passed = sum(1 for r in results.values() if r['passed'])
    failed = len(results) - passed
    logger.info('Total: %s' % len(results))
    logger.info('Passed: %s' % passed)
    logger.info('Failed: %s' % failed)
    if failed > 0:
        logger.info('\nFailed tests:')
        for test, result in results.items():
            if not result['passed']:
                logger.info('  - %s' % test)
    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
