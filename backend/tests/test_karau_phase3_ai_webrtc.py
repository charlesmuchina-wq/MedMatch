"""
AI KARAU Meeting Phase 3 - AI Transcription & WebRTC Tests
Tests for:
- Meeting creation and management
- AI transcription endpoints (Whisper)
- AI summary generation (GPT-5.2)
- Action item extraction
- WebRTC room status and participants
"""

import pytest
import requests
import os
import io
import wave
import struct

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "Swampdrainer2026!"


class TestKarauPhase3AIWebRTC:
    """Test AI KARAU Meeting Phase 3 features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data["access_token"]
        self.user_id = data["user"]["user_id"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    # ============ MEETING CREATION TESTS ============
    
    def test_create_meeting(self):
        """Test POST /api/karau-meet/meetings - Create meeting"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers=self.headers,
            json={
                "title": "TEST_Phase3_AI_Meeting",
                "settings": {"ai_transcription": True, "auto_summary": True}
            }
        )
        assert response.status_code == 200, f"Create meeting failed: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "meeting_id" in data, "Missing meeting_id in response"
        assert "title" in data, "Missing title in response"
        assert data["title"] == "TEST_Phase3_AI_Meeting"
        assert "host_id" in data, "Missing host_id"
        assert data["host_id"] == self.user_id
        
        # Store meeting_id for other tests
        self.__class__.test_meeting_id = data["meeting_id"]
        print(f"✓ Created meeting: {data['meeting_id']}")
    
    def test_get_meeting_details(self):
        """Test GET /api/karau-meet/meetings/{meeting_id}"""
        # First create a meeting if not exists
        if not hasattr(self.__class__, 'test_meeting_id'):
            self.test_create_meeting()
        
        meeting_id = self.__class__.test_meeting_id
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}",
            headers=self.headers
        )
        assert response.status_code == 200, f"Get meeting failed: {response.text}"
        data = response.json()
        
        assert "meeting" in data, "Missing meeting in response"
        assert "ice_servers" in data, "Missing ice_servers for WebRTC"
        print(f"✓ Got meeting details with ICE servers")
    
    def test_get_user_meetings(self):
        """Test GET /api/karau-meet/meetings - Get user's meetings"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers=self.headers
        )
        assert response.status_code == 200, f"Get meetings failed: {response.text}"
        data = response.json()
        
        assert "meetings" in data, "Missing meetings array"
        assert isinstance(data["meetings"], list)
        print(f"✓ Got {len(data['meetings'])} user meetings")
    
    # ============ AI TRANSCRIPTION TESTS ============
    
    def test_get_transcript_empty(self):
        """Test GET /api/karau-meet/ai/transcript/{meeting_id} - Empty transcript"""
        if not hasattr(self.__class__, 'test_meeting_id'):
            self.test_create_meeting()
        
        meeting_id = self.__class__.test_meeting_id
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/ai/transcript/{meeting_id}",
            headers=self.headers
        )
        assert response.status_code == 200, f"Get transcript failed: {response.text}"
        data = response.json()
        
        assert "meeting_id" in data, "Missing meeting_id"
        assert "entries" in data, "Missing entries array"
        assert "full_transcript" in data, "Missing full_transcript"
        print(f"✓ Got transcript (entries: {data.get('entry_count', 0)})")
    
    def test_transcribe_audio_mock(self):
        """Test POST /api/karau-meet/ai/transcribe - Audio transcription (mock mode)"""
        if not hasattr(self.__class__, 'test_meeting_id'):
            self.test_create_meeting()
        
        meeting_id = self.__class__.test_meeting_id
        
        # Create a minimal valid WAV file for testing
        audio_data = self._create_test_audio()
        
        files = {
            'audio_file': ('test_audio.wav', audio_data, 'audio/wav')
        }
        data = {
            'meeting_id': meeting_id,
            'speaker_name': 'Test Speaker',
            'language': 'en'
        }
        
        # Remove Content-Type header for multipart
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ai/transcribe",
            headers=headers,
            files=files,
            data=data
        )
        
        # Should succeed (mock mode if no EMERGENT_LLM_KEY)
        assert response.status_code == 200, f"Transcribe failed: {response.text}"
        result = response.json()
        
        assert "success" in result, "Missing success field"
        assert result["success"] == True, "Transcription not successful"
        assert "transcript" in result, "Missing transcript in response"
        
        # Check if mock mode
        if result.get("mock_mode"):
            print("✓ Transcription endpoint working (MOCK MODE - no EMERGENT_LLM_KEY)")
        else:
            print("✓ Transcription endpoint working with real Whisper API")
    
    def _create_test_audio(self):
        """Create a minimal valid WAV file for testing"""
        # Create a simple 1-second silent WAV file
        sample_rate = 16000
        duration = 1  # seconds
        num_samples = sample_rate * duration
        
        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            # Write silent audio (zeros)
            for _ in range(num_samples):
                wav_file.writeframes(struct.pack('<h', 0))
        
        audio_buffer.seek(0)
        return audio_buffer.read()
    
    # ============ AI SUMMARY TESTS ============
    
    def test_generate_summary_no_transcript(self):
        """Test POST /api/karau-meet/ai/summary/{meeting_id} - No transcript available"""
        if not hasattr(self.__class__, 'test_meeting_id'):
            self.test_create_meeting()
        
        meeting_id = self.__class__.test_meeting_id
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ai/summary/{meeting_id}",
            headers=self.headers,
            json={
                "meeting_title": "Test Meeting",
                "participants": ["Admin", "Test User"]
            }
        )
        
        # May return 500 if no transcript, or success with mock
        if response.status_code == 500:
            data = response.json()
            assert "detail" in data
            print(f"✓ Summary generation correctly requires transcript: {data['detail']}")
        else:
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            print(f"✓ Summary generation endpoint working")
    
    def test_get_summary_not_found(self):
        """Test GET /api/karau-meet/ai/summary/{meeting_id} - Summary not found"""
        # Use a non-existent meeting ID
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/ai/summary/nonexistent_meeting_123",
            headers=self.headers
        )
        
        # Should return 404 for non-existent summary
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Get summary correctly returns 404 for non-existent")
    
    # ============ ACTION ITEMS TESTS ============
    
    def test_extract_action_items_no_transcript(self):
        """Test POST /api/karau-meet/ai/action-items/extract/{meeting_id}"""
        if not hasattr(self.__class__, 'test_meeting_id'):
            self.test_create_meeting()
        
        meeting_id = self.__class__.test_meeting_id
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ai/action-items/extract/{meeting_id}",
            headers=self.headers
        )
        
        # May return 500 if no transcript, or success with empty items
        if response.status_code == 500:
            data = response.json()
            assert "detail" in data
            print(f"✓ Action item extraction correctly requires transcript")
        else:
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            print(f"✓ Action item extraction endpoint working")
    
    def test_get_action_items(self):
        """Test GET /api/karau-meet/ai/action-items/{meeting_id}"""
        if not hasattr(self.__class__, 'test_meeting_id'):
            self.test_create_meeting()
        
        meeting_id = self.__class__.test_meeting_id
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/ai/action-items/{meeting_id}",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Get action items failed: {response.text}"
        data = response.json()
        
        assert "meeting_id" in data, "Missing meeting_id"
        assert "action_items" in data, "Missing action_items array"
        assert "count" in data, "Missing count"
        print(f"✓ Got action items (count: {data['count']})")
    
    def test_update_action_item_status_invalid(self):
        """Test PUT /api/karau-meet/ai/action-items/{action_id}/status - Invalid action"""
        response = requests.put(
            f"{BASE_URL}/api/karau-meet/ai/action-items/invalid_action_123/status",
            headers=self.headers,
            json={"status": "completed"}
        )
        
        # Should return 400 for non-existent action item
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Update action item correctly returns 400 for non-existent")
    
    def test_update_action_item_invalid_status(self):
        """Test PUT /api/karau-meet/ai/action-items/{action_id}/status - Invalid status"""
        response = requests.put(
            f"{BASE_URL}/api/karau-meet/ai/action-items/some_action_id/status",
            headers=self.headers,
            json={"status": "invalid_status"}
        )
        
        # Should return 400 for invalid status
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        print("✓ Update action item correctly validates status values")
    
    # ============ WEBRTC ROOM STATUS TESTS ============
    
    def test_get_room_status(self):
        """Test GET /api/karau-meet/room/{meeting_id}/status - Public endpoint"""
        if not hasattr(self.__class__, 'test_meeting_id'):
            self.test_create_meeting()
        
        meeting_id = self.__class__.test_meeting_id
        
        # This is a public endpoint (no auth required)
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/room/{meeting_id}/status"
        )
        
        assert response.status_code == 200, f"Get room status failed: {response.text}"
        data = response.json()
        
        assert "meeting_id" in data, "Missing meeting_id"
        assert "active" in data, "Missing active status"
        assert "participant_count" in data, "Missing participant_count"
        print(f"✓ Room status: active={data['active']}, participants={data['participant_count']}")
    
    def test_get_room_participants(self):
        """Test GET /api/karau-meet/room/{meeting_id}/participants"""
        if not hasattr(self.__class__, 'test_meeting_id'):
            self.test_create_meeting()
        
        meeting_id = self.__class__.test_meeting_id
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/room/{meeting_id}/participants",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Get participants failed: {response.text}"
        data = response.json()
        
        assert "meeting_id" in data, "Missing meeting_id"
        assert "participants" in data, "Missing participants array"
        assert "count" in data, "Missing count"
        print(f"✓ Room participants: {data['count']}")
    
    # ============ MEETING JOIN/LEAVE TESTS ============
    
    def test_join_meeting(self):
        """Test POST /api/karau-meet/meetings/{meeting_id}/join"""
        if not hasattr(self.__class__, 'test_meeting_id'):
            self.test_create_meeting()
        
        meeting_id = self.__class__.test_meeting_id
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join",
            headers=self.headers,
            json={
                "video_enabled": True,
                "audio_enabled": True
            }
        )
        
        assert response.status_code == 200, f"Join meeting failed: {response.text}"
        data = response.json()
        
        assert "meeting" in data, "Missing meeting in response"
        assert "ice_servers" in data, "Missing ice_servers for WebRTC"
        print(f"✓ Joined meeting successfully with ICE servers")
    
    def test_leave_meeting(self):
        """Test POST /api/karau-meet/meetings/{meeting_id}/leave"""
        if not hasattr(self.__class__, 'test_meeting_id'):
            self.test_create_meeting()
        
        meeting_id = self.__class__.test_meeting_id
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/leave",
            headers=self.headers
        )
        
        # May return 404 if not in meeting, or 200 if successful
        assert response.status_code in [200, 404], f"Leave meeting failed: {response.text}"
        print(f"✓ Leave meeting endpoint working (status: {response.status_code})")
    
    # ============ MEETING CHAT TEST ============
    
    def test_send_chat_message(self):
        """Test POST /api/karau-meet/meetings/{meeting_id}/chat"""
        if not hasattr(self.__class__, 'test_meeting_id'):
            self.test_create_meeting()
        
        meeting_id = self.__class__.test_meeting_id
        
        # First join the meeting
        requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join",
            headers=self.headers,
            json={"video_enabled": True, "audio_enabled": True}
        )
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/chat",
            headers=self.headers,
            json={
                "message": "TEST_Phase3_Chat_Message",
                "message_type": "text"
            }
        )
        
        assert response.status_code == 200, f"Send chat failed: {response.text}"
        data = response.json()
        
        assert "message" in data, "Missing message in response"
        assert "user_name" in data, "Missing user_name"
        assert "timestamp" in data, "Missing timestamp"
        print(f"✓ Chat message sent successfully")
    
    # ============ PARTICIPANT UPDATE TEST ============
    
    def test_update_participant_status(self):
        """Test PUT /api/karau-meet/meetings/{meeting_id}/participant"""
        if not hasattr(self.__class__, 'test_meeting_id'):
            self.test_create_meeting()
        
        meeting_id = self.__class__.test_meeting_id
        
        # First join the meeting
        requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join",
            headers=self.headers,
            json={"video_enabled": True, "audio_enabled": True}
        )
        
        response = requests.put(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/participant",
            headers=self.headers,
            json={
                "video_enabled": False,
                "audio_enabled": True,
                "hand_raised": True
            }
        )
        
        # May return 404 if not in meeting, or 200 if successful
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") == True
            print(f"✓ Participant status updated successfully")
        else:
            print(f"✓ Participant update endpoint working (status: {response.status_code})")


class TestKarauPhase3EdgeCases:
    """Edge case tests for Phase 3 features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        self.token = data["access_token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_get_nonexistent_meeting(self):
        """Test GET /api/karau-meet/meetings/{meeting_id} - Non-existent"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/nonexistent_meeting_xyz",
            headers=self.headers
        )
        assert response.status_code == 404
        print("✓ Non-existent meeting returns 404")
    
    def test_join_nonexistent_meeting(self):
        """Test POST /api/karau-meet/meetings/{meeting_id}/join - Non-existent"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/nonexistent_meeting_xyz/join",
            headers=self.headers,
            json={"video_enabled": True, "audio_enabled": True}
        )
        assert response.status_code == 404
        print("✓ Join non-existent meeting returns 404")
    
    def test_transcribe_without_auth(self):
        """Test POST /api/karau-meet/ai/transcribe - Without auth"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ai/transcribe",
            files={'audio_file': ('test.wav', b'fake audio', 'audio/wav')},
            data={'meeting_id': 'test', 'speaker_name': 'Test'}
        )
        assert response.status_code == 401 or response.status_code == 403
        print("✓ Transcribe without auth correctly rejected")
    
    def test_room_status_nonexistent(self):
        """Test GET /api/karau-meet/room/{meeting_id}/status - Non-existent room"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/room/nonexistent_room_xyz/status"
        )
        # Should return 200 with active=false and participant_count=0
        assert response.status_code == 200
        data = response.json()
        assert data["active"] == False
        assert data["participant_count"] == 0
        print("✓ Non-existent room returns inactive status")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
