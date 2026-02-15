"""
AI KARAU Meeting - Recordings API Tests
Tests for browser-side recording metadata endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "Swampdrainer2026!"


class TestKarauRecordingsAPI:
    """Test recordings metadata API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get token
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        data = login_response.json()
        self.token = data.get("access_token")
        self.user = data.get("user")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
        # Create a test meeting for recording tests
        meeting_response = self.session.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            json={"title": "TEST_Recording_Meeting"}
        )
        if meeting_response.status_code == 200:
            self.test_meeting_id = meeting_response.json().get("meeting_id")
        else:
            self.test_meeting_id = "TEST-MEETING-123"
    
    def test_save_recording_metadata(self):
        """Test POST /api/karau-meet/recordings/metadata - Save recording metadata"""
        response = self.session.post(
            f"{BASE_URL}/api/karau-meet/recordings/metadata",
            json={
                "meeting_id": self.test_meeting_id,
                "meeting_title": "TEST_Recording_Meeting",
                "duration_seconds": 120,
                "file_size_bytes": 5242880,  # 5MB
                "file_name": "test-recording-2026.webm"
            }
        )
        
        assert response.status_code == 200, f"Failed to save recording metadata: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert data.get("success") == True
        assert "recording" in data
        
        recording = data["recording"]
        assert recording.get("meeting_id") == self.test_meeting_id
        assert recording.get("meeting_title") == "TEST_Recording_Meeting"
        assert recording.get("duration_seconds") == 120
        assert recording.get("file_size_bytes") == 5242880
        assert recording.get("file_name") == "test-recording-2026.webm"
        assert recording.get("storage_type") == "browser_local"
        assert recording.get("status") == "completed"
        assert "recording_id" in recording
        assert "recorded_at" in recording
        
        # Store recording_id for later tests
        self.__class__.test_recording_id = recording.get("recording_id")
        print(f"✓ Recording metadata saved: {recording.get('recording_id')}")
    
    def test_get_user_recordings(self):
        """Test GET /api/karau-meet/recordings/ - Get user recordings"""
        response = self.session.get(f"{BASE_URL}/api/karau-meet/recordings/")
        
        assert response.status_code == 200, f"Failed to get recordings: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "recordings" in data
        assert "total" in data
        assert "limit" in data
        assert "skip" in data
        
        assert isinstance(data["recordings"], list)
        assert isinstance(data["total"], int)
        
        print(f"✓ Retrieved {len(data['recordings'])} recordings (total: {data['total']})")
    
    def test_get_recording_stats(self):
        """Test GET /api/karau-meet/recordings/stats - Get recording statistics"""
        response = self.session.get(f"{BASE_URL}/api/karau-meet/recordings/stats")
        
        assert response.status_code == 200, f"Failed to get stats: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "total_recordings" in data
        assert "total_duration_seconds" in data
        assert "total_size_bytes" in data
        
        assert isinstance(data["total_recordings"], int)
        assert isinstance(data["total_duration_seconds"], int)
        assert isinstance(data["total_size_bytes"], int)
        
        print(f"✓ Recording stats: {data['total_recordings']} recordings, {data['total_duration_seconds']}s total duration")
    
    def test_get_meeting_recordings(self):
        """Test GET /api/karau-meet/recordings/meeting/{meeting_id} - Get meeting recordings"""
        response = self.session.get(
            f"{BASE_URL}/api/karau-meet/recordings/meeting/{self.test_meeting_id}"
        )
        
        assert response.status_code == 200, f"Failed to get meeting recordings: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "meeting_id" in data
        assert "recordings" in data
        assert "count" in data
        
        assert data["meeting_id"] == self.test_meeting_id
        assert isinstance(data["recordings"], list)
        
        print(f"✓ Meeting {self.test_meeting_id} has {data['count']} recordings")
    
    def test_delete_recording(self):
        """Test DELETE /api/karau-meet/recordings/{recording_id} - Delete recording"""
        # First create a recording to delete
        create_response = self.session.post(
            f"{BASE_URL}/api/karau-meet/recordings/metadata",
            json={
                "meeting_id": "DELETE-TEST-MEETING",
                "meeting_title": "TEST_Delete_Recording",
                "duration_seconds": 60,
                "file_size_bytes": 1048576,
                "file_name": "delete-test.webm"
            }
        )
        
        assert create_response.status_code == 200
        recording_id = create_response.json()["recording"]["recording_id"]
        
        # Now delete it
        delete_response = self.session.delete(
            f"{BASE_URL}/api/karau-meet/recordings/{recording_id}"
        )
        
        assert delete_response.status_code == 200, f"Failed to delete recording: {delete_response.text}"
        data = delete_response.json()
        
        assert data.get("success") == True
        assert data.get("deleted") == recording_id
        
        print(f"✓ Recording {recording_id} deleted successfully")
    
    def test_delete_nonexistent_recording(self):
        """Test DELETE with non-existent recording returns 404"""
        response = self.session.delete(
            f"{BASE_URL}/api/karau-meet/recordings/nonexistent-id-12345"
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent recording returns 404 as expected")
    
    def test_recordings_require_auth(self):
        """Test that recordings endpoints require authentication"""
        # Create a new session without auth
        no_auth_session = requests.Session()
        no_auth_session.headers.update({"Content-Type": "application/json"})
        
        # Test GET recordings
        response = no_auth_session.get(f"{BASE_URL}/api/karau-meet/recordings/")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
        # Test GET stats
        response = no_auth_session.get(f"{BASE_URL}/api/karau-meet/recordings/stats")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
        # Test POST metadata
        response = no_auth_session.post(
            f"{BASE_URL}/api/karau-meet/recordings/metadata",
            json={
                "meeting_id": "test",
                "meeting_title": "test",
                "duration_seconds": 60,
                "file_size_bytes": 1000,
                "file_name": "test.webm"
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
        print("✓ All recordings endpoints require authentication")


class TestWebRTCConfiguration:
    """Test WebRTC configuration with STUN servers"""
    
    def test_stun_servers_in_frontend(self):
        """Verify STUN servers are configured in MeetingRoom.jsx"""
        meeting_room_path = "/app/frontend/src/components/KarauMeet/MeetingRoom.jsx"
        
        with open(meeting_room_path, 'r') as f:
            content = f.read()
        
        # Check for Google STUN servers
        expected_stun_servers = [
            "stun:stun.l.google.com:19302",
            "stun:stun1.l.google.com:19302",
            "stun:stun2.l.google.com:19302",
            "stun:stun3.l.google.com:19302",
            "stun:stun4.l.google.com:19302"
        ]
        
        for server in expected_stun_servers:
            assert server in content, f"Missing STUN server: {server}"
        
        # Check for iceCandidatePoolSize
        assert "iceCandidatePoolSize" in content, "Missing iceCandidatePoolSize configuration"
        
        print(f"✓ All {len(expected_stun_servers)} Google STUN servers configured")
        print("✓ ICE candidate pool size configured")


class TestWebSocketSignaling:
    """Test WebSocket signaling message formats"""
    
    def test_signaling_message_types_in_frontend(self):
        """Verify WebSocket message types are handled in MeetingRoom.jsx"""
        meeting_room_path = "/app/frontend/src/components/KarauMeet/MeetingRoom.jsx"
        
        with open(meeting_room_path, 'r') as f:
            content = f.read()
        
        # Check for required message type handlers
        required_message_types = [
            "case 'offer':",
            "case 'answer':",
            "case 'ice_candidate':",
            "case 'user_joined':",
            "case 'user_left':",
            "case 'chat':",
            "case 'room_state':"
        ]
        
        for msg_type in required_message_types:
            assert msg_type in content, f"Missing message handler: {msg_type}"
        
        print(f"✓ All {len(required_message_types)} WebSocket message types handled")
    
    def test_signaling_message_sending(self):
        """Verify WebSocket message sending format"""
        meeting_room_path = "/app/frontend/src/components/KarauMeet/MeetingRoom.jsx"
        
        with open(meeting_room_path, 'r') as f:
            content = f.read()
        
        # Check for proper message sending format
        assert "type: 'offer'" in content, "Missing offer message sending"
        assert "type: 'answer'" in content, "Missing answer message sending"
        assert "type: 'ice_candidate'" in content, "Missing ICE candidate message sending"
        assert "type: 'chat'" in content, "Missing chat message sending"
        
        print("✓ WebSocket message sending formats verified")


class TestRecordingIntegration:
    """Test recording saves metadata to backend"""
    
    def test_recording_metadata_save_in_frontend(self):
        """Verify recording metadata is saved to backend after completion"""
        meeting_room_path = "/app/frontend/src/components/KarauMeet/MeetingRoom.jsx"
        
        with open(meeting_room_path, 'r') as f:
            content = f.read()
        
        # Check for MediaRecorder usage
        assert "MediaRecorder" in content, "Missing MediaRecorder usage"
        assert "mediaRecorderRef" in content, "Missing mediaRecorderRef"
        
        # Check for recording metadata save
        assert "/api/karau-meet/recordings/metadata" in content, "Missing recording metadata API call"
        
        # Check for recording data being sent
        assert "meeting_id" in content, "Missing meeting_id in recording data"
        assert "duration_seconds" in content, "Missing duration_seconds in recording data"
        assert "file_size_bytes" in content, "Missing file_size_bytes in recording data"
        assert "file_name" in content, "Missing file_name in recording data"
        
        print("✓ Recording metadata save to backend verified")
    
    def test_recording_download_trigger(self):
        """Verify recording download triggers automatically"""
        meeting_room_path = "/app/frontend/src/components/KarauMeet/MeetingRoom.jsx"
        
        with open(meeting_room_path, 'r') as f:
            content = f.read()
        
        # Check for download trigger
        assert "URL.createObjectURL" in content, "Missing blob URL creation"
        assert ".download" in content, "Missing download attribute"
        assert "a.click()" in content or "click()" in content, "Missing download trigger"
        
        print("✓ Recording download trigger verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
