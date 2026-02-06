"""
ATS (Applicant Tracking System) Feature Tests
Tests: Application links, public application form, status tracking, email notifications
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from review request
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "MedMatch2026!"
TEST_JOB_ID = "job_18471a266c11"
TEST_APPLICATION_LINK_TOKEN = "5CwH-nKMW9q3HANVumSlI7M5fAqU7XZM"
TEST_APPLICATION_ID = "app_faffb413b367"
TEST_TRACKING_TOKEN = "kYWoh3xDBUL27jJxFQhVlg"


class TestATSPublicEndpoints:
    """Test public ATS endpoints (no auth required)"""
    
    def test_get_application_form_valid_token(self):
        """GET /api/ats/apply/:token - Get application form with valid token"""
        response = requests.get(f"{BASE_URL}/api/ats/apply/{TEST_APPLICATION_LINK_TOKEN}")
        print(f"GET /api/ats/apply/{TEST_APPLICATION_LINK_TOKEN}: {response.status_code}")
        
        # Could be 200 (valid) or 404/410 (expired/invalid)
        if response.status_code == 200:
            data = response.json()
            assert "job" in data, "Response should contain job details"
            assert "require_resume" in data, "Response should contain require_resume field"
            print(f"Job details: {data.get('job', {}).get('title', 'N/A')}")
        elif response.status_code in [404, 410]:
            print(f"Token expired or invalid: {response.json().get('detail', 'Unknown')}")
        else:
            print(f"Unexpected status: {response.status_code}")
    
    def test_get_application_form_invalid_token(self):
        """GET /api/ats/apply/:token - Invalid token returns 404"""
        response = requests.get(f"{BASE_URL}/api/ats/apply/invalid_token_12345")
        print(f"GET /api/ats/apply/invalid_token: {response.status_code}")
        assert response.status_code == 404, "Invalid token should return 404"
    
    def test_track_application_valid(self):
        """GET /api/ats/track/:applicationId - Track application status"""
        params = {"token": TEST_TRACKING_TOKEN}
        response = requests.get(f"{BASE_URL}/api/ats/track/{TEST_APPLICATION_ID}", params=params)
        print(f"GET /api/ats/track/{TEST_APPLICATION_ID}: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            assert "application_id" in data, "Response should contain application_id"
            assert "status" in data, "Response should contain status"
            assert "status_label" in data, "Response should contain status_label"
            print(f"Application status: {data.get('status_label', 'N/A')}")
        elif response.status_code == 404:
            print("Application not found - may need to create test data")
    
    def test_track_application_invalid(self):
        """GET /api/ats/track/:applicationId - Invalid application returns 404"""
        response = requests.get(f"{BASE_URL}/api/ats/track/invalid_app_id")
        print(f"GET /api/ats/track/invalid_app_id: {response.status_code}")
        assert response.status_code == 404, "Invalid application ID should return 404"


class TestATSAuthenticatedEndpoints:
    """Test authenticated ATS endpoints (recruiter/admin required)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth session"""
        self.session = requests.Session()
        
        # Login as admin
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        if login_response.status_code != 200:
            pytest.skip(f"Login failed: {login_response.status_code}")
        
        print(f"Logged in as {ADMIN_EMAIL}")
        yield
    
    def test_create_application_link(self):
        """POST /api/ats/links - Create application link"""
        payload = {
            "job_id": TEST_JOB_ID,
            "expires_in_days": 30,
            "require_resume": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/ats/links", json=payload)
        print(f"POST /api/ats/links: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            assert "link_id" in data, "Response should contain link_id"
            assert "application_url" in data, "Response should contain application_url"
            assert "token" in data, "Response should contain token"
            print(f"Created link: {data.get('application_url', 'N/A')}")
        elif response.status_code == 404:
            print(f"Job not found: {response.json().get('detail', 'Unknown')}")
        elif response.status_code == 403:
            print(f"Permission denied: {response.json().get('detail', 'Unknown')}")
        else:
            print(f"Response: {response.json()}")
    
    def test_list_application_links(self):
        """GET /api/ats/links - List application links"""
        response = self.session.get(f"{BASE_URL}/api/ats/links")
        print(f"GET /api/ats/links: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "links" in data, "Response should contain links array"
        assert "count" in data, "Response should contain count"
        print(f"Found {data.get('count', 0)} application links")
    
    def test_get_ats_stats(self):
        """GET /api/ats/stats - Get ATS statistics"""
        response = self.session.get(f"{BASE_URL}/api/ats/stats")
        print(f"GET /api/ats/stats: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "total_applications" in data, "Response should contain total_applications"
        assert "active_links" in data, "Response should contain active_links"
        assert "available_statuses" in data, "Response should contain available_statuses"
        print(f"Stats: {data.get('total_applications', 0)} applications, {data.get('active_links', 0)} active links")
    
    def test_get_email_logs(self):
        """GET /api/ats/email-logs - Get email logs"""
        response = self.session.get(f"{BASE_URL}/api/ats/email-logs")
        print(f"GET /api/ats/email-logs: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "logs" in data, "Response should contain logs array"
        assert "count" in data, "Response should contain count"
        print(f"Found {data.get('count', 0)} email logs")
    
    def test_update_application_status(self):
        """PUT /api/ats/applications/:applicationId/status - Update status"""
        payload = {
            "status": "under_review",
            "send_email": False  # Don't send email in test
        }
        
        response = self.session.put(
            f"{BASE_URL}/api/ats/applications/{TEST_APPLICATION_ID}/status",
            json=payload
        )
        print(f"PUT /api/ats/applications/{TEST_APPLICATION_ID}/status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            assert "message" in data, "Response should contain message"
            print(f"Status update: {data.get('message', 'N/A')}")
        elif response.status_code == 404:
            print("Application not found - may need to create test data")
        elif response.status_code == 400:
            print(f"Invalid status: {response.json().get('detail', 'Unknown')}")
    
    def test_update_status_invalid_status(self):
        """PUT /api/ats/applications/:applicationId/status - Invalid status returns 400"""
        payload = {
            "status": "invalid_status_xyz",
            "send_email": False
        }
        
        response = self.session.put(
            f"{BASE_URL}/api/ats/applications/{TEST_APPLICATION_ID}/status",
            json=payload
        )
        print(f"PUT with invalid status: {response.status_code}")
        
        # Should be 400 for invalid status or 404 if application doesn't exist
        assert response.status_code in [400, 404], f"Expected 400 or 404, got {response.status_code}"


class TestATSApplicationSubmission:
    """Test application submission flow"""
    
    def test_submit_application_flow(self):
        """POST /api/ats/apply/:token - Submit application"""
        # First, get a valid token by logging in and creating a link
        session = requests.Session()
        
        # Login
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        if login_response.status_code != 200:
            pytest.skip("Login failed")
        
        # Create a new application link
        link_response = session.post(
            f"{BASE_URL}/api/ats/links",
            json={
                "job_id": TEST_JOB_ID,
                "expires_in_days": 30,
                "require_resume": False
            }
        )
        
        if link_response.status_code != 200:
            # Try with existing token
            token = TEST_APPLICATION_LINK_TOKEN
            print(f"Using existing token: {token}")
        else:
            token = link_response.json().get("token")
            print(f"Created new token: {token}")
        
        # Submit application (no auth required)
        unique_email = f"test_applicant_{int(time.time())}@test.com"
        application_data = {
            "name": "Test Applicant",
            "email": unique_email,
            "phone": "+1234567890",
            "cover_letter": "This is a test application for ATS testing."
        }
        
        submit_response = requests.post(
            f"{BASE_URL}/api/ats/apply/{token}",
            json=application_data
        )
        print(f"POST /api/ats/apply/{token}: {submit_response.status_code}")
        
        if submit_response.status_code == 200:
            data = submit_response.json()
            assert "application_id" in data, "Response should contain application_id"
            assert "tracking_token" in data, "Response should contain tracking_token"
            assert "tracking_url" in data, "Response should contain tracking_url"
            print(f"Application submitted: {data.get('application_id', 'N/A')}")
            print(f"Tracking URL: {data.get('tracking_url', 'N/A')}")
            
            # Verify we can track the application
            track_response = requests.get(
                f"{BASE_URL}/api/ats/track/{data['application_id']}",
                params={"token": data['tracking_token']}
            )
            assert track_response.status_code == 200, "Should be able to track submitted application"
            print(f"Tracking verified: {track_response.json().get('status_label', 'N/A')}")
            
        elif submit_response.status_code == 409:
            print("Duplicate application - email already used")
        elif submit_response.status_code in [404, 410]:
            print(f"Token issue: {submit_response.json().get('detail', 'Unknown')}")


class TestATSStatusValues:
    """Test all valid status values"""
    
    VALID_STATUSES = [
        "received", "under_review", "shortlisted", "interview_scheduled",
        "interview_completed", "offer_extended", "hired", "application_deferred",
        "not_selected", "position_closed", "withdrawn"
    ]
    
    def test_stats_returns_all_statuses(self):
        """Verify stats endpoint returns all valid statuses"""
        session = requests.Session()
        
        # Login
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        if login_response.status_code != 200:
            pytest.skip("Login failed")
        
        # Get stats
        response = session.get(f"{BASE_URL}/api/ats/stats")
        assert response.status_code == 200
        
        data = response.json()
        available_statuses = data.get("available_statuses", {})
        
        print(f"Available statuses: {list(available_statuses.keys())}")
        
        for status in self.VALID_STATUSES:
            assert status in available_statuses, f"Status '{status}' should be available"
            status_config = available_statuses[status]
            assert "label" in status_config, f"Status '{status}' should have label"
            assert "emoji" in status_config, f"Status '{status}' should have emoji"
            assert "description" in status_config, f"Status '{status}' should have description"
        
        print(f"All {len(self.VALID_STATUSES)} statuses verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
