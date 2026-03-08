"""
Test Auth Duplicate Credentials - Iteration 198
Tests that all 3 portals (MedMatch, AI KARAU, ENZI) can use the same credentials
and that all auth providers are exposed correctly.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSharedAuthBackend:
    """Test the shared /api/auth/login backend endpoint"""
    
    def test_admin_login_success(self):
        """Admin credentials work on the shared auth endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"},
            timeout=10
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "Missing access_token"
        assert "user" in data, "Missing user object"
        assert data["user"]["email"] == "admin@medmatch.com"
        assert data["user"]["role"] == "recruiter"
        print(f"✓ Admin login success: user_id={data['user']['user_id']}")
    
    def test_test_user_login(self):
        """Test user credentials work on the shared auth endpoint"""
        # First register test user if doesn't exist
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": "test@medmatch.io",
                "password": "TestPassword123!",
                "name": "Test User",
                "role": "job_seeker"
            },
            timeout=10
        )
        # Ignore 400 error if already registered
        
        # Now login
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@medmatch.io", "password": "TestPassword123!"},
            timeout=10
        )
        assert response.status_code == 200, f"Test user login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@medmatch.io"
        print(f"✓ Test user login success: user_id={data['user']['user_id']}, role={data['user']['role']}")
    
    def test_invalid_credentials_rejected(self):
        """Invalid credentials are properly rejected"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "invalid@test.com", "password": "wrongpassword"},
            timeout=10
        )
        assert response.status_code == 401, f"Expected 401 for invalid credentials, got {response.status_code}"
        print("✓ Invalid credentials properly rejected with 401")


class TestGitHubSSOEndpoint:
    """Test the GitHub SSO endpoint (mocked)"""
    
    def test_github_login_returns_auth_url(self):
        """POST /api/auth/github/login returns auth_url"""
        response = requests.post(
            f"{BASE_URL}/api/auth/github/login",
            timeout=10
        )
        assert response.status_code == 200, f"GitHub login failed: {response.text}"
        data = response.json()
        assert "auth_url" in data, "Missing auth_url in response"
        assert "configured" in data and data["configured"] is True
        assert "mode" in data and data["mode"] == "demo", "GitHub SSO should be in demo mode"
        assert BASE_URL in data["auth_url"] or "github" in data["auth_url"].lower()
        print(f"✓ GitHub SSO returns auth_url: {data['auth_url'][:50]}...")
    
    def test_github_config_status(self):
        """GET /api/auth/github/config returns configuration status"""
        response = requests.get(
            f"{BASE_URL}/api/auth/github/config",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert data["configured"] is True
        assert data["mode"] == "demo"
        print(f"✓ GitHub config: configured={data['configured']}, mode={data['mode']}")


class TestMicrosoftSSOEndpoint:
    """Test Microsoft SSO endpoint"""
    
    def test_microsoft_login_endpoint(self):
        """POST /api/auth/microsoft/login returns status"""
        response = requests.post(
            f"{BASE_URL}/api/auth/microsoft/login",
            timeout=10
        )
        # Either returns auth_url (if configured) or 501 (not configured)
        assert response.status_code in [200, 501], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "auth_url" in data
            print(f"✓ Microsoft SSO configured with auth_url")
        else:
            print("✓ Microsoft SSO not configured (501) - expected for demo")


class TestAppleSSOEndpoint:
    """Test Apple Sign In endpoint"""
    
    def test_apple_config_endpoint(self):
        """GET /api/auth/apple/config returns configuration"""
        response = requests.get(
            f"{BASE_URL}/api/auth/apple/config",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert "configured" in data
        assert "response_type" in data
        assert data["response_type"] == "code id_token"
        print(f"✓ Apple config: configured={data['configured']}")


class TestPasskeyEndpoints:
    """Test Passkey / WebAuthn endpoints"""
    
    def test_passkey_login_start_requires_email(self):
        """POST /api/auth/passkey/login/start requires email"""
        response = requests.post(
            f"{BASE_URL}/api/auth/passkey/login/start",
            json={"email": ""},
            timeout=10
        )
        assert response.status_code == 400, f"Expected 400 for empty email, got {response.status_code}"
        print("✓ Passkey login start properly validates email")
    
    def test_passkey_login_start_unknown_email(self):
        """POST /api/auth/passkey/login/start with unknown email"""
        response = requests.post(
            f"{BASE_URL}/api/auth/passkey/login/start",
            json={"email": "unknown_passkey_test@test.com"},
            timeout=10
        )
        assert response.status_code == 404, f"Expected 404 for unknown email, got {response.status_code}"
        data = response.json()
        assert "No passkeys" in data.get("detail", "")
        print("✓ Passkey login returns 404 for email without passkeys")


class TestAuthMeEndpoint:
    """Test /api/auth/me endpoint with valid token"""
    
    def test_auth_me_with_valid_token(self):
        """GET /api/auth/me with valid session token"""
        # First login to get token
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"},
            timeout=10
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Now call /me
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@medmatch.com"
        assert "user_id" in data
        print(f"✓ /api/auth/me returns user: {data['email']}, is_admin={data.get('is_admin', False)}")
    
    def test_auth_me_without_token(self):
        """GET /api/auth/me without token returns 401"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            timeout=10
        )
        assert response.status_code == 401
        print("✓ /api/auth/me properly requires authentication (401)")


class TestAllPortalsUseSharedAuth:
    """Verify all portals can authenticate through the same endpoint"""
    
    def test_same_credentials_work_for_all_portals(self):
        """The shared /api/auth/login works regardless of portal context"""
        # This is the same endpoint called by MedMatch (/), AI KARAU (/karau-meet), and ENZI (/lumi)
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"},
            headers={"Origin": f"{BASE_URL}"},  # Simulate frontend request
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify we get a complete user object
        assert "access_token" in data
        assert data["user"]["email"] == "admin@medmatch.com"
        assert data["user"]["role"] == "recruiter"
        
        # Token can be used across all portals
        token = data["access_token"]
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        assert me_response.status_code == 200
        print("✓ Same credentials and token work across all portal contexts")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
