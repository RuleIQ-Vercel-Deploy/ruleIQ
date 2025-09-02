"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Clean up duplicate and unused API endpoints
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any
PROJECT_ROOT = Path(__file__).parent.parent
ROUTERS_DIR = PROJECT_ROOT / 'api' / 'routers'
MAIN_PY = PROJECT_ROOT / 'main.py'


class DuplicateCleaner:

    def __init__(self) ->None:
        self.changes = []

    def load_duplicate_report(self) ->Any:
        """Load the duplicate analysis report"""
        report_file = PROJECT_ROOT / 'duplicate-analysis-report.json'
        if report_file.exists():
            with open(report_file, 'r') as f:
                return json.load(f)
        return None

    def consolidate_semantic_duplicates(self, dry_run: Any=True) ->Any:
        """Consolidate semantic duplicates"""
        logger.info('🔧 Consolidating Semantic Duplicates...')
        consolidation_plan = {'getcurrentuser': {'keep':
            'GET /api/v1/auth/me', 'remove': ['GET /api/v1/users/me'],
            'reason':
            'Auth endpoint is the canonical source for current user'},
            'getcircuitbreakerstatus': {'keep':
            'GET /api/v1/ai/optimization/circuit-breaker/status', 'remove':
            ['GET /api/v1/ai-assessments/circuit-breaker/status',
            'GET /api/ai/assessments/circuit-breaker/status'], 'reason':
            'Centralize circuit breaker in optimization namespace'},
            'resetcircuitbreaker': {'keep':
            'POST /api/v1/ai/optimization/circuit-breaker/reset', 'remove':
            ['POST /api/v1/ai-assessments/circuit-breaker/reset',
            'POST /api/ai/assessments/circuit-breaker/reset'], 'reason':
            'Centralize circuit breaker in optimization namespace'},
            'getaicachemetrics': {'keep':
            'GET /api/v1/ai/optimization/cache/metrics', 'remove': [
            'GET /api/v1/ai-assessments/cache/metrics',
            'GET /api/ai/assessments/cache/metrics',
            'GET /api/v1/chat/cache/metrics'], 'reason':
            'Centralize cache metrics in optimization namespace'},
            'getqualitytrends': {'keep':
            'GET /api/v1/evidence/quality/trends', 'remove': [
            'GET /api/v1/chat/quality/trends'], 'reason':
            'Evidence is the source of truth for quality metrics'}}
        for pattern, plan in consolidation_plan.items():
            logger.info('\n  Pattern: %s' % pattern)
            logger.info('    Keep: %s' % plan['keep'])
            logger.info('    Remove: %s' % ', '.join(plan['remove']))
            logger.info('    Reason: %s' % plan['reason'])
            if not dry_run:
                for endpoint in plan['remove']:
                    self.remove_endpoint(endpoint)
        return consolidation_plan

    def remove_endpoint(self, endpoint: str) ->bool:
        """Remove an endpoint from router files"""
        method, path = endpoint.split(' ', 1)
        method = method.lower()
        endpoint_map = {'GET /api/v1/users/me': ('users.py', '/me'),
            'GET /api/v1/ai-assessments/circuit-breaker/status': (
            'ai_assessments.py', '/circuit-breaker/status'),
            'POST /api/v1/ai-assessments/circuit-breaker/reset': (
            'ai_assessments.py', '/circuit-breaker/reset'),
            'GET /api/v1/ai-assessments/cache/metrics': (
            'ai_assessments.py', '/cache/metrics'),
            'GET /api/ai/assessments/circuit-breaker/status': None,
            'POST /api/ai/assessments/circuit-breaker/reset': None,
            'GET /api/ai/assessments/cache/metrics': None,
            'GET /api/v1/chat/cache/metrics': ('chat.py', '/cache/metrics'),
            'GET /api/v1/chat/quality/trends': ('chat.py', '/quality/trends')}
        if endpoint not in endpoint_map:
            logger.info('  ⚠️  No mapping for %s' % endpoint)
            return False
        mapping = endpoint_map[endpoint]
        if mapping is None:
            logger.info('  📝 %s handled via main.py router inclusion' %
                endpoint)
            return True
        router_file, local_path = mapping
        router_path = ROUTERS_DIR / router_file
        if not router_path.exists():
            logger.info('  ❌ Router file %s not found' % router_file)
            return False
        with open(router_path, 'r') as f:
            lines = f.readlines()
        new_lines = []
        found = False
        in_function = False
        decorator_line = f'@router.{method}("{local_path}"'
        for i, line in enumerate(lines):
            if decorator_line in line:
                found = True
                in_function = True
                new_lines.append('# REMOVED: Duplicate endpoint\n')
                new_lines.append('# ' + line)
            elif in_function:
                if line.strip().startswith('@'):
                    in_function = False
                    new_lines.append(line)
                elif i > 0 and not line.strip() and lines[i - 1].strip(
                    ) and not lines[i - 1].strip().endswith(','):
                    in_function = False
                    new_lines.append('#\n')
                    new_lines.append(line)
                else:
                    new_lines.append('# ' + line if line.strip() else '#\n')
            else:
                new_lines.append(line)
        if found:
            with open(router_path, 'w') as f:
                f.writelines(new_lines)
            self.changes.append(f'Removed {endpoint} from {router_file}')
            logger.info('  ✅ Removed %s from %s' % (endpoint, router_file))
            return True
        else:
            logger.info('  ⚠️  Endpoint %s not found in %s' % (
                decorator_line, router_file))
            return False

    def clean_namespace_duplicates(self, dry_run: Any=True) ->Any:
        """Clean up namespace duplicates by removing deprecated namespaces"""
        logger.info('\n🔧 Cleaning Namespace Duplicates...')
        deprecated_namespaces = ['/api/ai/assessments/',
            '/api/v1/ai-assessments/']
        for namespace in deprecated_namespaces:
            logger.info('\n  Removing deprecated namespace: %s' % namespace)
            if not dry_run:
                self.remove_namespace_routes(namespace)
        return deprecated_namespaces

    def remove_namespace_routes(self, namespace: str) ->Any:
        """Remove or comment out routes in a deprecated namespace"""
        with open(MAIN_PY, 'r') as f:
            lines = f.readlines()
        new_lines = []
        modified = False
        for line in lines:
            if (namespace == '/api/ai/assessments/' and 
                'app.include_router(ai_assessments.router, prefix="/api/ai/assessments"'
                 in line):
                new_lines.append('# DEPRECATED: ' + line)
                modified = True
                self.changes.append(
                    f'Commented out legacy namespace {namespace} in main.py')
            elif f'prefix="{namespace[:-1]}"' in line and 'app.include_router' in line:
                new_lines.append('# DEPRECATED: ' + line)
                modified = True
                self.changes.append(
                    f'Commented out namespace {namespace} in main.py')
            else:
                new_lines.append(line)
        if modified:
            with open(MAIN_PY, 'w') as f:
                f.writelines(new_lines)
        return modified

    def identify_safe_removals(self) ->Any:
        """Identify endpoints that are safe to remove"""
        report = self.load_duplicate_report()
        if not report:
            return []
        safe_to_remove = []
        test_endpoints = ['DELETE /api/test-utils/cleanup-test-users',
            'GET /api/test-utils/health']
        deprecated_endpoints = ['GET /api/ai/assessments/cache/metrics',
            'GET /api/ai/assessments/circuit-breaker/status',
            'POST /api/ai/assessments/circuit-breaker/reset',
            'GET /api/v1/ai-assessments/cache/metrics',
            'GET /api/v1/ai-assessments/circuit-breaker/status',
            'POST /api/v1/ai-assessments/circuit-breaker/reset']
        safe_to_remove.extend(test_endpoints)
        safe_to_remove.extend(deprecated_endpoints)
        return safe_to_remove

    def generate_cleanup_plan(self) ->Any:
        """Generate a comprehensive cleanup plan"""
        logger.info('\n' + '=' * 80)
        logger.info('🧹 API CLEANUP PLAN')
        logger.info('=' * 80)
        report = self.load_duplicate_report()
        if not report:
            print(
                '❌ No duplicate analysis report found. Run analyze-duplicates.py first.',
                )
            return
        semantic_plan = self.consolidate_semantic_duplicates(dry_run=True)
        namespace_plan = self.clean_namespace_duplicates(dry_run=True)
        safe_removals = self.identify_safe_removals()
        logger.info('\n🗑️  SAFE TO REMOVE:')
        for endpoint in safe_removals[:10]:
            logger.info('    - %s' % endpoint)
        if len(safe_removals) > 10:
            logger.info('    ... and %s more' % (len(safe_removals) - 10))
        logger.info('\n' + '=' * 80)
        logger.info('📊 CLEANUP SUMMARY:')
        logger.info('  Semantic duplicates to consolidate: %s' % len(
            semantic_plan))
        logger.info('  Deprecated namespaces to remove: %s' % len(
            namespace_plan))
        logger.info('  Safe endpoints to remove: %s' % len(safe_removals))
        total_reduction = len(semantic_plan) * 2 + len(safe_removals)
        logger.info('\n  Total endpoint reduction: ~%s endpoints' %
            total_reduction)
        logger.info('  From: 166 endpoints')
        logger.info('  To: ~%s endpoints' % (166 - total_reduction))
        return {'semantic_consolidation': semantic_plan,
            'namespace_cleanup': namespace_plan, 'safe_removals': safe_removals,
            }

    def execute_cleanup(self, cautious: Any=True) ->Any:
        """Execute the cleanup plan"""
        logger.info('\n🚀 EXECUTING CLEANUP...')
        if cautious:
            logger.info('  (Running in cautious mode - only safe changes)')
            logger.info('\n1. Consolidating semantic duplicates...')
            self.consolidate_semantic_duplicates(dry_run=False)
            logger.info('\n2. Skipping namespace removal (needs testing)')
            logger.info('\n✅ Cautious cleanup complete!')
        else:
            logger.info('  (Running in full mode - all changes)')
            self.consolidate_semantic_duplicates(dry_run=False)
            self.clean_namespace_duplicates(dry_run=False)
            logger.info('\n✅ Full cleanup complete!')
        if self.changes:
            logger.info('\n📝 Changes made:')
            for change in self.changes[:20]:
                logger.info('    - %s' % change)
            if len(self.changes) > 20:
                logger.info('    ... and %s more' % (len(self.changes) - 20))
        return self.changes


def main() ->Any:
    import sys
    cleaner = DuplicateCleaner()
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        cautious = '--full' not in sys.argv
        changes = cleaner.execute_cleanup(cautious=cautious)
        logger.info('\n💾 Total changes: %s' % len(changes))
        logger.info('\n⚠️  Remember to:')
        logger.info('  1. Review all changes with git diff')
        logger.info('  2. Test all affected endpoints')
        logger.info('  3. Update frontend if needed')
        logger.info('  4. Run integration tests')
    else:
        plan = cleaner.generate_cleanup_plan()
        logger.info('\n💡 To execute cleanup:')
        print(
            '  Cautious mode (recommended): python scripts/cleanup-duplicates.py --execute',
            )
        logger.info(
            '  Full mode: python scripts/cleanup-duplicates.py --execute --full',
            )
        with open(PROJECT_ROOT / 'cleanup-plan.json', 'w') as f:
            json.dump(plan, f, indent=2, default=str)
        logger.info('\n📄 Cleanup plan saved to cleanup-plan.json')


if __name__ == '__main__':
    main()
