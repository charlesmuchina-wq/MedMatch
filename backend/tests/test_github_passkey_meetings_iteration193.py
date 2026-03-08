"""
Test ENZI Iteration 193: GitHub SSO (MOCKED), Passkeys/WebAuthn, Cross-Portal Meeting Integration
- GitHub SSO is MOCKED (demo mode) - returns mock auth_url pointing to our callback
- Passkey endpoints for WebAuthn registration and login flows
- Cross-portal meeting creation from ENZI to AI KARAU
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_EMAIL = "test@medmatch.io"
TEST_PASSWORD = "TestPassword123!"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    data = response.json()
    return data["access_token"]


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


# =========================
# GITHUB SSO (MOCKED) TESTS
# =========================

class TestGitHubSSOMocked:
    """GitHub SSO is MOCKED for demo - no real GitHub OAuth configured"""

    def test_github_config_returns_demo_mode(self, api_client):
        """GET /api/auth/github/config returns configured=true, mode=demo"""
        response = api_client.get(f"{BASE_URL}/api/auth/github/config")
        assert response.status_code == 200
        data = response.json()
        assert data["configured"] is True, "GitHub should be configured"
        assert data["mode"] == "demo", "GitHub should be in demo mode"
        assert "demo" in data.get("message", "").lower()
        print(f"✓ GitHub config: {data}")

    def test_github_login_returns_auth_url(self, api_client):
        """POST /api/auth/github/login returns mock auth_url"""
        response = api_client.post(f"{BASE_URL}/api/auth/github/login")
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data, "Response should contain auth_url"
        assert data["configured"] is True
        assert data["mode"] == "demo"
        # Mock auth_url should point to our own callback
        assert "/api/auth/github/callback" in data["auth_url"]
        assert "code=mock_" in data["auth_url"]
        assert "state=" in data["auth_url"]
        print(f"✓ GitHub login auth_url: {data['auth_url'][:80]}...")

    def test_github_callback_creates_user(self, api_client):
        """GET /api/auth/github/callback creates mock user and redirects"""
        # Note: This is a redirect endpoint, checking response is redirect
        response = api_client.get(
            f"{BASE_URL}/api/auth/github/callback",
            params={"code": "mock_test123", "state": "teststate"},
            allow_redirects=False
        )
        # Should redirect to frontend with session
        assert response.status_code in [302, 303, 307], f"Expected redirect, got {response.status_code}"
        location = response.headers.get("location", "")
        assert "/lumi#session_id=" in location, f"Should redirect to ENZI with session: {location}"
        print(f"✓ GitHub callback redirects to: {location[:60]}...")

    def test_github_callback_without_code_fails(self, api_client):
        """GET /api/auth/github/callback without code returns error"""
        response = api_client.get(f"{BASE_URL}/api/auth/github/callback")
        assert response.status_code == 400
        data = response.json()
        assert "code" in data.get("detail", "").lower() or "authorization" in data.get("detail", "").lower()
        print(f"✓ GitHub callback error without code: {data}")


# =========================
# PASSKEYS / WEBAUTHN TESTS
# =========================

class TestPasskeyWebAuthn:
    """Passkey/WebAuthn registration and login endpoints"""

    def test_passkey_register_start_for_existing_user(self, api_client):
        """POST /api/auth/passkey/register/start returns challenge for existing user"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/passkey/register/start",
            json={"email": ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        # Verify WebAuthn challenge structure
        assert "challenge" in data, "Should return challenge"
        assert "rp" in data, "Should return relying party"
        assert data["rp"]["name"] == "ENZI"
        assert "user" in data, "Should return user info"
        assert "pubKeyCredParams" in data, "Should return public key params"
        assert len(data["pubKeyCredParams"]) > 0
        assert data["timeout"] == 60000
        print(f"✓ Passkey register challenge: {data['challenge'][:40]}...")

    def test_passkey_register_start_for_nonexistent_user(self, api_client):
        """POST /api/auth/passkey/register/start returns 404 for non-existent user"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/passkey/register/start",
            json={"email": "nonexistent_user_xyz@test.com"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data.get("detail", "").lower()
        print(f"✓ Passkey register 404 for non-existent: {data}")

    def test_passkey_register_start_without_email(self, api_client):
        """POST /api/auth/passkey/register/start without email returns 400/422"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/passkey/register/start",
            json={}
        )
        # May return 400 or 422 (validation error)
        assert response.status_code in [400, 422]
        print(f"✓ Passkey register without email: {response.status_code}")

    def test_passkey_login_start_no_passkeys_registered(self, api_client):
        """POST /api/auth/passkey/login/start returns 404 when no passkeys registered"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/passkey/login/start",
            json={"email": ADMIN_EMAIL}
        )
        # Admin doesn't have passkeys registered, should return 404
        assert response.status_code == 404
        data = response.json()
        assert "no passkeys" in data.get("detail", "").lower()
        print(f"✓ Passkey login 404 (no passkeys): {data}")

    def test_passkey_login_start_for_nonexistent_user(self, api_client):
        """POST /api/auth/passkey/login/start for non-existent user returns 404"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/passkey/login/start",
            json={"email": "nobody_xyz@nowhere.com"}
        )
        assert response.status_code == 404
        print(f"✓ Passkey login 404 for non-existent user")


# =========================
# CROSS-PORTAL MEETING TESTS
# =========================

