#!/usr/bin/env python3
"""Debug database connection."""
import logging
logger = logging.getLogger(__name__)

import sys
import os

sys.path.insert(0, ".")
os.environ["ENVIRONMENT"] = "test"

try:
    from database.db_setup import _get_configured_database_urls

    urls = _get_configured_database_urls()
    logger.info(f"URLs: {urls}")
except Exception as e:
    logger.info(f"Error: {e}")
    import traceback

    traceback.print_exc()
