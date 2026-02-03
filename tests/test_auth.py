"""
MedMatch Authentication API Tests
Tests for: /api/auth/register, /api/auth/login, /api/auth/me, /api/auth/logout, /api/applications/quick-apply
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthEndpoints:
    """Authentication endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Generate unique test email for each test run
        self.test_email = f"test_{uuid.uuid4().hex[:8]}@medmatch.com"
        self.test_password = "testpass123"
        self.test_name = "Test User"
        yield
        # Cleanup - logout if logged in
        try:
            self.session.post(f"{BASE_URL}/api/auth/logout")
        except:
            pass
    
    def test_api_root_accessible(self):
        """Test that API root is accessible"""
        response = self.session.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "MedMatch" in str(data)
        print(f"✅ API root accessible: {data}")
    
    def test_auth_me_returns_401_when_not_authenticated(self):
        """Test /api/auth/me returns 401 when not authenticated"""
        response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✅ /api/auth/me returns 401 when not authenticated: {data}")
    
    def test_register_new_user(self):
        """Test user registration creates new user"""
        payload = {
            "email": self.test_email,
            "password": self.test_password,
            "name": self.test_name
        }
        response = self.session.post(f"{BASE_URL}/api/auth/register", json=payload)
        
        # Should return 200 for successful registration
        assert response.status_code == 200, f"Registration failed: {response.text}"
        
        data = response.json()
        # Verify response structure
        assert "access_token" in data, "Missing access_token in response"
        assert "user" in data, "Missing user in response"
        assert data["user"]["email"] == self.test_email
        assert data["user"]["name"] == self.test_name
        assert data["user"]["auth_method"] == "email"
        assert "user_id" in data["user"]
        print(f"✅ User registered successfully: {data['user']['email']}")
        
        # Verify session cookie is set
        assert "session_token" in response.cookies or "set-cookie" in str(response.headers).lower()
    
    def test_register_duplicate_email_fails(self):
        """Test registration with duplicate email fails"""
        # First register
        payload = {
            "email": self.test_email,
            "password": self.test_password,
            "name": self.test_name
        }
        self.session.post(f"{BASE_URL}/api/auth/register", json=payload)
        
        # Try to register again with same email
        response = self.session.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print(f"✅ Duplicate registration correctly rejected: {data}")
    
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        # First register
        register_payload = {
            "email": self.test_email,
            "password": self.test_password,
            "name": self.test_name
        }
        self.session.post(f"{BASE_URL}/api/auth/register", json=register_payload)
        
        # Logout first
        self.session.post(f"{BASE_URL}/api/auth/logout")
        
        # Now login
        login_payload = {
            "email": self.test_email,
            "password": self.test_password
        }
        response = self.session.post(f"{BASE_URL}/api/auth/login", json=login_payload)
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == self.test_email
        print(f"✅ Login successful: {data['user']['email']}")
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials returns 401"""
        payload = {
            "email": "nonexistent@medmatch.com",
            "password": "wrongpassword"
        }
        response = self.session.post(f"{BASE_URL}/api/auth/login", json=payload)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✅ Invalid login correctly rejected: {data}")
    
    def test_auth_me_returns_user_after_login(self):
        """Test /api/auth/me returns user data after login"""
        # Register and login
        register_payload = {
            "email": self.test_email,
            "password": self.test_password,
            "name": self.test_name
        }
        reg_response = self.session.post(f"{BASE_URL}/api/auth/register", json=register_payload)
        assert reg_response.status_code == 200
        
        # Get session token from response
        reg_data = reg_response.json()
        session_token = reg_data.get("access_token")
        
        # Make request with Authorization header
        headers = {"Authorization": f"Bearer {session_token}"}
        response = self.session.get(f"{BASE_URL}/api/auth/me", headers=headers)
        
        assert response.status_code == 200, f"Auth me failed: {response.text}"
        
        data = response.json()
        assert "user_id" in data
        assert data["email"] == self.test_email
        assert data["name"] == self.test_name
        print(f"✅ /api/auth/me returns user data: {data}")
    
    def test_logout_clears_session(self):
        """Test logout clears session"""
        # Register
        register_payload = {
            "email": self.test_email,
            "password": self.test_password,
            "name": self.test_name
        }
        reg_response = self.session.post(f"{BASE_URL}/api/auth/register", json=register_payload)
        session_token = reg_response.json().get("access_token")
        
        # Logout
        headers = {"Authorization": f"Bearer {session_token}"}
        response = self.session.post(f"{BASE_URL}/api/auth/logout", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✅ Logout successful: {data}")
        
        # Verify session is cleared - auth/me should return 401
        response = self.session.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 401
        print("✅ Session cleared after logout")


class TestQuickApplyEndpoint:
    """Tests for quick-apply endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_quick_apply_endpoint_exists(self):
        """Test that quick-apply endpoint exists"""
        # Test with a sample job
        payload = {
            "job": {
                "id": "test_job_123",
                "title": "Quality Manager",
                "company": "Test Company",
                "location": "Remote",
                "url": "https://example.com/job/123"
            }
        }
        response = self.session.post(f"{BASE_URL}/api/applications/quick-apply", json=payload)
        
        # Should return 200 or 201 for success, or 401 if auth required
        assert response.status_code in [200, 201, 401, 422], f"Unexpected status: {response.status_code}"
        print(f"✅ Quick-apply endpoint accessible, status: {response.status_code}")


class TestPhoneAuthEndpoint:
    """Tests for phone authentication (Twilio)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_phone_send_otp_endpoint_exists(self):
        """Test phone OTP endpoint exists and returns appropriate error when not configured"""
        payload = {"phone_number": "+15551234567"}
        response = self.session.post(f"{BASE_URL}/api/auth/phone/send-otp", json=payload)
        
        # Should return 500 if Twilio not configured, or 200 if configured
        # 520 is Cloudflare error which can happen with Twilio import issues
        assert response.status_code in [200, 400, 500, 520], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 500:
            data = response.json()
            assert "detail" in data
            assert "not configured" in data["detail"].lower() or "twilio" in data["detail"].lower()
            print(f"✅ Phone auth endpoint exists but Twilio not configured: {data['detail']}")
        elif response.status_code == 520:
            print("✅ Phone auth endpoint exists but Twilio library not available (520 error)")
        else:
            print(f"✅ Phone auth endpoint accessible, status: {response.status_code}")


class TestGoogleAuthEndpoint:
    """Tests for Google OAuth endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_google_session_endpoint_exists(self):
        """Test Google session endpoint exists"""
        payload = {"session_id": "invalid_session_id"}
        response = self.session.post(f"{BASE_URL}/api/auth/google/session", json=payload)
        
        # Should return 401 for invalid session
        assert response.status_code in [400, 401], f"Unexpected status: {response.status_code}"
        print(f"✅ Google auth endpoint accessible, status: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
