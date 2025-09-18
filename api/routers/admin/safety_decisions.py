from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, asc

from api.dependencies.rbac_auth import UserWithRoles, require_permission
from database.db_setup import get_db
from database.safety_decision import SafetyDecision
from database.user import User  # for typing in annotations
from database.business_profile import BusinessProfile  # for typing
from database.chat_conversation import ChatConversation  # for typing

from database.services.safety_decision_service import sign_jsonl_line, compute_record_hash
from database.services.retention_service import (
    preview_retention,
    run_purge,
    run_redaction,
    get_retention_days_for_org,
    is_auto_purge_enabled,
)

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


@router.get("/export.csv")
async def export_safety_decisions_csv(
    org_id: Optional[str] = Query(None),
    business_profile_id: Optional[UUID] = Query(None),
    user_id: Optional[UUID] = Query(None),
    conversation_id: Optional[UUID] = Query(None),
    content_type: Optional[str] = Query(None),
    decision: Optional[str] = Query(None),
    start_at: Optional[datetime] = Query(None),
    end_at: Optional[datetime] = Query(None),
    limit: int = Query(100000, ge=1, le=500000),
    current_user: UserWithRoles = Depends(require_permission("admin_audit")),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    import csv
    import io
    import json

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

    headers = [
        "id",
        "org_id",
        "business_profile_id",
        "user_id",
        "conversation_id",
        "content_type",
        "decision",
        "confidence",
        "applied_filters",
        "request_hash",
        "prev_hash",
        "record_hash",
        "created_at",
        "metadata",
    ]

    def generate():
        # header
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(headers)
        yield buf.getvalue()
        buf.seek(0)
        buf.truncate(0)
        # rows
        for row in query.yield_per(1000):
            d = row.to_dict()
            out = [
                d.get("id"),
                d.get("org_id"),
                d.get("business_profile_id"),
                d.get("user_id"),
                d.get("conversation_id"),
                d.get("content_type"),
                d.get("decision"),
                d.get("confidence"),
                json.dumps(d.get("applied_filters", []), separators=(",", ":"), sort_keys=True),
                d.get("request_hash"),
                d.get("prev_hash"),
                d.get("record_hash"),
                d.get("created_at"),
                json.dumps(d.get("metadata", {}), separators=(",", ":"), sort_keys=True),
            ]
            writer.writerow(out)
            yield buf.getvalue()
            buf.seek(0)
            buf.truncate(0)

    filename = f"safety_decisions_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _chain_key(row: SafetyDecision) -> Tuple[str, Optional[str]]:
    if row.org_id:
        return ("org_id", row.org_id)
    if row.business_profile_id:
        return ("business_profile_id", str(row.business_profile_id))
    if row.user_id:
        return ("user_id", str(row.user_id))
    if row.conversation_id:
        return ("conversation_id", str(row.conversation_id))
    return ("none", None)


@router.get("/verify-chain")
async def verify_chain_integrity(
    org_id: Optional[str] = Query(None),
    business_profile_id: Optional[UUID] = Query(None),
    user_id: Optional[UUID] = Query(None),
    conversation_id: Optional[UUID] = Query(None),
    content_type: Optional[str] = Query(None),
    decision: Optional[str] = Query(None),
    start_at: Optional[datetime] = Query(None),
    end_at: Optional[datetime] = Query(None),
    limit: int = Query(100000, ge=1, le=500000),
    current_user: UserWithRoles = Depends(require_permission("admin_audit")),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    import json

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
    query = query.order_by(asc(SafetyDecision.created_at), asc(SafetyDecision.id)).limit(limit)

    last_hash: Dict[Tuple[str, Optional[str]], Optional[str]] = {}
    chains_stats: Dict[Tuple[str, Optional[str]], Dict[str, int]] = {}
    breaks: List[Dict[str, Any]] = []
    scanned = 0

    def recompute_row_hash(row: SafetyDecision) -> str:
        payload = {
            "id": str(row.id),
            "org_id": row.org_id,
            "business_profile_id": str(row.business_profile_id) if row.business_profile_id else None,
            "user_id": str(row.user_id) if row.user_id else None,
            "conversation_id": str(row.conversation_id) if row.conversation_id else None,
            "content_type": row.content_type,
            "decision": row.decision,
            "confidence": float(row.confidence) if row.confidence is not None else None,
            "applied_filters": row.applied_filters or [],
            "request_hash": row.request_hash,
            "prev_hash": row.prev_hash,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "metadata": row.metadata or {},
        }
        return compute_record_hash(payload, row.prev_hash)

    # Iterate and verify
    for row in query.yield_per(2000):
        scanned += 1
        key = _chain_key(row)
        if key not in chains_stats:
            chains_stats[key] = {"count": 0, "breaks": 0}
        chains_stats[key]["count"] += 1

        # Verify record_hash
        recomputed = recompute_row_hash(row)
        if recomputed != row.record_hash:
            breaks.append(
                {
                    "id": str(row.id),
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "type": "record_hash_mismatch",
                    "expected": recomputed,
                    "actual": row.record_hash,
                }
            )
            chains_stats[key]["breaks"] += 1

        # Verify prev linkage
        expected_prev = last_hash.get(key)
        if expected_prev is None:
            # first in our scan; check if DB has prior record for this chain (if scope is defined)
            scope, value = key
            db_prev = None
            if scope != "none":
                prior_q = db.query(SafetyDecision.record_hash).filter(getattr(SafetyDecision, scope) == (value if value is not None else None))
                prior_q = prior_q.filter(SafetyDecision.created_at < row.created_at).order_by(desc(SafetyDecision.created_at)).limit(1)
                prior = prior_q.first()
                db_prev = prior[0] if prior else None
            if (db_prev or row.prev_hash) and db_prev != row.prev_hash:
                breaks.append(
                    {
                        "id": str(row.id),
                        "created_at": row.created_at.isoformat() if row.created_at else None,
                        "type": "prev_link_mismatch_db",
                        "expected": db_prev,
                        "actual": row.prev_hash,
                    }
                )
                chains_stats[key]["breaks"] += 1
        else:
            if row.prev_hash != expected_prev:
                breaks.append(
                    {
                        "id": str(row.id),
                        "created_at": row.created_at.isoformat() if row.created_at else None,
                        "type": "prev_link_mismatch",
                        "expected": expected_prev,
                        "actual": row.prev_hash,
                    }
                )
                chains_stats[key]["breaks"] += 1

        last_hash[key] = row.record_hash

    valid = len(breaks) == 0
    chains_summary = [
        {"scope": k[0], "key": k[1], "count": v["count"], "breaks": v["breaks"]} for k, v in chains_stats.items()
    ]
    return {"valid": valid, "scanned": scanned, "breaks": breaks, "chains": chains_summary}


@router.get("/retention/preview")
async def preview_retention_candidates(
    org_id: Optional[str] = Query(None),
    days: Optional[int] = Query(None, ge=1),
    current_user: UserWithRoles = Depends(require_permission("admin_audit")),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return preview_retention(db, org_id=org_id, days=days)


@router.post("/retention/run")
async def run_retention_task(
    org_id: Optional[str] = Query(None),
    days: Optional[int] = Query(None, ge=1),
    dry_run: bool = Query(False),
    redact: bool = Query(False),
    redact_days: int = Query(30, ge=1),
    current_user: UserWithRoles = Depends(require_permission("admin_audit")),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    purge = run_purge(db, org_id=org_id, days=days, dry_run=dry_run)
    redaction = {"redacted": 0, "candidates": 0, "dry_run": dry_run}
    if redact:
        redaction = run_redaction(db, org_id=org_id, redact_days=redact_days, dry_run=dry_run)
    return {
        "purge": purge,
        "redaction": redaction,
        "auto_purge_enabled": is_auto_purge_enabled(),
        "default_days_for_org": get_retention_days_for_org(org_id),
    }