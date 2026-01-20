"""
Test Suite for New Features (Iteration 21)
- PWA Install Prompt (frontend component)
- LinkedIn Profile Sync APIs
- Company Feedback Learning System APIs
- Resume Auto-Fill APIs
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestFeedbackAPIs:
    """Test Company Feedback Learning System APIs"""
    
    def test_feedback_categories_returns_10_categories(self):
        """GET /api/feedback/categories should return all 10 feedback categories"""
        response = requests.get(f"{BASE_URL}/api/feedback/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 10
        
        # Verify expected categories exist
        category_ids = [c["id"] for c in data["categories"]]
        expected_ids = ["skills_gap", "experience_mismatch", "culture_fit", "salary_mismatch", 
                       "overqualified", "underqualified", "location", "communication", "portfolio", "other"]
        for expected_id in expected_ids:
            assert expected_id in category_ids, f"Missing category: {expected_id}"
        
        # Verify structure
        for category in data["categories"]:
            assert "id" in category
            assert "name" in category
            assert "description" in category
    
    def test_feedback_insights_requires_auth(self):
        """GET /api/feedback/insights should require authentication"""
        response = requests.get(f"{BASE_URL}/api/feedback/insights")
        assert response.status_code == 401
    
    def test_feedback_insights_with_auth(self, auth_token):
        """GET /api/feedback/insights should return insights or 'no feedback' message"""
        response = requests.get(
            f"{BASE_URL}/api/feedback/insights",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Should have has_feedback field
        assert "has_feedback" in data
        
        if data["has_feedback"]:
            assert "insights" in data
            assert "total_applications_with_feedback" in data
        else:
            assert "message" in data
            assert "No feedback" in data["message"] or "Keep applying" in data["message"]
    
    def test_feedback_benchmarks_requires_auth(self):
        """GET /api/feedback/benchmarks should require authentication"""
        response = requests.get(f"{BASE_URL}/api/feedback/benchmarks")
        assert response.status_code == 401
    
    def test_feedback_benchmarks_with_auth(self, auth_token):
        """GET /api/feedback/benchmarks should return industry benchmarks"""
        response = requests.get(
            f"{BASE_URL}/api/feedback/benchmarks",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "has_data" in data
        
        if data["has_data"]:
            assert "benchmarks" in data
            assert "total_feedback_collected" in data
        else:
            assert "message" in data


class TestLinkedInAPIs:
    """Test LinkedIn Profile Sync APIs"""
    
    def test_linkedin_status_requires_auth(self):
        """GET /api/linkedin/status should require authentication"""
        response = requests.get(f"{BASE_URL}/api/linkedin/status")
        assert response.status_code == 401
    
    def test_linkedin_status_with_auth(self, auth_token):
        """GET /api/linkedin/status should return configuration status"""
        response = requests.get(
            f"{BASE_URL}/api/linkedin/status",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Should have integration_configured field
        assert "integration_configured" in data
        assert "user_connected" in data
        
        # Since no LinkedIn credentials are set, should be false
        assert data["integration_configured"] == False
        assert data["user_connected"] == False
    
    def test_linkedin_auth_url_returns_503_when_not_configured(self):
        """GET /api/linkedin/auth-url should return 503 when LinkedIn not configured"""
        response = requests.get(
            f"{BASE_URL}/api/linkedin/auth-url",
            params={"redirect_uri": "https://test.com/callback"}
        )
        # Should return 503 since LinkedIn credentials are not set
        assert response.status_code == 503
        
        data = response.json()
        assert "detail" in data
        assert "not configured" in data["detail"].lower()


class TestAutoFillAPIs:
    """Test Resume Auto-Fill APIs"""
    
    def test_autofill_data_requires_auth(self):
        """GET /api/autofill/data should require authentication"""
        response = requests.get(f"{BASE_URL}/api/autofill/data")
        assert response.status_code == 401
    
    def test_autofill_data_with_auth(self, auth_token):
        """GET /api/autofill/data should return parsed resume data for auto-fill"""
        response = requests.get(
            f"{BASE_URL}/api/autofill/data",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Should return 200 if user has resume, 404 if not
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "autofill_data" in data
            assert "fields_available" in data
            
            # Verify categories exist
            autofill_data = data["autofill_data"]
            assert "personal" in autofill_data
            assert "professional" in autofill_data
            assert "education" in autofill_data
            assert "skills" in autofill_data
            assert "work_history" in autofill_data
    
    def test_autofill_copy_ready_requires_auth(self):
        """GET /api/autofill/copy-ready should require authentication"""
        response = requests.get(f"{BASE_URL}/api/autofill/copy-ready")
        assert response.status_code == 401
    
    def test_autofill_copy_ready_with_auth(self, auth_token):
        """GET /api/autofill/copy-ready should return formatted resume data"""
        response = requests.get(
            f"{BASE_URL}/api/autofill/copy-ready",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Should return 200 if user has resume, 404 if not
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "sections" in data
            
            sections = data["sections"]
            assert "contact_info" in sections
            assert "professional_summary" in sections
            assert "skills_text" in sections
            assert "education_text" in sections
            assert "experience_text" in sections


class TestRecruiterFeedbackSubmission:
    """Test recruiter feedback submission (requires recruiter role)"""
    
    def test_rejection_feedback_requires_auth(self):
        """POST /api/feedback/rejection should require authentication"""
        response = requests.post(
            f"{BASE_URL}/api/feedback/rejection",
            json={
                "application_id": "test_app_123",
                "candidate_id": "test_candidate_123",
                "job_id": "test_job_123",
                "feedback_type": "skills_gap"
            }
        )
        assert response.status_code == 401
    
    def test_rejection_feedback_requires_recruiter_role(self, auth_token):
        """POST /api/feedback/rejection should require recruiter role"""
        response = requests.post(
            f"{BASE_URL}/api/feedback/rejection",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "application_id": "test_app_123",
                "candidate_id": "test_candidate_123",
                "job_id": "test_job_123",
                "feedback_type": "skills_gap"
            }
        )
        # Admin user should get 403 (not a recruiter)
        assert response.status_code == 403


# ============== Fixtures ==============

@pytest.fixture
def auth_token():
    """Get authentication token for admin user"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": "admin@medmatch.com",
            "password": "MedMatch2026!"
        }
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture
def recruiter_token():
    """Get authentication token for recruiter user"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": "recruiter@medmatch-test.com",
            "password": "test123"
        }
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Recruiter authentication failed - skipping recruiter tests")
