"""
Debug AI chat conversation creation by testing ComplianceAssistant directly
"""
import logging
logger = logging.getLogger(__name__)
import asyncio
import sys
sys.path.append('/home/omar/Documents/ruleIQ')
from database.db_setup import get_async_db
from database.user import User
from database.business_profile import BusinessProfile
from services.ai import ComplianceAssistant
from sqlalchemy.future import select
import uuid

async def debug_ai_chat() ->None:
    """Debug the AI chat conversation creation by testing each step"""
    async for db in get_async_db():
        try:
            logger.info(
                '🔍 Debug: Testing AI chat conversation creation step by step')
            logger.info('Step 1: Getting test user...')
            result = await db.execute(select(User).where(User.email ==
                'test@ruleiq.dev'))
            user = result.scalars().first()
            if not user:
                logger.info('❌ Test user not found')
                return
            logger.info('✅ User found: %s' % user.email)
            logger.info('Step 2: Getting business profile...')
            profile_result = await db.execute(select(BusinessProfile).where
                (BusinessProfile.user_id == str(user.id)))
            business_profile = profile_result.scalars().first()
            if not business_profile:
                logger.info('❌ Business profile not found')
                return
            logger.info('✅ Business profile found: %s' % business_profile.
                company_name)
            logger.info('Step 3: Initializing ComplianceAssistant...')
            try:
                assistant = ComplianceAssistant(db)
                logger.info('✅ ComplianceAssistant initialized successfully')
            except Exception as e:
                logger.info(
                    '❌ Failed to initialize ComplianceAssistant: %s' % e)
                logger.info('Exception type: %s' % type(e))
                import traceback
                traceback.print_exc()
                return
            logger.info('Step 4: Testing process_message...')
            try:
                conversation_id = uuid.uuid4()
                test_message = 'Help me understand GDPR requirements'
                logger.info('   Conversation ID: %s' % conversation_id)
                logger.info('   Message: %s' % test_message)
                logger.info('   User ID: %s' % user.id)
                logger.info('   Business Profile ID: %s' % business_profile.id)
                response_task = asyncio.create_task(assistant.
                    process_message(conversation_id=conversation_id, user=
                    user, message=test_message, business_profile_id=
                    business_profile.id))
                logger.info(
                    '   Calling process_message with 10 second timeout...')
                response_text, metadata = await asyncio.wait_for(response_task,
                    timeout=10.0)
                logger.info('✅ process_message completed successfully!')
                logger.info('Response length: %s characters' % len(
                    response_text))
                logger.info('Response preview: %s...' % response_text[:100])
                logger.info('Metadata keys: %s' % list(metadata.keys()))
            except asyncio.TimeoutError:
                logger.info('⚠️  process_message timed out after 10 seconds')
                logger.info('This indicates the AI processing is hanging')
            except Exception as e:
                logger.info('❌ process_message failed: %s' % e)
                logger.info('Exception type: %s' % type(e))
                import traceback
                traceback.print_exc()
            break
        except Exception as e:
            logger.info('❌ Debug failed: %s' % e)
            import traceback
            traceback.print_exc()
            break

if __name__ == '__main__':
    asyncio.run(debug_ai_chat())
