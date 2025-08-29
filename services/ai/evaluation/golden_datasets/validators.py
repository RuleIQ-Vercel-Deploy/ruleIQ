"""Deep validation for golden datasets."""
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel
import warnings


# Authoritative domains allow-list
AUTHORITATIVE_DOMAINS = {
    'eur-lex.europa.eu',
    'ico.org.uk', 
    'hhs.gov',
    'govinfo.gov',
    'csrc.nist.gov',
    'nist.gov',
    'pages.nist.gov',
    'pcisecuritystandards.org',
    'attack.mitre.org',
    'cisecurity.org',
    'cppa.ca.gov',
    'leginfo.legislature.ca.gov'
}

# Known frameworks seed set
KNOWN_FRAMEWORKS = {
    'GDPR', 'UK GDPR', 'HIPAA', 'SOX', 'DSA', 'AI Act', 'DORA', 
    'PSD2', 'MiCA', 'NIST 800-53', 'NIST 800-37', 'NIST 800-30',
    'NIST 800-39', 'NIST 800-171', 'ZTA', 'ABAC', 'ISO27001',
    'SOC2', 'CSA CCM', 'PCI DSS'
}


class DeepValidator:
    """Multi-layer validation for golden datasets."""
    
    def validate(self, dataset: List[BaseModel]) -> Dict[str, Any]:
        """Run all validation layers.
        
        Returns:
            Dictionary with validation results per layer
        """
        results = {
            'semantic': self._validate_semantic(dataset),
            'cross_ref': self._validate_cross_references(dataset),
            'regulatory': self._validate_regulatory_accuracy(dataset),
            'temporal': self._validate_temporal(dataset),
            'overall_valid': True,
            'warnings': []
        }
        
        # Set overall validity
        results['overall_valid'] = all([
            results['semantic']['valid'],
            results['cross_ref']['valid'],
            results['regulatory']['valid'],
            results['temporal']['valid']
        ])
        
        return results
    
    def _validate_semantic(self, dataset: List[BaseModel]) -> Dict[str, Any]:
        """Layer 1: Semantic validation - check required fields."""
        errors = []
        
        for item in dataset:
            # Check for required fields based on type
            if hasattr(item, 'regulation_refs'):
                if not item.regulation_refs:
                    errors.append(f"{item.id}: Missing regulation_refs")
                    
            if hasattr(item, 'triggers'):
                if not item.triggers:
                    errors.append(f"{item.id}: Missing triggers")
                    
            if hasattr(item, 'version'):
                if not item.version:
                    errors.append(f"{item.id}: Missing version")
                    
            if hasattr(item, 'source'):
                if not item.source:
                    errors.append(f"{item.id}: Missing source")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _validate_cross_references(self, dataset: List[BaseModel]) -> Dict[str, Any]:
        """Layer 2: Cross-reference validation."""
        errors = []
        obligation_ids = set()
        
        # Collect all obligation IDs
        for item in dataset:
            if hasattr(item, 'obligation_id'):
                obligation_ids.add(item.obligation_id)
        
        # Check evidence cases reference valid obligations
        for item in dataset:
            if hasattr(item, 'evidence_items'):
                # Evidence case should have valid obligation_id
                if hasattr(item, 'obligation_id') and item.obligation_id:
                    # In real scenario, check against obligation registry
                    pass  # Placeholder for cross-ref check
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'obligation_count': len(obligation_ids)
        }
    
    def _validate_regulatory_accuracy(self, dataset: List[BaseModel]) -> Dict[str, Any]:
        """Layer 3: Regulatory accuracy validation."""
        errors = []
        warnings = []
        
        for item in dataset:
            if hasattr(item, 'regulation_refs'):
                for ref in item.regulation_refs:
                    # Check framework is known
                    if ref.framework not in KNOWN_FRAMEWORKS:
                        warnings.append(
                            f"{item.id}: Unknown framework '{ref.framework}'"
                        )
                    
                    # Check URL host is in allow-list
                    if ref.url:
                        url_str = str(ref.url)
                        host = url_str.split('/')[2] if '//' in url_str else ''
                        if host and host not in AUTHORITATIVE_DOMAINS:
                            errors.append(
                                f"{item.id}: Non-authoritative URL host '{host}'"
                            )
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_temporal(self, dataset: List[BaseModel]) -> Dict[str, Any]:
        """Layer 4: Temporal validation."""
        errors = []
        warnings = []
        today = date.today()
        
        for item in dataset:
            if hasattr(item, 'temporal') and item.temporal:
                temporal = item.temporal
                
                # Check date order (already validated in model)
                if temporal.effective_to and temporal.effective_to < temporal.effective_from:
                    errors.append(
                        f"{item.id}: Invalid date range"
                    )
                
                # Warn if expired
                if temporal.effective_to and temporal.effective_to < today:
                    warnings.append(
                        f"{item.id}: Expired (ended {temporal.effective_to})"
                    )
                
                # Warn if not yet effective
                if temporal.effective_from > today:
                    warnings.append(
                        f"{item.id}: Not yet effective (starts {temporal.effective_from})"
                    )
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


