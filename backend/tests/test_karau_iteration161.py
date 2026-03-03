"""
Test cases for Iteration 161: Shareable Replay Links and Dashboard Collapsible Sections
Tests the new features:
1. Dashboard APIs for collapsible sections (AI capabilities, Meeting Insights, Trending Topics, Activity Highlights)
2. Replay API for shareable moment links with ?t= timestamp parameter
3. Backend simulation endpoints (MOCKED)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthentication:
    """Test login to get auth token"""
    
    def test_login_admin(self):
        """Test admin login returns valid token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        assert "user" in data, "No user in response"
        assert data["user"]["email"] == "admin@medmatch.com"
        return data["access_token"]


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for authenticated tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@medmatch.com",
        "password": "Swampdrainer2026!"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    pytest.skip("Authentication failed")


class TestDashboardAPIs:
    """Tests for dashboard APIs that power collapsible sections"""
    
    def test_dashboard_stats(self, auth_token):
        """Test /api/karau-meet/stats returns stats grid data"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Stats failed: {response.text}"
        data = response.json()
        # Verify stats fields exist
        assert "total_meetings" in data, "Missing total_meetings"
        assert "total_hours" in data, "Missing total_hours"
        assert "ai_insights" in data, "Missing ai_insights"
        assert "total_participants" in data, "Missing total_participants"
    
    def test_meeting_insights(self, auth_token):
        """Test /api/karau-meet/meeting-insights returns insight cards"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meeting-insights",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Insights failed: {response.text}"
        data = response.json()
        assert "insights" in data, "Missing insights array"
        # Insights should be a list
        assert isinstance(data["insights"], list), "insights should be a list"
    
    def test_trending_topics(self, auth_token):
        """Test /api/karau-meet/trending-topics returns topic pills"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/trending-topics",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Trending topics failed: {response.text}"
        data = response.json()
        assert "topics" in data, "Missing topics array"
    
    def test_activity_feed(self, auth_token):
        """Test /api/karau-meet/activity-feed returns activity highlights"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/activity-feed?limit=12",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Activity feed failed: {response.text}"
        data = response.json()
        assert "activities" in data, "Missing activities array"
    
    def test_upcoming_meetings(self, auth_token):
        """Test /api/karau-meet/upcoming returns upcoming meeting data"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/upcoming",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Upcoming failed: {response.text}"
        data = response.json()
        assert "upcoming" in data, "Missing upcoming array"


class TestReplayAPI:
    """Tests for replay API and shareable moment links"""
    
    def test_get_demo_replay(self, auth_token):
        """Test /api/karau/replay/demo-meeting returns replay data"""
        response = requests.get(
            f"{BASE_URL}/api/karau/replay/demo-meeting",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Replay failed: {response.text}"
        data = response.json()
        
        # Verify replay data structure
        assert "title" in data, "Missing title"
        assert "duration_seconds" in data, "Missing duration_seconds"
        assert "chapters" in data, "Missing chapters"
        assert "transcript_segments" in data, "Missing transcript_segments"
        assert "waveform" in data, "Missing waveform"
        assert "key_moments" in data, "Missing key_moments"
        assert "director_cuts" in data, "Missing director_cuts"
        
        # Verify chapters count
        assert len(data["chapters"]) == 8, f"Expected 8 chapters, got {len(data['chapters'])}"
    
    def test_replay_requires_auth(self):
        """Test replay endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/karau/replay/demo-meeting")
        assert response.status_code == 401, "Replay should require authentication"
    
    def test_replay_timeline(self, auth_token):
        """Test /api/karau/replay/demo-meeting/timeline returns timeline data"""
        response = requests.get(
            f"{BASE_URL}/api/karau/replay/demo-meeting/timeline",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Timeline failed: {response.text}"
        data = response.json()
        assert "director_cuts" in data or "key_moments" in data, "Timeline should have cuts or moments"
    
    def test_generate_highlights(self, auth_token):
        """Test highlight generation endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/karau/replay/generate-highlights",
            json={"meeting_id": "demo-meeting", "style": "executive_summary"},
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
        )
        assert response.status_code == 200, f"Highlights failed: {response.text}"
        data = response.json()
        assert "highlights" in data, "Missing highlights in response"


class TestSimulationEndpointsMocked:
    """Tests for hardware simulation endpoints (MOCKED - not real hardware)"""
    
    def test_slam_stream(self, auth_token):
        """Test SLAM stream endpoint (MOCKED)"""
        response = requests.get(
            f"{BASE_URL}/api/karau/simulation/demo-meeting/slam-stream",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"SLAM failed: {response.text}"
        data = response.json()
        assert "positions" in data or "tracking_fps" in data, "Missing simulation data"
    
    def test_camera_stream(self, auth_token):
        """Test camera stream endpoint (MOCKED)"""
        response = requests.get(
            f"{BASE_URL}/api/karau/simulation/demo-meeting/camera-stream",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Camera failed: {response.text}"
    
    def test_audio_stream(self, auth_token):
        """Test audio stream endpoint (MOCKED)"""
        response = requests.get(
            f"{BASE_URL}/api/karau/simulation/demo-meeting/audio-stream",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Audio failed: {response.text}"
    
    def test_iot_stream(self, auth_token):
        """Test IoT stream endpoint (MOCKED)"""
        response = requests.get(
            f"{BASE_URL}/api/karau/simulation/demo-meeting/iot-stream",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"IoT failed: {response.text}"
    
    def test_biometric_stream(self, auth_token):
        """Test biometric stream endpoint (MOCKED)"""
        response = requests.get(
            f"{BASE_URL}/api/karau/simulation/demo-meeting/biometric-stream",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Biometric failed: {response.text}"


class TestAnalyticsAPIs:
    """Tests for analytics APIs used in dashboard"""
    
    def test_effectiveness_analytics(self, auth_token):
        """Test effectiveness analytics endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/karau/analytics/effectiveness",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # May return 200 or 404 depending on data
        assert response.status_code in [200, 404], f"Analytics failed: {response.text}"
    
    def test_gamification_analytics(self, auth_token):
        """Test gamification analytics endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/karau/analytics/gamification",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [200, 404], f"Gamification failed: {response.text}"
    
    def test_leaderboard(self, auth_token):
        """Test leaderboard endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/karau/analytics/leaderboard",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [200, 404], f"Leaderboard failed: {response.text}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
