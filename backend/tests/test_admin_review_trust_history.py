"""
Admin Review Moderation & Trust Score History Tests
Tests for:
- GET /api/credentials/trust-score/history - Trust score history endpoint
- GET /api/reviews/admin/stats - Admin review statistics
- Admin access control for stats endpoint
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user credentials
TEST_JOBSEEKER_EMAIL = f"TEST_history_{uuid.uuid4().hex[:8]}@test.com"
TEST_JOBSEEKER_PASSWORD = "Test123!"
TEST_RECRUITER_EMAIL = f"TEST_recruiter_hist_{uuid.uuid4().hex[:8]}@test.com"
TEST_RECRUITER_PASSWORD = "Test123!"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def jobseeker_token(api_client):
    """Create and login job seeker user"""
    # Register job seeker
    register_response = api_client.post(f"{BASE_URL}/api/auth/register", json={
        "email": TEST_JOBSEEKER_EMAIL,
        "password": TEST_JOBSEEKER_PASSWORD,
        "name": "Test Job Seeker History",
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
    
    return login_response.json().get("token")


@pytest.fixture(scope="module")
def recruiter_token(api_client):
    """Create and login recruiter user (non-admin)"""
    # Register recruiter
    register_response = api_client.post(f"{BASE_URL}/api/auth/register", json={
        "email": TEST_RECRUITER_EMAIL,
        "password": TEST_RECRUITER_PASSWORD,
        "name": "Test Recruiter History",
        "role": "recruiter",
        "company_name": "Test Company"
    })
    
    if register_response.status_code not in [200, 201, 400]:
        pytest.fail(f"Failed to register recruiter: {register_response.text}")
    
    # Login
    login_response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_RECRUITER_EMAIL,
        "password": TEST_RECRUITER_PASSWORD
    })
    
    if login_response.status_code != 200:
        pytest.fail(f"Failed to login recruiter: {login_response.text}")
    
    return login_response.json().get("token")


class TestTrustScoreHistory:
    """Test trust score history endpoint"""
    
    def test_history_requires_auth(self, api_client):
        """GET /api/credentials/trust-score/history - Should require authentication"""
        response = api_client.get(f"{BASE_URL}/api/credentials/trust-score/history")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ Trust score history requires authentication")
    
    def test_history_default_period(self, api_client, jobseeker_token):
        """GET /api/credentials/trust-score/history - Default 90 days period"""
        response = api_client.get(
            f"{BASE_URL}/api/credentials/trust-score/history",
            headers={"Authorization": f"Bearer {jobseeker_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "user_id" in data, "Response should contain user_id"
        assert "period_days" in data, "Response should contain period_days"
        assert "data_points" in data, "Response should contain data_points"
        assert "history" in data, "Response should contain history array"
        assert "current_score" in data, "Response should contain current_score"
        assert "current_level" in data, "Response should contain current_level"
        assert "trend" in data, "Response should contain trend"
        
        # Default period should be 90 days
        assert data["period_days"] == 90, f"Expected 90 days, got {data['period_days']}"
        
        print(f"✓ Trust score history retrieved: {data['data_points']} data points, current score: {data['current_score']}")
    
    def test_history_custom_period_7_days(self, api_client, jobseeker_token):
        """GET /api/credentials/trust-score/history?days=7 - Custom 7 days period"""
        response = api_client.get(
            f"{BASE_URL}/api/credentials/trust-score/history?days=7",
            headers={"Authorization": f"Bearer {jobseeker_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["period_days"] == 7, f"Expected 7 days, got {data['period_days']}"
        
        print(f"✓ Trust score history (7 days): {data['data_points']} data points")
    
    def test_history_custom_period_365_days(self, api_client, jobseeker_token):
        """GET /api/credentials/trust-score/history?days=365 - Custom 365 days period"""
        response = api_client.get(
            f"{BASE_URL}/api/credentials/trust-score/history?days=365",
            headers={"Authorization": f"Bearer {jobseeker_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["period_days"] == 365, f"Expected 365 days, got {data['period_days']}"
        
        print(f"✓ Trust score history (365 days): {data['data_points']} data points")
    
    def test_history_trend_structure(self, api_client, jobseeker_token):
        """GET /api/credentials/trust-score/history - Verify trend structure"""
        response = api_client.get(
            f"{BASE_URL}/api/credentials/trust-score/history",
            headers={"Authorization": f"Bearer {jobseeker_token}"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        trend = data.get("trend", {})
        
        assert "change" in trend, "Trend should contain 'change'"
        assert "change_percentage" in trend, "Trend should contain 'change_percentage'"
        assert "direction" in trend, "Trend should contain 'direction'"
        assert trend["direction"] in ["up", "down", "stable"], f"Invalid direction: {trend['direction']}"
        
        print(f"✓ Trend structure verified: direction={trend['direction']}, change={trend['change']}")
    
    def test_history_generates_snapshot(self, api_client, jobseeker_token):
        """Calling trust-score endpoint should generate history snapshot"""
        # First call trust-score to generate a snapshot
        trust_response = api_client.get(
            f"{BASE_URL}/api/credentials/trust-score",
            headers={"Authorization": f"Bearer {jobseeker_token}"}
        )
        assert trust_response.status_code == 200, "Trust score call should succeed"
        
        # Now check history - should have at least one data point
        history_response = api_client.get(
            f"{BASE_URL}/api/credentials/trust-score/history?days=1",
            headers={"Authorization": f"Bearer {jobseeker_token}"}
        )
        
        assert history_response.status_code == 200
        data = history_response.json()
        
        # After calling trust-score, we should have at least one snapshot
        assert data["data_points"] >= 1, "Should have at least one data point after calling trust-score"
        
        print(f"✓ History snapshot generated: {data['data_points']} data points")


class TestAdminReviewStats:
    """Test admin review statistics endpoint"""
    
    def test_stats_requires_auth(self, api_client):
        """GET /api/reviews/admin/stats - Should require authentication"""
        response = api_client.get(f"{BASE_URL}/api/reviews/admin/stats")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}: {response.text}"
        print("✓ Admin stats requires authentication")
    
    def test_stats_requires_admin_role(self, api_client, jobseeker_token):
        """GET /api/reviews/admin/stats - Should require admin role (job seeker denied)"""
        response = api_client.get(
            f"{BASE_URL}/api/reviews/admin/stats",
            headers={"Authorization": f"Bearer {jobseeker_token}"}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("✓ Admin stats denied for job seeker")
    
    def test_stats_requires_admin_role_recruiter(self, api_client, recruiter_token):
        """GET /api/reviews/admin/stats - Should require admin role (recruiter denied)"""
        response = api_client.get(
            f"{BASE_URL}/api/reviews/admin/stats",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("✓ Admin stats denied for non-admin recruiter")


class TestAdminPendingReviews:
    """Test admin pending reviews endpoint"""
    
    def test_pending_requires_auth(self, api_client):
        """GET /api/reviews/admin/pending - Should require authentication"""
        response = api_client.get(f"{BASE_URL}/api/reviews/admin/pending")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}: {response.text}"
        print("✓ Admin pending reviews requires authentication")
    
    def test_pending_requires_admin_role(self, api_client, jobseeker_token):
        """GET /api/reviews/admin/pending - Should require admin role"""
        response = api_client.get(
            f"{BASE_URL}/api/reviews/admin/pending",
            headers={"Authorization": f"Bearer {jobseeker_token}"}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("✓ Admin pending reviews denied for non-admin")


class TestAdminApproveReject:
    """Test admin approve/reject endpoints"""
    
    def test_approve_requires_admin(self, api_client, recruiter_token):
        """POST /api/reviews/admin/approve/{id} - Should require admin role"""
        response = api_client.post(
            f"{BASE_URL}/api/reviews/admin/approve/test_review_id",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("✓ Admin approve denied for non-admin")
    
    def test_reject_requires_admin(self, api_client, recruiter_token):
        """POST /api/reviews/admin/reject/{id} - Should require admin role"""
        response = api_client.post(
            f"{BASE_URL}/api/reviews/admin/reject/test_review_id?reason=Test%20rejection",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("✓ Admin reject denied for non-admin")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
