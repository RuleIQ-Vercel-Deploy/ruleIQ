"""
Analyze the actual connection status between frontend and backend.
"""
from typing import Any, Optional, Tuple
import logging
logger = logging.getLogger(__name__)
import json
import re
from collections import Counter


def analyze_connections() ->Optional[Tuple[Any, ...]]:
    """Analyze the connections in the HTML file."""
    with open('api-connection-map.html', 'r') as f:
        html_content = f.read()
    connections_match = re.search('const connections = (\\[[\\s\\S]*?\\]);',
        html_content)
    if not connections_match:
        logger.info('ERROR: Could not find connections array')
        return
    connections = json.loads(connections_match.group(1))
    stats = Counter()
    connected_endpoints = []
    missing_endpoints = []
    unused_endpoints = []
    for conn in connections:
        status = conn.get('status', 'unknown')
        stats[status] += 1
        if status == 'connected':
            if conn.get('frontendDetails') and conn.get('backend'):
                connected_endpoints.append({'frontend':
                    f"{conn['frontendDetails'].get('method', 'N/A')} {conn['frontendDetails'].get('path', 'N/A')}"
                    , 'backend':
                    f"{conn['backend'].get('method', 'N/A')} {conn['backend'].get('path', 'N/A')}"
                    , 'file': conn['frontendDetails'].get('file', 'N/A')})
        elif status == 'missing':
            if conn.get('frontendDetails'):
                missing_endpoints.append({'frontend':
                    f"{conn['frontendDetails'].get('method', 'N/A')} {conn['frontendDetails'].get('path', 'N/A')}"
                    , 'file': conn['frontendDetails'].get('file', 'N/A')})
        elif status == 'unused':
            if conn.get('backend'):
                unused_endpoints.append({'backend':
                    f"{conn['backend'].get('method', 'N/A')} {conn['backend'].get('path', 'N/A')}"
                    , 'summary': conn['backend'].get('summary', 'N/A')})
    logger.info('=' * 80)
    logger.info('API CONNECTION ANALYSIS')
    logger.info('=' * 80)
    logger.info('\nTotal connections mapped: %s' % len(connections))
    logger.info('\nConnection Status Breakdown:')
    logger.info('-' * 40)
    for status, count in sorted(stats.items()):
        percentage = count / len(connections) * 100
        logger.info('  %s : %s (%s%)' % (status, count, percentage))
    logger.info('\n' + '=' * 80)
    logger.info('CONNECTED ENDPOINTS (Frontend ↔ Backend)')
    logger.info('=' * 80)
    if connected_endpoints:
        logger.info('\nTotal connected: %s' % len(connected_endpoints))
        logger.info('\nFirst 20 connected endpoints:')
        for i, endpoint in enumerate(connected_endpoints[:20], 1):
            logger.info('\n%s. %s' % (i, endpoint['file']))
            logger.info('   Frontend: %s' % endpoint['frontend'])
            logger.info('   Backend:  %s' % endpoint['backend'])
    else:
        logger.info('\n❌ No connected endpoints found!')
    logger.info('\n' + '=' * 80)
    logger.info('MISSING BACKEND ENDPOINTS (Frontend → ???)')
    logger.info('=' * 80)
    if missing_endpoints:
        logger.info('\nTotal missing: %s' % len(missing_endpoints))
        logger.info('\nFirst 20 missing endpoints:')
        for i, endpoint in enumerate(missing_endpoints[:20], 1):
            logger.info('\n%s. %s' % (i, endpoint['file']))
            logger.info('   Frontend: %s' % endpoint['frontend'])
    logger.info('\n' + '=' * 80)
    logger.info('UNUSED BACKEND ENDPOINTS (??? ← Backend)')
    logger.info('=' * 80)
    if unused_endpoints:
        logger.info('\nTotal unused: %s' % len(unused_endpoints))
        logger.info('\nFirst 20 unused endpoints:')
        for i, endpoint in enumerate(unused_endpoints[:20], 1):
            logger.info('\n%s. %s' % (i, endpoint['backend']))
            logger.info('   Summary: %s' % endpoint['summary'])
    logger.info('\n' + '=' * 80)
    logger.info('CONNECTION ISSUES ANALYSIS')
    logger.info('=' * 80)
    frontend_paths = set()
    backend_paths = set()
    for conn in connections:
        if conn.get('frontendDetails') and conn['frontendDetails'].get('path'):
            frontend_paths.add(conn['frontendDetails']['path'])
        if conn.get('backend') and conn['backend'].get('path'):
            backend_paths.add(conn['backend']['path'])
    logger.info('\nUnique frontend paths: %s' % len(frontend_paths))
    logger.info('Unique backend paths: %s' % len(backend_paths))
    potential_matches = 0
    for f_path in frontend_paths:
        f_normalized = f_path.replace('/api/v1/', '').replace('/api/', '')
        for b_path in backend_paths:
            b_normalized = b_path.replace('/api/v1/', '').replace('/api/', '')
            if (f_normalized == b_normalized or f_normalized in
                b_normalized or b_normalized in f_normalized):
                potential_matches += 1
                break
    logger.info('Potential matches (with normalization): %s' %
        potential_matches)
    return stats, connected_endpoints, missing_endpoints, unused_endpoints


if __name__ == '__main__':
    analyze_connections()
