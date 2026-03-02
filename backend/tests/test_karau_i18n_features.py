"""
Test Suite for AI KARAU i18n Features, Meeting Insights, and How-To Guide
Tests for iteration 158 features:
- i18n translation support
- Meeting Insights API
- Dashboard endpoints
- Upcoming meetings API
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestAuth:
    """Authentication endpoint tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        return data["access_token"]
    
    def test_login_success(self):
        """Test successful login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "admin@medmatch.com"
        print("PASS: Login successful")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpass"
        })
        assert response.status_code in [401, 400]
        print("PASS: Invalid login returns error")


class TestMeetingInsights:
    """Meeting Insights API tests for dashboard card"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json().get("access_token")
    
    def test_meeting_insights_endpoint(self, auth_token):
        """Test GET /api/karau-meet/meeting-insights returns insights data"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meeting-insights",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "insights" in data
        assert isinstance(data["insights"], list)
        print(f"PASS: Meeting insights returns {len(data['insights'])} insights")
    
    def test_meeting_insights_structure(self, auth_token):
        """Test that insights contain expected fields"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meeting-insights",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        if len(data["insights"]) > 0:
            insight = data["insights"][0]
            expected_fields = ["meeting_id", "title", "host_name", "summary", "key_decisions", "action_items"]
            for field in expected_fields:
                assert field in insight, f"Missing field: {field}"
            print("PASS: Insights contain all expected fields")
        else:
            print("SKIP: No insights to validate structure")
    
    def test_meeting_insights_unauthorized(self):
        """Test meeting insights requires authentication"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/meeting-insights")
        assert response.status_code in [401, 403]
        print("PASS: Meeting insights requires auth")


class TestUpcomingMeetings:
    """Upcoming meetings API tests for dashboard"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json().get("access_token")
    
    def test_upcoming_meetings_endpoint(self, auth_token):
        """Test GET /api/karau-meet/upcoming returns upcoming meetings"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/upcoming",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "upcoming" in data
        assert isinstance(data["upcoming"], list)
        print(f"PASS: Upcoming meetings returns {len(data['upcoming'])} meetings")
    
    def test_upcoming_meetings_structure(self, auth_token):
        """Test upcoming meetings contain expected fields"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/upcoming",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        
        if len(data["upcoming"]) > 0:
            meeting = data["upcoming"][0]
            expected_fields = ["meeting_id", "title", "status"]
            for field in expected_fields:
                assert field in meeting, f"Missing field: {field}"
            print("PASS: Upcoming meetings contain expected fields")
        else:
            print("SKIP: No upcoming meetings to validate")


class TestDashboardStats:
    """Dashboard stats API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json().get("access_token")
    
    def test_stats_endpoint(self, auth_token):
        """Test GET /api/karau-meet/stats returns dashboard stats"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        expected_fields = ["total_meetings", "total_hours", "total_participants", "ai_insights"]
        for field in expected_fields:
            assert field in data, f"Missing stat field: {field}"
        
        print(f"PASS: Stats endpoint returns all expected fields")
        print(f"  - total_meetings: {data.get('total_meetings')}")
        print(f"  - total_hours: {data.get('total_hours')}")
        print(f"  - ai_insights: {data.get('ai_insights')}")


class TestActivityFeed:
    """Activity feed API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json().get("access_token")
    
    def test_activity_feed_endpoint(self, auth_token):
        """Test GET /api/karau-meet/activity-feed returns activities"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/activity-feed",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
        assert isinstance(data["activities"], list)
        print(f"PASS: Activity feed returns {len(data['activities'])} activities")


class TestTrendingTopics:
    """Trending topics API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json().get("access_token")
    
    def test_trending_topics_endpoint(self, auth_token):
        """Test GET /api/karau-meet/trending-topics returns topics"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/trending-topics",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "topics" in data
        print(f"PASS: Trending topics endpoint works, {len(data.get('topics', []))} topics found")


class TestMeetingsCRUD:
    """Meetings CRUD operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json().get("access_token")
    
    def test_get_meetings(self, auth_token):
        """Test GET /api/karau-meet/meetings returns user meetings"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "meetings" in data
        print(f"PASS: Get meetings returns {len(data['meetings'])} meetings")
    
    def test_create_meeting(self, auth_token):
        """Test POST /api/karau-meet/meetings creates a new meeting"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={"title": "TEST_i18n_Meeting"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "meeting_id" in data
        print(f"PASS: Created meeting with ID: {data['meeting_id']}")
        return data["meeting_id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
