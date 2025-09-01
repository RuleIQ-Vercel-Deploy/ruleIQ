#!/usr/bin/env python3
"""
Categorize and map UK regulatory obligations to specific regulations.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Regulation mapping based on URLs and content patterns
REGULATION_PATTERNS = {
    'GDPR/DPA': [
        r'data.?protection',
        r'gdpr',
        r'ukpga/2018/12',  # Data Protection Act 2018
        r'personal.?data',
        r'privacy'
    ],
    'FCA': [
        r'financial.?conduct',
        r'fca',
        r'financial.?services',
        r'ukpga/2000/8',  # Financial Services and Markets Act 2000
        r'consumer.?credit',
        r'ukpga/2021/22',  # Financial Services Act 2021
    ],
    'MLR': [
        r'money.?laundering',
        r'uksi/2017/692',  # Money Laundering Regulations 2017
        r'anti.?money',
        r'aml',
        r'terrorist.?financing'
    ],
    'Bribery Act': [
        r'bribery',
        r'ukpga/2010/23',  # Bribery Act 2010
        r'corruption',
        r'anti.?bribery'
    ],
    'Modern Slavery Act': [
        r'modern.?slavery',
        r'ukpga/2015/30',  # Modern Slavery Act 2015
        r'human.?trafficking',
        r'forced.?labour'
    ],
    'Companies Act': [
        r'companies.?act',
        r'ukpga/2006/46',  # Companies Act 2006
        r'corporate.?governance',
        r'director.?duties'
    ],
    'Equality Act': [
        r'equality',
        r'ukpga/2010/15',  # Equality Act 2010
        r'discrimination',
        r'equal.?opportunities'
    ],
    'HSWA': [
        r'health.?safety',
        r'hswa',
        r'workplace.?safety',
        r'occupational.?health'
    ],
    'PECR': [
        r'privacy.?electronic',
        r'pecr',
        r'electronic.?communications',
        r'uksi/2003/2426'  # Privacy and Electronic Communications Regulations
    ],
    'NIS': [
        r'network.?information',
        r'uksi/2018/506',  # NIS Regulations 2018
        r'cyber.?security',
        r'critical.?infrastructure'
    ],
    'MiFID II': [
        r'mifid',
        r'eur/2014/600',  # MiFID II
        r'eur/2014/596',  # MAR
        r'markets.?financial',
        r'investment.?services'
    ],
    'EMIR': [
        r'emir',
        r'eur/2012/648',  # EMIR
        r'derivatives',
        r'clearing.?obligations'
    ],
    'SFTR': [
        r'securities.?financing',
        r'eur/2015/2365',  # SFTR
        r'sftr',
        r'securities.?lending'
    ],
    'Prospectus': [
        r'prospectus',
        r'eur/2017/1129',  # Prospectus Regulation
        r'securities.?offerings',
        r'public.?offerings'
    ],
    'Benchmarks': [
        r'benchmark',
        r'eur/2016/1011',  # Benchmarks Regulation
        r'libor',
        r'reference.?rates'
    ],
    'Competition Act': [
        r'competition',
        r'ukpga/1998/41',  # Competition Act 1998
        r'anti.?competitive',
        r'monopoly'
    ],
    'Enterprise Act': [
        r'enterprise',
        r'ukpga/2002/40',  # Enterprise Act 2002
        r'merger.?control',
        r'market.?investigation'
    ],
    'Criminal Justice Act': [
        r'criminal.?justice',
        r'ukpga/2017/22',  # Criminal Finances Act 2017
        r'tax.?evasion',
        r'criminal.?finances'
    ],
    'Proceeds of Crime': [
        r'proceeds.?crime',
        r'ukpga/2002/29',  # Proceeds of Crime Act 2002
        r'asset.?recovery',
        r'confiscation'
    ],
    'Terrorism Act': [
        r'terrorism',
        r'ukpga/2006/35',  # Terrorism Act 2006
        r'counter.?terrorism',
        r'terrorist.?financing'
    ],
    'Pensions Act': [
        r'pensions',
        r'ukpga/2015/4',  # Pensions Schemes Act 2015
        r'retirement.?benefits',
        r'pension.?schemes'
    ],
    'Building Safety Act': [
        r'building.?safety',
        r'ukpga/2022/10',  # Building Safety Act 2022
        r'fire.?safety',
        r'construction.?safety'
    ],
    'Environment Act': [
        r'environment',
        r'ukpga/2021/31',  # Environment Act 2021
        r'environmental.?protection',
        r'pollution.?control'
    ],
    'Online Safety Act': [
        r'online.?safety',
        r'ukpga/2023/50',  # Online Safety Act 2023
        r'harmful.?content',
        r'social.?media.?regulation'
    ],
    'Economic Crime Act': [
        r'economic.?crime',
        r'ukpga/2022/46',  # Economic Crime Act 2022
        r'corporate.?transparency',
        r'beneficial.?ownership'
    ]
}

def identify_regulation(doc_data: Dict[str, Any], file_name: str) -> str:
    """Identify which regulation a document belongs to."""
    url = doc_data.get('url', '')
    metadata = doc_data.get('metadata', {})
    requirements = doc_data.get('requirements', [])
    
    # Combine text for analysis
    text_to_analyze = f"{url} {json.dumps(metadata)} {json.dumps(requirements[:5])}"
    text_lower = text_to_analyze.lower()
    
    # Check each regulation pattern
    for reg_name, patterns in REGULATION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return reg_name
    
    # Fallback: Try to extract from URL
    if 'ukpga' in url:
        year_match = re.search(r'ukpga/(\d{4})/(\d+)', url)
        if year_match:
            return f"UK Act {year_match.group(1)}/{year_match.group(2)}"
    elif 'uksi' in url:
        year_match = re.search(r'uksi/(\d{4})/(\d+)', url)
        if year_match:
            return f"UK SI {year_match.group(1)}/{year_match.group(2)}"
    elif 'eur' in url:
        year_match = re.search(r'eur/(\d{4})/(\d+)', url)
        if year_match:
            return f"EU Reg {year_match.group(1)}/{year_match.group(2)}"
    
    return 'Other'

def main():
    """Categorize obligations by regulation type."""
    # Load extracted obligations
    extracted_path = Path('/home/omar/Documents/ruleIQ/data/manifests/uk_obligations_extracted.json')
    with open(extracted_path, 'r') as f:
        extracted_data = json.load(f)
    
    cache_dir = Path('/home/omar/Documents/ruleIQ/data/regulation_cache')
    
    # Map each document to a regulation
    doc_to_regulation = {}
    regulation_obligations = {}
    
    for doc_file in cache_dir.glob('uk_*.json'):
        with open(doc_file, 'r') as f:
            doc_data = json.load(f)
        
        regulation = identify_regulation(doc_data, doc_file.name)
        doc_to_regulation[doc_file.name] = regulation
        
        if regulation not in regulation_obligations:
            regulation_obligations[regulation] = {
                'name': regulation,
                'documents': [],
                'obligations': [],
                'urls': set(),
                'count': 0
            }
        
        regulation_obligations[regulation]['documents'].append(doc_file.name)
        if doc_data.get('url'):
            regulation_obligations[regulation]['urls'].add(doc_data['url'])
    
    # Re-process obligations with regulation mapping
    all_obligations = []
    
    for doc_file in cache_dir.glob('uk_*.json'):
        with open(doc_file, 'r') as f:
            doc_data = json.load(f)
        
        regulation = doc_to_regulation[doc_file.name]
        
        # Extract obligations with regulation tagging
        requirements = doc_data.get('requirements', [])
        for i, req in enumerate(requirements):
            if isinstance(req, dict):
                obligation = {
                    'regulation': regulation,
                    'type': 'requirement',
                    'id': f"{regulation}-REQ-{i+1:03d}",
                    'title': req.get('title', ''),
                    'description': req.get('description', ''),
                    'text': req.get('text', req.get('description', '')),
                    'category': req.get('category', ''),
                    'compliance_level': req.get('compliance_level', 'mandatory'),
                    'source_file': doc_file.name,
                    'source_url': doc_data.get('url', '')
                }
                all_obligations.append(obligation)
                regulation_obligations[regulation]['obligations'].append(obligation)
        
        regulation_obligations[regulation]['count'] = len(regulation_obligations[regulation]['obligations'])
    
    # Convert sets to lists for JSON serialization
    for reg in regulation_obligations.values():
        reg['urls'] = list(reg['urls'])
    
    # Select top obligations per regulation (aiming for ~108 total)
    selected_obligations = []
    target_per_regulation = 108 // len(regulation_obligations)
    
    for reg_name, reg_data in regulation_obligations.items():
        # Take up to target_per_regulation obligations from each
        selected = reg_data['obligations'][:target_per_regulation]
        selected_obligations.extend(selected)
    
    # If we have less than 108, add more from regulations with more obligations
    if len(selected_obligations) < 108:
        remaining = 108 - len(selected_obligations)
        for reg_name, reg_data in sorted(regulation_obligations.items(), 
                                        key=lambda x: x[1]['count'], 
                                        reverse=True):
            additional = reg_data['obligations'][target_per_regulation:target_per_regulation + remaining]
            selected_obligations.extend(additional)
            remaining -= len(additional)
            if remaining <= 0:
                break
    
    # Ensure we have exactly 108 obligations
    selected_obligations = selected_obligations[:108]
    
    # Create final manifest
    manifest = {
        'version': '2.0',
        'created_at': datetime.now().isoformat(),
        'total_obligations': len(selected_obligations),
        'regulations': {},
        'obligations': []
    }
    
    # Group selected obligations by regulation
    for obl in selected_obligations:
        reg = obl['regulation']
        if reg not in manifest['regulations']:
            manifest['regulations'][reg] = {
                'name': reg,
                'obligations': []
            }
        manifest['regulations'][reg]['obligations'].append(obl)
    
    manifest['obligations'] = selected_obligations
    
    # Save categorized manifest
    output_path = Path('/home/omar/Documents/ruleIQ/data/manifests/uk_compliance_manifest_complete.json')
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print("\n" + "="*80)
    print("CATEGORIZATION COMPLETE")
    print("="*80)
    print(f"Total obligations selected: {len(selected_obligations)}")
    print(f"\nBy regulation:")
    for reg_name, reg_data in sorted(manifest['regulations'].items()):
        print(f"  - {reg_name}: {len(reg_data['obligations'])} obligations")
    print(f"\nManifest saved to: {output_path}")
    
    # Save full analysis
    analysis_path = Path('/home/omar/Documents/ruleIQ/data/manifests/uk_regulations_analysis.json')
    with open(analysis_path, 'w') as f:
        json.dump({
            'document_to_regulation': doc_to_regulation,
            'regulation_summary': {k: {
                'name': v['name'],
                'document_count': len(v['documents']),
                'total_obligations': v['count'],
                'urls': v['urls']
            } for k, v in regulation_obligations.items()}
        }, f, indent=2)
    
    print(f"Full analysis saved to: {analysis_path}")

if __name__ == "__main__":
    main()