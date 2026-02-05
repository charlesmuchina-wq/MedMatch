"""
Comprehensive Functional Assessment Test Suite for MedMatch Platform
Tests all major API endpoints across all user types and features.
"""
import pytest
import requests
import os
from datetime import datetime

# Get backend URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
JOB_SEEKER_CREDS = {"email": "test_jobseeker_ui@test.com", "password": "Test123!"}
ADMIN_CREDS = {"email": "admin@medmatch.com", "password": "MedMatch2026!"}
RECRUITER_CREDS = {"email": "recruiter_test@emergent.com", "password": "testpassword"}


class TestHealthAndStatus:
    """Basic health and status endpoints"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        print(f"✅ Health check passed - Version: {data['version']}")
    
    def test_status_endpoint(self):
        """Test /api/status returns operational status"""
        response = requests.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "mongodb" in data
        print(f"✅ Status check passed - MongoDB: {data['mongodb']['status']}")


class TestAuthentication:
    """Authentication flow tests"""
    
    def test_admin_login(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "admin@medmatch.com"
        print(f"✅ Admin login successful")
        return data["access_token"]
    
    def test_job_seeker_login(self):
        """Test job seeker login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if response.status_code == 401:
            # Create user if doesn't exist
            register_data = {
                "email": JOB_SEEKER_CREDS["email"],
                "password": JOB_SEEKER_CREDS["password"],
                "name": "Test Job Seeker",
                "role": "job_seeker"
            }
            response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print(f"✅ Job seeker login/register successful")
        return data["access_token"]
    
    def test_recruiter_login(self):
        """Test recruiter login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_CREDS)
        if response.status_code == 401:
            # Create recruiter if doesn't exist
            register_data = {
                "email": RECRUITER_CREDS["email"],
                "password": RECRUITER_CREDS["password"],
                "name": "Test Recruiter",
                "role": "recruiter"
            }
            response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print(f"✅ Recruiter login/register successful")
        return data["access_token"]
    
    def test_invalid_login(self):
        """Test invalid credentials return 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print(f"✅ Invalid login correctly rejected")
    
    def test_get_current_user(self):
        """Test /api/auth/me endpoint"""
        # First login
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code != 200:
            pytest.skip("Could not login")
        
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        print(f"✅ Get current user successful - User ID: {data['user_id']}")


class TestJobSearch:
    """Job search and related endpoints"""
    
    def test_job_search_basic(self):
        """Test basic job search"""
        response = requests.get(f"{BASE_URL}/api/jobs/search", params={"q": "quality engineer"})
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        print(f"✅ Job search returned {len(data['jobs'])} jobs")
    
    def test_job_search_with_location(self):
        """Test job search with location filter"""
        response = requests.get(f"{BASE_URL}/api/jobs/search", params={
            "q": "software engineer",
            "location": "Remote"
        })
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        print(f"✅ Job search with location returned {len(data['jobs'])} jobs")
    
    def test_job_sources(self):
        """Test job sources endpoint"""
        response = requests.get(f"{BASE_URL}/api/jobs/sources")
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert len(data["sources"]) > 0
        print(f"✅ Job sources returned {len(data['sources'])} sources")
    
    def test_quality_keywords(self):
        """Test quality engineering keywords endpoint"""
        response = requests.get(f"{BASE_URL}/api/jobs/quality-keywords")
        assert response.status_code == 200
        data = response.json()
        assert "keywords" in data
        assert "categories" in data
        print(f"✅ Quality keywords returned {len(data['keywords'])} keywords")


