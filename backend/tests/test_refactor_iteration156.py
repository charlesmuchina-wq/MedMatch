"""
Iteration 156: Backend API Tests for WebinarLiveRoom Refactor
Tests APIs that the refactored components use:
- Room info API
- Polls API
- Q&A API
- Webinar controls
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
WEBINAR_ID = "WEB-39C2FEC4"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for testing"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data, "No access_token in response"
    return data["access_token"]


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Headers with authorization"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestWebinarRoomInfo:
    """Tests for /api/karau/webinar/{id}/room-info - used by WebinarLiveRoom"""
    
    def test_get_room_info_success(self, auth_headers):
        """Room info API should return data including permissions"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{WEBINAR_ID}/room-info",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Verify essential fields used by WebinarLiveRoom
        assert "title" in data, "Missing 'title' in room-info"
        assert "status" in data, "Missing 'status' in room-info"
        assert "my_role" in data, "Missing 'my_role' in room-info"
        assert "can_stream_video" in data, "Missing 'can_stream_video'"
        assert "can_control" in data, "Missing 'can_control'"
        print(f"✓ Room info returned: title={data.get('title')}, status={data.get('status')}, role={data.get('my_role')}")
    
    def test_room_info_permission_fields(self, auth_headers):
        """Verify permission-related fields for TopBar and VideoStage"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{WEBINAR_ID}/room-info",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # Check permission fields
        assert isinstance(data.get("can_stream_video"), bool), "can_stream_video should be boolean"
        assert isinstance(data.get("can_control"), bool), "can_control should be boolean"
        assert isinstance(data.get("can_drive_slides", False), bool), "can_drive_slides should be boolean"
        print(f"✓ Permissions: stream={data.get('can_stream_video')}, control={data.get('can_control')}, slides={data.get('can_drive_slides')}")


class TestPollsAPI:
    """Tests for Polls API - used by PollsChallengesPanel (lazy-loaded in SidePanel)"""
    
    def test_get_active_polls(self, auth_headers):
        """GET /api/karau/polls/{meeting_id}/active"""
        response = requests.get(
            f"{BASE_URL}/api/karau/polls/{WEBINAR_ID}/active",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "polls" in data, "Response should have 'polls' array"
        assert isinstance(data["polls"], list), "polls should be a list"
        print(f"✓ Active polls API works: {len(data['polls'])} active polls")
    
    def test_create_poll(self, auth_headers):
        """POST /api/karau/polls/create"""
        response = requests.post(
            f"{BASE_URL}/api/karau/polls/create",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={
                "meeting_id": WEBINAR_ID,
                "poll_type": "multiple_choice",
                "question": "TEST_POLL: Refactor test question?",
                "options": [
                    {"text": "Option A", "is_correct": False},
                    {"text": "Option B", "is_correct": True},
                    {"text": "Option C", "is_correct": False}
                ]
            }
        )
        # 200 or 201 both acceptable for create
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        data = response.json()
        assert "poll_id" in data or "id" in data, "Response should contain poll ID"
        print(f"✓ Poll creation works: {data}")


class TestQAAPI:
    """Tests for Q&A API - used by QAPanel (lazy-loaded in SidePanel)"""
    
    def test_get_qa_questions(self, auth_headers):
        """GET /api/karau/webinar/{id}/qa"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{WEBINAR_ID}/qa",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "questions" in data, "Response should have 'questions' array"
        assert isinstance(data["questions"], list), "questions should be a list"
        print(f"✓ Q&A GET works: {len(data['questions'])} questions")
    
    def test_ask_question(self, auth_headers):
        """POST /api/karau/webinar/{id}/qa/ask"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{WEBINAR_ID}/qa/ask",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={
                "question": "TEST_Q: Is the refactor working?",
                "is_anonymous": False
            }
        )
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        print(f"✓ Q&A ask works: {response.json()}")


class TestSentimentAPI:
    """Tests for Sentiment Dashboard API - used by SentimentDashboard (lazy-loaded)"""
    
    def test_sentiment_dashboard(self, auth_headers):
        """GET /api/karau-features/sentiment/dashboard/{meeting_id}"""
        response = requests.get(
            f"{BASE_URL}/api/karau-features/sentiment/dashboard/{WEBINAR_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Verify fields used by engagement polling in WebinarLiveRoom
        assert "engagement_score" in data or "avg_engagement" in data, "Should have engagement metric"
        print(f"✓ Sentiment dashboard works: {data}")


class TestWebinarControls:
    """Tests for webinar control APIs - used by useWebinarActions hook"""
    
    def test_hand_raises_endpoint(self, auth_headers):
        """GET /api/karau/webinar/{id}/hand-raises"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{WEBINAR_ID}/hand-raises",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "hand_raises" in data, "Response should have 'hand_raises' array"
        print(f"✓ Hand raises endpoint works: {len(data.get('hand_raises', []))} hands raised")
    
    def test_leaderboard_endpoint(self, auth_headers):
        """GET /api/karau/webinar/{id}/leaderboard"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{WEBINAR_ID}/leaderboard",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "leaderboard" in data or "participants" in data, "Response should have leaderboard data"
        print(f"✓ Leaderboard endpoint works: {data}")


class TestDirectorModeAPI:
    """Tests for Director Mode API - used by useDirectorMode hook"""
    
    def test_get_director_mode(self, auth_headers):
        """GET /api/karau/director/{meeting_id}/mode"""
        response = requests.get(
            f"{BASE_URL}/api/karau/director/{WEBINAR_ID}/mode",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "mode" in data, "Response should have 'mode' field"
        print(f"✓ Director mode API works: mode={data.get('mode')}, view={data.get('recommended_view')}")


class TestBreakoutLounge:
    """Tests for Breakout Lounge API - used by BreakoutLoungePanel (lazy-loaded)"""
    
    def test_get_lounges(self, auth_headers):
        """GET /api/karau/breakout/{meeting_id}/lounges"""
        response = requests.get(
            f"{BASE_URL}/api/karau/breakout/{WEBINAR_ID}/lounges",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "lounges" in data, "Response should have 'lounges' array"
        print(f"✓ Breakout lounges API works: {len(data.get('lounges', []))} lounges")


class TestAICoachAPI:
    """Tests for AI Coach API - used by WebinarLiveRoom's coach tips polling"""
    
    def test_get_coach_tip(self, auth_headers):
        """POST /api/karau-features/ai-coach/tip"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/ai-coach/tip",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={
                "meeting_id": WEBINAR_ID,
                "transcript_segment": "Let me explain the next topic in detail...",
                "speaker": "Host",
                "speaking_duration_seconds": 120,
                "total_meeting_seconds": 300,
                "engagement_score": 7,
                "participant_count": 5
            }
        )
        # AI Coach may return 200 with tip or 204 no content
        assert response.status_code in [200, 201, 204], f"Expected 200/201/204, got {response.status_code}: {response.text}"
        if response.status_code == 200:
            data = response.json()
            print(f"✓ AI Coach tip API works: {data.get('tip', 'No tip')[:50]}...")
        else:
            print(f"✓ AI Coach tip API works (no tip returned)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
