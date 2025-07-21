"""Query optimization utilities for ruleIQ database."""

from sqlalchemy import select, func, and_, or_, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Optimized database queries to prevent N+1 problems."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_evidence_with_relations(
        self, user_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get evidence items with all related data in a single query.

        Prevents N+1 queries when accessing related data.
        """
        from database.evidence_item import EvidenceItem

        query = (
            select(EvidenceItem)
            .options(
                selectinload(EvidenceItem.user),
                selectinload(EvidenceItem.business_profile),
                selectinload(EvidenceItem.framework),
            )
            .where(EvidenceItem.user_id == user_id)
            .order_by(EvidenceItem.created_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        evidence_items = result.scalars().all()

        return [
            {
                "id": str(item.id),
                "evidence_name": item.evidence_name,
                "description": item.description,
                "status": item.status,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "business_profile": {
                    "id": str(item.business_profile.id),
                    "company_name": item.business_profile.company_name,
                    "industry": item.business_profile.industry,
                }
                if item.business_profile
                else None,
                "framework": {
                    "id": str(item.framework.id),
                    "name": item.framework.name,
                    "category": item.framework.category,
                }
                if item.framework
                else None,
            }
            for item in evidence_items
        ]

    async def get_business_profile_with_counts(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get business profile with aggregated counts in a single query.

        Prevents multiple queries for counting related items.
        """
        from database.business_profile import BusinessProfile
        from database.evidence_item import EvidenceItem
        from database.assessment_session import AssessmentSession

        query = (
            select(
                BusinessProfile,
                func.count(EvidenceItem.id).label("evidence_count"),
                func.count(AssessmentSession.id).label("assessment_count"),
            )
            .outerjoin(EvidenceItem, EvidenceItem.business_profile_id == BusinessProfile.id)
            .outerjoin(
                AssessmentSession, AssessmentSession.business_profile_id == BusinessProfile.id
            )
            .where(BusinessProfile.user_id == user_id)
            .group_by(BusinessProfile.id)
        )

        result = await self.db.execute(query)
        row = result.first()

        if not row:
            return None

        profile, evidence_count, assessment_count = row

        return {
            "id": str(profile.id),
            "company_name": profile.company_name,
            "industry": profile.industry,
            "company_size": profile.company_size,
            "evidence_count": evidence_count,
            "assessment_count": assessment_count,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
        }

    async def get_frameworks_with_usage_counts(self) -> List[Dict[str, Any]]:
        """
        Get frameworks with usage counts for analytics.

        Prevents N+1 queries when calculating framework usage.
        """
        from database.compliance_framework import ComplianceFramework
        from database.assessment_session import AssessmentSession

        query = (
            select(ComplianceFramework, func.count(AssessmentSession.id).label("usage_count"))
            .outerjoin(AssessmentSession, AssessmentSession.framework_id == ComplianceFramework.id)
            .where(ComplianceFramework.is_active == True)
            .group_by(ComplianceFramework.id)
            .order_by(func.count(AssessmentSession.id).desc())
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            {
                "id": str(framework.id),
                "name": framework.name,
                "category": framework.category,
                "description": framework.description,
                "usage_count": usage_count,
                "is_active": framework.is_active,
            }
            for framework, usage_count in rows
        ]

    async def search_evidence_efficiently(
        self,
        user_id: str,
        query: str,
        status: Optional[str] = None,
        framework_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Search evidence with full-text search and filters.

        Uses GIN indexes for efficient text search.
        """
        from database.evidence_item import EvidenceItem

        # Build base query
        base_query = (
            select(EvidenceItem)
            .options(
                selectinload(EvidenceItem.business_profile), selectinload(EvidenceItem.framework)
            )
            .where(EvidenceItem.user_id == user_id)
        )

        # Add search conditions
        conditions = []

        if query:
            conditions.append(
                or_(
                    EvidenceItem.evidence_name.ilike(f"%{query}%"),
                    EvidenceItem.description.ilike(f"%{query}%"),
                )
            )

        if status:
            conditions.append(EvidenceItem.status == status)

        if framework_id:
            conditions.append(EvidenceItem.framework_id == framework_id)

        if conditions:
            base_query = base_query.where(and_(*conditions))

        # Add ordering and limit
        base_query = base_query.order_by(EvidenceItem.created_at.desc()).limit(limit)

        result = await self.db.execute(base_query)
        evidence_items = result.scalars().all()

        return [
            {
                "id": str(item.id),
                "evidence_name": item.evidence_name,
                "description": item.description,
                "status": item.status,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "business_profile": {
                    "id": str(item.business_profile.id),
                    "company_name": item.business_profile.company_name,
                }
                if item.business_profile
                else None,
                "framework": {"id": str(item.framework.id), "name": item.framework.name}
                if item.framework
                else None,
            }
            for item in evidence_items
        ]


class BatchQueryOptimizer:
    """Batch operations to reduce database round trips."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def batch_update_evidence_status(self, evidence_ids: List[str], new_status: str) -> int:
        """
        Update multiple evidence items in a single query.

        Returns number of updated records.
        """
        from database.evidence_item import EvidenceItem

        query = (
            update(EvidenceItem)
            .where(EvidenceItem.id.in_(evidence_ids))
            .values(status=new_status)
            .execution_options(synchronize_session=False)
        )

        result = await self.db.execute(query)
        await self.db.commit()

        return result.rowcount

    async def batch_delete_evidence(self, evidence_ids: List[str]) -> int:
        """
        Delete multiple evidence items in a single query.

        Returns number of deleted records.
        """
        from database.evidence_item import EvidenceItem

        query = (
            delete(EvidenceItem)
            .where(EvidenceItem.id.in_(evidence_ids))
            .execution_options(synchronize_session=False)
        )

        result = await self.db.execute(query)
        await self.db.commit()

        return result.rowcount

    async def get_evidence_batch_by_ids(self, evidence_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple evidence items by IDs in a single query.

        Prevents N+1 queries when loading evidence by ID.
        """
        from database.evidence_item import EvidenceItem

        query = (
            select(EvidenceItem)
            .options(
                selectinload(EvidenceItem.business_profile), selectinload(EvidenceItem.framework)
            )
            .where(EvidenceItem.id.in_(evidence_ids))
        )

        result = await self.db.execute(query)
        evidence_items = result.scalars().all()

        return [
            {
                "id": str(item.id),
                "evidence_name": item.evidence_name,
                "description": item.description,
                "status": item.status,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "business_profile_id": str(item.business_profile_id),
                "framework_id": str(item.framework_id),
            }
            for item in evidence_items
        ]


# Query caching utilities
class QueryCache:
    """Simple query caching to reduce database load."""

    def __init__(self):
        self._cache = {}

    def get(self, key: str) -> Any:
        """Get cached result."""
        return self._cache.get(key)

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set cached result with TTL (default 5 minutes)."""
        import time

        self._cache[key] = {"value": value, "expires": time.time() + ttl}

    def is_valid(self, key: str) -> bool:
        """Check if cached result is still valid."""
        import time

        if key not in self._cache:
            return False

        cached = self._cache[key]
        return time.time() < cached["expires"]

    def invalidate(self, key: str) -> None:
        """Invalidate specific cache entry."""
        self._cache.pop(key, None)

    def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate cache entries matching pattern."""
        import re

        keys_to_remove = [key for key in self._cache.keys() if re.search(pattern, key)]
        for key in keys_to_remove:
            self.invalidate(key)

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()


# Global query cache instance
query_cache = QueryCache()
