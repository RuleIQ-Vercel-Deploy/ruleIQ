"""
from __future__ import annotations
import logging

# Constants
MAX_RETRIES = 3

logger = logging.getLogger(__name__)

Update the API connection map HTML file to reflect the new consolidated API structure.
Based on the API alignment cleanup we performed.
"""
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
ENDPOINT_UPDATES = {'removed': ['/api/v1/users/me',
    '/api/v1/ai-assessments/circuit-breaker/status',
    '/api/v1/ai-assessments/circuit-breaker/reset',
    '/api/v1/ai-assessments/cache/metrics', '/api/v1/chat/cache/metrics',
    '/api/v1/chat/quality/trends', '/api/ai/assessments',
    '/api/v1/ai-assessments'], 'updated': {'/api/v1/users/me':
    '/api/v1/auth/me', '/api/v1/ai-assessments/circuit-breaker/status':
    '/api/v1/ai/optimization/circuit-breaker/status',
    '/api/v1/ai-assessments/circuit-breaker/reset':
    '/api/v1/ai/optimization/circuit-breaker/reset',
    '/api/v1/ai-assessments/cache/metrics':
    '/api/v1/ai/optimization/cache/metrics', '/api/v1/chat/cache/metrics':
    '/api/v1/ai/optimization/cache/metrics', '/api/v1/chat/quality/trends':
    '/api/v1/evidence/quality/trends', '/api/v1/ai-assessments':
    '/api/v1/ai/assessments', '/api/ai/assessments': '/api/v1/ai/assessments'}}

def update_connection_path(path: str) ->Optional[str]:
    """Update a single path if needed."""
    if path in ENDPOINT_UPDATES['updated']:
        return ENDPOINT_UPDATES['updated'][path]
    for old_path, new_path in ENDPOINT_UPDATES['updated'].items():
        if path.startswith(old_path):
            trailing = path[len(old_path):]
            return new_path + trailing
    return None

def should_remove_connection(path: str) ->bool:
    """Check if a connection should be removed."""
    for removed_path in ENDPOINT_UPDATES['removed']:
        if removed_path in ENDPOINT_UPDATES['updated']:
            continue
        if path == removed_path or path.startswith(removed_path + '/'):
            return True
    return False

def process_connections(connections: List[Dict[str, Any]], stats: Dict[str,
    int]) ->List[Dict[str, Any]]:
    """Process connections array and update paths."""
    updated_connections = []
    for conn in connections:
        if conn.get('frontendDetails') and conn['frontendDetails'].get('path'):
            frontend_path = conn['frontendDetails']['path']
            if should_remove_connection(frontend_path):
                stats['removed'] += 1
                continue
            new_path = update_connection_path(frontend_path)
            if new_path:
                conn['frontendDetails']['path'] = new_path
                if conn.get('frontend'):
                    parts = conn['frontend'].split(':')
                    if len(parts) >= MAX_RETRIES:
                        parts[-1] = new_path
                        conn['frontend'] = ':'.join(parts)
                stats['frontend_updated'] += 1
        if conn.get('backend') and conn['backend'].get('path'):
            backend_path = conn['backend']['path']
            if should_remove_connection(backend_path):
                if conn.get('frontendDetails'):
                    conn['backend'] = None
                    conn['status'] = 'missing'
                else:
                    stats['removed'] += 1
                    continue
            else:
                new_path = update_connection_path(backend_path)
                if new_path:
                    conn['backend']['path'] = new_path
                    stats['backend_updated'] += 1
        if conn.get('frontendDetails') and conn.get('backend'):
            frontend_path = conn['frontendDetails']['path']
            backend_path = conn['backend']['path']
            if frontend_path == backend_path:
                conn['status'] = 'connected'
            elif frontend_path.replace('/api/v1', '') == backend_path.replace(
                '/api/v1', ''):
                conn['status'] = 'connected'
        updated_connections.append(conn)
    return updated_connections

def update_html_file(input_file: str, output_file: str) ->Optional[Any]:
    """Update the HTML file with new API structure."""
    logger.info('Loading HTML from: %s' % input_file)
    with open(input_file, 'r') as f:
        html_content = f.read()
    connections_match = re.search('const connections = (\\[[\\s\\S]*?\\]);',
        html_content)
    if not connections_match:
        logger.info('ERROR: Could not find connections array in HTML')
        return None
    try:
        connections_str = connections_match.group(1)
        connections = json.loads(connections_str)
        logger.info('Found %s connections' % len(connections))
    except json.JSONDecodeError as e:
        logger.info('ERROR: Failed to parse connections JSON: %s' % e)
        return None
    stats = {'frontend_updated': 0, 'backend_updated': 0, 'removed': 0,
        'unchanged': 0}
    updated_connections = process_connections(connections, stats)
    stats['unchanged'] = len(updated_connections) - stats['frontend_updated'
        ] - stats['backend_updated']
    updated_connections_str = json.dumps(updated_connections, indent=2)
    update_notice = f"""
      <div style="background: #fef3c7; color: #92400e; padding: 10px; text-align: center; margin-top: 10px; border-radius: 6px;">
        <strong>Updated: {datetime.now().strftime('%Y-%m-%d')}</strong> - API structure consolidated with {stats['frontend_updated'] + stats['backend_updated']} endpoint updates
      </div>"""
    start_match = re.search('const connections = \\[', html_content)
    end_match = re.search('\\];\\s*let currentFilter', html_content)
    if start_match and end_match:
        updated_html = (html_content[:start_match.start()] +
            f"""const connections = {updated_connections_str};
    """ +
            html_content[end_match.start() + 2:])
    else:
        print(
            'WARNING: Could not find exact positions for replacement, using original HTML'
            )
        updated_html = html_content
    updated_html = re.sub('(<h1>.*?</h1>\\s*<p>.*?</p>)', '\\1' +
        update_notice, updated_html)
    updated_html = re.sub('<title>.*?</title>',
        f"<title>RuleIQ API Connection Map - Consolidated ({datetime.now().strftime('%Y-%m-%d')})</title>"
        , updated_html)
    logger.info('\nSaving updated HTML to: %s' % output_file)
    with open(output_file, 'w') as f:
        f.write(updated_html)
    return stats

def main() ->None:
    """Main entry point."""
    input_file = 'api-connection-map.html'
    output_file = 'api-connection-map-consolidated.html'
    if not Path(input_file).exists():
        logger.info('ERROR: %s not found!' % input_file)
        return
    stats = update_html_file(input_file, output_file)
    if stats:
        logger.info('\n' + '=' * 60)
        logger.info('UPDATE SUMMARY')
        logger.info('=' * 60)
        logger.info('Frontend paths updated: %s' % stats['frontend_updated'])
        logger.info('Backend paths updated: %s' % stats['backend_updated'])
        logger.info('Connections removed: %s' % stats['removed'])
        logger.info('Unchanged connections: %s' % stats['unchanged'])
        logger.info('Total processed: %s' % (sum(stats.values()) - stats[
            'unchanged']))
        logger.info('\n✅ HTML visualization updated successfully!')
        logger.info('📁 Output file: %s' % output_file)

if __name__ == '__main__':
    main()
