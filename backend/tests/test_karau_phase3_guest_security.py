"""
Test Suite: KARAU Phase 3 - Guest Security (2FA OTP, Age Declaration) & Sharing Features
Features:
  - Guest 2FA Flow: register -> verify-otp -> age-declaration
  - Calendar ICS Export
  - Social Media Sharing Links (LinkedIn, Twitter, Facebook, WhatsApp, Email)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestGuestRegistration:
    """Guest 2FA Step 1: Register and send OTP"""

    def test_guest_register_success(self):
        """POST /api/karau-meet/guest/register returns success and _dev_otp"""
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(f"{BASE_URL}/api/karau-meet/guest/register", json={
            "email": email,
            "name": "Test Guest",
            "meeting_id": "TEST123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["email"] == email.lower()
        assert "_dev_otp" in data
        assert len(data["_dev_otp"]) == 6
        assert "expires_in_minutes" in data

    def test_guest_register_invalid_email(self):
        """POST /api/karau-meet/guest/register with invalid email returns 400"""
        response = requests.post(f"{BASE_URL}/api/karau-meet/guest/register", json={
            "email": "invalid-email",
            "name": "Test Guest",
            "meeting_id": "TEST123"
        })
        assert response.status_code == 400

    def test_guest_register_missing_name(self):
        """POST /api/karau-meet/guest/register with empty name returns 400"""
        response = requests.post(f"{BASE_URL}/api/karau-meet/guest/register", json={
            "email": "test@example.com",
            "name": "",
            "meeting_id": "TEST123"
        })
        assert response.status_code == 400


class TestOTPVerification:
    """Guest 2FA Step 2: Verify OTP"""

    def test_verify_otp_success(self):
        """Full OTP verification flow - register then verify"""
        email = f"otp_test_{uuid.uuid4().hex[:8]}@example.com"
        
        # Step 1: Register
        register_resp = requests.post(f"{BASE_URL}/api/karau-meet/guest/register", json={
            "email": email,
            "name": "OTP Test",
            "meeting_id": "OTP_TEST"
        })
        assert register_resp.status_code == 200
        otp = register_resp.json()["_dev_otp"]
        
        # Step 2: Verify OTP
        verify_resp = requests.post(f"{BASE_URL}/api/karau-meet/guest/verify-otp", json={
            "email": email,
            "otp": otp,
            "meeting_id": "OTP_TEST"
        })
        assert verify_resp.status_code == 200
        data = verify_resp.json()
        assert data["success"] is True
        assert data["verified"] is True
        assert data["next_step"] == "age_declaration"

    def test_verify_otp_invalid_code(self):
        """POST /api/karau-meet/guest/verify-otp with wrong code returns 400"""
        email = f"invalid_otp_{uuid.uuid4().hex[:8]}@example.com"
        
        # Register first
        requests.post(f"{BASE_URL}/api/karau-meet/guest/register", json={
            "email": email,
            "name": "Test",
            "meeting_id": "TEST123"
        })
        
        # Try invalid OTP
        response = requests.post(f"{BASE_URL}/api/karau-meet/guest/verify-otp", json={
            "email": email,
            "otp": "000000",
            "meeting_id": "TEST123"
        })
        assert response.status_code == 400

    def test_verify_otp_no_pending_verification(self):
        """POST /api/karau-meet/guest/verify-otp without registration returns 400"""
        response = requests.post(f"{BASE_URL}/api/karau-meet/guest/verify-otp", json={
            "email": "nonexistent@example.com",
            "otp": "123456",
            "meeting_id": "TEST123"
        })
        assert response.status_code == 400


class TestAgeDeclaration:
    """Guest 2FA Step 3: Age Declaration"""

    def test_age_declaration_success(self):
        """Full flow: register -> verify -> age declaration"""
        email = f"age_test_{uuid.uuid4().hex[:8]}@example.com"
        name = "Age Test User"
        meeting_id = "AGE_TEST"
        
        # Step 1: Register
        reg_resp = requests.post(f"{BASE_URL}/api/karau-meet/guest/register", json={
            "email": email, "name": name, "meeting_id": meeting_id
        })
        otp = reg_resp.json()["_dev_otp"]
        
        # Step 2: Verify
        requests.post(f"{BASE_URL}/api/karau-meet/guest/verify-otp", json={
            "email": email, "otp": otp, "meeting_id": meeting_id
        })
        
        # Step 3: Age Declaration
        age_resp = requests.post(f"{BASE_URL}/api/karau-meet/guest/age-declaration", json={
            "email": email,
            "meeting_id": meeting_id,
            "confirmed_age_16_plus": True
        })
        assert age_resp.status_code == 200
        data = age_resp.json()
        assert data["success"] is True
        assert data["verified"] is True
        assert data["age_declared"] is True
        assert "guest_id" in data
        assert "user" in data
        assert data["user"]["is_guest"] is True
        assert data["user"]["is_verified"] is True

    def test_age_declaration_without_verification(self):
        """POST /api/karau-meet/guest/age-declaration without OTP verification returns 400"""
        response = requests.post(f"{BASE_URL}/api/karau-meet/guest/age-declaration", json={
            "email": "unverified@example.com",
            "meeting_id": "TEST123",
            "confirmed_age_16_plus": True
        })
        assert response.status_code == 400

    def test_age_declaration_under_16(self):
        """POST /api/karau-meet/guest/age-declaration with confirmed_age_16_plus=false returns 403"""
        email = f"under16_{uuid.uuid4().hex[:8]}@example.com"
        meeting_id = "UNDER16"
        
        # Register and verify
        reg_resp = requests.post(f"{BASE_URL}/api/karau-meet/guest/register", json={
            "email": email, "name": "Test", "meeting_id": meeting_id
        })
        otp = reg_resp.json()["_dev_otp"]
        requests.post(f"{BASE_URL}/api/karau-meet/guest/verify-otp", json={
            "email": email, "otp": otp, "meeting_id": meeting_id
        })
        
        # Try age declaration with false
        response = requests.post(f"{BASE_URL}/api/karau-meet/guest/age-declaration", json={
            "email": email,
            "meeting_id": meeting_id,
            "confirmed_age_16_plus": False
        })
        assert response.status_code == 403


class TestResendOTP:
    """Resend OTP functionality"""

    def test_resend_otp_success(self):
        """POST /api/karau-meet/guest/resend-otp generates new code"""
        email = f"resend_{uuid.uuid4().hex[:8]}@example.com"
        
        # First registration
        reg1 = requests.post(f"{BASE_URL}/api/karau-meet/guest/register", json={
            "email": email, "name": "Test", "meeting_id": "RESEND"
        })
        otp1 = reg1.json()["_dev_otp"]
        
        # Resend
        resend = requests.post(f"{BASE_URL}/api/karau-meet/guest/resend-otp", json={
            "email": email, "name": "Test", "meeting_id": "RESEND"
        })
        assert resend.status_code == 200
        data = resend.json()
        assert data["success"] is True
        assert "_dev_otp" in data
        # OTP may be different (random)


class TestGuestStatus:
    """Guest verification status check"""

    @pytest.fixture
    def verified_guest(self):
        """Create a fully verified guest"""
        email = f"status_{uuid.uuid4().hex[:8]}@example.com"
        meeting_id = "STATUS_TEST"
        
        # Full verification flow
        reg = requests.post(f"{BASE_URL}/api/karau-meet/guest/register", json={
            "email": email, "name": "Status Test", "meeting_id": meeting_id
        })
        otp = reg.json()["_dev_otp"]
        requests.post(f"{BASE_URL}/api/karau-meet/guest/verify-otp", json={
            "email": email, "otp": otp, "meeting_id": meeting_id
        })
        requests.post(f"{BASE_URL}/api/karau-meet/guest/age-declaration", json={
            "email": email, "meeting_id": meeting_id, "confirmed_age_16_plus": True
        })
        return email, meeting_id

    def test_guest_status_verified(self, verified_guest):
        """GET /api/karau-meet/guest/status returns verified=true for verified guest"""
        email, meeting_id = verified_guest
        response = requests.get(f"{BASE_URL}/api/karau-meet/guest/status", params={
            "email": email, "meeting_id": meeting_id
        })
        assert response.status_code == 200
        data = response.json()
        assert data["verified"] is True
        assert "guest_id" in data
        assert "user" in data

    def test_guest_status_not_verified(self):
        """GET /api/karau-meet/guest/status returns verified=false for unverified email"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/guest/status", params={
            "email": "never_registered@example.com", "meeting_id": "NONE"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["verified"] is False


class TestCalendarICSExport:
    """Calendar .ics file export"""

    @pytest.fixture
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Auth failed")

    @pytest.fixture
    def test_meeting(self, auth_token):
        """Create a test meeting"""
        response = requests.post(f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "ICS Test Meeting"}
        )
        if response.status_code == 200:
            return response.json()["meeting_id"]
        pytest.skip("Meeting creation failed")

    def test_ics_export_success(self, test_meeting):
        """GET /api/karau-meet/share/calendar/{meetingId}.ics returns text/calendar"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/share/calendar/{test_meeting}.ics")
        assert response.status_code == 200
        assert "text/calendar" in response.headers.get("Content-Type", "")
        content = response.text
        assert "BEGIN:VCALENDAR" in content
        assert "BEGIN:VEVENT" in content
        assert "SUMMARY:" in content
        assert f"UID:{test_meeting}" in content

    def test_ics_export_404_invalid_meeting(self):
        """GET /api/karau-meet/share/calendar/INVALID.ics returns 404"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/share/calendar/INVALID_MEETING_ID.ics")
        assert response.status_code == 404


