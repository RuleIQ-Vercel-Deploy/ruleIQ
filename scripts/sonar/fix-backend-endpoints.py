"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Backend API Endpoint Alignment Script
Fixes trailing slashes and standardizes endpoint naming
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
PROJECT_ROOT = Path(__file__).parent.parent
ROUTERS_DIR = PROJECT_ROOT / 'api' / 'routers'
ENDPOINT_MAPPINGS = {'@router\\.(get|post|put|patch|delete)\\("([^"]+)/"\\)':
    '@router.\\1("\\2")',
    '@router\\.(get|post|put|patch|delete)\\("([^"]+)/",':
    '@router.\\1("\\2",', '\\{session_id\\}': '{id}', '\\{assessment_id\\}':
    '{id}', '\\{profile_id\\}': '{id}', '\\{policy_id\\}': '{id}',
    '\\{framework_id\\}': '{id}', '\\{user_id\\}': '{id}',
    '/business_profiles': '/business-profiles', '/evidence_collection':
    '/evidence-collection', '/self_review': '/self-review'}
ROUTER_FILES = ['assessments.py', 'business_profiles.py', 'policies.py',
    'evidence.py', 'frameworks.py', 'compliance.py', 'chat.py',
    'implementation.py', 'integrations.py', 'monitoring.py', 'reports.py',
    'dashboard.py', 'auth.py', 'ai_chat.py', 'ai_assessments.py', 'iq_agent.py'
    ]


def analyze_router_file(filepath: Path) ->Dict:
    """Analyze a router file for endpoints"""
    with open(filepath, 'r') as f:
        content = f.read()
    endpoint_pattern = (
        '@router\\.(get|post|put|patch|delete)\\("([^"]+)"[^)]*\\)')
    endpoints = re.findall(endpoint_pattern, content)
    prefix_pattern = (
        'router\\s*=\\s*APIRouter\\([^)]*prefix\\s*=\\s*["\\\']([^"\\\']+)["\\\']'
        )
    prefix_match = re.search(prefix_pattern, content)
    prefix = prefix_match.group(1) if prefix_match else ''
    return {'file': filepath.name, 'prefix': prefix, 'endpoints': [(method.
        upper(), path) for method, path in endpoints], 'issues':
        analyze_issues(endpoints)}


def analyze_issues(endpoints: List[Tuple[str, str]]) ->List[str]:
    """Identify issues with endpoints"""
    issues = []
    for method, path in endpoints:
        if path.endswith('/'):
            issues.append(f'Trailing slash: {method} {path}')
        if '{session_id}' in path or '{assessment_id}' in path:
            issues.append(f'Non-standard ID param: {method} {path}')
        if '_' in path and not path.startswith('{'):
            issues.append(f'Underscore in path: {method} {path}')
    return issues


def fix_router_file(filepath: Path, dry_run: bool=True) ->Tuple[str, List[str]
    ]:
    """Fix issues in a router file"""
    with open(filepath, 'r') as f:
        content = f.read()
    original_content = content
    changes = []
    for pattern, replacement in ENDPOINT_MAPPINGS.items():
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes.append(f'Applied pattern: {pattern}')
    prefix_pattern = (
        '(router\\s*=\\s*APIRouter\\([^)]*prefix\\s*=\\s*["\\\'])([^"\\\']+/)["\\\']'
        )
    prefix_match = re.search(prefix_pattern, content)
    if prefix_match and prefix_match.group(2).endswith('/'):
        new_prefix = prefix_match.group(2).rstrip('/')
        content = re.sub(prefix_pattern, f'\\1{new_prefix}"', content)
        changes.append(
            f'Removed trailing slash from prefix: {prefix_match.group(2)}')
    if content != original_content:
        if not dry_run:
            with open(filepath, 'w') as f:
                f.write(content)
    return content, changes


def main() ->None:
    """Main execution"""
    logger.info('🔍 Analyzing Backend API Endpoints\n')
    logger.info('=' * 80)
    all_issues = []
    all_endpoints = {}
    for filename in ROUTER_FILES:
        filepath = ROUTERS_DIR / filename
        if filepath.exists():
            analysis = analyze_router_file(filepath)
            all_endpoints[filename] = analysis
            if analysis['issues']:
                logger.info('\n📁 %s' % filename)
                logger.info('   Prefix: %s' % analysis['prefix'])
                logger.info('   Issues found: %s' % len(analysis['issues']))
                for issue in analysis['issues']:
                    logger.info('   - %s' % issue)
                    all_issues.append((filename, issue))
    if not all_issues:
        logger.info('\n✅ No issues found! All endpoints follow standards.')
        return
    logger.info('\n' + '=' * 80)
    logger.info('\n📊 Total Issues Found: %s' % len(all_issues))
    import sys
    response = sys.argv[1] if len(sys.argv) > 1 else 'n'
    if response.lower() == 'y':
        logger.info('\n🛠️  Fixing issues...')
        for filename in ROUTER_FILES:
            filepath = ROUTERS_DIR / filename
            if filepath.exists():
                _, changes = fix_router_file(filepath, dry_run=False)
                if changes:
                    logger.info('\n✅ Fixed %s:' % filename)
                    for change in changes:
                        logger.info('   - %s' % change)
        logger.info('\n✅ All issues fixed!')
        logger.info('\n📝 Next steps:')
        logger.info("1. Review the changes with 'git diff'")
        logger.info('2. Test the API endpoints')
        logger.info('3. Update frontend services to match')
    else:
        logger.info('\n📝 Dry run mode - no changes made')
        logger.info('Run with confirmation to apply fixes')
    with open(PROJECT_ROOT / 'api-alignment-backend-report.json', 'w') as f:
        json.dump({'total_files': len(ROUTER_FILES), 'files_with_issues':
            len([f for f, a in all_endpoints.items() if a.get('issues')]),
            'total_issues': len(all_issues), 'endpoints': all_endpoints}, f,
            indent=2)
    logger.info('\n📄 Report saved to api-alignment-backend-report.json')


if __name__ == '__main__':
    main()
