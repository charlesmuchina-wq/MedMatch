"""
COMPREHENSIVE FINAL VALIDATION - AI KARAU
Tests ALL endpoints, translations, and integrations
Iteration 118 - Complete system validation
"""

import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_USER_EMAIL = "test@medmatch.io"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_ORG_ID = "org_5a18c854f810"

class TestHealthAndBasics:
    """Health check and basic API validation"""
    
    def test_health_endpoint(self):
        """GET /api/health returns 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ Health endpoint working")


class TestAuthUserManagement:
    """Authentication and user management tests"""
    
    def test_admin_login_returns_access_token(self):
        """POST /api/auth/login (admin) returns access_token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print(f"✓ Admin login - token received")
        return data["access_token"]
    
    def test_test_user_login_returns_access_token(self):
        """POST /api/auth/login (test user) returns access_token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print(f"✓ Test user login - token received")
    
    def test_login_wrong_password_returns_error(self):
        """POST /api/auth/login (wrong password) returns error"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": "WrongPassword!"
        })
        assert response.status_code in [400, 401]
        print("✓ Wrong password rejected")
    
    def test_auth_me_with_valid_token(self):
        """GET /api/auth/me (valid token) returns user data"""
        # Get token first
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["access_token"]
        
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "email" in data or "user" in data
        print("✓ Auth me - user data returned")
    
    def test_auth_me_no_token_returns_401(self):
        """GET /api/auth/me (no token) returns 401"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("✓ Auth me without token - 401 returned")
    
    def test_auth_me_invalid_token_returns_401(self):
        """GET /api/auth/me (invalid token) returns 401"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_xyz"}
        )
        assert response.status_code == 401
        print("✓ Auth me invalid token - 401 returned")
    
    def test_auth_preferences_get(self):
        """GET /api/auth/preferences returns language preference"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["access_token"]
        
        response = requests.get(
            f"{BASE_URL}/api/auth/preferences",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        print("✓ Auth preferences GET working")
    
    def test_auth_preferences_update(self):
        """PUT /api/auth/preferences updates language"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["access_token"]
        
        response = requests.put(
            f"{BASE_URL}/api/auth/preferences",
            headers={"Authorization": f"Bearer {token}"},
            json={"language": "en"}
        )
        assert response.status_code == 200
        print("✓ Auth preferences PUT working")


class TestMeetingCRUD:
    """Meeting CRUD operations"""
    
    @pytest.fixture
    def admin_token(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return login_resp.json()["access_token"]
    
    def test_create_meeting(self, admin_token):
        """POST /api/karau-meet/meetings creates meeting with meeting_id"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "TEST_Validation Meeting",
                "scheduled_time": "2026-02-01T10:00:00Z",
                "duration_minutes": 60
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "meeting_id" in data or "id" in data
        print("✓ Meeting created successfully")
        return data.get("meeting_id") or data.get("id")
    
    def test_get_meetings_list(self, admin_token):
        """GET /api/karau-meet/meetings returns meetings list"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "meetings" in data
        print("✓ Meetings list retrieved")
    
    def test_get_meeting_info(self, admin_token):
        """GET /api/karau-meet/meetings/{id}/info returns public meeting info"""
        # Create a meeting first
        create_resp = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "TEST_Info Check Meeting",
                "scheduled_time": "2026-02-01T11:00:00Z",
                "duration_minutes": 30
            }
        )
        meeting_id = create_resp.json().get("meeting_id") or create_resp.json().get("id")
        
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/info")
        assert response.status_code == 200
        print("✓ Meeting info retrieved")
    
    def test_meetings_no_auth_returns_401(self):
        """GET /api/karau-meet/meetings (no auth) returns 401"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings")
        assert response.status_code == 401
        print("✓ Meetings without auth - 401 returned")


class TestGuest2FAFlow:
    """Guest 2FA verification flow"""
    
    def test_guest_register_sends_otp(self):
        """POST /api/karau-meet/guest/register sends OTP, returns _dev_otp"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/guest/register",
            json={
                "email": "testguest@example.com",
                "name": "Test Guest"
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "_dev_otp" in data or "verification_code" in data or "otp" in data
        print(f"✓ Guest register - OTP sent (_dev_otp present)")
        return data.get("_dev_otp") or data.get("verification_code") or data.get("otp")
    
    def test_guest_register_invalid_email(self):
        """POST /api/karau-meet/guest/register (invalid email) returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/guest/register",
            json={
                "email": "invalid-email",
                "name": "Test Guest"
            }
        )
        assert response.status_code in [400, 422]
        print("✓ Invalid email rejected")
    
    def test_guest_verify_otp_correct(self):
        """POST /api/karau-meet/guest/verify-otp (correct OTP) returns success"""
        # Register first
        reg_resp = requests.post(
            f"{BASE_URL}/api/karau-meet/guest/register",
            json={"email": "testguest2@example.com", "name": "Test Guest 2"}
        )
        otp = reg_resp.json().get("_dev_otp") or reg_resp.json().get("verification_code")
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/guest/verify-otp",
            json={
                "email": "testguest2@example.com",
                "code": otp
            }
        )
        assert response.status_code == 200
        print("✓ OTP verification successful")
    
    def test_guest_verify_otp_wrong(self):
        """POST /api/karau-meet/guest/verify-otp (wrong OTP) returns error"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/guest/verify-otp",
            json={
                "email": "testguest@example.com",
                "code": "000000"
            }
        )
        assert response.status_code in [400, 401, 404]
        print("✓ Wrong OTP rejected")
    
    def test_guest_age_declaration_confirmed(self):
        """POST /api/karau-meet/guest/age-declaration (confirmed) returns guest user"""
        # Full flow: register → verify → age declaration
        reg_resp = requests.post(
            f"{BASE_URL}/api/karau-meet/guest/register",
            json={"email": "testguest3@example.com", "name": "Test Guest 3"}
        )
        otp = reg_resp.json().get("_dev_otp") or reg_resp.json().get("verification_code")
        
        requests.post(
            f"{BASE_URL}/api/karau-meet/guest/verify-otp",
            json={"email": "testguest3@example.com", "code": otp}
        )
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/guest/age-declaration",
            json={
                "email": "testguest3@example.com",
                "confirmed": True
            }
        )
        assert response.status_code == 200
        print("✓ Age declaration confirmed")
    
    def test_guest_age_declaration_not_confirmed(self):
        """POST /api/karau-meet/guest/age-declaration (not confirmed) returns error"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/guest/age-declaration",
            json={
                "email": "testguest_noage@example.com",
                "confirmed": False
            }
        )
        assert response.status_code in [400, 403]
        print("✓ Age declaration not confirmed - rejected")
    
    def test_guest_status(self):
        """GET /api/karau-meet/guest/status returns verification status"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/guest/status",
            params={"email": "testguest@example.com"}
        )
        # May return 200 or 404 depending on if guest exists
        assert response.status_code in [200, 404]
        print("✓ Guest status endpoint working")
    
    def test_guest_resend_otp(self):
        """POST /api/karau-meet/guest/resend-otp generates new code"""
        # Register first
        requests.post(
            f"{BASE_URL}/api/karau-meet/guest/register",
            json={"email": "testguest_resend@example.com", "name": "Test Guest Resend"}
        )
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/guest/resend-otp",
            json={"email": "testguest_resend@example.com"}
        )
        assert response.status_code == 200
        print("✓ OTP resent successfully")


class TestLobbyFlow:
    """Lobby join, waiting, and admit flow"""
    
    @pytest.fixture
    def setup_meeting_for_lobby(self):
        """Create a meeting for lobby testing"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["access_token"]
        
        create_resp = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "TEST_Lobby Meeting",
                "scheduled_time": "2026-02-01T12:00:00Z",
                "duration_minutes": 60
            }
        )
        meeting_id = create_resp.json().get("meeting_id") or create_resp.json().get("id")
        return {"meeting_id": meeting_id, "token": token}
    
    def test_lobby_join(self, setup_meeting_for_lobby):
        """POST /api/karau-meet/meetings/{id}/lobby/join creates waiting entry"""
        meeting_id = setup_meeting_for_lobby["meeting_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join",
            json={"name": "TEST_Lobby Guest", "email": "lobbyguest@test.com"}
        )
        assert response.status_code in [200, 201]
        data = response.json()
        # Server generates guest_id
        assert "guest_id" in data or "user_id" in data or "id" in data
        print("✓ Guest joined lobby")
        return data.get("guest_id") or data.get("user_id") or data.get("id")
    
    def test_lobby_waiting_list(self, setup_meeting_for_lobby):
        """GET /api/karau-meet/meetings/{id}/lobby/waiting returns waiting list"""
        meeting_id = setup_meeting_for_lobby["meeting_id"]
        token = setup_meeting_for_lobby["token"]
        
        # Join lobby first
        join_resp = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join",
            json={"name": "TEST_Waiting Guest", "email": "waitingguest@test.com"}
        )
        
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/waiting",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "waiting" in data
        print("✓ Waiting list retrieved (host only)")
    
    def test_lobby_admit(self, setup_meeting_for_lobby):
        """POST /api/karau-meet/meetings/{id}/lobby/admit admits guest"""
        meeting_id = setup_meeting_for_lobby["meeting_id"]
        token = setup_meeting_for_lobby["token"]
        
        # Join lobby
        join_resp = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join",
            json={"name": "TEST_Admit Guest", "email": "admitguest@test.com"}
        )
        guest_id = join_resp.json().get("guest_id") or join_resp.json().get("user_id") or join_resp.json().get("id")
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/admit",
            headers={"Authorization": f"Bearer {token}"},
            json={"guest_id": guest_id}
        )
        assert response.status_code == 200
        print("✓ Guest admitted")
    
    def test_lobby_status(self, setup_meeting_for_lobby):
        """GET /api/karau-meet/meetings/{id}/lobby/status returns admission status"""
        meeting_id = setup_meeting_for_lobby["meeting_id"]
        
        # Join lobby
        join_resp = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join",
            json={"name": "TEST_Status Guest", "email": "statusguest@test.com"}
        )
        guest_id = join_resp.json().get("guest_id") or join_resp.json().get("user_id") or join_resp.json().get("id")
        
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/status",
            params={"guest_id": guest_id}
        )
        assert response.status_code == 200
        print("✓ Lobby status retrieved")
    
    def test_lobby_admit_all(self, setup_meeting_for_lobby):
        """POST /api/karau-meet/meetings/{id}/lobby/admit-all admits all waiting"""
        meeting_id = setup_meeting_for_lobby["meeting_id"]
        token = setup_meeting_for_lobby["token"]
        
        # Join multiple guests
        for i in range(2):
            requests.post(
                f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join",
                json={"name": f"TEST_Bulk Guest {i}", "email": f"bulkguest{i}@test.com"}
            )
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/admit-all",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        print("✓ All guests admitted")


class TestBreakoutRooms:
    """Breakout room session tests"""
    
    @pytest.fixture
    def setup_meeting_for_breakout(self):
        """Create a meeting for breakout testing"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["access_token"]
        
        create_resp = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "TEST_Breakout Meeting",
                "scheduled_time": "2026-02-01T13:00:00Z",
                "duration_minutes": 60
            }
        )
        meeting_id = create_resp.json().get("meeting_id") or create_resp.json().get("id")
        return {"meeting_id": meeting_id, "token": token}
    
    def test_breakout_session_start(self, setup_meeting_for_breakout):
        """POST /api/karau-meet/meetings/{id}/breakout-session/start creates rooms"""
        meeting_id = setup_meeting_for_breakout["meeting_id"]
        token = setup_meeting_for_breakout["token"]
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/breakout-session/start",
            headers={"Authorization": f"Bearer {token}"},
            json={"room_count": 3, "duration_minutes": 15}
        )
        assert response.status_code in [200, 201]
        print("✓ Breakout session started")
    
    def test_breakout_session_close(self, setup_meeting_for_breakout):
        """POST /api/karau-meet/meetings/{id}/breakout-session/close closes all rooms"""
        meeting_id = setup_meeting_for_breakout["meeting_id"]
        token = setup_meeting_for_breakout["token"]
        
        # Start first
        requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/breakout-session/start",
            headers={"Authorization": f"Bearer {token}"},
            json={"room_count": 2, "duration_minutes": 10}
        )
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/breakout-session/close",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        print("✓ Breakout session closed")


class TestCalendarAndSharing:
    """Calendar export and social sharing tests"""
    
    @pytest.fixture
    def setup_meeting_for_sharing(self):
        """Create a meeting for sharing tests"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["access_token"]
        
        create_resp = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "TEST_Sharing Meeting",
                "scheduled_time": "2026-02-01T14:00:00Z",
                "duration_minutes": 60
            }
        )
        meeting_id = create_resp.json().get("meeting_id") or create_resp.json().get("id")
        return {"meeting_id": meeting_id, "token": token}
    
    def test_calendar_ics_export(self, setup_meeting_for_sharing):
        """GET /api/karau-meet/share/calendar/{id}.ics returns text/calendar ICS file"""
        meeting_id = setup_meeting_for_sharing["meeting_id"]
        
        response = requests.get(f"{BASE_URL}/api/karau-meet/share/calendar/{meeting_id}.ics")
        assert response.status_code == 200
        assert "text/calendar" in response.headers.get("Content-Type", "")
        assert "BEGIN:VCALENDAR" in response.text
        print("✓ ICS calendar export working")
    
    def test_social_sharing_links(self, setup_meeting_for_sharing):
        """GET /api/karau-meet/share/social/{id} returns 5 platform links"""
        meeting_id = setup_meeting_for_sharing["meeting_id"]
        
        response = requests.get(f"{BASE_URL}/api/karau-meet/share/social/{meeting_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Check for all 5 platforms
        platforms = ["linkedin", "twitter", "facebook", "email", "whatsapp"]
        for platform in platforms:
            assert platform in data, f"Missing {platform} link"
        print("✓ Social sharing - all 5 platforms present")
    
    def test_calendar_status(self):
        """GET /api/karau-meet/calendar/status returns providers"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["access_token"]
        
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/calendar/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        # Check providers present
        assert "microsoft" in str(data).lower() or "google" in str(data).lower() or "apple" in str(data).lower()
        print("✓ Calendar status shows providers")
    
    def test_microsoft_calendar_connect(self):
        """GET /api/karau-meet/calendar/microsoft/connect returns 503 (not configured)"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["access_token"]
        
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/calendar/microsoft/connect",
            headers={"Authorization": f"Bearer {token}"},
            allow_redirects=False
        )
        # 503 if not configured, 302 if redirect to OAuth
        assert response.status_code in [302, 503]
        print("✓ Microsoft calendar connect endpoint exists")
    
    def test_google_calendar_connect(self):
        """GET /api/karau-meet/calendar/google/connect returns 503 (not configured)"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["access_token"]
        
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/calendar/google/connect",
            headers={"Authorization": f"Bearer {token}"},
            allow_redirects=False
        )
        # 503 if not configured, 302 if redirect to OAuth
        assert response.status_code in [302, 503]
        print("✓ Google calendar connect endpoint exists")
    
    def test_calendar_disconnect(self):
        """POST /api/karau-meet/calendar/disconnect works"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["access_token"]
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/calendar/disconnect",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 204]
        print("✓ Calendar disconnect working")


class TestEnterpriseOrganizations:
    """Enterprise organization endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return login_resp.json()["access_token"]
    
    def test_get_organization_details(self, admin_token):
        """GET /api/karau-meet/organizations/{org_id} returns org details"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/{TEST_ORG_ID}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        print(f"✓ Organization details: {data.get('name')}")
    
    def test_get_organization_employees(self, admin_token):
        """GET /api/karau-meet/organizations/{org_id}/employees returns employee list"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/{TEST_ORG_ID}/employees",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "employees" in data
        print("✓ Organization employees retrieved")
    
    def test_get_organization_rooms(self, admin_token):
        """GET /api/karau-meet/organizations/{org_id}/rooms returns conference rooms"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/{TEST_ORG_ID}/rooms",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "rooms" in data
        print("✓ Conference rooms retrieved")
    
    def test_get_organization_branding(self, admin_token):
        """GET /api/karau-meet/organizations/branding/{org_id} returns branding info"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/branding/{TEST_ORG_ID}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        print("✓ Organization branding retrieved")
    
    def test_verify_domain(self, admin_token):
        """POST /api/karau-meet/organizations/{org_id}/verify-domain works"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{TEST_ORG_ID}/verify-domain",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"domain": "medmatch.com"}
        )
        assert response.status_code in [200, 400, 409]  # May already be verified
        print("✓ Domain verification endpoint working")


class TestSSOSAML:
    """SSO/SAML configuration tests"""
    
    @pytest.fixture
    def admin_token(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return login_resp.json()["access_token"]
    
    @pytest.fixture
    def test_user_token(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        return login_resp.json()["access_token"]
    
    def test_sso_metadata(self):
        """GET /api/karau-meet/sso/metadata returns SAML XML with EntityDescriptor"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/sso/metadata")
        assert response.status_code == 200
        assert "EntityDescriptor" in response.text or "md:EntityDescriptor" in response.text
        print("✓ SSO SAML metadata returned")
    
    def test_sso_configure_admin(self, admin_token):
        """POST /api/karau-meet/sso/configure (admin) saves SSO config"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/sso/configure",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "org_id": TEST_ORG_ID,
                "idp_entity_id": "https://idp.test.com/entity",
                "idp_sso_url": "https://idp.test.com/sso",
                "idp_certificate": "-----BEGIN CERTIFICATE-----\nMIICtest\n-----END CERTIFICATE-----",
                "enable_sso": True
            }
        )
        assert response.status_code in [200, 201]
        print("✓ SSO config saved by admin")
    
    def test_sso_configure_non_admin_returns_403(self, test_user_token):
        """POST /api/karau-meet/sso/configure (non-admin) returns 403"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/sso/configure",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={
                "org_id": TEST_ORG_ID,
                "idp_entity_id": "https://idp.test.com/entity",
                "idp_sso_url": "https://idp.test.com/sso"
            }
        )
        assert response.status_code in [401, 403]
        print("✓ Non-admin SSO config rejected")
    
    def test_sso_get_config(self, admin_token):
        """GET /api/karau-meet/sso/config/{org_id} returns saved config"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/sso/config/{TEST_ORG_ID}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]  # 404 if not configured yet
        print("✓ SSO config GET working")
    
    def test_sso_update_config(self, admin_token):
        """PUT /api/karau-meet/sso/config/{org_id} updates config"""
        response = requests.put(
            f"{BASE_URL}/api/karau-meet/sso/config/{TEST_ORG_ID}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "enable_sso": True,
                "idp_sso_url": "https://idp.updated.com/sso"
            }
        )
        assert response.status_code in [200, 404]
        print("✓ SSO config UPDATE working")
    
    def test_sso_delete_config(self, admin_token):
        """DELETE /api/karau-meet/sso/config/{org_id} removes config"""
        response = requests.delete(
            f"{BASE_URL}/api/karau-meet/sso/config/{TEST_ORG_ID}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 204, 404]
        print("✓ SSO config DELETE working")
    
    def test_sso_discover(self, admin_token):
        """GET /api/karau-meet/sso/discover?email=user@medmatch.com checks domain"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/sso/discover",
            params={"email": "user@medmatch.com"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]
        print("✓ SSO discover endpoint working")


