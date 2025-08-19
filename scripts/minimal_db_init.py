#!/usr/bin/env python3
"""Minimal database initialization for testing"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from database.db_setup import get_db_engine, Base
    from sqlalchemy import text

    # Create tables
    engine = get_db_engine()
    Base.metadata.create_all(engine)

    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")

except Exception as e:
    print(f"⚠️ Database initialization failed: {e}")
    print("Continuing with test setup...")
