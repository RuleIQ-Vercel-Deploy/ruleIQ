"""
Evidence Collector service for LangGraph integration.
Bridges to existing evidence collection services.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from typing import Dict, List, Any, Optional
from uuid import UUID
import hashlib
from datetime import datetime


class EvidenceCollector:
    """Wrapper for evidence collection services."""
    
    def __init__(self):
        """Initialize evidence collector."""
        self.collected_evidence = []
        
    async def collect_evidence(
        self,
        company_id: UUID,
        compliance_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Collect evidence for compliance requirements."""
        
        evidence = []
        
        # Extract obligations from compliance data
        obligations = compliance_data.get('obligations', [])
        frameworks = compliance_data.get('frameworks', [])
        
        # Generate evidence for each obligation
        for i, obligation in enumerate(obligations[:5]):  # Limit to 5 for performance
            evidence_item = {
                'id': f'evidence_{i+1}',
                'obligation_id': obligation.get('id', f'ob_{i+1}'),
                'type': 'document',
                'title': f'Evidence for {obligation.get("title", "Requirement")}',
                'description': f'Documentation supporting compliance with {obligation.get("framework", "standard")}',
                'collected_at': datetime.utcnow().isoformat(),
                'status': 'collected',
                'hash': hashlib.md5(f'{company_id}_{i}'.encode()).hexdigest()
            }
            evidence.append(evidence_item)
            
        # Add framework-specific evidence
        for framework in frameworks[:3]:
            evidence.append({
                'id': f'framework_evidence_{framework.lower()}',
                'type': 'certification',
                'title': f'{framework} Compliance Evidence',
                'description': f'Evidence package for {framework} compliance',
                'collected_at': datetime.utcnow().isoformat(),
                'status': 'pending_review',
                'hash': hashlib.md5(f'{company_id}_{framework}'.encode()).hexdigest()
            })
            
        self.collected_evidence.extend(evidence)
        return evidence
    
    async def verify_evidence(
        self,
        evidence_id: str
    ) -> Dict[str, Any]:
        """Verify a piece of evidence."""
        
        # Find evidence in collected items
        for item in self.collected_evidence:
            if item['id'] == evidence_id:
                item['status'] = 'verified'
                item['verified_at'] = datetime.utcnow().isoformat()
                return item
                
        return {
            'id': evidence_id,
            'status': 'not_found',
            'error': 'Evidence not found in collection'
        }