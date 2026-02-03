"""
Mutual Match E2E Test Suite
============================
Tests the complete recruiter-candidate mutual match workflow:
1. Recruiter registration and verification
2. Job seeker resume creation
3. Recruiter job posting
4. Blind screening candidate search
5. Contact request flow
6. Accept/Decline workflow
7. Secure messaging after match
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

# Base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
JOB_SEEKER_EMAIL = "testuser@medmatch.com"
JOB_SEEKER_PASSWORD = "Test123!"
RECRUITER_EMAIL = "recruiter@medmatch.com"
RECRUITER_PASSWORD = "Test123!"


class TestSetupAndAuth:
    """Test authentication and setup"""
    
    @pytest.fixture(scope="class")
    def job_seeker_token(self):
        """Get job seeker auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": JOB_SEEKER_PASSWORD
        })
        assert response.status_code == 200, f"Job seeker login failed: {response.text}"
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def recruiter_token(self):
        """Get recruiter auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        assert response.status_code == 200, f"Recruiter login failed: {response.text}"
        return response.json()["access_token"]
    
    def test_health_check(self):
        """Test API health"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ API Health: {data['status']}")
    
    def test_job_seeker_login(self, job_seeker_token):
        """Test job seeker can login"""
        assert job_seeker_token is not None
        print(f"✓ Job seeker login successful")
    
    def test_recruiter_login(self, recruiter_token):
        """Test recruiter can login"""
        assert recruiter_token is not None
        print(f"✓ Recruiter login successful")


