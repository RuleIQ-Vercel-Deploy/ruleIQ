"""Minimal database initialization for testing"""
import sys
from pathlib import Path
import logging
logger = logging.getLogger(__name__)
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
try:
    from database.db_setup import get_db_engine, Base
    from sqlalchemy import text
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        logger.info('✅ Database connection successful')
except Exception as e:
    logger.info('⚠️ Database initialization failed: %s' % e)
    logger.info('Continuing with test setup...')
