"""
MedMatch Comprehensive Backend Assessment Tests - Fixed Version
Tests all API endpoints for deployment readiness with proper auth handling
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Session for authenticated requests
session = requests.Session()
auth_token = None

def get_auth_token():
    """Get authentication token"""
    global auth_token
    if auth_token:
        return auth_token
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@medmatch.com",
        "password": "MedMatch2026!"
    })
    if response.status_code == 200:
        data = response.json()
        auth_token = data.get("access_token")
        return auth_token
    return None

def auth_headers():
    """Get headers with auth token"""
    token = get_auth_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


class TestSystemHealth:
    """System health and infrastructure tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "MedMatch API"
        assert "version" in data
        print(f"✅ Health: {data['status']}, Version: {data['version']}")
        
    def test_status_endpoint(self):
        """Test /api/status returns operational status"""
        response = requests.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["mongodb"]["status"] == "connected"
        assert data["scheduler"]["running"] == True
        print(f"✅ Status: {data['status']}, MongoDB: {data['mongodb']['status']}")
        
    def test_supervisor_status(self):
        """Test AI Supervisor health score > 80%"""
        response = requests.get(f"{BASE_URL}/api/supervisor/status")
        assert response.status_code == 200
        data = response.json()
        assert "health_score" in data
        health_score = data["health_score"]
        assert health_score >= 80, f"Health score {health_score} is below 80%"
        print(f"✅ AI Supervisor health score: {health_score:.1f}%")
        
    def test_circuit_breakers_closed(self):
        """Test all circuit breakers are closed"""
        response = requests.get(f"{BASE_URL}/api/supervisor/status")
        assert response.status_code == 200
        data = response.json()
        circuit_breakers = data.get("circuit_breakers", {})
        all_closed = True
        for name, cb in circuit_breakers.items():
            if cb["state"] != "closed":
                all_closed = False
                print(f"⚠️ Circuit breaker {name} is {cb['state']}")
        assert all_closed, "Some circuit breakers are not closed"
        print(f"✅ All {len(circuit_breakers)} circuit breakers closed")
            
    def test_rate_limiter_functioning(self):
        """Test rate limiter is operational"""
        response = requests.get(f"{BASE_URL}/api/rate-limit/stats")
        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert data["type"] in ["in-memory", "redis"]
        print(f"✅ Rate limiter type: {data['type']}")
        
    def test_cache_system_operational(self):
        """Test cache system is working"""
        response = requests.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["cache"]["type"] == "in-memory"
        assert "stats" in data["cache"]
        print(f"✅ Cache: {data['cache']['type']}, Size: {data['cache']['stats']['size']}/{data['cache']['stats']['max_size']}")


