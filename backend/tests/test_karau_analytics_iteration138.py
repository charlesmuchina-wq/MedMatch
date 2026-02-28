"""
KARAU Analytics API Tests - Iteration 138
Tests for meeting effectiveness, gamification, and participation analytics endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestKarauAnalyticsAPI:
    """Test suite for KARAU analytics endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_effectiveness_endpoint_returns_200(self):
        """Test /api/karau/analytics/effectiveness returns valid response"""
        response = requests.get(
            f"{BASE_URL}/api/karau/analytics/effectiveness",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Verify response structure
        assert "overall_score" in data
        assert "avg_duration_minutes" in data
        assert "avg_participants" in data
        assert "meetings_with_notes" in data
        assert "meetings_with_action_items" in data
        assert "total_meetings" in data
        assert "on_time_rate" in data
        assert "engagement_level" in data
        assert "tip" in data
        
        # Validate data types
        assert isinstance(data["overall_score"], int)
        assert isinstance(data["avg_duration_minutes"], (int, float))
        assert isinstance(data["avg_participants"], (int, float))
        assert data["engagement_level"] in ["Low", "Medium", "High"]
        print(f"Effectiveness Score: {data['overall_score']}, Engagement: {data['engagement_level']}")
    
    def test_gamification_endpoint_returns_200(self):
        """Test /api/karau/analytics/gamification returns valid response"""
        response = requests.get(
            f"{BASE_URL}/api/karau/analytics/gamification",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Verify response structure
        assert "level" in data
        assert "xp" in data
        assert "xp_to_next" in data
        assert "streak_days" in data
        assert "badges" in data
        assert "rank_title" in data
        assert "total_meetings" in data
        assert "total_hours" in data
        
        # Validate data types
        assert isinstance(data["level"], int)
        assert isinstance(data["xp"], int)
        assert isinstance(data["badges"], list)
        assert isinstance(data["rank_title"], str)
        print(f"Level: {data['level']}, XP: {data['xp']}, Rank: {data['rank_title']}")
    
    def test_participation_endpoint_returns_200(self):
        """Test /api/karau/analytics/participation returns valid response"""
        response = requests.get(
            f"{BASE_URL}/api/karau/analytics/participation",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Verify response structure
        assert "total_meetings_attended" in data
        assert "total_meetings_hosted" in data
        assert "total_hours" in data
        assert "avg_meeting_duration" in data
        assert "busiest_day" in data
        assert "busiest_hour" in data
        assert "meetings_by_day" in data
        assert "weekly_trend" in data
        
        # Validate data types
        assert isinstance(data["total_meetings_attended"], int)
        assert isinstance(data["meetings_by_day"], dict)
        assert isinstance(data["weekly_trend"], list)
        print(f"Hosted: {data['total_meetings_hosted']}, Attended: {data['total_meetings_attended']}")
    
    def test_effectiveness_requires_auth(self):
        """Test effectiveness endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/karau/analytics/effectiveness")
        assert response.status_code in [401, 403], "Should require auth"
    
    def test_gamification_requires_auth(self):
        """Test gamification endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/karau/analytics/gamification")
        assert response.status_code in [401, 403], "Should require auth"


class TestKarauMeetAPI:
    """Test suite for KARAU Meet base endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Login failed")
    
    def test_stats_endpoint(self):
        """Test /api/karau-meet/stats returns meeting statistics"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/stats",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_meetings" in data
        assert "total_hours" in data
        assert "recordings" in data
        print(f"Stats: {data['total_meetings']} meetings, {data['total_hours']} hours")
    
    def test_upcoming_meetings_endpoint(self):
        """Test /api/karau-meet/upcoming returns upcoming meetings"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/upcoming",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "upcoming" in data
        assert isinstance(data["upcoming"], list)
        print(f"Upcoming meetings: {len(data['upcoming'])}")
    
    def test_trending_topics_endpoint(self):
        """Test /api/karau-meet/trending-topics returns AI-extracted topics"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/trending-topics",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "topics" in data
        print(f"Trending topics: {len(data['topics'])}")
    
    def test_activity_feed_endpoint(self):
        """Test /api/karau-meet/activity-feed returns activity items"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/activity-feed?limit=10",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
        print(f"Activities: {len(data['activities'])}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
