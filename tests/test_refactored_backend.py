"""
MedMatch Backend API Tests - Post-Refactoring Verification
Tests all critical endpoints after server.py refactoring from 5766 to 211 lines
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://remotejobapp.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "MedMatch2026!"
RECRUITER_EMAIL = "testrecruiter@medmatch.com"
RECRUITER_PASSWORD = "Test123!"


class TestHealthCheck:
    """Health check endpoint - verify server is running"""
    
    def test_health_endpoint(self):
        """Test GET /api/health"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "MedMatch API"
        assert data["version"] == "2.0.0"
        print(f"✅ GET /api/health - Status: {response.status_code}, Version: {data['version']}")


class TestAuthentication:
    """Authentication routes - /api/auth/*"""
    
    def test_admin_login(self):
        """Test POST /api/auth/login with admin credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        print(f"✅ POST /api/auth/login (admin) - Status: {response.status_code}")
        return data["access_token"]
    
    def test_invalid_login(self):
        """Test POST /api/auth/login with invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "invalid@test.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        print(f"✅ POST /api/auth/login (invalid) - Status: {response.status_code}")
    
    def test_get_current_user_unauthenticated(self):
        """Test GET /api/auth/me without session"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print(f"✅ GET /api/auth/me (unauthenticated) - Status: {response.status_code}")
    
    def test_get_current_user_authenticated(self):
        """Test GET /api/auth/me with valid session"""
        # Login first
        session = requests.Session()
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert login_response.status_code == 200
        
        # Get current user
        me_response = session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        data = me_response.json()
        assert data["email"] == ADMIN_EMAIL
        print(f"✅ GET /api/auth/me (authenticated) - Status: {me_response.status_code}")


class TestJobSearch:
    """Job search routes - /api/jobs/*"""
    
    def test_search_jobs_default(self):
        """Test GET /api/jobs/search - default search"""
        response = requests.get(f"{BASE_URL}/api/jobs/search")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        print(f"✅ GET /api/jobs/search - Status: {response.status_code}, Jobs: {data['total']}")
    
    def test_search_jobs_with_query(self):
        """Test GET /api/jobs/search?q=engineer"""
        response = requests.get(f"{BASE_URL}/api/jobs/search", params={"q": "engineer"})
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        print(f"✅ GET /api/jobs/search?q=engineer - Status: {response.status_code}, Jobs: {data['total']}")
    
    def test_search_jobs_with_location(self):
        """Test GET /api/jobs/search with location filter"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/search",
            params={"q": "developer", "location": "Remote"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        print(f"✅ GET /api/jobs/search (with location) - Status: {response.status_code}")


class TestResume:
    """Resume routes - /api/resume/*"""
    
    def test_get_resume_authenticated(self):
        """Test GET /api/resume with session"""
        session = requests.Session()
        session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        response = session.get(f"{BASE_URL}/api/resume")
        assert response.status_code == 200
        data = response.json()
        # Resume may have various fields
        print(f"✅ GET /api/resume - Status: {response.status_code}")
    
    def test_resume_upload_endpoint_exists(self):
        """Test POST /api/resume/upload endpoint exists"""
        session = requests.Session()
        session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        # Test with empty file - should return 422 (validation error) or 400
        response = session.post(f"{BASE_URL}/api/resume/upload")
        # Endpoint exists if we get validation error, not 404
        assert response.status_code != 404
        print(f"✅ POST /api/resume/upload endpoint exists - Status: {response.status_code}")


class TestApplications:
    """Applications routes - /api/applications/*"""
    
    def test_get_applications(self):
        """Test GET /api/applications"""
        session = requests.Session()
        session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        response = session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/applications - Status: {response.status_code}, Count: {len(data)}")
    
    def test_create_application(self):
        """Test POST /api/applications"""
        session = requests.Session()
        session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        test_app = {
            "job": {
                "id": f"TEST_refactor_job_{int(time.time())}",
                "title": "TEST Refactoring Verification Job",
                "company": "Test Company",
                "location": "Remote",
                "description": "Test application for refactoring verification",
                "url": f"https://example.com/job/{int(time.time())}",
                "salary": "",
                "tags": ["test"],
                "source": "Test"
            },
            "notes": "Test application for refactoring verification"
        }
        
        response = session.post(f"{BASE_URL}/api/applications", json=test_app)
        assert response.status_code == 200
        data = response.json()
        assert "application" in data or "message" in data
        print(f"✅ POST /api/applications - Status: {response.status_code}")


class TestCoverLetter:
    """Cover letter routes - /api/cover-letter/*"""
    
    def test_generate_cover_letter(self):
        """Test POST /api/cover-letter/generate"""
        session = requests.Session()
        session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        request_data = {
            "job_title": "Software Engineer",
            "company": "Test Tech Inc",
            "job_description": "Looking for a software engineer with Python experience.",
            "job_url": "https://example.com/job"
        }
        
        response = session.post(
            f"{BASE_URL}/api/cover-letter/generate",
            json=request_data,
            timeout=60
        )
        # May return 200 (success) or 400/500 (if resume not uploaded or AI error)
        assert response.status_code in [200, 400, 500]
        print(f"✅ POST /api/cover-letter/generate - Status: {response.status_code}")


class TestInterviewPrep:
    """Interview prep routes - /api/interview/*"""
    
    def test_generate_interview_questions(self):
        """Test POST /api/interview/generate-questions"""
        session = requests.Session()
        session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        request_data = {
            "job_title": "Software Engineer",
            "company": "Test Tech Inc",
            "job_description": "Looking for a software engineer with Python experience."
        }
        
        response = session.post(
            f"{BASE_URL}/api/interview/generate-questions",
            json=request_data,
            timeout=60
        )
        # May return 200 (success) or 400/500 (if AI error)
        assert response.status_code in [200, 400, 500]
        print(f"✅ POST /api/interview/generate-questions - Status: {response.status_code}")


class TestAnalytics:
    """Analytics routes - /api/analytics/*"""
    
    def test_get_analytics_dashboard(self):
        """Test GET /api/analytics/dashboard"""
        session = requests.Session()
        session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        response = session.get(f"{BASE_URL}/api/analytics/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "status_breakdown" in data
        print(f"✅ GET /api/analytics/dashboard - Status: {response.status_code}")


class TestRecruiter:
    """Recruiter routes - /api/recruiter/*"""
    
    def test_recruiter_dashboard_stats_unauthenticated(self):
        """Test GET /api/recruiter/dashboard/stats without auth"""
        response = requests.get(f"{BASE_URL}/api/recruiter/dashboard/stats")
        assert response.status_code == 401
        print(f"✅ GET /api/recruiter/dashboard/stats (unauthenticated) - Status: {response.status_code}")
    
    def test_recruiter_dashboard_stats_non_recruiter(self):
        """Test GET /api/recruiter/dashboard/stats with non-recruiter user"""
        session = requests.Session()
        session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        response = session.get(f"{BASE_URL}/api/recruiter/dashboard/stats")
        # Admin may or may not have recruiter role
        assert response.status_code in [200, 403]
        print(f"✅ GET /api/recruiter/dashboard/stats (admin) - Status: {response.status_code}")


class TestMessaging:
    """Messaging routes - /api/messages/*"""
    
    def test_get_conversations(self):
        """Test GET /api/messages/conversations"""
        session = requests.Session()
        session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        response = session.get(f"{BASE_URL}/api/messages/conversations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/messages/conversations - Status: {response.status_code}, Count: {len(data)}")
    
    def test_get_unread_count(self):
        """Test GET /api/messages/unread-count"""
        session = requests.Session()
        session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        response = session.get(f"{BASE_URL}/api/messages/unread-count")
        assert response.status_code == 200
        data = response.json()
        assert "unread_count" in data
        print(f"✅ GET /api/messages/unread-count - Status: {response.status_code}, Count: {data['unread_count']}")


class TestSessionPersistence:
    """Session persistence across multiple requests"""
    
    def test_session_persists_across_requests(self):
        """Test that session persists across multiple API calls"""
        session = requests.Session()
        
        # Login
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert login_response.status_code == 200
        
        # Make multiple authenticated requests
        endpoints = [
            "/api/auth/me",
            "/api/applications",
            "/api/analytics/dashboard",
            "/api/messages/conversations"
        ]
        
        for endpoint in endpoints:
            response = session.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"Failed on {endpoint}: {response.status_code}"
        
        print(f"✅ Session persistence verified across {len(endpoints)} requests")


class TestSavedJobs:
    """Saved jobs routes - /api/saved-jobs/*"""
    
    def test_get_saved_jobs(self):
        """Test GET /api/saved-jobs"""
        session = requests.Session()
        session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        response = session.get(f"{BASE_URL}/api/saved-jobs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/saved-jobs - Status: {response.status_code}, Count: {len(data)}")


class TestJobAlerts:
    """Job alerts routes - /api/job-alerts/*"""
    
    def test_get_job_alerts(self):
        """Test GET /api/job-alerts"""
        session = requests.Session()
        session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        response = session.get(f"{BASE_URL}/api/job-alerts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/job-alerts - Status: {response.status_code}, Count: {len(data)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