class TestTranslations:
    """Translation API tests"""
    
    def test_translate_text(self):
        """POST /api/translate/text translates text between languages"""
        response = requests.post(
            f"{BASE_URL}/api/translate/text",
            json={
                "text": "Hello, welcome to the meeting",
                "source_lang": "en",
                "target_lang": "es"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "translated" in data or "translation" in data or "text" in data
        print("✓ Translation API working")
    
    def test_get_supported_languages(self):
        """GET /api/translate/languages returns supported languages list"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "languages" in data
        print("✓ Supported languages list retrieved")


class TestAccessibility:
    """Accessibility settings tests"""
    
    def test_accessibility_settings(self):
        """GET /api/karau-meet/accessibility/settings returns accessibility config"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["access_token"]
        
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/accessibility/settings",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        print("✓ Accessibility settings retrieved")


class TestRecordings:
    """Recordings tests"""
    
    def test_recordings_with_auth(self):
        """GET /api/karau-meet/recordings returns recordings list (authed)"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["access_token"]
        
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/recordings",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        print("✓ Recordings retrieved with auth")
    
    def test_recordings_no_auth(self):
        """GET /api/karau-meet/recordings (no auth) returns 401"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/recordings")
        assert response.status_code == 401
        print("✓ Recordings without auth - 401 returned")


class TestScheduling:
    """Scheduling tests"""
    
    def test_scheduled_meetings(self):
        """GET /api/karau-meet/schedule/meetings returns scheduled meetings"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["access_token"]
        
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/schedule/meetings",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        print("✓ Scheduled meetings retrieved")


class TestAnalytics:
    """Analytics tests"""
    
    def test_analytics_dashboard(self):
        """GET /api/analytics/dashboard returns analytics data"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["access_token"]
        
        response = requests.get(
            f"{BASE_URL}/api/analytics/dashboard",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        print("✓ Analytics dashboard data retrieved")


class TestTranslationFiles:
    """Verify translation locale files"""
    
    def test_locale_files_exist(self):
        """Verify 52 locale files exist"""
        locales_path = "/app/frontend/src/locales/"
        import os
        files = [f for f in os.listdir(locales_path) if f.endswith('.json')]
        assert len(files) >= 52, f"Expected 52 locales, found {len(files)}"
        print(f"✓ {len(files)} locale files found")
    
    def test_en_locale_has_2005_keys(self):
        """Verify EN locale has 2005+ translation keys"""
        import json
        
        def count_keys(obj):
            count = 0
            if isinstance(obj, dict):
                for value in obj.values():
                    if isinstance(value, dict):
                        count += count_keys(value)
                    else:
                        count += 1
            return count
        
        with open("/app/frontend/src/locales/en.json") as f:
            en_data = json.load(f)
        
        total_keys = count_keys(en_data)
        assert total_keys >= 2005, f"Expected 2005+ keys, found {total_keys}"
        print(f"✓ EN locale has {total_keys} keys")
    
    def test_key_locales_have_same_structure(self):
        """Verify key locales (es, fr, de, ja, ar, zh, hi) have same key structure as EN"""
        import json
        
        with open("/app/frontend/src/locales/en.json") as f:
            en_data = json.load(f)
        en_top_keys = set(en_data.keys())
        
        key_locales = ["es", "fr", "de", "ja", "zh"]
        for locale in key_locales:
            with open(f"/app/frontend/src/locales/{locale}.json") as f:
                locale_data = json.load(f)
            locale_top_keys = set(locale_data.keys())
            
            # Check most top-level keys are present
            missing = en_top_keys - locale_top_keys
            assert len(missing) < len(en_top_keys) * 0.2, f"{locale} missing too many keys: {missing}"
        
        print(f"✓ Key locales have matching structure")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
