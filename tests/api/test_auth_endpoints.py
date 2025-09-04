"""
Comprehensive tests for authentication API endpoints.
Tests login, registration, JWT tokens, and OAuth flows.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
import jwt
import json

from api.main import app
from database import User
from utils.auth import create_access_token, get_password_hash, verify_password


@pytest.mark.unit
class TestAuthEndpoints:
    """Unit tests for authentication endpoints"""
    
    @pytest.fixture
    def client(self):
        """Test client for FastAPI app"""
        return TestClient(app)
    
    @pytest.fixture
    def user_data(self):
        """Sample user registration data"""
        return {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User",
            "company": "Test Company",
            "role": "compliance_manager"
        }
    
    @pytest.fixture
    def existing_user(self, db_session):
        """Create an existing user in the database"""
        user = User(
            email="existing@example.com",
            full_name="Existing User",
            hashed_password=get_password_hash("ExistingPassword123!"),
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    @pytest.mark.asyncio
    async def test_register_success(self, client, user_data):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, user_data, existing_user):
        """Test registration with duplicate email"""
        user_data["email"] = existing_user.email
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client, user_data):
        """Test registration with invalid email format"""
        user_data["email"] = "not-an-email"
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422
        assert "email" in str(response.json()["detail"]).lower()
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client, user_data):
        """Test registration with weak password"""
        user_data["password"] = "weak"
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422
        assert "password" in str(response.json()["detail"]).lower()
    
    @pytest.mark.asyncio
    async def test_login_success(self, client, existing_user):
        """Test successful login"""
        login_data = {
            "username": existing_user.email,  # OAuth2 uses 'username' field
            "password": "ExistingPassword123!"
        }
        
        response = client.post(
            "/api/v1/auth/token",
            data=login_data,  # Form data, not JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify token is valid
        token = data["access_token"]
        payload = jwt.decode(token, options={"verify_signature": False})
        assert payload["sub"] == existing_user.email
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client, existing_user):
        """Test login with incorrect password"""
        login_data = {
            "username": existing_user.email,
            "password": "WrongPassword123!"
        }
        
        response = client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "Password123!"
        }
        
        response = client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_inactive_user(self, client, db_session):
        """Test login with inactive user account"""
        # Create inactive user
        user = User(
            email="inactive@example.com",
            full_name="Inactive User",
            hashed_password=get_password_hash("Password123!"),
            is_active=False,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()
        
        login_data = {
            "username": "inactive@example.com",
            "password": "Password123!"
        }
        
        response = client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, client, existing_user):
        """Test getting current user info with valid token"""
        token = create_access_token(data={"sub": existing_user.email})
        
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == existing_user.email
        assert data["full_name"] == existing_user.full_name
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 401
        assert "could not validate" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self, client, existing_user):
        """Test getting current user with expired token"""
        # Create token that expires immediately
        token = create_access_token(
            data={"sub": existing_user.email},
            expires_delta=timedelta(seconds=-1)
        )
        
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, client, existing_user):
        """Test refreshing access token"""
        # Get initial token
        login_data = {
            "username": existing_user.email,
            "password": "ExistingPassword123!"
        }
        
        login_response = client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        initial_token = login_response.json()["access_token"]
        
        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {initial_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] != initial_token  # Should be new token
    
    @pytest.mark.asyncio
    async def test_logout(self, client, existing_user):
        """Test logout endpoint"""
        token = create_access_token(data={"sub": existing_user.email})
        
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"
    
    @pytest.mark.asyncio
    async def test_password_reset_request(self, client, existing_user):
        """Test password reset request"""
        response = client.post(
            "/api/v1/auth/password-reset",
            json={"email": existing_user.email}
        )
        
        assert response.status_code == 200
        assert "reset link" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_password_reset_confirm(self, client, existing_user):
        """Test password reset confirmation"""
        # Generate reset token
        reset_token = create_access_token(
            data={"sub": existing_user.email, "type": "password_reset"},
            expires_delta=timedelta(hours=1)
        )
        
        response = client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": reset_token,
                "new_password": "NewSecurePassword123!"
            }
        )
        
        assert response.status_code == 200
        assert "successfully reset" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_change_password(self, client, existing_user):
        """Test changing password for authenticated user"""
        token = create_access_token(data={"sub": existing_user.email})
        
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "ExistingPassword123!",
                "new_password": "NewSecurePassword456!"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "successfully changed" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_verify_email(self, client, db_session):
        """Test email verification"""
        # Create unverified user
        user = User(
            email="unverified@example.com",
            full_name="Unverified User",
            hashed_password=get_password_hash("Password123!"),
            is_active=True,
            is_verified=False
        )
        db_session.add(user)
        db_session.commit()
        
        # Create verification token
        verify_token = create_access_token(
            data={"sub": user.email, "type": "email_verification"},
            expires_delta=timedelta(hours=24)
        )
        
        response = client.get(
            f"/api/v1/auth/verify-email?token={verify_token}"
        )
        
        assert response.status_code == 200
        assert "verified" in response.json()["message"].lower()
        
        # Check user is now verified
        db_session.refresh(user)
        assert user.is_verified is True


@pytest.mark.unit
class TestGoogleOAuth:
    """Tests for Google OAuth authentication"""
    
    @pytest.fixture
    def client(self):
        """Test client for FastAPI app"""
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_google_login_redirect(self, client):
        """Test Google OAuth login redirect"""
        response = client.get("/api/v1/auth/google/login", follow_redirects=False)
        
        assert response.status_code == 307
        assert "accounts.google.com" in response.headers["location"]
        assert "oauth2" in response.headers["location"]
    
    @pytest.mark.asyncio
    async def test_google_callback_success(self, client):
        """Test successful Google OAuth callback"""
        with patch('api.routers.google_auth.get_google_user_info') as mock_google:
            mock_google.return_value = {
                "email": "google@example.com",
                "name": "Google User",
                "picture": "https://example.com/picture.jpg",
                "verified_email": True
            }
            
            response = client.get(
                "/api/v1/auth/google/callback?code=test-auth-code"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["user"]["email"] == "google@example.com"
    
    @pytest.mark.asyncio
    async def test_google_callback_invalid_code(self, client):
        """Test Google OAuth callback with invalid code"""
        with patch('api.routers.google_auth.get_google_user_info') as mock_google:
            mock_google.side_effect = Exception("Invalid authorization code")
            
            response = client.get(
                "/api/v1/auth/google/callback?code=invalid-code"
            )
            
            assert response.status_code == 400
            assert "authentication failed" in response.json()["detail"].lower()


@pytest.mark.unit  
class TestRBACAuth:
    """Tests for Role-Based Access Control"""
    
    @pytest.fixture
    def client(self):
        """Test client for FastAPI app"""
        return TestClient(app)
    
    @pytest.fixture
    def admin_user(self, db_session):
        """Create admin user"""
        user = User(
            email="admin@example.com",
            full_name="Admin User",
            hashed_password=get_password_hash("AdminPass123!"),
            is_active=True,
            is_verified=True,
            is_admin=True,
            role="admin"
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    @pytest.fixture
    def regular_user(self, db_session):
        """Create regular user"""
        user = User(
            email="user@example.com",
            full_name="Regular User",
            hashed_password=get_password_hash("UserPass123!"),
            is_active=True,
            is_verified=True,
            is_admin=False,
            role="user"
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    @pytest.mark.asyncio
    async def test_admin_access(self, client, admin_user):
        """Test admin accessing admin-only endpoint"""
        token = create_access_token(
            data={"sub": admin_user.email, "role": "admin"}
        )
        
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_regular_user_denied_admin(self, client, regular_user):
        """Test regular user denied from admin endpoint"""
        token = create_access_token(
            data={"sub": regular_user.email, "role": "user"}
        )
        
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_role_based_content(self, client, admin_user, regular_user):
        """Test different content based on user role"""
        # Admin sees all data
        admin_token = create_access_token(
            data={"sub": admin_user.email, "role": "admin"}
        )
        
        admin_response = client.get(
            "/api/v1/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Regular user sees filtered data
        user_token = create_access_token(
            data={"sub": regular_user.email, "role": "user"}
        )
        
        user_response = client.get(
            "/api/v1/dashboard",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert admin_response.status_code == 200
        assert user_response.status_code == 200
        # Admin should have more data/features
        assert len(admin_response.json()) >= len(user_response.json())


@pytest.mark.integration
class TestAuthIntegration:
    """Integration tests for authentication flow"""
    
    @pytest.mark.asyncio
    async def test_complete_auth_flow(self, client, db_session):
        """Test complete authentication workflow"""
        # 1. Register new user
        register_data = {
            "email": "newuser@example.com",
            "password": "NewUserPass123!",
            "full_name": "New User",
            "company": "New Company"
        }
        
        register_response = client.post(
            "/api/v1/auth/register",
            json=register_data
        )
        assert register_response.status_code == 201
        
        # 2. Login
        login_response = client.post(
            "/api/v1/auth/token",
            data={
                "username": register_data["email"],
                "password": register_data["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 3. Access protected endpoint
        me_response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == register_data["email"]
        
        # 4. Change password
        change_pass_response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": register_data["password"],
                "new_password": "UpdatedPass456!"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert change_pass_response.status_code == 200
        
        # 5. Logout
        logout_response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert logout_response.status_code == 200
        
        # 6. Login with new password
        new_login_response = client.post(
            "/api/v1/auth/token",
            data={
                "username": register_data["email"],
                "password": "UpdatedPass456!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert new_login_response.status_code == 200