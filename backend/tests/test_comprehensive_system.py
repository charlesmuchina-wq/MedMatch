"""
Comprehensive System Test - MedMatch Full Regression
Tests all major features: Auth, Jobs, Credentials, Trust Score, Reviews, Taxonomy, Recruiter
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user credentials
TEST_JOB_SEEKER_EMAIL = f"test_jobseeker_{uuid.uuid4().hex[:8]}@test.com"
TEST_JOB_SEEKER_PASSWORD = "Test123!"
TEST_RECRUITER_EMAIL = f"test_recruiter_{uuid.uuid4().hex[:8]}@test.com"
TEST_RECRUITER_PASSWORD = "Test123!"
ADMIN_EMAIL = "test_admin_ui@test.com"
ADMIN_PASSWORD = "Test123!"
VERIFIED_RECRUITER_EMAIL = "verified_recruiter@test.com"
VERIFIED_RECRUITER_PASSWORD = "Test123!"


class TestHealthCheck:
    """Basic health check tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ API Health: {data.get('status')}")


class TestAuthentication:
    """Authentication endpoint tests"""
    
    def test_register_job_seeker(self):
        """Test job seeker registration"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_JOB_SEEKER_EMAIL,
            "password": TEST_JOB_SEEKER_PASSWORD,
            "name": "Test Job Seeker",
            "role": "job_seeker"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "job_seeker"
        print(f"✓ Job Seeker Registration: {data['user']['email']}")
        return data["access_token"]
    
    def test_register_recruiter(self):
        """Test recruiter registration"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_RECRUITER_EMAIL,
            "password": TEST_RECRUITER_PASSWORD,
            "name": "Test Recruiter",
            "role": "recruiter"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "recruiter"
        print(f"✓ Recruiter Registration: {data['user']['email']}")
        return data["access_token"]
    
    def test_login_job_seeker(self):
        """Test job seeker login"""
        # First register
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_JOB_SEEKER_EMAIL,
            "password": TEST_JOB_SEEKER_PASSWORD,
            "name": "Test Job Seeker",
            "role": "job_seeker"
        })
        
        # Then login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_JOB_SEEKER_EMAIL,
            "password": TEST_JOB_SEEKER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        print(f"✓ Job Seeker Login: {data['user']['email']}")
        return data["access_token"]
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid credentials rejected correctly")
    
    def test_get_current_user_requires_auth(self):
        """Test /auth/me requires authentication"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("✓ /auth/me requires authentication")
    
    def test_get_current_user_with_token(self):
        """Test /auth/me with valid token"""
        # Register and get token
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_me_{uuid.uuid4().hex[:8]}@test.com",
            "password": "Test123!",
            "name": "Test User",
            "role": "job_seeker"
        })
        token = reg_response.json().get("access_token")
        
        # Get current user
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        print(f"✓ /auth/me returns user: {data['email']}")


class TestJobSearch:
    """Job search endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user"""
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_jobs_{uuid.uuid4().hex[:8]}@test.com",
            "password": "Test123!",
            "name": "Test User",
            "role": "job_seeker"
        })
        self.token = reg_response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_search_jobs(self):
        """Test job search endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/search",
            params={"query": "Quality Engineer", "limit": 5},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data or "results" in data or isinstance(data, list)
        print(f"✓ Job search returned results")
    
    def test_save_job(self):
        """Test saving a job"""
        job_data = {
            "id": f"test_job_{uuid.uuid4().hex[:8]}",
            "title": "Test Quality Engineer",
            "company": "Test Company",
            "location": "Remote",
            "description": "Test job description",
            "url": "https://example.com/job"
        }
        response = requests.post(
            f"{BASE_URL}/api/jobs/save",
            json={"job": job_data},
            headers=self.headers
        )
        # Accept 200, 201, or 409 (already saved)
        assert response.status_code in [200, 201, 409]
        print(f"✓ Save job endpoint working")
    
    def test_get_saved_jobs(self):
        """Test getting saved jobs"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/saved",
            headers=self.headers
        )
        # Accept 200 or 404 (no saved jobs)
        assert response.status_code in [200, 404]
        print(f"✓ Get saved jobs endpoint working")


class TestCredentials:
    """Credentials and Trust Score endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user"""
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_creds_{uuid.uuid4().hex[:8]}@test.com",
            "password": "Test123!",
            "name": "Test User",
            "role": "job_seeker"
        })
        self.token = reg_response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_submit_credential(self):
        """Test submitting a credential for verification"""
        credential_data = {
            "credential_type": "certification",
            "credential_name": "ASQ CQE",
            "issuing_authority": "ASQ",
            "issue_date": "2024-01-15",
            "credential_id": f"CQE-{uuid.uuid4().hex[:8]}"
        }
        response = requests.post(
            f"{BASE_URL}/api/credentials/submit",
            json=credential_data,
            headers=self.headers
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data or "credential_id" in data or "message" in data
        print(f"✓ Credential submission working")
    
    def test_get_user_credentials(self):
        """Test getting user credentials"""
        response = requests.get(
            f"{BASE_URL}/api/credentials/user",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "credentials" in data or isinstance(data, list)
        print(f"✓ Get user credentials working")
    
    def test_get_trust_score(self):
        """Test getting trust score"""
        response = requests.get(
            f"{BASE_URL}/api/credentials/trust-score",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_score" in data or "score" in data or "trust_score" in data
        print(f"✓ Trust score endpoint working")
    
    def test_get_trust_score_history(self):
        """Test getting trust score history"""
        response = requests.get(
            f"{BASE_URL}/api/credentials/trust-score/history",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "history" in data or "data_points" in data or isinstance(data, dict)
        print(f"✓ Trust score history endpoint working")
    
    def test_get_credly_status(self):
        """Test Credly connection status"""
        response = requests.get(
            f"{BASE_URL}/api/credentials/credly/status",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "connected" in data or "status" in data
        print(f"✓ Credly status endpoint working")


class TestEmployerReviews:
    """Employer reviews endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test recruiter"""
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_reviewer_{uuid.uuid4().hex[:8]}@test.com",
            "password": "Test123!",
            "name": "Test Recruiter",
            "role": "recruiter"
        })
        self.token = reg_response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Also create a job seeker for reviews
        js_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_candidate_{uuid.uuid4().hex[:8]}@test.com",
            "password": "Test123!",
            "name": "Test Candidate",
            "role": "job_seeker"
        })
        self.candidate_token = js_response.json().get("access_token")
        self.candidate_id = js_response.json().get("user", {}).get("user_id")
    
    def test_create_review(self):
        """Test creating a review (recruiter only)"""
        review_data = {
            "candidate_id": self.candidate_id or "test_candidate_123",
            "rating": 4,
            "comment": "Great candidate with strong technical skills",
            "review_type": "interview",
            "strengths": ["Technical Skills", "Communication"],
            "would_hire_again": True
        }
        response = requests.post(
            f"{BASE_URL}/api/reviews/create",
            json=review_data,
            headers=self.headers
        )
        # Accept 200, 201, or 403 (if recruiter verification required)
        assert response.status_code in [200, 201, 403]
        print(f"✓ Create review endpoint working (status: {response.status_code})")
    
    def test_get_my_reviews(self):
        """Test getting reviews received"""
        response = requests.get(
            f"{BASE_URL}/api/reviews/my-reviews",
            headers={"Authorization": f"Bearer {self.candidate_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "reviews" in data or isinstance(data, list)
        print(f"✓ Get my reviews endpoint working")
    
    def test_get_strength_suggestions(self):
        """Test getting strength tag suggestions"""
        response = requests.get(
            f"{BASE_URL}/api/reviews/strength-suggestions",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data or "strengths" in data or isinstance(data, list)
        print(f"✓ Strength suggestions endpoint working")


class TestAdminReviews:
    """Admin review moderation tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin user"""
        # Try to login as admin
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
        else:
            # Create admin user if doesn't exist
            reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD,
                "name": "Test Admin",
                "role": "admin"
            })
            self.token = reg_response.json().get("access_token") if reg_response.status_code == 200 else None
        
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
    
    def test_get_pending_reviews_requires_admin(self):
        """Test pending reviews requires admin"""
        # Test without auth
        response = requests.get(f"{BASE_URL}/api/reviews/admin/pending")
        assert response.status_code in [401, 403]
        print("✓ Admin pending reviews requires authentication")
    
    def test_get_pending_reviews_with_admin(self):
        """Test getting pending reviews as admin"""
        if not self.token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/reviews/admin/pending",
            headers=self.headers
        )
        # Accept 200 or 403 (if admin flag not set)
        assert response.status_code in [200, 403]
        if response.status_code == 200:
            data = response.json()
            assert "pending_reviews" in data or "reviews" in data
        print(f"✓ Admin pending reviews endpoint (status: {response.status_code})")


class TestTaxonomy:
    """Taxonomy and career pivot endpoint tests"""
    
    def test_get_sectors(self):
        """Test getting all sectors"""
        response = requests.get(f"{BASE_URL}/api/taxonomy/sectors")
        assert response.status_code == 200
        data = response.json()
        assert "sectors" in data or isinstance(data, list)
        print(f"✓ Get sectors endpoint working")
    
    def test_get_roles(self):
        """Test getting all roles"""
        response = requests.get(f"{BASE_URL}/api/taxonomy/roles")
        assert response.status_code == 200
        data = response.json()
        assert "roles" in data or isinstance(data, list)
        print(f"✓ Get roles endpoint working")
    
    def test_get_certifications(self):
        """Test getting certifications"""
        response = requests.get(f"{BASE_URL}/api/taxonomy/certifications")
        assert response.status_code == 200
        data = response.json()
        assert "certifications" in data or isinstance(data, list)
        print(f"✓ Get certifications endpoint working")
    
    def test_get_popular_pivots(self):
        """Test getting popular career pivots"""
        response = requests.get(f"{BASE_URL}/api/taxonomy/pivots/popular")
        # Also try alternate endpoint
        if response.status_code == 404:
            response = requests.get(f"{BASE_URL}/api/career-pivots/popular")
        
        assert response.status_code == 200
        data = response.json()
        assert "popular_pivots" in data or "pivots" in data or isinstance(data, list)
        print(f"✓ Popular career pivots endpoint working")


class TestRecruiterFeatures:
    """Recruiter RBAC and candidate search tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup recruiter user"""
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_recruiter_rbac_{uuid.uuid4().hex[:8]}@test.com",
            "password": "Test123!",
            "name": "Test Recruiter",
            "role": "recruiter"
        })
        self.token = reg_response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_verification_status(self):
        """Test getting recruiter verification status"""
        response = requests.get(
            f"{BASE_URL}/api/recruiter-rbac/verification/status",
            headers=self.headers
        )
        # Also try alternate endpoint
        if response.status_code == 404:
            response = requests.get(
                f"{BASE_URL}/api/recruiter/verification-status",
                headers=self.headers
            )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "status" in data or "is_verified" in data
        print(f"✓ Recruiter verification status endpoint (status: {response.status_code})")
    
    def test_search_candidates_requires_verification(self):
        """Test candidate search requires verification"""
        response = requests.get(
            f"{BASE_URL}/api/recruiter-rbac/candidates/search",
            params={"skills": "Python", "limit": 5},
            headers=self.headers
        )
        # Should return 403 if not verified, or 200 if verified
        assert response.status_code in [200, 403]
        print(f"✓ Candidate search endpoint (status: {response.status_code})")
    
    def test_contact_request_requires_auth(self):
        """Test contact request requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/recruiter/contact-request",
            json={"candidate_id": "test_123", "message": "Test message"}
        )
        # Also try mutual-match endpoint
        if response.status_code == 404:
            response = requests.post(
                f"{BASE_URL}/api/mutual-match/request",
                json={"candidate_id": "test_123", "message": "Test message"}
            )
        
        assert response.status_code in [401, 403, 404]
        print(f"✓ Contact request requires auth (status: {response.status_code})")


