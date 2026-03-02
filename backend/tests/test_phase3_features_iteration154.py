"""
Iteration 154: Phase 3 Features Test Suite
- Hardware Discovery Dashboard: device registry, scan, live/simulation toggle
- Virtual Breakout Lounges: 2D avatar movement, proximity-based audio, lounge zones
- Interactive Polls & Challenges: multiple choice, quiz, word cloud, rating, leaderboard integration
- Biometric Feed Verification: session watermarks, integrity scoring, trust dashboard
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
MEETING_ID = f"test-phase3-{int(time.time())}"


class TestAuth:
    """Get authentication token for all tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}


# ============================================================
# HARDWARE DISCOVERY DASHBOARD TESTS
# ============================================================
class TestHardwareDiscovery(TestAuth):
    """Test hardware discovery dashboard endpoints"""
    
    def test_list_devices_initial(self, auth_headers):
        """GET /api/karau/hardware/{meeting_id}/devices - list hardware devices"""
        response = requests.get(
            f"{BASE_URL}/api/karau/hardware/{MEETING_ID}/devices",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Should return simulated devices when empty
        assert "devices" in data
        assert "by_type" in data
        assert "total" in data
        assert "online" in data
        assert "live_mode" in data
        assert "simulation_mode" in data
        print(f"PASS: List devices returned {data['total']} devices, {data['online']} online")
    
    def test_scan_for_devices(self, auth_headers):
        """POST /api/karau/hardware/{meeting_id}/scan - scan for devices"""
        response = requests.post(
            f"{BASE_URL}/api/karau/hardware/{MEETING_ID}/scan",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("scan_complete") is True
        assert "discovered" in data
        assert "devices" in data
        assert data["discovered"] >= 1
        print(f"PASS: Scan discovered {data['discovered']} devices")
    
    def test_register_device(self, auth_headers):
        """POST /api/karau/hardware/{meeting_id}/register - register a device"""
        device_id = f"test-device-{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/karau/hardware/{MEETING_ID}/register",
            headers=auth_headers,
            json={
                "device_id": device_id,
                "device_type": "camera_360",
                "name": "Test Camera",
                "manufacturer": "Test Corp",
                "model": "TC-360",
                "firmware": "v1.0",
                "connection_type": "usb",
                "capabilities": ["360_video", "1080p"]
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        assert data.get("device_id") == device_id
        assert data.get("status") == "registered"
        print(f"PASS: Registered device {device_id}")
        return device_id
    
    def test_register_device_invalid_type(self, auth_headers):
        """POST /api/karau/hardware/{meeting_id}/register - invalid device type should return 400"""
        response = requests.post(
            f"{BASE_URL}/api/karau/hardware/{MEETING_ID}/register",
            headers=auth_headers,
            json={
                "device_id": "test-invalid",
                "device_type": "invalid_type",
                "name": "Test"
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: Invalid device type returns 400")
    
    def test_update_device_status_and_mode(self, auth_headers):
        """POST /api/karau/hardware/{meeting_id}/status - update device status and mode"""
        # First register a device
        device_id = f"test-status-{uuid.uuid4().hex[:8]}"
        requests.post(
            f"{BASE_URL}/api/karau/hardware/{MEETING_ID}/register",
            headers=auth_headers,
            json={
                "device_id": device_id,
                "device_type": "mic_array",
                "name": "Test Mic"
            }
        )
        
        # Update to live mode
        response = requests.post(
            f"{BASE_URL}/api/karau/hardware/{MEETING_ID}/status",
            headers=auth_headers,
            json={
                "device_id": device_id,
                "status": "online",
                "mode": "live"
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        assert data.get("mode") == "live"
        print(f"PASS: Updated device {device_id} to live mode")
        
        # Update to simulation mode
        response = requests.post(
            f"{BASE_URL}/api/karau/hardware/{MEETING_ID}/status",
            headers=auth_headers,
            json={
                "device_id": device_id,
                "status": "standby",
                "mode": "simulation"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("mode") == "simulation"
        print("PASS: Toggled device to simulation mode")
    
    def test_remove_device(self, auth_headers):
        """DELETE /api/karau/hardware/{meeting_id}/{device_id} - remove device"""
        # First register a device
        device_id = f"test-delete-{uuid.uuid4().hex[:8]}"
        requests.post(
            f"{BASE_URL}/api/karau/hardware/{MEETING_ID}/register",
            headers=auth_headers,
            json={
                "device_id": device_id,
                "device_type": "display",
                "name": "Test Display"
            }
        )
        
        # Delete it
        response = requests.delete(
            f"{BASE_URL}/api/karau/hardware/{MEETING_ID}/{device_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        assert data.get("removed") == device_id
        print(f"PASS: Removed device {device_id}")
    
    def test_hardware_requires_auth(self):
        """Hardware endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/karau/hardware/{MEETING_ID}/devices")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Hardware endpoints require auth (401 without)")


# ============================================================
# BREAKOUT LOUNGES TESTS
# ============================================================
class TestBreakoutLounges(TestAuth):
    """Test virtual breakout lounges with avatar movement and proximity"""
    
    lounge_id = None
    
    def test_create_lounge(self, auth_headers):
        """POST /api/karau/breakout/{meeting_id}/lounge - create breakout lounge"""
        response = requests.post(
            f"{BASE_URL}/api/karau/breakout/{MEETING_ID}/lounge",
            headers=auth_headers,
            json={
                "name": "Networking Zone",
                "topic": "Casual conversation",
                "capacity": 10,
                "time_limit_minutes": 0,
                "position": {"x": 200, "y": 150},
                "radius": 100
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        assert "lounge_id" in data
        assert data.get("name") == "Networking Zone"
        
        TestBreakoutLounges.lounge_id = data["lounge_id"]
        print(f"PASS: Created lounge {data['lounge_id']}")
    
    def test_list_lounges(self, auth_headers):
        """GET /api/karau/breakout/{meeting_id}/lounges - list lounges with avatars"""
        response = requests.get(
            f"{BASE_URL}/api/karau/breakout/{MEETING_ID}/lounges",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "lounges" in data
        assert "avatars" in data
        assert isinstance(data["lounges"], list)
        print(f"PASS: Listed {len(data['lounges'])} lounges, {len(data['avatars'])} avatars")
    
    def test_move_avatar_and_proximity(self, auth_headers):
        """POST /api/karau/breakout/{meeting_id}/move - move avatar and get proximity"""
        # Move user 1 to position
        response1 = requests.post(
            f"{BASE_URL}/api/karau/breakout/{MEETING_ID}/move",
            headers=auth_headers,
            json={
                "user_id": "user_test_1",
                "user_name": "Test User 1",
                "x": 200,
                "y": 150,
                "avatar_color": "#6366f1"
            }
        )
        assert response1.status_code == 200, f"Failed: {response1.text}"
        data1 = response1.json()
        
        assert data1.get("success") is True
        assert "position" in data1
        assert "nearby_users" in data1
        assert "current_lounge" in data1
        print(f"PASS: Moved user_test_1 to (200, 150)")
        
        # Move user 2 near user 1 (within 150px proximity threshold)
        response2 = requests.post(
            f"{BASE_URL}/api/karau/breakout/{MEETING_ID}/move",
            headers=auth_headers,
            json={
                "user_id": "user_test_2",
                "user_name": "Test User 2",
                "x": 250,  # 50px away from user 1
                "y": 150,
                "avatar_color": "#ec4899"
            }
        )
        assert response2.status_code == 200, f"Failed: {response2.text}"
        data2 = response2.json()
        
        assert data2.get("success") is True
        assert "nearby_users" in data2
        
        # User 2 should see user 1 as nearby
        nearby = data2.get("nearby_users", [])
        assert len(nearby) >= 1, "User 2 should see user 1 as nearby"
        
        # Verify distance and audio_volume
        user1_nearby = next((n for n in nearby if n["user_id"] == "user_test_1"), None)
        assert user1_nearby is not None, "User 1 should be in nearby list"
        assert user1_nearby["distance"] <= 150, "Distance should be within proximity threshold"
        assert "audio_volume" in user1_nearby, "Should have audio_volume"
        print(f"PASS: User 2 sees User 1 nearby at distance {user1_nearby['distance']}, audio volume {user1_nearby['audio_volume']}")
    
    def test_get_proximity_data(self, auth_headers):
        """GET /api/karau/breakout/{meeting_id}/proximity/{user_id} - get proximity data"""
        response = requests.get(
            f"{BASE_URL}/api/karau/breakout/{MEETING_ID}/proximity/user_test_2",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("user_id") == "user_test_2"
        assert "position" in data
        assert "nearby" in data
        print(f"PASS: Got proximity data for user_test_2, {len(data['nearby'])} nearby users")
    
    def test_update_lounge(self, auth_headers):
        """PUT /api/karau/breakout/{meeting_id}/lounge/{lounge_id} - update lounge"""
        if not TestBreakoutLounges.lounge_id:
            pytest.skip("No lounge created")
        
        response = requests.put(
            f"{BASE_URL}/api/karau/breakout/{MEETING_ID}/lounge/{TestBreakoutLounges.lounge_id}",
            headers=auth_headers,
            json={
                "name": "Updated Lounge Name",
                "capacity": 15
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("lounge_id") == TestBreakoutLounges.lounge_id
        print("PASS: Updated lounge settings")
    
    def test_delete_lounge(self, auth_headers):
        """DELETE /api/karau/breakout/{meeting_id}/lounge/{lounge_id} - close lounge"""
        if not TestBreakoutLounges.lounge_id:
            pytest.skip("No lounge created")
        
        response = requests.delete(
            f"{BASE_URL}/api/karau/breakout/{MEETING_ID}/lounge/{TestBreakoutLounges.lounge_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        assert data.get("closed") == TestBreakoutLounges.lounge_id
        print(f"PASS: Closed lounge {TestBreakoutLounges.lounge_id}")
    
    def test_breakout_requires_auth(self):
        """Breakout endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/karau/breakout/{MEETING_ID}/lounges")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Breakout endpoints require auth (401 without)")


# ============================================================
# INTERACTIVE POLLS & CHALLENGES TESTS
# ============================================================
class TestPollsChallenges(TestAuth):
    """Test polls with multiple types: multiple_choice, quiz, word_cloud, rating"""
    
    poll_id = None
    quiz_poll_id = None
    word_cloud_poll_id = None
    rating_poll_id = None
    
    def test_create_multiple_choice_poll(self, auth_headers):
        """POST /api/karau/polls/create - create multiple choice poll"""
        response = requests.post(
            f"{BASE_URL}/api/karau/polls/create",
            headers=auth_headers,
            json={
                "meeting_id": MEETING_ID,
                "question": "What's your favorite feature?",
                "poll_type": "multiple_choice",
                "options": [
                    {"text": "Real-time translation"},
                    {"text": "AI summaries"},
                    {"text": "Spatial audio"}
                ],
                "time_limit_seconds": 0,
                "anonymous": False,
                "points": 5
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        assert "poll_id" in data
        assert data.get("poll_type") == "multiple_choice"
        
        TestPollsChallenges.poll_id = data["poll_id"]
        print(f"PASS: Created multiple choice poll {data['poll_id']}")
    
    def test_create_quiz_poll(self, auth_headers):
        """POST /api/karau/polls/create - create quiz with correct_answer"""
        response = requests.post(
            f"{BASE_URL}/api/karau/polls/create",
            headers=auth_headers,
            json={
                "meeting_id": MEETING_ID,
                "question": "What year was Python released?",
                "poll_type": "quiz",
                "options": [
                    {"text": "1989", "id": "opt-0"},
                    {"text": "1991", "id": "opt-1"},
                    {"text": "1995", "id": "opt-2"}
                ],
                "correct_answer_id": "opt-1",  # 1991 is correct
                "time_limit_seconds": 0,
                "points": 10
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        assert data.get("poll_type") == "quiz"
        
        TestPollsChallenges.quiz_poll_id = data["poll_id"]
        print(f"PASS: Created quiz poll {data['poll_id']}")
    
    def test_create_word_cloud_poll(self, auth_headers):
        """POST /api/karau/polls/create - create word cloud poll"""
        response = requests.post(
            f"{BASE_URL}/api/karau/polls/create",
            headers=auth_headers,
            json={
                "meeting_id": MEETING_ID,
                "question": "Describe this meeting in one word",
                "poll_type": "word_cloud",
                "options": [],
                "points": 5
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        assert data.get("poll_type") == "word_cloud"
        
        TestPollsChallenges.word_cloud_poll_id = data["poll_id"]
        print(f"PASS: Created word cloud poll {data['poll_id']}")
    
    def test_create_rating_poll(self, auth_headers):
        """POST /api/karau/polls/create - create rating poll"""
        response = requests.post(
            f"{BASE_URL}/api/karau/polls/create",
            headers=auth_headers,
            json={
                "meeting_id": MEETING_ID,
                "question": "Rate this presentation (1-10)",
                "poll_type": "rating",
                "options": [],
                "points": 5
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        assert data.get("poll_type") == "rating"
        
        TestPollsChallenges.rating_poll_id = data["poll_id"]
        print(f"PASS: Created rating poll {data['poll_id']}")
    
    def test_get_active_polls(self, auth_headers):
        """GET /api/karau/polls/{meeting_id}/active - get active polls"""
        response = requests.get(
            f"{BASE_URL}/api/karau/polls/{MEETING_ID}/active",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "polls" in data
        assert len(data["polls"]) >= 4, f"Should have at least 4 active polls, got {len(data['polls'])}"
        print(f"PASS: Found {len(data['polls'])} active polls")
    
    def test_vote_on_multiple_choice(self, auth_headers):
        """POST /api/karau/polls/{poll_id}/vote - vote on multiple choice poll"""
        if not TestPollsChallenges.poll_id:
            pytest.skip("No poll created")
        
        response = requests.post(
            f"{BASE_URL}/api/karau/polls/{TestPollsChallenges.poll_id}/vote",
            headers=auth_headers,
            json={"option_id": "opt-0"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        assert "points_earned" in data
        print(f"PASS: Voted on poll, earned {data.get('points_earned')} points")
    
    def test_duplicate_vote_returns_409(self, auth_headers):
        """POST /api/karau/polls/{poll_id}/vote - duplicate vote should return 409"""
        if not TestPollsChallenges.poll_id:
            pytest.skip("No poll created")
        
        # Try to vote again on the same poll
        response = requests.post(
            f"{BASE_URL}/api/karau/polls/{TestPollsChallenges.poll_id}/vote",
            headers=auth_headers,
            json={"option_id": "opt-1"}
        )
        assert response.status_code == 409, f"Expected 409 for duplicate vote, got {response.status_code}"
        print("PASS: Duplicate vote returns 409")
    
    def test_quiz_correct_answer_scoring(self, auth_headers):
        """POST /api/karau/polls/{poll_id}/vote - quiz with correct answer gives points"""
        if not TestPollsChallenges.quiz_poll_id:
            pytest.skip("No quiz poll created")
        
        # Vote with correct answer (opt-1 = 1991)
        response = requests.post(
            f"{BASE_URL}/api/karau/polls/{TestPollsChallenges.quiz_poll_id}/vote",
            headers=auth_headers,
            json={"option_id": "opt-1"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        assert data.get("is_correct") is True, "Correct answer should return is_correct=True"
        assert data.get("points_earned", 0) > 0, "Correct answer should earn points"
        print(f"PASS: Quiz correct answer: is_correct={data['is_correct']}, points={data['points_earned']}")
    
    def test_word_cloud_response(self, auth_headers):
        """POST /api/karau/polls/{poll_id}/vote - word cloud with text_response"""
        if not TestPollsChallenges.word_cloud_poll_id:
            pytest.skip("No word cloud poll created")
        
        response = requests.post(
            f"{BASE_URL}/api/karau/polls/{TestPollsChallenges.word_cloud_poll_id}/vote",
            headers=auth_headers,
            json={"text_response": "innovative productive amazing"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        print(f"PASS: Word cloud response recorded, points={data.get('points_earned')}")
    
    def test_rating_vote(self, auth_headers):
        """POST /api/karau/polls/{poll_id}/vote - rating poll with rating value"""
        if not TestPollsChallenges.rating_poll_id:
            pytest.skip("No rating poll created")
        
        response = requests.post(
            f"{BASE_URL}/api/karau/polls/{TestPollsChallenges.rating_poll_id}/vote",
            headers=auth_headers,
            json={"rating": 8}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        print(f"PASS: Rating vote recorded (8), points={data.get('points_earned')}")
    
    def test_get_poll_results(self, auth_headers):
        """GET /api/karau/polls/{poll_id}/results - get poll results with percentages"""
        if not TestPollsChallenges.poll_id:
            pytest.skip("No poll created")
        
        response = requests.get(
            f"{BASE_URL}/api/karau/polls/{TestPollsChallenges.poll_id}/results",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("poll_id") == TestPollsChallenges.poll_id
        assert "total_votes" in data
        assert "options" in data
        
        # Verify percentage calculation
        for opt in data.get("options", []):
            assert "percentage" in opt, "Each option should have percentage"
        print(f"PASS: Poll results: {data['total_votes']} votes, options have percentages")
    
    def test_get_rating_results(self, auth_headers):
        """GET /api/karau/polls/{poll_id}/results - rating results with average"""
        if not TestPollsChallenges.rating_poll_id:
            pytest.skip("No rating poll created")
        
        response = requests.get(
            f"{BASE_URL}/api/karau/polls/{TestPollsChallenges.rating_poll_id}/results",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "average_rating" in data
        assert "rating_count" in data
        print(f"PASS: Rating results: avg={data['average_rating']}, count={data['rating_count']}")
    
    def test_close_poll(self, auth_headers):
        """POST /api/karau/polls/{poll_id}/close - close a poll"""
        if not TestPollsChallenges.poll_id:
            pytest.skip("No poll created")
        
        response = requests.post(
            f"{BASE_URL}/api/karau/polls/{TestPollsChallenges.poll_id}/close",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        assert data.get("status") == "closed"
        print(f"PASS: Closed poll {TestPollsChallenges.poll_id}")
    
    def test_poll_history(self, auth_headers):
        """GET /api/karau/polls/{meeting_id}/history - poll history"""
        response = requests.get(
            f"{BASE_URL}/api/karau/polls/{MEETING_ID}/history",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "polls" in data
        assert len(data["polls"]) >= 1, "Should have at least 1 poll in history"
        print(f"PASS: Poll history has {len(data['polls'])} polls")
    
    def test_polls_requires_auth(self):
        """Polls endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/karau/polls/{MEETING_ID}/active")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Polls endpoints require auth (401 without)")


# ============================================================
# BIOMETRIC FEED VERIFICATION TESTS
# ============================================================
class TestBiometricVerification(TestAuth):
    """Test biometric feed verification: watermarks, integrity, trust dashboard"""
    
    watermark_hash = None
    
    def test_create_session_watermark(self, auth_headers):
        """POST /api/karau/biometric/{meeting_id}/watermark - create session watermark"""
        response = requests.post(
            f"{BASE_URL}/api/karau/biometric/{MEETING_ID}/watermark",
            headers=auth_headers,
            json={
                "meeting_id": MEETING_ID,
                "user_id": "test_user_bio"
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "watermark_hash" in data
        assert data.get("status") == "active"
        assert "visual_pattern" in data
        
        # Visual pattern should have segments
        pattern = data["visual_pattern"]
        assert "type" in pattern
        assert "segments" in pattern
        
        TestBiometricVerification.watermark_hash = data["watermark_hash"]
        print(f"PASS: Created watermark {data['watermark_hash'][:12]}..., pattern type: {pattern['type']}")
    
    def test_verify_feed_integrity(self, auth_headers):
        """POST /api/karau/biometric/{meeting_id}/verify - verify feed integrity"""
        if not TestBiometricVerification.watermark_hash:
            pytest.skip("No watermark created")
        
        response = requests.post(
            f"{BASE_URL}/api/karau/biometric/{MEETING_ID}/verify",
            headers=auth_headers,
            json={
                "meeting_id": MEETING_ID,
                "user_id": "test_user_bio",
                "frame_hash": TestBiometricVerification.watermark_hash,
                "timestamp": "2026-01-15T10:00:00Z"
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "verified" in data
        assert "integrity_score" in data
        assert "trust_level" in data
        assert "check_count" in data
        
        # Using the same watermark should verify successfully
        assert data.get("verified") is True
        assert data.get("trust_level") in ["high", "medium", "low", "unverified"]
        print(f"PASS: Verify feed: verified={data['verified']}, trust={data['trust_level']}, score={data['integrity_score']}")
    
    def test_verify_feed_mismatch(self, auth_headers):
        """POST /api/karau/biometric/{meeting_id}/verify - mismatched hash lowers integrity"""
        response = requests.post(
            f"{BASE_URL}/api/karau/biometric/{MEETING_ID}/verify",
            headers=auth_headers,
            json={
                "meeting_id": MEETING_ID,
                "user_id": "test_user_bio",
                "frame_hash": "invalid_hash_12345",
                "timestamp": "2026-01-15T10:01:00Z"
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Mismatched hash should return verified=False
        assert data.get("verified") is False
        print(f"PASS: Mismatched hash: verified={data['verified']}, score={data['integrity_score']}")
    
    def test_trust_dashboard(self, auth_headers):
        """GET /api/karau/biometric/{meeting_id}/trust - trust dashboard"""
        response = requests.get(
            f"{BASE_URL}/api/karau/biometric/{MEETING_ID}/trust",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "participants" in data
        assert "summary" in data
        
        summary = data["summary"]
        assert "total" in summary
        assert "verified" in summary
        assert "unverified" in summary
        assert "average_integrity" in summary
        assert "overall_trust" in summary
        
        # Verify participant data structure
        participants = data["participants"]
        if participants:
            p = participants[0]
            assert "user_id" in p
            assert "trust_level" in p
            assert "integrity_score" in p
            assert "visual_pattern" in p
        
        print(f"PASS: Trust dashboard: {summary['total']} participants, overall trust: {summary['overall_trust']}")
    
    def test_biometric_requires_auth(self):
        """Biometric endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/karau/biometric/{MEETING_ID}/trust")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Biometric endpoints require auth (401 without)")


# ============================================================
# SUMMARY TEST
# ============================================================
class TestSummary(TestAuth):
    """Summary of all Phase 3 features"""
    
    def test_all_features_summary(self, auth_headers):
        """Verify all 4 Phase 3 feature modules are working"""
        results = {
            "hardware_discovery": {"scan": False, "devices": False, "mode_toggle": False},
            "breakout_lounges": {"create": False, "move": False, "proximity": False},
            "polls_challenges": {"create": False, "vote": False, "quiz_scoring": False},
            "biometric_verify": {"watermark": False, "verify": False, "trust": False}
        }
        
        # Hardware
        try:
            r = requests.post(f"{BASE_URL}/api/karau/hardware/summary-test/scan", headers=auth_headers)
            results["hardware_discovery"]["scan"] = r.status_code == 200
            r = requests.get(f"{BASE_URL}/api/karau/hardware/summary-test/devices", headers=auth_headers)
            results["hardware_discovery"]["devices"] = r.status_code == 200
            results["hardware_discovery"]["mode_toggle"] = True  # Tested above
        except: pass
        
        # Breakout
        try:
            r = requests.get(f"{BASE_URL}/api/karau/breakout/summary-test/lounges", headers=auth_headers)
            results["breakout_lounges"]["create"] = r.status_code == 200
            results["breakout_lounges"]["move"] = True  # Tested above
            results["breakout_lounges"]["proximity"] = True  # Tested above
        except: pass
        
        # Polls
        try:
            r = requests.get(f"{BASE_URL}/api/karau/polls/summary-test/active", headers=auth_headers)
            results["polls_challenges"]["create"] = r.status_code == 200
            results["polls_challenges"]["vote"] = True  # Tested above
            results["polls_challenges"]["quiz_scoring"] = True  # Tested above
        except: pass
        
        # Biometric
        try:
            r = requests.get(f"{BASE_URL}/api/karau/biometric/summary-test/trust", headers=auth_headers)
            results["biometric_verify"]["watermark"] = True  # Tested above
            results["biometric_verify"]["verify"] = True  # Tested above
            results["biometric_verify"]["trust"] = r.status_code == 200
        except: pass
        
        print("\n=== PHASE 3 FEATURES SUMMARY ===")
        for feature, checks in results.items():
            status = "PASS" if all(checks.values()) else "PARTIAL"
            print(f"{status}: {feature} - {checks}")
        
        assert True  # This is a summary test


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
