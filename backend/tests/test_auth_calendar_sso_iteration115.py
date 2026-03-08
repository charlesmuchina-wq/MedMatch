"""
Iteration 115: Auth Fix + Calendar Integration + SSO/SAML 2.0 Tests
Tests:
- Auth endpoints return 401 (not 500) for unauthenticated requests
- Calendar integration endpoints (status, connect, disconnect)
- SSO/SAML 2.0 configuration and discovery
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://karau-enzi-nexus.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_USER_EMAIL = "test@medmatch.io"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_ORG_ID = "org_5a18c854f810"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin token for authenticated tests."""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def test_user_token():
    """Get non-admin user token for permission tests."""
    # Try to login, if fails register first
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    if response.status_code != 200:
        # Register test user
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": "Test User"
        })
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
    return response.json()["access_token"]


class TestAuthEndpoints:
    """Auth Fix: Verify 401 responses for unauthenticated requests."""

    def test_auth_me_without_token_returns_401(self):
        """GET /api/auth/me without token should return 401 (not 500)."""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        assert "Authentication required" in response.json().get("detail", "")

    def test_auth_me_with_invalid_token_returns_401(self):
        """GET /api/auth/me with invalid token should return 401."""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        assert response.status_code == 401

    def test_auth_me_with_valid_token_returns_200(self, admin_token):
        """GET /api/auth/me with valid token should return 200."""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert data["email"] == ADMIN_EMAIL

    def test_auth_preferences_without_token_returns_401(self):
        """GET /api/auth/preferences without token should return 401."""
        response = requests.get(f"{BASE_URL}/api/auth/preferences")
        assert response.status_code == 401


class TestCalendarIntegration:
    """Calendar Integration: Microsoft Outlook/365, Apple .ics, Google."""

    def test_calendar_status_authenticated(self, admin_token):
        """GET /api/karau-meet/calendar/status (authed) returns providers and configured."""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/calendar/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert "configured" in data
        # Microsoft not configured (no Azure credentials)
        assert data["configured"]["microsoft"] == False
        # Apple .ics always available
        assert data["configured"]["apple_ics"] == True

    def test_calendar_status_without_auth_returns_401(self):
        """GET /api/karau-meet/calendar/status without auth returns 401."""
        response = requests.get(f"{BASE_URL}/api/karau-meet/calendar/status")
        assert response.status_code == 401

    def test_microsoft_connect_returns_503_not_configured(self, admin_token):
        """GET /api/karau-meet/calendar/microsoft/connect (authed) returns 503 since not configured."""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/calendar/microsoft/connect",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 503
        assert "not configured" in response.json().get("detail", "").lower()

    def test_calendar_disconnect(self, admin_token):
        """POST /api/karau-meet/calendar/disconnect (authed) works."""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/calendar/disconnect",
            headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
            json={"provider": "microsoft"}
        )
        assert response.status_code == 200
        assert response.json()["success"] == True


class TestSSOSAML:
    """SSO/SAML 2.0: Configuration, login flow, metadata."""

    def test_sso_metadata_returns_xml(self):
        """GET /api/karau-meet/sso/metadata returns XML metadata."""
        response = requests.get(f"{BASE_URL}/api/karau-meet/sso/metadata")
        assert response.status_code == 200
        assert "xml" in response.headers.get("content-type", "").lower()
        assert "EntityDescriptor" in response.text
        assert "https://aikarau.com/saml/metadata" in response.text

    def test_sso_discover_no_sso(self):
        """GET /api/karau-meet/sso/discover?email=test@example.com returns sso_available:false."""
        response = requests.get(f"{BASE_URL}/api/karau-meet/sso/discover?email=test@example.com")
        assert response.status_code == 200
        assert response.json()["sso_available"] == False

    def test_sso_configure_admin_success(self, admin_token):
        """POST /api/karau-meet/sso/configure (admin) saves SSO config."""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/sso/configure",
            headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
            json={
                "org_id": TEST_ORG_ID,
                "idp_entity_id": "https://idp.test.com/saml/metadata",
                "idp_sso_url": "https://idp.test.com/saml/sso",
                "idp_slo_url": "https://idp.test.com/saml/slo",
                "idp_certificate": "-----BEGIN CERTIFICATE-----\nTEST_CERT\n-----END CERTIFICATE-----",
                "enforce_sso": False,
                "auto_provision": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "sp_metadata" in data

    def test_sso_get_config_admin(self, admin_token):
        """GET /api/karau-meet/sso/config/{org_id} (admin) returns config."""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/sso/config/{TEST_ORG_ID}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("configured") == True or data.get("org_id") == TEST_ORG_ID

    def test_sso_update_config_admin(self, admin_token):
        """PUT /api/karau-meet/sso/config/{org_id} (admin) updates config."""
        response = requests.put(
            f"{BASE_URL}/api/karau-meet/sso/config/{TEST_ORG_ID}",
            headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
            json={"enforce_sso": True}
        )
        assert response.status_code == 200
        assert response.json()["success"] == True

    def test_sso_delete_config_admin(self, admin_token):
        """DELETE /api/karau-meet/sso/config/{org_id} (admin) deletes config."""
        response = requests.delete(
            f"{BASE_URL}/api/karau-meet/sso/config/{TEST_ORG_ID}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["success"] == True
        
        # Verify deleted
        verify_response = requests.get(
            f"{BASE_URL}/api/karau-meet/sso/config/{TEST_ORG_ID}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert verify_response.json().get("configured") == False

    def test_sso_configure_non_admin_returns_403(self, test_user_token):
        """POST /api/karau-meet/sso/configure without admin returns 403."""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/sso/configure",
            headers={"Authorization": f"Bearer {test_user_token}", "Content-Type": "application/json"},
            json={
                "org_id": "org_test_unauthorized",
                "idp_entity_id": "https://idp.example.com/saml/metadata",
                "idp_sso_url": "https://idp.example.com/saml/sso",
                "idp_certificate": "-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----"
            }
        )
        assert response.status_code == 403
        assert "Admin access required" in response.json().get("detail", "")
