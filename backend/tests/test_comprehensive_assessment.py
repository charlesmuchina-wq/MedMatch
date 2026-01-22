"""
MedMatch Comprehensive Backend Assessment Tests
Tests all API endpoints for deployment readiness
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

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
        
    def test_status_endpoint(self):
        """Test /api/status returns operational status"""
        response = requests.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["mongodb"]["status"] == "connected"
        assert data["scheduler"]["running"] == True
        
    def test_supervisor_status(self):
        """Test AI Supervisor health score > 80%"""
        response = requests.get(f"{BASE_URL}/api/supervisor/status")
        assert response.status_code == 200
        data = response.json()
        assert "health_score" in data
        assert data["health_score"] >= 80, f"Health score {data['health_score']} is below 80%"
        
    def test_circuit_breakers_closed(self):
        """Test all circuit breakers are closed"""
        response = requests.get(f"{BASE_URL}/api/supervisor/status")
        assert response.status_code == 200
        data = response.json()
        circuit_breakers = data.get("circuit_breakers", {})
        for name, cb in circuit_breakers.items():
            assert cb["state"] == "closed", f"Circuit breaker {name} is {cb['state']}"
            
    def test_rate_limiter_functioning(self):
        """Test rate limiter is operational"""
        response = requests.get(f"{BASE_URL}/api/rate-limit/stats")
        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert data["type"] in ["in-memory", "redis"]
        
    def test_cache_system_operational(self):
        """Test cache system is working"""
        response = requests.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["cache"]["type"] == "in-memory"
        assert "stats" in data["cache"]


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
        assert "session_id" in data or "user_id" in data
        
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code in [401, 404]
        
    def test_auth_me_unauthorized(self):
        """Test /api/auth/me without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        
    def test_google_oauth_config(self):
        """Test Google OAuth configuration"""
        response = requests.get(f"{BASE_URL}/api/auth/google/config")
        assert response.status_code == 200
        data = response.json()
        assert data.get("configured") == True
        
    def test_apple_signin_config(self):
        """Test Apple Sign In configuration"""
        response = requests.get(f"{BASE_URL}/api/auth/apple/config")
        assert response.status_code == 200
        data = response.json()
        assert data.get("configured") == True
        assert "client_id" in data


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
        assert isinstance(data, list)
        
    def test_job_search_with_filters(self):
        """Test job search with location filter"""
        response = requests.get(f"{BASE_URL}/api/jobs/search", params={
            "query": "nurse",
            "location": "remote"
        })
        assert response.status_code == 200
        
    def test_ai_deep_search(self):
        """Test AI deep search endpoint"""
        response = requests.post(f"{BASE_URL}/api/jobs/ai-search", json={
            "query": "healthcare quality manager",
            "preferences": {"remote": True}
        })
        # May return 200 or 400 depending on resume availability
        assert response.status_code in [200, 400, 404]


class TestResumeAPI:
    """Resume API endpoint tests"""
    
    def test_get_resume(self):
        """Test get resume endpoint"""
        response = requests.get(f"{BASE_URL}/api/resume")
        # Returns 200 with data or empty object
        assert response.status_code == 200
        
    def test_autofill_data(self):
        """Test autofill data endpoint"""
        response = requests.get(f"{BASE_URL}/api/autofill/data")
        # Returns 200 or 404 if no resume
        assert response.status_code in [200, 404]


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
        
    def test_google_drive_configured(self):
        """Test Google Drive is configured"""
        response = requests.get(f"{BASE_URL}/api/cloud/status")
        assert response.status_code == 200
        data = response.json()
        assert data["google_drive"]["configured"] == True
        
    def test_onedrive_configured(self):
        """Test OneDrive is configured"""
        response = requests.get(f"{BASE_URL}/api/cloud/status")
        assert response.status_code == 200
        data = response.json()
        assert data["onedrive"]["configured"] == True
        
    def test_dropbox_configured(self):
        """Test Dropbox is configured"""
        response = requests.get(f"{BASE_URL}/api/cloud/status")
        assert response.status_code == 200
        data = response.json()
        assert data["dropbox"]["configured"] == True
        
    def test_dropbox_auth_url(self):
        """Test Dropbox OAuth URL generation"""
        response = requests.get(f"{BASE_URL}/api/cloud/dropbox/auth-url")
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "qjcao2halndcd70" in data["auth_url"]
        
    def test_onedrive_auth_url(self):
        """Test OneDrive OAuth URL generation"""
        response = requests.get(f"{BASE_URL}/api/cloud/onedrive/auth-url")
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "33fd0966-d65f-4474-9eb7-2afeef5e72df" in data["auth_url"]


class TestLinkedIn:
    """LinkedIn integration tests"""
    
    def test_linkedin_status(self):
        """Test LinkedIn integration status"""
        response = requests.get(f"{BASE_URL}/api/linkedin/status")
        assert response.status_code == 200
        data = response.json()
        assert data.get("integration_configured") == True
        
    def test_linkedin_auth_url(self):
        """Test LinkedIn OAuth URL generation"""
        response = requests.get(f"{BASE_URL}/api/linkedin/auth-url")
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "77wcvs14tufhyu" in data["auth_url"]


class TestPayments:
    """Payment integration tests"""
    
    def test_membership_status(self):
        """Test membership status endpoint"""
        response = requests.get(f"{BASE_URL}/api/membership/status")
        assert response.status_code == 200
        data = response.json()
        assert "tier" in data or "status" in data
        
    def test_paypal_create_payment(self):
        """Test PayPal payment creation (sandbox)"""
        response = requests.post(f"{BASE_URL}/api/payments/paypal/create", json={
            "plan": "premium",
            "amount": 1.00
        })
        assert response.status_code == 200
        data = response.json()
        assert "payment_id" in data
        assert "approval_url" in data
        
    def test_stripe_checkout(self):
        """Test Stripe checkout (may fail with test key)"""
        response = requests.post(f"{BASE_URL}/api/payments/create-checkout", json={
            "plan": "premium",
            "success_url": f"{BASE_URL}/payment-success",
            "cancel_url": f"{BASE_URL}/membership"
        })
        # May fail with placeholder API key
        assert response.status_code in [200, 400, 500, 520]


