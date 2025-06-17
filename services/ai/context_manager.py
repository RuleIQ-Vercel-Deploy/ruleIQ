"""
Manages the retrieval of contextual information to inform the AI assistant's responses.
"""

from typing import Dict, List, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
import json

from database.business_profile import BusinessProfile
from database.evidence_item import EvidenceItem

class ContextManager:
    """Gathers relevant data to build a context for AI conversations."""

    def __init__(self, db: Session):
        self.db = db

    async def get_conversation_context(self, conversation_id: UUID, business_profile_id: UUID) -> Dict[str, Any]:
        """Assembles the full context for a given conversation."""
        try:
            # Get business profile
            profile = self.db.query(BusinessProfile).filter(
                BusinessProfile.id == str(business_profile_id)
            ).first()
            
            if not profile:
                return self._get_default_context(conversation_id, business_profile_id)
            
            # Get recent evidence (last 30 days)
            recent_evidence = self.db.query(EvidenceItem).filter(
                and_(
                    EvidenceItem.user_id == str(profile.user_id),
                    EvidenceItem.created_at > datetime.utcnow() - timedelta(days=30)
                )
            ).order_by(desc(EvidenceItem.created_at)).limit(10).all()
            
            # Get compliance status (mock implementation - you can enhance based on your readiness service)
            compliance_status = await self._get_compliance_status(profile)
            
            return {
                'conversation_id': str(conversation_id),
                'business_profile_id': str(business_profile_id),
                'business_profile': {
                    'name': profile.company_name or 'Unknown Company',
                    'industry': profile.industry or 'Unknown Industry',
                    'frameworks': profile.compliance_frameworks or [],
                    'size': getattr(profile, 'company_size', 'Unknown'),
                    'country': getattr(profile, 'country', 'Unknown')
                },
                'recent_evidence': [
                    {
                        'title': e.evidence_name or 'Untitled Evidence',
                        'type': e.evidence_type or 'Unknown Type',
                        'status': e.status or 'active',
                        'created_date': e.created_at.isoformat() if e.created_at else None
                    } for e in recent_evidence
                ],
                'compliance_status': compliance_status,
                'evidence_summary': {
                    'total_items': len(recent_evidence),
                    'evidence_types': list(set([e.evidence_type for e in recent_evidence if e.evidence_type])),
                    'recent_activity': len([e for e in recent_evidence if e.created_at and e.created_at > datetime.utcnow() - timedelta(days=7)])
                }
            }
            
        except Exception as e:
            print(f"Error getting conversation context: {e}")
            return self._get_default_context(conversation_id, business_profile_id)

    async def get_conversation_history(self, conversation_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves the most recent messages from a conversation."""
        try:
            # For now, return empty history since ChatMessage model isn't created yet
            # This will be implemented when the chat models are ready
            return []
            
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []

    async def get_relevant_evidence(self, business_profile_id: UUID, query: str, limit: int = 5) -> List[Any]:
        """Searches for evidence relevant to the user's query."""
        try:
            profile = self.db.query(BusinessProfile).filter(
                BusinessProfile.id == str(business_profile_id)
            ).first()
            
            if not profile:
                return []
            
            # Simple text search in evidence items
            # You can enhance this with vector search or more sophisticated matching
            query_lower = query.lower()
            
            evidence_items = self.db.query(EvidenceItem).filter(
                EvidenceItem.user_id == str(profile.user_id)
            ).all()
            
            # Filter evidence based on query relevance
            relevant_items = []
            for item in evidence_items:
                relevance_score = 0
                
                # Check title/name relevance
                if item.evidence_name and query_lower in item.evidence_name.lower():
                    relevance_score += 3
                
                # Check description relevance
                if item.description and query_lower in item.description.lower():
                    relevance_score += 2
                
                # Check type relevance
                if item.evidence_type and query_lower in item.evidence_type.lower():
                    relevance_score += 1
                
                if relevance_score > 0:
                    relevant_items.append((item, relevance_score))
            
            # Sort by relevance and return top items
            relevant_items.sort(key=lambda x: x[1], reverse=True)
            return [item[0] for item in relevant_items[:limit]]
            
        except Exception as e:
            print(f"Error searching evidence: {e}")
            return []

    async def get_framework_specific_context(self, business_profile_id: UUID, framework: str) -> Dict[str, Any]:
        """Gets context specific to a compliance framework."""
        try:
            profile = self.db.query(BusinessProfile).filter(
                BusinessProfile.id == str(business_profile_id)
            ).first()
            
            if not profile:
                return {}
            
            # Get evidence relevant to the specific framework
            framework_evidence = self.db.query(EvidenceItem).filter(
                and_(
                    EvidenceItem.user_id == str(profile.user_id),
                    EvidenceItem.framework_mappings.like(f'%{framework}%')
                )
            ).all()
            
            return {
                'framework': framework,
                'evidence_count': len(framework_evidence),
                'evidence_types': list(set([e.evidence_type for e in framework_evidence if e.evidence_type])),
                'completion_status': await self._calculate_framework_completion(framework, framework_evidence),
                'recent_updates': len([
                    e for e in framework_evidence 
                    if e.created_at and e.created_at > datetime.utcnow() - timedelta(days=30)
                ])
            }
            
        except Exception as e:
            print(f"Error getting framework context: {e}")
            return {}

    async def _get_compliance_status(self, profile: BusinessProfile) -> Dict[str, Any]:
        """Gets current compliance status for the business profile."""
        try:
            # This is a mock implementation - you can integrate with your readiness service
            from services.readiness_service import calculate_readiness_score
            
            readiness_data = calculate_readiness_score(str(profile.id), self.db)
            
            return {
                'overall_score': readiness_data.get('overall_score', 0),
                'framework_scores': readiness_data.get('framework_scores', {}),
                'last_updated': datetime.utcnow().isoformat(),
                'status': 'good' if readiness_data.get('overall_score', 0) > 80 else 'needs_improvement'
            }
            
        except Exception as e:
            print(f"Error getting compliance status: {e}")
            return {
                'overall_score': 0,
                'framework_scores': {},
                'last_updated': datetime.utcnow().isoformat(),
                'status': 'unknown'
            }

    async def _calculate_framework_completion(self, framework: str, evidence_items: List[Any]) -> float:
        """Calculates completion percentage for a specific framework."""
        try:
            # This is a simplified calculation - you can make it more sophisticated
            # based on required evidence items for each framework
            
            framework_requirements = {
                'ISO27001': 30,  # Assuming 30 key evidence items needed
                'SOC2': 25,
                'GDPR': 20,
                'HIPAA': 35
            }
            
            required_items = framework_requirements.get(framework, 20)
            collected_items = len(evidence_items)
            
            completion = min((collected_items / required_items) * 100, 100)
            return round(completion, 1)
            
        except Exception:
            return 0.0

    def _get_default_context(self, conversation_id: UUID, business_profile_id: UUID) -> Dict[str, Any]:
        """Returns a default context when profile information is unavailable."""
        return {
            'conversation_id': str(conversation_id),
            'business_profile_id': str(business_profile_id),
            'business_profile': {
                'name': 'Unknown Company',
                'industry': 'Unknown Industry',
                'frameworks': [],
                'size': 'Unknown',
                'country': 'Unknown'
            },
            'recent_evidence': [],
            'compliance_status': {
                'overall_score': 0,
                'framework_scores': {},
                'last_updated': datetime.utcnow().isoformat(),
                'status': 'unknown'
            },
            'evidence_summary': {
                'total_items': 0,
                'evidence_types': [],
                'recent_activity': 0
            }
        }