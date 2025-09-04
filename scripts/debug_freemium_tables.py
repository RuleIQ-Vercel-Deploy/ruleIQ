"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Debug script to test freemium table creation and database connectivity.
"""

import os
import sys
import traceback
from sqlalchemy import create_engine, text, inspect
os.environ['ENV'] = 'testing'
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5433/compliance_test?sslmode=require',
    )
sys.path.insert(0, '/home/omar/Documents/ruleIQ')

def main() ->None:
    logger.info('=== Freemium Database Table Debug Script ===')
    """Main"""
    try:
        logger.info('1. Testing Database Connection...')
        db_url = os.environ['DATABASE_URL']
        if '+asyncpg' in db_url:
            db_url = db_url.replace('+asyncpg', '+psycopg2')
        elif 'postgresql://' in db_url and '+psycopg2' not in db_url:
            db_url = db_url.replace('postgresql://',
                'postgresql+psycopg2://', 1)
        engine = create_engine(db_url, echo=True)
        with engine.connect() as conn:
            result = conn.execute(text('SELECT version()'))
            version = result.fetchone()[0]
            logger.info('✅ Database connected: %s' % version)
        logger.info('\n2. Checking existing tables...')
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info('Found %s tables:' % len(tables))
        for table in sorted(tables):
            logger.info('  - %s' % table)
        freemium_tables = ['assessment_leads',
            'freemium_assessment_sessions', 'ai_question_bank',
            'lead_scoring_events', 'conversion_events']
        logger.info('\n3. Checking freemium table status...')
        for table in freemium_tables:
            exists = table in tables
            status = '✅ EXISTS' if exists else '❌ MISSING'
            logger.info('  %s: %s' % (table, status))
        logger.info('\n4. Testing model imports...')
        try:
            from database.assessment_lead import AssessmentLead
            logger.info('✅ AssessmentLead imported successfully')
        except Exception as e:
            logger.info('❌ AssessmentLead import failed: %s' % e)
            traceback.print_exc()
        try:
            logger.info('✅ FreemiumAssessmentSession imported successfully')
        except (ValueError, TypeError) as e:
            logger.info('❌ FreemiumAssessmentSession import failed: %s' % e)
            traceback.print_exc()
        try:
            logger.info('✅ AIQuestionBank imported successfully')
        except (ValueError, TypeError) as e:
            logger.info('❌ AIQuestionBank import failed: %s' % e)
            traceback.print_exc()
        try:
            logger.info('✅ LeadScoringEvent imported successfully')
        except (ValueError, TypeError) as e:
            logger.info('❌ LeadScoringEvent import failed: %s' % e)
            traceback.print_exc()
        try:
            logger.info('✅ ConversionEvent imported successfully')
        except (ValueError, TypeError) as e:
            logger.info('❌ ConversionEvent import failed: %s' % e)
            traceback.print_exc()
        logger.info('\n5. Testing Base.metadata.create_all...')
        try:
            from database.db_setup import Base
            Base.metadata.create_all(bind=engine)
            logger.info('✅ Base.metadata.create_all executed without error')
        except Exception as e:
            logger.info('❌ Base.metadata.create_all failed: %s' % e)
            traceback.print_exc()
        logger.info('\n6. Re-checking tables after create_all...')
        inspector = inspect(engine)
        tables_after = inspector.get_table_names()
        logger.info('Found %s tables after create_all:' % len(tables_after))
        for table in freemium_tables:
            exists = table in tables_after
            status = '✅ EXISTS' if exists else '❌ STILL MISSING'
            logger.info('  %s: %s' % (table, status))
        logger.info('\n7. Testing record creation...')
        try:
            from database.assessment_lead import AssessmentLead
            from sqlalchemy.orm import sessionmaker
            Session = sessionmaker(bind=engine)
            session = Session()
            lead = AssessmentLead(email='debug@test.com', consent_marketing
                =True)
            session.add(lead)
            session.commit()
            logger.info('✅ Test AssessmentLead record created successfully')
            session.delete(lead)
            session.commit()
            session.close()
            logger.info('✅ Test record cleaned up')
        except Exception as e:
            logger.info('❌ Record creation failed: %s' % e)
            traceback.print_exc()
            try:
                session.rollback()
                session.close()
            except (ValueError, TypeError):
                pass
    except (ValueError, TypeError) as e:
        logger.info('❌ Script failed: %s' % e)
        traceback.print_exc()

if __name__ == '__main__':
    main()