class ExternalDataValidator:
    """Validate and score external data sources."""
    
    def score_trustworthiness(self, source_data: List[BaseModel], 
                            source_metadata: Dict[str, Any]) -> Dict[str, float]:
        """Calculate trust score for external data.
        
        Returns:
            Dictionary with subscores and overall trust score
        """
        scores = {
            'source_reputation': self._check_source_reputation(source_metadata),
            'data_freshness': self._check_data_age(source_metadata),
            'regulatory_alignment': self._check_regulatory_accuracy(source_data),
            'internal_consistency': self._check_consistency(source_data),
            'coverage_completeness': self._check_coverage(source_data)
        }
        
        # Calculate weighted average
        weights = {
            'source_reputation': 0.3,
            'data_freshness': 0.2,
            'regulatory_alignment': 0.2,
            'internal_consistency': 0.15,
            'coverage_completeness': 0.15
        }
        
        scores['overall'] = sum(
            scores[key] * weights[key] for key in weights
        )
        
        return scores
    
    def _check_source_reputation(self, metadata: Dict[str, Any]) -> float:
        """Check if source is from allow-listed domain."""
        domain = metadata.get('domain', '')
        if domain in AUTHORITATIVE_DOMAINS:
            return 1.0
        elif domain.endswith('.gov') or domain.endswith('.org'):
            return 0.7
        else:
            return 0.4
    
    def _check_data_age(self, metadata: Dict[str, Any]) -> float:
        """Score based on data freshness."""
        fetched_at = metadata.get('fetched_at')
        if not fetched_at:
            return 0.5
        
        if isinstance(fetched_at, str):
            fetched_at = datetime.fromisoformat(fetched_at)
        
        age = datetime.utcnow() - fetched_at
        
        if age <= timedelta(days=180):  # ≤6 months
            return 1.0
        elif age <= timedelta(days=365):  # 6-12 months
            return 0.8
        elif age <= timedelta(days=730):  # 12-24 months
            return 0.6
        else:
            return 0.4
    
    def _check_regulatory_accuracy(self, data: List[BaseModel]) -> float:
        """Check alignment with known frameworks."""
        if not data:
            return 0.0
        
        framework_count = 0
        total_refs = 0
        
        for item in data:
            if hasattr(item, 'regulation_refs'):
                for ref in item.regulation_refs:
                    total_refs += 1
                    if ref.framework in KNOWN_FRAMEWORKS:
                        framework_count += 1
        
        if total_refs == 0:
            return 0.0
        
        return framework_count / total_refs
    
    def _check_consistency(self, data: List[BaseModel]) -> float:
        """Check internal consistency of data."""
        if not data:
            return 0.0
        
        # Check for duplicate IDs
        ids = []
        for item in data:
            if hasattr(item, 'id'):
                ids.append(item.id)
        
        unique_ratio = len(set(ids)) / len(ids) if ids else 0
        
        # Check for required fields presence
        field_scores = []
        for item in data:
            score = 1.0
            if hasattr(item, 'version') and not item.version:
                score *= 0.8
            if hasattr(item, 'source') and not item.source:
                score *= 0.8
            field_scores.append(score)
        
        avg_field_score = sum(field_scores) / len(field_scores) if field_scores else 0
        
        return (unique_ratio + avg_field_score) / 2
    
    def _check_coverage(self, data: List[BaseModel]) -> float:
        """Check diversity of frameworks and jurisdictions."""
        if not data:
            return 0.0
        
        frameworks = set()
        jurisdictions = set()
        
        for item in data:
            if hasattr(item, 'regulation_refs'):
                for ref in item.regulation_refs:
                    frameworks.add(ref.framework)
                    # Extract jurisdiction from framework or metadata
                    if 'UK' in ref.framework:
                        jurisdictions.add('UK')
                    elif 'GDPR' in ref.framework:
                        jurisdictions.add('EU')
                    elif any(us in ref.framework for us in ['HIPAA', 'SOX', 'CCPA']):
                        jurisdictions.add('US')
        
        # Score based on diversity
        framework_score = min(len(frameworks) / 5, 1.0)  # 5+ frameworks = 1.0
        jurisdiction_score = min(len(jurisdictions) / 3, 1.0)  # 3+ jurisdictions = 1.0
        
        return (framework_score + jurisdiction_score) / 2