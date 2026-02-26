"""
P1 Integration Tests for MedMatch-AI KARAU
Tests: ORCID OAuth, LinkedIn Profile Sync, PayPal Payments, AI KARAU Meeting Portal
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_PAYPAL_EMAIL = "test_paypal@medmatch.com"
TEST_PAYPAL_PASSWORD = "TestPass123!"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Admin authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def trial_user_token(api_client):
    """Get trial user authentication token (for PayPal tests)"""
    # First try to create the test user if it doesn't exist
    register_response = api_client.post(f"{BASE_URL}/api/auth/register", json={
        "email": TEST_PAYPAL_EMAIL,
        "password": TEST_PAYPAL_PASSWORD,
        "name": "PayPal Test User",
        "role": "job_seeker"
    })
    
    # Now login
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_PAYPAL_EMAIL,
        "password": TEST_PAYPAL_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Trial user authentication failed - skipping PayPal tests")


class TestORCIDOAuth:
    """ORCID OAuth Integration Tests"""
    
    def test_orcid_config_returns_configured_true(self, api_client):
        """GET /api/auth/orcid/config returns configured: true"""
        response = api_client.get(f"{BASE_URL}/api/auth/orcid/config")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "configured" in data, "Response should have 'configured' field"
        assert data["configured"] == True, f"Expected configured: true, got {data['configured']}"
        print(f"PASS: ORCID config returns configured: {data['configured']}, environment: {data.get('environment')}")
    
    def test_orcid_login_redirects_to_orcid_org(self, api_client):
        """GET /api/auth/orcid/login returns 307 redirect to orcid.org"""
        # Don't follow redirects to check the redirect URL
        response = api_client.get(f"{BASE_URL}/api/auth/orcid/login", allow_redirects=False)
        
        # Should be a redirect (307 Temporary Redirect)
        assert response.status_code == 307, f"Expected 307 redirect, got {response.status_code}"
        
        # Check Location header points to orcid.org
        location = response.headers.get("Location", "")
        assert "orcid.org" in location, f"Redirect should be to orcid.org, got: {location}"
        
        # Verify correct client_id is in the URL
        assert "APP-K9HUYS6GQY2RERX6" in location, f"Redirect should contain ORCID client_id, got: {location}"
        
        print(f"PASS: ORCID login redirects to: {location[:100]}...")


class TestLinkedInSync:
    """LinkedIn Profile Sync Integration Tests"""
    
    def test_linkedin_status_returns_integration_configured(self, api_client, admin_token):
        """GET /api/linkedin/status with auth returns integration_configured: true"""
        response = api_client.get(
            f"{BASE_URL}/api/linkedin/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "integration_configured" in data, "Response should have 'integration_configured' field"
        assert data["integration_configured"] == True, f"Expected integration_configured: true, got {data['integration_configured']}"
        print(f"PASS: LinkedIn status returns integration_configured: {data['integration_configured']}")
    
    def test_linkedin_auth_url_returns_linkedin_url(self, api_client):
        """GET /api/linkedin/auth-url returns auth_url with linkedin.com"""
        redirect_uri = f"{BASE_URL}/settings?linkedin_callback=true"
        response = api_client.get(
            f"{BASE_URL}/api/linkedin/auth-url",
            params={"redirect_uri": redirect_uri}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "auth_url" in data, "Response should have 'auth_url' field"
        auth_url = data["auth_url"]
        assert "linkedin.com" in auth_url, f"auth_url should contain linkedin.com, got: {auth_url}"
        print(f"PASS: LinkedIn auth-url returns: {auth_url[:100]}...")


class TestPayPalPayments:
    """PayPal Payment Integration Tests"""
    
    def test_paypal_create_returns_payment_and_approval_url(self, api_client, trial_user_token):
        """POST /api/payments/paypal/create returns payment_id and approval_url"""
        response = api_client.post(
            f"{BASE_URL}/api/payments/paypal/create",
            headers={"Authorization": f"Bearer {trial_user_token}"},
            json={
                "success_url": f"{BASE_URL}/membership?success=true",
                "cancel_url": f"{BASE_URL}/membership?canceled=true",
                "plan": "lifetime"
            }
        )
        
        # PayPal create should return 200
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "payment_id" in data, "Response should have 'payment_id' field"
        assert "approval_url" in data, "Response should have 'approval_url' field"
        
        # Verify approval_url points to PayPal sandbox
        approval_url = data["approval_url"]
        assert "paypal.com" in approval_url, f"approval_url should contain paypal.com, got: {approval_url}"
        
        print(f"PASS: PayPal create returns payment_id: {data['payment_id'][:20]}..., approval_url points to PayPal")
    
    def test_paypal_execute_returns_error_for_missing_payer_id(self, api_client, trial_user_token):
        """POST /api/payments/paypal/execute returns error for missing payer_id (expected behavior)"""
        response = api_client.post(
            f"{BASE_URL}/api/payments/paypal/execute",
            headers={"Authorization": f"Bearer {trial_user_token}"},
            json={
                "payment_id": "FAKE-PAYMENT-ID"
            }
        )
        
        # Should return 400 for missing payer_id
        assert response.status_code == 400, f"Expected 400 for missing payer_id, got {response.status_code}"
        print("PASS: PayPal execute returns 400 for missing payer_id (expected)")


class TestMeetingPortal:
    """AI KARAU Meeting Portal Integration Tests"""
    
    def test_meetings_list_returns_meetings_for_authenticated_user(self, api_client, admin_token):
        """GET /api/karau-meet/meetings returns meeting list"""
        response = api_client.get(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "meetings" in data, "Response should have 'meetings' field"
        assert isinstance(data["meetings"], list), "meetings should be a list"
        print(f"PASS: Meeting list returns {len(data['meetings'])} meetings")
    
    def test_meetings_create_returns_meeting_id(self, api_client, admin_token):
        """POST /api/karau-meet/meetings creates a new meeting"""
        response = api_client.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "TEST_Integration Test Meeting"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "meeting_id" in data, "Response should have 'meeting_id' field"
        meeting_id = data["meeting_id"]
        assert len(meeting_id) > 0, "meeting_id should not be empty"
        print(f"PASS: Meeting created with ID: {meeting_id}")
        
        # Return meeting_id for cleanup
        return meeting_id
    
    def test_meeting_join_returns_ice_servers(self, api_client, admin_token):
        """POST /api/karau-meet/meetings/{id}/join returns ice_servers for WebRTC"""
        # First create a meeting
        create_response = api_client.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"title": "TEST_Join Test Meeting"}
        )
        assert create_response.status_code == 200, f"Failed to create meeting: {create_response.text}"
        meeting_id = create_response.json()["meeting_id"]
        
        # Now join the meeting
        join_response = api_client.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "video_enabled": True,
                "audio_enabled": True
            }
        )
        assert join_response.status_code == 200, f"Expected 200, got {join_response.status_code}: {join_response.text}"
        
        data = join_response.json()
        assert "ice_servers" in data, "Response should have 'ice_servers' for WebRTC"
        print(f"PASS: Meeting join returns ice_servers: {len(data['ice_servers'])} servers")


class TestHealthCheck:
    """Basic health check to ensure services are running"""
    
    def test_api_health(self, api_client):
        """Backend API responds"""
        response = api_client.get(f"{BASE_URL}/api")
        assert response.status_code == 200, f"API health check failed: {response.status_code}"
        print("PASS: Backend API is healthy")
    
    def test_admin_login(self, api_client):
        """Admin can log in"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.status_code}"
        data = response.json()
        assert "access_token" in data, "Login should return access_token"
        print(f"PASS: Admin login successful, token received")