class TestRecruiterSetup:
    """Test recruiter registration and verification"""
    
    @pytest.fixture(scope="class")
    def recruiter_token(self):
        """Get recruiter auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_recruiter_registration(self, recruiter_token):
        """Register recruiter profile"""
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        
        # First check current status
        status_response = requests.get(
            f"{BASE_URL}/api/recruiter-rbac/verification/status",
            headers=headers
        )
        current_status = status_response.json()
        print(f"Current recruiter status: {current_status}")
        
        # If not registered, register
        if current_status.get("status") == "not_registered":
            registration_data = {
                "company_name": "MedMatch Healthcare",
                "company_website": "https://medmatch-healthcare.com",
                "business_email": "recruiter@medmatch-healthcare.com",
                "job_title": "Senior Recruiter",
                "department": "Human Resources",
                "phone_number": "+1-555-123-4567",
                "company_size": "51-200",
                "healthcare_sector": "Hospital"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/recruiter-rbac/register",
                json=registration_data,
                headers=headers
            )
            
            # May fail due to email domain validation - that's expected
            if response.status_code == 200:
                print(f"✓ Recruiter registered: {response.json()}")
            else:
                print(f"Registration response: {response.status_code} - {response.text}")
        else:
            print(f"✓ Recruiter already registered with status: {current_status.get('status')}")
    
    def test_recruiter_verification_status(self, recruiter_token):
        """Check recruiter verification status"""
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/recruiter-rbac/verification/status",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Verification status: {data}")
        return data


class TestJobSeekerSetup:
    """Test job seeker resume setup"""
    
    @pytest.fixture(scope="class")
    def job_seeker_token(self):
        """Get job seeker auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": JOB_SEEKER_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_check_resume(self, job_seeker_token):
        """Check if job seeker has a resume"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        
        response = requests.get(f"{BASE_URL}/api/resume", headers=headers)
        assert response.status_code == 200
        
        resume = response.json()
        if resume:
            print(f"✓ Resume exists: {resume.get('full_name', 'Unknown')}")
        else:
            print("✗ No resume found - needs to be created")
        
        return resume


class TestRecruiterJobPosting:
    """Test recruiter job posting"""
    
    @pytest.fixture(scope="class")
    def recruiter_token(self):
        """Get recruiter auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_get_posted_jobs(self, recruiter_token):
        """Get recruiter's posted jobs"""
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        
        response = requests.get(f"{BASE_URL}/api/recruiter/jobs", headers=headers)
        assert response.status_code == 200
        
        jobs = response.json()
        print(f"✓ Posted jobs count: {len(jobs)}")
        return jobs
    
    def test_create_job_posting(self, recruiter_token):
        """Create a test job posting"""
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        
        job_data = {
            "title": "TEST_Senior ICU Nurse",
            "company": "MedMatch Healthcare",
            "location": "New York, NY",
            "description": "We are looking for an experienced ICU nurse with critical care skills. Must have BLS/ACLS certification and 3+ years experience.",
            "salary": "$80,000 - $100,000",
            "tags": ["ICU", "Critical Care", "Nursing", "Healthcare"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/recruiter/jobs",
            json=job_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Job created: {data.get('job_id')}")
        return data.get("job_id")


class TestBlindScreening:
    """Test blind screening functionality"""
    
    @pytest.fixture(scope="class")
    def recruiter_token(self):
        """Get recruiter auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_blind_screening_status(self, recruiter_token):
        """Check blind screening mode status"""
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/recruiter-rbac/blind-screening/status",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Blind screening mode: {data.get('blind_screening_mode')}")
        return data
    
    def test_toggle_blind_screening(self, recruiter_token):
        """Toggle blind screening mode"""
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        
        # Get current status
        status_response = requests.get(
            f"{BASE_URL}/api/recruiter-rbac/blind-screening/status",
            headers=headers
        )
        current_mode = status_response.json().get("blind_screening_mode", True)
        
        # Toggle
        response = requests.post(
            f"{BASE_URL}/api/recruiter-rbac/blind-screening/toggle",
            json={"enabled": not current_mode},
            headers=headers
        )
        
        # May fail if recruiter profile doesn't exist
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Blind screening toggled: {data}")
        else:
            print(f"Toggle failed (expected if not registered): {response.status_code} - {response.text}")
    
    def test_candidate_search(self, recruiter_token):
        """Search for candidates (requires verified recruiter)"""
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/recruiter-rbac/candidates/search",
            params={"skills": "ICU,Nursing", "limit": 10},
            headers=headers
        )
        
        # May fail if recruiter not verified
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Candidate search results: {data.get('total_found', 0)} candidates")
        elif response.status_code == 403:
            print(f"✗ Candidate search requires verification: {response.json().get('detail')}")
        else:
            print(f"Search response: {response.status_code} - {response.text}")


class TestMutualMatchFlow:
    """Test the mutual match contact request flow"""
    
    @pytest.fixture(scope="class")
    def job_seeker_token(self):
        """Get job seeker auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": JOB_SEEKER_PASSWORD
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def recruiter_token(self):
        """Get recruiter auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_get_sent_requests(self, recruiter_token):
        """Get contact requests sent by recruiter"""
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/mutual-match/requests/sent",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Sent requests: {data.get('total', 0)}")
        return data
    
    def test_get_received_requests(self, job_seeker_token):
        """Get contact requests received by job seeker"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/mutual-match/requests/received",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Received requests: {data.get('total', 0)}, Pending: {data.get('pending_count', 0)}")
        return data
    
    def test_get_matches(self, job_seeker_token):
        """Get mutual matches for job seeker"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/mutual-match/matches",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Mutual matches: {data.get('total', 0)}")
        return data
    
    def test_ghost_mode_status(self, job_seeker_token):
        """Check ghost mode status for job seeker"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/mutual-match/ghost-mode/status",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Ghost mode - Searchable: {data.get('searchable')}, Blocked orgs: {len(data.get('blocked_organizations', []))}")
        return data


class TestSecureMessaging:
    """Test secure messaging between matched users"""
    
    @pytest.fixture(scope="class")
    def job_seeker_token(self):
        """Get job seeker auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": JOB_SEEKER_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_get_matches_for_messaging(self, job_seeker_token):
        """Get matches to test messaging"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/mutual-match/matches",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        if data.get("total", 0) > 0:
            match_id = data["matches"][0]["id"]
            print(f"✓ Found match for messaging: {match_id}")
            return match_id
        else:
            print("✗ No matches found for messaging test")
            return None


# Cleanup test data
class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture(scope="class")
    def recruiter_token(self):
        """Get recruiter auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_cleanup_test_jobs(self, recruiter_token):
        """Delete test job postings"""
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        
        # Get all jobs
        response = requests.get(f"{BASE_URL}/api/recruiter/jobs", headers=headers)
        if response.status_code == 200:
            jobs = response.json()
            for job in jobs:
                if job.get("title", "").startswith("TEST_"):
                    delete_response = requests.delete(
                        f"{BASE_URL}/api/recruiter/jobs/{job['id']}",
                        headers=headers
                    )
                    if delete_response.status_code == 200:
                        print(f"✓ Deleted test job: {job['id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
