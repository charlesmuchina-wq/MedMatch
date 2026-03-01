"""
Iteration 152: Distance Zero Features Testing
Tests for:
1. P2 Bug Fix - Gamification auth error handling (401 instead of 500)
2. Cinematic Director Mode API
3. QR Code Touchless Entry API  
4. Ghost Booking Prevention API
5. Enhanced Sentiment Dashboard + AI Copilot API
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_EMAIL = "test@medmatch.io"
TEST_PASSWORD = "TestPassword123!"


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for admin user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token") or data.get("token")
    pytest.skip("Authentication failed")


@pytest.fixture
def auth_headers(auth_token):
    """Auth headers for authenticated requests"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="module")
def test_webinar_id():
    """Generate a test webinar ID"""
    return f"WEB-DIST0-{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def test_meeting_id():
    """Generate a test meeting ID"""
    return f"MTG-DIST0-{uuid.uuid4().hex[:8]}"


# ============== P2 Bug Fix Tests - Auth Error Handling ==============
class TestGamificationAuthFix:
    """Test that gamification endpoints return 401 (not 500) when unauthenticated"""

    def test_reaction_without_auth_returns_401(self, test_webinar_id):
        """POST /api/karau/webinar/{id}/reaction without auth should return 401"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{test_webinar_id}/reaction",
            json={"reaction": "thumbsup", "sender_name": "Test"}
        )
        # Should be 401 (unauthorized), NOT 500
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_leaderboard_track_without_auth_returns_401(self, test_webinar_id):
        """POST /api/karau/webinar/{id}/leaderboard/track without auth should return 401"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{test_webinar_id}/leaderboard/track",
            json={"action": "question", "value": 1}
        )
        # Should be 401 (unauthorized), NOT 500
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_recent_reactions_public_no_auth(self, test_webinar_id):
        """GET /api/karau/webinar/{id}/reactions/recent should work without auth"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/{test_webinar_id}/reactions/recent")
        assert response.status_code == 200
        data = response.json()
        assert "reactions" in data

    def test_leaderboard_public_no_auth(self, test_webinar_id):
        """GET /api/karau/webinar/{id}/leaderboard should work without auth"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/{test_webinar_id}/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert "leaderboard" in data


