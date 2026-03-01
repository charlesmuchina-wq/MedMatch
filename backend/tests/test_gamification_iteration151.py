"""
Iteration 151: Gamification API Tests
Tests for:
- POST /api/karau/webinar/{id}/reaction - Send emoji reaction
- GET /api/karau/webinar/{id}/reactions/recent - Get recent reactions
- GET /api/karau/webinar/{id}/leaderboard - Get leaderboard
- POST /api/karau/webinar/{id}/leaderboard/track - Track participation
- GET /api/karau/webinar/{id}/reactions/summary - Reaction summary
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test webinar ID for gamification tests
TEST_WEBINAR_ID = "WEB-GAMIFY-151"

class TestGamificationReactions:
    """Tests for emoji reaction endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get token
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json().get("access_token") or login_res.json().get("token")
        assert token, f"No token in response: {login_res.json()}"
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.token = token
    
    def test_send_reaction_thumbsup(self):
        """Test sending a thumbsup reaction"""
        response = self.session.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/reaction",
            json={"reaction": "thumbsup", "sender_name": "Test User"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data.get("emoji") == "\U0001f44d"  # thumbsup emoji
        assert "reaction_id" in data
        print(f"PASS: Sent thumbsup reaction, id={data['reaction_id']}")
    
    def test_send_reaction_clap(self):
        """Test sending a clap reaction"""
        response = self.session.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/reaction",
            json={"reaction": "clap", "sender_name": "Test User"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data.get("emoji") == "\U0001f44f"  # clap emoji
        print(f"PASS: Sent clap reaction")
    
    def test_send_reaction_heart(self):
        """Test sending a heart reaction"""
        response = self.session.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/reaction",
            json={"reaction": "heart", "sender_name": "Test User"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        print(f"PASS: Sent heart reaction")
    
    def test_send_reaction_fire(self):
        """Test sending a fire reaction"""
        response = self.session.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/reaction",
            json={"reaction": "fire", "sender_name": "Test User"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data.get("emoji") == "\U0001f525"  # fire emoji
        print(f"PASS: Sent fire reaction")
    
    def test_send_reaction_invalid_type(self):
        """Test sending an invalid reaction type returns error"""
        response = self.session.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/reaction",
            json={"reaction": "invalid_emoji", "sender_name": "Test User"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"PASS: Invalid reaction type returns 400 error")
    
    def test_send_reaction_all_valid_types(self):
        """Test all valid reaction types work"""
        valid_reactions = ["thumbsup", "clap", "heart", "laugh", "fire", "mindblown", "wave", "100"]
        for reaction in valid_reactions:
            response = self.session.post(
                f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/reaction",
                json={"reaction": reaction, "sender_name": f"Test-{reaction}"}
            )
            assert response.status_code == 200, f"Reaction '{reaction}' failed: {response.text}"
        print(f"PASS: All {len(valid_reactions)} valid reaction types work")


class TestGamificationRecentReactions:
    """Tests for recent reactions endpoint"""
    
    def test_get_recent_reactions(self):
        """Test getting recent reactions - no auth required"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/reactions/recent?limit=20")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "reactions" in data
        assert isinstance(data["reactions"], list)
        print(f"PASS: Got {len(data['reactions'])} recent reactions")
    
    def test_get_recent_reactions_with_limit(self):
        """Test recent reactions respects limit parameter"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/reactions/recent?limit=5")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert len(data["reactions"]) <= 5
        print(f"PASS: Limit parameter works, got {len(data['reactions'])} reactions")


class TestGamificationLeaderboard:
    """Tests for leaderboard endpoints"""
    
    def test_get_leaderboard(self):
        """Test getting leaderboard - no auth required"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/leaderboard?limit=10")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "leaderboard" in data
        assert "total_participants" in data
        assert isinstance(data["leaderboard"], list)
        print(f"PASS: Got leaderboard with {data['total_participants']} participants")
    
    def test_leaderboard_has_ranks(self):
        """Test leaderboard entries have rank field"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/leaderboard")
        assert response.status_code == 200
        data = response.json()
        for entry in data["leaderboard"]:
            assert "rank" in entry
            assert "total_score" in entry
            assert "user_name" in entry
        print(f"PASS: Leaderboard entries have required fields (rank, total_score, user_name)")


class TestGamificationTracking:
    """Tests for participation tracking"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json().get("access_token") or login_res.json().get("token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def test_track_question_action(self):
        """Test tracking a question action (5 points per question)"""
        response = self.session.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/leaderboard/track",
            json={"action": "question", "value": 1}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data.get("action") == "question"
        assert data.get("score_added") == 5  # question = 5 points
        print(f"PASS: Tracked question action, score_added={data['score_added']}")
    
    def test_track_reaction_action(self):
        """Test tracking a reaction action (2 points per reaction)"""
        response = self.session.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/leaderboard/track",
            json={"action": "reaction", "value": 1}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data.get("score_added") == 2  # reaction = 2 points
        print(f"PASS: Tracked reaction action, score_added={data['score_added']}")
    
    def test_track_speaking_action(self):
        """Test tracking speaking time (1 point per second)"""
        response = self.session.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/leaderboard/track",
            json={"action": "speaking", "value": 30}  # 30 seconds
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data.get("score_added") == 30  # 30 * 1 point
        print(f"PASS: Tracked speaking action, score_added={data['score_added']}")
    
    def test_track_chat_action(self):
        """Test tracking chat message (1 point per message)"""
        response = self.session.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/leaderboard/track",
            json={"action": "chat", "value": 1}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data.get("score_added") == 1  # chat = 1 point
        print(f"PASS: Tracked chat action, score_added={data['score_added']}")


class TestGamificationSummary:
    """Tests for reaction summary endpoint"""
    
    def test_get_reaction_summary(self):
        """Test getting aggregated reaction counts"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/reactions/summary")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "summary" in data
        assert "total_reactions" in data
        assert isinstance(data["summary"], dict)
        print(f"PASS: Got reaction summary with {data['total_reactions']} total reactions")
    
    def test_summary_has_emoji_counts(self):
        """Test summary contains emoji and count for each reaction type"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/reactions/summary")
        assert response.status_code == 200
        data = response.json()
        for key, val in data["summary"].items():
            assert "count" in val
            assert "emoji" in val
        print(f"PASS: Summary has emoji and count for each reaction type")


class TestGamificationAuth:
    """Tests for auth requirements"""
    
    def test_reaction_requires_auth(self):
        """Test that sending reaction requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/reaction",
            json={"reaction": "thumbsup", "sender_name": "Anon"}
        )
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: Reaction endpoint requires auth (returns {response.status_code})")
    
    def test_tracking_requires_auth(self):
        """Test that tracking requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/leaderboard/track",
            json={"action": "question", "value": 1}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: Tracking endpoint requires auth (returns {response.status_code})")
    
    def test_recent_reactions_no_auth_required(self):
        """Test that getting recent reactions doesn't require auth"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/reactions/recent")
        assert response.status_code == 200
        print(f"PASS: Recent reactions endpoint accessible without auth")
    
    def test_leaderboard_no_auth_required(self):
        """Test that getting leaderboard doesn't require auth"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/leaderboard")
        assert response.status_code == 200
        print(f"PASS: Leaderboard endpoint accessible without auth")
    
    def test_summary_no_auth_required(self):
        """Test that getting summary doesn't require auth"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/reactions/summary")
        assert response.status_code == 200
        print(f"PASS: Summary endpoint accessible without auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
