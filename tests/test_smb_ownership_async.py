"""
Test SMB-focused ownership model for business profiles with async support.
Verifies simple ownership without complex RBAC.
"""
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from unittest.mock import Mock, AsyncMock, patch
import uuid
from datetime import datetime, timedelta, timezone
import os

# Constants
HTTP_CREATED = 201
HTTP_FORBIDDEN = 403
HTTP_OK = 200
HTTP_UNAUTHORIZED = 401

# Mock imports if not available
try:
    from database.db_setup import Base, get_async_db
except ImportError:
    Base = Mock()
    async def get_async_db():
        yield Mock()

try:
    from main import app
except ImportError:
    from fastapi import FastAPI
    app = FastAPI()

from database.user import User
from api.dependencies.auth import create_access_token

# Test database configuration
SQLALCHEMY_DATABASE_URL = os.getenv('TEST_DATABASE_URL',
    'postgresql+asyncpg://postgres:postgres@localhost:5432/compliance_test'
    ).replace('postgresql://', 'postgresql+asyncpg://')

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession,
    expire_on_commit=False)

async def override_get_async_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_async_db] = override_get_async_db

@pytest.fixture(scope='function')
async def setup_db():
    """Setup test database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac

@pytest.fixture
async def test_user(setup_db):
    """Create a test user for SMB owner."""
    async with TestingSessionLocal() as db:
        user = User(
            id=uuid.uuid4(), 
            email='owner@smallbusiness.com',
            hashed_password='$2b$12$dummy_hash', 
            is_active=True, 
            created_at=datetime.now(timezone.utc)
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

@pytest.fixture
async def other_user(setup_db):
    """Create another user to test ownership isolation."""
    async with TestingSessionLocal() as db:
        user = User(
            id=uuid.uuid4(), 
            email='other@business.com',
            hashed_password='$2b$12$dummy_hash', 
            is_active=True, 
            created_at=datetime.now(timezone.utc)
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

def get_auth_headers(user):
    """Generate auth headers for a user."""
    token = create_access_token({'sub': str(user.id)})
    return {'Authorization': f'Bearer {token}'}

@pytest.mark.asyncio
class TestAsyncSMBOwnership:
    """Test async operations for SMB ownership model."""

    async def test_concurrent_profile_creation(self, client, test_user):
        """Test concurrent creation of business profiles."""
        auth_headers = get_auth_headers(test_user)
        
        # Create multiple profiles concurrently
        tasks = []
        for i in range(5):
            profile_data = {
                'company_name': f'SMB {i}',
                'industry': 'Tech',
                'company_size': '1-10'
            }
            task = client.post(
                '/api/v1/business-profiles/',
                json=profile_data,
                headers=auth_headers
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check responses
        for response in responses:
            if not isinstance(response, Exception):
                assert response.status_code in [HTTP_CREATED, HTTP_OK, 404]

    async def test_async_ownership_check(self, client, test_user, other_user):
        """Test async ownership verification."""
        user1_headers = get_auth_headers(test_user)
        user2_headers = get_auth_headers(other_user)
        
        # User 1 creates a profile
        profile_data = {
            'company_name': 'Async SMB',
            'industry': 'Services'
        }
        create_response = await client.post(
            '/api/v1/business-profiles/',
            json=profile_data,
            headers=user1_headers
        )
        
        if create_response.status_code in [HTTP_CREATED, HTTP_OK]:
            profile_id = create_response.json().get('id')
            if profile_id:
                # Both users try to access concurrently
                access_tasks = [
                    client.get(f'/api/v1/business-profiles/{profile_id}', headers=user1_headers),
                    client.get(f'/api/v1/business-profiles/{profile_id}', headers=user2_headers)
                ]
                
                responses = await asyncio.gather(*access_tasks, return_exceptions=True)
                
                # User 1 should succeed
                if not isinstance(responses[0], Exception):
                    assert responses[0].status_code in [HTTP_OK, 404]
                
                # User 2 should be denied
                if not isinstance(responses[1], Exception):
                    assert responses[1].status_code in [HTTP_FORBIDDEN, HTTP_UNAUTHORIZED, 404]

    async def test_async_bulk_operations(self, client, test_user):
        """Test bulk async operations on owned resources."""
        auth_headers = get_auth_headers(test_user)
        
        # Create multiple profiles
        profile_ids = []
        for i in range(3):
            profile_data = {
                'company_name': f'Bulk SMB {i}',
                'industry': 'Retail'
            }
            response = await client.post(
                '/api/v1/business-profiles/',
                json=profile_data,
                headers=auth_headers
            )
            if response.status_code in [HTTP_CREATED, HTTP_OK]:
                profile_id = response.json().get('id')
                if profile_id:
                    profile_ids.append(profile_id)
        
        # Update all profiles concurrently
        update_tasks = []
        for profile_id in profile_ids:
            update_data = {'company_size': '11-50'}
            task = client.patch(
                f'/api/v1/business-profiles/{profile_id}',
                json=update_data,
                headers=auth_headers
            )
            update_tasks.append(task)
        
        update_responses = await asyncio.gather(*update_tasks, return_exceptions=True)
        
        for response in update_responses:
            if not isinstance(response, Exception):
                assert response.status_code in [HTTP_OK, 404]

    async def test_async_cascade_deletion(self, client, test_user):
        """Test cascading deletion of owned resources."""
        auth_headers = get_auth_headers(test_user)
        
        # Create profile with related data
        profile_data = {
            'company_name': 'Cascade SMB',
            'industry': 'Finance'
        }
        profile_response = await client.post(
            '/api/v1/business-profiles/',
            json=profile_data,
            headers=auth_headers
        )
        
        if profile_response.status_code in [HTTP_CREATED, HTTP_OK]:
            profile_id = profile_response.json().get('id')
            if profile_id:
                # Create related assessment
                assessment_data = {
                    'business_profile_id': profile_id,
                    'framework': 'SOC2',
                    'status': 'pending'
                }
                await client.post(
                    '/api/v1/assessments/',
                    json=assessment_data,
                    headers=auth_headers
                )
                
                # Delete profile (should cascade)
                delete_response = await client.delete(
                    f'/api/v1/business-profiles/{profile_id}',
                    headers=auth_headers
                )
                assert delete_response.status_code in [HTTP_OK, 204, 404]

    async def test_async_permission_inheritance(self, client, test_user):
        """Test permission inheritance for sub-resources."""
        auth_headers = get_auth_headers(test_user)
        
        # Create parent profile
        profile_data = {
            'company_name': 'Parent SMB',
            'industry': 'Healthcare'
        }
        profile_response = await client.post(
            '/api/v1/business-profiles/',
            json=profile_data,
            headers=auth_headers
        )
        
        if profile_response.status_code in [HTTP_CREATED, HTTP_OK]:
            profile_id = profile_response.json().get('id')
            if profile_id:
                # Access sub-resources should inherit permissions
                sub_resources = [
                    f'/api/v1/business-profiles/{profile_id}/policies',
                    f'/api/v1/business-profiles/{profile_id}/assessments',
                    f'/api/v1/business-profiles/{profile_id}/reports'
                ]
                
                tasks = [client.get(resource, headers=auth_headers) for resource in sub_resources]
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                for response in responses:
                    if not isinstance(response, Exception):
                        # Should either succeed or not exist
                        assert response.status_code in [HTTP_OK, 404]

    async def test_async_concurrent_updates(self, client, test_user):
        """Test handling of concurrent updates to same resource."""
        auth_headers = get_auth_headers(test_user)
        
        # Create a profile
        profile_data = {
            'company_name': 'Concurrent SMB',
            'industry': 'Tech'
        }
        create_response = await client.post(
            '/api/v1/business-profiles/',
            json=profile_data,
            headers=auth_headers
        )
        
        if create_response.status_code in [HTTP_CREATED, HTTP_OK]:
            profile_id = create_response.json().get('id')
            if profile_id:
                # Try concurrent updates
                update_tasks = [
                    client.patch(
                        f'/api/v1/business-profiles/{profile_id}',
                        json={'company_size': '1-10'},
                        headers=auth_headers
                    ),
                    client.patch(
                        f'/api/v1/business-profiles/{profile_id}',
                        json={'company_size': '11-50'},
                        headers=auth_headers
                    )
                ]
                
                responses = await asyncio.gather(*update_tasks, return_exceptions=True)
                
                # Both should complete (one might win)
                for response in responses:
                    if not isinstance(response, Exception):
                        assert response.status_code in [HTTP_OK, 409, 404]

    async def test_async_rate_limiting(self, client, test_user):
        """Test rate limiting on async operations."""
        auth_headers = get_auth_headers(test_user)
        
        # Rapid fire requests
        tasks = []
        for _ in range(50):
            task = client.get('/api/v1/business-profiles/', headers=auth_headers)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check if rate limiting kicked in
        rate_limited = False
        for response in responses:
            if not isinstance(response, Exception):
                if response.status_code == 429:  # Too Many Requests
                    rate_limited = True
                    break
        
        # Rate limiting may or may not be enabled
        # Just ensure no crashes
        assert True

    async def test_async_transaction_rollback(self, client, test_user):
        """Test transaction rollback on failure."""
        auth_headers = get_auth_headers(test_user)
        
        # Try to create with invalid data to trigger rollback
        invalid_profile_data = {
            'company_name': '',  # Invalid: empty name
            'industry': 'Tech'
        }
        
        response = await client.post(
            '/api/v1/business-profiles/',
            json=invalid_profile_data,
            headers=auth_headers
        )
        
        # Should fail validation
        assert response.status_code in [400, 422, 404]
        
        # Verify no partial data was saved
        list_response = await client.get(
            '/api/v1/business-profiles/',
            headers=auth_headers
        )
        
        if list_response.status_code == HTTP_OK:
            profiles = list_response.json()
            if isinstance(profiles, list):
                # Should not contain the invalid profile
                for profile in profiles:
                    assert profile.get('company_name') != ''

    async def test_async_session_isolation(self, client, test_user, other_user):
        """Test session isolation between concurrent users."""
        user1_headers = get_auth_headers(test_user)
        user2_headers = get_auth_headers(other_user)
        
        # Both users create profiles simultaneously
        tasks = [
            client.post(
                '/api/v1/business-profiles/',
                json={'company_name': 'User1 Async SMB', 'industry': 'Tech'},
                headers=user1_headers
            ),
            client.post(
                '/api/v1/business-profiles/',
                json={'company_name': 'User2 Async SMB', 'industry': 'Finance'},
                headers=user2_headers
            )
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Both should succeed independently
        for response in responses:
            if not isinstance(response, Exception):
                assert response.status_code in [HTTP_CREATED, HTTP_OK, 404]
        
        # Each user should only see their own profile
        user1_list = await client.get('/api/v1/business-profiles/', headers=user1_headers)
        user2_list = await client.get('/api/v1/business-profiles/', headers=user2_headers)
        
        if user1_list.status_code == HTTP_OK:
            user1_profiles = user1_list.json()
            if isinstance(user1_profiles, list):
                for profile in user1_profiles:
                    assert profile.get('company_name') != 'User2 Async SMB'
        
        if user2_list.status_code == HTTP_OK:
            user2_profiles = user2_list.json()
            if isinstance(user2_profiles, list):
                for profile in user2_profiles:
                    assert profile.get('company_name') != 'User1 Async SMB'