# ============== Cinematic Director Mode Tests ==============
class TestDirectorMode:
    """Test Director Mode API endpoints"""

    def test_set_director_mode_with_auth(self, auth_headers, test_meeting_id):
        """POST /api/karau/director/{meeting_id}/mode - set director mode"""
        response = requests.post(
            f"{BASE_URL}/api/karau/director/{test_meeting_id}/mode",
            headers=auth_headers,
            json={"mode": "auto", "pinned_user_id": None}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("mode") == "auto"

    def test_set_director_mode_panoramic(self, auth_headers, test_meeting_id):
        """Set director mode to panoramic"""
        response = requests.post(
            f"{BASE_URL}/api/karau/director/{test_meeting_id}/mode",
            headers=auth_headers,
            json={"mode": "panoramic"}
        )
        assert response.status_code == 200
        assert response.json().get("mode") == "panoramic"

    def test_set_director_mode_speaker_closeup(self, auth_headers, test_meeting_id):
        """Set director mode to speaker closeup"""
        response = requests.post(
            f"{BASE_URL}/api/karau/director/{test_meeting_id}/mode",
            headers=auth_headers,
            json={"mode": "speaker_closeup"}
        )
        assert response.status_code == 200
        assert response.json().get("mode") == "speaker_closeup"

    def test_set_director_mode_conversation(self, auth_headers, test_meeting_id):
        """Set director mode to conversation"""
        response = requests.post(
            f"{BASE_URL}/api/karau/director/{test_meeting_id}/mode",
            headers=auth_headers,
            json={"mode": "conversation"}
        )
        assert response.status_code == 200
        assert response.json().get("mode") == "conversation"

    def test_set_director_mode_invalid(self, auth_headers, test_meeting_id):
        """Invalid director mode should return 400"""
        response = requests.post(
            f"{BASE_URL}/api/karau/director/{test_meeting_id}/mode",
            headers=auth_headers,
            json={"mode": "invalid_mode"}
        )
        assert response.status_code == 400

    def test_get_director_mode_public(self, test_meeting_id):
        """GET /api/karau/director/{meeting_id}/mode - no auth required"""
        response = requests.get(f"{BASE_URL}/api/karau/director/{test_meeting_id}/mode")
        assert response.status_code == 200
        data = response.json()
        assert "mode" in data

    def test_analyze_director_with_auth(self, auth_headers, test_meeting_id):
        """POST /api/karau/director/{meeting_id}/analyze - AI analyze speaking patterns"""
        response = requests.post(
            f"{BASE_URL}/api/karau/director/{test_meeting_id}/analyze",
            headers=auth_headers,
            json={
                "meeting_id": test_meeting_id,
                "speaking_events": [
                    {"user_id": "user1", "user_name": "Alice", "is_speaking": True, "duration_seconds": 5.0},
                    {"user_id": "user2", "user_name": "Bob", "is_speaking": False, "duration_seconds": 0}
                ],
                "participant_count": 2,
                "elapsed_seconds": 60
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "recommended_view" in data
        assert data["recommended_view"] in ["panoramic", "speaker_closeup", "conversation"]
        assert "focus_users" in data
        assert "should_switch" in data


# ============== QR Code Touchless Entry Tests ==============
class TestQRCodeEntry:
    """Test QR Code Entry API endpoints"""

    def test_generate_qr_code_requires_auth(self, test_meeting_id):
        """POST /api/karau-meet/qr/generate without auth should fail"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/qr/generate",
            json={"meeting_id": test_meeting_id, "expires_minutes": 60, "max_uses": 10}
        )
        assert response.status_code == 401

    def test_generate_qr_code_meeting_not_found(self, auth_headers, test_meeting_id):
        """POST /api/karau-meet/qr/generate for non-existent meeting returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/qr/generate",
            headers=auth_headers,
            json={"meeting_id": f"NONEXISTENT-{uuid.uuid4().hex[:8]}", "expires_minutes": 60, "max_uses": 10}
        )
        # 404 is expected because meeting doesn't exist
        assert response.status_code == 404

    def test_validate_qr_code_invalid(self):
        """GET /api/karau-meet/qr/validate/{qr_token} - invalid token returns 404"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/qr/validate/INVALID-TOKEN-12345")
        assert response.status_code == 404

    def test_list_qr_codes_requires_auth(self, test_meeting_id):
        """GET /api/karau-meet/qr/meeting/{meeting_id} requires auth"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/qr/meeting/{test_meeting_id}")
        assert response.status_code == 401

    def test_list_qr_codes_with_auth(self, auth_headers, test_meeting_id):
        """GET /api/karau-meet/qr/meeting/{meeting_id} with auth returns list"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/qr/meeting/{test_meeting_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "qr_codes" in data
        assert isinstance(data["qr_codes"], list)

    def test_deactivate_qr_code_requires_auth(self):
        """DELETE /api/karau-meet/qr/{qr_token} requires auth"""
        response = requests.delete(f"{BASE_URL}/api/karau-meet/qr/SOME-TOKEN")
        assert response.status_code == 401


# ============== Ghost Booking Prevention Tests ==============
class TestGhostBooking:
    """Test Ghost Booking Prevention API endpoints"""

    def test_activity_ping_requires_auth(self, test_meeting_id):
        """POST /api/karau-meet/ghost/ping requires auth"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ghost/ping",
            json={"meeting_id": test_meeting_id, "activity_type": "presence"}
        )
        assert response.status_code == 401

    def test_activity_ping_with_auth(self, auth_headers, test_meeting_id):
        """POST /api/karau-meet/ghost/ping with auth succeeds"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ghost/ping",
            headers=auth_headers,
            json={"meeting_id": test_meeting_id, "activity_type": "presence"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("pinged") == test_meeting_id

    def test_check_ghost_status_requires_auth(self, test_meeting_id):
        """GET /api/karau-meet/ghost/check/{meeting_id} requires auth"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/ghost/check/{test_meeting_id}")
        assert response.status_code == 401

    def test_check_ghost_status_with_auth(self, auth_headers, test_meeting_id):
        """GET /api/karau-meet/ghost/check/{meeting_id} with auth returns status"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/ghost/check/{test_meeting_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "meeting_id" in data
        assert "is_idle" in data
        assert "approaching_idle" in data
        assert "active_users" in data

    def test_release_meeting_requires_auth(self, test_meeting_id):
        """POST /api/karau-meet/ghost/release/{meeting_id} requires auth"""
        response = requests.post(f"{BASE_URL}/api/karau-meet/ghost/release/{test_meeting_id}")
        assert response.status_code == 401

    def test_release_meeting_with_auth(self, auth_headers, test_meeting_id):
        """POST /api/karau-meet/ghost/release/{meeting_id} releases meeting"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ghost/release/{test_meeting_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("status") == "released"

    def test_keep_alive_requires_auth(self, test_meeting_id):
        """POST /api/karau-meet/ghost/keep/{meeting_id} requires auth"""
        response = requests.post(f"{BASE_URL}/api/karau-meet/ghost/keep/{test_meeting_id}")
        assert response.status_code == 401

    def test_keep_alive_with_auth(self, auth_headers, test_meeting_id):
        """POST /api/karau-meet/ghost/keep/{meeting_id} keeps meeting alive"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ghost/keep/{test_meeting_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True

    def test_update_ghost_settings_requires_auth(self, test_meeting_id):
        """POST /api/karau-meet/ghost/settings/{meeting_id} requires auth"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ghost/settings/{test_meeting_id}",
            json={"idle_timeout_minutes": 15, "auto_release": True}
        )
        assert response.status_code == 401

    def test_update_ghost_settings_with_auth(self, auth_headers, test_meeting_id):
        """POST /api/karau-meet/ghost/settings/{meeting_id} updates settings"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ghost/settings/{test_meeting_id}",
            headers=auth_headers,
            json={"idle_timeout_minutes": 15, "auto_release": True, "notify_before_release_minutes": 3}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True


# ============== Enhanced Sentiment Dashboard Tests ==============
class TestSentimentDashboard:
    """Test Enhanced Sentiment Dashboard API endpoints"""

    def test_update_sentiment_requires_auth(self, test_meeting_id):
        """POST /api/karau/sentiment-dash/update requires auth"""
        response = requests.post(
            f"{BASE_URL}/api/karau/sentiment-dash/update",
            json={
                "meeting_id": test_meeting_id,
                "participants": [
                    {"user_id": "u1", "user_name": "Alice", "attention_score": 7.5, "confusion_level": 0.2, "engagement_level": 8.0, "energy": "high"}
                ]
            }
        )
        assert response.status_code == 401

    def test_update_sentiment_with_auth(self, auth_headers, test_meeting_id):
        """POST /api/karau/sentiment-dash/update with auth succeeds"""
        response = requests.post(
            f"{BASE_URL}/api/karau/sentiment-dash/update",
            headers=auth_headers,
            json={
                "meeting_id": test_meeting_id,
                "participants": [
                    {"user_id": "u1", "user_name": "Alice", "attention_score": 7.5, "confusion_level": 0.2, "engagement_level": 8.0, "energy": "high"},
                    {"user_id": "u2", "user_name": "Bob", "attention_score": 5.0, "confusion_level": 0.6, "engagement_level": 4.0, "energy": "low"}
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("updated") == 2

    def test_get_heatmap_requires_auth(self, test_meeting_id):
        """GET /api/karau/sentiment-dash/heatmap/{meeting_id} requires auth"""
        response = requests.get(f"{BASE_URL}/api/karau/sentiment-dash/heatmap/{test_meeting_id}")
        assert response.status_code == 401

    def test_get_heatmap_with_auth(self, auth_headers, test_meeting_id):
        """GET /api/karau/sentiment-dash/heatmap/{meeting_id} returns heatmap data"""
        response = requests.get(
            f"{BASE_URL}/api/karau/sentiment-dash/heatmap/{test_meeting_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "meeting_id" in data
        assert "participants" in data
        assert "aggregate" in data
        assert "recommendations" in data
        # Check aggregate metrics
        agg = data.get("aggregate", {})
        assert "avg_attention" in agg
        assert "avg_engagement" in agg
        assert "avg_confusion" in agg


# ============== AI Copilot Tests ==============
class TestAICopilot:
    """Test Multiplayer AI Copilot API endpoints"""

    def test_copilot_query_requires_auth(self, test_meeting_id):
        """POST /api/karau/sentiment-dash/copilot/query requires auth"""
        response = requests.post(
            f"{BASE_URL}/api/karau/sentiment-dash/copilot/query",
            json={
                "meeting_id": test_meeting_id,
                "question": "What were the action items?",
                "include_past_meetings": True
            }
        )
        assert response.status_code == 401

    def test_copilot_query_with_auth(self, auth_headers, test_meeting_id):
        """POST /api/karau/sentiment-dash/copilot/query with auth returns AI answer"""
        response = requests.post(
            f"{BASE_URL}/api/karau/sentiment-dash/copilot/query",
            headers=auth_headers,
            json={
                "meeting_id": test_meeting_id,
                "question": "What are the key topics for this meeting?",
                "include_past_meetings": False,
                "context_window": 3
            },
            timeout=30  # AI response may take time
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert len(data["answer"]) > 0

    def test_copilot_history_requires_auth(self, test_meeting_id):
        """GET /api/karau/sentiment-dash/copilot/history/{meeting_id} requires auth"""
        response = requests.get(f"{BASE_URL}/api/karau/sentiment-dash/copilot/history/{test_meeting_id}")
        assert response.status_code == 401

    def test_copilot_history_with_auth(self, auth_headers, test_meeting_id):
        """GET /api/karau/sentiment-dash/copilot/history/{meeting_id} returns history"""
        response = requests.get(
            f"{BASE_URL}/api/karau/sentiment-dash/copilot/history/{test_meeting_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "interactions" in data
        assert isinstance(data["interactions"], list)


# ============== Health Check ==============
class TestHealthCheck:
    """Basic health check to ensure API is running"""

    def test_api_health(self):
        """GET /api/health should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
