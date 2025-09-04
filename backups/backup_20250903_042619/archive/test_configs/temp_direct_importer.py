import os
import sys
import logging
logger = logging.getLogger(__name__)


# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

try:
    logger.info("Import successful")
except Exception as e:
    import traceback

    logger.info(f"Import failed: {type(e).__name__}: {e}")
    logger.info(traceback.format_exc())
