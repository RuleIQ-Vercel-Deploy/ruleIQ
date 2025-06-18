"""
Manages the retrieval of contextual information to inform the AI assistant's responses.
"""

from typing import Dict, List, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from database.business_profile import BusinessProfile
from database.evidence_item import EvidenceItem

class ContextManager:
    """Gathers relevant data to build a context for AI conversations asynchronously."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_conversation_context(self, conversation_id: UUID, business_profile_id: UUID) -> Dict[str, Any]:
        """Assembles the full context for a given conversation asynchronously."""
        profile_stmt = select(BusinessProfile).where(BusinessProfile.id == business_profile_id)
        profile_res = await self.db.execute(profile_stmt)
        profile = profile_res.scalars().first()
        
        if not profile:
            return self._get_default_context(conversation_id, business_profile_id)
        
        # Get recent evidence (last 30 days)
        recent_evidence_stmt = select(EvidenceItem).where(
            and_(
                EvidenceItem.user_id == profile.user_id,
                EvidenceItem.created_at > datetime.utcnow() - timedelta(days=30)
            )
        ).order_by(desc(EvidenceItem.created_at)).limit(10)
        recent_evidence_res = await self.db.execute(recent_evidence_stmt)
        recent_evidence = recent_evidence_res.scalars().all()
        
        # In a real app, this would call the async readiness service
        compliance_status = {"overall_score": 75, "framework_scores": {"ISO27001": 80}}
        
        return {
            'conversation_id': str(conversation_id),
            'business_profile_id': str(business_profile_id),
            'business_profile': {
                'name': profile.company_name,
                'industry': profile.industry,
                'frameworks': profile.existing_frameworks + profile.planned_frameworks,
            },
            'recent_evidence': [item.to_dict() for item in recent_evidence],
            'compliance_status': compliance_status,
        }

    def _get_default_context(self, conversation_id: UUID, business_profile_id: UUID) -> Dict[str, Any]:
        """Returns a default context when profile information is unavailable."""
        return {
            'conversation_id': str(conversation_id),
            'business_profile_id': str(business_profile_id),
            'business_profile': {
                'name': 'Unknown Company',
                'industry': 'Unknown Industry',
                'frameworks': [],
            },
            'recent_evidence': [],
            'compliance_status': {
                'overall_score': 0,
                'framework_scores': {},
            },
        }
