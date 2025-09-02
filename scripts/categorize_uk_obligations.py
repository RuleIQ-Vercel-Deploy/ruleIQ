"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Categorize and map UK regulatory obligations to specific regulations.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
REGULATION_PATTERNS = {'GDPR/DPA': ['data.?protection', 'gdpr',
    'ukpga/2018/12', 'personal.?data', 'privacy'], 'FCA': [
    'financial.?conduct', 'fca', 'financial.?services', 'ukpga/2000/8',
    'consumer.?credit', 'ukpga/2021/22'], 'MLR': ['money.?laundering',
    'uksi/2017/692', 'anti.?money', 'aml', 'terrorist.?financing'],
    'Bribery Act': ['bribery', 'ukpga/2010/23', 'corruption',
    'anti.?bribery'], 'Modern Slavery Act': ['modern.?slavery',
    'ukpga/2015/30', 'human.?trafficking', 'forced.?labour'],
    'Companies Act': ['companies.?act', 'ukpga/2006/46',
    'corporate.?governance', 'director.?duties'], 'Equality Act': [
    'equality', 'ukpga/2010/15', 'discrimination', 'equal.?opportunities'],
    'HSWA': ['health.?safety', 'hswa', 'workplace.?safety',
    'occupational.?health'], 'PECR': ['privacy.?electronic', 'pecr',
    'electronic.?communications', 'uksi/2003/2426'], 'NIS': [
    'network.?information', 'uksi/2018/506', 'cyber.?security',
    'critical.?infrastructure'], 'MiFID II': ['mifid', 'eur/2014/600',
    'eur/2014/596', 'markets.?financial', 'investment.?services'], 'EMIR':
    ['emir', 'eur/2012/648', 'derivatives', 'clearing.?obligations'],
    'SFTR': ['securities.?financing', 'eur/2015/2365', 'sftr',
    'securities.?lending'], 'Prospectus': ['prospectus', 'eur/2017/1129',
    'securities.?offerings', 'public.?offerings'], 'Benchmarks': [
    'benchmark', 'eur/2016/1011', 'libor', 'reference.?rates'],
    'Competition Act': ['competition', 'ukpga/1998/41', 'anti.?competitive',
    'monopoly'], 'Enterprise Act': ['enterprise', 'ukpga/2002/40',
    'merger.?control', 'market.?investigation'], 'Criminal Justice Act': [
    'criminal.?justice', 'ukpga/2017/22', 'tax.?evasion',
    'criminal.?finances'], 'Proceeds of Crime': ['proceeds.?crime',
    'ukpga/2002/29', 'asset.?recovery', 'confiscation'], 'Terrorism Act': [
    'terrorism', 'ukpga/2006/35', 'counter.?terrorism',
    'terrorist.?financing'], 'Pensions Act': ['pensions', 'ukpga/2015/4',
    'retirement.?benefits', 'pension.?schemes'], 'Building Safety Act': [
    'building.?safety', 'ukpga/2022/10', 'fire.?safety',
    'construction.?safety'], 'Environment Act': ['environment',
    'ukpga/2021/31', 'environmental.?protection', 'pollution.?control'],
    'Online Safety Act': ['online.?safety', 'ukpga/2023/50',
    'harmful.?content', 'social.?media.?regulation'], 'Economic Crime Act':
    ['economic.?crime', 'ukpga/2022/46', 'corporate.?transparency',
    'beneficial.?ownership']}


def identify_regulation(doc_data: Dict[str, Any], file_name: str) ->str:
    """Identify which regulation a document belongs to."""
    url = doc_data.get('url', '')
    metadata = doc_data.get('metadata', {})
    requirements = doc_data.get('requirements', [])
    text_to_analyze = (
        f'{url} {json.dumps(metadata)} {json.dumps(requirements[:5])}')
    text_lower = text_to_analyze.lower()
    for reg_name, patterns in REGULATION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return reg_name
    if 'ukpga' in url:
        year_match = re.search('ukpga/(\\d{4})/(\\d+)', url)
        if year_match:
            return f'UK Act {year_match.group(1)}/{year_match.group(2)}'
    elif 'uksi' in url:
        year_match = re.search('uksi/(\\d{4})/(\\d+)', url)
        if year_match:
            return f'UK SI {year_match.group(1)}/{year_match.group(2)}'
    elif 'eur' in url:
        year_match = re.search('eur/(\\d{4})/(\\d+)', url)
        if year_match:
            return f'EU Reg {year_match.group(1)}/{year_match.group(2)}'
    return 'Other'


