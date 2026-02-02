"""
Comprehensive Backend API Tests for MedMatch
Tests: Authentication, Jobs, AI Features, Applications, Resume, Saved Jobs
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ai-job-hunter-4.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "MedMatch2026!"
TEST_EMAIL = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "TestPass123!"


class TestAuthentication:
    """Authentication endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_login_success(self):
        """Test successful login with admin credentials"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert "access_token" in data
        print(f"✓ Login successful for {ADMIN_EMAIL}")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpass"
        })
        assert response.status_code in [401, 400], f"Expected 401/400, got {response.status_code}"
        print("✓ Invalid credentials rejected correctly")
    
    def test_register_new_user(self):
        """Test user registration"""
        response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": "Test User",
            "role": "job_seeker"
        })
        assert response.status_code in [200, 201], f"Registration failed: {response.text}"
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == TEST_EMAIL
        print(f"✓ User registration successful for {TEST_EMAIL}")
    
    def test_get_current_user(self):
        """Test getting current user info"""
        # First login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200
        
        # Get current user
        response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200, f"Get user failed: {response.text}"
        data = response.json()
        assert "user_id" in data
        assert data["email"] == ADMIN_EMAIL
        print("✓ Get current user successful")
    
    def test_logout(self):
        """Test logout functionality"""
        # First login
        self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        # Logout
        response = self.session.post(f"{BASE_URL}/api/auth/logout")
        assert response.status_code == 200, f"Logout failed: {response.text}"
        print("✓ Logout successful")


class TestJobSearch:
    """Job search endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login first
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200, "Login failed in setup"
    
    def test_search_jobs(self):
        """Test job search functionality"""
        response = self.session.get(f"{BASE_URL}/api/jobs/search", params={
            "query": "software engineer",
            "location_type": "remote"
        })
        assert response.status_code == 200, f"Job search failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of jobs"
        print(f"✓ Job search returned {len(data)} results")
    
    def test_search_jobs_with_filters(self):
        """Test job search with multiple filters"""
        response = self.session.get(f"{BASE_URL}/api/jobs/search", params={
            "query": "developer",
            "location_type": "remote",
            "country": "United States"
        })
        assert response.status_code == 200, f"Filtered search failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Filtered job search returned {len(data)} results")
    
    def test_save_job(self):
        """Test saving a job"""
        job_data = {
            "title": "Test Software Engineer",
            "company": "Test Company",
            "location": "Remote",
            "description": "Test job description",
            "url": "https://example.com/job/123",
            "source": "test"
        }
        response = self.session.post(f"{BASE_URL}/api/jobs/save", json=job_data)
        assert response.status_code in [200, 201, 400], f"Save job failed: {response.text}"
        if response.status_code == 400:
            # Job might already be saved
            assert "already saved" in response.text.lower()
            print("✓ Job already saved (expected)")
        else:
            data = response.json()
            assert "id" in data
            print("✓ Job saved successfully")
    
    def test_get_saved_jobs(self):
        """Test getting saved jobs"""
        response = self.session.get(f"{BASE_URL}/api/jobs/saved")
        assert response.status_code == 200, f"Get saved jobs failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} saved jobs")


class TestApplications:
    """Application tracking endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login first
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200, "Login failed in setup"
    
    def test_create_application(self):
        """Test creating a job application"""
        app_data = {
            "job": {
                "title": "Test Application Job",
                "company": "Test Company",
                "location": "Remote",
                "url": f"https://example.com/job/{uuid.uuid4().hex[:8]}"
            },
            "notes": "Test application notes"
        }
        response = self.session.post(f"{BASE_URL}/api/applications", json=app_data)
        assert response.status_code in [200, 201], f"Create application failed: {response.text}"
        data = response.json()
        assert "id" in data
        self.app_id = data["id"]
        print(f"✓ Application created with ID: {self.app_id}")
        return data["id"]
    
    def test_get_applications(self):
        """Test getting all applications"""
        response = self.session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200, f"Get applications failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} applications")
    
    def test_update_application_status(self):
        """Test updating application status"""
        # First create an application
        app_data = {
            "job": {
                "title": "Status Update Test Job",
                "company": "Test Company",
                "url": f"https://example.com/job/{uuid.uuid4().hex[:8]}"
            },
            "notes": ""
        }
        create_response = self.session.post(f"{BASE_URL}/api/applications", json=app_data)
        assert create_response.status_code in [200, 201]
        app_id = create_response.json()["id"]
        
        # Update status
        response = self.session.put(f"{BASE_URL}/api/applications/{app_id}", json={
            "status": "interviewing"
        })
        assert response.status_code == 200, f"Update status failed: {response.text}"
        print("✓ Application status updated successfully")


class TestResume:
    """Resume endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login first
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200, "Login failed in setup"
    
    def test_get_resume(self):
        """Test getting resume"""
        response = self.session.get(f"{BASE_URL}/api/resume")
        # Resume might not exist yet
        assert response.status_code in [200, 404], f"Get resume failed: {response.text}"
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Resume retrieved: {data.get('full_name', 'No name')}")
        else:
            print("✓ No resume found (expected for new user)")


