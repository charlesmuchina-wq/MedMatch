"""
Test KARAU Meeting Dashboard Stats and Activity Feed - Iteration 133
Tests the new /stats and /activity-feed endpoints that return real MongoDB data
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://lumi-productivity.preview.emergentagent.com').rstrip('/')

class TestKarauStatsAndActivityFeed:
    """Test /api/karau-meet/stats and /api/karau-meet/activity-feed endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login and get auth token"""
        login_resp = requests.post(f'{BASE_URL}/api/auth/login', json={
            'email': 'admin@medmatch.com',
            'password': 'Swampdrainer2026!'
        })
        if login_resp.status_code != 200:
            pytest.skip("Login failed - cannot test authenticated endpoints")
        self.token = login_resp.json().get('access_token')
        self.headers = {'Authorization': f'Bearer {self.token}'}

    # ===================== /api/karau-meet/stats TESTS =====================
    
    def test_stats_endpoint_returns_200(self):
        """Test that /stats endpoint returns 200 for authenticated user"""
        resp = requests.get(f'{BASE_URL}/api/karau-meet/stats', headers=self.headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        print("PASS: /stats returns 200")

    def test_stats_has_required_fields(self):
        """Test that /stats returns all required fields"""
        resp = requests.get(f'{BASE_URL}/api/karau-meet/stats', headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        
        required_fields = ['total_meetings', 'active_meetings', 'total_hours', 
                          'recordings', 'total_participants', 'ai_insights']
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        print(f"PASS: Stats has all required fields: {required_fields}")

    def test_stats_values_are_numeric(self):
        """Test that all stats values are numeric (int or float)"""
        resp = requests.get(f'{BASE_URL}/api/karau-meet/stats', headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        
        for key, value in data.items():
            assert isinstance(value, (int, float)), f"{key} is not numeric: {type(value)}"
        print("PASS: All stats values are numeric")

    def test_stats_returns_real_data_not_hardcoded(self):
        """Test that stats returns real MongoDB data (not hardcoded 24/48/12/156)"""
        resp = requests.get(f'{BASE_URL}/api/karau-meet/stats', headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        
        # Previous hardcoded values were: 24 meetings, 48 hours, 12 recordings, 156 participants
        # If we get different values, it means we're getting real data
        # We know from the MongoDB there are ~198 meetings
        
        total_meetings = data.get('total_meetings', 0)
        total_participants = data.get('total_participants', 0)
        
        # Check we're NOT getting the old hardcoded values
        assert total_meetings != 24, "Stats appears to still be hardcoded (24 meetings)"
        assert total_participants != 156, "Stats appears to still be hardcoded (156 participants)"
        
        print(f"PASS: Stats returns real data - {total_meetings} meetings, {total_participants} participants")

    def test_stats_requires_auth(self):
        """Test that /stats requires authentication"""
        resp = requests.get(f'{BASE_URL}/api/karau-meet/stats')
        assert resp.status_code in [401, 403], f"Expected 401/403 without auth, got {resp.status_code}"
        print("PASS: /stats requires authentication")

    # ===================== /api/karau-meet/activity-feed TESTS =====================

    def test_activity_feed_returns_200(self):
        """Test that /activity-feed returns 200"""
        resp = requests.get(f'{BASE_URL}/api/karau-meet/activity-feed', headers=self.headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        print("PASS: /activity-feed returns 200")

    def test_activity_feed_has_activities_array(self):
        """Test that /activity-feed returns activities array"""
        resp = requests.get(f'{BASE_URL}/api/karau-meet/activity-feed', headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        
        assert 'activities' in data, "Response missing 'activities' key"
        assert isinstance(data['activities'], list), "'activities' is not a list"
        print(f"PASS: Activity feed returns {len(data['activities'])} activities")

    def test_activity_feed_entry_has_required_fields(self):
        """Test that each activity entry has required fields"""
        resp = requests.get(f'{BASE_URL}/api/karau-meet/activity-feed?limit=5', headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        
        activities = data.get('activities', [])
        if len(activities) == 0:
            pytest.skip("No activities in feed to validate")
        
        required_fields = ['type', 'text', 'timestamp', 'meeting_id', 'icon']
        
        for activity in activities:
            for field in required_fields:
                assert field in activity, f"Activity missing field: {field}"
        
        print(f"PASS: All {len(activities)} activities have required fields")

    def test_activity_feed_types_are_valid(self):
        """Test that activity types are from expected set"""
        resp = requests.get(f'{BASE_URL}/api/karau-meet/activity-feed?limit=15', headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        
        valid_types = {'meeting_created', 'meeting_started', 'meeting_ended', 
                      'participant_joined', 'ai_insight'}
        
        activities = data.get('activities', [])
        found_types = set()
        
        for activity in activities:
            activity_type = activity.get('type')
            assert activity_type in valid_types, f"Invalid activity type: {activity_type}"
            found_types.add(activity_type)
        
        print(f"PASS: Found valid activity types: {found_types}")

    def test_activity_feed_respects_limit(self):
        """Test that limit parameter works"""
        resp = requests.get(f'{BASE_URL}/api/karau-meet/activity-feed?limit=3', headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        
        activities = data.get('activities', [])
        assert len(activities) <= 3, f"Expected <= 3 activities, got {len(activities)}"
        print(f"PASS: Limit=3 returned {len(activities)} activities")

    def test_activity_feed_requires_auth(self):
        """Test that /activity-feed requires authentication"""
        resp = requests.get(f'{BASE_URL}/api/karau-meet/activity-feed')
        assert resp.status_code in [401, 403], f"Expected 401/403 without auth, got {resp.status_code}"
        print("PASS: /activity-feed requires authentication")

    # ===================== DATA VERIFICATION TESTS =====================

    def test_stats_active_meetings_is_reasonable(self):
        """Test that active_meetings count is reasonable (0 to total_meetings)"""
        resp = requests.get(f'{BASE_URL}/api/karau-meet/stats', headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        
        active = data.get('active_meetings', 0)
        total = data.get('total_meetings', 0)
        
        assert active >= 0, f"active_meetings should be >= 0, got {active}"
        assert active <= total, f"active_meetings ({active}) should be <= total_meetings ({total})"
        print(f"PASS: active_meetings ({active}) is within valid range (0 to {total})")

    def test_activity_feed_has_meeting_created_events(self):
        """Test that activity feed includes meeting_created events"""
        resp = requests.get(f'{BASE_URL}/api/karau-meet/activity-feed?limit=20', headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        
        activities = data.get('activities', [])
        meeting_created = [a for a in activities if a.get('type') == 'meeting_created']
        
        assert len(meeting_created) > 0, "Expected at least one meeting_created event"
        print(f"PASS: Found {len(meeting_created)} meeting_created events")
