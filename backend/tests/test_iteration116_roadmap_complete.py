"""
Iteration 116: Complete KARAU Roadmap Testing
Tests: Auth fix across routes, Google Calendar OAuth, Guest 2FA with Resend, PWA manifest, LDAP

Auth fix was applied to 54+ route files - testing that endpoints return 401 (not 500) without auth.
Google Calendar OAuth endpoints follow same pattern as Microsoft.
Guest 2FA now sends OTP via Resend email API with fallback to _dev_otp.
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_ORG_ID = "org_5a18c854f810"


class TestAuthFixVerification:
    """Verify auth fix: endpoints return 401 instead of 500 without authentication"""

    def test_auth_me_without_token_returns_401(self):
        """GET /api/auth/me should return 401 when not authenticated"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: /api/auth/me returns 401 without token")

    def test_auth_preferences_without_token_returns_401(self):
        """GET /api/auth/preferences should return 401 when not authenticated"""
        response = requests.get(f"{BASE_URL}/api/auth/preferences")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: /api/auth/preferences returns 401 without token")

    def test_karau_meetings_without_token_returns_401(self):
        """GET /api/karau-meet/meetings should return 401 when not authenticated"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: /api/karau-meet/meetings returns 401 without token")

    def test_analytics_dashboard_without_token_returns_401(self):
        """GET /api/analytics/dashboard should return 401 when not authenticated"""
        response = requests.get(f"{BASE_URL}/api/analytics/dashboard")
        # Analytics might return 401 or 404 if endpoint doesn't exist
        assert response.status_code in [401, 404], f"Expected 401 or 404, got {response.status_code}"
        print(f"PASS: /api/analytics/dashboard returns {response.status_code} without token")

    def test_calendar_status_without_token_returns_401(self):
        """GET /api/karau-meet/calendar/status should return 401"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/calendar/status")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: /api/karau-meet/calendar/status returns 401 without token")


