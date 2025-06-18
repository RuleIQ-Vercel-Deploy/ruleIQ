from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_active_user
from api.schemas.models import (
    EvidenceCreate,
    EvidenceResponse,
    EvidenceStatusUpdate,
    EvidenceDashboardResponse,
)
from database.db_setup import get_async_db
from database.user import User
from services.evidence_service import EvidenceService

router = APIRouter()


@router.post("/", response_model=EvidenceResponse)
async def create_new_evidence(
    evidence_data: EvidenceCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new evidence item."""
    evidence = await EvidenceService.create_evidence_item(
        db=db, user=current_user, evidence_data=evidence_data.dict()
    )
    return evidence


@router.get("/", response_model=List[EvidenceResponse])
async def list_evidence(
    framework_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all evidence items for a user and framework."""
    evidence_list = await EvidenceService.list_evidence_items(
        db=db, user=current_user, framework_id=framework_id
    )
    return evidence_list


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence_details(
    evidence_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve the details of a specific evidence item."""
    evidence = await EvidenceService.get_evidence_item(
        db=db, user_id=current_user.id, evidence_id=evidence_id
    )
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


@router.put("/{evidence_id}", response_model=EvidenceResponse)
async def update_evidence_status(
    evidence_id: UUID,
    status_update: EvidenceStatusUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update the status and notes of an evidence item."""
    evidence = await EvidenceService.update_evidence_status(
        db=db,
        user=current_user,
        evidence_id=evidence_id,
        status=status_update.status,
        notes=status_update.notes,
    )
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


@router.post("/{evidence_id}/upload", response_model=EvidenceResponse)
async def upload_evidence_file_route(
    evidence_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Upload a file and link it to an evidence item."""
    # Assuming file content is read and passed to the service method
    file_content = await file.read()
    file_info = {"filename": file.filename, "content_type": file.content_type}

    evidence = await EvidenceService.link_evidence_to_file(
        db=db,
        user_id=current_user.id,
        evidence_id=evidence_id,
        file_info=file_info,
        file_content=file_content,
    )
    if not evidence:
        raise HTTPException(
            status_code=404, detail="Failed to upload or link file to evidence"
        )
    return evidence


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
