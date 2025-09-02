#!/usr/bin/env python3
"""
Debug AI chat conversation creation by testing ComplianceAssistant directly
"""

import asyncio
import sys

sys.path.append("/home/omar/Documents/ruleIQ")

from database.db_setup import get_async_db
from database.user import User
from database.business_profile import BusinessProfile
from services.ai import ComplianceAssistant
from sqlalchemy.future import select
import uuid


async def debug_ai_chat():
    """Debug the AI chat conversation creation by testing each step"""
    async for db in get_async_db():
        try:
            print("🔍 Debug: Testing AI chat conversation creation step by step")

            # Step 1: Get test user
            print("Step 1: Getting test user...")
            result = await db.execute(
                select(User).where(User.email == "test@ruleiq.dev")
            )
            user = result.scalars().first()

            if not user:
                print("❌ Test user not found")
                return

            print(f"✅ User found: {user.email}")

            # Step 2: Get business profile
            print("Step 2: Getting business profile...")
            profile_result = await db.execute(
                select(BusinessProfile).where(BusinessProfile.user_id == str(user.id))
            )
            business_profile = profile_result.scalars().first()

            if not business_profile:
                print("❌ Business profile not found")
                return

            print(f"✅ Business profile found: {business_profile.company_name}")

            # Step 3: Test ComplianceAssistant initialization
            print("Step 3: Initializing ComplianceAssistant...")
            try:
                assistant = ComplianceAssistant(db)
                print("✅ ComplianceAssistant initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize ComplianceAssistant: {e}")
                print(f"Exception type: {type(e)}")
                import traceback

                traceback.print_exc()
                return

            # Step 4: Test process_message
            print("Step 4: Testing process_message...")
            try:
                conversation_id = uuid.uuid4()
                test_message = "Help me understand GDPR requirements"

                print(f"   Conversation ID: {conversation_id}")
                print(f"   Message: {test_message}")
                print(f"   User ID: {user.id}")
                print(f"   Business Profile ID: {business_profile.id}")

                # Set a timeout for testing
                response_task = asyncio.create_task(
                    assistant.process_message(
                        conversation_id=conversation_id,
                        user=user,
                        message=test_message,
                        business_profile_id=business_profile.id,
                    )
                )

                print("   Calling process_message with 10 second timeout...")
                response_text, metadata = await asyncio.wait_for(
                    response_task, timeout=10.0
                )

                print("✅ process_message completed successfully!")
                print(f"Response length: {len(response_text)} characters")
                print(f"Response preview: {response_text[:100]}...")
                print(f"Metadata keys: {list(metadata.keys())}")

            except asyncio.TimeoutError:
                print("⚠️  process_message timed out after 10 seconds")
                print("This indicates the AI processing is hanging")
            except Exception as e:
                print(f"❌ process_message failed: {e}")
                print(f"Exception type: {type(e)}")
                import traceback

                traceback.print_exc()

            break

        except Exception as e:
            print(f"❌ Debug failed: {e}")
            import traceback

            traceback.print_exc()
            break


if __name__ == "__main__":
    asyncio.run(debug_ai_chat())
