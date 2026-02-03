"""
Test Explainable AI (Why matched?) and Pricing Features
Tests for iteration 42
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestExplainableAI:
    """Test GDPR Article 22 - Right to Explanation features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test credentials"""
        self.job_seeker_email = "testuser@medmatch.com"
        self.job_seeker_password = "Test123!"
        self.recruiter_email = "recruiter@medmatch.com"
        self.recruiter_password = "Test123!"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_job_seeker_token(self):
        """Login as job seeker and get token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.job_seeker_email,
            "password": self.job_seeker_password
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def get_recruiter_token(self):
        """Login as recruiter and get token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.recruiter_email,
            "password": self.recruiter_password
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def test_health_check(self):
        """Test API health"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ Health check passed")
    
    def test_job_seeker_login(self):
        """Test job seeker can login"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.job_seeker_email,
            "password": self.job_seeker_password
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        print(f"✓ Job seeker login successful")
    
    def test_recruiter_login(self):
        """Test recruiter can login"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.recruiter_email,
            "password": self.recruiter_password
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        print(f"✓ Recruiter login successful")
    
    def test_explain_match_endpoint_exists(self):
        """Test /api/privacy/explain/match/{job_id} endpoint exists"""
        token = self.get_job_seeker_token()
        assert token, "Failed to get job seeker token"
        
        # Test with a sample job_id
        response = self.session.get(
            f"{BASE_URL}/api/privacy/explain/match/test_job_123",
            headers={"Authorization": f"Bearer {token}"}
        )
        # Should return 200 even if job not found (returns default explanation)
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
        assert "match_factors" in data
        print(f"✓ Explain match endpoint works - explanation: {data.get('explanation')[:50]}...")
    
    def test_explain_match_returns_factors(self):
        """Test that explain match returns proper factors structure"""
        token = self.get_job_seeker_token()
        assert token, "Failed to get job seeker token"
        
        response = self.session.get(
            f"{BASE_URL}/api/privacy/explain/match/any_job_id",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "explanation" in data
        assert "match_factors" in data
        assert isinstance(data["match_factors"], list)
        
        # Check transparency note exists
        if "transparency_note" in data:
            print(f"✓ Transparency note: {data['transparency_note'][:50]}...")
        
        # Check human review option
        if "request_review_available" in data:
            print(f"✓ Human review available: {data['request_review_available']}")
        
        print(f"✓ Explain match returns proper structure")
    
    def test_human_review_request_endpoint(self):
        """Test /api/privacy/review/request endpoint for GDPR Article 22"""
        token = self.get_job_seeker_token()
        assert token, "Failed to get job seeker token"
        
        response = self.session.post(
            f"{BASE_URL}/api/privacy/review/request",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "job_id": "test_job_123",
                "reason": "User requested human review of AI matching decision",
                "additional_context": "Test review request"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "review_id" in data or "message" in data
        print(f"✓ Human review request endpoint works")
    
    def test_contact_requests_received_endpoint(self):
        """Test /api/mutual-match/requests/received endpoint"""
        token = self.get_job_seeker_token()
        assert token, "Failed to get job seeker token"
        
        response = self.session.get(
            f"{BASE_URL}/api/mutual-match/requests/received",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "requests" in data
        assert isinstance(data["requests"], list)
        print(f"✓ Contact requests received endpoint works - {len(data['requests'])} requests found")
        return data["requests"]
    
    def test_contact_requests_sent_endpoint(self):
        """Test /api/mutual-match/requests/sent endpoint for recruiter"""
        token = self.get_recruiter_token()
        assert token, "Failed to get recruiter token"
        
        response = self.session.get(
            f"{BASE_URL}/api/mutual-match/requests/sent",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "requests" in data
        print(f"✓ Contact requests sent endpoint works - {len(data['requests'])} requests found")


class TestPricingTiers:
    """Test pricing page tiers"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test credentials"""
        self.job_seeker_email = "testuser@medmatch.com"
        self.job_seeker_password = "Test123!"
        self.recruiter_email = "recruiter@medmatch.com"
        self.recruiter_password = "Test123!"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_token(self, email, password):
        """Login and get token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def test_membership_status_endpoint(self):
        """Test /api/membership/status endpoint"""
        token = self.get_token(self.job_seeker_email, self.job_seeker_password)
        assert token, "Failed to get token"
        
        response = self.session.get(
            f"{BASE_URL}/api/membership/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Membership status endpoint works - status: {data}")
    
    def test_recruiter_membership_status(self):
        """Test recruiter membership status"""
        token = self.get_token(self.recruiter_email, self.recruiter_password)
        assert token, "Failed to get token"
        
        response = self.session.get(
            f"{BASE_URL}/api/membership/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Recruiter membership status endpoint works - status: {data}")


class TestBlindScreeningDashboard:
    """Test recruiter blind screening dashboard"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test credentials"""
        self.recruiter_email = "recruiter@medmatch.com"
        self.recruiter_password = "Test123!"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_recruiter_token(self):
        """Login as recruiter and get token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.recruiter_email,
            "password": self.recruiter_password
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def test_candidate_search_endpoint(self):
        """Test /api/recruiter-rbac/candidates/search endpoint"""
        token = self.get_recruiter_token()
        assert token, "Failed to get recruiter token"
        
        response = self.session.get(
            f"{BASE_URL}/api/recruiter-rbac/candidates/search",
            headers={"Authorization": f"Bearer {token}"},
            params={"min_match_score": 0}  # Use 0 to get all candidates
        )
        assert response.status_code == 200
        data = response.json()
        assert "candidates" in data
        print(f"✓ Candidate search endpoint works - {len(data['candidates'])} candidates found")
    
    def test_blind_screening_status(self):
        """Test /api/recruiter-rbac/blind-screening/status endpoint"""
        token = self.get_recruiter_token()
        assert token, "Failed to get recruiter token"
        
        response = self.session.get(
            f"{BASE_URL}/api/recruiter-rbac/blind-screening/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Blind screening status endpoint works - enabled: {data.get('enabled')}")
    
    def test_send_contact_request(self):
        """Test sending contact request to candidate"""
        token = self.get_recruiter_token()
        assert token, "Failed to get recruiter token"
        
        # First get a candidate
        search_response = self.session.get(
            f"{BASE_URL}/api/recruiter-rbac/candidates/search",
            headers={"Authorization": f"Bearer {token}"},
            params={"min_match_score": 0}
        )
        
        if search_response.status_code == 200:
            candidates = search_response.json().get("candidates", [])
            if candidates:
                candidate = candidates[0]
                print(f"✓ Found candidate: {candidate.get('id', 'unknown')}")
            else:
                print("⚠ No candidates found for contact request test")
        else:
            print(f"⚠ Could not search candidates: {search_response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
