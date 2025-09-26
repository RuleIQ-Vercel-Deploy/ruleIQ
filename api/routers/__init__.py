# api/routers/__init__.py
"""
Router exports for ruleIQ API.
This module exports all available routers to simplify imports in main.py.
"""

import importlib
import logging

logger = logging.getLogger(__name__)

_modules = [
    'auth', 'evidence', 'ai_assessments', 'ai_cost_monitoring', 'ai_cost_websocket',
    'ai_optimization', 'ai_policy', 'assessments', 'business_profiles', 'chat',
    'compliance', 'evidence_collection', 'foundation_evidence', 'frameworks',
    'freemium', 'implementation', 'integrations', 'iq_agent', 'monitoring', 'policies',
    'readiness', 'rbac_auth', 'reports', 'security', 'uk_compliance', 'users'
]

__all__ = []
for name in _modules:
    try:
        globals()[name] = importlib.import_module(f'.{name}', __name__)
        # Optional: validate that module has `router`
        if not hasattr(globals()[name], 'router'):
            logger.warning("Router module '%s' has no 'router' attribute", name)
        __all__.append(name)
    except Exception as e:
        logger.warning("Router '%s' import skipped: %s", name, e)