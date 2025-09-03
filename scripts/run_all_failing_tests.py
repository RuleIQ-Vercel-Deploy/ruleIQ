"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Comprehensive test runner for all 32 failing tests.
Runs tests with proper error reporting and summary.
"""

from typing import Any, Dict, List, Optional
import subprocess
import sys
import os
from pathlib import Path
TEST_CATEGORIES = {'Cache Strategy & Content': [
    'tests/unit/services/test_cache_strategy_optimization.py',
    'tests/unit/services/test_cached_content.py'], 'AI Compliance Accuracy':
    ['tests/ai/test_compliance_accuracy.py'], 'AI Optimization Performance':
    ['tests/performance/test_ai_optimization_performance.py'],
    'Database Performance': ['tests/performance/test_database_performance.py']}

def run_test_category(category_name: Any, test_files: Any) ->Any:
    """Run tests in a category."""
    logger.info('\n%s' % ('=' * 60))
    logger.info('Running %s Tests' % category_name)
    logger.info('=' * 60)
    results = []
    for test_file in test_files:
        if not Path(test_file).exists():
            logger.info('\n❌ %s - FILE NOT FOUND' % test_file)
            results.append({'file': test_file, 'passed': False, 'error':
                'File not found'})
            continue
        logger.info('\n▶ Running %s...' % test_file)
        cmd = [sys.executable, '-m', 'pytest', test_file, '-v',
            '--tb=short', '--no-header', '--no-summary', '-q']
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout + result.stderr
        passed = result.returncode == 0
        if passed:
            passed_count = output.count(' PASSED')
            logger.info('  ✅ All tests passed (%s tests)' % passed_count)
        else:
            failed_count = output.count(' FAILED')
            error_count = output.count(' ERROR')
            logger.info('  ❌ Tests failed (Failed: %s, Errors: %s)' % (
                failed_count, error_count))
            error_lines = [line for line in output.split('\n') if 'FAILED' in
                line or 'ERROR' in line][:3]
            for line in error_lines:
                logger.info('     %s' % line.strip())
        results.append({'file': test_file, 'passed': passed, 'output': output})
    return results

def main() ->Any:
    """Run all test categories and provide summary."""
    logger.info('🧪 Running All Failing Tests')
    logger.info('=' * 60)
    all_results = {}
    os.environ['ENV'] = 'testing'
    os.environ['USE_MOCK_AI'] = 'true'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    for category, test_files in TEST_CATEGORIES.items():
        results = run_test_category(category, test_files)
        all_results[category] = results
    logger.info('\n%s' % ('=' * 60))
    logger.info('📊 TEST SUMMARY')
    logger.info('=' * 60)
    total_files = 0
    passed_files = 0
    for category, results in all_results.items():
        category_passed = sum(1 for r in results if r['passed'])
        category_total = len(results)
        total_files += category_total
        passed_files += category_passed
        status = '✅' if category_passed == category_total else '❌'
        logger.info('%s %s: %s/%s files passed' % (status, category,
            category_passed, category_total))
    logger.info('\n📈 Overall: %s/%s test files passed' % (passed_files,
        total_files))
    if passed_files < total_files:
        logger.info('\n❌ Failed test files:')
        for category, results in all_results.items():
            for result in results:
                if not result['passed']:
                    logger.info('  - %s' % result['file'])
    return passed_files == total_files

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
