from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import yaml
from sqlalchemy import and_, delete, func
from sqlalchemy.orm import Session

from database.safety_decision import SafetyDecision


def _load_privacy_config() -> Dict[str, Any]:
    try:
        with open("config/privacy.yml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return data
    except Exception:
        return {}


def _get_retention_defaults(cfg: Dict[str, Any]) -> Tuple[int, bool]:
    defaults = cfg.get("defaults", {})
    retention = defaults.get("retention", {})
    days = int(retention.get("default_days", 365))
    auto = bool(retention.get("auto_purge_enabled", True))
    return days, auto


def get_retention_days_for_org(org_id: Optional[str]) -> int:
    cfg = _load_privacy_config()
    days, _ = _get_retention_defaults(cfg)
    if not org_id:
        return days
    overrides = cfg.get("overrides", {}).get("tenants", {})
    tenant = overrides.get(org_id)
    if tenant:
        r = tenant.get("retention", {})
        if "default_days" in r:
            try:
                return int(r["default_days"])
            except Exception:
                pass
    return days


def is_auto_purge_enabled() -> bool:
    cfg = _load_privacy_config()
    _, auto = _get_retention_defaults(cfg)
    return auto


def preview_retention(db: Session, *, org_id: Optional[str], days: Optional[int] = None) -> Dict[str, Any]:
    if days is None:
        days = get_retention_days_for_org(org_id)
    cutoff = datetime.now(timezone.utc) - timedelta(days=int(days))
    q = db.query(func.count(SafetyDecision.id)).filter(SafetyDecision.created_at < cutoff)
    if org_id:
        q = q.filter(SafetyDecision.org_id == org_id)
    count = int(q.scalar() or 0)
    return {"org_id": org_id, "days": int(days), "cutoff": cutoff.isoformat(), "purge_candidates": count}


def run_purge(db: Session, *, org_id: Optional[str], days: Optional[int] = None, dry_run: bool = False) -> Dict[str, Any]:
    if days is None:
        days = get_retention_days_for_org(org_id)
    cutoff = datetime.now(timezone.utc) - timedelta(days=int(days))
    base_q = db.query(SafetyDecision).filter(SafetyDecision.created_at < cutoff)
    if org_id:
        base_q = base_q.filter(SafetyDecision.org_id == org_id)
    to_purge = base_q.count()
    purged = 0
    if not dry_run and to_purge > 0:
        # SQLAlchemy 2.0 ORM delete
        db.query(SafetyDecision).filter(SafetyDecision.created_at < cutoff, *( [SafetyDecision.org_id == org_id] if org_id else [] )).delete(synchronize_session=False)
        db.commit()
        purged = to_purge
    return {"org_id": org_id, "days": int(days), "cutoff": cutoff.isoformat(), "purged": purged, "candidates": to_purge, "dry_run": dry_run}


def run_redaction(db: Session, *, org_id: Optional[str], redact_days: int = 30, dry_run: bool = False) -> Dict[str, Any]:
    """
    Minimal redaction: mask free-text 'reasoning' in metadata and mark metadata.redacted=true
    for rows older than `redact_days`, optionally scoped by org_id.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=int(redact_days))
    q = db.query(SafetyDecision).filter(SafetyDecision.created_at < cutoff)
    if org_id:
        q = q.filter(SafetyDecision.org_id == org_id)

    redacted = 0
    if dry_run:
        # Count rows that would be redacted (that have non-empty reasoning or not marked redacted)
        rows = q.yield_per(1000)
        for row in rows:
            meta = (row.metadata or {})
            if not meta.get("redacted") or ("reasoning" in meta and meta.get("reasoning") not in (None, "", "[REDACTED]")):
                redacted += 1
        return {"org_id": org_id, "redact_days": int(redact_days), "cutoff": cutoff.isoformat(), "redacted": 0, "candidates": redacted, "dry_run": True}

    rows = q.yield_per(500)
    for row in rows:
        meta = dict(row.metadata or {})
        if "reasoning" in meta and meta.get("reasoning") not in (None, "", "[REDACTED]"):
            meta["reasoning"] = "[REDACTED]"
        if not meta.get("redacted"):
            meta["redacted"] = True
            meta["redacted_at"] = datetime.now(timezone.utc).isoformat()
        row.metadata = meta
        redacted += 1
    if redacted:
        db.commit()
    return {"org_id": org_id, "redact_days": int(redact_days), "cutoff": cutoff.isoformat(), "redacted": redacted, "dry_run": False}