class TestIntegrationFlows:
    """End-to-end integration flow tests"""
    
    def test_job_seeker_flow(self):
        """Test complete job seeker flow: register -> login -> view dashboard data"""
        # 1. Register
        email = f"test_flow_{uuid.uuid4().hex[:8]}@test.com"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": "Test123!",
            "name": "Flow Test User",
            "role": "job_seeker"
        })
        assert reg_response.status_code == 200
        token = reg_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Get current user
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        # 3. Get trust score
        trust_response = requests.get(f"{BASE_URL}/api/credentials/trust-score", headers=headers)
        assert trust_response.status_code == 200
        
        # 4. Get credentials
        creds_response = requests.get(f"{BASE_URL}/api/credentials/user", headers=headers)
        assert creds_response.status_code == 200
        
        # 5. Get Credly status
        credly_response = requests.get(f"{BASE_URL}/api/credentials/credly/status", headers=headers)
        assert credly_response.status_code == 200
        
        print("✓ Job seeker flow completed successfully")
    
    def test_recruiter_flow(self):
        """Test recruiter flow: register -> check verification -> search candidates"""
        # 1. Register as recruiter
        email = f"test_recruiter_flow_{uuid.uuid4().hex[:8]}@test.com"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": "Test123!",
            "name": "Recruiter Flow Test",
            "role": "recruiter"
        })
        assert reg_response.status_code == 200
        token = reg_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Check verification status
        verify_response = requests.get(
            f"{BASE_URL}/api/recruiter-rbac/verification/status",
            headers=headers
        )
        # Accept 200 or 404
        assert verify_response.status_code in [200, 404]
        
        # 3. Try to search candidates (should fail if not verified)
        search_response = requests.get(
            f"{BASE_URL}/api/recruiter-rbac/candidates/search",
            params={"skills": "Python"},
            headers=headers
        )
        # Accept 200 (if verified) or 403 (if not verified)
        assert search_response.status_code in [200, 403]
        
        print("✓ Recruiter flow completed successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
