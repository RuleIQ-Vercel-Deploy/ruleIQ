from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import BusinessProfile, ComplianceFramework, GeneratedPolicy, User
from database.evidence_item import EvidenceItem
# Assuming the AI function is awaitable or wrapped to be non-blocking
from services.ai.evidence_generator import generate_checklist_with_ai


class EvidenceService:
    """Provides business logic for evidence management."""

    @staticmethod
    def _convert_evidence_item_to_response(evidence_item: EvidenceItem) -> Dict[str, Any]:
        """Convert EvidenceItem model to expected response format."""
        return {
            "id": evidence_item.id,
            "user_id": evidence_item.user_id,
            "title": evidence_item.evidence_name,
            "description": evidence_item.description or "",
            "control_id": evidence_item.control_reference,
            "framework_id": evidence_item.framework_id,
            "business_profile_id": evidence_item.business_profile_id,
            "source": evidence_item.automation_source or "manual_upload",
            "tags": [],  # EvidenceItem doesn't have tags field
            "file_path": getattr(evidence_item, 'file_path', None),
            "status": evidence_item.status,
            "created_at": evidence_item.created_at,
            "updated_at": evidence_item.updated_at,
            "evidence_type": evidence_item.evidence_type,  # Add the missing field
        }

    @staticmethod
    async def create_evidence(user_id: UUID, evidence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for creating evidence. Mocked in tests."""
        pass

    @staticmethod
    async def create_evidence_item(
        db: AsyncSession, user: User, evidence_data: Dict[str, Any]
    ) -> EvidenceItem:
        """Create a new evidence item."""
        from uuid import uuid4

        # Create new evidence item with all required fields
        evidence = EvidenceItem(
            id=uuid4(),
            user_id=user.id,
            evidence_name=evidence_data["title"],
            evidence_type=evidence_data.get("evidence_type", "document"),
            control_reference=evidence_data["control_id"],
            framework_id=evidence_data["framework_id"],
            business_profile_id=evidence_data["business_profile_id"],
            automation_source=evidence_data.get("source", "manual_upload"),
            description=evidence_data.get("description", ""),
            status="pending_review",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(evidence)
        await db.commit()
        await db.refresh(evidence)
        return evidence

    @staticmethod
    async def get_evidence_by_id(
        db: AsyncSession, evidence_id: UUID, user_id: UUID
    ) -> Optional[EvidenceItem]:
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
    ) -> List[EvidenceItem]:
        """Generate a comprehensive evidence checklist for a compliance framework asynchronously."""
        existing_items_stmt = select(EvidenceItem).where(
            EvidenceItem.user_id == user.id, EvidenceItem.framework_id == framework_id
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
            item = EvidenceItem(
                user_id=user.id,
                evidence_name=title,
                evidence_type="document",
                control_reference="TBD",
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
    ) -> EvidenceItem:
        """Attach a file to an evidence item asynchronously."""
        item = await EvidenceService.get_evidence_item(db, evidence_id, user.id)
        if not item:
            raise ValueError("Evidence item not found")

        item.file_path = file_path
        item.file_type = file_name.split('.')[-1] if '.' in file_name else None
        item.status = "collected"
        item.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def get_evidence_item(
        db: AsyncSession, evidence_id: UUID, user_id: UUID
    ) -> Optional[EvidenceItem]:
        """Retrieve a single evidence item by ID asynchronously."""
        stmt = select(EvidenceItem).where(
            EvidenceItem.id == evidence_id, EvidenceItem.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_evidence_item_with_auth_check(
        db: AsyncSession, evidence_id: UUID, user_id: UUID
    ) -> tuple[Optional[EvidenceItem], str]:
        """
        Retrieve evidence item with authorization check.
        Returns (evidence_item, status) where status is:
        - 'found': Evidence found and user has access
        - 'not_found': Evidence doesn't exist
        - 'unauthorized': Evidence exists but user doesn't have access
        """
        # First check if evidence exists at all
        stmt = select(EvidenceItem).where(EvidenceItem.id == evidence_id)
        result = await db.execute(stmt)
        evidence = result.scalars().first()

        if not evidence:
            return None, 'not_found'

        # Check if user has access to this evidence
        if evidence.user_id != user_id:
            return None, 'unauthorized'

        return evidence, 'found'

    @staticmethod
    async def update_evidence_status(
        db: AsyncSession,
        user: User,
        evidence_id: UUID,
        status: str,
        notes: Optional[str] = None,
    ) -> Optional[EvidenceItem]:
        """Update the status of an evidence item asynchronously."""
        item = await EvidenceService.get_evidence_item(db, evidence_id, user.id)
        if not item:
            return None

        item.status = status
        if notes:
            item.collection_notes = notes
        item.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def update_evidence_item(
        db: AsyncSession,
        user: User,
        evidence_id: UUID,
        update_data: Dict[str, Any]
    ) -> tuple[Optional[EvidenceItem], str]:
        """
        Update an evidence item with provided data.
        Returns (evidence_item, status) where status is:
        - 'updated': Evidence updated successfully
        - 'not_found': Evidence doesn't exist
        - 'unauthorized': Evidence exists but user doesn't have access
        """
        item, status = await EvidenceService.get_evidence_item_with_auth_check(db, evidence_id, user.id)
        if status != 'found':
            return None, status

        # Update fields that are provided
        for field, value in update_data.items():
            if field == "title":
                item.evidence_name = value
            elif field == "control_id":
                item.control_reference = value
            elif hasattr(item, field):
                setattr(item, field, value)

        await db.commit()
        await db.refresh(item)
        return item, 'updated'

    @staticmethod
    async def delete_evidence_item(
        db: AsyncSession,
        user: User,
        evidence_id: UUID
    ) -> tuple[bool, str]:
        """
        Delete an evidence item asynchronously.
        Returns (success, status) where status is:
        - 'deleted': Evidence deleted successfully
        - 'not_found': Evidence doesn't exist
        - 'unauthorized': Evidence exists but user doesn't have access
        """
        item, status = await EvidenceService.get_evidence_item_with_auth_check(db, evidence_id, user.id)
        if status != 'found':
            return False, status

        await db.delete(item)
        await db.commit()
        return True, 'deleted'

    @staticmethod
    async def get_evidence_summary(db: AsyncSession, user: User) -> Dict[str, Any]:
        """Get a summary of evidence status asynchronously."""
        stmt = select(EvidenceItem).where(EvidenceItem.user_id == user.id)
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
                {"id": item.id, "title": item.evidence_name, "status": item.status, "updated_at": item.updated_at}
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
    ) -> List[EvidenceItem]:
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
    ) -> List[EvidenceItem]:
        """List all evidence items for a user and framework."""
        stmt = select(EvidenceItem).where(
            EvidenceItem.user_id == user.id, EvidenceItem.framework_id == framework_id
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def list_all_evidence_items(
        db: AsyncSession,
        user: User,
        framework_id: Optional[UUID] = None,
        evidence_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[EvidenceItem]:
        """List all evidence items for a user with optional filtering."""
        stmt = select(EvidenceItem).where(EvidenceItem.user_id == user.id)

        if framework_id:
            stmt = stmt.where(EvidenceItem.framework_id == framework_id)
        if evidence_type:
            stmt = stmt.where(EvidenceItem.evidence_type == evidence_type)
        if status:
            stmt = stmt.where(EvidenceItem.status == status)

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
                {"id": item.id, "title": item.evidence_name, "status": item.status, "updated_at": item.updated_at}
                for item in sorted(items, key=lambda x: x.updated_at, reverse=True)[:5]
            ],
        }

    @staticmethod
    async def bulk_update_evidence_status(
        db: AsyncSession,
        user: User,
        evidence_ids: List[UUID],
        status: str,
        reason: Optional[str] = None
    ) -> tuple[int, int, List[UUID]]:
        """
        Bulk update evidence status for multiple items.
        Returns (updated_count, failed_count, failed_ids)
        """
        updated_count = 0
        failed_count = 0
        failed_ids = []

        for evidence_id in evidence_ids:
            try:
                item, auth_status = await EvidenceService.get_evidence_item_with_auth_check(
                    db, evidence_id, user.id
                )

                if auth_status == 'found':
                    item.status = status
                    if reason:
                        # Add reason to metadata if it exists, otherwise create metadata
                        if item.metadata:
                            item.metadata["status_update_reason"] = reason
                        else:
                            item.metadata = {"status_update_reason": reason}
                    updated_count += 1
                else:
                    failed_count += 1
                    failed_ids.append(evidence_id)
            except Exception:
                failed_count += 1
                failed_ids.append(evidence_id)

        if updated_count > 0:
            await db.commit()

        return updated_count, failed_count, failed_ids
