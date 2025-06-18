import sys
import os

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    import tests.integration.test_evidence_flow
    print("Import successful")
except Exception as e:
    import traceback
    print(f"Import failed: {type(e).__name__}: {e}")
    print(traceback.format_exc())
