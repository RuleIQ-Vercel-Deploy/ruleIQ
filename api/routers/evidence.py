from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_active_user
from api.schemas.models import (
    EvidenceCreate,
    EvidenceResponse,
    EvidenceUpdate,
    EvidenceStatusUpdate,
    EvidenceDashboardResponse,
    EvidenceBulkUpdate,
    EvidenceBulkUpdateResponse,
)
from database.db_setup import get_async_db
from database.user import User
from services.evidence_service import EvidenceService

router = APIRouter()


@router.post("/", status_code=201, response_model=EvidenceResponse)
async def create_new_evidence(
    evidence_data: EvidenceCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new evidence item."""
    evidence = await EvidenceService.create_evidence_item(
        db=db, user=current_user, evidence_data=evidence_data.model_dump()
    )
    # Convert EvidenceItem to expected response format
    return EvidenceService._convert_evidence_item_to_response(evidence)


@router.get("/", response_model=List[EvidenceResponse])
async def list_evidence(
    framework_id: Optional[UUID] = None,
    evidence_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all evidence items for a user with optional filtering."""
    evidence_list = await EvidenceService.list_all_evidence_items(
        db=db,
        user=current_user,
        framework_id=framework_id,
        evidence_type=evidence_type,
        status=status
    )
    # Convert EvidenceItem objects to expected response format
    return [EvidenceService._convert_evidence_item_to_response(item) for item in evidence_list]


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence_details(
    evidence_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve the details of a specific evidence item."""
    evidence, status = await EvidenceService.get_evidence_item_with_auth_check(
        db=db, user_id=current_user.id, evidence_id=evidence_id
    )

    if status == 'not_found':
        raise HTTPException(status_code=404, detail="Evidence not found")
    elif status == 'unauthorized':
        raise HTTPException(status_code=403, detail="Access denied")

    # Convert EvidenceItem to expected response format
    return EvidenceService._convert_evidence_item_to_response(evidence)


@router.put("/{evidence_id}", response_model=EvidenceResponse)
async def update_evidence_item(
    evidence_id: UUID,
    evidence_update: EvidenceUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an evidence item with full or partial data."""
    evidence, status = await EvidenceService.update_evidence_item(
        db=db,
        user=current_user,
        evidence_id=evidence_id,
        update_data=evidence_update.model_dump(exclude_unset=True)
    )

    if status == 'not_found':
        raise HTTPException(status_code=404, detail="Evidence not found")
    elif status == 'unauthorized':
        raise HTTPException(status_code=403, detail="Access denied")

    # Convert EvidenceItem to expected response format
    return EvidenceService._convert_evidence_item_to_response(evidence)


@router.patch("/{evidence_id}", response_model=EvidenceResponse)
async def partial_update_evidence_item(
    evidence_id: UUID,
    evidence_update: EvidenceUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Partially update an evidence item."""
    evidence, status = await EvidenceService.update_evidence_item(
        db=db,
        user=current_user,
        evidence_id=evidence_id,
        update_data=evidence_update.model_dump(exclude_unset=True)
    )

    if status == 'not_found':
        raise HTTPException(status_code=404, detail="Evidence not found")
    elif status == 'unauthorized':
        raise HTTPException(status_code=403, detail="Access denied")

    # Convert EvidenceItem to expected response format
    return EvidenceService._convert_evidence_item_to_response(evidence)


@router.delete("/{evidence_id}", status_code=204)
async def delete_evidence_item(
    evidence_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an evidence item."""
    success, status = await EvidenceService.delete_evidence_item(
        db=db,
        user=current_user,
        evidence_id=evidence_id
    )

    if status == 'not_found':
        raise HTTPException(status_code=404, detail="Evidence not found")
    elif status == 'unauthorized':
        raise HTTPException(status_code=403, detail="Access denied")


@router.post("/bulk-update", response_model=EvidenceBulkUpdateResponse)
async def bulk_update_evidence_status(
    bulk_update: EvidenceBulkUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Bulk update evidence status for multiple items."""
    updated_count, failed_count, failed_ids = await EvidenceService.bulk_update_evidence_status(
        db=db,
        user=current_user,
        evidence_ids=bulk_update.evidence_ids,
        status=bulk_update.status,
        reason=bulk_update.reason
    )

    return EvidenceBulkUpdateResponse(
        updated_count=updated_count,
        failed_count=failed_count,
        failed_ids=failed_ids if failed_ids else None
    )


@router.post("/{evidence_id}/upload", response_model=EvidenceResponse)
async def upload_evidence_file_route(
    evidence_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Upload a file and link it to an evidence item."""
    # Save file to a temporary location (in production, use proper file storage)
    file_path = f"/tmp/{evidence_id}_{file.filename}"

    evidence = await EvidenceService.upload_evidence_file(
        db=db,
        user=current_user,
        evidence_id=evidence_id,
        file_name=file.filename,
        file_path=file_path,
        metadata={"content_type": file.content_type}
    )
    if not evidence:
        raise HTTPException(
            status_code=404, detail="Failed to upload or link file to evidence"
        )
    # Convert EvidenceItem to expected response format
    return EvidenceService._convert_evidence_item_to_response(evidence)


@router.get("/dashboard/{framework_id}", response_model=EvidenceDashboardResponse)
async def get_evidence_dashboard(
    framework_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get dashboard data for evidence collection status."""
    dashboard_data = await EvidenceService.get_evidence_dashboard(
        db=db, user=current_user, framework_id=framework_id
    )
    return dashboard_data
