"""
E2E Test for AI KARAU Meeting - Multi-user Video Call Features
"""
import pytest
import requests
import os
import json
import websocket
import threading
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://audio-coverage-tools.preview.emergentagent.com')

class TestKarauMeetingE2E:
    """E2E tests for AI KARAU Meeting features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get("access_token")
        self.user = data.get("user")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        print(f"✓ Logged in as {self.user.get('email')}")
    
    def test_01_health_check(self):
        """Test API health endpoint"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ API Health: {data.get('status')}")
    
    def test_02_ice_servers_endpoint(self):
        """Test ICE servers endpoint returns STUN/TURN configuration"""
        response = self.session.get(f"{BASE_URL}/api/karau-meet/ice-servers")
        assert response.status_code == 200
        data = response.json()
        
        assert "ice_servers" in data
        assert len(data["ice_servers"]) > 0
        
        # Check for STUN servers
        stun_servers = [s for s in data["ice_servers"] if "stun:" in str(s.get("urls", ""))]
        print(f"✓ STUN servers: {len(stun_servers)}")
        
        # Check for TURN servers
        turn_servers = [s for s in data["ice_servers"] if "turn:" in str(s.get("urls", ""))]
        print(f"✓ TURN servers: {len(turn_servers)}")
        
        # Check if TURN is enabled
        if data.get("turn_enabled"):
            print("✓ TURN servers enabled (Xirsys)")
        else:
            print("⚠ TURN servers not enabled (using STUN only)")
    
    def test_03_create_meeting(self):
        """Test creating a new meeting"""
        response = self.session.post(f"{BASE_URL}/api/karau-meet/meetings", json={
            "title": "E2E Test Meeting"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "meeting_id" in data
        self.meeting_id = data["meeting_id"]
        print(f"✓ Meeting created: {self.meeting_id}")
        
        # Store for other tests
        TestKarauMeetingE2E.test_meeting_id = self.meeting_id
    
    def test_04_list_meetings(self):
        """Test listing user's meetings"""
        response = self.session.get(f"{BASE_URL}/api/karau-meet/meetings")
        assert response.status_code == 200
        data = response.json()
        
        assert "meetings" in data
        print(f"✓ Found {len(data['meetings'])} meetings")
    
    def test_05_join_meeting(self):
        """Test joining a meeting"""
        meeting_id = getattr(TestKarauMeetingE2E, 'test_meeting_id', None)
        if not meeting_id:
            pytest.skip("No meeting ID from previous test")
        
        response = self.session.post(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join", json={
            "video_enabled": True,
            "audio_enabled": True
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "meeting" in data
        assert "ice_servers" in data
        print(f"✓ Joined meeting: {meeting_id}")
    
    def test_06_get_meeting_participants(self):
        """Test getting meeting participants"""
        meeting_id = getattr(TestKarauMeetingE2E, 'test_meeting_id', None)
        if not meeting_id:
            pytest.skip("No meeting ID from previous test")
        
        response = self.session.get(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/participants")
        assert response.status_code == 200
        data = response.json()
        
        assert "participants" in data
        print(f"✓ Participants: {len(data['participants'])}")
    
    def test_07_room_status(self):
        """Test room status endpoint"""
        meeting_id = getattr(TestKarauMeetingE2E, 'test_meeting_id', None)
        if not meeting_id:
            pytest.skip("No meeting ID from previous test")
        
        response = self.session.get(f"{BASE_URL}/api/karau-meet/room/{meeting_id}/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "meeting_id" in data
        assert "active" in data
        print(f"✓ Room status: active={data.get('active')}, participants={data.get('participant_count')}")
    
    def test_08_send_chat_message(self):
        """Test sending chat message in meeting"""
        meeting_id = getattr(TestKarauMeetingE2E, 'test_meeting_id', None)
        if not meeting_id:
            pytest.skip("No meeting ID from previous test")
        
        response = self.session.post(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/chat", json={
            "message": "Hello from E2E test!",
            "message_type": "text"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data or "user_name" in data
        print("✓ Chat message sent")
    
    def test_09_accessibility_settings(self):
        """Test accessibility settings endpoints"""
        # Get settings
        response = self.session.get(f"{BASE_URL}/api/karau-meet/accessibility/settings")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Accessibility settings retrieved")
        
        # Update settings
        response = self.session.put(f"{BASE_URL}/api/karau-meet/accessibility/settings", json={
            "high_contrast": True
        })
        assert response.status_code == 200
        print("✓ Accessibility settings updated")
    
    def test_10_security_compliance(self):
        """Test security compliance endpoint"""
        response = self.session.get(f"{BASE_URL}/api/karau-meet/security/compliance")
        assert response.status_code == 200
        data = response.json()
        
        assert "gdpr" in data
        assert "hipaa" in data
        print(f"✓ GDPR compliant: {data['gdpr'].get('compliant')}")
        print(f"✓ HIPAA compliant: {data['hipaa'].get('compliant')}")
    
    def test_11_recordings_stats(self):
        """Test recordings stats endpoint"""
        response = self.session.get(f"{BASE_URL}/api/karau-meet/recordings/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_recordings" in data
        print(f"✓ Recordings: {data.get('total_recordings')}, Duration: {data.get('total_duration_seconds')}s")
    
    def test_12_recordings_list(self):
        """Test recordings list endpoint"""
        response = self.session.get(f"{BASE_URL}/api/karau-meet/recordings/")
        assert response.status_code == 200
        data = response.json()
        
        assert "recordings" in data
        print(f"✓ Found {len(data['recordings'])} recordings")
    
    def test_13_ai_transcript(self):
        """Test AI transcript endpoint"""
        meeting_id = getattr(TestKarauMeetingE2E, 'test_meeting_id', None)
        if not meeting_id:
            pytest.skip("No meeting ID from previous test")
        
        response = self.session.get(f"{BASE_URL}/api/karau-meet/ai/transcript/{meeting_id}")
        # May return 200 or 404 if no transcript yet
        assert response.status_code in [200, 404]
        print(f"✓ AI transcript endpoint: {response.status_code}")
    
    def test_14_ai_action_items(self):
        """Test AI action items endpoint"""
        meeting_id = getattr(TestKarauMeetingE2E, 'test_meeting_id', None)
        if not meeting_id:
            pytest.skip("No meeting ID from previous test")
        
        response = self.session.get(f"{BASE_URL}/api/karau-meet/ai/action-items/{meeting_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert "action_items" in data
        print(f"✓ Action items: {len(data['action_items'])}")
    
    def test_15_leave_meeting(self):
        """Test leaving a meeting"""
        meeting_id = getattr(TestKarauMeetingE2E, 'test_meeting_id', None)
        if not meeting_id:
            pytest.skip("No meeting ID from previous test")
        
        response = self.session.post(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/leave")
        assert response.status_code == 200
        print("✓ Left meeting successfully")


class TestWebSocketSignaling:
    """Test WebSocket signaling for WebRTC"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200
        data = response.json()
        self.token = data.get("access_token")
        self.user = data.get("user")
    
    def test_websocket_connection(self):
        """Test WebSocket connection for meeting signaling"""
        # Create a meeting first
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        response = self.session.post(f"{BASE_URL}/api/karau-meet/meetings", json={
            "title": "WebSocket Test Meeting"
        })
        assert response.status_code == 200
        meeting_id = response.json()["meeting_id"]
        
        # Build WebSocket URL
        ws_url = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        ws_url = f"{ws_url}/api/karau-meet/ws/{meeting_id}?token={self.token}&user_name=TestUser&is_host=true"
        
        # Test WebSocket connection
        messages_received = []
        connection_success = [False]
        
        def on_message(ws, message):
            messages_received.append(json.loads(message))
            print(f"✓ WebSocket message received: {message[:100]}...")
        
        def on_error(ws, error):
            print(f"⚠ WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print(f"WebSocket closed: {close_status_code}")
        
        def on_open(ws):
            connection_success[0] = True
            print("✓ WebSocket connected successfully")
            # Send a ping
            ws.send(json.dumps({"type": "ping"}))
            time.sleep(1)
            ws.close()
        
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        # Run WebSocket in a thread with timeout
        ws_thread = threading.Thread(target=ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        ws_thread.join(timeout=5)
        
        assert connection_success[0], "WebSocket connection failed"
        print(f"✓ WebSocket test passed, received {len(messages_received)} messages")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
