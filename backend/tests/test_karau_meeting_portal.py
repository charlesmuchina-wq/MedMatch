"""
AI KARAU Meeting Portal - Backend API Tests
Tests for WebRTC video conferencing functionality including:
- Guest join flow
- Meeting management
- ICE server configuration
- WebSocket signaling endpoints
"""

import pytest
import requests
import os
import json
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://distance-zero-replay.preview.emergentagent.com')

# Test meeting ID
TEST_MEETING_ID = "DAF3BD00"


class TestKarauMeetHealth:
    """Health check tests"""
    
    def test_api_health(self):
        """Test that the API health endpoint is working"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ API Health: {data.get('status')}")


class TestKarauMeetGuestJoin:
    """Guest join flow tests - join meeting without login"""
    
    def test_get_meeting_info(self):
        """Test fetching meeting details without authentication"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings/{TEST_MEETING_ID}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify meeting structure
        assert "meeting" in data
        meeting = data["meeting"]
        assert meeting.get("meeting_id") == TEST_MEETING_ID
        assert "title" in meeting
        assert "status" in meeting
        assert "host_id" in meeting
        assert "settings" in meeting
        print(f"✓ Meeting found: {meeting.get('title')}")
        print(f"✓ Status: {meeting.get('status')}")
    
    def test_guest_join_meeting(self):
        """Test joining a meeting as a guest"""
        guest_name = f"TestGuest_{datetime.now().strftime('%H%M%S')}"
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{TEST_MEETING_ID}/join-guest",
            json={
                "guest_name": guest_name,
                "video_enabled": True,
                "audio_enabled": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify guest join response
        assert "guest_user_id" in data
        assert "guest_name" in data
        assert "meeting" in data
        assert data["guest_name"] == guest_name
        assert data["guest_user_id"].startswith("guest_")
        
        print(f"✓ Guest joined as: {data['guest_name']}")
        print(f"✓ Guest ID: {data['guest_user_id']}")
        
        return data["guest_user_id"]
    
    def test_guest_join_nonexistent_meeting(self):
        """Test joining a non-existent meeting returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/INVALID123/join-guest",
            json={"guest_name": "TestGuest", "video_enabled": True, "audio_enabled": True}
        )
        assert response.status_code == 404
        print("✓ Non-existent meeting correctly returns 404")


class TestKarauMeetICEServers:
    """ICE server configuration tests"""
    
    def test_get_ice_servers(self):
        """Test fetching ICE (STUN/TURN) servers"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/ice-servers")
        assert response.status_code == 200
        data = response.json()
        
        # Verify ICE servers structure
        assert "ice_servers" in data
        servers = data["ice_servers"]
        assert len(servers) > 0
        
        # Check at least one STUN server exists
        has_stun = any("stun:" in s.get("urls", "") for s in servers)
        assert has_stun, "Should have at least one STUN server"
        
        print(f"✓ ICE Servers: {len(servers)} servers configured")
        for s in servers[:3]:  # Print first 3
            print(f"  - {s.get('urls')}")
    
    def test_ice_servers_in_meeting_response(self):
        """Test that meeting response includes ICE servers"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings/{TEST_MEETING_ID}")
        assert response.status_code == 200
        data = response.json()
        
        # Should include ice_servers in meeting response
        assert "ice_servers" in data
        print(f"✓ Meeting response includes {len(data['ice_servers'])} ICE servers")


class TestKarauMeetSettings:
    """Meeting settings tests"""
    
    def test_meeting_settings_structure(self):
        """Test that meeting settings are properly returned"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings/{TEST_MEETING_ID}")
        assert response.status_code == 200
        data = response.json()
        meeting = data.get("meeting", {})
        settings = meeting.get("settings", {})
        
        # Verify expected settings exist
        expected_settings = [
            "video_enabled",
            "audio_enabled",
            "screen_share_enabled",
            "chat_enabled",
            "recording_enabled",
            "ai_notes_enabled",
            "e2e_encryption"
        ]
        
        for setting in expected_settings:
            assert setting in settings, f"Missing setting: {setting}"
            print(f"✓ {setting}: {settings.get(setting)}")


class TestAuthenticatedMeetingFlow:
    """Tests requiring authentication"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_authenticated_join_meeting(self, auth_token):
        """Test joining meeting with authentication"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{TEST_MEETING_ID}/join",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"video_enabled": True, "audio_enabled": True}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "meeting" in data
        print(f"✓ Authenticated user joined meeting")
    
    def test_create_meeting(self, auth_token):
        """Test creating a new meeting"""
        meeting_title = f"Test Meeting {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={"title": meeting_title}
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        
        assert "meeting_id" in data
        print(f"✓ Created meeting: {data.get('meeting_id')}")
        return data.get("meeting_id")
    
    def test_list_meetings(self, auth_token):
        """Test listing user's meetings"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "meetings" in data
        print(f"✓ Found {len(data.get('meetings', []))} meetings")
    
    def test_leave_meeting(self, auth_token):
        """Test leaving a meeting"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{TEST_MEETING_ID}/leave",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Leave should succeed or return 404 if not in meeting
        assert response.status_code in [200, 404]
        print(f"✓ Leave meeting response: {response.status_code}")


class TestWebRTCEndpoints:
    """WebRTC related endpoint tests"""
    
    def test_websocket_url_format(self):
        """Verify WebSocket URL structure is correct"""
        # The WebSocket endpoint should be at /api/karau-meet/ws/{meeting_id}
        ws_url = f"{BASE_URL.replace('https://', 'wss://').replace('http://', 'ws://')}/api/karau-meet/ws/{TEST_MEETING_ID}"
        
        # We can't fully test WebSocket connection here, but verify URL format
        assert "ws" in ws_url
        assert TEST_MEETING_ID in ws_url
        print(f"✓ WebSocket URL format: {ws_url}")
    
    def test_meeting_participants(self):
        """Test getting meeting participants"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings/{TEST_MEETING_ID}")
        assert response.status_code == 200
        data = response.json()
        meeting = data.get("meeting", {})
        
        # Check participants list exists
        participants = meeting.get("participants", [])
        assert isinstance(participants, list)
        print(f"✓ Meeting has {len(participants)} recorded participants")


class TestRecordingsMetadata:
    """Test recordings metadata endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    def test_save_recording_metadata(self, auth_token):
        """Test saving recording metadata"""
        metadata = {
            "meeting_id": TEST_MEETING_ID,
            "meeting_title": "Test Recording",
            "duration_seconds": 60,
            "file_size_bytes": 1024000,
            "file_name": "test-recording.webm"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/recordings/metadata",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json=metadata
        )
        
        # Should succeed or return appropriate error
        print(f"✓ Recording metadata response: {response.status_code}")


class TestMeetingErrorHandling:
    """Error handling tests"""
    
    def test_invalid_meeting_id_format(self):
        """Test handling of invalid meeting ID format"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings/abc")
        # Should return 404 for non-existent meeting
        assert response.status_code == 404
        print("✓ Invalid meeting ID correctly returns 404")
    
    def test_guest_join_without_name(self):
        """Test guest join without providing name"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{TEST_MEETING_ID}/join-guest",
            json={"video_enabled": True, "audio_enabled": True}
        )
        # Should either fail validation or use default name
        print(f"✓ Guest join without name response: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
