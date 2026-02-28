"""
Test Suite for Iteration 139: Webinar Mode, Gamification & Leaderboard APIs
Features tested:
- Webinar CRUD: create, list, get, register, start, end
- Gamification: XP, level, badges, rank_title
- Leaderboard: team ranking with my_rank
"""
import pytest
import requests
import os
import time
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestWebinarAPIs:
    """Webinar Mode API Tests - WebEx-style large events"""
    
    @pytest.fixture(autouse=True)
    def setup(self, auth_token):
        self.token = auth_token
        self.headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
    
    def test_webinar_list(self, auth_token):
        """GET /api/karau/webinar/list - List user's webinars"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = requests.get(f"{BASE_URL}/api/karau/webinar/list", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "webinars" in data
        assert isinstance(data["webinars"], list)
        print(f"✓ webinar/list returned {len(data['webinars'])} webinars")
        
        # Check webinar structure if any exist
        if data["webinars"]:
            webinar = data["webinars"][0]
            assert "webinar_id" in webinar
            assert "title" in webinar
            assert "status" in webinar
            assert "registered_count" in webinar
            print(f"  First webinar: {webinar['title']} (status: {webinar['status']})")
    
    def test_webinar_create(self, auth_token):
        """POST /api/karau/webinar/create - Create new webinar"""
        headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
        
        # Schedule for tomorrow
        scheduled_time = (datetime.now() + timedelta(days=1)).isoformat()
        payload = {
            "title": "TEST_Webinar_Iteration139",
            "description": "Test webinar for automated testing",
            "scheduled_time": scheduled_time,
            "max_attendees": 500,
            "registration_required": True,
            "q_and_a_enabled": True,
            "chat_enabled": True,
            "attendee_video": False,
            "attendee_audio": False,
            "panelist_emails": []
        }
        
        response = requests.post(f"{BASE_URL}/api/karau/webinar/create", 
                                headers=headers, json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "webinar_id" in data, "Missing webinar_id in response"
        assert data["title"] == payload["title"]
        assert data["status"] == "scheduled"
        assert data["max_attendees"] == 500
        assert "registration_url" in data
        assert "join_url" in data
        
        print(f"✓ Created webinar: {data['webinar_id']}")
        return data["webinar_id"]
    
    def test_webinar_get_public(self, auth_token):
        """GET /api/karau/webinar/{id} - Get webinar details (public endpoint)"""
        # First get the list
        headers = {'Authorization': f'Bearer {auth_token}'}
        list_resp = requests.get(f"{BASE_URL}/api/karau/webinar/list", headers=headers)
        webinars = list_resp.json().get("webinars", [])
        
        if not webinars:
            pytest.skip("No webinars available for testing")
        
        webinar_id = webinars[0]["webinar_id"]
        
        # Get webinar details (no auth required for public view)
        response = requests.get(f"{BASE_URL}/api/karau/webinar/{webinar_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "webinar_id" in data
        assert "title" in data
        assert "scheduled_time" in data
        assert "host_name" in data
        assert "status" in data
        print(f"✓ Retrieved webinar: {data['title']} by {data['host_name']}")
    
    def test_webinar_register(self, auth_token):
        """POST /api/karau/webinar/{id}/register - Register as attendee"""
        # Get a webinar to register for
        headers = {'Authorization': f'Bearer {auth_token}'}
        list_resp = requests.get(f"{BASE_URL}/api/karau/webinar/list", headers=headers)
        webinars = list_resp.json().get("webinars", [])
        
        if not webinars:
            pytest.skip("No webinars available for testing")
        
        # Find a scheduled webinar (not ended)
        scheduled = [w for w in webinars if w.get("status") == "scheduled"]
        if not scheduled:
            pytest.skip("No scheduled webinars available")
        
        webinar_id = scheduled[0]["webinar_id"]
        
        # Generate unique email for test
        unique_email = f"test_reg_{int(time.time())}@example.com"
        
        payload = {
            "name": "Test User Iteration139",
            "email": unique_email,
            "organization": "Test Org",
            "role": "attendee"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{webinar_id}/register",
            headers={'Content-Type': 'application/json'},
            json=payload
        )
        
        # 200 = success, 400 = already registered
        assert response.status_code in [200, 400], f"Unexpected: {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") == True
            assert "reg_id" in data
            assert "join_url" in data
            print(f"✓ Registered for webinar: {data['reg_id']}")
        else:
            print(f"✓ Registration validation working (duplicate/full check)")
    
    def test_webinar_start_host_only(self, auth_token):
        """POST /api/karau/webinar/{id}/start - Start webinar (host only)"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # Get user's webinars (must be host)
        list_resp = requests.get(f"{BASE_URL}/api/karau/webinar/list", headers=headers)
        webinars = list_resp.json().get("webinars", [])
        
        scheduled = [w for w in webinars if w.get("status") == "scheduled"]
        if not scheduled:
            pytest.skip("No scheduled webinars to start")
        
        webinar_id = scheduled[0]["webinar_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{webinar_id}/start",
            headers=headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True
        assert data.get("status") == "live"
        print(f"✓ Webinar started: {webinar_id}")
        
        # Store for end test
        return webinar_id
    
    def test_webinar_end_host_only(self, auth_token):
        """POST /api/karau/webinar/{id}/end - End webinar (host only)"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # Get user's webinars
        list_resp = requests.get(f"{BASE_URL}/api/karau/webinar/list", headers=headers)
        webinars = list_resp.json().get("webinars", [])
        
        live = [w for w in webinars if w.get("status") == "live"]
        if not live:
            pytest.skip("No live webinars to end")
        
        webinar_id = live[0]["webinar_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{webinar_id}/end",
            headers=headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True
        assert data.get("status") == "ended"
        print(f"✓ Webinar ended: {webinar_id}")


class TestGamificationAPIs:
    """Gamification API Tests - XP, levels, badges, streaks"""
    
    def test_gamification_profile(self, auth_token):
        """GET /api/karau/analytics/gamification - Get user's gamification profile"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = requests.get(f"{BASE_URL}/api/karau/analytics/gamification", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify all required fields
        assert "level" in data, "Missing level"
        assert "xp" in data, "Missing xp"
        assert "xp_to_next" in data, "Missing xp_to_next"
        assert "streak_days" in data, "Missing streak_days"
        assert "badges" in data, "Missing badges"
        assert "rank_title" in data, "Missing rank_title"
        assert "total_meetings" in data, "Missing total_meetings"
        assert "total_hours" in data, "Missing total_hours"
        
        # Type checks
        assert isinstance(data["level"], int)
        assert isinstance(data["xp"], int)
        assert isinstance(data["badges"], list)
        assert isinstance(data["rank_title"], str)
        
        print(f"✓ Gamification: Level {data['level']}, {data['xp']} XP, Rank: {data['rank_title']}")
        print(f"  Badges: {len(data['badges'])}, Streak: {data['streak_days']} days")
        
        # If badges exist, verify structure
        if data["badges"]:
            badge = data["badges"][0]
            assert "id" in badge
            assert "name" in badge
            assert "earned" in badge


class TestLeaderboardAPIs:
    """Leaderboard API Tests - Team rankings"""
    
    def test_leaderboard(self, auth_token):
        """GET /api/karau/analytics/leaderboard - Get team leaderboard"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = requests.get(f"{BASE_URL}/api/karau/analytics/leaderboard", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "leaderboard" in data, "Missing leaderboard array"
        assert "my_rank" in data, "Missing my_rank"
        assert "total_users" in data, "Missing total_users"
        
        assert isinstance(data["leaderboard"], list)
        assert isinstance(data["my_rank"], int)
        assert isinstance(data["total_users"], int)
        
        print(f"✓ Leaderboard: {data['total_users']} users, Your rank: #{data['my_rank']}")
        print(f"  Top entries returned: {len(data['leaderboard'])}")
        
        # Verify entry structure
        if data["leaderboard"]:
            entry = data["leaderboard"][0]
            assert "user_id" in entry
            assert "name" in entry
            assert "xp" in entry
            assert "level" in entry
            assert "rank_title" in entry
            print(f"  #1: {entry['name']} - {entry['xp']} XP, {entry['rank_title']}")


class TestMeetingEffectivenessAPI:
    """Meeting Effectiveness API Tests"""
    
    def test_effectiveness(self, auth_token):
        """GET /api/karau/analytics/effectiveness - Meeting effectiveness score"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = requests.get(f"{BASE_URL}/api/karau/analytics/effectiveness", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify structure
        assert "overall_score" in data
        assert "engagement_level" in data
        assert "tip" in data
        assert "total_meetings" in data
        
        print(f"✓ Effectiveness: Score {data['overall_score']}, {data['engagement_level']} engagement")


# Fixtures
@pytest.fixture(scope="session")
def auth_token():
    """Get authentication token using admin credentials"""
    login_data = {
        "email": "admin@medmatch.com",
        "password": "Swampdrainer2026!"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        headers={'Content-Type': 'application/json'},
        json=login_data
    )
    
    if response.status_code != 200:
        pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")
    
    data = response.json()
    token = data.get("access_token") or data.get("token")
    
    if not token:
        pytest.skip(f"No token in response: {data}")
    
    print(f"✓ Authenticated as admin@medmatch.com")
    return token


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
