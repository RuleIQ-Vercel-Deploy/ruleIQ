"""Script to fix enum type issues in the database."""
import logging
logger = logging.getLogger(__name__)
from __future__ import annotations
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()

def main() ->None:
    database_url = os.getenv('DATABASE_URL')
    """Main"""
    if not database_url:
        logger.info('ERROR: DATABASE_URL not found in environment variables')
        sys.exit(1)
    engine = create_engine(database_url)
    try:
        with engine.connect() as conn:
            logger.info('Dropping existing integrationstatus enum type...')
            conn.execute(text('DROP TYPE IF EXISTS integrationstatus CASCADE'))
            conn.commit()
            logger.info('Successfully dropped integrationstatus enum type')
    except Exception as e:
        logger.info('ERROR: %s' % e)
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == '__main__':
    main()
