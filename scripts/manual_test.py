"""Manual test to verify freemium models work with the exact test setup."""
import logging
logger = logging.getLogger(__name__)
from __future__ import annotations
import sys
import os
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ['ENV'] = 'testing'
os.environ['DATABASE_URL'] = (
    'postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require',
    )
os.environ['SECRET_KEY'] = 'test_secret_key_for_pytest_sessions'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Optional
db_url = os.environ['DATABASE_URL']
if '+asyncpg' in db_url:
    db_url = db_url.replace('+asyncpg', '+psycopg2')
elif 'postgresql://' in db_url and '+psycopg2' not in db_url:
    db_url = db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
engine = create_engine(db_url, poolclass=StaticPool, echo=False,
    connect_args={'connect_timeout': 10})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_with_exact_setup() ->Optional[bool]:
    """Test using the exact same setup as pytest conftest."""
    logger.info('=== Using Exact Test Setup ===')
    from database import Base, AssessmentLead
    logger.info('✅ Models imported')
    Base.metadata.create_all(bind=engine)
    logger.info('✅ Tables created')
    session = TestSessionLocal()
    logger.info('✅ Test session created')
    try:
        lead = AssessmentLead(email='manual-test@example.com',
            consent_marketing=True)
        session.add(lead)
        session.commit()
        logger.info('✅ Lead saved: %s' % lead.id)
        saved_lead = session.query(AssessmentLead).filter_by(email=
            'manual-test@example.com').first()
        logger.info('✅ Lead retrieved: %s' % saved_lead)
        session.delete(saved_lead)
        session.commit()
        logger.info('✅ Cleanup completed')
        return True
    except Exception as e:
        logger.info('❌ Test failed: %s' % e)
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

def simulate_pytest_test() ->Optional[bool]:
    """Simulate the exact pytest test that's failing."""
    logger.info('\n=== Simulating Pytest Test ===')
    try:
        from database import AssessmentLead
        session = TestSessionLocal()
        try:
            email = 'test@example.com'
            lead = AssessmentLead(email=email, consent_marketing=True)
            session.add(lead)
            session.commit()
            assert lead.id is not None
            assert lead.email == email
            assert lead.consent_marketing is True
            assert lead.lead_score == 0
            assert lead.created_at is not None
            assert lead.updated_at is not None
            logger.info('✅ Pytest simulation PASSED!')
            session.delete(lead)
            session.commit()
            return True
        except (ValueError, TypeError):
            session.rollback()
            raise
        finally:
            session.close()
    except (ValueError, TypeError) as e:
        logger.info('❌ Pytest simulation FAILED: %s' % e)
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    logger.info('🧪 Manual Test with Exact Setup')
    success1 = test_with_exact_setup()
    success2 = simulate_pytest_test()
    if success1 and success2:
        logger.info('\n🎉 Both tests PASSED! The models work correctly.')
        logger.info(
            'The issue might be with pytest configuration or environment.')
    else:
        logger.info('\n❌ Tests failed. Check errors above.')
    sys.exit(0 if success1 and success2 else 1)
