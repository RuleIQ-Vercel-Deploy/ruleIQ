#!/usr/bin/env python3
"""
Extract official ISO metadata for SMB-relevant standards.
This uses REAL ISO Open Data, not website summaries.
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def extract_iso_metadata():
    """Extract official ISO metadata from ISO Open Data."""
    
    # SMB-relevant ISO standards to extract
    target_standards = {
        "ISO/IEC 27001:2022": "Information security management systems",
        "ISO 9001:2015": "Quality management systems",
        "ISO 14001:2015": "Environmental management systems", 
        "ISO 31000:2018": "Risk management",
        "ISO/IEC 20000-1:2018": "IT Service management",
        "ISO 37301:2021": "Compliance management systems"
    }
    
    # Path to ISO metadata CSV
    csv_path = Path("/home/omar/Documents/ruleIQ/data/iso_metadata/iso_deliverables_metadata.csv")
    
    extracted_standards = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            reference = row.get('reference', '')
            
            # Check if this is one of our target standards
            for std_ref, std_type in target_standards.items():
                if reference == std_ref:
                    print(f"\nFound official metadata for {std_ref}")
                    
                    # Extract comprehensive metadata
                    extracted_standards[std_ref] = {
                        "id": row.get('id'),
                        "reference": reference,
                        "title_en": row.get('title.en', ''),
                        "title_fr": row.get('title.fr', ''),
                        "type": std_type,
                        "publication_date": row.get('publicationDate', ''),
                        "edition": row.get('edition', ''),
                        "ics_codes": eval(row.get('icsCode', '[]')) if row.get('icsCode') else [],
                        "owner_committee": row.get('ownerCommittee', ''),
                        "number_of_pages": row.get('numberOfPages', ''),
                        "abstract": row.get('abstract', ''),
                        "stage": row.get('stage', ''),
                        "stage_date": row.get('stageDate', ''),
                        "deliverable_type": row.get('deliverableType', ''),
                        "languages": eval(row.get('languages', '[]')) if row.get('languages') else []
                    }
                    
                    # Print key information
                    print(f"  Title: {row.get('title.en', '')[:100]}...")
                    print(f"  Publication Date: {row.get('publicationDate', '')}")
                    print(f"  Edition: {row.get('edition', '')}")
                    print(f"  Owner Committee: {row.get('ownerCommittee', '')}")
                    if row.get('abstract'):
                        print(f"  Abstract available: {len(row.get('abstract', ''))} characters")
    
    # Create comprehensive manifest
    manifest = {
        "title": "Official ISO Standards Metadata for SMBs",
        "source": "ISO Open Data (https://www.iso.org/open-data.html)",
        "license": "ODC Attribution License (ODC-By) v1.0",
        "extraction_date": datetime.now().isoformat(),
        "total_standards": len(extracted_standards),
        "standards": extracted_standards,
        "data_integrity": {
            "source_type": "Official ISO metadata",
            "verification": "Direct from ISO Open Data CSV",
            "authenticity": "100% - Official ISO source"
        }
    }
    
    # Save manifest
    manifest_path = Path("/home/omar/Documents/ruleIQ/data/manifests/official_iso_metadata.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n{'='*80}")
    print("OFFICIAL ISO METADATA EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"Extracted {len(extracted_standards)} standards from official ISO Open Data")
    print(f"Manifest saved to: {manifest_path}")
    
    # Also search for related/supporting standards
    print("\n" + "="*80)
    print("SEARCHING FOR RELATED STANDARDS")
    print("="*80)
    
    # Search for related standards
    related_keywords = ["27002", "27005", "9004", "14004", "31010", "20000-2", "37002", "19011"]
    related_standards = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            reference = row.get('reference', '')
            for keyword in related_keywords:
                if keyword in reference and "IS" in row.get('deliverableType', ''):
                    if reference not in related_standards:
                        related_standards[reference] = {
                            "reference": reference,
                            "title": row.get('title.en', ''),
                            "publication_date": row.get('publicationDate', ''),
                            "related_to": keyword
                        }
    
    if related_standards:
        print("\nFound related/supporting standards:")
        for ref, info in related_standards.items():
            print(f"  - {ref}: {info['title'][:80]}...")
    
    return manifest

if __name__ == "__main__":
    extract_iso_metadata()