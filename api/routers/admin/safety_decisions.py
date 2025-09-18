from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from api.dependencies.rbac_auth import UserWithRoles, require_permission
from database.db_setup import get_db
from database.safety_decision import SafetyDecision
from database.user import User  # for typing in annotations
from database.business_profile import BusinessProfile  # for typing
from database.chat_conversation import ChatConversation  # for typing

from database.services.safety_decision_service import sign_jsonl_line

router = APIRouter(prefix="/api/v1/admin/safety-decisions", tags=["admin", "safety-decisions"])


def _apply_filters(
    query,
    org_id: Optional[str],
    business_profile_id: Optional[UUID],
    user_id: Optional[UUID],
    conversation_id: Optional[UUID],
    content_type: Optional[str],
    decision: Optional[str],
    start_at: Optional[datetime],
    end_at: Optional[datetime],
):
    if org_id:
        query = query.filter(SafetyDecision.org_id == org_id)
    if business_profile_id:
        query = query.filter(SafetyDecision.business_profile_id == business_profile_id)
    if user_id:
        query = query.filter(SafetyDecision.user_id == user_id)
    if conversation_id:
        query = query.filter(SafetyDecision.conversation_id == conversation_id)
    if content_type:
        query = query.filter(SafetyDecision.content_type == content_type)
    if decision:
        query = query.filter(SafetyDecision.decision == decision)
    if start_at:
        query = query.filter(SafetyDecision.created_at >= start_at)
    if end_at:
        query = query.filter(SafetyDecision.created_at <= end_at)
    return query


@router.get("/", response_model=List[Dict[str, Any]])
async def list_safety_decisions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    org_id: Optional[str] = Query(None),
    business_profile_id: Optional[UUID] = Query(None),
    user_id: Optional[UUID] = Query(None),
    conversation_id: Optional[UUID] = Query(None),
    content_type: Optional[str] = Query(None),
    decision: Optional[str] = Query(None),
    start_at: Optional[datetime] = Query(None),
    end_at: Optional[datetime] = Query(None),
    current_user: UserWithRoles = Depends(require_permission("admin_audit")),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    query = db.query(SafetyDecision)
    query = _apply_filters(
        query,
        org_id,
        business_profile_id,
        user_id,
        conversation_id,
        content_type,
        decision,
        start_at,
        end_at,
    )
    offset = (page - 1) * limit
    rows = query.order_by(desc(SafetyDecision.created_at)).offset(offset).limit(limit).all()
    return [r.to_dict() for r in rows]


@router.get("/export")
async def export_safety_decisions_jsonl(
    org_id: Optional[str] = Query(None),
    business_profile_id: Optional[UUID] = Query(None),
    user_id: Optional[UUID] = Query(None),
    conversation_id: Optional[UUID] = Query(None),
    content_type: Optional[str] = Query(None),
    decision: Optional[str] = Query(None),
    start_at: Optional[datetime] = Query(None),
    end_at: Optional[datetime] = Query(None),
    limit: int = Query(10000, ge=1, le=100000),
    current_user: UserWithRoles = Depends(require_permission("admin_audit")),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    query = db.query(SafetyDecision)
    query = _apply_filters(
        query,
        org_id,
        business_profile_id,
        user_id,
        conversation_id,
        content_type,
        decision,
        start_at,
        end_at,
    )
    query = query.order_by(desc(SafetyDecision.created_at)).limit(limit)

    def generate():
        # stream results line-by-line
        for row in query.yield_per(1000):
            record = row.to_dict()
            line_bytes = json.dumps(record, separators=(",", ":"), sort_keys=True).encode("utf-8")
            sig = sign_jsonl_line(line_bytes)
            envelope = {"record": record, "sig": sig, "alg": "HS256"}
            yield json.dumps(envelope, separators=(",", ":"), sort_keys=True) + "\n"

    import json
    filename = f"safety_decisions_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jsonl"
    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )