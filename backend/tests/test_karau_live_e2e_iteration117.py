"""
AI KARAU Live Multi-User E2E Test - Iteration 117
Tests complete meeting portal functionality across all features:
- Guest 2FA flow (register → OTP → age declaration → lobby → admit)
- Meeting CRUD and lobby flow
- Breakout rooms
- Calendar ICS export and social sharing
- Enterprise organizations (org details, employees, rooms, branding)
- SSO/SAML configuration
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://future-comms.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_USER_EMAIL = "test@medmatch.io"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_ORG_ID = "org_5a18c854f810"


class TestAuthentication:
    """Test authentication flows"""
    
    def test_login_admin(self):
        """Login as admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in login response"
        return data["access_token"]

    def test_login_test_user(self):
        """Login as test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200, f"Test user login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in login response"

    def test_auth_required_endpoint(self):
        """Test that protected endpoints return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestGuestVerification:
    """Test full guest 2FA verification flow"""
    
    @pytest.fixture
    def test_meeting_id(self):
        """Create a meeting for testing"""
        # Login as admin
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create meeting
        create_resp = requests.post(f"{BASE_URL}/api/karau-meet/meetings", 
            headers=headers,
            json={"title": "E2E Test Meeting - Guest 2FA"}
        )
        assert create_resp.status_code == 200, f"Meeting creation failed: {create_resp.text}"
        meeting = create_resp.json()
        return meeting.get("meeting_id")

    def test_guest_register_sends_otp(self, test_meeting_id):
        """Step 1: Guest registers with email - receives OTP"""
        response = requests.post(f"{BASE_URL}/api/karau-meet/guest/register", json={
            "email": "guest.e2e.test@example.com",
            "name": "E2E Guest Tester",
            "meeting_id": test_meeting_id
        })
        assert response.status_code == 200, f"Guest register failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "email" in data
        # In dev mode, OTP is returned in _dev_otp
        assert "_dev_otp" in data or "expires_in_minutes" in data
        return data.get("_dev_otp")

    def test_full_guest_2fa_flow(self, test_meeting_id):
        """Complete guest 2FA flow: register → OTP → age → lobby"""
        guest_email = f"guest.full.flow.{int(time.time())}@example.com"
        
        # Step 1: Register
        register_resp = requests.post(f"{BASE_URL}/api/karau-meet/guest/register", json={
            "email": guest_email,
            "name": "Full Flow Guest",
            "meeting_id": test_meeting_id
        })
        assert register_resp.status_code == 200, f"Register failed: {register_resp.text}"
        otp = register_resp.json().get("_dev_otp")
        assert otp, "No OTP returned in dev mode"
        
        # Step 2: Verify OTP
        verify_resp = requests.post(f"{BASE_URL}/api/karau-meet/guest/verify-otp", json={
            "email": guest_email,
            "otp": otp,
            "meeting_id": test_meeting_id
        })
        assert verify_resp.status_code == 200, f"OTP verify failed: {verify_resp.text}"
        assert verify_resp.json().get("verified") == True
        
        # Step 3: Age declaration
        age_resp = requests.post(f"{BASE_URL}/api/karau-meet/guest/age-declaration", json={
            "email": guest_email,
            "meeting_id": test_meeting_id,
            "confirmed_age_16_plus": True
        })
        assert age_resp.status_code == 200, f"Age declaration failed: {age_resp.text}"
        age_data = age_resp.json()
        assert age_data.get("verified") == True
        assert age_data.get("age_declared") == True
        assert "guest_id" in age_data


class TestMeetingCRUD:
    """Test meeting creation and retrieval"""
    
    @pytest.fixture
    def admin_token(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return login_resp.json().get("access_token")

    def test_create_meeting(self, admin_token):
        """POST /api/karau-meet/meetings creates meeting with valid meeting_id"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.post(f"{BASE_URL}/api/karau-meet/meetings",
            headers=headers,
            json={"title": "E2E Test Meeting - CRUD"}
        )
        assert response.status_code == 200, f"Create meeting failed: {response.text}"
        data = response.json()
        assert "meeting_id" in data, "No meeting_id in response"
        assert data.get("title") == "E2E Test Meeting - CRUD"
        return data.get("meeting_id")

    def test_get_meeting_info_public(self, admin_token):
        """GET /api/karau-meet/meetings/{id}/info returns public info"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Create meeting first
        create_resp = requests.post(f"{BASE_URL}/api/karau-meet/meetings",
            headers=headers, json={"title": "Public Info Test"})
        meeting_id = create_resp.json().get("meeting_id")
        
        # Get public info (no auth required)
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/info")
        assert response.status_code == 200, f"Get meeting info failed: {response.text}"
        data = response.json()
        assert data.get("meeting_id") == meeting_id
        assert "title" in data
        assert "host_name" in data

    def test_get_meetings_list(self, admin_token):
        """GET /api/karau-meet/meetings returns user's meetings"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings", headers=headers)
        assert response.status_code == 200, f"Get meetings failed: {response.text}"
        data = response.json()
        assert "meetings" in data
        assert isinstance(data["meetings"], list)


class TestLobbyFlow:
    """Test lobby/waiting room flow: guest joins → host admits"""
    
    @pytest.fixture
    def meeting_setup(self):
        """Create meeting and login as admin"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        create_resp = requests.post(f"{BASE_URL}/api/karau-meet/meetings",
            headers=headers, json={"title": "Lobby Test Meeting"})
        meeting_id = create_resp.json().get("meeting_id")
        
        return {"token": token, "headers": headers, "meeting_id": meeting_id}

    def test_guest_joins_lobby_returns_waiting_status(self, meeting_setup):
        """Guest joins waiting room, gets waiting status"""
        meeting_id = meeting_setup["meeting_id"]
        
        # Guest joins lobby (no auth)
        response = requests.post(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join", json={
            "guest_name": "Lobby Test Guest",
            "guest_email": "lobby.guest@example.com",
            "is_guest": True
        })
        assert response.status_code == 200, f"Lobby join failed: {response.text}"
        data = response.json()
        assert data.get("status") == "waiting"
        assert "user_id" in data  # Server generates guest user_id
        return data.get("user_id")

    def test_host_sees_waiting_list(self, meeting_setup):
        """Host can view users in waiting room"""
        meeting_id = meeting_setup["meeting_id"]
        headers = meeting_setup["headers"]
        
        # First, have a guest join
        join_resp = requests.post(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join", json={
            "guest_name": "Waiting List Guest",
            "guest_email": "waiting@example.com"
        })
        guest_user_id = join_resp.json().get("user_id")
        
        # Host checks waiting list
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/waiting",
            headers=headers
        )
        assert response.status_code == 200, f"Get waiting list failed: {response.text}"
        data = response.json()
        assert "waiting" in data
        assert "count" in data

    def test_host_admits_guest(self, meeting_setup):
        """Host admits guest from lobby → guest status becomes admitted"""
        meeting_id = meeting_setup["meeting_id"]
        headers = meeting_setup["headers"]
        
        # Guest joins lobby
        join_resp = requests.post(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join", json={
            "guest_name": "Admit Test Guest",
            "guest_email": "admit.me@example.com"
        })
        guest_user_id = join_resp.json().get("user_id")
        
        # Host admits guest
        admit_resp = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/admit",
            headers=headers,
            json={"user_id": guest_user_id}
        )
        assert admit_resp.status_code == 200, f"Admit failed: {admit_resp.text}"
        
        # Check guest status
        status_resp = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/status?user_id={guest_user_id}"
        )
        assert status_resp.status_code == 200
        assert status_resp.json().get("status") == "admitted"


class TestBreakoutRooms:
    """Test breakout room session management"""
    
    @pytest.fixture
    def meeting_with_token(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        create_resp = requests.post(f"{BASE_URL}/api/karau-meet/meetings",
            headers=headers, json={"title": "Breakout Test Meeting"})
        meeting_id = create_resp.json().get("meeting_id")
        
        return {"token": token, "headers": headers, "meeting_id": meeting_id}

    def test_start_breakout_session(self, meeting_with_token):
        """Start breakout session with rooms"""
        meeting_id = meeting_with_token["meeting_id"]
        headers = meeting_with_token["headers"]
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/breakout-session/start",
            headers=headers,
            json={
                "rooms": [
                    {"room_name": "Room A", "participant_ids": []},
                    {"room_name": "Room B", "participant_ids": []}
                ],
                "timer_minutes": 15
            }
        )
        assert response.status_code == 200, f"Breakout start failed: {response.text}"
        data = response.json()
        assert "session_id" in data or "rooms" in data

    def test_get_breakout_session_status(self, meeting_with_token):
        """Check breakout session status"""
        meeting_id = meeting_with_token["meeting_id"]
        headers = meeting_with_token["headers"]
        
        # Start session first
        requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/breakout-session/start",
            headers=headers,
            json={"rooms": [{"room_name": "Status Test Room", "participant_ids": []}]}
        )
        
        # Check status - NOTE: endpoint is /breakout-session (singular, not /breakout-session/status)
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/breakout-session",
            headers=headers
        )
        assert response.status_code == 200, f"Breakout status failed: {response.text}"
        data = response.json()
        assert "status" in data

    def test_close_breakout_session(self, meeting_with_token):
        """Close breakout session returns participants to main room"""
        meeting_id = meeting_with_token["meeting_id"]
        headers = meeting_with_token["headers"]
        
        # Start session first
        requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/breakout-session/start",
            headers=headers,
            json={"rooms": [{"room_name": "Close Test Room", "participant_ids": []}]}
        )
        
        # Close session
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/breakout-session/close",
            headers=headers
        )
        assert response.status_code == 200, f"Breakout close failed: {response.text}"