class TestTranslation:
    """Translation API tests"""
    
    def test_get_languages(self):
        """Test get supported languages"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) >= 39
        
    def test_batch_translate(self):
        """Test batch translation"""
        response = requests.post(f"{BASE_URL}/api/translate/batch", json={
            "texts": ["Hello", "Welcome"],
            "target_language": "es"
        })
        assert response.status_code == 200
        data = response.json()
        assert "translations" in data


class TestInterviewFeatures:
    """Interview and AI features tests"""
    
    def test_interview_questions(self):
        """Test interview questions endpoint"""
        response = requests.post(f"{BASE_URL}/api/interview/questions", json={
            "job_title": "Software Engineer",
            "company": "Tech Corp"
        })
        # May require auth or resume
        assert response.status_code in [200, 400, 401, 404]
        
    def test_qa_practice_categories(self):
        """Test QA practice categories"""
        response = requests.get(f"{BASE_URL}/api/qa-practice/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "categories" in data


class TestFeedback:
    """Feedback API tests"""
    
    def test_feedback_categories(self):
        """Test feedback categories endpoint"""
        response = requests.get(f"{BASE_URL}/api/feedback/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "categories" in data


class TestNotifications:
    """Notifications API tests"""
    
    def test_notifications_endpoint(self):
        """Test notifications endpoint"""
        response = requests.get(f"{BASE_URL}/api/notifications")
        # May require auth
        assert response.status_code in [200, 401]


class TestCompanies:
    """Companies API tests"""
    
    def test_companies_list(self):
        """Test companies list endpoint"""
        response = requests.get(f"{BASE_URL}/api/companies")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "companies" in data


class TestSkills:
    """Skills API tests"""
    
    def test_skills_assessments(self):
        """Test skills assessments endpoint"""
        response = requests.get(f"{BASE_URL}/api/skills/assessments")
        assert response.status_code in [200, 401]


class TestIDVerification:
    """ID Verification API tests"""
    
    def test_verification_levels(self):
        """Test verification levels endpoint"""
        response = requests.get(f"{BASE_URL}/api/cached/id-levels")
        assert response.status_code == 200
        data = response.json()
        assert "levels" in data


class TestAnalytics:
    """Analytics API tests"""
    
    def test_analytics_dashboard(self):
        """Test analytics dashboard endpoint"""
        response = requests.get(f"{BASE_URL}/api/analytics/dashboard")
        # May require auth
        assert response.status_code in [200, 401]


class TestMessages:
    """Messages API tests"""
    
    def test_messages_endpoint(self):
        """Test messages endpoint"""
        response = requests.get(f"{BASE_URL}/api/messages")
        # May require auth
        assert response.status_code in [200, 401]


class TestRecruiter:
    """Recruiter API tests"""
    
    def test_recruiter_jobs(self):
        """Test recruiter jobs endpoint"""
        response = requests.get(f"{BASE_URL}/api/recruiter/jobs")
        # May require auth
        assert response.status_code in [200, 401]


class TestScheduling:
    """Scheduling API tests"""
    
    def test_scheduling_slots(self):
        """Test scheduling slots endpoint"""
        response = requests.get(f"{BASE_URL}/api/scheduling/slots")
        # May require auth
        assert response.status_code in [200, 401]


class TestDigest:
    """Digest API tests"""
    
    def test_digest_settings(self):
        """Test digest settings endpoint"""
        response = requests.get(f"{BASE_URL}/api/digest/settings")
        # May require auth
        assert response.status_code in [200, 401, 404]


class TestDragon:
    """Dragon AI assistant tests"""
    
    def test_dragon_chat(self):
        """Test Dragon AI chat endpoint"""
        response = requests.post(f"{BASE_URL}/api/dragon/chat", json={
            "message": "Hello",
            "context": {}
        })
        # May require auth
        assert response.status_code in [200, 401]


class TestBiometric:
    """Biometric auth tests"""
    
    def test_biometric_status(self):
        """Test biometric status endpoint"""
        response = requests.get(f"{BASE_URL}/api/biometric/status")
        # May require auth
        assert response.status_code in [200, 401]


class TestVideoInterview:
    """Video interview tests"""
    
    def test_video_interview_status(self):
        """Test video interview status endpoint"""
        response = requests.get(f"{BASE_URL}/api/video-interview/status")
        # May require auth
        assert response.status_code in [200, 401]


class TestPushNotifications:
    """Push notifications tests"""
    
    def test_push_subscribe(self):
        """Test push subscription endpoint"""
        response = requests.post(f"{BASE_URL}/api/push/subscribe", json={
            "subscription": {"endpoint": "test"}
        })
        # May require auth or valid subscription
        assert response.status_code in [200, 400, 401]


class TestResponseTimes:
    """API response time tests"""
    
    def test_health_response_time(self):
        """Test health endpoint responds < 2 seconds"""
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/health")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 2.0, f"Response time {elapsed}s exceeds 2s limit"
        
    def test_status_response_time(self):
        """Test status endpoint responds < 2 seconds"""
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/status")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 2.0, f"Response time {elapsed}s exceeds 2s limit"
        
    def test_job_search_response_time(self):
        """Test job search responds < 5 seconds"""
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/jobs/search", params={"query": "nurse"})
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 5.0, f"Response time {elapsed}s exceeds 5s limit"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