class TestAIFeatures:
    """AI Features endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login first
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200, "Login failed in setup"
    
    def test_ai_assistant(self):
        """Test KARAU DRAGON AI assistant"""
        response = self.session.post(f"{BASE_URL}/api/assistant", json={
            "message": "What are some tips for job interviews?",
            "context": "interview"
        })
        assert response.status_code == 200, f"AI assistant failed: {response.text}"
        data = response.json()
        assert "response" in data
        assert data.get("assistant") == "KARAU DRAGON"
        print("✓ AI assistant responded successfully")
    
    def test_interview_prep_generate(self):
        """Test interview prep question generation"""
        response = self.session.post(f"{BASE_URL}/api/interview-prep", json={
            "job_title": "Software Engineer",
            "company": "Tech Company",
            "difficulty": "medium",
            "num_questions": 3
        })
        assert response.status_code == 200, f"Interview prep failed: {response.text}"
        data = response.json()
        assert "questions" in data
        assert len(data["questions"]) > 0
        print(f"✓ Generated {len(data['questions'])} interview questions")
    
    def test_interview_prep_history(self):
        """Test getting interview prep history"""
        response = self.session.get(f"{BASE_URL}/api/interview-prep/history")
        assert response.status_code == 200, f"Get history failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} interview prep records")
    
    def test_quick_probability(self):
        """Test quick callback probability"""
        response = self.session.post(f"{BASE_URL}/api/jobs/quick-probability", json={
            "job_title": "Software Engineer",
            "company": "Test Company",
            "job_description": "Looking for a skilled software engineer with Python experience.",
            "location": "Remote"
        })
        assert response.status_code == 200, f"Quick probability failed: {response.text}"
        data = response.json()
        assert "probability_score" in data
        assert "probability_label" in data
        print(f"✓ Quick probability: {data['probability_score']}% ({data['probability_label']})")
    
    def test_voice_coach(self):
        """Test voice coach tips"""
        response = self.session.post(f"{BASE_URL}/api/voice-coach", json={
            "mode": "tips",
            "topic": "elevator pitch"
        })
        assert response.status_code == 200, f"Voice coach failed: {response.text}"
        data = response.json()
        assert "coaching" in data or "key_points" in data
        print("✓ Voice coach tips retrieved")
    
    def test_stt_status(self):
        """Test speech-to-text status"""
        response = self.session.get(f"{BASE_URL}/api/stt/status")
        assert response.status_code == 200, f"STT status failed: {response.text}"
        data = response.json()
        assert "available" in data
        print(f"✓ STT available: {data['available']}")


class TestMembership:
    """Membership endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login first
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200, "Login failed in setup"
    
    def test_get_membership_status(self):
        """Test getting membership status"""
        response = self.session.get(f"{BASE_URL}/api/membership/status")
        assert response.status_code == 200, f"Get membership failed: {response.text}"
        data = response.json()
        assert "tier" in data
        print(f"✓ Membership tier: {data['tier']}")
    
    def test_get_membership_plans(self):
        """Test getting membership plans"""
        response = self.session.get(f"{BASE_URL}/api/membership/plans")
        assert response.status_code == 200, f"Get plans failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} membership plans")


class TestNotifications:
    """Notification endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login first
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200, "Login failed in setup"
    
    def test_get_notifications(self):
        """Test getting notifications"""
        response = self.session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200, f"Get notifications failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} notifications")


class TestCompanies:
    """Company endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login first
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200, "Login failed in setup"
    
    def test_get_companies(self):
        """Test getting companies list"""
        response = self.session.get(f"{BASE_URL}/api/companies")
        assert response.status_code == 200, f"Get companies failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} companies")


class TestMessages:
    """Messages endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login first
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200, "Login failed in setup"
    
    def test_get_conversations(self):
        """Test getting conversations"""
        response = self.session.get(f"{BASE_URL}/api/messages/conversations")
        assert response.status_code == 200, f"Get conversations failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} conversations")


class TestInterviews:
    """Interview scheduling endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login first
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200, "Login failed in setup"
    
    def test_get_interviews(self):
        """Test getting interviews"""
        response = self.session.get(f"{BASE_URL}/api/interviews")
        assert response.status_code == 200, f"Get interviews failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} interviews")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
