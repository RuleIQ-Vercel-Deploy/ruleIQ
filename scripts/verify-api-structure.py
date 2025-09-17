"""
from __future__ import annotations
import logging

# Constants
DEFAULT_RETRIES = 5

logger = logging.getLogger(__name__)

Verify API structure and naming conventions
"""
import re
from pathlib import Path
from typing import Dict, List, Any
PROJECT_ROOT = Path(__file__).parent.parent
ROUTERS_DIR = PROJECT_ROOT / 'api' / 'routers'
MAIN_PY = PROJECT_ROOT / 'api' / 'main.py'


def extract_endpoints() ->Dict[str, List[str]]:
    """Extract all API endpoints from routers"""
    endpoints = {}
    for router_file in ROUTERS_DIR.glob('*.py'):
        if router_file.name == '__init__.py':
            continue
        with open(router_file, 'r') as f:
            content = f.read()
        pattern = '@router\\.(get|post|put|patch|delete)\\("([^"]+)"'
        matches = re.findall(pattern, content)
        endpoints[router_file.stem] = [f'{method.upper()} {path}' for
            method, path in matches]
    return endpoints


def check_naming_conventions(endpoints: Dict[str, List[str]]) ->Dict[str,
    List[str]]:
    """Check for naming convention issues"""
    issues = {'trailing_slashes': [], 'underscores_in_paths': [],
        'inconsistent_params': [], 'camelCase_in_paths': []}
    for router, paths in endpoints.items():
        for endpoint in paths:
            method, path = endpoint.split(' ', 1)
            if path.endswith('/') and path != '/':
                issues['trailing_slashes'].append(f'{router}: {endpoint}')
            path_without_params = re.sub('\\{[^}]+\\}', '', path)
            if '_' in path_without_params:
                issues['underscores_in_paths'].append(f'{router}: {endpoint}')
            if re.search('[a-z][A-Z]', path_without_params):
                issues['camelCase_in_paths'].append(f'{router}: {endpoint}')
            params = re.findall('\\{([^}]+)\\}', path)
            for param in params:
                if param not in ['id', 'user_id', 'framework_id',
                    'assessment_id']:
                    issues['inconsistent_params'].append(
                        f'{router}: {endpoint} - param: {{{param}}}')
    return issues


def find_duplicates(endpoints: Dict[str, List[str]]) ->List[str]:
    """Find potentially duplicate endpoints"""
    duplicates = []
    all_paths = []
    for router, paths in endpoints.items():
        for endpoint in paths:
            all_paths.append((router, endpoint))
    for i, (router1, endpoint1) in enumerate(all_paths):
        for router2, endpoint2 in all_paths[i + 1:]:
            method1, path1 = endpoint1.split(' ', 1)
            method2, path2 = endpoint2.split(' ', 1)
            if method1 == method2:
                norm_path1 = re.sub('\\{[^}]+\\}', '{id}', path1)
                norm_path2 = re.sub('\\{[^}]+\\}', '{id}', path2)
                if ('generate' in norm_path1 and 'generate' in norm_path2 and
                    router1 != router2):
                    duplicates.append(
                        f'{router1}: {endpoint1} <-> {router2}: {endpoint2}')
                elif norm_path1 == norm_path2 and router1 != router2:
                    duplicates.append(
                        f'{router1}: {endpoint1} <-> {router2}: {endpoint2}')
    return duplicates


def main() ->Any:
    logger.info('🔍 API Structure Verification')
    logger.info('=' * 80)
    endpoints = extract_endpoints()
    total_endpoints = sum(len(paths) for paths in endpoints.values())
    logger.info('\n📊 Statistics:')
    logger.info('   Total Routers: %s' % len(endpoints))
    logger.info('   Total Endpoints: %s' % total_endpoints)
    issues = check_naming_conventions(endpoints)
    logger.info('\n✅ Naming Convention Check:')
    for issue_type, issue_list in issues.items():
        if issue_list:
            logger.info('\n   ⚠️  %s:' % issue_type.replace('_', ' ').title())
            for issue in issue_list[:5]:
                logger.info('      - %s' % issue)
            if len(issue_list) > DEFAULT_RETRIES:
                logger.info('      ... and %s more' % (len(issue_list) - 5))
        else:
            logger.info('   ✅ No %s found' % issue_type.replace('_', ' '))
    duplicates = find_duplicates(endpoints)
    if duplicates:
        logger.info('\n⚠️  Potential Duplicate Endpoints:')
        for dup in duplicates[:10]:
            logger.info('   - %s' % dup)
    else:
        logger.info('\n✅ No duplicate endpoints found')
    logger.info('\n' + '=' * 80)
    logger.info('📋 Summary:')
    total_issues = sum(len(v) for v in issues.values()) + len(duplicates)
    if total_issues == 0:
        logger.info('   ✅ All API endpoints follow naming conventions!')
    else:
        logger.info('   ⚠️  Found %s total issues to review' % total_issues)
        logger.info('\n   Recommendations:')
        logger.info('   1. Use kebab-case for all URL paths')
        logger.info('   2. Standardize path parameters to use {id}')
        logger.info('   3. Remove trailing slashes except for root paths')
        logger.info('   4. Consolidate duplicate functionality')
    logger.info('\n' + '=' * 80)
    logger.info('🔍 Policy Endpoints Analysis:')
    policy_endpoints = {}
    for router, paths in endpoints.items():
        if 'polic' in router.lower() or 'ai' in router.lower():
            policy_related = [p for p in paths if 'polic' in p.lower() or
                'generate' in p.lower()]
            if policy_related:
                policy_endpoints[router] = policy_related
    if policy_endpoints:
        logger.info('\n   Policy-related endpoints found in:')
        for router, paths in policy_endpoints.items():
            logger.info('\n   📁 %s:' % router)
            for path in paths:
                logger.info('      - %s' % path)
    return total_issues == 0


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
