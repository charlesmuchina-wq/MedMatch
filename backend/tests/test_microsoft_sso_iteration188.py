"""
Microsoft SSO Integration Tests - Iteration 188
Tests: Microsoft Azure AD SSO endpoints and session validation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestMicrosoftSSOConfig:
    """Tests for /api/auth/microsoft/config endpoint"""
    
    def test_microsoft_config_returns_configured_true(self):
        """Test that GET /api/auth/microsoft/config returns configured:true"""
        response = requests.get(f"{BASE_URL}/api/auth/microsoft/config")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Must have 'configured' key
        assert "configured" in data, "Response missing 'configured' key"
        assert data["configured"] is True, f"Expected configured=true, got {data['configured']}"
        
        # Should have a message
        assert "message" in data, "Response missing 'message' key"
        print(f"Microsoft SSO config: configured={data['configured']}, message={data['message']}")


class TestMicrosoftSSOLogin:
    """Tests for /api/auth/microsoft/login endpoint"""
    
    def test_microsoft_login_returns_auth_url(self):
        """Test that POST /api/auth/microsoft/login returns auth_url with login.microsoftonline.com"""
        response = requests.post(f"{BASE_URL}/api/auth/microsoft/login")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Must have auth_url
        assert "auth_url" in data, f"Response missing 'auth_url' key: {data}"
        auth_url = data["auth_url"]
        
        # auth_url must contain login.microsoftonline.com
        assert "login.microsoftonline.com" in auth_url, f"auth_url doesn't contain login.microsoftonline.com: {auth_url}"
        
        # Verify it contains the tenant ID
        assert "d4e8b623-9f2d-4e6c-b6d4-a0bf218eb3fd" in auth_url, f"auth_url doesn't contain expected tenant ID: {auth_url}"
        
        # Verify it contains the client ID
        assert "40a72049-50e2-46ad-b085-514d3e831cc7" in auth_url, f"auth_url doesn't contain expected client ID: {auth_url}"
        
        # Verify configured flag
        assert data.get("configured") is True, f"Expected configured=true, got {data.get('configured')}"
        
        print(f"Microsoft SSO login auth_url verified: {auth_url[:100]}...")


class TestMicrosoftSSOCallback:
    """Tests for /api/auth/microsoft/callback endpoint existence"""
    
    def test_microsoft_callback_endpoint_exists(self):
        """Test that GET /api/auth/microsoft/callback exists and handles missing code"""
        # Call without code should return 400 (no authorization code)
        response = requests.get(f"{BASE_URL}/api/auth/microsoft/callback")
        
        # Should return 400 because no code provided, not 404
        assert response.status_code == 400, f"Expected 400 for missing code, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data, f"Expected error detail: {data}"
        print(f"Microsoft callback endpoint exists, returns proper error for missing code: {data['detail']}")
    
    def test_microsoft_callback_with_error(self):
        """Test that callback handles OAuth error parameter"""
        response = requests.get(f"{BASE_URL}/api/auth/microsoft/callback?error=access_denied")
        
        assert response.status_code == 400, f"Expected 400 for OAuth error, got {response.status_code}"
        data = response.json()
        assert "detail" in data, f"Expected error detail: {data}"
        assert "access_denied" in data["detail"].lower() or "error" in data["detail"].lower(), \
            f"Error detail should mention the error: {data['detail']}"
        print(f"Microsoft callback handles OAuth error properly: {data['detail']}")


class TestSessionValidation:
    """Tests for /api/auth/session/validate endpoint"""
    
    def test_session_validate_requires_token(self):
        """Test that POST /api/auth/session/validate requires session_token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/session/validate",
            json={}
        )
        
        assert response.status_code == 400, f"Expected 400 for missing token, got {response.status_code}"
        data = response.json()
        assert "detail" in data, f"Expected error detail: {data}"
        print(f"Session validate requires token: {data['detail']}")
    
    def test_session_validate_rejects_invalid_token(self):
        """Test that POST /api/auth/session/validate rejects invalid token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/session/validate",
            json={"session_token": "invalid_token_12345"}
        )
        
        assert response.status_code == 401, f"Expected 401 for invalid token, got {response.status_code}"
        data = response.json()
        assert "detail" in data, f"Expected error detail: {data}"
        print(f"Session validate rejects invalid token: {data['detail']}")
    
    def test_session_validate_with_valid_session(self):
        """Test session validation with a real session from login"""
        # First, login to get a valid session token
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "admin@medmatch.com",
                "password": "Swampdrainer2026!"
            }
        )
        
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        login_data = login_response.json()
        session_token = login_data.get("access_token")
        
        assert session_token, f"No access_token in login response: {login_data}"
        
        # Now validate this session token
        validate_response = requests.post(
            f"{BASE_URL}/api/auth/session/validate",
            json={"session_token": session_token}
        )
        
        assert validate_response.status_code == 200, f"Session validation failed: {validate_response.text}"
        data = validate_response.json()
        
        # Verify response structure matches expected format
        assert "access_token" in data, f"Response missing access_token: {data}"
        assert "token_type" in data, f"Response missing token_type: {data}"
        assert "user" in data, f"Response missing user: {data}"
        
        user = data["user"]
        assert "user_id" in user, f"User missing user_id: {user}"
        assert "email" in user, f"User missing email: {user}"
        
        print(f"Session validation successful: user_id={user['user_id']}, email={user['email']}")


class TestAuthURLStructure:
    """Tests to verify Microsoft OAuth URL structure"""
    
    def test_auth_url_contains_required_params(self):
        """Test that auth_url contains all required OAuth parameters"""
        response = requests.post(f"{BASE_URL}/api/auth/microsoft/login")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        auth_url = response.json().get("auth_url", "")
        
        # Required OAuth parameters
        required_params = [
            "client_id=",
            "response_type=code",
            "redirect_uri=",
            "scope=",
        ]
        
        for param in required_params:
            assert param in auth_url, f"auth_url missing required param '{param}': {auth_url}"
        
        # Check scopes include required permissions
        assert "openid" in auth_url, "Missing openid scope"
        assert "profile" in auth_url, "Missing profile scope"
        assert "email" in auth_url, "Missing email scope"
        
        print(f"Auth URL contains all required OAuth parameters")
    
    def test_redirect_uri_points_to_callback(self):
        """Test that redirect_uri points to the callback endpoint"""
        response = requests.post(f"{BASE_URL}/api/auth/microsoft/login")
        
        assert response.status_code == 200
        auth_url = response.json().get("auth_url", "")
        
        # Verify redirect_uri contains the callback path
        assert "/api/auth/microsoft/callback" in auth_url, \
            f"redirect_uri doesn't point to callback: {auth_url}"
        
        print("Redirect URI correctly points to callback endpoint")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