def main() ->None:
    """Categorize obligations by regulation type."""
    extracted_path = Path(
        '/home/omar/Documents/ruleIQ/data/manifests/uk_obligations_extracted.json',
        )
    with open(extracted_path, 'r') as f:
        extracted_data = json.load(f)
    cache_dir = Path('/home/omar/Documents/ruleIQ/data/regulation_cache')
    doc_to_regulation = {}
    regulation_obligations = {}
    for doc_file in cache_dir.glob('uk_*.json'):
        with open(doc_file, 'r') as f:
            doc_data = json.load(f)
        regulation = identify_regulation(doc_data, doc_file.name)
        doc_to_regulation[doc_file.name] = regulation
        if regulation not in regulation_obligations:
            regulation_obligations[regulation] = {'name': regulation,
                'documents': [], 'obligations': [], 'urls': set(), 'count': 0}
        regulation_obligations[regulation]['documents'].append(doc_file.name)
        if doc_data.get('url'):
            regulation_obligations[regulation]['urls'].add(doc_data['url'])
    all_obligations = []
    for doc_file in cache_dir.glob('uk_*.json'):
        with open(doc_file, 'r') as f:
            doc_data = json.load(f)
        regulation = doc_to_regulation[doc_file.name]
        requirements = doc_data.get('requirements', [])
        for i, req in enumerate(requirements):
            if isinstance(req, dict):
                obligation = {'regulation': regulation, 'type':
                    'requirement', 'id': f'{regulation}-REQ-{i + 1:03d}',
                    'title': req.get('title', ''), 'description': req.get(
                    'description', ''), 'text': req.get('text', req.get(
                    'description', '')), 'category': req.get('category', ''
                    ), 'compliance_level': req.get('compliance_level',
                    'mandatory'), 'source_file': doc_file.name,
                    'source_url': doc_data.get('url', '')}
                all_obligations.append(obligation)
                regulation_obligations[regulation]['obligations'].append(
                    obligation)
        regulation_obligations[regulation]['count'] = len(
            regulation_obligations[regulation]['obligations'])
    for reg in regulation_obligations.values():
        reg['urls'] = list(reg['urls'])
    selected_obligations = []
    target_per_regulation = 108 // len(regulation_obligations)
    for reg_name, reg_data in regulation_obligations.items():
        selected = reg_data['obligations'][:target_per_regulation]
        selected_obligations.extend(selected)
    if len(selected_obligations) < 108:
        remaining = 108 - len(selected_obligations)
        for reg_name, reg_data in sorted(regulation_obligations.items(),
            key=lambda x: x[1]['count'], reverse=True):
            additional = reg_data['obligations'][target_per_regulation:
                target_per_regulation + remaining]
            selected_obligations.extend(additional)
            remaining -= len(additional)
            if remaining <= 0:
                break
    selected_obligations = selected_obligations[:108]
    manifest = {'version': '2.0', 'created_at': datetime.now().isoformat(),
        'total_obligations': len(selected_obligations), 'regulations': {},
        'obligations': []}
    for obl in selected_obligations:
        reg = obl['regulation']
        if reg not in manifest['regulations']:
            manifest['regulations'][reg] = {'name': reg, 'obligations': []}
        manifest['regulations'][reg]['obligations'].append(obl)
    manifest['obligations'] = selected_obligations
    output_path = Path(
        '/home/omar/Documents/ruleIQ/data/manifests/uk_compliance_manifest_complete.json',
        )
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    logger.info('\n' + '=' * 80)
    logger.info('CATEGORIZATION COMPLETE')
    logger.info('=' * 80)
    logger.info('Total obligations selected: %s' % len(selected_obligations))
    logger.info('\nBy regulation:')
    for reg_name, reg_data in sorted(manifest['regulations'].items()):
        logger.info('  - %s: %s obligations' % (reg_name, len(reg_data[
            'obligations'])))
    logger.info('\nManifest saved to: %s' % output_path)
    analysis_path = Path(
        '/home/omar/Documents/ruleIQ/data/manifests/uk_regulations_analysis.json',
        )
    with open(analysis_path, 'w') as f:
        json.dump({'document_to_regulation': doc_to_regulation,
            'regulation_summary': {k: {'name': v['name'], 'document_count':
            len(v['documents']), 'total_obligations': v['count'], 'urls': v
            ['urls']} for k, v in regulation_obligations.items()}}, f, indent=2,
            )
    logger.info('Full analysis saved to: %s' % analysis_path)


if __name__ == '__main__':
    main()
