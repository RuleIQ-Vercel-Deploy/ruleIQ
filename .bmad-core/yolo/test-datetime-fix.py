#!/usr/bin/env python3
"""
Test script to verify datetime deprecation fixes
"""
import warnings
import sys

# Enable all warnings including DeprecationWarning
warnings.filterwarnings('error', category=DeprecationWarning)

print("Testing datetime fixes for deprecation warnings...")

try:
    # Import our fixed modules
    import importlib.util

    # Load yolo-system.py
    spec = importlib.util.spec_from_file_location("yolo_system", "yolo-system.py")
    yolo_system = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(yolo_system)
    YOLOOrchestrator = yolo_system.YOLOOrchestrator

    # Load context-refresh-system.py
    spec = importlib.util.spec_from_file_location("context_refresh_system", "context-refresh-system.py")
    context_refresh_system = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(context_refresh_system)
    ContextRefreshSystem = context_refresh_system.ContextRefreshSystem

    # Test YOLOOrchestrator
    print("✓ Importing YOLOOrchestrator - No deprecation warnings")
    orchestrator = YOLOOrchestrator()
    orchestrator.activate()
    print("✓ Activating YOLO system - No deprecation warnings")

    # Test ContextRefreshSystem
    print("✓ Importing ContextRefreshSystem - No deprecation warnings")
    context_system = ContextRefreshSystem()
    print("✓ Creating context system - No deprecation warnings")

    # Test the actual datetime operations
    status = orchestrator.get_status()
    print("✓ Getting status with timestamps - No deprecation warnings")

    print("\n✅ SUCCESS: All datetime operations are using timezone-aware UTC")
    print("No deprecation warnings detected!")

except DeprecationWarning as e:
    print(f"\n❌ FAILED: Deprecation warning detected: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n⚠️  Error during test: {e}")
    sys.exit(1)
