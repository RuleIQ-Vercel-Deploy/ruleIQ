from __future__ import annotations

from typing import Any, Dict, Optional

import os
import tempfile
import yaml
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from api.dependencies.rbac_auth import UserWithRoles, require_permission

router = APIRouter(prefix="/api/v1/admin/privacy", tags=["admin", "privacy"])

PRIVACY_CONFIG_PATH = os.path.join("config", "privacy.yml")


def _load_config() -> Dict[str, Any]:
    try:
        with open(PRIVACY_CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read privacy config: {e!s}")


def _atomic_write_yaml(data: Dict[str, Any]) -> None:
    try:
        # atomic write
        fd, tmp_path = tempfile.mkstemp(prefix="privacy_", suffix=".yml", dir=os.path.dirname(PRIVACY_CONFIG_PATH) or None)
        os.close(fd)
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False)
        os.replace(tmp_path, PRIVACY_CONFIG_PATH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write privacy config: {e!s}")


class RetentionDefaultsUpdate(BaseModel):
    default_days: int
    auto_purge_enabled: Optional[bool] = None


class TenantRetentionUpdate(BaseModel):
    default_days: int


@router.get("/config", dependencies=[Depends(require_permission("admin_audit"))])
async def get_privacy_config() -> Dict[str, Any]:
    """
    Return the parsed privacy.yml as JSON.
    Note: comments are not preserved in YAML -> JSON conversion.
    """
    return _load_config()


@router.get("/retention", dependencies=[Depends(require_permission("admin_audit"))])
async def get_retention(defaults_only: bool = False, tenant: Optional[str] = None) -> Dict[str, Any]:
    """
    Get retention settings.
    - defaults_only: return only defaults.retention
    - tenant: return effective and override values for a specific tenant
    """
    cfg = _load_config()
    defaults = (cfg.get("defaults") or {}).get("retention") or {}
    result: Dict[str, Any] = {"defaults": {"default_days": defaults.get("default_days", 365), "auto_purge_enabled": defaults.get("auto_purge_enabled", True)}}
    if defaults_only:
        return result
    if tenant:
        overrides = (cfg.get("overrides") or {}).get("tenants") or {}
        t = overrides.get(tenant) or {}
        tret = (t.get("retention") or {})
        effective_days = int(tret.get("default_days", defaults.get("default_days", 365)))
        result["tenant"] = {"id": tenant, "override": {"default_days": tret.get("default_days")}, "effective_days": effective_days}
    return result


@router.put("/retention", dependencies=[Depends(require_permission("admin_audit"))])
async def update_retention_defaults(payload: RetentionDefaultsUpdate) -> Dict[str, Any]:
    """
    Update defaults.retention in privacy.yml.
    """
    cfg = _load_config()
    cfg.setdefault("defaults", {})
    cfg["defaults"].setdefault("retention", {})
    cfg["defaults"]["retention"]["default_days"] = int(payload.default_days)
    if payload.auto_purge_enabled is not None:
        cfg["defaults"]["retention"]["auto_purge_enabled"] = bool(payload.auto_purge_enabled)
    _atomic_write_yaml(cfg)
    return {"updated": True, "defaults": cfg["defaults"]["retention"]}


@router.put("/retention/tenant/{tenant_id}", dependencies=[Depends(require_permission("admin_audit"))])
async def update_tenant_retention(tenant_id: str = Path(...), payload: TenantRetentionUpdate = None) -> Dict[str, Any]:
    """
    Update overrides.tenants.<tenant_id>.retention.default_days in privacy.yml.
    """
    if payload is None:
        raise HTTPException(status_code=400, detail="Missing payload")
    cfg = _load_config()
    cfg.setdefault("overrides", {})
    cfg["overrides"].setdefault("tenants", {})
    cfg["overrides"]["tenants"].setdefault(tenant_id, {})
    cfg["overrides"]["tenants"][tenant_id].setdefault("retention", {})
    cfg["overrides"]["tenants"][tenant_id]["retention"]["default_days"] = int(payload.default_days)
    _atomic_write_yaml(cfg)
    return {"updated": True, "tenant": tenant_id, "retention": cfg["overrides"]["tenants"][tenant_id]["retention"]}