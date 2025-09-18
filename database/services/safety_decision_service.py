from __future__ import annotations

import hashlib
import hmac
import json
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Sequence

from sqlalchemy import and_, desc, select
from sqlalchemy.orm import Session

from database.db_setup import get_db_context
from database.safety_decision import SafetyDecision
from config.settings import settings


def _canonical_dumps(data: Dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_request_hash(
    *,
    input_content: str,
    response_content: str,
    content_type: str,
    user_id: Optional[str],
    session_id: Optional[str],
    applied_filters: Sequence[str],
) -> str:
    payload = {
        "input": input_content[:1024],
        "response": response_content[:2048],
        "type": content_type,
        "user_id": str(user_id) if user_id else None,
        "session_id": str(session_id) if session_id else None,
        "filters": list(applied_filters or []),
    }
    digest = hashlib.sha256(_canonical_dumps(payload).encode("utf-8")).hexdigest()
    return digest


def compute_record_hash(payload: Dict[str, Any], prev_hash: Optional[str]) -> str:
    data = {**payload, "prev_hash": prev_hash}
    # Do not include record_hash itself
    data.pop("record_hash", None)
    return hashlib.sha256(_canonical_dumps(data).encode("utf-8")).hexdigest()


def _get_prev_hash(db: Session, org_id: Optional[str], business_profile_id: Optional[str], user_id: Optional[str], conversation_id: Optional[str]) -> Optional[str]:
    q = None
    if org_id:
        q = db.query(SafetyDecision.record_hash).filter(SafetyDecision.org_id == org_id).order_by(desc(SafetyDecision.created_at)).limit(1)
    elif business_profile_id:
        q = db.query(SafetyDecision.record_hash).filter(SafetyDecision.business_profile_id == business_profile_id).order_by(desc(SafetyDecision.created_at)).limit(1)
    elif user_id:
        q = db.query(SafetyDecision.record_hash).filter(SafetyDecision.user_id == user_id).order_by(desc(SafetyDecision.created_at)).limit(1)
    elif conversation_id:
        q = db.query(SafetyDecision.record_hash).filter(SafetyDecision.conversation_id == conversation_id).order_by(desc(SafetyDecision.created_at)).limit(1)

    if q is None:
        return None
    row = q.first()
    return row[0] if row else None


def persist_safety_decision(
    *,
    org_id: Optional[str],
    business_profile_id: Optional[str],
    user_id: Optional[str],
    conversation_id: Optional[str],
    content_type: str,
    decision: str,
    confidence: Optional[float],
    applied_filters: Sequence[str],
    request_hash: str,
    metadata: Dict[str, Any],
    created_at: Optional[datetime] = None,
) -> Optional[str]:
    created = created_at or datetime.now(timezone.utc)
    # Compute prev_hash and record_hash
    try:
        with get_db_context() as db:
            prev = _get_prev_hash(
                db=db,
                org_id=org_id,
                business_profile_id=str(business_profile_id) if business_profile_id else None,
                user_id=str(user_id) if user_id else None,
                conversation_id=str(conversation_id) if conversation_id else None,
            )
            model_payload = {
                "id": str(uuid.uuid4()),
                "org_id": org_id,
                "business_profile_id": str(business_profile_id) if business_profile_id else None,
                "user_id": str(user_id) if user_id else None,
                "conversation_id": str(conversation_id) if conversation_id else None,
                "content_type": content_type,
                "decision": decision,
                "confidence": float(confidence) if confidence is not None else None,
                "applied_filters": list(applied_filters or []),
                "request_hash": request_hash,
                "prev_hash": prev,
                "created_at": created.isoformat(),
                "metadata": metadata or {},
            }
            record_hash = compute_record_hash(model_payload, prev)
            obj = SafetyDecision(
                id=uuid.UUID(model_payload["id"]),
                org_id=org_id,
                business_profile_id=uuid.UUID(model_payload["business_profile_id"]) if model_payload["business_profile_id"] else None,
                user_id=uuid.UUID(model_payload["user_id"]) if model_payload["user_id"] else None,
                conversation_id=uuid.UUID(model_payload["conversation_id"]) if model_payload["conversation_id"] else None,
                content_type=content_type,
                decision=decision,
                confidence=confidence,
                applied_filters=list(applied_filters or []),
                request_hash=request_hash,
                prev_hash=prev,
                record_hash=record_hash,
                created_at=created,
                metadata=metadata or {},
            )
            db.add(obj)
            # db.commit() handled by context manager
            return record_hash
    except Exception:
        # Do not raise in hot path
        return None


def persist_safety_decision_background(**kwargs: Any) -> None:
    threading.Thread(target=persist_safety_decision, kwargs=kwargs, daemon=True).start()


def sign_jsonl_line(line_bytes: bytes) -> str:
    key = settings.jwt_secret_key.encode("utf-8")
    sig = hmac.new(key, line_bytes, hashlib.sha256).hexdigest()
    return sig