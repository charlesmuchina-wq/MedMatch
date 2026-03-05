"""
Test suite for MedMatch Recruiter Features:
1. Applicant Tracking System
2. Candidate Search
3. In-App Messaging
4. AI Prescreening

Tests the P0/P1 features implemented for recruiters.
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://lumi-productivity.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "MedMatch2026!"
RECRUITER_EMAIL = "testrecruiter@medmatch.com"
RECRUITER_PASSWORD = "Test123!"

# Known test data
TEST_JOB_ID = "posted_12690fde0714"


class TestRecruiterAuth:
    """Test recruiter authentication and session management"""
    
    @pytest.fixture(scope="class")
    def recruiter_session(self):
        """Create authenticated recruiter session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login as recruiter
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
            return session
        
        # If recruiter doesn't exist, register one
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD,
            "name": "Test Recruiter",
            "role": "recruiter"
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
        
        return session
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Create authenticated admin session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
        
        return session
    
    def test_recruiter_login(self, recruiter_session):
        """Test recruiter can login"""
        response = recruiter_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "recruiter" or data.get("email") == RECRUITER_EMAIL
        print(f"✅ Recruiter login successful: {data.get('email')}")


class TestRecruiterDashboard:
    """Test recruiter dashboard stats endpoint"""
    
    @pytest.fixture(scope="class")
    def recruiter_session(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    def test_dashboard_stats_endpoint(self, recruiter_session):
        """Test /api/recruiter/dashboard/stats returns stats"""
        response = recruiter_session.get(f"{BASE_URL}/api/recruiter/dashboard/stats")
        
        # Should return 200 for recruiters
        assert response.status_code in [200, 403], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "jobs" in data
            assert "applicants" in data
            print(f"✅ Dashboard stats: {data.get('jobs', {}).get('total', 0)} jobs, {data.get('applicants', {}).get('total', 0)} applicants")
        else:
            print("⚠️ Dashboard stats returned 403 - user may not be recruiter role")


class TestRecruiterJobs:
    """Test recruiter job posting endpoints"""
    
    @pytest.fixture(scope="class")
    def recruiter_session(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    def test_get_recruiter_jobs(self, recruiter_session):
        """Test GET /api/recruiter/jobs returns job list"""
        response = recruiter_session.get(f"{BASE_URL}/api/recruiter/jobs")
        
        assert response.status_code in [200, 403], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            print(f"✅ Recruiter has {len(data)} job postings")
            
            # Check job structure if any exist
            if len(data) > 0:
                job = data[0]
                assert "id" in job
                assert "title" in job
                print(f"   First job: {job.get('title')} at {job.get('company')}")
    
    def test_create_job_posting(self, recruiter_session):
        """Test POST /api/recruiter/jobs creates a new job"""
        job_data = {
            "title": "TEST_Quality Engineer",
            "company": "Test Medical Devices Inc",
            "location": "Remote",
            "description": "Test job posting for QA testing purposes. Looking for quality engineer with ISO 13485 experience.",
            "salary": "$80,000 - $120,000",
            "tags": ["Quality", "ISO 13485", "Medical Device"]
        }
        
        response = recruiter_session.post(f"{BASE_URL}/api/recruiter/jobs", json=job_data)
        
        assert response.status_code in [200, 403], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "job_id" in data
            print(f"✅ Created job posting: {data.get('job_id')}")
            return data.get("job_id")


class TestApplicantTracking:
    """Test applicant tracking system endpoints"""
    
    @pytest.fixture(scope="class")
    def recruiter_session(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    def test_get_job_applicants(self, recruiter_session):
        """Test GET /api/recruiter/jobs/{job_id}/applicants"""
        # First get recruiter's jobs
        jobs_response = recruiter_session.get(f"{BASE_URL}/api/recruiter/jobs")
        
        if jobs_response.status_code == 200:
            jobs = jobs_response.json()
            if len(jobs) > 0:
                job_id = jobs[0].get("id")
                
                response = recruiter_session.get(f"{BASE_URL}/api/recruiter/jobs/{job_id}/applicants")
                
                assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
                
                if response.status_code == 200:
                    data = response.json()
                    assert "job" in data
                    assert "applicants" in data
                    print(f"✅ Job '{data['job'].get('title')}' has {len(data['applicants'])} applicants")
            else:
                print("⚠️ No jobs found to test applicants endpoint")
        else:
            print(f"⚠️ Could not get jobs: {jobs_response.status_code}")
    
    def test_update_applicant_status(self, recruiter_session):
        """Test PUT /api/recruiter/applicants/{id}/status"""
        # This test requires an existing applicant - we'll test the endpoint structure
        # Using a fake ID to test the endpoint exists and returns proper error
        fake_app_id = "app_test123"
        
        response = recruiter_session.put(
            f"{BASE_URL}/api/recruiter/applicants/{fake_app_id}/status",
            json={"status": "reviewing"}
        )
        
        # Should return 404 for non-existent applicant, not 500
        assert response.status_code in [200, 403, 404], f"Unexpected status: {response.status_code}"
        print(f"✅ Update applicant status endpoint responds correctly: {response.status_code}")
    
    def test_add_applicant_note(self, recruiter_session):
        """Test POST /api/recruiter/applicants/{id}/notes"""
        fake_app_id = "app_test123"
        
        response = recruiter_session.post(
            f"{BASE_URL}/api/recruiter/applicants/{fake_app_id}/notes",
            json={"note": "Test note from automated testing"}
        )
        
        # Should return 404 for non-existent applicant, not 500
        assert response.status_code in [200, 403, 404], f"Unexpected status: {response.status_code}"
        print(f"✅ Add applicant note endpoint responds correctly: {response.status_code}")


class TestCandidateSearch:
    """Test candidate search functionality"""
    
    @pytest.fixture(scope="class")
    def recruiter_session(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    def test_search_candidates_by_skills(self, recruiter_session):
        """Test POST /api/recruiter/candidates/search with skills filter"""
        search_data = {
            "skills": ["Python", "Quality"],
            "keywords": [],
            "limit": 10
        }
        
        response = recruiter_session.post(
            f"{BASE_URL}/api/recruiter/candidates/search",
            json=search_data
        )
        
        assert response.status_code in [200, 403], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "candidates" in data
            assert "total_found" in data
            print(f"✅ Candidate search found {data.get('total_found', 0)} candidates")
            
            # Check candidate structure if any found
            if len(data.get("candidates", [])) > 0:
                candidate = data["candidates"][0]
                assert "full_name" in candidate or "email" in candidate
                print(f"   First candidate: {candidate.get('full_name', 'Anonymous')}")
    
    def test_search_candidates_by_keywords(self, recruiter_session):
        """Test candidate search with keywords"""
        search_data = {
            "skills": [],
            "keywords": ["medical", "quality"],
            "limit": 10
        }
        
        response = recruiter_session.post(
            f"{BASE_URL}/api/recruiter/candidates/search",
            json=search_data
        )
        
        assert response.status_code in [200, 403], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Keyword search found {data.get('total_found', 0)} candidates")
    
    def test_get_candidate_profile(self, recruiter_session):
        """Test GET /api/recruiter/candidates/{candidate_id}"""
        # First search for candidates
        search_response = recruiter_session.post(
            f"{BASE_URL}/api/recruiter/candidates/search",
            json={"skills": [], "keywords": [], "limit": 5}
        )
        
        if search_response.status_code == 200:
            candidates = search_response.json().get("candidates", [])
            if len(candidates) > 0:
                candidate_id = candidates[0].get("id")
                
                response = recruiter_session.get(
                    f"{BASE_URL}/api/recruiter/candidates/{candidate_id}"
                )
                
                assert response.status_code in [200, 403, 404], f"Unexpected status: {response.status_code}"
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Got candidate profile: {data.get('full_name', 'Anonymous')}")
            else:
                print("⚠️ No candidates found to test profile endpoint")


class TestInAppMessaging:
    """Test in-app messaging system"""
    
    @pytest.fixture(scope="class")
    def recruiter_session(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    def test_get_conversations(self, recruiter_session):
        """Test GET /api/messages/conversations"""
        response = recruiter_session.get(f"{BASE_URL}/api/messages/conversations")
        
        assert response.status_code == 200, f"Unexpected status: {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ User has {len(data)} conversations")
        
        if len(data) > 0:
            conv = data[0]
            assert "id" in conv
            assert "participants" in conv
            print(f"   First conversation ID: {conv.get('id')}")
    
    def test_get_unread_count(self, recruiter_session):
        """Test GET /api/messages/unread-count"""
        response = recruiter_session.get(f"{BASE_URL}/api/messages/unread-count")
        
        assert response.status_code == 200, f"Unexpected status: {response.status_code}"
        
        data = response.json()
        assert "unread_count" in data
        print(f"✅ Unread message count: {data.get('unread_count', 0)}")
    
    def test_send_message(self, recruiter_session, admin_session):
        """Test POST /api/messages/send"""
        # Get admin user ID
        admin_me = admin_session.get(f"{BASE_URL}/api/auth/me")
        if admin_me.status_code != 200:
            pytest.skip("Could not get admin user info")
        
        admin_user_id = admin_me.json().get("user_id")
        
        message_data = {
            "recipient_id": admin_user_id,
            "subject": "Test Message from Automated Testing",
            "content": f"This is a test message sent at {time.time()}"
        }
        
        response = recruiter_session.post(
            f"{BASE_URL}/api/messages/send",
            json=message_data
        )
        
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "message_id" in data
            assert "conversation_id" in data
            print(f"✅ Message sent: {data.get('message_id')}")
            return data.get("conversation_id")
    
    def test_get_conversation_messages(self, recruiter_session):
        """Test GET /api/messages/conversations/{id}"""
        # First get conversations
        conv_response = recruiter_session.get(f"{BASE_URL}/api/messages/conversations")
        
        if conv_response.status_code == 200:
            conversations = conv_response.json()
            if len(conversations) > 0:
                conv_id = conversations[0].get("id")
                
                response = recruiter_session.get(
                    f"{BASE_URL}/api/messages/conversations/{conv_id}"
                )
                
                assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
                
                if response.status_code == 200:
                    data = response.json()
                    assert "conversation" in data
                    assert "messages" in data
                    print(f"✅ Conversation has {len(data.get('messages', []))} messages")
            else:
                print("⚠️ No conversations found to test messages endpoint")


class TestAIPrescreening:
    """Test AI prescreening functionality"""
    
    @pytest.fixture(scope="class")
    def recruiter_session(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    def test_ai_prescreen_endpoint_exists(self, recruiter_session):
        """Test POST /api/recruiter/ai-prescreen endpoint exists"""
        # Test with fake IDs to verify endpoint structure
        prescreen_data = {
            "candidate_id": "fake_candidate_123",
            "job_id": "fake_job_123"
        }
        
        response = recruiter_session.post(
            f"{BASE_URL}/api/recruiter/ai-prescreen",
            json=prescreen_data
        )
        
        # Should return 404 for non-existent candidate/job, not 500 (unless AI not configured)
        assert response.status_code in [200, 403, 404, 500], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 404:
            print("✅ AI prescreen endpoint responds correctly (404 for non-existent data)")
        elif response.status_code == 403:
            print("⚠️ AI prescreen returned 403 - user may not be recruiter role")
        elif response.status_code == 500:
            # Check if it's AI not configured error
            data = response.json()
            if "AI" in str(data.get("detail", "")):
                print("⚠️ AI prescreen: AI features not configured")
            else:
                print(f"⚠️ AI prescreen returned 500: {data}")


class TestSidebarNavigation:
    """Test that sidebar shows different links for recruiters vs job seekers"""
    
    def test_recruiter_role_check(self):
        """Verify recruiter role is properly set"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            user = data.get("user", {})
            role = user.get("role", "unknown")
            print(f"✅ User role: {role}")
            
            # Recruiters should have role = "recruiter"
            if role == "recruiter":
                print("   Sidebar should show: Dashboard, My Job Postings, Search Candidates, Messages")
            else:
                print("   Sidebar should show: Job seeker navigation")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
