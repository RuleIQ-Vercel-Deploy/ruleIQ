"""
Compliance service for framework management and assessment processing.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from uuid import UUID
from pydantic import BaseModel


class ComplianceScore(BaseModel):
    """Model for compliance score results."""
    percentage: float
    compliant_count: int
    total_count: int
    weighted: bool = False


class ComplianceGap(BaseModel):
    """Model for identified compliance gaps."""
    requirement_id: str
    title: str
    description: str
    severity: str


class FrameworkRequirement(BaseModel):
    """Model for compliance framework requirements."""
    id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    risk_level: Optional[str] = None
    effort: Optional[str] = None


class AssessmentResponse(BaseModel):
    """Model for assessment response data."""
    compliant: bool
    evidence: List[str] = []
    notes: Optional[str] = None
    validated_by: Optional[str] = None


class ComplianceService:
    """Service for managing compliance assessments and frameworks."""
    
    def __init__(self, db_session=None):
        """Initialize compliance service with database session."""
        self.db = db_session
    
    async def calculate_compliance_score(
        self,
        responses: Dict[str, Any],
        total_requirements: int
    ) -> ComplianceScore:
        """Calculate overall compliance score from assessment responses."""
        compliant_count = sum(
            1 for r in responses.values() 
            if r.get('compliant', False)
        )
        percentage = (compliant_count / total_requirements) * 100 if total_requirements > 0 else 0
        
        return ComplianceScore(
            percentage=percentage,
            compliant_count=compliant_count,
            total_count=total_requirements,
            weighted=False
        )
    
    async def calculate_weighted_score(self, responses: Dict[str, Any]) -> ComplianceScore:
        """Calculate weighted compliance score."""
        total_weight = sum(r.get('weight', 1) for r in responses.values())
        compliant_weight = sum(
            r.get('weight', 1) for r in responses.values()
            if r.get('compliant', False)
        )
        percentage = (compliant_weight / total_weight) * 100 if total_weight > 0 else 0
        
        return ComplianceScore(
            percentage=percentage,
            compliant_count=compliant_weight,
            total_count=total_weight,
            weighted=True
        )
    
    async def identify_gaps(
        self,
        requirements: List[Dict],
        responses: Dict[str, Any]
    ) -> List[ComplianceGap]:
        """Identify compliance gaps from assessment responses."""
        gaps = []
        for req in requirements:
            req_id = req.get('id')
            if req_id and not responses.get(req_id, {}).get('compliant', False):
                gaps.append(ComplianceGap(
                    requirement_id=req_id,
                    title=req.get('title', ''),
                    description=req.get('description', ''),
                    severity=req.get('priority', 'medium')
                ))
        return gaps
    
    async def generate_recommendations(self, gaps: List[ComplianceGap]) -> List[str]:
        """Generate recommendations based on identified gaps."""
        recommendations = []
        for gap in gaps:
            if 'breach' in gap.title.lower() or 'breach' in gap.description.lower():
                recommendations.append(f"Implement breach notification process for {gap.requirement_id}")
            if 'minimization' in gap.title.lower() or 'minimization' in gap.description.lower():
                recommendations.append(f"Implement data minimization controls for {gap.requirement_id}")
            if gap.severity == 'critical':
                recommendations.append(f"Prioritize immediate remediation of {gap.requirement_id}")
        return recommendations
    
    async def create_assessment(
        self,
        framework_id: int,
        business_id: str,
        user_id: str
    ) -> Any:
        """Create a new compliance assessment."""
        # Stub implementation
        class Assessment:
            def __init__(self):
                self.id = str(UUID(int=1))
                self.framework_id = framework_id
                self.business_id = business_id
                self.user_id = user_id
                self.responses = {}
                self.total_requirements = 3
        
        return Assessment()
    
    async def update_response(
        self,
        assessment_id: str,
        requirement_id: str,
        response: AssessmentResponse
    ) -> bool:
        """Update an assessment response."""
        # Stub implementation
        return True
    
    async def validate_evidence(
        self,
        evidence_files: List[Dict]
    ) -> tuple[List[Dict], List[Dict]]:
        """Validate evidence files."""
        valid = []
        invalid = []
        
        for file in evidence_files:
            if file.get('type') == 'application/x-executable':
                invalid.append(file)
            else:
                valid.append(file)
        
        return valid, invalid
    
    async def get_framework_requirements(self, framework_id: int) -> List:
        """Get requirements for a framework."""
        # Stub implementation
        return [
            type('Requirement', (), {'id': 'REQ-1', 'title': 'Requirement 1'}),
            type('Requirement', (), {'id': 'REQ-2', 'title': 'Requirement 2'})
        ]
    
    async def get_assessment(self, assessment_id: str) -> Any:
        """Get assessment by ID."""
        # Stub implementation
        class Assessment:
            def __init__(self):
                self.responses = {'REQ-1': {'compliant': True}, 'REQ-2': {'compliant': True}}
                self.total_requirements = 2
        return Assessment()
    
    async def complete_assessment(self, assessment_id: str) -> Dict:
        """Mark assessment as complete."""
        assessment = await self.get_assessment(assessment_id)
        score = await self.calculate_compliance_score(
            assessment.responses,
            assessment.total_requirements
        )
        return {
            'status': 'completed',
            'score': {'percentage': score.percentage}
        }
    
    async def export_report(
        self,
        assessment_data: Dict,
        format: str = 'json'
    ) -> Dict:
        """Export assessment report."""
        return {
            'assessment_id': assessment_data.get('id'),
            'compliance_score': assessment_data.get('score', {}).get('percentage', 0),
            'gaps': assessment_data.get('gaps', [])
        }
    
    async def benchmark_score(
        self,
        score: float,
        industry: str
    ) -> Dict:
        """Benchmark score against industry average."""
        industry_average = 72.5  # Stub value
        return {
            'user_score': score,
            'industry_average': industry_average,
            'above_average': score > industry_average
        }
    
    async def get_assessment_history(
        self,
        business_id: str,
        limit: int = 10
    ) -> List:
        """Get assessment history for a business."""
        # Stub implementation
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        
        class HistoryItem:
            def __init__(self, days_ago, score):
                self.id = str(UUID(int=days_ago))
                self.created_at = now - timedelta(days=days_ago)
                self.score = score
        
        return [
            HistoryItem(30, 65.0),
            HistoryItem(15, 75.0),
            HistoryItem(0, 85.0)
        ]
    
    async def analyze_trends(self, history: List[Dict]) -> Dict:
        """Analyze compliance trends."""
        scores = [h.get('score', 0) for h in history]
        avg_improvement = sum(scores[i] - scores[i-1] for i in range(1, len(scores))) / max(len(scores) - 1, 1)
        
        return {
            'overall_trend': 'improving' if avg_improvement > 0 else 'declining',
            'average_improvement': avg_improvement,
            'forecast': scores[-1] + avg_improvement if scores else 0
        }
    
    async def prioritize_requirements(
        self,
        requirements: List[FrameworkRequirement]
    ) -> List[FrameworkRequirement]:
        """Prioritize requirements by risk and effort."""
        # Sort by risk_level (critical first) then by effort (low first)
        risk_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        effort_order = {'low': 0, 'medium': 1, 'high': 2}
        
        return sorted(
            requirements,
            key=lambda r: (
                risk_order.get(r.risk_level, 4),
                effort_order.get(r.effort, 3)
            )
        )
    
    async def map_evidence_to_requirements(
        self,
        evidence_files: List[Dict],
        requirements: List[Dict]
    ) -> Dict[str, List[str]]:
        """Map evidence files to requirements."""
        mapping = {}
        
        for req in requirements:
            req_id = req.get('id')
            keywords = req.get('keywords', [])
            mapping[req_id] = []
            
            for file in evidence_files:
                file_name = file.get('name', '')
                file_tags = file.get('tags', [])
                
                # Check if any keyword matches file name or tags
                for keyword in keywords:
                    if keyword.lower() in file_name.lower() or keyword.lower() in [t.lower() for t in file_tags]:
                        mapping[req_id].append(file_name)
                        break
        
        return mapping