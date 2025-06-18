from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import BusinessProfile, ComplianceFramework, Evidence, GeneratedPolicy, User
# Assuming the AI function is awaitable or wrapped to be non-blocking
from services.ai.evidence_generator import generate_checklist_with_ai


class EvidenceService:
    """Provides business logic for evidence management."""

    @staticmethod
    async def create_evidence(user_id: UUID, evidence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for creating evidence. Mocked in tests."""
        pass

    @staticmethod
    async def get_evidence_by_id(
        db: AsyncSession, evidence_id: UUID, user_id: UUID
    ) -> Optional[Evidence]:
        """Alias for get_evidence_item for test compatibility."""
        return await EvidenceService.get_evidence_item(db, evidence_id, user_id)

    @staticmethod
    def validate_evidence_quality(evidence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for validating evidence quality. Mocked in tests."""
        pass

    @staticmethod
    def validate_evidence_type(evidence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for validating evidence type. Mocked in tests."""
        pass

    @staticmethod
    async def generate_evidence_checklist(
        db: AsyncSession,
        user: User,
        framework_id: UUID,
        policy_id: Optional[UUID] = None
    ) -> List[Evidence]:
        """Generate a comprehensive evidence checklist for a compliance framework asynchronously."""
        existing_items_stmt = select(Evidence).where(
            Evidence.user_id == user.id, Evidence.framework_id == framework_id
        )
        existing_items_res = await db.execute(existing_items_stmt)
        existing_items = existing_items_res.scalars().all()
        if existing_items:
            return existing_items

        profile_stmt = select(BusinessProfile).where(BusinessProfile.user_id == user.id)
        profile_res = await db.execute(profile_stmt)
        profile = profile_res.scalars().first()
        if not profile:
            raise ValueError("Business profile not found")

        framework_stmt = select(ComplianceFramework).where(ComplianceFramework.id == framework_id)
        framework_res = await db.execute(framework_stmt)
        framework = framework_res.scalars().first()
        if not framework:
            raise ValueError("Compliance framework not found")

        policy = None
        if policy_id:
            policy_stmt = select(GeneratedPolicy).where(
                GeneratedPolicy.id == policy_id, GeneratedPolicy.user_id == user.id
            )
            policy_res = await db.execute(policy_stmt)
            policy = policy_res.scalars().first()

        prompt_details = (
            f"Business Profile: {profile.description}. "
            f"Compliance Framework: {framework.name} ({framework.description}). "
            f"Key Controls: {', '.join([c.name for c in framework.controls[:5]])}."
        )
        if policy:
            prompt_details += f" Relevant Policy: {policy.title}."

        generated_titles = await generate_checklist_with_ai(prompt_details)

        new_evidence_items = []
        for title in generated_titles:
            item = Evidence(
                user_id=user.id,
                title=title,
                description=f"Evidence for {framework.name}",
                status="pending",
                framework_id=framework_id,
            )
            new_evidence_items.append(item)

        db.add_all(new_evidence_items)
        await db.commit()
        return new_evidence_items

    @staticmethod
    async def upload_evidence_file(
        db: AsyncSession,
        user: User,
        evidence_id: UUID,
        file_name: str,
        file_path: str,
        metadata: Optional[Dict] = None,
    ) -> Evidence:
        """Attach a file to an evidence item asynchronously."""
        item = await EvidenceService.get_evidence_item(db, evidence_id, user.id)
        if not item:
            raise ValueError("Evidence item not found")

        item.file_path = file_path
        item.file_name = file_name
        item.metadata = metadata or item.metadata
        item.status = "collected"
        item.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def get_evidence_item(
        db: AsyncSession, evidence_id: UUID, user_id: UUID
    ) -> Optional[Evidence]:
        """Retrieve a single evidence item by ID asynchronously."""
        stmt = select(Evidence).where(
            Evidence.id == evidence_id, Evidence.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def update_evidence_status(
        db: AsyncSession,
        user: User,
        evidence_id: UUID,
        status: str,
        notes: Optional[str] = None,
    ) -> Optional[Evidence]:
        """Update the status of an evidence item asynchronously."""
        item = await EvidenceService.get_evidence_item(db, evidence_id, user.id)
        if not item:
            return None

        item.status = status
        if notes:
            item.notes = notes
        item.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def delete_evidence_item(db: AsyncSession, evidence_id: UUID, user_id: UUID) -> bool:
        """Delete an evidence item asynchronously."""
        item = await EvidenceService.get_evidence_item(db, evidence_id, user_id)
        if not item:
            return False

        await db.delete(item)
        await db.commit()
        return True

    @staticmethod
    async def get_evidence_summary(db: AsyncSession, user: User) -> Dict[str, Any]:
        """Get a summary of evidence status asynchronously."""
        stmt = select(Evidence).where(Evidence.user_id == user.id)
        result = await db.execute(stmt)
        items = result.scalars().all()

        status_counts = {
            "pending": 0, "collected": 0, "in_review": 0, "approved": 0, "rejected": 0
        }
        for item in items:
            if item.status in status_counts:
                status_counts[item.status] += 1

        total_items = len(items)
        completion_percentage = (
            status_counts["approved"] / total_items * 100 if total_items > 0 else 0
        )

        return {
            "total_items": total_items,
            "status_counts": status_counts,
            "completion_percentage": round(completion_percentage, 2),
            "recently_updated": [
                {"id": item.id, "title": item.title, "status": item.status, "updated_at": item.updated_at}
                for item in sorted(items, key=lambda x: x.updated_at, reverse=True)[:5]
            ],
        }

    @staticmethod
    def get_evidence_guidance(cloud_provider: str) -> Dict[str, str]:
        """Get guidance on where to find evidence for a specific cloud provider."""
        guidance_map = {
            "AWS": {
                "access_logs": "CloudTrail logs, S3 access logs, VPC flow logs",
                "security_config": "IAM policies, Security Group rules, AWS Config findings",
            },
            "Azure": {
                "access_logs": "Azure Monitor logs, Activity Log, NSG flow logs",
                "security_config": "Azure Policy assignments, Security Center recommendations",
            },
            "Google Cloud": {
                "access_logs": "Cloud Audit Logs, Cloud Logging exports",
                "security_config": "Security Command Center findings, policies",
            }
        }
        return guidance_map.get(cloud_provider, {})

    @staticmethod
    async def bulk_update_evidence_status(
        db: AsyncSession, user: User, evidence_ids: List[UUID], status: str, notes: str = ""
    ) -> List[Evidence]:
        """Bulk update multiple evidence items asynchronously."""
        updated_items = []
        for evidence_id in evidence_ids:
            try:
                item = await EvidenceService.update_evidence_status(db, user, evidence_id, status, notes)
                if item:
                    updated_items.append(item)
            except ValueError:
                continue
        return updated_items

    @staticmethod
    async def list_evidence_items(
        db: AsyncSession, user: User, framework_id: UUID
    ) -> List[Evidence]:
        """List all evidence items for a user and framework."""
        stmt = select(Evidence).where(
            Evidence.user_id == user.id, Evidence.framework_id == framework_id
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_evidence_dashboard(
        db: AsyncSession, user: User, framework_id: UUID
    ) -> Dict[str, Any]:
        """Get dashboard data for evidence collection status."""
        items = await EvidenceService.list_evidence_items(db, user, framework_id)
        if not items:
            return {"message": "No evidence items found for this framework."}

        status_counts = {
            "pending": 0, "collected": 0, "in_review": 0, "approved": 0, "rejected": 0
        }
        for item in items:
            if item.status in status_counts:
                status_counts[item.status] += 1

        total_items = len(items)
        completion_percentage = (
            status_counts["approved"] / total_items * 100 if total_items > 0 else 0
        )

        return {
            "total_items": total_items,
            "status_counts": status_counts,
            "completion_percentage": round(completion_percentage, 2),
            "recently_updated": [
                {"id": item.id, "title": item.title, "status": item.status, "updated_at": item.updated_at}
                for item in sorted(items, key=lambda x: x.updated_at, reverse=True)[:5]
            ],
        }
