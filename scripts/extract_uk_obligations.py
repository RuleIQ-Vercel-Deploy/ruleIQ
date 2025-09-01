#!/usr/bin/env python3
"""
Extract all UK regulatory obligations from cached documents.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import hashlib

def extract_obligations_from_document(doc_path: Path) -> Dict[str, Any]:
    """Extract obligations from a single document."""
    with open(doc_path, 'r') as f:
        data = json.load(f)
    
    doc_info = {
        'file': doc_path.name,
        'url': data.get('url', ''),
        'fetched_at': data.get('fetched_at', ''),
        'metadata': data.get('metadata', {}),
        'obligations': []
    }
    
    # Extract from requirements section
    requirements = data.get('requirements', [])
    for req in requirements:
        if isinstance(req, dict):
            obligation = {
                'type': 'requirement',
                'id': req.get('id', ''),
                'title': req.get('title', ''),
                'description': req.get('description', ''),
                'category': req.get('category', ''),
                'compliance_level': req.get('compliance_level', ''),
                'source_section': req.get('section', ''),
                'text': req.get('text', req.get('description', ''))
            }
            doc_info['obligations'].append(obligation)
    
    # Extract from controls section
    controls = data.get('controls', [])
    for control in controls:
        if isinstance(control, dict):
            obligation = {
                'type': 'control',
                'id': control.get('id', ''),
                'title': control.get('title', control.get('name', '')),
                'description': control.get('description', ''),
                'category': control.get('category', control.get('type', '')),
                'compliance_level': control.get('compliance_level', 'mandatory'),
                'source_section': control.get('section', ''),
                'text': control.get('text', control.get('description', ''))
            }
            doc_info['obligations'].append(obligation)
    
    # Extract from penalties section (these indicate obligations)
    penalties = data.get('penalties', [])
    for penalty in penalties:
        if isinstance(penalty, dict):
            obligation = {
                'type': 'penalty_based',
                'id': penalty.get('id', ''),
                'title': penalty.get('violation', penalty.get('title', '')),
                'description': f"Violation: {penalty.get('violation', '')}",
                'category': penalty.get('category', 'enforcement'),
                'compliance_level': 'mandatory',
                'penalty_amount': penalty.get('amount', ''),
                'source_section': penalty.get('section', ''),
                'text': penalty.get('description', penalty.get('violation', ''))
            }
            if obligation['title'] or obligation['text']:
                doc_info['obligations'].append(obligation)
    
    return doc_info

def main():
    """Extract all obligations from UK regulatory documents."""
    cache_dir = Path('/home/omar/Documents/ruleIQ/data/regulation_cache')
    uk_files = sorted(cache_dir.glob('uk_*.json'))
    
    print(f"Found {len(uk_files)} UK regulatory documents")
    
    all_obligations = []
    regulation_map = {}
    
    for doc_path in uk_files:
        print(f"\nProcessing: {doc_path.name}")
        doc_info = extract_obligations_from_document(doc_path)
        
        # Map to regulation type based on metadata or content
        metadata = doc_info.get('metadata', {})
        reg_type = metadata.get('regulation', metadata.get('type', 'unknown'))
        
        if reg_type not in regulation_map:
            regulation_map[reg_type] = {
                'documents': [],
                'obligations': [],
                'count': 0
            }
        
        regulation_map[reg_type]['documents'].append(doc_path.name)
        regulation_map[reg_type]['obligations'].extend(doc_info['obligations'])
        regulation_map[reg_type]['count'] += len(doc_info['obligations'])
        
        all_obligations.extend(doc_info['obligations'])
        
        print(f"  - Extracted {len(doc_info['obligations'])} obligations")
        print(f"  - URL: {doc_info['url'][:80]}..." if doc_info['url'] else "  - No URL")
    
    # Generate unique obligations (remove duplicates)
    unique_obligations = []
    seen_hashes = set()
    
    for obl in all_obligations:
        # Create hash from key fields
        obl_text = f"{obl['title']}_{obl['text']}_{obl['type']}"
        obl_hash = hashlib.md5(obl_text.encode()).hexdigest()
        
        if obl_hash not in seen_hashes:
            seen_hashes.add(obl_hash)
            # Assign unique ID
            obl['obligation_id'] = f"UK-OBL-{len(unique_obligations)+1:04d}"
            unique_obligations.append(obl)
    
    # Create summary
    summary = {
        'extraction_date': datetime.now().isoformat(),
        'total_documents': len(uk_files),
        'total_raw_obligations': len(all_obligations),
        'unique_obligations': len(unique_obligations),
        'by_type': {},
        'by_regulation': regulation_map,
        'obligations': unique_obligations
    }
    
    # Count by type
    for obl in unique_obligations:
        obl_type = obl['type']
        if obl_type not in summary['by_type']:
            summary['by_type'][obl_type] = 0
        summary['by_type'][obl_type] += 1
    
    # Save extracted obligations
    output_path = Path('/home/omar/Documents/ruleIQ/data/manifests/uk_obligations_extracted.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"Total documents processed: {len(uk_files)}")
    print(f"Total raw obligations found: {len(all_obligations)}")
    print(f"Unique obligations identified: {len(unique_obligations)}")
    print(f"\nBy type:")
    for obl_type, count in summary['by_type'].items():
        print(f"  - {obl_type}: {count}")
    print(f"\nBy regulation:")
    for reg_type, info in regulation_map.items():
        print(f"  - {reg_type}: {info['count']} obligations from {len(info['documents'])} documents")
    print(f"\nOutput saved to: {output_path}")
    
    # Show sample obligations
    if unique_obligations:
        print("\n" + "="*80)
        print("SAMPLE OBLIGATIONS (first 5)")
        print("="*80)
        for i, obl in enumerate(unique_obligations[:5], 1):
            print(f"\n{i}. {obl['obligation_id']}")
            print(f"   Type: {obl['type']}")
            print(f"   Title: {obl['title'][:100]}...")
            print(f"   Text: {obl['text'][:150]}...")

if __name__ == "__main__":
    main()