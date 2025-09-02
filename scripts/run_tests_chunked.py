"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Chunked Test Execution Script for NexCompli

This script provides optimized test execution strategies for different scenarios:
- Fast: Unit tests only with high parallelism
- Integration: Integration tests with medium parallelism
- Full: All tests in optimized chunks
- CI: Optimized for CI/CD environments
- Performance: Performance tests with minimal parallelism

Usage:
    python scripts/run_tests_chunked.py --mode fast
    python scripts/run_tests_chunked.py --mode integration
    python scripts/run_tests_chunked.py --mode full
    python scripts/run_tests_chunked.py --mode ci
    python scripts/run_tests_chunked.py --mode performance
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple
import psutil
TEST_CONFIGS = {'fast': {'description': 'Fast unit tests only', 'chunks': [
    {'name': 'Unit Tests', 'command': ['python', '-m', 'pytest',
    'tests/unit/', '-m', 'unit', '--tb=short', '--maxfail=10',
    '--disable-warnings'], 'timeout': 300, 'parallel': False}]},
    'integration': {'description': 'Integration tests with database',
    'chunks': [{'name': 'API Integration Tests', 'command': ['python', '-m',
    'pytest', 'tests/integration/api/', '-n', '2', '--dist=worksteal', '-m',
    'integration', '--tb=short', '--maxfail=5'], 'timeout': 600, 'parallel':
    True}, {'name': 'Database Integration Tests', 'command': ['python',
    '-m', 'pytest', 'tests/integration/database/', '-n', '1', '-m',
    'database', '--tb=short', '--maxfail=5'], 'timeout': 400, 'parallel': 
    False}, {'name': 'Service Integration Tests', 'command': ['python',
    '-m', 'pytest', 'tests/integration/test_evidence_flow.py', '-n', '2',
    '--dist=worksteal', '-m', 'integration', '--tb=short', '--maxfail=5'],
    'timeout': 500, 'parallel': True}]}, 'performance': {'description':
    'Performance and load tests', 'chunks': [{'name':
    'API Performance Tests', 'command': ['python', '-m', 'pytest',
    'tests/performance/test_api_performance.py', '-n', '1', '-m',
    'performance', '--tb=short', '--maxfail=3', '--benchmark-only',
    '--benchmark-sort=mean'], 'timeout': 1800, 'parallel': False}, {'name':
    'Database Performance Tests', 'command': ['python', '-m', 'pytest',
    'tests/performance/test_database_performance.py', '-n', '1', '-m',
    'performance', '--tb=short', '--maxfail=3'], 'timeout': 1200,
    'parallel': False}]}, 'e2e': {'description':
    'End-to-end workflow tests', 'chunks': [{'name': 'User Onboarding E2E',
    'command': ['python', '-m', 'pytest',
    'tests/e2e/test_user_onboarding_flow.py', '-n', '1', '-m', 'e2e',
    '--tb=short', '--maxfail=3'], 'timeout': 900, 'parallel': False}]},
    'security': {'description': 'Security and authentication tests',
    'chunks': [{'name': 'Authentication Tests', 'command': ['python', '-m',
    'pytest', 'tests/security/test_authentication.py', '-n', '2',
    '--dist=worksteal', '-m', 'security', '--tb=short', '--maxfail=5'],
    'timeout': 400, 'parallel': True}]}, 'ai': {'description':
    'AI and compliance accuracy tests', 'chunks': [{'name':
    'AI Compliance Tests', 'command': ['python', '-m', 'pytest',
    'tests/ai/test_compliance_accuracy.py', '-n', '2', '--dist=worksteal',
    '-m', 'ai', '--tb=short', '--maxfail=5'], 'timeout': 600, 'parallel': 
    True}]}}
TEST_CONFIGS['full'] = {'description':
    'Complete test suite in optimized chunks', 'chunks': TEST_CONFIGS[
    'fast']['chunks'] + TEST_CONFIGS['integration']['chunks'] +
    TEST_CONFIGS['security']['chunks'] + TEST_CONFIGS['ai']['chunks'] +
    TEST_CONFIGS['e2e']['chunks'] + TEST_CONFIGS['performance']['chunks']}
TEST_CONFIGS['ci'] = {'description': 'CI/CD optimized test execution',
    'chunks': [{'name': 'Fast Tests (Unit + Integration)', 'command': [
    'python', '-m', 'pytest', 'tests/unit/', 'tests/integration/', '-n',
    '4', '--dist=worksteal', '-m', 'not slow and not performance',
    '--tb=short', '--maxfail=10', '--disable-warnings'], 'timeout': 600,
    'parallel': True}, {'name': 'Critical E2E Tests', 'command': ['python',
    '-m', 'pytest', 'tests/e2e/', '-n', '1', '-m', 'smoke or critical',
    '--tb=short', '--maxfail=3'], 'timeout': 400, 'parallel': False}]}


def get_system_info() ->Dict:
    """Get system information for optimal test configuration."""
    return {'cpu_count': psutil.cpu_count(), 'memory_gb': psutil.
        virtual_memory().total / 1024 ** 3, 'available_memory_gb': psutil.
        virtual_memory().available / 1024 ** 3}


def optimize_parallelism(base_workers: int, system_info: Dict) ->int:
    """Optimize number of parallel workers based on system resources."""
    cpu_workers = min(base_workers, system_info['cpu_count'])
    memory_workers = max(1, int(system_info['available_memory_gb'] / 2))
    return min(cpu_workers, memory_workers)