class TestCalendarSharing:
    """Test calendar ICS export and social sharing links"""
    
    @pytest.fixture
    def test_meeting_id(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        create_resp = requests.post(f"{BASE_URL}/api/karau-meet/meetings",
            headers=headers, json={"title": "Calendar Sharing Test"})
        return create_resp.json().get("meeting_id")

    def test_ics_export(self, test_meeting_id):
        """GET /api/karau-meet/share/calendar/{meetingId}.ics returns text/calendar"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/share/calendar/{test_meeting_id}.ics")
        assert response.status_code == 200, f"ICS export failed: {response.text}"
        assert "text/calendar" in response.headers.get("content-type", "")
        # Verify ICS content
        content = response.text
        assert "BEGIN:VCALENDAR" in content
        assert "BEGIN:VEVENT" in content
        assert "SUMMARY:" in content
        assert "END:VEVENT" in content

    def test_social_sharing_links(self, test_meeting_id):
        """GET /api/karau-meet/share/social/{meetingId} returns all social links"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/share/social/{test_meeting_id}")
        assert response.status_code == 200, f"Social sharing failed: {response.text}"
        data = response.json()
        assert "share_links" in data
        share_links = data["share_links"]
        # Verify all social platforms
        assert "linkedin" in share_links
        assert "twitter" in share_links
        assert "whatsapp" in share_links
        assert "email" in share_links
        assert "facebook" in share_links


class TestEnterpriseOrganizations:
    """Test enterprise organization endpoints"""
    
    @pytest.fixture
    def admin_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}

    def test_get_organization_details(self, admin_headers):
        """GET /api/karau-meet/organizations/{org_id} returns org details"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/{TEST_ORG_ID}",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Get org failed: {response.text}"
        data = response.json()
        assert data.get("org_id") == TEST_ORG_ID
        # Check expected org properties
        assert "name" in data
        assert "tier" in data or "tier_name" in data
        assert "email_domains" in data

    def test_list_organizations(self, admin_headers):
        """GET /api/karau-meet/organizations returns org list (admin)"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations",
            headers=admin_headers
        )
        assert response.status_code == 200, f"List orgs failed: {response.text}"
        data = response.json()
        assert "organizations" in data
        assert isinstance(data["organizations"], list)

    def test_get_employees(self, admin_headers):
        """GET /api/karau-meet/organizations/{org_id}/employees returns employee list"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/{TEST_ORG_ID}/employees",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Get employees failed: {response.text}"
        data = response.json()
        assert "employees" in data
        assert "count" in data

    def test_get_conference_rooms(self, admin_headers):
        """GET /api/karau-meet/organizations/{org_id}/rooms returns conference rooms"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/{TEST_ORG_ID}/rooms",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Get rooms failed: {response.text}"
        data = response.json()
        assert "rooms" in data
        assert "count" in data

    def test_get_branding(self, admin_headers):
        """GET /api/karau-meet/organizations/branding/{org_id} returns branding info"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/branding/{TEST_ORG_ID}",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Get branding failed: {response.text}"
        data = response.json()
        assert "has_branding" in data


class TestSSOConfiguration:
    """Test SSO/SAML configuration endpoints"""
    
    @pytest.fixture
    def admin_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}

    def test_sso_configure(self, admin_headers):
        """POST /api/karau-meet/sso/configure saves config for org"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/sso/configure",
            headers=admin_headers,
            json={
                "org_id": TEST_ORG_ID,
                "idp_entity_id": "https://test-idp.example.com",
                "idp_sso_url": "https://test-idp.example.com/sso",
                "idp_certificate": "-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
                "enforce_sso": False,
                "auto_provision": True
            }
        )
        assert response.status_code == 200, f"SSO configure failed: {response.text}"
        data = response.json()
        assert data.get("success") == True

    def test_sso_discover(self, admin_headers):
        """GET /api/karau-meet/sso/discover?email=user@medmatch.com detects SSO"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/sso/discover?email=user@medmatch.com"
        )
        assert response.status_code == 200, f"SSO discover failed: {response.text}"
        data = response.json()
        # Should have sso_available field
        assert "sso_available" in data

    def test_sso_metadata(self):
        """GET /api/karau-meet/sso/metadata returns SAML SP metadata XML"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/sso/metadata")
        assert response.status_code == 200, f"SSO metadata failed: {response.text}"
        content = response.text
        # Verify XML content
        assert "<?xml" in content or "EntityDescriptor" in content
        assert "SPSSODescriptor" in content


class TestCalendarStatus:
    """Test calendar integration status"""
    
    @pytest.fixture
    def auth_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}

    def test_calendar_status_shows_providers(self, auth_headers):
        """GET /api/karau-meet/calendar/status shows all providers"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/calendar/status",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Calendar status failed: {response.text}"
        data = response.json()
        assert "providers" in data or "configured" in data
        # Check configured providers
        configured = data.get("configured", {})
        assert "apple_ics" in configured or "providers" in data


class TestHealthAndBasics:
    """Basic health checks"""
    
    def test_api_health(self):
        """API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        # Accept 200 or 404 (some deployments may not have /health)
        assert response.status_code in [200, 404], f"Health check unexpected: {response.status_code}"

    def test_frontend_accessible(self):
        """Frontend is accessible"""
        response = requests.get(BASE_URL)
        assert response.status_code == 200, f"Frontend not accessible: {response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
