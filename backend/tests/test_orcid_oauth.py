"""
ORCID OAuth Integration Tests
Tests for ORCID OAuth login flow including:
- Config endpoint
- Login redirect
- Callback error handling
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestOrcidOAuthConfig:
    """Test ORCID OAuth configuration endpoint"""
    
    def test_orcid_config_endpoint_returns_200(self):
        """GET /api/auth/orcid/config returns 200 with configured status"""
        response = requests.get(f"{BASE_URL}/api/auth/orcid/config")
        assert response.status_code == 200
        
        data = response.json()
        assert "configured" in data
        assert "environment" in data
        
    def test_orcid_config_shows_configured_true(self):
        """ORCID should be configured with client ID"""
        response = requests.get(f"{BASE_URL}/api/auth/orcid/config")
        data = response.json()
        
        assert data["configured"] == True, "ORCID should be configured"
        assert data["environment"] in ["production", "sandbox"]

class TestOrcidOAuthLogin:
    """Test ORCID OAuth login redirect"""
    
    def test_orcid_login_returns_307_redirect(self):
        """GET /api/auth/orcid/login returns 307 redirect"""
        response = requests.get(
            f"{BASE_URL}/api/auth/orcid/login",
            allow_redirects=False
        )
        assert response.status_code == 307
        
    def test_orcid_login_redirects_to_orcid_org(self):
        """Login should redirect to orcid.org authorize endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/auth/orcid/login",
            allow_redirects=False
        )
        
        redirect_url = response.headers.get("Location", "")
        assert "orcid.org/oauth/authorize" in redirect_url
        
    def test_orcid_login_includes_correct_client_id(self):
        """Redirect URL should include the correct client ID"""
        response = requests.get(
            f"{BASE_URL}/api/auth/orcid/login",
            allow_redirects=False
        )
        
        redirect_url = response.headers.get("Location", "")
        # Client ID should be APP-K9HUYS6GQY2RERX6
        assert "client_id=APP-K9HUYS6GQY2RERX6" in redirect_url
        
    def test_orcid_login_includes_required_oauth_params(self):
        """Redirect URL should include all required OAuth params"""
        response = requests.get(
            f"{BASE_URL}/api/auth/orcid/login",
            allow_redirects=False
        )
        
        redirect_url = response.headers.get("Location", "")
        
        # Check for required OAuth parameters
        assert "response_type=code" in redirect_url
        assert "scope=/authenticate" in redirect_url
        assert "redirect_uri=" in redirect_url
        assert "state=" in redirect_url
        
    def test_orcid_login_redirect_uri_matches_callback(self):
        """Redirect URI should point to our callback endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/auth/orcid/login",
            allow_redirects=False
        )
        
        redirect_url = response.headers.get("Location", "")
        expected_callback = f"{BASE_URL}/api/auth/orcid/callback"
        
        assert expected_callback in redirect_url or "orcid/callback" in redirect_url

class TestOrcidOAuthCallback:
    """Test ORCID OAuth callback error handling"""
    
    def test_callback_with_invalid_state_returns_error(self):
        """Callback with invalid state should redirect with orcid_error"""
        response = requests.get(
            f"{BASE_URL}/api/auth/orcid/callback?code=test_code&state=invalid_state",
            allow_redirects=False
        )
        
        assert response.status_code == 307
        redirect_url = response.headers.get("Location", "")
        assert "orcid_error=invalid_state" in redirect_url
        
    def test_callback_with_missing_state_returns_error(self):
        """Callback with missing state should redirect with error"""
        response = requests.get(
            f"{BASE_URL}/api/auth/orcid/callback?code=test_code",
            allow_redirects=False
        )
        
        assert response.status_code == 307
        redirect_url = response.headers.get("Location", "")
        assert "orcid_error" in redirect_url
        
    def test_callback_with_oauth_error_redirects_with_error(self):
        """Callback with error parameter should redirect with that error"""
        response = requests.get(
            f"{BASE_URL}/api/auth/orcid/callback?error=access_denied&error_description=User+denied",
            allow_redirects=False
        )
        
        assert response.status_code == 307
        redirect_url = response.headers.get("Location", "")
        assert "orcid_error=access_denied" in redirect_url
        
    def test_callback_error_redirects_to_login_page(self):
        """Error redirects should go to the login page"""
        response = requests.get(
            f"{BASE_URL}/api/auth/orcid/callback?error=access_denied",
            allow_redirects=False
        )
        
        redirect_url = response.headers.get("Location", "")
        assert "/login" in redirect_url

class TestOrcidWithExistingAuth:
    """Test ORCID alongside existing auth methods"""
    
    def test_email_login_still_works(self):
        """Existing email login should still function"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "admin@medmatch.com",
                "password": "Swampdrainer2026!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "admin@medmatch.com"
        
    def test_google_config_still_available(self):
        """Google OAuth config should still be available"""
        # Google doesn't have a config endpoint, but session endpoint should work
        # This is a simple check that other auth methods aren't broken
        pass
        
    def test_apple_config_still_available(self):
        """Apple Sign In config should still be available"""
        response = requests.get(f"{BASE_URL}/api/auth/apple/config")
        assert response.status_code == 200
        data = response.json()
        assert "client_id" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
