"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Analyze ALL missing connections and generate a comprehensive fix plan.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any


def extract_connections() ->Any:
    """Extract and categorize all connections from the HTML file."""
    with open('api-connection-map.html', 'r') as f:
        html_content = f.read()
    connections_match = re.search('const connections = (\\[[\\s\\S]*?\\]);',
        html_content)
    if not connections_match:
        return None
    return json.loads(connections_match.group(1))


def analyze_missing_endpoints(connections: Any) ->Any:
    """Analyze all missing backend endpoints by service."""
    missing_by_service = defaultdict(list)
    for conn in connections:
        if conn.get('status') == 'missing' and conn.get('frontendDetails'):
            details = conn['frontendDetails']
            service = details.get('file', 'unknown').replace('.ts', '')
            endpoint_info = {'method': details.get('method', 'GET'), 'path':
                details.get('path', ''), 'line': details.get('line', 0),
                'full_path': f"/api/v1{details.get('path', '')}" if not
                details.get('path', '').startswith('/api') else details.get
                ('path', '')}
            missing_by_service[service].append(endpoint_info)
    return missing_by_service


def analyze_connected_patterns(connections: Any) ->Any:
    """Analyze patterns in successfully connected endpoints."""
    patterns = {'path_patterns': [], 'working_services': set(),
        'common_prefixes': set()}
    for conn in connections:
        if conn.get('status') == 'connected':
            if conn.get('frontendDetails') and conn.get('backend'):
                frontend = conn['frontendDetails']
                backend = conn['backend']
                patterns['working_services'].add(frontend.get('file', '').
                    replace('.ts', ''))
                f_path = frontend.get('path', '')
                b_path = backend.get('path', '')
                if f_path and b_path:
                    if b_path.startswith('/api/v1'):
                        prefix = b_path[:7]
                        patterns['common_prefixes'].add(prefix)
                    patterns['path_patterns'].append({'frontend': f_path,
                        'backend': b_path, 'service': frontend.get('file', '')},
                        )
    return patterns


def generate_backend_endpoints(missing_by_service: Any) ->Any:
    """Generate backend endpoint implementations needed."""
    endpoints_to_create = []
    for service, endpoints in missing_by_service.items():
        for endpoint in endpoints:
            router_map = {'ai-self-review.service': 'ai_assessments',
                'assessments.service': 'assessments',
                'assessments-ai.service': 'ai_assessments',
                'business-profiles.service': 'business_profiles',
                'chat.service': 'chat', 'compliance.service': 'compliance',
                'evidence.service': 'evidence', 'frameworks.service':
                'frameworks', 'implementation.service': 'implementation',
                'integrations.service': 'integrations', 'policies.service':
                'policies', 'reports.service': 'reports', 'users.service':
                'users', 'team.service': 'team', 'notifications.service':
                'notifications', 'useSurvey': 'surveys',
                'useBusinessProfile': 'business_profiles', 'useAssessments':
                'assessments', 'useEvidence': 'evidence', 'useTeam': 'team',
                'useUsers': 'users', 'useWorkflow': 'workflows'}
            router_name = router_map.get(service, service.replace(
                '.service', '').replace('-', '_'))
            path = endpoint['path']
            if path.startswith('/'):
                path = path[1:]
            path_with_params = path.replace('${', '{').replace('}', '}')
            endpoints_to_create.append({'service': service, 'router':
                router_name, 'method': endpoint['method'], 'path':
                path_with_params, 'full_path':
                f'/api/v1/{path_with_params}', 'frontend_line': endpoint[
                'line']})
    return endpoints_to_create