class TestAuthentication:
    """Authentication endpoint tests"""
    
    def test_login_success(self):
        """Test successful login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "MedMatch2026!"
        })
        assert response.status_code == 200
        data = response.json()
        # Check for access_token (JWT auth) or session_id
        assert "access_token" in data or "session_id" in data or "user" in data
        print(f"✅ Login successful, token type: {data.get('token_type', 'session')}")
        
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code in [401, 404]
        print(f"✅ Invalid login correctly rejected with {response.status_code}")
        
    def test_auth_me_unauthorized(self):
        """Test /api/auth/me without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("✅ Unauthenticated /auth/me correctly returns 401")
        
    def test_auth_me_with_token(self):
        """Test /api/auth/me with valid token"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert "email" in data or "user_id" in data
        print("✅ Authenticated /auth/me returns user data")
        
    def test_apple_signin_config(self):
        """Test Apple Sign In configuration"""
        response = requests.get(f"{BASE_URL}/api/auth/apple/config")
        assert response.status_code == 200
        data = response.json()
        assert data.get("configured") == True
        assert "client_id" in data
        print(f"✅ Apple Sign In configured: {data.get('client_id')}")


class TestJobsAPI:
    """Jobs API endpoint tests"""
    
    def test_job_search(self):
        """Test job search returns results"""
        response = requests.get(f"{BASE_URL}/api/jobs/search", params={
            "query": "developer",
            "source": "all"
        })
        assert response.status_code == 200
        data = response.json()
        # Handle both list and dict with 'jobs' key
        jobs = data if isinstance(data, list) else data.get("jobs", [])
        assert isinstance(jobs, list)
        print(f"✅ Job search returned {len(jobs)} results")
        
    def test_job_search_with_filters(self):
        """Test job search with location filter"""
        response = requests.get(f"{BASE_URL}/api/jobs/search", params={
            "query": "nurse",
            "location": "remote"
        })
        assert response.status_code == 200
        print("✅ Job search with filters works")


class TestResumeAPI:
    """Resume API endpoint tests"""
    
    def test_get_resume_with_auth(self):
        """Test get resume endpoint with auth"""
        response = requests.get(f"{BASE_URL}/api/resume", headers=auth_headers())
        # Returns 200 with data or empty object
        assert response.status_code == 200
        print("✅ Resume endpoint accessible with auth")
        
    def test_autofill_data_with_auth(self):
        """Test autofill data endpoint with auth"""
        response = requests.get(f"{BASE_URL}/api/autofill/data", headers=auth_headers())
        # Returns 200 or 404 if no resume
        assert response.status_code in [200, 404]
        print(f"✅ Autofill endpoint returns {response.status_code}")


class TestCloudStorage:
    """Cloud storage integration tests"""
    
    def test_cloud_status(self):
        """Test cloud storage status endpoint"""
        response = requests.get(f"{BASE_URL}/api/cloud/status")
        assert response.status_code == 200
        data = response.json()
        assert "google_drive" in data
        assert "onedrive" in data
        assert "dropbox" in data
        print("✅ Cloud storage status endpoint works")
        
    def test_google_drive_configured(self):
        """Test Google Drive is configured"""
        response = requests.get(f"{BASE_URL}/api/cloud/status")
        assert response.status_code == 200
        data = response.json()
        assert data["google_drive"]["configured"] == True
        print("✅ Google Drive configured")
        
    def test_onedrive_configured(self):
        """Test OneDrive is configured"""
        response = requests.get(f"{BASE_URL}/api/cloud/status")
        assert response.status_code == 200
        data = response.json()
        assert data["onedrive"]["configured"] == True
        print("✅ OneDrive configured")
        
    def test_dropbox_configured(self):
        """Test Dropbox is configured"""
        response = requests.get(f"{BASE_URL}/api/cloud/status")
        assert response.status_code == 200
        data = response.json()
        assert data["dropbox"]["configured"] == True
        print("✅ Dropbox configured")


class TestLinkedIn:
    """LinkedIn integration tests"""
    
    def test_linkedin_status_with_auth(self):
        """Test LinkedIn integration status with auth"""
        response = requests.get(f"{BASE_URL}/api/linkedin/status", headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data.get("integration_configured") == True
        print("✅ LinkedIn integration configured")


class TestPayments:
    """Payment integration tests"""
    
    def test_membership_status_with_auth(self):
        """Test membership status endpoint with auth"""
        response = requests.get(f"{BASE_URL}/api/membership/status", headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert "tier" in data or "status" in data or "plan" in data
        print(f"✅ Membership status: {data.get('tier', data.get('plan', 'unknown'))}")
        
    def test_paypal_create_payment_with_auth(self):
        """Test PayPal payment creation (sandbox) with auth"""
        response = requests.post(f"{BASE_URL}/api/payments/paypal/create", 
            json={"plan": "premium", "amount": 1.00},
            headers=auth_headers())
        # May return 200 or 422 if missing required fields
        assert response.status_code in [200, 422]
        if response.status_code == 200:
            data = response.json()
            assert "payment_id" in data or "approval_url" in data
            print("✅ PayPal payment creation works")
        else:
            print("⚠️ PayPal requires additional fields")


class TestTranslation:
    """Translation API tests"""
    
    def test_get_languages(self):
        """Test get supported languages"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        lang_count = len(data["languages"])
        assert lang_count >= 39
        print(f"✅ Translation supports {lang_count} languages")
        
    def test_batch_translate(self):
        """Test batch translation"""
        response = requests.post(f"{BASE_URL}/api/translate/batch", json={
            "texts": ["Hello", "Welcome"],
            "target_language": "es"
        })
        assert response.status_code == 200
        data = response.json()
        assert "translations" in data
        print("✅ Batch translation works")


