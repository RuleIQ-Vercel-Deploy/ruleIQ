"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Extract official ISO metadata for SMB-relevant standards.
This uses REAL ISO Open Data, not website summaries.
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Any


def extract_iso_metadata() ->Any:
    """Extract official ISO metadata from ISO Open Data."""
    target_standards = {'ISO/IEC 27001:2022':
        'Information security management systems', 'ISO 9001:2015':
        'Quality management systems', 'ISO 14001:2015':
        'Environmental management systems', 'ISO 31000:2018':
        'Risk management', 'ISO/IEC 20000-1:2018': 'IT Service management',
        'ISO 37301:2021': 'Compliance management systems'}
    csv_path = Path(
        '/home/omar/Documents/ruleIQ/data/iso_metadata/iso_deliverables_metadata.csv',
        )
    extracted_standards = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            reference = row.get('reference', '')
            for std_ref, std_type in target_standards.items():
                if reference == std_ref:
                    logger.info('\nFound official metadata for %s' % std_ref)
                    extracted_standards[std_ref] = {'id': row.get('id'),
                        'reference': reference, 'title_en': row.get(
                        'title.en', ''), 'title_fr': row.get('title.fr', ''
                        ), 'type': std_type, 'publication_date': row.get(
                        'publicationDate', ''), 'edition': row.get(
                        'edition', ''), 'ics_codes': eval(row.get('icsCode',
                        '[]')) if row.get('icsCode') else [],
                        'owner_committee': row.get('ownerCommittee', ''),
                        'number_of_pages': row.get('numberOfPages', ''),
                        'abstract': row.get('abstract', ''), 'stage': row.
                        get('stage', ''), 'stage_date': row.get('stageDate',
                        ''), 'deliverable_type': row.get('deliverableType',
                        ''), 'languages': eval(row.get('languages', '[]')) if
                        row.get('languages') else []}
                    logger.info('  Title: %s...' % row.get('title.en', '')[
                        :100])
                    logger.info('  Publication Date: %s' % row.get(
                        'publicationDate', ''))
                    logger.info('  Edition: %s' % row.get('edition', ''))
                    logger.info('  Owner Committee: %s' % row.get(
                        'ownerCommittee', ''))
                    if row.get('abstract'):
                        print(
                            f"  Abstract available: {len(row.get('abstract', ''))} characters",
                            )
    manifest = {'title': 'Official ISO Standards Metadata for SMBs',
        'source': 'ISO Open Data (https://www.iso.org/open-data.html)',
        'license': 'ODC Attribution License (ODC-By) v1.0',
        'extraction_date': datetime.now().isoformat(), 'total_standards':
        len(extracted_standards), 'standards': extracted_standards,
        'data_integrity': {'source_type': 'Official ISO metadata',
        'verification': 'Direct from ISO Open Data CSV', 'authenticity':
        '100% - Official ISO source'}}
    manifest_path = Path(
        '/home/omar/Documents/ruleIQ/data/manifests/official_iso_metadata.json',
        )
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    logger.info('\n%s' % ('=' * 80))
    logger.info('OFFICIAL ISO METADATA EXTRACTION COMPLETE')
    logger.info('%s' % ('=' * 80))
    logger.info('Extracted %s standards from official ISO Open Data' % len(
        extracted_standards))
    logger.info('Manifest saved to: %s' % manifest_path)
    logger.info('\n' + '=' * 80)
    logger.info('SEARCHING FOR RELATED STANDARDS')
    logger.info('=' * 80)
    related_keywords = ['27002', '27005', '9004', '14004', '31010',
        '20000-2', '37002', '19011']
    related_standards = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            reference = row.get('reference', '')
            for keyword in related_keywords:
                if keyword in reference and 'IS' in row.get('deliverableType',
                    ''):
                    if reference not in related_standards:
                        related_standards[reference] = {'reference':
                            reference, 'title': row.get('title.en', ''),
                            'publication_date': row.get('publicationDate',
                            ''), 'related_to': keyword}
    if related_standards:
        logger.info('\nFound related/supporting standards:')
        for ref, info in related_standards.items():
            logger.info('  - %s: %s...' % (ref, info['title'][:80]))
    return manifest


if __name__ == '__main__':
    extract_iso_metadata()