async def run_test_chunk(chunk: Dict, system_info: Dict) ->Tuple[str, bool,
    str, float]:
    """Run a single test chunk and return results."""
    start_time = time.time()
    chunk_name = chunk['name']
    command = chunk['command'].copy()
    if '-n' in command:
        n_index = command.index('-n')
        if n_index + 1 < len(command):
            if command[n_index + 1] == 'auto':
                command[n_index + 1] = str(optimize_parallelism(psutil.
                    cpu_count(), system_info))
            elif command[n_index + 1].isdigit():
                original_workers = int(command[n_index + 1])
                command[n_index + 1] = str(optimize_parallelism(
                    original_workers, system_info))
    logger.info('🚀 Starting: %s' % chunk_name)
    logger.info('   Command: %s' % ' '.join(command))
    try:
        process = await asyncio.create_subprocess_exec(*command, stdout=
            asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT, cwd=
            Path(__file__).parent.parent)
        stdout, _ = await asyncio.wait_for(process.communicate(), timeout=
            chunk.get('timeout', 600))
        duration = time.time() - start_time
        success = process.returncode == 0
        output = stdout.decode() if stdout else ''
        status = '✅ PASSED' if success else '❌ FAILED'
        logger.info('%s: %s (%ss)' % (status, chunk_name, duration))
        return chunk_name, success, output, duration
    except asyncio.TimeoutError:
        duration = time.time() - start_time
        logger.info('⏰ TIMEOUT: %s (%ss)' % (chunk_name, duration))
        return (chunk_name, False,
            f'Test chunk timed out after {duration:.1f}s', duration)
    except Exception as e:
        duration = time.time() - start_time
        logger.info('💥 ERROR: %s - %s' % (chunk_name, e))
        return chunk_name, False, f'Error: {e!s}', duration


async def run_chunks_parallel(chunks: List[Dict], max_concurrent: int=3
    ) ->List[Tuple]:
    """Run test chunks with controlled parallelism."""
    system_info = get_system_info()
    print(
        f"🖥️  System: {system_info['cpu_count']} CPUs, {system_info['available_memory_gb']:.1f}GB available",
        )
    parallel_chunks = [c for c in chunks if c.get('parallel', True)]
    sequential_chunks = [c for c in chunks if not c.get('parallel', True)]
    results = []
    if parallel_chunks:
        print(
            f'🔄 Running {len(parallel_chunks)} chunks in parallel (max {max_concurrent} concurrent)',
            )
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run_with_semaphore(chunk):
            async with semaphore:
                return await run_test_chunk(chunk, system_info)
        parallel_results = await asyncio.gather(*[run_with_semaphore(chunk) for
            chunk in parallel_chunks], return_exceptions=True)
        results.extend(parallel_results)
    if sequential_chunks:
        logger.info('⏭️  Running %s chunks sequentially' % len(
            sequential_chunks))
        for chunk in sequential_chunks:
            result = await run_test_chunk(chunk, system_info)
            results.append(result)
    return results


def print_summary(results: List[Tuple], total_time: float) ->None:
    """Print test execution summary."""
    logger.info('\n' + '=' * 80)
    logger.info('📊 TEST EXECUTION SUMMARY')
    logger.info('=' * 80)
    passed = sum(1 for _, success, _, _ in results if success)
    failed = len(results) - passed
    total_test_time = sum(duration for _, _, _, duration in results)
    logger.info('Total Chunks: %s' % len(results))
    logger.info('Passed: %s ✅' % passed)
    logger.info('Failed: %s ❌' % failed)
    logger.info('Success Rate: %s%' % (passed / len(results) * 100))
    logger.info('Total Time: %ss' % total_time)
    logger.info('Test Time: %ss' % total_test_time)
    logger.info('Efficiency: %sx' % (total_test_time / total_time))
    if failed > 0:
        logger.info('\n❌ FAILED CHUNKS:')
        for name, success, output, duration in results:
            if not success:
                logger.info('  • %s (%ss)' % (name, duration))
                if output:
                    lines = output.strip().split('\n')
                    relevant_lines = [l for l in lines[-10:] if 'FAILED' in
                        l or 'ERROR' in l or 'assert' in l]
                    if relevant_lines:
                        logger.info('    %s...' % relevant_lines[-1][:100])
    logger.info('=' * 80)


async def main() ->None:
    """Main execution function."""
    parser = argparse.ArgumentParser(description=
        'Run NexCompli tests in optimized chunks')
    parser.add_argument('--mode', choices=list(TEST_CONFIGS.keys()),
        default='fast', help='Test execution mode')
    parser.add_argument('--max-concurrent', type=int, default=3, help=
        'Maximum concurrent test chunks')
    parser.add_argument('--list-modes', action='store_true', help=
        'List available test modes')
    args = parser.parse_args()
    if args.list_modes:
        logger.info('Available test modes:')
        for mode, config in TEST_CONFIGS.items():
            logger.info('  %s - %s' % (mode, config['description']))
            logger.info('               %s chunks' % len(config['chunks']))
        return
    config = TEST_CONFIGS[args.mode]
    logger.info('🎯 Mode: %s - %s' % (args.mode, config['description']))
    logger.info('📦 Chunks: %s' % len(config['chunks']))
    start_time = time.time()
    results = await run_chunks_parallel(config['chunks'], args.max_concurrent)
    total_time = time.time() - start_time
    print_summary(results, total_time)
    failed_count = sum(1 for _, success, _, _ in results if not success)
    sys.exit(failed_count)


if __name__ == '__main__':
    asyncio.run(main())
