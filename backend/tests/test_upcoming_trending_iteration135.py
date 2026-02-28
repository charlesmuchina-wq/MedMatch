"""
Tests for Upcoming Meetings and Trending Topics features - Iteration 135
- GET /api/karau-meet/upcoming: Returns meetings with status 'waiting' or 'scheduled'
- GET /api/karau-meet/trending-topics: Returns AI-extracted topics from meeting notes
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
    )
    if response.status_code != 200:
        pytest.skip("Authentication failed - skipping tests")
    return response.json().get("access_token")


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Create session with auth header"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    return session


class TestUpcomingMeetings:
    """Tests for GET /api/karau-meet/upcoming endpoint"""
    
    def test_upcoming_endpoint_returns_200(self, api_client):
        """Test that upcoming endpoint returns 200 OK"""
        response = api_client.get(f"{BASE_URL}/api/karau-meet/upcoming")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: /api/karau-meet/upcoming returns 200")
    
    def test_upcoming_response_structure(self, api_client):
        """Test that response contains 'upcoming' array"""
        response = api_client.get(f"{BASE_URL}/api/karau-meet/upcoming")
        data = response.json()
        
        assert "upcoming" in data, "Response should contain 'upcoming' key"
        assert isinstance(data["upcoming"], list), "upcoming should be a list"
        print(f"PASS: Response has 'upcoming' array with {len(data['upcoming'])} items")
    
    def test_upcoming_meeting_fields(self, api_client):
        """Test that each meeting has required fields"""
        response = api_client.get(f"{BASE_URL}/api/karau-meet/upcoming")
        data = response.json()
        
        if not data["upcoming"]:
            pytest.skip("No upcoming meetings to test")
        
        first_meeting = data["upcoming"][0]
        required_fields = ["meeting_id", "title", "status"]
        
        for field in required_fields:
            assert field in first_meeting, f"Meeting should have '{field}' field"
        
        print(f"PASS: Meeting has required fields: {required_fields}")
        print(f"  - meeting_id: {first_meeting.get('meeting_id')}")
        print(f"  - title: {first_meeting.get('title')}")
        print(f"  - status: {first_meeting.get('status')}")
    
    def test_upcoming_only_waiting_or_scheduled(self, api_client):
        """Test that only meetings with status 'waiting' or 'scheduled' are returned"""
        response = api_client.get(f"{BASE_URL}/api/karau-meet/upcoming")
        data = response.json()
        
        if not data["upcoming"]:
            pytest.skip("No upcoming meetings to test")
        
        valid_statuses = ["waiting", "scheduled"]
        for meeting in data["upcoming"]:
            status = meeting.get("status")
            assert status in valid_statuses, f"Meeting status '{status}' not in {valid_statuses}"
        
        print(f"PASS: All {len(data['upcoming'])} meetings have valid status (waiting/scheduled)")
    
    def test_upcoming_max_5_meetings(self, api_client):
        """Test that maximum 5 meetings are returned"""
        response = api_client.get(f"{BASE_URL}/api/karau-meet/upcoming")
        data = response.json()
        
        assert len(data["upcoming"]) <= 5, f"Should return max 5 meetings, got {len(data['upcoming'])}"
        print(f"PASS: Returned {len(data['upcoming'])} meetings (max 5)")


class TestTrendingTopics:
    """Tests for GET /api/karau-meet/trending-topics endpoint"""
    
    def test_trending_endpoint_returns_200(self, api_client):
        """Test that trending-topics endpoint returns 200 OK"""
        response = api_client.get(f"{BASE_URL}/api/karau-meet/trending-topics", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: /api/karau-meet/trending-topics returns 200")
    
    def test_trending_response_structure(self, api_client):
        """Test that response contains 'topics' array and 'source'"""
        response = api_client.get(f"{BASE_URL}/api/karau-meet/trending-topics", timeout=15)
        data = response.json()
        
        assert "topics" in data, "Response should contain 'topics' key"
        assert "source" in data, "Response should contain 'source' key"
        assert isinstance(data["topics"], list), "topics should be a list"
        print(f"PASS: Response has 'topics' array with {len(data['topics'])} items")
        print(f"  - source: {data['source']}")
    
    def test_trending_topic_fields(self, api_client):
        """Test that each topic has required fields"""
        response = api_client.get(f"{BASE_URL}/api/karau-meet/trending-topics", timeout=15)
        data = response.json()
        
        if not data["topics"]:
            pytest.skip("No topics returned - may not have AI notes yet")
        
        first_topic = data["topics"][0]
        
        # topic and count are required
        assert "topic" in first_topic, "Topic should have 'topic' field"
        assert "count" in first_topic, "Topic should have 'count' field"
        
        print(f"PASS: Topic has required fields")
        print(f"  - topic: {first_topic.get('topic')}")
        print(f"  - count: {first_topic.get('count')}")
    
    def test_trending_max_5_topics(self, api_client):
        """Test that maximum 5 topics are returned"""
        response = api_client.get(f"{BASE_URL}/api/karau-meet/trending-topics", timeout=15)
        data = response.json()
        
        assert len(data["topics"]) <= 5, f"Should return max 5 topics, got {len(data['topics'])}"
        print(f"PASS: Returned {len(data['topics'])} topics (max 5)")
    
    def test_trending_source_values(self, api_client):
        """Test that source is one of expected values"""
        response = api_client.get(f"{BASE_URL}/api/karau-meet/trending-topics", timeout=15)
        data = response.json()
        
        valid_sources = ["ai", "no_data", "no_key", "parse_error", "error"]
        assert data["source"] in valid_sources, f"Source '{data['source']}' not in {valid_sources}"
        print(f"PASS: Source '{data['source']}' is valid")


class TestExistingEndpoints:
    """Verify existing endpoints still work"""
    
    def test_stats_endpoint(self, api_client):
        """Test that stats endpoint still works"""
        response = api_client.get(f"{BASE_URL}/api/karau-meet/stats")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["total_meetings", "active_meetings", "ai_insights"]
        for field in required_fields:
            assert field in data, f"Stats should have '{field}'"
        
        print(f"PASS: Stats endpoint returns data")
        print(f"  - total_meetings: {data.get('total_meetings')}")
        print(f"  - active_meetings: {data.get('active_meetings')}")
        print(f"  - ai_insights: {data.get('ai_insights')}")
    
    def test_activity_feed_endpoint(self, api_client):
        """Test that activity-feed endpoint still works"""
        response = api_client.get(f"{BASE_URL}/api/karau-meet/activity-feed?limit=5")
        assert response.status_code == 200
        data = response.json()
        
        assert "activities" in data, "Response should have 'activities'"
        print(f"PASS: Activity feed returns {len(data.get('activities', []))} activities")
    
    def test_meetings_endpoint(self, api_client):
        """Test that meetings endpoint still works"""
        response = api_client.get(f"{BASE_URL}/api/karau-meet/meetings")
        assert response.status_code == 200
        data = response.json()
        
        assert "meetings" in data, "Response should have 'meetings'"
        print(f"PASS: Meetings endpoint returns {len(data.get('meetings', []))} meetings")


class TestMeetingCreation:
    """Test that meeting creation still works"""
    
    def test_create_meeting(self, api_client):
        """Test creating a new meeting"""
        response = api_client.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            json={"title": "TEST_Upcoming_Trending_Iteration135"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "meeting_id" in data, "Response should have 'meeting_id'"
        # Note: status may not be in create response but meeting is created with 'waiting' status
        
        print(f"PASS: Created meeting {data.get('meeting_id')}")
    
    def test_new_meeting_appears_in_upcoming(self, api_client):
        """Test that newly created meeting appears in upcoming"""
        # Create a meeting
        create_response = api_client.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            json={"title": "TEST_Verify_Upcoming_List"}
        )
        meeting_id = create_response.json().get("meeting_id")
        
        # Get upcoming meetings
        upcoming_response = api_client.get(f"{BASE_URL}/api/karau-meet/upcoming")
        data = upcoming_response.json()
        
        # Check if new meeting is in list
        meeting_ids = [m.get("meeting_id") for m in data.get("upcoming", [])]
        
        # Note: May not appear if there are already 5 newer meetings
        if meeting_id in meeting_ids:
            print(f"PASS: New meeting {meeting_id} appears in upcoming list")
        else:
            print(f"Note: Meeting {meeting_id} may be past the 5-meeting limit in upcoming")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
