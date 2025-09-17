"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Extract all UK regulatory obligations from cached documents.
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import hashlib


def extract_obligations_from_document(doc_path: Path) ->Dict[str, Any]:
    """Extract obligations from a single document."""
    with open(doc_path, 'r') as f:
        data = json.load(f)
    doc_info = {'file': doc_path.name, 'url': data.get('url', ''),
        'fetched_at': data.get('fetched_at', ''), 'metadata': data.get(
        'metadata', {}), 'obligations': []}
    requirements = data.get('requirements', [])
    for req in requirements:
        if isinstance(req, dict):
            obligation = {'type': 'requirement', 'id': req.get('id', ''),
                'title': req.get('title', ''), 'description': req.get(
                'description', ''), 'category': req.get('category', ''),
                'compliance_level': req.get('compliance_level', ''),
                'source_section': req.get('section', ''), 'text': req.get(
                'text', req.get('description', ''))}
            doc_info['obligations'].append(obligation)
    controls = data.get('controls', [])
    for control in controls:
        if isinstance(control, dict):
            obligation = {'type': 'control', 'id': control.get('id', ''),
                'title': control.get('title', control.get('name', '')),
                'description': control.get('description', ''), 'category':
                control.get('category', control.get('type', '')),
                'compliance_level': control.get('compliance_level',
                'mandatory'), 'source_section': control.get('section', ''),
                'text': control.get('text', control.get('description', ''))}
            doc_info['obligations'].append(obligation)
    penalties = data.get('penalties', [])
    for penalty in penalties:
        if isinstance(penalty, dict):
            obligation = {'type': 'penalty_based', 'id': penalty.get('id',
                ''), 'title': penalty.get('violation', penalty.get('title',
                '')), 'description':
                f"Violation: {penalty.get('violation', '')}", 'category':
                penalty.get('category', 'enforcement'), 'compliance_level':
                'mandatory', 'penalty_amount': penalty.get('amount', ''),
                'source_section': penalty.get('section', ''), 'text':
                penalty.get('description', penalty.get('violation', ''))}
            if obligation['title'] or obligation['text']:
                doc_info['obligations'].append(obligation)
    return doc_info


def main() ->None:
    """Extract all obligations from UK regulatory documents."""
    cache_dir = Path('/home/omar/Documents/ruleIQ/data/regulation_cache')
    uk_files = sorted(cache_dir.glob('uk_*.json'))
    logger.info('Found %s UK regulatory documents' % len(uk_files))
    all_obligations = []
    regulation_map = {}
    for doc_path in uk_files:
        logger.info('\nProcessing: %s' % doc_path.name)
        doc_info = extract_obligations_from_document(doc_path)
        metadata = doc_info.get('metadata', {})
        reg_type = metadata.get('regulation', metadata.get('type', 'unknown'))
        if reg_type not in regulation_map:
            regulation_map[reg_type] = {'documents': [], 'obligations': [],
                'count': 0}
        regulation_map[reg_type]['documents'].append(doc_path.name)
        regulation_map[reg_type]['obligations'].extend(doc_info['obligations'])
        regulation_map[reg_type]['count'] += len(doc_info['obligations'])
        all_obligations.extend(doc_info['obligations'])
        logger.info('  - Extracted %s obligations' % len(doc_info[
            'obligations']))
        print(f"  - URL: {doc_info['url'][:80]}..." if doc_info['url'] else
            '  - No URL')
    unique_obligations = []
    seen_hashes = set()
    for obl in all_obligations:
        obl_text = f"{obl['title']}_{obl['text']}_{obl['type']}"
        obl_hash = hashlib.md5(obl_text.encode()).hexdigest()
        if obl_hash not in seen_hashes:
            seen_hashes.add(obl_hash)
            obl['obligation_id'] = f'UK-OBL-{len(unique_obligations) + 1:04d}'
            unique_obligations.append(obl)
    summary = {'extraction_date': datetime.now().isoformat(),
        'total_documents': len(uk_files), 'total_raw_obligations': len(
        all_obligations), 'unique_obligations': len(unique_obligations),
        'by_type': {}, 'by_regulation': regulation_map, 'obligations':
        unique_obligations}
    for obl in unique_obligations:
        obl_type = obl['type']
        if obl_type not in summary['by_type']:
            summary['by_type'][obl_type] = 0
        summary['by_type'][obl_type] += 1
    output_path = Path(
        '/home/omar/Documents/ruleIQ/data/manifests/uk_obligations_extracted.json',
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    logger.info('\n' + '=' * 80)
    logger.info('EXTRACTION SUMMARY')
    logger.info('=' * 80)
    logger.info('Total documents processed: %s' % len(uk_files))
    logger.info('Total raw obligations found: %s' % len(all_obligations))
    logger.info('Unique obligations identified: %s' % len(unique_obligations))
    logger.info('\nBy type:')
    for obl_type, count in summary['by_type'].items():
        logger.info('  - %s: %s' % (obl_type, count))
    logger.info('\nBy regulation:')
    for reg_type, info in regulation_map.items():
        print(
            f"  - {reg_type}: {info['count']} obligations from {len(info['documents'])} documents",
            )
    logger.info('\nOutput saved to: %s' % output_path)
    if unique_obligations:
        logger.info('\n' + '=' * 80)
        logger.info('SAMPLE OBLIGATIONS (first 5)')
        logger.info('=' * 80)
        for i, obl in enumerate(unique_obligations[:5], 1):
            logger.info('\n%s. %s' % (i, obl['obligation_id']))
            logger.info('   Type: %s' % obl['type'])
            logger.info('   Title: %s...' % obl['title'][:100])
            logger.info('   Text: %s...' % obl['text'][:150])


if __name__ == '__main__':
    main()
