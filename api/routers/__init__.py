# api/routers/__init__.py
"""
Router exports for ruleIQ API.
This module exports all available routers to simplify imports in main.py.
"""

import importlib
import logging
import types
from typing import Any, List
from fastapi import APIRouter

logger = logging.getLogger(__name__)

_modules = [
    'auth', 'evidence', 'ai_assessments', 'ai_cost_monitoring', 'ai_cost_websocket',
    'ai_optimization', 'ai_policy', 'assessments', 'business_profiles', 'chat',
    'compliance', 'evidence_collection', 'foundation_evidence', 'frameworks',
    'freemium', 'implementation', 'integrations', 'iq_agent', 'monitoring', 'policies',
    'readiness', 'rbac_auth', 'reports', 'security', 'uk_compliance', 'users'
]

__all__: List[str] = []
_failed_imports: List[str] = []
_successful_imports: List[str] = []

for name in _modules:
    try:
        # Import the module
        module = importlib.import_module(f'.{name}', __name__)
        
        # Validate that module has required 'router' attribute
        if not hasattr(module, 'router'):
            logger.warning(
                "Router module 'api.routers.%s' imported but has no 'router' attribute",
                name
            )
            _failed_imports.append(name)
            # Create a placeholder with minimal router to prevent import errors in main.py
            placeholder = types.SimpleNamespace(
                module_name=name,
                router=APIRouter()  # Minimal router prevents attribute errors
            )
            globals()[name] = placeholder
        else:
            globals()[name] = module
            _successful_imports.append(name)
            logger.debug("Successfully imported router module: api.routers.%s", name)
            
        # Always add to __all__ to maintain expected exports
        __all__.append(name)
        
    except (ImportError, ModuleNotFoundError) as e:
        logger.error(
            "Failed to import router module 'api.routers.%s': %s",
            name, e
        )
        _failed_imports.append(name)
        
        # Create a placeholder module to prevent cascading import failures
        # Use SimpleNamespace with a minimal router to prevent startup crashes
        placeholder = types.SimpleNamespace(
            module_name=name,
            router=APIRouter()  # Minimal router prevents attribute errors
        )
        globals()[name] = placeholder
        __all__.append(name)  # Still export to prevent KeyError
        
    except Exception as e:
        logger.error(
            "Unexpected error importing router module 'api.routers.%s': %s", 
            name, e
        )
        _failed_imports.append(name)
        
        # Create a placeholder module with a minimal router
        placeholder = types.SimpleNamespace(
            module_name=name,
            router=APIRouter()  # Minimal router prevents attribute errors
        )
        globals()[name] = placeholder
        __all__.append(name)

# Log summary of imports
if _successful_imports:
    logger.info(
        "Successfully imported %d/%d router modules: %s",
        len(_successful_imports), len(_modules), ', '.join(_successful_imports[:5])
    )
    
if _failed_imports:
    logger.warning(
        "Failed to import %d/%d router modules: %s",
        len(_failed_imports), len(_modules), ', '.join(_failed_imports)
    )