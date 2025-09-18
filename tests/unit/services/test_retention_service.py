from __future__ import annotations

from database.services.retention_service import get_retention_days_for_org, is_auto_purge_enabled

def test_retention_defaults_from_config():
    days = get_retention_days_for_org(None)
    assert isinstance(days, int)
    assert days >= 1  # from config/privacy.yml default_days: 365 by default

def test_retention_tenant_override_from_config():
    days = get_retention_days_for_org("acme_corp")
    # In config/privacy.yml, acme_corp override sets default_days: 730
    # If config changes, keep the assertion flexible but ensure override applies
    assert days >= 365
    assert days != get_retention_days_for_org(None)

def test_auto_purge_enabled_flag():
    flag = is_auto_purge_enabled()
    assert isinstance(flag, bool)