class TestCrossPortalMeetings:
    """Cross-portal meeting creation from ENZI to AI KARAU"""

    def test_quick_meeting_creation(self, api_client, admin_token):
        """POST /api/lumi/meetings/quick creates instant meeting"""
        response = api_client.post(
            f"{BASE_URL}/api/lumi/meetings/quick",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"title": "TEST_Quick_Meeting_Pytest"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "meeting_id" in data
        assert "join_url" in data
        assert "title" in data
        assert data["status"] == "waiting"
        assert "/karau-meet/meeting/" in data["join_url"]
        print(f"✓ Quick meeting created: {data['meeting_id']}")
        return data["meeting_id"]

    def test_quick_meeting_with_channel(self, api_client, admin_token):
        """POST /api/lumi/meetings/quick with channel_id posts notification"""
        response = api_client.post(
            f"{BASE_URL}/api/lumi/meetings/quick",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "TEST_Channel_Meeting",
                "channel_id": "test_channel_123",
                "participants": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "TEST_Channel_Meeting"
        print(f"✓ Quick meeting with channel: {data}")

    def test_schedule_meeting(self, api_client, admin_token):
        """POST /api/lumi/meetings/schedule schedules a meeting"""
        response = api_client.post(
            f"{BASE_URL}/api/lumi/meetings/schedule",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "TEST_Scheduled_Meeting_Pytest",
                "scheduled_at": "2026-03-15T14:00:00Z",
                "description": "Test scheduled meeting from pytest"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "meeting_id" in data
        assert "join_url" in data
        assert "scheduled_at" in data
        assert data["status"] == "scheduled"
        print(f"✓ Scheduled meeting: {data['meeting_id']} at {data['scheduled_at']}")

    def test_schedule_meeting_with_description(self, api_client, admin_token):
        """POST /api/lumi/meetings/schedule with description and channel_id"""
        response = api_client.post(
            f"{BASE_URL}/api/lumi/meetings/schedule",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "TEST_Full_Scheduled_Meeting",
                "scheduled_at": "2026-03-20T10:30:00Z",
                "channel_id": "channel_test",
                "participants": ["user1", "user2"],
                "description": "This is a comprehensive test meeting"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "TEST_Full_Scheduled_Meeting"
        print(f"✓ Full scheduled meeting: {data}")

    def test_get_active_meetings(self, api_client, admin_token):
        """GET /api/lumi/meetings/active returns user's meetings"""
        response = api_client.get(
            f"{BASE_URL}/api/lumi/meetings/active",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "meetings" in data
        assert "count" in data
        assert isinstance(data["meetings"], list)
        # Should have at least the meetings we created
        print(f"✓ Active meetings count: {data['count']}")
        # Verify meeting structure
        if data["meetings"]:
            meeting = data["meetings"][0]
            assert "id" in meeting
            assert "title" in meeting
            assert "status" in meeting
            assert "source" in meeting

    def test_meeting_creation_unauthorized(self, api_client):
        """POST /api/lumi/meetings/quick without auth returns 401"""
        response = api_client.post(
            f"{BASE_URL}/api/lumi/meetings/quick",
            json={"title": "Unauthorized Test"}
        )
        assert response.status_code == 401
        print(f"✓ Unauthorized meeting creation blocked")

    def test_schedule_meeting_missing_scheduled_at(self, api_client, admin_token):
        """POST /api/lumi/meetings/schedule without scheduled_at returns error"""
        response = api_client.post(
            f"{BASE_URL}/api/lumi/meetings/schedule",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"title": "Missing Time Meeting"}
        )
        # Should return 422 (validation error) since scheduled_at is required
        assert response.status_code == 422
        print(f"✓ Schedule without time returns validation error")


# =========================
# EMAIL/PASSWORD LOGIN TEST
# =========================

class TestEmailPasswordLogin:
    """Verify email/password login still works"""

    def test_admin_login_success(self, api_client):
        """POST /api/auth/login with admin credentials succeeds"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["is_admin"] is True
        print(f"✓ Admin login success: {data['user']['name']}")

    def test_invalid_password_fails(self, api_client):
        """POST /api/auth/login with wrong password returns 401"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": "wrongpassword"}
        )
        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data.get("detail", "").lower()
        print(f"✓ Invalid password rejected")

    def test_nonexistent_user_fails(self, api_client):
        """POST /api/auth/login with non-existent user returns 401"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "nobody@nowhere.com", "password": "anypass"}
        )
        assert response.status_code == 401
        print(f"✓ Non-existent user rejected")


# =========================
# AUTH PROVIDER CONFIG TESTS
# =========================

class TestAuthProviderConfigs:
    """Test auth provider configuration endpoints"""

    def test_microsoft_config(self, api_client):
        """GET /api/auth/microsoft/config returns config status"""
        response = api_client.get(f"{BASE_URL}/api/auth/microsoft/config")
        assert response.status_code == 200
        data = response.json()
        assert "configured" in data
        print(f"✓ Microsoft config: {data}")

    def test_apple_config(self, api_client):
        """GET /api/auth/apple/config returns Apple Sign-In config"""
        response = api_client.get(f"{BASE_URL}/api/auth/apple/config")
        assert response.status_code == 200
        data = response.json()
        assert "configured" in data
        print(f"✓ Apple config: {data}")

    def test_orcid_config(self, api_client):
        """GET /api/auth/orcid/config returns ORCID config"""
        response = api_client.get(f"{BASE_URL}/api/auth/orcid/config")
        assert response.status_code == 200
        data = response.json()
        assert "configured" in data
        print(f"✓ ORCID config: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
