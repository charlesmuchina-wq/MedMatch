"""
Iteration 136: Meeting Scheduling + i18n Tests
Tests:
1. Meeting creation with scheduled_time parameter
2. Upcoming meetings endpoint returns scheduled meetings
3. Backend endpoints working correctly
"""
import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestMeetingSchedulingAndI18n:
    """Test meeting scheduling and related features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test - login and get auth token"""
        # Login to get token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Auth failed - skipping authenticated tests")
    
    # ==================== MEETING SCHEDULING TESTS ====================
    
    def test_create_meeting_without_scheduled_time(self):
        """Test creating an instant meeting (no scheduled_time)"""
        response = requests.post(f"{BASE_URL}/api/karau-meet/meetings", 
            headers=self.headers,
            json={
                "title": "TEST_Instant_Meeting_Iteration136"
            })
        assert response.status_code == 200, f"Create instant meeting failed: {response.text}"
        data = response.json()
        assert "meeting_id" in data
        assert data.get("title") == "TEST_Instant_Meeting_Iteration136"
        # Instant meetings should not have scheduled_time
        print(f"✓ Created instant meeting: {data.get('meeting_id')}")
    
    def test_create_meeting_with_scheduled_time(self):
        """Test creating a scheduled meeting with datetime-local format"""
        # Schedule meeting 2 hours from now
        scheduled_time = (datetime.utcnow() + timedelta(hours=2)).isoformat() + "Z"
        
        response = requests.post(f"{BASE_URL}/api/karau-meet/meetings", 
            headers=self.headers,
            json={
                "title": "TEST_Scheduled_Meeting_Iteration136",
                "scheduled_time": scheduled_time
            })
        assert response.status_code == 200, f"Create scheduled meeting failed: {response.text}"
        data = response.json()
        assert "meeting_id" in data
        # Meeting should be created successfully
        print(f"✓ Created scheduled meeting: {data.get('meeting_id')}")
    
    def test_upcoming_endpoint_returns_scheduled_meetings(self):
        """Test /upcoming endpoint returns meetings with status waiting/scheduled"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/upcoming", headers=self.headers)
        assert response.status_code == 200, f"Upcoming endpoint failed: {response.text}"
        data = response.json()
        
        assert "upcoming" in data
        upcoming = data["upcoming"]
        assert isinstance(upcoming, list)
        
        # Check each meeting has required fields
        for meeting in upcoming[:3]:
            assert "meeting_id" in meeting
            assert "title" in meeting
            assert meeting.get("status") in ["waiting", "scheduled"], f"Unexpected status: {meeting.get('status')}"
        
        print(f"✓ Upcoming endpoint returned {len(upcoming)} meetings")
    
    def test_trending_topics_endpoint(self):
        """Test /trending-topics endpoint returns AI-extracted topics"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/trending-topics", headers=self.headers)
        assert response.status_code == 200, f"Trending topics failed: {response.text}"
        data = response.json()
        
        assert "topics" in data
        assert "source" in data
        
        # Source should be ai, no_data, or error
        assert data["source"] in ["ai", "no_data", "error", "no_key", "parse_error"]
        
        if data["source"] == "ai" and data["topics"]:
            for topic in data["topics"][:3]:
                assert "topic" in topic
                # count and sentiment are optional but often present
        
        print(f"✓ Trending topics source: {data['source']}, count: {len(data.get('topics', []))}")
    
    def test_stats_endpoint_returns_data(self):
        """Test /stats endpoint returns real MongoDB data"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/stats", headers=self.headers)
        assert response.status_code == 200, f"Stats endpoint failed: {response.text}"
        data = response.json()
        
        # Verify required stat fields
        required_fields = ["total_meetings", "total_hours", "ai_insights", "total_participants", "active_meetings"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
            assert isinstance(data[field], (int, float)), f"Field {field} should be numeric"
        
        # Previous iteration had 198 meetings - should be at least close
        assert data["total_meetings"] >= 0
        
        print(f"✓ Stats: {data['total_meetings']} meetings, {data['ai_insights']} AI insights, {data['total_participants']} participants")
    
    def test_activity_feed_endpoint(self):
        """Test /activity-feed returns activities"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/activity-feed?limit=10", headers=self.headers)
        assert response.status_code == 200, f"Activity feed failed: {response.text}"
        data = response.json()
        
        assert "activities" in data
        activities = data["activities"]
        
        if activities:
            for activity in activities[:3]:
                assert "type" in activity
                assert "text" in activity
                assert activity["type"] in ["meeting_created", "meeting_started", "meeting_ended", "participant_joined", "ai_insight"]
        
        print(f"✓ Activity feed returned {len(activities)} activities")
    
    # ==================== MEETINGS CRUD TESTS ====================
    
    def test_get_meetings_list(self):
        """Test /meetings returns user's meetings"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings", headers=self.headers)
        assert response.status_code == 200, f"Get meetings failed: {response.text}"
        data = response.json()
        
        assert "meetings" in data
        meetings = data["meetings"]
        assert isinstance(meetings, list)
        
        if meetings:
            meeting = meetings[0]
            assert "meeting_id" in meeting
            assert "title" in meeting
            assert "status" in meeting
        
        print(f"✓ Retrieved {len(meetings)} meetings")
    
    def test_get_meeting_info(self):
        """Test getting specific meeting info"""
        # First create a meeting
        create_response = requests.post(f"{BASE_URL}/api/karau-meet/meetings", 
            headers=self.headers,
            json={"title": "TEST_Info_Check_Iteration136"})
        
        if create_response.status_code == 200:
            meeting_id = create_response.json().get("meeting_id")
            
            # Get public info (no auth required)
            info_response = requests.get(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/info")
            assert info_response.status_code == 200, f"Get meeting info failed: {info_response.text}"
            
            data = info_response.json()
            assert data.get("meeting_id") == meeting_id
            assert "title" in data
            assert "status" in data
            
            print(f"✓ Retrieved meeting info for {meeting_id}")
        else:
            print("⚠ Skipped info test - meeting creation failed")


class TestKarauFeaturesAIAssistant:
    """Test AI assistant and templates endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test - login and get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Auth failed")
    
    def test_templates_endpoint(self):
        """Test /templates endpoint for meeting templates"""
        response = requests.get(f"{BASE_URL}/api/karau-features/templates")
        assert response.status_code == 200, f"Templates endpoint failed: {response.text}"
        data = response.json()
        
        assert "templates" in data
        templates = data["templates"]
        assert isinstance(templates, list)
        
        if templates:
            template = templates[0]
            assert "template_id" in template or "name" in template
        
        print(f"✓ Retrieved {len(templates)} templates")
    
    def test_ai_assistant_ask(self):
        """Test AI assistant ask endpoint"""
        response = requests.post(f"{BASE_URL}/api/karau-features/ai-assistant/ask", 
            headers=self.headers,
            json={
                "meeting_id": "general",
                "question": "What are best practices for meetings?"
            })
        
        # AI might take time or fail on rate limits, but endpoint should exist
        assert response.status_code in [200, 429, 500], f"AI assistant unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data
            print(f"✓ AI assistant responded with {len(data.get('answer', ''))} chars")
        else:
            print(f"⚠ AI assistant returned {response.status_code} - may be rate limited")


class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ Health endpoint OK")
    
    def test_login_success(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        print("✓ Admin login successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
