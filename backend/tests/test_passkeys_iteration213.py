"""
Passkeys/WebAuthn API Tests - Iteration 213
Tests for GET /api/auth/passkeys and DELETE /api/auth/passkeys/{credential_id}
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

class TestPasskeyEndpoints:
    """Test passkey management API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin and get token"""
        self.session = requests.Session()
        # Login with admin credentials
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.token = login_resp.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        yield
    
    # Backend: GET /api/auth/passkeys returns list of passkeys for authenticated user
    def test_get_passkeys_authenticated(self):
        """GET /api/auth/passkeys should return list of passkeys for authenticated user"""
        resp = self.session.get(f"{BASE_URL}/api/auth/passkeys")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "passkeys" in data, "Response should contain 'passkeys' key"
        assert isinstance(data["passkeys"], list), "passkeys should be a list"
        
        # Verify passkey structure if any exist
        for pk in data["passkeys"]:
            assert "credential_id" in pk, "Each passkey should have credential_id"
            assert "created_at" in pk or pk.get("created_at") is not None or pk.get("created_at") == "", "Each passkey should have created_at"
            # public_key should NOT be returned for security
            assert "public_key" not in pk, "public_key should not be exposed"
        
        print(f"SUCCESS: GET /api/auth/passkeys returned {len(data['passkeys'])} passkeys")
    
    # Backend: GET /api/auth/passkeys returns 401 for unauthenticated user
    def test_get_passkeys_unauthenticated(self):
        """GET /api/auth/passkeys should return 401 without auth token"""
        # Create a new session without auth header
        unauth_session = requests.Session()
        resp = unauth_session.get(f"{BASE_URL}/api/auth/passkeys")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
        print("SUCCESS: GET /api/auth/passkeys returns 401 for unauthenticated user")
    
    # Backend: DELETE /api/auth/passkeys/{credential_id} returns 404 for non-existent credential
    def test_delete_passkey_not_found(self):
        """DELETE /api/auth/passkeys/{credential_id} should return 404 for non-existent credential"""
        fake_cred_id = "nonexistent_credential_id_12345"
        resp = self.session.delete(f"{BASE_URL}/api/auth/passkeys/{fake_cred_id}")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
        print("SUCCESS: DELETE /api/auth/passkeys returns 404 for non-existent credential")
    
    # Backend: DELETE /api/auth/passkeys/{credential_id} returns 401 for unauthenticated
    def test_delete_passkey_unauthenticated(self):
        """DELETE /api/auth/passkeys/{credential_id} should return 401 without auth token"""
        unauth_session = requests.Session()
        resp = unauth_session.delete(f"{BASE_URL}/api/auth/passkeys/some_credential_id")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
        print("SUCCESS: DELETE /api/auth/passkeys returns 401 for unauthenticated user")


class TestPasskeyRegisterLoginFlow:
    """Test passkey registration and login start endpoints (backend already existed)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        yield
    
    # Test register start requires registered user
    def test_passkey_register_start_requires_user(self):
        """POST /api/auth/passkey/register/start should require existing user"""
        resp = self.session.post(f"{BASE_URL}/api/auth/passkey/register/start", json={
            "email": "nonexistent_user_test@example.com"
        })
        # Should return 404 if user doesn't exist
        assert resp.status_code == 404, f"Expected 404 for non-existent user, got {resp.status_code}"
        print("SUCCESS: Passkey register/start returns 404 for non-existent user")
    
    # Test register start with valid user (admin)
    def test_passkey_register_start_with_valid_user(self):
        """POST /api/auth/passkey/register/start should return challenge for existing user"""
        resp = self.session.post(f"{BASE_URL}/api/auth/passkey/register/start", json={
            "email": "admin@medmatch.com"
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "challenge" in data, "Response should contain challenge"
        assert "rp" in data, "Response should contain relying party info"
        assert "user" in data, "Response should contain user info"
        assert "pubKeyCredParams" in data, "Response should contain pubKeyCredParams"
        print("SUCCESS: Passkey register/start returns challenge for existing user")
    
    # Test login start requires passkeys
    def test_passkey_login_start_requires_passkeys(self):
        """POST /api/auth/passkey/login/start should return 404 if no passkeys registered"""
        resp = self.session.post(f"{BASE_URL}/api/auth/passkey/login/start", json={
            "email": "nonexistent_passkey_user@example.com"
        })
        assert resp.status_code == 404, f"Expected 404 for user with no passkeys, got {resp.status_code}"
        print("SUCCESS: Passkey login/start returns 404 when no passkeys registered")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
