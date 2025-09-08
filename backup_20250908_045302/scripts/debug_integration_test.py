"""Debug integration test manually"""
import logging

# Constants
HTTP_OK = 200

logger = logging.getLogger(__name__)
from __future__ import annotations
from typing import Any, Dict, List, Optional
import asyncio
import sys
import os
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch
from dotenv import load_dotenv
load_dotenv('.env.local', override=True)
os.environ.update({'IS_TESTING': 'true'})


def test_ai_help_manually() ->Any:
    """Test the AI help endpoint manually"""
    try:
        from main import app
        from database.db_setup import get_db_session
        from tests.conftest import TEST_USER_ID
        from database.user import User
        from database.business_profile import BusinessProfile
        from api.dependencies.auth import create_access_token, get_password_hash
        from datetime import timedelta
        from services.ai.assistant import ComplianceAssistant
        logger.info('🔄 Setting up test client...')
        client = TestClient(app)
        logger.info('🔄 Setting up database session...')
        from database.db_setup import init_db
        init_db()
        db = next(get_db_session())
        logger.info('🔄 Checking database schema...')
        from sqlalchemy import text
        result = db.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position"
            ))
        columns = [row[0] for row in result]
        logger.info('✅ Columns in users table: %s' % columns)
        logger.info('🔄 Creating test user...')
        existing_user = db.query(User).filter_by(id=TEST_USER_ID).first()
        if not existing_user:
            user = User(id=TEST_USER_ID, email='test@example.com',
                hashed_password=get_password_hash('TestPassword123!'),
                is_active=True)
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user = existing_user
        logger.info('✅ User created/found: %s' % user.email)
        logger.info('🔄 Creating business profile...')
        existing_profile = db.query(BusinessProfile).filter_by(user_id=user.id
            ).first()
        if not existing_profile:
            profile = BusinessProfile(user_id=user.id, company_name=
                'Test Company', industry='Technology', company_size='10-50',
                primary_location='London')
            db.add(profile)
            db.commit()
            db.refresh(profile)
        else:
            profile = existing_profile
        logger.info('✅ Business profile created/found: %s' % profile.
            company_name)
        logger.info('🔄 Creating auth token...')
        token_data = {'sub': str(user.id)}
        auth_token = create_access_token(data=token_data, expires_delta=
            timedelta(minutes=30))
        headers = {'Authorization': f'Bearer {auth_token}'}
        logger.info('✅ Auth token created: %s...' % auth_token[:50])
        request_data = {'question_id': 'q1', 'question_text':
            'What is GDPR compliance?', 'framework_id': 'gdpr',
            'section_id': 'data_protection', 'user_context': {
            'business_profile_id': str(profile.id), 'industry': 'technology'}}
        logger.info('🔄 Testing endpoint with mock...')
        with patch.object(ComplianceAssistant, 'get_assessment_help'
            ) as mock_help:
            mock_help.return_value = {'guidance':
                'GDPR requires organizations to protect personal data...',
                'confidence_score': 0.95, 'related_topics': [
                'data protection', 'privacy rights'],
                'follow_up_suggestions': [
                'What are the key GDPR principles?'], 'source_references':
                ['GDPR Article 5'], 'request_id': 'test-request-id',
                'generated_at': '2024-01-01T00:00:00Z'}
            logger.info('🔄 Making POST request...')
            response = client.post('/api/ai/assessments/gdpr/help', json=
                request_data, headers=headers)
            logger.info('✅ Response status: %s' % response.status_code)
            logger.info('✅ Response headers: %s' % dict(response.headers))
            if response.status_code != HTTP_OK:
                logger.info('❌ Response content: %s' % response.text)
                logger.info('❌ Response JSON: %s' % (response.json() if
                    response.content else 'No content'))
            else:
                response_data = response.json()
                logger.info('✅ Response data keys: %s' % list(response_data
                    .keys()))
                logger.info('✅ Guidance: %s...' % response_data.get(
                    'guidance', 'N/A')[:100])
                assert 'guidance' in response_data
                assert 'confidence_score' in response_data
                assert 'request_id' in response_data
                assert 'generated_at' in response_data
                assert response_data['confidence_score'] >= 0.0
                assert response_data['confidence_score'] <= 1.0
                logger.info('🎉 All assertions passed!')
        db.close()
    except Exception as e:
        logger.info('❌ Test failed with error: %s' % e)
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_ai_help_manually()
