"""
Employer Reviews System Tests
Tests for review creation, retrieval, trust score integration, and cache invalidation.
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user credentials
TEST_RECRUITER_EMAIL = f"TEST_recruiter_review_{uuid.uuid4().hex[:8]}@test.com"
TEST_RECRUITER_PASSWORD = "Test123!"
TEST_JOBSEEKER_EMAIL = f"TEST_jobseeker_review_{uuid.uuid4().hex[:8]}@test.com"
TEST_JOBSEEKER_PASSWORD = "Test123!"


class TestEmployerReviewsSetup:
    """Setup test users for review testing"""
    
    @pytest.fixture(scope="class")
    def recruiter_token(self, api_client):
        """Create and login recruiter user"""
        # Register recruiter
        register_response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_RECRUITER_EMAIL,
            "password": TEST_RECRUITER_PASSWORD,
            "name": "Test Recruiter",
            "role": "recruiter",
            "company_name": "Test Company Inc"
        })
        
        if register_response.status_code not in [200, 201, 400]:  # 400 if already exists
            pytest.fail(f"Failed to register recruiter: {register_response.text}")
        
        # Login
        login_response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_RECRUITER_EMAIL,
            "password": TEST_RECRUITER_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.fail(f"Failed to login recruiter: {login_response.text}")
        
        return login_response.json().get("token")
    
    @pytest.fixture(scope="class")
    def jobseeker_data(self, api_client):
        """Create and login job seeker user"""
        # Register job seeker
        register_response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_JOBSEEKER_EMAIL,
            "password": TEST_JOBSEEKER_PASSWORD,
            "name": "Test Job Seeker",
            "role": "job_seeker"
        })
        
        if register_response.status_code not in [200, 201, 400]:
            pytest.fail(f"Failed to register job seeker: {register_response.text}")
        
        # Login
        login_response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_JOBSEEKER_EMAIL,
            "password": TEST_JOBSEEKER_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.fail(f"Failed to login job seeker: {login_response.text}")
        
        data = login_response.json()
        return {
            "token": data.get("token"),
            "user_id": data.get("user", {}).get("user_id")
        }


class TestStrengthSuggestions:
    """Test strength/tag suggestions endpoint"""
    
    def test_get_strength_suggestions(self, api_client):
        """GET /api/reviews/strength-suggestions - Get predefined tags"""
        response = api_client.get(f"{BASE_URL}/api/reviews/strength-suggestions")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "strengths" in data, "Response should contain 'strengths'"
        assert "areas_for_improvement" in data, "Response should contain 'areas_for_improvement'"
        assert len(data["strengths"]) > 0, "Should have at least one strength suggestion"
        assert len(data["areas_for_improvement"]) > 0, "Should have at least one improvement suggestion"
        
        # Verify some expected strengths
        expected_strengths = ["Strong communication skills", "Technical expertise", "Problem solver"]
        for strength in expected_strengths:
            assert strength in data["strengths"], f"Expected strength '{strength}' not found"
        
        print(f"✓ Strength suggestions: {len(data['strengths'])} strengths, {len(data['areas_for_improvement'])} improvements")


class TestReviewCreation(TestEmployerReviewsSetup):
    """Test review creation by recruiters"""
    
    def test_create_review_requires_auth(self, api_client):
        """POST /api/reviews/create - Should require authentication"""
        response = api_client.post(f"{BASE_URL}/api/reviews/create", json={
            "candidate_id": "test_candidate",
            "rating": 5,
            "review_type": "interview"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Review creation requires authentication")
    
    def test_create_review_requires_recruiter_role(self, api_client, jobseeker_data):
        """POST /api/reviews/create - Should require recruiter role"""
        response = api_client.post(
            f"{BASE_URL}/api/reviews/create",
            json={
                "candidate_id": "test_candidate",
                "rating": 5,
                "review_type": "interview"
            },
            headers={"Authorization": f"Bearer {jobseeker_data['token']}"}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("✓ Review creation requires recruiter role")
    
    def test_create_review_success(self, api_client, recruiter_token, jobseeker_data):
        """POST /api/reviews/create - Recruiter can create review"""
        review_data = {
            "candidate_id": jobseeker_data["user_id"],
            "rating": 5,
            "review_type": "interview",
            "strengths": ["Strong communication skills", "Technical expertise"],
            "areas_for_improvement": ["Time management"],
            "comment": "Excellent candidate with strong technical skills and great communication.",
            "would_hire_again": True,
            "professionalism": 5,
            "communication": 5,
            "technical_skills": 4,
            "reliability": 5,
            "is_anonymous": False
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/reviews/create",
            json=review_data,
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Response should indicate success"
        assert "review_id" in data, "Response should contain review_id"
        assert "pending" in data.get("message", "").lower(), "Review should be pending approval"
        
        print(f"✓ Review created successfully: {data['review_id']}")
        return data["review_id"]
    
    def test_create_review_invalid_candidate(self, api_client, recruiter_token):
        """POST /api/reviews/create - Should fail for non-existent candidate"""
        response = api_client.post(
            f"{BASE_URL}/api/reviews/create",
            json={
                "candidate_id": "non_existent_user_id",
                "rating": 5,
                "review_type": "interview"
            },
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print("✓ Review creation fails for non-existent candidate")


class TestReviewRetrieval(TestEmployerReviewsSetup):
    """Test review retrieval endpoints"""
    
    def test_get_my_reviews_requires_auth(self, api_client):
        """GET /api/reviews/my-reviews - Should require authentication"""
        response = api_client.get(f"{BASE_URL}/api/reviews/my-reviews")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ My reviews requires authentication")
    
    def test_get_my_reviews_success(self, api_client, jobseeker_data):
        """GET /api/reviews/my-reviews - Job seeker can view their reviews"""
        response = api_client.get(
            f"{BASE_URL}/api/reviews/my-reviews",
            headers={"Authorization": f"Bearer {jobseeker_data['token']}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_reviews" in data, "Response should contain total_reviews"
        assert "approved_reviews" in data, "Response should contain approved_reviews"
        assert "pending_reviews" in data, "Response should contain pending_reviews"
        assert "reviews" in data, "Response should contain reviews list"
        
        print(f"✓ My reviews retrieved: {data['total_reviews']} total, {data['approved_reviews']} approved, {data['pending_reviews']} pending")
    
    def test_get_candidate_reviews_requires_auth(self, api_client, jobseeker_data):
        """GET /api/reviews/candidate/{id} - Should require authentication"""
        response = api_client.get(f"{BASE_URL}/api/reviews/candidate/{jobseeker_data['user_id']}")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Candidate reviews requires authentication")
    
    def test_get_candidate_reviews_success(self, api_client, recruiter_token, jobseeker_data):
        """GET /api/reviews/candidate/{id} - Get reviews for a candidate"""
        response = api_client.get(
            f"{BASE_URL}/api/reviews/candidate/{jobseeker_data['user_id']}",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "candidate_id" in data, "Response should contain candidate_id"
        assert "total_reviews" in data, "Response should contain total_reviews"
        assert "reviews" in data, "Response should contain reviews list"
        
        # Only approved reviews should be shown
        for review in data.get("reviews", []):
            assert review.get("status") == "approved", "Only approved reviews should be returned"
        
        print(f"✓ Candidate reviews retrieved: {data['total_reviews']} approved reviews")
    
    def test_get_reviews_given_requires_recruiter(self, api_client, jobseeker_data):
        """GET /api/reviews/given - Should require recruiter role"""
        response = api_client.get(
            f"{BASE_URL}/api/reviews/given",
            headers={"Authorization": f"Bearer {jobseeker_data['token']}"}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("✓ Reviews given requires recruiter role")
    
    def test_get_reviews_given_success(self, api_client, recruiter_token):
        """GET /api/reviews/given - Recruiter can view reviews they've given"""
        response = api_client.get(
            f"{BASE_URL}/api/reviews/given",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_given" in data, "Response should contain total_given"
        assert "reviews" in data, "Response should contain reviews list"
        
        print(f"✓ Reviews given retrieved: {data['total_given']} reviews")


class TestTrustScoreIntegration(TestEmployerReviewsSetup):
    """Test trust score calculation with reviews category"""
    
    def test_trust_score_requires_auth(self, api_client):
        """GET /api/credentials/trust-score - Should require authentication"""
        response = api_client.get(f"{BASE_URL}/api/credentials/trust-score")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Trust score requires authentication")
    
    def test_trust_score_includes_reviews_category(self, api_client, jobseeker_data):
        """GET /api/credentials/trust-score - Should include reviews category in breakdown"""
        response = api_client.get(
            f"{BASE_URL}/api/credentials/trust-score",
            headers={"Authorization": f"Bearer {jobseeker_data['token']}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_score" in data, "Response should contain total_score"
        assert "breakdown" in data, "Response should contain breakdown"
        
        breakdown = data.get("breakdown", {})
        assert "reviews" in breakdown, "Breakdown should include 'reviews' category"
        
        reviews_breakdown = breakdown.get("reviews", {})
        assert "points" in reviews_breakdown, "Reviews breakdown should have points"
        assert "details" in reviews_breakdown, "Reviews breakdown should have details"
        
        print(f"✓ Trust score includes reviews category: {reviews_breakdown.get('points', 0)} points")
    
    def test_trust_score_structure(self, api_client, jobseeker_data):
        """GET /api/credentials/trust-score - Verify complete response structure"""
        response = api_client.get(
            f"{BASE_URL}/api/credentials/trust-score",
            headers={"Authorization": f"Bearer {jobseeker_data['token']}"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        required_fields = ["user_id", "total_score", "max_score", "percentage", "level", "breakdown", "calculated_at"]
        for field in required_fields:
            assert field in data, f"Response should contain '{field}'"
        
        # Check level structure
        level = data.get("level", {})
        assert "name" in level, "Level should have name"
        assert "color" in level, "Level should have color"
        
        # Check breakdown categories
        breakdown = data.get("breakdown", {})
        expected_categories = ["credentials", "profile", "engagement", "tenure", "reviews"]
        for category in expected_categories:
            assert category in breakdown, f"Breakdown should include '{category}'"
        
        print(f"✓ Trust score structure verified: {data['total_score']}/{data['max_score']} ({data['percentage']}%)")


class TestAdminModeration:
    """Test admin moderation endpoints (requires admin user)"""
    
    def test_pending_reviews_requires_admin(self, api_client):
        """GET /api/reviews/admin/pending - Should require admin access"""
        # Without auth
        response = api_client.get(f"{BASE_URL}/api/reviews/admin/pending")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Pending reviews requires admin access")
    
    def test_approve_review_requires_admin(self, api_client):
        """POST /api/reviews/admin/approve/{id} - Should require admin access"""
        response = api_client.post(f"{BASE_URL}/api/reviews/admin/approve/test_review_id")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Approve review requires admin access")


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
