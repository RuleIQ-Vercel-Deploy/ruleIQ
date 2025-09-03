"""
Assign business_user role to a specific test user for API testing
"""
import logging
logger = logging.getLogger(__name__)
import asyncio
import asyncpg
import os
from dotenv import load_dotenv
load_dotenv()

async def assign_user_role() ->bool:
    """Assign business_user role to the test user"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.info('❌ DATABASE_URL not found in environment variables')
        return False
    try:
        conn = await asyncpg.connect(database_url)
        logger.info('✅ Connected to database')
        user_email = 'test-1754509023483@debugtest.com'
        user_result = await conn.fetchrow(
            'SELECT id FROM users WHERE email = $1', user_email)
        if not user_result:
            logger.info('❌ User not found: %s' % user_email)
            await conn.close()
            return False
        user_id = user_result['id']
        logger.info('✅ Found user: %s (ID: %s)' % (user_email, user_id))
        role_result = await conn.fetchrow(
            "SELECT id FROM rbac_roles WHERE name = 'business_user'")
        if not role_result:
            logger.info('❌ business_user role not found')
            await conn.close()
            return False
        role_id = role_result['id']
        logger.info('✅ Found business_user role (ID: %s)' % role_id)
        existing_assignment = await conn.fetchrow(
            'SELECT id FROM rbac_user_roles WHERE user_id = $1 AND role_id = $2'
            , user_id, role_id)
        if existing_assignment:
            logger.info('ℹ️  User already has business_user role assigned')
        else:
            await conn.execute(
                'INSERT INTO rbac_user_roles (user_id, role_id) VALUES ($1, $2)'
                , user_id, role_id)
            logger.info('✅ Successfully assigned business_user role to user')
        permissions_query = """
        SELECT DISTINCT p.name
        FROM rbac_permissions p
        JOIN rbac_role_permissions rp ON p.id = rp.permission_id
        JOIN rbac_user_roles ur ON rp.role_id = ur.role_id
        WHERE ur.user_id = $1
        ORDER BY p.name
        """
        permissions = await conn.fetch(permissions_query, user_id)
        permission_names = [p['name'] for p in permissions]
        logger.info('\n✅ User now has %s permissions:' % len(permission_names))
        for perm in permission_names[:10]:
            logger.info('   - %s' % perm)
        if len(permission_names) > 10:
            logger.info('   ... and %s more' % (len(permission_names) - 10))
        assessment_perms = [p for p in permission_names if 'assessment' in p]
        if assessment_perms:
            logger.info('\n🎯 Assessment permissions found:')
            for perm in assessment_perms:
                logger.info('   - %s' % perm)
        else:
            logger.info('\n⚠️  No assessment permissions found')
        await conn.close()
        logger.info('\n✅ Role assignment completed successfully')
        return True
    except Exception as e:
        logger.info('❌ Error: %s' % e)
        return False

if __name__ == '__main__':
    success = asyncio.run(assign_user_role())
    exit(0 if success else 1)