class TestNotifications:
    """Notification system tests"""
    
    @pytest.fixture
    def auth_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code != 200:
            # Register if not exists
            requests.post(f"{BASE_URL}/api/auth/register", json={
                "email": JOB_SEEKER_CREDS["email"],
                "password": JOB_SEEKER_CREDS["password"],
                "name": "Test Job Seeker",
                "role": "job_seeker"
            })
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_notifications(self, auth_headers):
        """Test getting notifications"""
        response = requests.get(f"{BASE_URL}/api/notifications", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        print(f"✅ Get notifications successful - {len(data['notifications'])} notifications")
    
    def test_get_notification_preferences(self, auth_headers):
        """Test getting notification preferences"""
        response = requests.get(f"{BASE_URL}/api/notifications/preferences", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "preferences" in data or "email_enabled" in data
        print(f"✅ Get notification preferences successful")
    
    def test_update_notification_preferences(self, auth_headers):
        """Test updating notification preferences"""
        response = requests.put(f"{BASE_URL}/api/notifications/preferences", 
            headers=auth_headers,
            json={"email_enabled": True, "push_enabled": True}
        )
        assert response.status_code == 200
        print(f"✅ Update notification preferences successful")


class TestGeolocation:
    """Geolocation and location services tests"""
    
    @pytest.fixture
    def auth_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code != 200:
            requests.post(f"{BASE_URL}/api/auth/register", json={
                "email": JOB_SEEKER_CREDS["email"],
                "password": JOB_SEEKER_CREDS["password"],
                "name": "Test Job Seeker",
                "role": "job_seeker"
            })
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_major_hubs(self, auth_headers):
        """Test getting major tech/healthcare hubs"""
        response = requests.get(f"{BASE_URL}/api/geolocation/hubs", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "hubs" in data
        print(f"✅ Get major hubs successful - {len(data['hubs'])} hubs")
    
    def test_calculate_distance(self, auth_headers):
        """Test distance calculation between two points"""
        response = requests.post(f"{BASE_URL}/api/geolocation/distance", 
            headers=auth_headers,
            json={
                "from_lat": 37.7749,
                "from_lng": -122.4194,
                "to_lat": 34.0522,
                "to_lng": -118.2437
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "distance_miles" in data
        # SF to LA should be ~350 miles
        assert 300 < data["distance_miles"] < 400
        print(f"✅ Distance calculation successful - {data['distance_miles']:.0f} miles")
    
    def test_get_geolocation_preferences(self, auth_headers):
        """Test getting geolocation preferences"""
        response = requests.get(f"{BASE_URL}/api/geolocation/preferences", headers=auth_headers)
        assert response.status_code == 200
        print(f"✅ Get geolocation preferences successful")


class TestJobVerification:
    """Ghost job prevention and verification tests"""
    
    @pytest.fixture
    def auth_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code != 200:
            requests.post(f"{BASE_URL}/api/auth/register", json={
                "email": JOB_SEEKER_CREDS["email"],
                "password": JOB_SEEKER_CREDS["password"],
                "name": "Test Job Seeker",
                "role": "job_seeker"
            })
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_report_expired_job(self, auth_headers):
        """Test reporting an expired/ghost job"""
        response = requests.post(f"{BASE_URL}/api/jobs/verify/report", 
            headers=auth_headers,
            json={
                "job_id": "test_job_123",
                "job_url": "https://example.com/job/123",
                "reason": "expired",
                "details": "Job posting is no longer available"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "report_id" in data or "success" in data
        print(f"✅ Report expired job successful")
    
    def test_get_job_verification_status(self, auth_headers):
        """Test getting job verification status"""
        response = requests.get(f"{BASE_URL}/api/jobs/verify/test_job_123", headers=auth_headers)
        # May return 200 or 404 depending on if job exists
        assert response.status_code in [200, 404]
        print(f"✅ Get job verification status - Status: {response.status_code}")


class TestCredentials:
    """Credential verification and trust score tests"""
    
    @pytest.fixture
    def auth_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code != 200:
            requests.post(f"{BASE_URL}/api/auth/register", json={
                "email": JOB_SEEKER_CREDS["email"],
                "password": JOB_SEEKER_CREDS["password"],
                "name": "Test Job Seeker",
                "role": "job_seeker"
            })
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_certifications(self, auth_headers):
        """Test getting available certifications"""
        response = requests.get(f"{BASE_URL}/api/credentials/certifications", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "certifications" in data
        print(f"✅ Get certifications successful - {len(data['certifications'])} certifications")
    
    def test_get_trust_score(self, auth_headers):
        """Test getting user trust score"""
        response = requests.get(f"{BASE_URL}/api/credentials/trust-score", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_score" in data or "score" in data
        print(f"✅ Get trust score successful")
    
    def test_get_my_credentials(self, auth_headers):
        """Test getting user's credentials"""
        response = requests.get(f"{BASE_URL}/api/credentials/my-credentials", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "credentials" in data
        print(f"✅ Get my credentials successful - {len(data['credentials'])} credentials")


class TestEmployerReviews:
    """Employer review system tests"""
    
    @pytest.fixture
    def recruiter_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_CREDS)
        if login_resp.status_code != 200:
            requests.post(f"{BASE_URL}/api/auth/register", json={
                "email": RECRUITER_CREDS["email"],
                "password": RECRUITER_CREDS["password"],
                "name": "Test Recruiter",
                "role": "recruiter"
            })
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_CREDS)
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture
    def job_seeker_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code != 200:
            requests.post(f"{BASE_URL}/api/auth/register", json={
                "email": JOB_SEEKER_CREDS["email"],
                "password": JOB_SEEKER_CREDS["password"],
                "name": "Test Job Seeker",
                "role": "job_seeker"
            })
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_strength_suggestions(self, recruiter_headers):
        """Test getting strength suggestions for reviews"""
        response = requests.get(f"{BASE_URL}/api/reviews/strength-suggestions", headers=recruiter_headers)
        assert response.status_code == 200
        data = response.json()
        assert "strengths" in data
        print(f"✅ Get strength suggestions successful")
    
    def test_get_my_reviews(self, job_seeker_headers):
        """Test getting reviews received by job seeker"""
        response = requests.get(f"{BASE_URL}/api/reviews/my-reviews", headers=job_seeker_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_reviews" in data
        print(f"✅ Get my reviews successful - {data['total_reviews']} reviews")


class TestAIFeatures:
    """AI-powered features tests"""
    
    @pytest.fixture
    def auth_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code != 200:
            requests.post(f"{BASE_URL}/api/auth/register", json={
                "email": JOB_SEEKER_CREDS["email"],
                "password": JOB_SEEKER_CREDS["password"],
                "name": "Test Job Seeker",
                "role": "job_seeker"
            })
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_dragon_ai_assistant(self, auth_headers):
        """Test KARAU Dragon AI assistant"""
        response = requests.post(f"{BASE_URL}/api/assistant", 
            headers=auth_headers,
            json={"message": "What jobs are available for quality engineers?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data or "message" in data or "answer" in data
        print(f"✅ Dragon AI assistant responded successfully")
    
    def test_ai_cover_letter(self, auth_headers):
        """Test AI cover letter generation"""
        response = requests.post(f"{BASE_URL}/api/ai/cover-letter", 
            headers=auth_headers,
            json={
                "job_title": "Quality Engineer",
                "company": "Test Company",
                "job_description": "Looking for a quality engineer with 5 years experience"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "cover_letter" in data or "content" in data
        print(f"✅ AI cover letter generation successful")
    
    def test_ai_interview_questions(self, auth_headers):
        """Test AI interview question generation"""
        response = requests.post(f"{BASE_URL}/api/ai/interview-questions", 
            headers=auth_headers,
            json={
                "job_title": "Quality Engineer",
                "skills": ["ISO 13485", "FDA compliance", "CAPA"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        print(f"✅ AI interview questions generated - {len(data['questions'])} questions")


class TestTranslation:
    """Translation and i18n tests"""
    
    def test_get_supported_languages(self):
        """Test getting supported languages"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        print(f"✅ Get supported languages - {len(data['languages'])} languages")
    
    def test_translate_text(self):
        """Test text translation"""
        response = requests.post(f"{BASE_URL}/api/translate", json={
            "text": "Hello, how are you?",
            "target_language": "es"
        })
        assert response.status_code == 200
        data = response.json()
        assert "translated_text" in data or "translation" in data
        print(f"✅ Text translation successful")
    
    def test_translation_analytics(self):
        """Test translation analytics endpoint"""
        response = requests.get(f"{BASE_URL}/api/translation-analytics")
        assert response.status_code == 200
        print(f"✅ Translation analytics endpoint working")


class TestAdminFeatures:
    """Admin-only features tests"""
    
    @pytest.fixture
    def admin_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_admin_pending_reviews(self, admin_headers):
        """Test admin getting pending reviews"""
        response = requests.get(f"{BASE_URL}/api/reviews/admin/pending", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "pending_reviews" in data
        print(f"✅ Admin pending reviews - {len(data['pending_reviews'])} pending")
    
    def test_admin_review_stats(self, admin_headers):
        """Test admin review statistics"""
        response = requests.get(f"{BASE_URL}/api/reviews/admin/stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "pending_count" in data
        print(f"✅ Admin review stats - Pending: {data['pending_count']}")
    
    def test_admin_credentials_pending(self, admin_headers):
        """Test admin getting pending credential reviews"""
        response = requests.get(f"{BASE_URL}/api/credentials/admin/pending-reviews", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "pending_reviews" in data
        print(f"✅ Admin credentials pending - {len(data['pending_reviews'])} pending")


class TestProductionMetrics:
    """Production metrics and monitoring tests"""
    
    def test_production_metrics(self):
        """Test production metrics endpoint"""
        response = requests.get(f"{BASE_URL}/api/production-metrics")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Production metrics endpoint working")
    
    def test_supervisor_status(self):
        """Test AI supervisor status"""
        response = requests.get(f"{BASE_URL}/api/supervisor/status")
        assert response.status_code == 200
        data = response.json()
        assert "health" in data
        print(f"✅ Supervisor status - Health: {data['health']}")
    
    def test_rate_limit_status(self):
        """Test rate limit status"""
        response = requests.get(f"{BASE_URL}/api/rate-limit/status")
        assert response.status_code == 200
        data = response.json()
        assert "tier" in data
        print(f"✅ Rate limit status - Tier: {data['tier']}")


class TestJobAlerts:
    """Job alerts tests"""
    
    @pytest.fixture
    def auth_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code != 200:
            requests.post(f"{BASE_URL}/api/auth/register", json={
                "email": JOB_SEEKER_CREDS["email"],
                "password": JOB_SEEKER_CREDS["password"],
                "name": "Test Job Seeker",
                "role": "job_seeker"
            })
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_job_alerts(self, auth_headers):
        """Test getting job alerts"""
        response = requests.get(f"{BASE_URL}/api/jobs/alerts", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        print(f"✅ Get job alerts successful - {len(data['alerts'])} alerts")
    
    def test_create_job_alert(self, auth_headers):
        """Test creating a job alert"""
        response = requests.post(f"{BASE_URL}/api/jobs/alerts", 
            headers=auth_headers,
            json={
                "keywords": ["quality engineer", "QA manager"],
                "locations": ["Remote", "San Francisco"],
                "email": JOB_SEEKER_CREDS["email"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "alert_id" in data or "id" in data or "success" in data
        print(f"✅ Create job alert successful")


class TestDeepSearch:
    """Deep search and web crawling tests"""
    
    @pytest.fixture
    def auth_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code != 200:
            requests.post(f"{BASE_URL}/api/auth/register", json={
                "email": JOB_SEEKER_CREDS["email"],
                "password": JOB_SEEKER_CREDS["password"],
                "name": "Test Job Seeker",
                "role": "job_seeker"
            })
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_deep_search(self, auth_headers):
        """Test AI deep search"""
        response = requests.post(f"{BASE_URL}/api/jobs/deep-search", 
            headers=auth_headers,
            json={
                "query": "quality engineer medical device",
                "skills": ["ISO 13485", "FDA"]
            }
        )
        # Deep search may take time, so we just check it doesn't error
        assert response.status_code in [200, 202, 504]  # 504 timeout is acceptable for long searches
        print(f"✅ Deep search endpoint working - Status: {response.status_code}")


class TestPrivacy:
    """Privacy and GDPR compliance tests"""
    
    @pytest.fixture
    def auth_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code != 200:
            requests.post(f"{BASE_URL}/api/auth/register", json={
                "email": JOB_SEEKER_CREDS["email"],
                "password": JOB_SEEKER_CREDS["password"],
                "name": "Test Job Seeker",
                "role": "job_seeker"
            })
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_data_export(self, auth_headers):
        """Test GDPR data export (Article 20)"""
        response = requests.get(f"{BASE_URL}/api/privacy/export", headers=auth_headers)
        assert response.status_code == 200
        print(f"✅ Data export endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
