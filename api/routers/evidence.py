from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from api.dependencies.auth import get_current_active_user
from api.schemas.models import EvidenceItemCreate, EvidenceItemResponse, EvidenceItemUpdate
from database.user import User
from services.evidence_service import (
    create_evidence_item,
    get_evidence_by_id,
    get_user_evidence,
    update_evidence_status,
    upload_evidence_file,
)

router = APIRouter()

@router.post("/", response_model=EvidenceItemResponse)
async def create_evidence(
    evidence: EvidenceItemCreate,
    current_user: User = Depends(get_current_active_user)
):
    item = create_evidence_item(current_user, evidence)
    return item

@router.get("/", response_model=List[EvidenceItemResponse])
async def list_evidence(
    framework_id: Optional[UUID] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    evidence = get_user_evidence(current_user, framework_id, status)
    return evidence

@router.get("/{evidence_id}", response_model=EvidenceItemResponse)
async def get_evidence(
    evidence_id: UUID,
    current_user: User = Depends(get_current_active_user)
):
    evidence = get_evidence_by_id(current_user, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence

@router.put("/{evidence_id}", response_model=EvidenceItemResponse)
async def update_evidence(
    evidence_id: UUID,
    update_data: EvidenceItemUpdate,
    current_user: User = Depends(get_current_active_user)
):
    evidence = update_evidence_status(current_user, evidence_id, update_data)
    return evidence

@router.post("/{evidence_id}/upload")
async def upload_file(
    evidence_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    result = await upload_evidence_file(current_user, evidence_id, file)
    return result
