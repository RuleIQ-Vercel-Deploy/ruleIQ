"""
Report generation service for ComplianceGPT
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

# Import existing database models and services
from database.business_profile import BusinessProfile
from database.evidence_item import EvidenceItem
from database.compliance_framework import ComplianceFramework
from database.generated_policy import GeneratedPolicy
from database.readiness_assesment import ReadinessAssessment
from database.assessment_session import AssessmentSession
from services.evidence_service import get_user_evidence_items, get_evidence_dashboard_data
# from services.readiness_service import calculate_compliance_readiness
from core.business_profile import BusinessProfile as CoreBusinessProfile
from core.evidence_item import EvidenceItem as CoreEvidenceItem
from sqlalchemy_access import User


class ReportGenerator:
    """Generate compliance reports"""

    def __init__(self, db: Session):
        self.db = db

    async def generate_report(
        self,
        user: User,
        business_profile_id: UUID,
        report_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a report based on type and parameters"""
        profile = self.db.query(BusinessProfile).filter(
            BusinessProfile.id == business_profile_id
        ).first()

        if not profile:
            raise ValueError("Business profile not found")

        # Route to the appropriate data gathering method
        report_builders = {
            'executive_summary': self._generate_executive_summary,
            'compliance_status': self._generate_compliance_status,
            'gap_analysis': self._generate_gap_analysis,
            'evidence_report': self._generate_evidence_report,
            'audit_readiness': self._generate_audit_readiness,
            'control_matrix': self._generate_control_matrix,
            'risk_assessment': self._generate_risk_assessment,
        }
        
        builder = report_builders.get(report_type)
        if not builder:
            raise ValueError(f"Unknown report type: {report_type}")
            
        return await builder(user, profile, parameters)

    # --- Private Report Builder Methods ---

    async def _generate_executive_summary(
        self, user: User, profile: BusinessProfile, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate data for the executive summary report"""
        frameworks = parameters.get('frameworks', profile.existing_framew or [])
        period_days = parameters.get('period_days', 30)

        report_data = {
            'report_type': 'executive_summary',
            'generated_at': datetime.utcnow().isoformat(),
            'business_profile': {
                'name': profile.company_name, 
                'industry': profile.industry,
                'employee_count': profile.employee_count,
                'country': profile.country
            },
            'summary': {},
            'key_metrics': {},
            'trends': {},
            'recommendations': []
        }

        # Calculate compliance scores for each framework
        for framework in frameworks:
            try:
                # Get evidence completion for this framework
                framework_obj = self.db.query(ComplianceFramework).filter(
                    ComplianceFramework.name == framework
                ).first()
                
                if framework_obj:
                    evidence_data = get_evidence_dashboard_data(user, framework_obj.id)
                    completion_pct = evidence_data.get('completion_percentage', 0)
                    
                    report_data['summary'][framework] = {
                        'overall_score': completion_pct,
                        'status': self._get_score_status(completion_pct),
                        'gaps_count': evidence_data.get('total_items', 0) - evidence_data.get('status_breakdown', {}).get('approved', 0),
                        'evidence_completion': completion_pct
                    }
                else:
                    raise Exception("Framework not found")
            except Exception as e:
                # Fallback for frameworks without assessments
                report_data['summary'][framework] = {
                    'overall_score': 0,
                    'status': 'Not Assessed',
                    'gaps_count': 0,
                    'evidence_completion': 0
                }
        
        report_data['key_metrics'] = await self._calculate_key_metrics(user, profile.id, frameworks, period_days)
        report_data['recommendations'] = await self._generate_recommendations(user, profile.id, frameworks, limit=5)
        report_data['trends'] = await self._calculate_trends(user, profile.id, frameworks, period_days)

        return report_data
    
    async def _generate_gap_analysis(
        self, user: User, profile: BusinessProfile, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate data for the gap analysis report"""
        frameworks = parameters.get('frameworks', profile.existing_framew or [])
        severity_filter = parameters.get('severity_filter')

        report_data = {
            'report_type': 'gap_analysis',
            'generated_at': datetime.utcnow().isoformat(),
            'business_profile': {'name': profile.company_name},
            'gaps': {},
            'summary': {'total_gaps': 0, 'critical_gaps': 0, 'high_gaps': 0, 'medium_gaps': 0, 'low_gaps': 0}
        }

        all_gaps = []
        for framework in frameworks:
            try:
                # Generate mock gaps data for now (would be replaced with actual gap analysis)
                gaps = [
                    {
                        'title': f'Sample Gap for {framework}',
                        'description': 'This is a sample gap for demonstration',
                        'severity': 'medium',
                        'category': 'Access Control',
                        'remediation_effort': 'medium'
                    }
                ]
                
                if severity_filter:
                    gaps = [g for g in gaps if g.get('severity') == severity_filter]
                
                report_data['gaps'][framework] = {}
                for gap in gaps:
                    category = gap.get('category', 'General')
                    if category not in report_data['gaps'][framework]:
                        report_data['gaps'][framework][category] = []
                    report_data['gaps'][framework][category].append(gap)
                    
                    report_data['summary']['total_gaps'] += 1
                    severity = gap.get('severity', 'medium').lower()
                    severity_key = f"{severity}_gaps"
                    if severity_key in report_data['summary']:
                        report_data['summary'][severity_key] += 1
                    all_gaps.append(gap)
            except Exception:
                # No gaps data available for this framework
                continue
        
        report_data['remediation_plan'] = self._generate_remediation_plan(all_gaps)
        return report_data

    async def _generate_evidence_report(
        self, user: User, profile: BusinessProfile, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate data for the evidence collection report"""
        frameworks = parameters.get('frameworks', profile.existing_framew or [])
        
        report_data = {
            'report_type': 'evidence_report',
            'generated_at': datetime.utcnow().isoformat(),
            'business_profile': {'name': profile.company_name},
            'evidence_summary': {},
            'collection_status': {},
            'automation_opportunities': []
        }

        for framework in frameworks:
            try:
                # Get evidence dashboard data for this framework
                framework_obj = self.db.query(ComplianceFramework).filter(
                    ComplianceFramework.name == framework
                ).first()
                
                if framework_obj:
                    evidence_data = get_evidence_dashboard_data(user, framework_obj.id)
                    
                    report_data['evidence_summary'][framework] = {
                        'total_items': evidence_data['total_items'],
                        'completion_percentage': evidence_data['completion_percentage'],
                        'automation_opportunities': evidence_data['automation_opportunities']
                    }
                    
                    report_data['collection_status'][framework] = evidence_data['status_breakdown']
                    
                    # Add upcoming items to automation opportunities
                    for item in evidence_data['upcoming_items']:
                        if item.get('automation_source'):
                            report_data['automation_opportunities'].append({
                                'framework': framework,
                                'evidence_name': item['name'],
                                'automation_source': item['automation_source'],
                                'priority': item['priority']
                            })
            except Exception:
                continue

        return report_data

    async def _generate_audit_readiness(
        self, user: User, profile: BusinessProfile, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate audit readiness report"""
        frameworks = parameters.get('frameworks', profile.existing_framew or [])
        
        report_data = {
            'report_type': 'audit_readiness',
            'generated_at': datetime.utcnow().isoformat(),
            'business_profile': {'name': profile.company_name},
            'readiness_scores': {},
            'critical_items': [],
            'audit_timeline': {}
        }

        for framework in frameworks:
            try:
                # Get evidence completion for this framework  
                framework_obj = self.db.query(ComplianceFramework).filter(
                    ComplianceFramework.name == framework
                ).first()
                
                if framework_obj:
                    evidence_data = get_evidence_dashboard_data(user, framework_obj.id)
                    completion_pct = evidence_data.get('completion_percentage', 0)
                    
                    report_data['readiness_scores'][framework] = {
                        'overall_score': completion_pct,
                        'evidence_completion': completion_pct,
                        'policy_completion': 80.0,  # Mock value
                        'gaps_remaining': max(0, evidence_data.get('total_items', 0) - evidence_data.get('status_breakdown', {}).get('approved', 0))
                    }
                    
                    # Add mock critical items
                    if completion_pct < 70:
                        report_data['critical_items'].append({
                            'framework': framework,
                            'title': f'Complete Evidence Collection for {framework}',
                            'severity': 'high',
                            'description': f'Evidence collection for {framework} is at {completion_pct:.1f}%',
                            'remediation_effort': 'medium'
                        })
                        
            except Exception:
                continue

        return report_data

    async def _generate_compliance_status(
        self, user: User, profile: BusinessProfile, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate compliance status report"""
        frameworks = parameters.get('frameworks', profile.existing_framew or [])
        
        report_data = {
            'report_type': 'compliance_status',
            'generated_at': datetime.utcnow().isoformat(),
            'business_profile': {'name': profile.company_name},
            'framework_status': {},
            'overall_metrics': {}
        }

        total_score = 0
        framework_count = 0
        
        for framework in frameworks:
            try:
                # Get evidence completion for this framework
                framework_obj = self.db.query(ComplianceFramework).filter(
                    ComplianceFramework.name == framework
                ).first()
                
                if framework_obj:
                    evidence_data = get_evidence_dashboard_data(user, framework_obj.id)
                    completion_pct = evidence_data.get('completion_percentage', 0)
                    
                    report_data['framework_status'][framework] = {
                        'score': completion_pct,
                        'status': self._get_score_status(completion_pct),
                        'last_assessed': 'Recently',  # Mock value
                        'gaps': max(0, evidence_data.get('total_items', 0) - evidence_data.get('status_breakdown', {}).get('approved', 0))
                    }
                    
                    total_score += completion_pct
                    framework_count += 1
                
            except Exception:
                continue

        if framework_count > 0:
            report_data['overall_metrics'] = {
                'average_score': total_score / framework_count,
                'frameworks_assessed': framework_count,
                'overall_status': self._get_score_status(total_score / framework_count)
            }

        return report_data

    async def _generate_control_matrix(
        self, user: User, profile: BusinessProfile, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate control matrix report"""
        frameworks = parameters.get('frameworks', profile.existing_framew or [])
        
        report_data = {
            'report_type': 'control_matrix',
            'generated_at': datetime.utcnow().isoformat(),
            'business_profile': {'name': profile.company_name},
            'control_mappings': {},
            'coverage_analysis': {}
        }

        # This would require detailed control mapping data
        # For now, return basic structure
        for framework in frameworks:
            report_data['control_mappings'][framework] = {
                'total_controls': 0,
                'implemented_controls': 0,
                'control_details': []
            }

        return report_data

    async def _generate_risk_assessment(
        self, user: User, profile: BusinessProfile, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate risk assessment report"""
        frameworks = parameters.get('frameworks', profile.existing_framew or [])
        
        report_data = {
            'report_type': 'risk_assessment',
            'generated_at': datetime.utcnow().isoformat(),
            'business_profile': {'name': profile.company_name},
            'risk_factors': {},
            'risk_matrix': {}
        }

        # Analyze business profile for risk factors
        risk_factors = []
        
        if profile.handles_persona:
            risk_factors.append({
                'category': 'Data Privacy',
                'risk': 'Handles Personal Data',
                'impact': 'High',
                'likelihood': 'Medium'
            })
            
        if profile.processes_payme:
            risk_factors.append({
                'category': 'Financial',
                'risk': 'Processes Payments',
                'impact': 'High',
                'likelihood': 'Medium'
            })
            
        if profile.stores_health_d:
            risk_factors.append({
                'category': 'Healthcare',
                'risk': 'Stores Health Data',
                'impact': 'Critical',
                'likelihood': 'High'
            })

        report_data['risk_factors'] = risk_factors
        return report_data
        
    # --- Helper Methods ---

    def _get_score_status(self, score: float) -> str:
        """Get a text label for a compliance score."""
        if score >= 90: return 'Excellent'
        if score >= 80: return 'Good'
        if score >= 70: return 'Satisfactory'
        if score >= 60: return 'Needs Improvement'
        return 'Critical'

    async def _calculate_key_metrics(self, user: User, business_profile_id: UUID, frameworks: List[str], period_days: int) -> Dict[str, Any]:
        """Calculate high-level metrics."""
        # Get evidence collection metrics
        total_evidence = 0
        collected_evidence = 0
        
        for framework in frameworks:
            try:
                framework_obj = self.db.query(ComplianceFramework).filter(
                    ComplianceFramework.name == framework
                ).first()
                
                if framework_obj:
                    evidence_data = get_evidence_dashboard_data(user, framework_obj.id)
                    total_evidence += evidence_data['total_items']
                    collected_evidence += evidence_data['status_breakdown'].get('collected', 0)
                    collected_evidence += evidence_data['status_breakdown'].get('approved', 0)
            except Exception:
                continue

        evidence_completion = (collected_evidence / total_evidence * 100) if total_evidence > 0 else 0
        
        return {
            'total_evidence_items': total_evidence,
            'evidence_completion_percentage': evidence_completion,
            'frameworks_tracked': len(frameworks),
            'period_days': period_days
        }

    async def _generate_recommendations(self, user: User, business_profile_id: UUID, frameworks: List[str], limit: int) -> List[Dict[str, Any]]:
        """Generate top N recommendations based on gaps."""
        recommendations = []
        
        # Get evidence completion status for recommendations
        for framework in frameworks:
            try:
                framework_obj = self.db.query(ComplianceFramework).filter(
                    ComplianceFramework.name == framework
                ).first()
                
                if framework_obj:
                    evidence_data = get_evidence_dashboard_data(user, framework_obj.id)
                    completion_pct = evidence_data.get('completion_percentage', 0)
                    
                    if completion_pct < 80:  # If less than 80% complete
                        recommendations.append({
                            'priority': len(recommendations) + 1,
                            'title': f'Complete Evidence Collection for {framework}',
                            'description': f'Evidence collection for {framework} is at {completion_pct:.1f}%. Focus on completing high-priority evidence items.',
                            'impact': 'High' if completion_pct < 50 else 'Medium',
                            'effort': 'Medium',
                            'framework': framework
                        })
                        
                        if len(recommendations) >= limit:
                            break
                    
            except Exception:
                continue

        # Add default recommendations if not enough gaps found
        if len(recommendations) < limit:
            default_recs = [
                {
                    'priority': len(recommendations) + 1,
                    'title': "Complete Evidence Collection",
                    'description': "Ensure all required evidence items are collected and documented",
                    'impact': 'High',
                    'effort': 'Medium',
                    'framework': 'General'
                },
                {
                    'priority': len(recommendations) + 2,
                    'title': "Review Security Policies",
                    'description': "Conduct regular review of security policies and procedures",
                    'impact': 'Medium',
                    'effort': 'Low',
                    'framework': 'General'
                }
            ]
            
            for rec in default_recs:
                if len(recommendations) >= limit:
                    break
                recommendations.append(rec)

        return recommendations[:limit]

    async def _calculate_trends(self, user: User, business_profile_id: UUID, frameworks: List[str], period_days: int) -> Dict[str, str]:
        """Calculate trends over a given period."""
        # This would require historical data tracking
        # For now, return mock trends based on current state
        return {
            'compliance_trend': 'improving',
            'evidence_trend': 'stable',
            'gap_trend': 'decreasing'
        }

    def _generate_remediation_plan(self, all_gaps: List[Dict]) -> List[Dict]:
        """Generate a prioritized remediation plan."""
        plan = []
        
        # Sort gaps by severity and effort
        critical_gaps = [g for g in all_gaps if g.get('severity') == 'critical']
        high_gaps = [g for g in all_gaps if g.get('severity') == 'high']
        low_effort_gaps = [g for g in all_gaps if g.get('remediation_effort') == 'low']
        
        # Phase 1: Critical gaps and quick wins
        for gap in critical_gaps[:3]:
            plan.append({
                'phase': 'Phase 1 (0-30 days)',
                'title': gap.get('title', 'Critical Gap'),
                'effort': gap.get('remediation_effort', 'High'),
                'impact': 'Critical',
                'description': gap.get('description', '')
            })
            
        for gap in low_effort_gaps[:2]:
            if gap not in critical_gaps:
                plan.append({
                    'phase': 'Phase 1 (0-30 days)',
                    'title': gap.get('title', 'Quick Win'),
                    'effort': 'Low',
                    'impact': gap.get('severity', 'Medium'),
                    'description': gap.get('description', '')
                })
        
        # Phase 2: High priority items
        for gap in high_gaps[:3]:
            if gap not in critical_gaps and gap not in low_effort_gaps:
                plan.append({
                    'phase': 'Phase 2 (30-90 days)',
                    'title': gap.get('title', 'High Priority Gap'),
                    'effort': gap.get('remediation_effort', 'Medium'),
                    'impact': 'High',
                    'description': gap.get('description', '')
                })
        
        return plan[:8]  # Limit to 8 items total