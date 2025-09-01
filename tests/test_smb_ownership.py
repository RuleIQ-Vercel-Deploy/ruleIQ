"""
Test SMB-focused ownership model for business profiles.
Verifies simple ownership without complex RBAC.
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from database.db_setup import Base, get_async_db
from main import app
from database.user import User
from api.dependencies.auth import create_access_token
import uuid
from datetime import datetime, timedelta
import os

# Test database setup - using async PostgreSQL for JSONB support
SQLALCHEMY_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5433/compliance_test"
).replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_async_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_async_db] = override_get_async_db

@pytest.fixture(scope="module")
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(test_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def test_user(test_db):
    """Create a test user for SMB owner."""
    async with TestingSessionLocal() as db:
        user = User(
            id=uuid.uuid4(),
            email="owner@smallbusiness.com",
            hashed_password="$2b$12$dummy_hash",
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        yield user
        # Cleanup
        await db.delete(user)
        await db.commit()

@pytest.fixture
async def other_user(test_db):
    """Create another user to test ownership isolation."""
    async with TestingSessionLocal() as db:
        user = User(
            id=uuid.uuid4(),
            email="other@business.com",
            hashed_password="$2b$12$dummy_hash",
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        yield user
        # Cleanup
        await db.delete(user)
        await db.commit()

@pytest.fixture
def auth_headers(test_user):
    """Generate auth headers for the test user."""
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def other_auth_headers(other_user):
    """Generate auth headers for the other user."""
    token = create_access_token({"sub": str(other_user.id)})
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
class TestSMBOwnership:
    """Test simple ownership model for SMBs."""
    
    async def test_create_business_profile(self, client, auth_headers):
        """Test that SMB owner can create their business profile."""
        profile_data = {
            "company_name": "Small Business LLC",
            "industry": "Retail",
            "company_size": "1-10",
            "description": "A small retail business"
        }
        
        response = await client.post(
            "/api/v1/business-profiles/",
            json=profile_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["company_name"] == "Small Business LLC"
        assert data["industry"] == "Retail"
    
    def test_get_own_profile(self, client, auth_headers, test_user):
        """Test that owner can retrieve their own profile."""
        # First create a profile
        profile_data = {
            "company_name": "My Small Business",
            "industry": "Services",
            "company_size": "1-10"
        }
        
        create_response = client.post(
            "/api/v1/business-profiles/",
            json=profile_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        
        # Now retrieve it
        response = client.get(
            "/api/v1/business-profiles/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "My Small Business"
    
    def test_cannot_access_others_profile(self, client, auth_headers, other_auth_headers):
        """Test that users cannot access profiles they don't own."""
        # Create profile as first user
        profile_data = {
            "company_name": "Private Business",
            "industry": "Manufacturing",
            "company_size": "1-10"
        }
        
        create_response = client.post(
            "/api/v1/business-profiles/",
            json=profile_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]
        
        # Try to access as second user
        response = client.get(
            f"/api/v1/business-profiles/{profile_id}",
            headers=other_auth_headers
        )
        
        assert response.status_code == 403
        assert "don't have access" in response.json()["detail"].lower()
    
    def test_cannot_update_others_profile(self, client, auth_headers, other_auth_headers):
        """Test that users cannot update profiles they don't own."""
        # Create profile as first user
        profile_data = {
            "company_name": "Original Name",
            "industry": "Tech",
            "company_size": "1-10"
        }
        
        create_response = client.post(
            "/api/v1/business-profiles/",
            json=profile_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]
        
        # Try to update as second user
        update_data = {
            "company_name": "Hacked Name"
        }
        
        response = client.put(
            f"/api/v1/business-profiles/{profile_id}",
            json=update_data,
            headers=other_auth_headers
        )
        
        assert response.status_code == 403
        assert "don't have access" in response.json()["detail"].lower()
    
    def test_cannot_delete_others_profile(self, client, auth_headers, other_auth_headers):
        """Test that users cannot delete profiles they don't own."""
        # Create profile as first user
        profile_data = {
            "company_name": "To Delete",
            "industry": "Retail",
            "company_size": "1-10"
        }
        
        create_response = client.post(
            "/api/v1/business-profiles/",
            json=profile_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]
        
        # Try to delete as second user
        response = client.delete(
            f"/api/v1/business-profiles/{profile_id}",
            headers=other_auth_headers
        )
        
        assert response.status_code == 403
        assert "don't have access" in response.json()["detail"].lower()
    
    def test_list_only_own_profiles(self, client, auth_headers, other_auth_headers):
        """Test that list endpoint only shows owned profiles."""
        # Create profile as first user
        profile1_data = {
            "company_name": "User 1 Business",
            "industry": "Tech",
            "company_size": "1-10"
        }
        
        client.post(
            "/api/v1/business-profiles/",
            json=profile1_data,
            headers=auth_headers
        )
        
        # Create profile as second user
        profile2_data = {
            "company_name": "User 2 Business",
            "industry": "Retail",
            "company_size": "1-10"
        }
        
        client.post(
            "/api/v1/business-profiles/",
            json=profile2_data,
            headers=other_auth_headers
        )
        
        # List as first user - should only see their own
        response = client.get(
            "/api/v1/business-profiles/list",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["profiles"][0]["company_name"] == "User 1 Business"
        
        # List as second user - should only see their own
        response2 = client.get(
            "/api/v1/business-profiles/list",
            headers=other_auth_headers
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total"] == 1
        assert data2["profiles"][0]["company_name"] == "User 2 Business"
    
    def test_no_auth_rejected(self, client):
        """Test that requests without auth are rejected."""
        response = client.get("/api/v1/business-profiles/")
        assert response.status_code == 401
        
        response = client.post(
            "/api/v1/business-profiles/",
            json={"company_name": "Test"}
        )
        assert response.status_code == 401
    
    def test_expired_token_rejected(self, client, test_user):
        """Test that expired tokens are rejected."""
        # Create an expired token
        expired_token = create_access_token(
            {"sub": test_user.email},
            expires_delta=timedelta(seconds=-1)
        )
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = client.get("/api/v1/business-profiles/", headers=headers)
        assert response.status_code == 401