class TestSocialSharingLinks:
    """Social media share link generation"""

    @pytest.fixture
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Auth failed")

    @pytest.fixture
    def test_meeting(self, auth_token):
        """Create a test meeting"""
        response = requests.post(f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "Share Test Meeting"}
        )
        if response.status_code == 200:
            return response.json()["meeting_id"]
        pytest.skip("Meeting creation failed")

    def test_social_links_success(self, test_meeting):
        """GET /api/karau-meet/share/social/{meetingId} returns all platform links"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/share/social/{test_meeting}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["meeting_id"] == test_meeting
        assert "share_links" in data
        links = data["share_links"]
        
        # All platforms present
        assert "linkedin" in links
        assert "twitter" in links
        assert "facebook" in links
        assert "whatsapp" in links
        assert "email" in links
        
        # Links are valid URLs
        assert "linkedin.com" in links["linkedin"]
        assert "twitter.com" in links["twitter"]
        assert "facebook.com" in links["facebook"]
        assert "wa.me" in links["whatsapp"]
        assert "mailto:" in links["email"]

    def test_social_links_404_invalid_meeting(self):
        """GET /api/karau-meet/share/social/INVALID returns 404"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/share/social/INVALID_MEETING")
        assert response.status_code == 404


class TestE2EGuestJoinFlow:
    """End-to-end guest join workflow"""

    @pytest.fixture
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Auth failed")

    @pytest.fixture
    def real_meeting(self, auth_token):
        """Create a real meeting for E2E test"""
        response = requests.post(f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "E2E Guest Test Meeting"}
        )
        if response.status_code == 200:
            return response.json()["meeting_id"]
        pytest.skip("Meeting creation failed")

    def test_e2e_guest_verification_flow(self, real_meeting):
        """Complete guest verification from register to status check"""
        email = f"e2e_guest_{uuid.uuid4().hex[:8]}@example.com"
        name = "E2E Test Guest"
        
        # 1. Register
        reg = requests.post(f"{BASE_URL}/api/karau-meet/guest/register", json={
            "email": email, "name": name, "meeting_id": real_meeting
        })
        assert reg.status_code == 200
        otp = reg.json()["_dev_otp"]
        
        # 2. Verify OTP
        verify = requests.post(f"{BASE_URL}/api/karau-meet/guest/verify-otp", json={
            "email": email, "otp": otp, "meeting_id": real_meeting
        })
        assert verify.status_code == 200
        
        # 3. Age Declaration
        age = requests.post(f"{BASE_URL}/api/karau-meet/guest/age-declaration", json={
            "email": email, "meeting_id": real_meeting, "confirmed_age_16_plus": True
        })
        assert age.status_code == 200
        guest_id = age.json()["guest_id"]
        
        # 4. Status Check
        status = requests.get(f"{BASE_URL}/api/karau-meet/guest/status", params={
            "email": email, "meeting_id": real_meeting
        })
        assert status.status_code == 200
        data = status.json()
        assert data["verified"] is True
        assert data["guest_id"] == guest_id
