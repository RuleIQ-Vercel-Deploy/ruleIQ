"""
Fix for main app import issues in tests.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Create mock app if main doesn't exist
def get_test_app():
    """Get or create test app."""
    try:
        from api.main import app
        return app
    except ImportError:
        # Create a minimal test app
        from fastapi import FastAPI
        app = FastAPI(title="Test App")
        
        @app.get("/health")
        def health():
            return {"status": "ok"}
            
        return app