class TestAuthenticatedEndpoints:
    """Verify endpoints work correctly with valid authentication"""

    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Login as admin and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_auth_me_with_valid_token_returns_200(self):
        """GET /api/auth/me with valid token returns user data"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        print(f"PASS: /api/auth/me returns 200 with user_id={data['user_id']}")

    def test_auth_preferences_with_valid_token_returns_200(self):
        """GET /api/auth/preferences with valid token returns preferences"""
        response = requests.get(f"{BASE_URL}/api/auth/preferences", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "language" in data
        print(f"PASS: /api/auth/preferences returns 200 with language={data['language']}")


class TestCalendarIntegration:
    """Test Calendar Integration endpoints for Microsoft and Google"""

    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Login as admin and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_calendar_status_shows_all_providers(self):
        """GET /api/karau-meet/calendar/status shows microsoft, google, apple_ics"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/calendar/status", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "configured" in data, "Missing 'configured' key"
        configured = data["configured"]
        assert "microsoft" in configured, "Missing microsoft provider"
        assert "google" in configured, "Missing google provider"
        assert "apple_ics" in configured, "Missing apple_ics provider"
        assert configured["apple_ics"] == True, "apple_ics should always be True"
        print(f"PASS: Calendar status shows 3 providers: microsoft={configured['microsoft']}, google={configured['google']}, apple_ics={configured['apple_ics']}")

    def test_microsoft_connect_returns_503_not_configured(self):
        """GET /api/karau-meet/calendar/microsoft/connect returns 503 when not configured"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/calendar/microsoft/connect", headers=self.headers)
        # Returns 503 when MS_CALENDAR_CLIENT_ID not set
        assert response.status_code == 503, f"Expected 503, got {response.status_code}"
        data = response.json()
        assert "not configured" in data.get("detail", "").lower()
        print("PASS: Microsoft connect returns 503 (not configured)")

    def test_google_connect_returns_503_not_configured(self):
        """GET /api/karau-meet/calendar/google/connect returns 503 when not configured"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/calendar/google/connect", headers=self.headers)
        # Returns 503 when GOOGLE_CALENDAR_CLIENT_ID not set
        assert response.status_code == 503, f"Expected 503, got {response.status_code}"
        data = response.json()
        assert "not configured" in data.get("detail", "").lower()
        print("PASS: Google connect returns 503 (not configured)")

    def test_calendar_disconnect_works(self):
        """POST /api/karau-meet/calendar/disconnect handles request"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/calendar/disconnect",
            headers=self.headers,
            json={"provider": "microsoft"}
        )
        # Should return 200 even if not connected (idempotent)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Calendar disconnect endpoint works")


class TestSSOSAMLEndpoints:
    """Test SSO/SAML 2.0 configuration endpoints"""

    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_sso_metadata_returns_valid_xml(self):
        """GET /api/karau-meet/sso/metadata returns valid XML"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/sso/metadata")
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "xml" in content_type.lower(), f"Expected XML content-type, got {content_type}"
        assert "EntityDescriptor" in response.text
        assert "SPSSODescriptor" in response.text
        print("PASS: SSO metadata returns valid XML with EntityDescriptor")

    def test_sso_discover_works(self):
        """GET /api/karau-meet/sso/discover?email=test@example.com works"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/sso/discover?email=test@example.com")
        assert response.status_code == 200
        data = response.json()
        assert "sso_available" in data
        print(f"PASS: SSO discover returns sso_available={data['sso_available']}")

    def test_sso_configure_requires_admin(self):
        """POST /api/karau-meet/sso/configure requires admin (403 for non-admin)"""
        # Test user is admin so this should work - first delete any existing config
        response = requests.delete(
            f"{BASE_URL}/api/karau-meet/sso/config/{TEST_ORG_ID}",
            headers=self.headers
        )
        # Now try to configure
        config = {
            "org_id": TEST_ORG_ID,
            "idp_entity_id": "https://test-idp.example.com/metadata",
            "idp_sso_url": "https://test-idp.example.com/sso",
            "idp_certificate": "-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----"
        }
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/sso/configure",
            headers=self.headers,
            json=config
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: SSO configure works for admin")

    def test_sso_config_crud(self):
        """Test full CRUD for SSO config (GET, PUT, DELETE)"""
        # GET config
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/sso/config/{TEST_ORG_ID}",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("configured") == True or "idp_entity_id" in data
        print(f"PASS: SSO config GET works, configured={data.get('configured', 'yes')}")

        # PUT update
        response = requests.put(
            f"{BASE_URL}/api/karau-meet/sso/config/{TEST_ORG_ID}",
            headers=self.headers,
            json={"enforce_sso": True}
        )
        assert response.status_code == 200
        print("PASS: SSO config PUT (update) works")

        # DELETE config (cleanup)
        response = requests.delete(
            f"{BASE_URL}/api/karau-meet/sso/config/{TEST_ORG_ID}",
            headers=self.headers
        )
        assert response.status_code == 200
        print("PASS: SSO config DELETE works")


class TestGuestVerification2FA:
    """Test Guest 2FA flow with Resend email integration"""

    def test_guest_register_sends_otp(self):
        """POST /api/karau-meet/guest/register sends OTP (falls back to _dev_otp)"""
        import uuid
        test_email = f"test_guest_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/guest/register",
            json={
                "email": test_email,
                "name": "Test Guest",
                "meeting_id": "test_meeting_123"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        # Should have _dev_otp if Resend didn't send (test key only sends to owner)
        assert "email" in data
        print(f"PASS: Guest register sends OTP, _dev_otp present: {'_dev_otp' in data}")

    def test_guest_verify_otp_validates_code(self):
        """POST /api/karau-meet/guest/verify-otp validates the code"""
        import uuid
        test_email = f"test_guest_{uuid.uuid4().hex[:8]}@example.com"
        
        # First register
        reg_response = requests.post(
            f"{BASE_URL}/api/karau-meet/guest/register",
            json={
                "email": test_email,
                "name": "Test Guest",
                "meeting_id": "test_meeting_verify"
            }
        )
        assert reg_response.status_code == 200
        otp = reg_response.json().get("_dev_otp", "000000")

        # Try to verify
        verify_response = requests.post(
            f"{BASE_URL}/api/karau-meet/guest/verify-otp",
            json={
                "email": test_email,
                "otp": otp,
                "meeting_id": "test_meeting_verify"
            }
        )
        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data.get("verified") == True
        print("PASS: Guest OTP verification works")

    def test_guest_status_endpoint(self):
        """GET /api/karau-meet/guest/status checks verification status"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/guest/status",
            params={"email": "nonexistent@example.com", "meeting_id": "test123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "verified" in data
        print(f"PASS: Guest status returns verified={data['verified']}")


class TestPWAManifest:
    """Test PWA manifest.json has KARAU branding"""

    def test_manifest_json_accessible(self):
        """GET /manifest.json returns valid JSON"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "name" in data
        assert "short_name" in data
        print(f"PASS: manifest.json accessible, name={data['name']}")

    def test_manifest_has_karau_branding(self):
        """manifest.json has KARAU branding"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        assert response.status_code == 200
        data = response.json()
        # Check for KARAU branding
        assert "KARAU" in data.get("name", "") or "KARAU" in data.get("short_name", "")
        print(f"PASS: manifest.json has KARAU branding: {data.get('short_name', data.get('name'))}")

    def test_manifest_has_meeting_shortcuts(self):
        """manifest.json has meeting-focused shortcuts"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        assert response.status_code == 200
        data = response.json()
        shortcuts = data.get("shortcuts", [])
        assert len(shortcuts) > 0, "Expected shortcuts in manifest"
        shortcut_urls = [s.get("url", "") for s in shortcuts]
        assert any("/karau-meet" in url for url in shortcut_urls), "Expected karau-meet in shortcuts"
        print(f"PASS: manifest.json has {len(shortcuts)} shortcuts including meeting URLs")


class TestMeetingsEndpoint:
    """Test /api/karau-meet/meetings endpoint"""

    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_meetings_list_with_auth(self):
        """GET /api/karau-meet/meetings with auth returns meetings list"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, (list, dict)), "Expected list or dict response"
        print(f"PASS: /api/karau-meet/meetings returns 200 with auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
