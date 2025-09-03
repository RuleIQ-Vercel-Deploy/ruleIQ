"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Update Postman collection to reflect the new consolidated API structure.
Based on the API alignment cleanup we performed.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
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


def update_request_url(request: Dict[str, Any]) ->bool:
    """Update a single request URL if needed."""
    if 'url' not in request:
        return False
    url = request['url']
    if isinstance(url, dict) and 'raw' in url:
        raw_url = url['raw']
        updated = False
        for old_path, new_path in ENDPOINT_UPDATES['updated'].items():
            if old_path in raw_url:
                url['raw'] = raw_url.replace(old_path, new_path)
                if 'path' in url and isinstance(url['path'], list):
                    new_path_parts = new_path.strip('/').split('/')
                    url['path'] = new_path_parts
                logger.info('  Updated: %s -> %s' % (old_path, new_path))
                updated = True
                break
        return updated
    return False


def should_remove_request(request: Dict[str, Any]) ->bool:
    """Check if a request should be removed."""
    if 'url' not in request:
        return False
    url = request['url']
    if isinstance(url, dict) and 'raw' in url:
        raw_url = url['raw']
        for removed_path in ENDPOINT_UPDATES['removed']:
            if (removed_path in raw_url and removed_path not in
                ENDPOINT_UPDATES['updated']):
                logger.info('  Removing deprecated endpoint: %s' % removed_path,
                    )
                return True
    return False


def process_items(items: List[Dict[str, Any]], stats: Dict[str, int]) ->List[
    Dict[str, Any]]:
    """Process collection items recursively."""
    updated_items = []
    for item in items:
        if 'item' in item and isinstance(item['item'], list):
            logger.info('\nProcessing folder: %s' % item.get('name', 'Unnamed'),
                )
            item['item'] = process_items(item['item'], stats)
            if item['item']:
                updated_items.append(item)
        elif 'request' in item:
            if should_remove_request(item):
                stats['removed'] += 1
            else:
                if update_request_url(item):
                    stats['updated'] += 1
                else:
                    stats['unchanged'] += 1
                updated_items.append(item)
    return updated_items


def update_collection(input_file: str, output_file: str) ->Any:
    """Update the Postman collection with new API structure."""
    logger.info('Loading collection from: %s' % input_file)
    with open(input_file, 'r') as f:
        collection = json.load(f)
    logger.info('Collection: %s' % collection['info']['name'])
    logger.info('Original schema: %s' % collection['info'].get('schema',
        'unknown'))
    collection['info']['name'] = (
        f"RuleIQ API Collection - Consolidated ({datetime.now().strftime('%Y-%m-%d')})",
        )
    collection['info']['description'] = """Updated RuleIQ API collection after endpoint consolidation and cleanup.

Changes:
- Removed duplicate endpoints
- Consolidated AI optimization endpoints
- Updated namespace from /api/v1/ai-assessments to /api/v1/ai/assessments
- Moved user/me to auth/me
- Consolidated cache and circuit breaker endpoints under /api/v1/ai/optimization"""
    stats = {'updated': 0, 'removed': 0, 'unchanged': 0}
    if 'item' in collection:
        logger.info('\nProcessing collection items...')
        collection['item'] = process_items(collection['item'], stats)
    logger.info('\nSaving updated collection to: %s' % output_file)
    with open(output_file, 'w') as f:
        json.dump(collection, f, indent=2)
    logger.info('\n' + '=' * 60)
    logger.info('UPDATE SUMMARY')
    logger.info('=' * 60)
    logger.info('Updated endpoints: %s' % stats['updated'])
    logger.info('Removed endpoints: %s' % stats['removed'])
    logger.info('Unchanged endpoints: %s' % stats['unchanged'])
    logger.info('Total processed: %s' % sum(stats.values()))
    return stats


def main() ->None:
    """Main entry point."""
    collections = ['ruleiq_postman_collection.json',
        'ruleiq_complete_collection.json',
        'ruleiq_postman_collection_with_doppler.json',
        'ruleiq_comprehensive_postman_collection_fixed.json',
        'ruleiq_comprehensive_postman_collection.json']
    input_file = None
    for collection in collections:
        if Path(collection).exists():
            input_file = collection
            break
    if not input_file:
        logger.info('No Postman collection found!')
        return
    output_file = 'ruleiq_postman_collection_consolidated.json'
    stats = update_collection(input_file, output_file)
    logger.info('\n✅ Collection updated successfully!')
    logger.info('📁 Output file: %s' % output_file)


if __name__ == '__main__':
    main()