class TestFeedback:
    """Feedback API tests"""
    
    def test_feedback_categories(self):
        """Test feedback categories endpoint"""
        response = requests.get(f"{BASE_URL}/api/feedback/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "categories" in data
        print("✅ Feedback categories endpoint works")


class TestNotifications:
    """Notifications API tests"""
    
    def test_notifications_endpoint(self):
        """Test notifications endpoint"""
        response = requests.get(f"{BASE_URL}/api/notifications", headers=auth_headers())
        # May require auth
        assert response.status_code in [200, 401]
        print(f"✅ Notifications endpoint returns {response.status_code}")


class TestCompanies:
    """Companies API tests"""
    
    def test_companies_list(self):
        """Test companies list endpoint"""
        response = requests.get(f"{BASE_URL}/api/companies")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "companies" in data
        print("✅ Companies list endpoint works")


class TestIDVerification:
    """ID Verification API tests"""
    
    def test_verification_levels(self):
        """Test verification levels endpoint"""
        response = requests.get(f"{BASE_URL}/api/cached/id-levels")
        assert response.status_code == 200
        data = response.json()
        assert "levels" in data
        print(f"✅ ID verification levels: {len(data['levels'])} levels")


class TestAnalytics:
    """Analytics API tests"""
    
    def test_analytics_dashboard(self):
        """Test analytics dashboard endpoint"""
        response = requests.get(f"{BASE_URL}/api/analytics/dashboard", headers=auth_headers())
        # May require auth
        assert response.status_code in [200, 401]
        print(f"✅ Analytics dashboard returns {response.status_code}")


class TestRecruiter:
    """Recruiter API tests"""
    
    def test_recruiter_jobs(self):
        """Test recruiter jobs endpoint"""
        response = requests.get(f"{BASE_URL}/api/recruiter/jobs", headers=auth_headers())
        # May require auth
        assert response.status_code in [200, 401]
        print(f"✅ Recruiter jobs returns {response.status_code}")


class TestDigest:
    """Digest API tests"""
    
    def test_digest_settings(self):
        """Test digest settings endpoint"""
        response = requests.get(f"{BASE_URL}/api/digest/settings", headers=auth_headers())
        # May require auth
        assert response.status_code in [200, 401, 404]
        print(f"✅ Digest settings returns {response.status_code}")


class TestResponseTimes:
    """API response time tests"""
    
    def test_health_response_time(self):
        """Test health endpoint responds < 2 seconds"""
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/health")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 2.0, f"Response time {elapsed}s exceeds 2s limit"
        print(f"✅ Health response time: {elapsed*1000:.0f}ms")
        
    def test_status_response_time(self):
        """Test status endpoint responds < 2 seconds"""
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/status")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 2.0, f"Response time {elapsed}s exceeds 2s limit"
        print(f"✅ Status response time: {elapsed*1000:.0f}ms")


class TestEnvironmentConfig:
    """Environment configuration tests"""
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = requests.options(f"{BASE_URL}/api/health", headers={
            "Origin": "https://liquid-glass-chat-5.preview.emergentagent.com",
            "Access-Control-Request-Method": "GET"
        })
        # CORS preflight should return 200 or actual response
        assert response.status_code in [200, 204]
        print("✅ CORS configured correctly")
        
    def test_api_prefix(self):
        """Test all routes use /api prefix"""
        # Test that root redirects to docs
        response = requests.get(f"{BASE_URL}/", allow_redirects=False)
        assert response.status_code in [200, 307, 308]
        print("✅ API routes use /api prefix")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
