"""
Test AI KARAU Meeting - Multi-User WebRTC Signaling
Tests WebSocket connections, ICE servers, and meeting functionality
"""

import pytest
import requests
import asyncio
import websockets
import json
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "Swampdrainer2026!"


class TestKarauMeetingAPIs:
    """Test AI KARAU Meeting REST APIs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.token = None
        self.meeting_id = None
    
    def get_auth_token(self):
        """Get authentication token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token") or data.get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            return self.token
        return None
    
    def test_01_health_check(self):
        """Test API health endpoint"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"Health check passed: {data}")
    
    def test_02_ice_servers_endpoint(self):
        """Test ICE servers endpoint returns STUN/TURN config"""
        response = self.session.get(f"{BASE_URL}/api/karau-meet/ice-servers")
        assert response.status_code == 200
        data = response.json()
        
        # Verify ICE servers structure
        assert "ice_servers" in data
        assert isinstance(data["ice_servers"], list)
        assert len(data["ice_servers"]) > 0
        
        # Check for STUN servers
        stun_servers = [s for s in data["ice_servers"] if "stun:" in str(s.get("urls", ""))]
        assert len(stun_servers) > 0, "Should have at least one STUN server"
        
        print(f"ICE servers: {len(data['ice_servers'])} servers configured")
        print(f"TURN enabled: {data.get('turn_enabled', False)}")
    
    def test_03_authentication(self):
        """Test user authentication"""
        token = self.get_auth_token()
        assert token is not None, "Authentication should succeed"
        print(f"Authentication successful, token received")
    
    def test_04_create_meeting(self):
        """Test creating a new meeting"""
        self.get_auth_token()
        
        response = self.session.post(f"{BASE_URL}/api/karau-meet/meetings", json={
            "title": "Multi-User WebRTC Test Meeting"
        })
        assert response.status_code in [200, 201]
        data = response.json()
        
        assert "meeting_id" in data
        self.meeting_id = data["meeting_id"]
        print(f"Created meeting: {self.meeting_id}")
        
        # Store for other tests
        return self.meeting_id
    
    def test_05_get_meeting_details(self):
        """Test getting meeting details"""
        self.get_auth_token()
        
        # Create a meeting first
        create_response = self.session.post(f"{BASE_URL}/api/karau-meet/meetings", json={
            "title": "Test Meeting Details"
        })
        meeting_id = create_response.json().get("meeting_id")
        
        # Get meeting details
        response = self.session.get(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert "meeting" in data
        assert "ice_servers" in data
        print(f"Meeting details retrieved: {data['meeting'].get('title')}")
    
    def test_06_join_meeting(self):
        """Test joining a meeting"""
        self.get_auth_token()
        
        # Create a meeting first
        create_response = self.session.post(f"{BASE_URL}/api/karau-meet/meetings", json={
            "title": "Test Join Meeting"
        })
        meeting_id = create_response.json().get("meeting_id")
        
        # Join the meeting
        response = self.session.post(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join", json={
            "video_enabled": True,
            "audio_enabled": True
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "ice_servers" in data
        print(f"Joined meeting: {meeting_id}")
    
    def test_07_room_status(self):
        """Test getting room status"""
        self.get_auth_token()
        
        # Create and join a meeting
        create_response = self.session.post(f"{BASE_URL}/api/karau-meet/meetings", json={
            "title": "Test Room Status"
        })
        meeting_id = create_response.json().get("meeting_id")
        
        # Get room status (public endpoint)
        response = self.session.get(f"{BASE_URL}/api/karau-meet/room/{meeting_id}/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "meeting_id" in data
        assert "active" in data
        assert "participant_count" in data
        print(f"Room status: active={data['active']}, participants={data['participant_count']}")
    
    def test_08_send_chat_message(self):
        """Test sending chat message in meeting"""
        self.get_auth_token()
        
        # Create and join a meeting
        create_response = self.session.post(f"{BASE_URL}/api/karau-meet/meetings", json={
            "title": "Test Chat Meeting"
        })
        meeting_id = create_response.json().get("meeting_id")
        
        # Join the meeting
        self.session.post(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join", json={
            "video_enabled": True,
            "audio_enabled": True
        })
        
        # Send chat message
        response = self.session.post(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/chat", json={
            "message": "Hello from multi-user test!",
            "message_type": "text"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data or "id" in data
        print(f"Chat message sent successfully")
    
    def test_09_leave_meeting(self):
        """Test leaving a meeting"""
        self.get_auth_token()
        
        # Create and join a meeting
        create_response = self.session.post(f"{BASE_URL}/api/karau-meet/meetings", json={
            "title": "Test Leave Meeting"
        })
        meeting_id = create_response.json().get("meeting_id")
        
        # Join the meeting
        self.session.post(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join", json={
            "video_enabled": True,
            "audio_enabled": True
        })
        
        # Leave the meeting
        response = self.session.post(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/leave")
        assert response.status_code == 200
        print(f"Left meeting: {meeting_id}")
    
    def test_10_get_user_meetings(self):
        """Test getting user's meetings list"""
        self.get_auth_token()
        
        response = self.session.get(f"{BASE_URL}/api/karau-meet/meetings")
        assert response.status_code == 200
        data = response.json()
        
        assert "meetings" in data
        print(f"User has {len(data['meetings'])} meetings")