def generate_fix_plan(missing_by_service: Any, patterns: Any,
    endpoints_to_create: Any) ->Any:
    """Generate a comprehensive fix plan."""
    plan = {'summary': {'total_missing': sum(len(endpoints) for endpoints in
        missing_by_service.values()), 'services_affected': len(
        missing_by_service), 'endpoints_to_create': len(endpoints_to_create
        )}, 'by_service': {}, 'implementation_order': []}
    by_router = defaultdict(list)
    for endpoint in endpoints_to_create:
        by_router[endpoint['router']].append(endpoint)
    for router, endpoints in sorted(by_router.items(), key=lambda x: len(x[
        1]), reverse=True):
        plan['by_service'][router] = {'file': f'api/routers/{router}.py',
            'endpoints': endpoints, 'count': len(endpoints)}
        plan['implementation_order'].append(router)
    return plan


def generate_documentation(plan: Any, missing_by_service: Any) ->Any:
    """Generate comprehensive documentation."""
    doc = []
    doc.append('# API Connection Fix Implementation Plan')
    doc.append(f'\n## Summary')
    doc.append(
        f"- **Total Missing Endpoints**: {plan['summary']['total_missing']}")
    doc.append(
        f"- **Services Affected**: {plan['summary']['services_affected']}")
    doc.append(
        f"- **Backend Endpoints to Create**: {plan['summary']['endpoints_to_create']}",
        )
    doc.append(f'\n## Implementation by Router')
    for router in plan['implementation_order']:
        router_info = plan['by_service'][router]
        doc.append(f"\n### {router}.py ({router_info['count']} endpoints)")
        doc.append(f"**File**: `{router_info['file']}`\n")
        doc.append('| Method | Path | Frontend Service |')
        doc.append('|--------|------|-----------------|')
        for endpoint in router_info['endpoints']:
            doc.append(
                f"| {endpoint['method']} | `{endpoint['path']}` | {endpoint['service']} |",
                )
    doc.append(f'\n## Frontend Services Breakdown')
    for service, endpoints in sorted(missing_by_service.items()):
        doc.append(f'\n### {service} ({len(endpoints)} endpoints)')
        for endpoint in endpoints:
            doc.append(f"- {endpoint['method']} `{endpoint['path']}`")
    return '\n'.join(doc)


def main() ->Any:
    """Main analysis function."""
    logger.info('=' * 80)
    logger.info('COMPREHENSIVE API CONNECTION ANALYSIS')
    logger.info('=' * 80)
    connections = extract_connections()
    if not connections:
        logger.info('ERROR: Could not extract connections')
        return
    missing_by_service = analyze_missing_endpoints(connections)
    patterns = analyze_connected_patterns(connections)
    endpoints_to_create = generate_backend_endpoints(missing_by_service)
    plan = generate_fix_plan(missing_by_service, patterns, endpoints_to_create)
    logger.info('\n📊 MISSING ENDPOINTS BY SERVICE:')
    logger.info('-' * 40)
    for service, endpoints in sorted(missing_by_service.items()):
        logger.info('%s : %s endpoints' % (service, len(endpoints)))
    logger.info('\n🔧 BACKEND ROUTERS TO UPDATE:')
    logger.info('-' * 40)
    for router in plan['implementation_order']:
        router_info = plan['by_service'][router]
        logger.info('%s : %s endpoints' % (router, router_info['count']))
    logger.info('\n✅ WORKING PATTERNS FOUND:')
    logger.info('-' * 40)
    logger.info('Working services: %s' % ', '.join(patterns[
        'working_services']))
    logger.info('Common prefixes: %s' % ', '.join(patterns['common_prefixes']))
    documentation = generate_documentation(plan, missing_by_service)
    with open('api-fix-plan.md', 'w') as f:
        f.write(documentation)
    logger.info('\n📝 Documentation saved to: api-fix-plan.md')
    with open('api-fix-plan.json', 'w') as f:
        json.dump({'missing_by_service': {k: v for k, v in
            missing_by_service.items()}, 'patterns': {'working_services':
            list(patterns['working_services']), 'common_prefixes': list(
            patterns['common_prefixes']), 'path_patterns': patterns[
            'path_patterns']}, 'plan': plan}, f, indent=2)
    logger.info('📊 Detailed plan saved to: api-fix-plan.json')
    return plan


if __name__ == '__main__':
    main()
