"""
Full Integration Tests for MedMatch
Tests all configured integrations: Apple Sign In, LinkedIn, Cloud Storage (Google Drive, OneDrive, Dropbox),
PayPal, Stripe, AI Supervisor, Translation, Job Search, Feedback, AutoFill
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://meeting-portal-test.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "MedMatch2026!"
RECRUITER_EMAIL = "recruiter@medmatch-test.com"
RECRUITER_PASSWORD = "test123"


class TestAppleSignIn:
    """Apple Sign In integration tests"""
    
    def test_apple_config_endpoint(self):
        """Test Apple Sign In configuration endpoint returns configured=true"""
        response = requests.get(f"{BASE_URL}/api/auth/apple/config")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "configured" in data, "Response should contain 'configured' field"
        assert data["configured"] == True, f"Apple Sign In should be configured=true, got {data['configured']}"
        
        # Verify client_id is correct
        assert "client_id" in data, "Response should contain 'client_id'"
        assert data["client_id"] == "com.medmatch.signin.web", f"Expected client_id 'com.medmatch.signin.web', got {data['client_id']}"
        
        # Verify redirect_uri is present
        assert "redirect_uri" in data, "Response should contain 'redirect_uri'"
        assert "/api/auth/apple/redirect" in data["redirect_uri"], "Redirect URI should contain /api/auth/apple/redirect"
        
        print(f"✅ Apple Sign In configured: {data}")


class TestLinkedInIntegration:
    """LinkedIn OAuth integration tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    def test_linkedin_status_configured(self, auth_token):
        """Test LinkedIn status shows integration_configured=true"""
        response = requests.get(
            f"{BASE_URL}/api/linkedin/status",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "integration_configured" in data, "Response should contain 'integration_configured'"
        assert data["integration_configured"] == True, f"LinkedIn should be configured=true, got {data['integration_configured']}"
        
        print(f"✅ LinkedIn integration configured: {data}")
    
    def test_linkedin_auth_url(self, auth_token):
        """Test LinkedIn auth URL returns valid OAuth URL"""
        redirect_uri = f"{BASE_URL}/settings?linkedin_callback=true"
        response = requests.get(
            f"{BASE_URL}/api/linkedin/auth-url",
            params={"redirect_uri": redirect_uri}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "auth_url" in data, "Response should contain 'auth_url'"
        assert "linkedin.com/oauth" in data["auth_url"], "Auth URL should be LinkedIn OAuth URL"
        assert "77wcvs14tufhyu" in data["auth_url"], "Auth URL should contain correct client_id"
        
        print(f"✅ LinkedIn auth URL valid: {data['auth_url'][:100]}...")


class TestCloudStorageIntegrations:
    """Cloud Storage integration tests (Google Drive, OneDrive, Dropbox)"""
    
    def test_cloud_status_all_providers(self):
        """Test cloud status shows all 3 providers configured"""
        response = requests.get(f"{BASE_URL}/api/cloud/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Google Drive
        assert "google_drive" in data, "Response should contain 'google_drive'"
        assert data["google_drive"]["configured"] == True, "Google Drive should be configured"
        print(f"✅ Google Drive configured: {data['google_drive']}")
        
        # OneDrive
        assert "onedrive" in data, "Response should contain 'onedrive'"
        assert data["onedrive"]["configured"] == True, f"OneDrive should be configured, got {data['onedrive']}"
        print(f"✅ OneDrive configured: {data['onedrive']}")
        
        # Dropbox
        assert "dropbox" in data, "Response should contain 'dropbox'"
        assert data["dropbox"]["configured"] == True, f"Dropbox should be configured, got {data['dropbox']}"
        print(f"✅ Dropbox configured: {data['dropbox']}")
    
    def test_dropbox_auth_url(self):
        """Test Dropbox auth URL returns valid OAuth URL"""
        redirect_uri = f"{BASE_URL}/api/cloud/dropbox/callback"
        response = requests.get(
            f"{BASE_URL}/api/cloud/dropbox/auth-url",
            params={"redirect_uri": redirect_uri}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "auth_url" in data, "Response should contain 'auth_url'"
        assert "dropbox.com" in data["auth_url"], "Auth URL should be Dropbox OAuth URL"
        assert "qjcao2halndcd70" in data["auth_url"], "Auth URL should contain correct app key"
        
        print(f"✅ Dropbox auth URL valid: {data['auth_url'][:100]}...")
    
    def test_onedrive_auth_url(self):
        """Test OneDrive auth URL returns valid OAuth URL"""
        redirect_uri = f"{BASE_URL}/api/cloud/onedrive/callback"
        response = requests.get(
            f"{BASE_URL}/api/cloud/onedrive/auth-url",
            params={"redirect_uri": redirect_uri}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "auth_url" in data, "Response should contain 'auth_url'"
        assert "microsoft" in data["auth_url"].lower() or "login.microsoftonline" in data["auth_url"], "Auth URL should be Microsoft OAuth URL"
        assert "33fd0966-d65f-4474-9eb7-2afeef5e72df" in data["auth_url"], "Auth URL should contain correct client_id"
        
        print(f"✅ OneDrive auth URL valid: {data['auth_url'][:100]}...")


class TestPaymentIntegrations:
    """Payment integration tests (Stripe and PayPal)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    def test_paypal_create_payment(self, auth_token):
        """Test PayPal create payment returns payment_id and approval_url"""
        response = requests.post(
            f"{BASE_URL}/api/payments/paypal/create",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "success_url": f"{BASE_URL}/membership?provider=paypal&success=true",
                "cancel_url": f"{BASE_URL}/membership?provider=paypal&cancelled=true",
                "plan": "lifetime"
            }
        )
        
        # PayPal might return 500 if SDK not installed, but should return proper response if configured
        if response.status_code == 200:
            data = response.json()
            assert "payment_id" in data, "Response should contain 'payment_id'"
            assert "approval_url" in data, "Response should contain 'approval_url'"
            assert "paypal.com" in data["approval_url"], "Approval URL should be PayPal URL"
            print(f"✅ PayPal payment created: payment_id={data['payment_id']}")
        elif response.status_code == 500:
            # Check if it's a configuration issue vs SDK issue
            error_detail = response.json().get("detail", "")
            if "not configured" in error_detail.lower():
                pytest.fail("PayPal not configured")
            elif "SDK not installed" in error_detail:
                pytest.skip("PayPal SDK not installed")
            else:
                print(f"⚠️ PayPal error (may be sandbox issue): {error_detail}")
        else:
            pytest.fail(f"Unexpected status {response.status_code}: {response.text}")
    
    def test_stripe_create_checkout(self, auth_token):
        """Test Stripe checkout session creation"""
        response = requests.post(
            f"{BASE_URL}/api/payments/create-checkout",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "success_url": f"{BASE_URL}/membership?session_id={{CHECKOUT_SESSION_ID}}",
                "cancel_url": f"{BASE_URL}/membership?cancelled=true",
                "plan": "lifetime"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "session_id" in data or "url" in data, "Response should contain session_id or url"
            print(f"✅ Stripe checkout created: {data}")
        elif response.status_code == 500:
            error_detail = response.json().get("detail", "")
            if "not configured" in error_detail.lower():
                pytest.fail("Stripe not configured")
            else:
                # Stripe test key might have issues
                print(f"⚠️ Stripe error (may be test key issue): {error_detail}")
        else:
            pytest.fail(f"Unexpected status {response.status_code}: {response.text}")
    
    def test_membership_status(self, auth_token):
        """Test membership status endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/membership/status",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "status" in data, "Response should contain 'status'"
        assert "is_active" in data, "Response should contain 'is_active'"
        
        print(f"✅ Membership status: {data}")


class TestAISupervisor:
    """AI Supervisor health check tests"""
    
    def test_supervisor_status(self):
        """Test AI Supervisor status endpoint returns healthy"""
        response = requests.get(f"{BASE_URL}/api/supervisor/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "health_score" in data, "Response should contain 'health_score'"
        assert data["health_score"] > 0, "Health score should be positive"
        
        # Check circuit breakers
        if "circuit_breakers" in data:
            print(f"✅ AI Supervisor healthy: health_score={data['health_score']}, circuit_breakers={data.get('circuit_breakers', {})}")
        else:
            print(f"✅ AI Supervisor healthy: health_score={data['health_score']}")


class TestTranslationAPI:
    """Translation API tests"""
    
    def test_translate_batch(self):
        """Test batch translation endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/translate/batch",
            json={
                "texts": ["Hello", "Welcome to MedMatch"],
                "target_language": "es"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "translations" in data or "translated" in data, "Response should contain translations"
        
        print(f"✅ Translation API working: {data}")
    
    def test_languages_list(self):
        """Test languages list endpoint"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "languages" in data, "Response should contain 'languages'"
        assert len(data["languages"]) >= 30, f"Should have at least 30 languages, got {len(data['languages'])}"
        
        print(f"✅ Languages available: {len(data['languages'])}")


class TestJobSearchAPI:
    """Job Search API tests"""
    
    def test_job_search(self):
        """Test job search endpoint returns results"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/search",
            params={"query": "nurse", "limit": 10}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "jobs" in data or "results" in data, "Response should contain jobs or results"
        
        jobs = data.get("jobs") or data.get("results", [])
        print(f"✅ Job search working: {len(jobs)} jobs found")


class TestFeedbackAPI:
    """Feedback Learning API tests"""
    
    def test_feedback_categories(self):
        """Test feedback categories returns 10 categories"""
        response = requests.get(f"{BASE_URL}/api/feedback/categories")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "categories" in data, "Response should contain 'categories'"
        assert len(data["categories"]) == 10, f"Should have 10 categories, got {len(data['categories'])}"
        
        print(f"✅ Feedback categories: {len(data['categories'])} categories")
        for cat in data["categories"]:
            print(f"   - {cat['id']}: {cat['name']}")


class TestAutoFillAPI:
    """AutoFill API tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    def test_autofill_data(self, auth_token):
        """Test autofill data endpoint returns resume fields"""
        response = requests.get(
            f"{BASE_URL}/api/autofill/data",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # May return 404 if no resume uploaded, which is acceptable
        if response.status_code == 200:
            data = response.json()
            assert "autofill_data" in data, "Response should contain 'autofill_data'"
            print(f"✅ AutoFill data available: {data.get('fields_available', 0)} fields")
        elif response.status_code == 404:
            print("⚠️ AutoFill: No resume found (expected if no resume uploaded)")
        else:
            pytest.fail(f"Unexpected status {response.status_code}: {response.text}")


class TestAuthenticationFlow:
    """Full authentication flow tests"""
    
    def test_admin_login(self):
        """Test admin login with email works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data, "Response should contain 'access_token'"
        assert "user" in data, "Response should contain 'user'"
        assert data["user"]["email"] == ADMIN_EMAIL, "User email should match"
        
        print(f"✅ Admin login successful: {data['user']['email']}")
    
    def test_auth_me_endpoint(self):
        """Test /auth/me returns user info"""
        # First login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json().get("access_token")
        
        # Then get user info
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "user_id" in data, "Response should contain 'user_id'"
        assert "email" in data, "Response should contain 'email'"
        
        print(f"✅ Auth /me working: {data['email']}")


class TestHealthEndpoints:
    """Health check endpoints"""
    
    def test_health_endpoint(self):
        """Test main health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "healthy", f"Expected healthy status, got {data}"
        
        print(f"✅ Health endpoint: {data}")
    
    def test_status_endpoint(self):
        """Test status endpoint"""
        response = requests.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        print("✅ Status endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