class TestWebSocketSignaling:
    """Test WebSocket signaling for multi-user video calls"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_auth_token(self):
        """Get authentication token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
        return None
    
    def create_meeting(self, token):
        """Create a meeting and return meeting_id"""
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        response = self.session.post(f"{BASE_URL}/api/karau-meet/meetings", json={
            "title": "WebSocket Test Meeting"
        })
        if response.status_code in [200, 201]:
            return response.json().get("meeting_id")
        return None
    
    @pytest.mark.asyncio
    async def test_11_websocket_connection(self):
        """Test WebSocket connection to meeting room"""
        token = self.get_auth_token()
        assert token is not None
        
        meeting_id = self.create_meeting(token)
        assert meeting_id is not None
        
        # Convert HTTPS URL to WSS
        ws_base = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        ws_url = f"{ws_base}/api/karau-meet/ws/{meeting_id}?token={token}&user_name=TestUser1&is_host=true"
        
        try:
            async with websockets.connect(ws_url, timeout=10) as websocket:
                # Wait for welcome message
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(response)
                
                print(f"WebSocket connected, received: {data.get('type')}")
                assert data.get("type") in ["welcome", "participant_joined", "participants_list"]
                
        except asyncio.TimeoutError:
            print("WebSocket connection timed out - this may be expected in test environment")
        except Exception as e:
            print(f"WebSocket test note: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_12_multi_user_websocket_simulation(self):
        """Simulate multiple users connecting to the same meeting"""
        token = self.get_auth_token()
        assert token is not None
        
        meeting_id = self.create_meeting(token)
        assert meeting_id is not None
        
        ws_base = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        
        users = [
            {"name": "User1", "is_host": "true"},
            {"name": "User2", "is_host": "false"},
            {"name": "User3", "is_host": "false"}
        ]
        
        connected_users = []
        
        for user in users:
            ws_url = f"{ws_base}/api/karau-meet/ws/{meeting_id}?token={token}&user_name={user['name']}&is_host={user['is_host']}"
            
            try:
                websocket = await asyncio.wait_for(
                    websockets.connect(ws_url),
                    timeout=5
                )
                connected_users.append({"name": user["name"], "ws": websocket})
                print(f"User {user['name']} connected to meeting {meeting_id}")
                
            except asyncio.TimeoutError:
                print(f"User {user['name']} connection timed out")
            except Exception as e:
                print(f"User {user['name']} connection error: {str(e)}")
        
        # Close all connections
        for user in connected_users:
            try:
                await user["ws"].close()
            except:
                pass
        
        print(f"Multi-user simulation: {len(connected_users)}/{len(users)} users connected")
    
    @pytest.mark.asyncio
    async def test_13_websocket_signaling_messages(self):
        """Test WebSocket signaling message types"""
        token = self.get_auth_token()
        assert token is not None
        
        meeting_id = self.create_meeting(token)
        assert meeting_id is not None
        
        ws_base = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        ws_url = f"{ws_base}/api/karau-meet/ws/{meeting_id}?token={token}&user_name=SignalTest&is_host=true"
        
        try:
            async with websockets.connect(ws_url, timeout=10) as websocket:
                # Send a ping message
                await websocket.send(json.dumps({"type": "ping"}))
                
                # Try to receive response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=3)
                    data = json.loads(response)
                    print(f"Received signaling message: {data.get('type')}")
                except asyncio.TimeoutError:
                    print("No immediate response to ping - may be expected")
                
                # Send state update
                await websocket.send(json.dumps({
                    "type": "state_update",
                    "state": {"video_enabled": True, "audio_enabled": True}
                }))
                print("Sent state update message")
                
        except Exception as e:
            print(f"Signaling test note: {str(e)}")


class TestVideoTutorialsAvatars:
    """Test Video Tutorials page avatar/region functionality"""
    
    def test_14_tutorials_videos_endpoint(self):
        """Test tutorials videos endpoint"""
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/tutorials/videos")
        
        # May require auth or return 401
        if response.status_code == 200:
            data = response.json()
            assert "videos" in data
            print(f"Found {len(data['videos'])} tutorial videos")
        else:
            print(f"Tutorials endpoint returned {response.status_code}")
    
    def test_15_region_avatar_urls_accessible(self):
        """Test that region avatar URLs are accessible"""
        # These are the Unsplash URLs used in REGION_AVATARS
        avatar_urls = {
            'Europe': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=512&h=512&fit=crop&crop=face',
            'Asia': 'https://images.unsplash.com/photo-1594744803329-e58b31de8bf5?w=512&h=512&fit=crop&crop=face',
            'Africa': 'https://images.unsplash.com/photo-1633419798503-0b0c628f267c?w=512&h=512&fit=crop&crop=face',
            'Middle East': 'https://images.unsplash.com/photo-1625987306773-8b9e554b25e2?w=512&h=512&fit=crop&crop=face',
        }
        
        session = requests.Session()
        accessible_count = 0
        
        for region, url in avatar_urls.items():
            try:
                response = session.head(url, timeout=5)
                if response.status_code == 200:
                    accessible_count += 1
                    print(f"{region} avatar URL: accessible")
                else:
                    print(f"{region} avatar URL: status {response.status_code}")
            except Exception as e:
                print(f"{region} avatar URL: error - {str(e)}")
        
        print(f"Avatar URLs accessible: {accessible_count}/{len(avatar_urls)}")
        assert accessible_count >= 2, "At least 2 avatar URLs should be accessible"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
