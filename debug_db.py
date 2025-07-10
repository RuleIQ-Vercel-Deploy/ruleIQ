#!/usr/bin/env python3
"""Debug database connection."""

import sys
import os
sys.path.insert(0, '.')
os.environ['ENVIRONMENT'] = 'test'

try:
    from database.db_setup import _get_configured_database_urls
    urls = _get_configured_database_urls()
    print(f"URLs: {urls}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()