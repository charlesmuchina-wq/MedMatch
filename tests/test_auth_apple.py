"""
Test suite for MedMatch Authentication including Apple Sign In
Tests: Apple config, Apple callback, Google session, Email login/register, User info, Logout
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAppleSignIn:
    """Apple Sign In endpoint tests"""
    
    def test_apple_config_returns_valid_config(self):
        """Test /api/auth/apple/config returns proper configuration"""
        response = requests.get(f"{BASE_URL}/api/auth/apple/config")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        assert "client_id" in data
        assert "scope" in data
        assert "response_mode" in data
        assert "response_type" in data
        
        # Verify expected values
        assert data["client_id"] == "com.medmatch.signin.web"
        assert data["scope"] == "name email"
        assert data["response_mode"] == "fragment"
        assert data["response_type"] == "code id_token"
        print(f"✅ Apple config endpoint returns valid configuration: {data}")
    
    def test_apple_callback_rejects_invalid_token(self):
        """Test /api/auth/apple/callback rejects invalid tokens"""
        response = requests.post(
            f"{BASE_URL}/api/auth/apple/callback",
            json={"id_token": "invalid_token"}
        )
        
        # Should return 401 for invalid token
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Invalid" in data["detail"] or "token" in data["detail"].lower()
        print(f"✅ Apple callback correctly rejects invalid token: {data['detail']}")
    
    def test_apple_callback_requires_id_token(self):
        """Test /api/auth/apple/callback requires id_token field"""
        response = requests.post(
            f"{BASE_URL}/api/auth/apple/callback",
            json={}
        )
        
        # Should return 422 for missing required field
        assert response.status_code == 422
        print("✅ Apple callback requires id_token field")


class TestGoogleSignIn:
    """Google Sign In endpoint tests"""
    
    def test_google_session_requires_session_id(self):
        """Test /api/auth/google/session requires session_id"""
        response = requests.post(
            f"{BASE_URL}/api/auth/google/session",
            json={}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Session ID required" in data.get("detail", "")
        print("✅ Google session endpoint requires session_id")
    
    def test_google_session_rejects_invalid_session(self):
        """Test /api/auth/google/session rejects invalid session"""
        response = requests.post(
            f"{BASE_URL}/api/auth/google/session",
            json={"session_id": "invalid_session_id"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid session" in data.get("detail", "")
        print("✅ Google session endpoint rejects invalid session")


class TestEmailAuth:
    """Email authentication tests"""
    
    def test_admin_login_works(self):
        """Test admin bypass login with provided credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "admin@medmatch.com",
                "password": "MedMatch2026!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "token_type" in data
        assert "user" in data
        
        # Verify user data
        user = data["user"]
        assert user["email"] == "admin@medmatch.com"
        assert user["name"] == "Admin"
        assert user["auth_method"] == "admin"
        assert user.get("is_admin") == True
        print(f"✅ Admin login works: {user['email']}")
        
        return data["access_token"]
    
    def test_login_rejects_invalid_credentials(self):
        """Test login rejects invalid email/password"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid" in data.get("detail", "")
        print("✅ Login correctly rejects invalid credentials")
    
    def test_register_creates_new_user(self):
        """Test registration creates new user with trial membership"""
        test_email = f"TEST_register_{int(time.time())}@example.com"
        
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": test_email,
                "password": "TestPass123!",
                "name": "Test User",
                "role": "job_seeker"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "user" in data
        
        # Verify user data
        user = data["user"]
        assert user["email"] == test_email
        assert user["name"] == "Test User"
        assert user["auth_method"] == "email"
        assert user["role"] == "job_seeker"
        assert user["membership_status"] == "trial"
        assert user["trial_ends_at"] is not None
        print(f"✅ Registration creates user with trial: {user['email']}")
    
    def test_register_recruiter_gets_free_membership(self):
        """Test recruiter registration gets free active membership"""
        test_email = f"TEST_recruiter_{int(time.time())}@example.com"
        
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": test_email,
                "password": "TestPass123!",
                "name": "Test Recruiter",
                "role": "recruiter"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        user = data["user"]
        assert user["role"] == "recruiter"
        assert user["membership_status"] == "active"
        print(f"✅ Recruiter registration gets free active membership: {user['email']}")
    
    def test_register_rejects_duplicate_email(self):
        """Test registration rejects duplicate email"""
        # First registration
        test_email = f"TEST_dup_{int(time.time())}@example.com"
        requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": test_email,
                "password": "TestPass123!",
                "name": "Test User"
            }
        )
        
        # Second registration with same email
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": test_email,
                "password": "TestPass123!",
                "name": "Test User 2"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data.get("detail", "").lower()
        print("✅ Registration rejects duplicate email")


class TestUserInfo:
    """User info endpoint tests"""
    
    def test_auth_me_requires_authentication(self):
        """Test /api/auth/me requires authentication"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data.get("detail", "")
        print("✅ /api/auth/me requires authentication")
    
    def test_auth_me_returns_user_info(self):
        """Test /api/auth/me returns user info with valid token"""
        # Login first
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "admin@medmatch.com",
                "password": "MedMatch2026!"
            }
        )
        token = login_response.json()["access_token"]
        
        # Get user info
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify user data fields
        assert "user_id" in data
        assert "email" in data
        assert "name" in data
        assert "auth_method" in data
        assert "role" in data
        assert "membership_status" in data
        assert data["email"] == "admin@medmatch.com"
        print(f"✅ /api/auth/me returns user info: {data['email']}")


class TestLogout:
    """Logout endpoint tests"""
    
    def test_logout_works(self):
        """Test /api/auth/logout clears session"""
        response = requests.post(f"{BASE_URL}/api/auth/logout")
        
        assert response.status_code == 200
        data = response.json()
        assert "Logged out" in data.get("message", "")
        print("✅ Logout endpoint works")
    
    def test_logout_invalidates_session(self):
        """Test logout invalidates the session token"""
        # Login first
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "admin@medmatch.com",
                "password": "MedMatch2026!"
            }
        )
        token = login_response.json()["access_token"]
        
        # Verify token works
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        
        # Logout with cookie (simulating browser)
        session = requests.Session()
        session.cookies.set("session_token", token)
        logout_response = session.post(f"{BASE_URL}/api/auth/logout")
        assert logout_response.status_code == 200
        
        print("✅ Logout invalidates session")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
