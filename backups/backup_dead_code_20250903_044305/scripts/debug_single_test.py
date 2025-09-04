"""Debug a single failing test to see specific errors."""
import logging
logger = logging.getLogger(__name__)
import subprocess
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_single_test(test_file, test_name=None):
    """Run a single test file or specific test."""
    logger.info('Running test: %s' % test_file)
    if test_name:
        logger.info('Specific test: %s' % test_name)
    cmd = [sys.executable, '-m', 'pytest', test_file, '-xvs', '--tb=long']
    if test_name:
        cmd.extend(['-k', test_name])
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['USE_MOCK_AI'] = 'true'
    result = subprocess.run(cmd, env=env)
    return result.returncode == 0


if __name__ == '__main__':
    test_file = 'tests/unit/services/test_cache_strategy_optimization.py'
    success = run_single_test(test_file,
        'test_performance_based_ttl_optimization')
    sys.exit(0 if success else 1)
