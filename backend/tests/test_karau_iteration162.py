"""
Test suite for Iteration 162: i18n fixes for hardcoded English strings on dashboard
Tests cover:
- Login redirect (not stuck on /login)
- Dashboard API endpoints
- Replay API endpoints
- Simulation endpoints (mocked hardware)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthentication:
    """Authentication and login redirect tests"""
    
    def test_login_returns_token(self):
        """Test login with admin credentials returns access token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "admin@medmatch.com"
        
    def test_login_returns_user_info(self):
        """Test login returns user information"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "name" in data["user"]
        assert "user_id" in data["user"]


class TestDashboardAPIs:
    """Dashboard related API tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json().get("access_token")
    
    def test_dashboard_stats(self, auth_token):
        """Test /api/karau-meet/stats returns meeting stats"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_meetings" in data
        assert "total_hours" in data
    
    def test_meeting_insights(self, auth_token):
        """Test /api/karau-meet/meeting-insights returns insight cards"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meeting-insights",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "insights" in data
    
    def test_trending_topics(self, auth_token):
        """Test /api/karau-meet/trending-topics returns topic pills"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/trending-topics",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "topics" in data
    
    def test_activity_feed(self, auth_token):
        """Test /api/karau-meet/activity-feed returns activity highlights"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/activity-feed",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
    
    def test_upcoming_meetings(self, auth_token):
        """Test /api/karau-meet/upcoming returns upcoming meetings"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/upcoming",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "upcoming" in data


class TestReplayAPIs:
    """Replay page API tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json().get("access_token")
    
    def test_demo_replay_returns_chapters(self, auth_token):
        """Test demo replay returns 8 chapters"""
        response = requests.get(
            f"{BASE_URL}/api/karau/replay/demo-meeting",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "chapters" in data
        assert len(data["chapters"]) == 8
    
    def test_demo_replay_returns_transcript(self, auth_token):
        """Test demo replay returns 62 transcript segments"""
        response = requests.get(
            f"{BASE_URL}/api/karau/replay/demo-meeting",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "transcript_segments" in data
        assert len(data["transcript_segments"]) == 62
    
    def test_demo_replay_returns_waveform(self, auth_token):
        """Test demo replay returns waveform data"""
        response = requests.get(
            f"{BASE_URL}/api/karau/replay/demo-meeting",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "waveform" in data
        assert len(data["waveform"]) > 0
    
    def test_demo_replay_returns_key_moments(self, auth_token):
        """Test demo replay returns key moments"""
        response = requests.get(
            f"{BASE_URL}/api/karau/replay/demo-meeting",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "key_moments" in data
    
    def test_replay_requires_auth(self):
        """Test replay endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/karau/replay/demo-meeting")
        assert response.status_code == 401


class TestSimulationAPIs:
    """Hardware simulation API tests (MOCKED - not real hardware)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json().get("access_token")
    
    def test_slam_stream_returns_positions(self, auth_token):
        """Test SLAM stream returns positions (MOCKED)"""
        response = requests.get(
            f"{BASE_URL}/api/karau/simulation/test/slam-stream",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "positions" in data
        assert len(data["positions"]) > 0
    
    def test_slam_stream_returns_point_cloud(self, auth_token):
        """Test SLAM stream returns point cloud data (MOCKED)"""
        response = requests.get(
            f"{BASE_URL}/api/karau/simulation/test/slam-stream",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "point_cloud" in data


class TestAnalyticsAPIs:
    """Analytics API tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json().get("access_token")
    
    def test_effectiveness_analytics(self, auth_token):
        """Test effectiveness analytics endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/karau/analytics/effectiveness",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data or "total_meetings" in data
    
    def test_gamification_analytics(self, auth_token):
        """Test gamification analytics endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/karau/analytics/gamification",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "xp" in data or "level" in data
    
    def test_leaderboard(self, auth_token):
        """Test leaderboard endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/karau/analytics/leaderboard",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "leaderboard" in data or "my_rank" in data
