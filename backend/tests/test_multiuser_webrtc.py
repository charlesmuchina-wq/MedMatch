"""
Multi-User WebRTC WebSocket Signaling Tests
Tests 3 users in same meeting with:
- User join notifications broadcast
- Chat message broadcast to all
- WebRTC offer/answer exchange
- ICE candidate forwarding
- Audio/video state updates (mute/unmute)
- Screen sharing state updates
"""
import asyncio
import json
import os
import pytest
import requests
import websockets
import uuid

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
WS_BASE_URL = BASE_URL.replace('https://', 'wss://').replace('http://', 'ws://')


def get_auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    return None


class TestMultiUserWebRTC:
    """Test multi-user WebRTC signaling with 3 users"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.token = get_auth_token()
        self.meeting_id = f"test-multiuser-{uuid.uuid4().hex[:8]}"
        assert self.token, "Failed to get auth token"
    
    @pytest.mark.asyncio
    async def test_three_users_join_notifications(self):
        """Test that all 3 users receive join notifications"""
        ws_url_host = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?token={self.token}&user_name=Host&is_host=true"
        ws_url_guest1 = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?user_name=Guest1&is_host=false"
        ws_url_guest2 = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?user_name=Guest2&is_host=false"
        
        async with websockets.connect(ws_url_host, close_timeout=10) as ws_host:
            # Host joins - receives room_state
            msg = await asyncio.wait_for(ws_host.recv(), timeout=5)
            data = json.loads(msg)
            assert data["type"] == "room_state", f"Expected room_state, got {data['type']}"
            assert data["meeting_id"] == self.meeting_id
            host_id = data["your_id"]
            print(f"Host joined with ID: {host_id}")
            
            async with websockets.connect(ws_url_guest1, close_timeout=10) as ws_guest1:
                # Guest1 joins - receives room_state
                msg = await asyncio.wait_for(ws_guest1.recv(), timeout=5)
                data = json.loads(msg)
                assert data["type"] == "room_state"
                guest1_id = data["your_id"]
                print(f"Guest1 joined with ID: {guest1_id}")
                
                # Host should receive user_joined for Guest1
                msg = await asyncio.wait_for(ws_host.recv(), timeout=5)
                data = json.loads(msg)
                assert data["type"] == "user_joined", f"Expected user_joined, got {data['type']}"
                assert data["user_name"] == "Guest1"
                assert len(data["participants"]) == 2
                print("Host received Guest1 join notification")
                
                async with websockets.connect(ws_url_guest2, close_timeout=10) as ws_guest2:
                    # Guest2 joins - receives room_state
                    msg = await asyncio.wait_for(ws_guest2.recv(), timeout=5)
                    data = json.loads(msg)
                    assert data["type"] == "room_state"
                    guest2_id = data["your_id"]
                    assert len(data["participants"]) == 3  # All 3 users
                    print(f"Guest2 joined with ID: {guest2_id}")
                    
                    # Host should receive user_joined for Guest2
                    msg = await asyncio.wait_for(ws_host.recv(), timeout=5)
                    data = json.loads(msg)
                    assert data["type"] == "user_joined"
                    assert data["user_name"] == "Guest2"
                    print("Host received Guest2 join notification")
                    
                    # Guest1 should also receive user_joined for Guest2
                    msg = await asyncio.wait_for(ws_guest1.recv(), timeout=5)
                    data = json.loads(msg)
                    assert data["type"] == "user_joined"
                    assert data["user_name"] == "Guest2"
                    print("Guest1 received Guest2 join notification")
                    
                    print("PASS: All 3 users joined and received notifications")
    
    @pytest.mark.asyncio
    async def test_chat_broadcast_to_all_three_users(self):
        """Test chat message broadcast to all 3 users"""
        ws_url_host = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?token={self.token}&user_name=Host&is_host=true"
        ws_url_guest1 = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?user_name=Guest1&is_host=false"
        ws_url_guest2 = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?user_name=Guest2&is_host=false"
        
        async with websockets.connect(ws_url_host, close_timeout=10) as ws_host:
            await asyncio.wait_for(ws_host.recv(), timeout=5)  # room_state
            
            async with websockets.connect(ws_url_guest1, close_timeout=10) as ws_guest1:
                await asyncio.wait_for(ws_guest1.recv(), timeout=5)  # room_state
                await asyncio.wait_for(ws_host.recv(), timeout=5)  # user_joined
                
                async with websockets.connect(ws_url_guest2, close_timeout=10) as ws_guest2:
                    await asyncio.wait_for(ws_guest2.recv(), timeout=5)  # room_state
                    await asyncio.wait_for(ws_host.recv(), timeout=5)  # user_joined
                    await asyncio.wait_for(ws_guest1.recv(), timeout=5)  # user_joined
                    
                    # Host sends chat message
                    chat_msg = {"type": "chat", "message": "Hello everyone!"}
                    await ws_host.send(json.dumps(chat_msg))
                    print("Host sent chat message")
                    
                    # Guest1 should receive chat
                    msg = await asyncio.wait_for(ws_guest1.recv(), timeout=5)
                    data = json.loads(msg)
                    assert data["type"] == "chat"
                    assert data["message"] == "Hello everyone!"
                    assert data["from_name"] == "Host"
                    print("Guest1 received chat message")
                    
                    # Guest2 should receive chat
                    msg = await asyncio.wait_for(ws_guest2.recv(), timeout=5)
                    data = json.loads(msg)
                    assert data["type"] == "chat"
                    assert data["message"] == "Hello everyone!"
                    print("Guest2 received chat message")
                    
                    print("PASS: Chat broadcast to all 3 users")
    
    @pytest.mark.asyncio
    async def test_webrtc_offer_answer_exchange(self):
        """Test WebRTC offer/answer exchange between peers"""
        ws_url_host = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?token={self.token}&user_name=Host&is_host=true"
        ws_url_guest1 = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?user_name=Guest1&is_host=false"
        
        async with websockets.connect(ws_url_host, close_timeout=10) as ws_host:
            msg = await asyncio.wait_for(ws_host.recv(), timeout=5)
            host_data = json.loads(msg)
            host_id = host_data["your_id"]
            
            async with websockets.connect(ws_url_guest1, close_timeout=10) as ws_guest1:
                msg = await asyncio.wait_for(ws_guest1.recv(), timeout=5)
                guest1_data = json.loads(msg)
                guest1_id = guest1_data["your_id"]
                
                await asyncio.wait_for(ws_host.recv(), timeout=5)  # user_joined
                
                # Host sends WebRTC offer to Guest1
                offer = {
                    "type": "offer",
                    "target": guest1_id,
                    "offer": {
                        "type": "offer",
                        "sdp": "v=0\r\no=- 123456 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n"
                    }
                }
                await ws_host.send(json.dumps(offer))
                print(f"Host sent offer to Guest1 ({guest1_id})")
                
                # Guest1 should receive the offer
                msg = await asyncio.wait_for(ws_guest1.recv(), timeout=5)
                data = json.loads(msg)
                assert data["type"] == "offer"
                assert data["from_user"] == host_id
                assert "offer" in data
                print("Guest1 received offer from Host")
                
                # Guest1 sends answer back to Host
                answer = {
                    "type": "answer",
                    "target": host_id,
                    "answer": {
                        "type": "answer",
                        "sdp": "v=0\r\no=- 654321 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n"
                    }
                }
                await ws_guest1.send(json.dumps(answer))
                print(f"Guest1 sent answer to Host ({host_id})")
                
                # Host should receive the answer
                msg = await asyncio.wait_for(ws_host.recv(), timeout=5)
                data = json.loads(msg)
                assert data["type"] == "answer"
                assert data["from_user"] == guest1_id
                assert "answer" in data
                print("Host received answer from Guest1")
                
                print("PASS: WebRTC offer/answer exchange successful")
    
    @pytest.mark.asyncio
    async def test_ice_candidate_forwarding(self):
        """Test ICE candidate forwarding between peers"""
        ws_url_host = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?token={self.token}&user_name=Host&is_host=true"
        ws_url_guest1 = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?user_name=Guest1&is_host=false"
        
        async with websockets.connect(ws_url_host, close_timeout=10) as ws_host:
            msg = await asyncio.wait_for(ws_host.recv(), timeout=5)
            host_data = json.loads(msg)
            host_id = host_data["your_id"]
            
            async with websockets.connect(ws_url_guest1, close_timeout=10) as ws_guest1:
                msg = await asyncio.wait_for(ws_guest1.recv(), timeout=5)
                guest1_data = json.loads(msg)
                guest1_id = guest1_data["your_id"]
                
                await asyncio.wait_for(ws_host.recv(), timeout=5)  # user_joined
                
                # Host sends ICE candidate to Guest1
                ice_candidate = {
                    "type": "ice_candidate",
                    "target": guest1_id,
                    "candidate": {
                        "candidate": "candidate:1 1 UDP 2130706431 192.168.1.1 54321 typ host",
                        "sdpMid": "0",
                        "sdpMLineIndex": 0
                    }
                }
                await ws_host.send(json.dumps(ice_candidate))
                print(f"Host sent ICE candidate to Guest1")
                
                # Guest1 should receive the ICE candidate
                msg = await asyncio.wait_for(ws_guest1.recv(), timeout=5)
                data = json.loads(msg)
                assert data["type"] == "ice_candidate"
                assert data["from_user"] == host_id
                assert "candidate" in data
                print("Guest1 received ICE candidate from Host")
                
                # Guest1 sends ICE candidate back to Host
                ice_candidate2 = {
                    "type": "ice_candidate",
                    "target": host_id,
                    "candidate": {
                        "candidate": "candidate:2 1 UDP 2130706431 192.168.1.2 54322 typ host",
                        "sdpMid": "0",
                        "sdpMLineIndex": 0
                    }
                }
                await ws_guest1.send(json.dumps(ice_candidate2))
                print(f"Guest1 sent ICE candidate to Host")
                
                # Host should receive the ICE candidate
                msg = await asyncio.wait_for(ws_host.recv(), timeout=5)
                data = json.loads(msg)
                assert data["type"] == "ice_candidate"
                assert data["from_user"] == guest1_id
                print("Host received ICE candidate from Guest1")
                
                print("PASS: ICE candidate forwarding successful")
    
    @pytest.mark.asyncio
    async def test_audio_video_state_updates_broadcast(self):
        """Test audio/video state updates (mute/unmute) broadcast to all"""
        ws_url_host = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?token={self.token}&user_name=Host&is_host=true"
        ws_url_guest1 = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?user_name=Guest1&is_host=false"
        ws_url_guest2 = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?user_name=Guest2&is_host=false"
        
        async with websockets.connect(ws_url_host, close_timeout=10) as ws_host:
            msg = await asyncio.wait_for(ws_host.recv(), timeout=5)
            host_data = json.loads(msg)
            host_id = host_data["your_id"]
            
            async with websockets.connect(ws_url_guest1, close_timeout=10) as ws_guest1:
                await asyncio.wait_for(ws_guest1.recv(), timeout=5)  # room_state
                await asyncio.wait_for(ws_host.recv(), timeout=5)  # user_joined
                
                async with websockets.connect(ws_url_guest2, close_timeout=10) as ws_guest2:
                    await asyncio.wait_for(ws_guest2.recv(), timeout=5)  # room_state
                    await asyncio.wait_for(ws_host.recv(), timeout=5)  # user_joined
                    await asyncio.wait_for(ws_guest1.recv(), timeout=5)  # user_joined
                    
                    # Host mutes audio
                    state_update = {
                        "type": "state_update",
                        "state": {"audio_enabled": False}
                    }
                    await ws_host.send(json.dumps(state_update))
                    print("Host sent audio mute state update")
                    
                    # Guest1 should receive participant_state_changed
                    msg = await asyncio.wait_for(ws_guest1.recv(), timeout=5)
                    data = json.loads(msg)
                    assert data["type"] == "participant_state_changed"
                    assert data["user_id"] == host_id
                    assert data["changes"]["audio_enabled"] == False
                    print("Guest1 received Host's audio mute state")
                    
                    # Guest2 should also receive participant_state_changed
                    msg = await asyncio.wait_for(ws_guest2.recv(), timeout=5)
                    data = json.loads(msg)
                    assert data["type"] == "participant_state_changed"
                    assert data["changes"]["audio_enabled"] == False
                    print("Guest2 received Host's audio mute state")
                    
                    # Host unmutes audio and disables video
                    state_update2 = {
                        "type": "state_update",
                        "state": {"audio_enabled": True, "video_enabled": False}
                    }
                    await ws_host.send(json.dumps(state_update2))
                    print("Host sent audio unmute + video disable state update")
                    
                    # Guest1 should receive the update
                    msg = await asyncio.wait_for(ws_guest1.recv(), timeout=5)
                    data = json.loads(msg)
                    assert data["type"] == "participant_state_changed"
                    assert data["changes"]["audio_enabled"] == True
                    assert data["changes"]["video_enabled"] == False
                    print("Guest1 received Host's state update")
                    
                    # Guest2 should also receive the update
                    msg = await asyncio.wait_for(ws_guest2.recv(), timeout=5)
                    data = json.loads(msg)
                    assert data["type"] == "participant_state_changed"
                    print("Guest2 received Host's state update")
                    
                    print("PASS: Audio/video state updates broadcast to all")
    
    @pytest.mark.asyncio
    async def test_screen_sharing_state_broadcast(self):
        """Test screen sharing state updates broadcast to all participants"""
        ws_url_host = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?token={self.token}&user_name=Host&is_host=true"
        ws_url_guest1 = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?user_name=Guest1&is_host=false"
        ws_url_guest2 = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?user_name=Guest2&is_host=false"
        
        async with websockets.connect(ws_url_host, close_timeout=10) as ws_host:
            msg = await asyncio.wait_for(ws_host.recv(), timeout=5)
            host_data = json.loads(msg)
            host_id = host_data["your_id"]
            
            async with websockets.connect(ws_url_guest1, close_timeout=10) as ws_guest1:
                await asyncio.wait_for(ws_guest1.recv(), timeout=5)  # room_state
                await asyncio.wait_for(ws_host.recv(), timeout=5)  # user_joined
                
                async with websockets.connect(ws_url_guest2, close_timeout=10) as ws_guest2:
                    await asyncio.wait_for(ws_guest2.recv(), timeout=5)  # room_state
                    await asyncio.wait_for(ws_host.recv(), timeout=5)  # user_joined
                    await asyncio.wait_for(ws_guest1.recv(), timeout=5)  # user_joined
                    
                    # Host starts screen sharing
                    screen_share_start = {
                        "type": "state_update",
                        "state": {"screen_sharing": True}
                    }
                    await ws_host.send(json.dumps(screen_share_start))
                    print("Host started screen sharing")
                    
                    # Guest1 should receive screen sharing state
                    msg = await asyncio.wait_for(ws_guest1.recv(), timeout=5)
                    data = json.loads(msg)
                    assert data["type"] == "participant_state_changed"
                    assert data["user_id"] == host_id
                    assert data["changes"]["screen_sharing"] == True
                    assert data["participant"]["screen_sharing"] == True
                    print("Guest1 received screen sharing start notification")
                    
                    # Guest2 should also receive screen sharing state
                    msg = await asyncio.wait_for(ws_guest2.recv(), timeout=5)
                    data = json.loads(msg)
                    assert data["type"] == "participant_state_changed"
                    assert data["changes"]["screen_sharing"] == True
                    print("Guest2 received screen sharing start notification")
                    
                    # Host stops screen sharing
                    screen_share_stop = {
                        "type": "state_update",
                        "state": {"screen_sharing": False}
                    }
                    await ws_host.send(json.dumps(screen_share_stop))
                    print("Host stopped screen sharing")
                    
                    # Guest1 should receive screen sharing stop
                    msg = await asyncio.wait_for(ws_guest1.recv(), timeout=5)
                    data = json.loads(msg)
                    assert data["type"] == "participant_state_changed"
                    assert data["changes"]["screen_sharing"] == False
                    print("Guest1 received screen sharing stop notification")
                    
                    # Guest2 should also receive screen sharing stop
                    msg = await asyncio.wait_for(ws_guest2.recv(), timeout=5)
                    data = json.loads(msg)
                    assert data["type"] == "participant_state_changed"
                    assert data["changes"]["screen_sharing"] == False
                    print("Guest2 received screen sharing stop notification")
                    
                    print("PASS: Screen sharing state broadcast to all participants")
    
    @pytest.mark.asyncio
    async def test_hand_raise_broadcast(self):
        """Test hand raise state broadcast to all participants"""
        ws_url_host = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?token={self.token}&user_name=Host&is_host=true"
        ws_url_guest1 = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?user_name=Guest1&is_host=false"
        
        async with websockets.connect(ws_url_host, close_timeout=10) as ws_host:
            await asyncio.wait_for(ws_host.recv(), timeout=5)  # room_state
            
            async with websockets.connect(ws_url_guest1, close_timeout=10) as ws_guest1:
                msg = await asyncio.wait_for(ws_guest1.recv(), timeout=5)
                guest1_data = json.loads(msg)
                guest1_id = guest1_data["your_id"]
                
                await asyncio.wait_for(ws_host.recv(), timeout=5)  # user_joined
                
                # Guest1 raises hand
                raise_hand = {"type": "raise_hand", "raised": True}
                await ws_guest1.send(json.dumps(raise_hand))
                print("Guest1 raised hand")
                
                # Host should receive hand raise notification
                msg = await asyncio.wait_for(ws_host.recv(), timeout=5)
                data = json.loads(msg)
                assert data["type"] == "participant_state_changed"
                assert data["user_id"] == guest1_id
                assert data["changes"]["hand_raised"] == True
                print("Host received Guest1's hand raise")
                
                # Guest1 lowers hand
                lower_hand = {"type": "raise_hand", "raised": False}
                await ws_guest1.send(json.dumps(lower_hand))
                print("Guest1 lowered hand")
                
                # Host should receive hand lower notification
                msg = await asyncio.wait_for(ws_host.recv(), timeout=5)
                data = json.loads(msg)
                assert data["type"] == "participant_state_changed"
                assert data["changes"]["hand_raised"] == False
                print("Host received Guest1's hand lower")
                
                print("PASS: Hand raise broadcast working")
    
    @pytest.mark.asyncio
    async def test_user_leave_notification(self):
        """Test user leave notification broadcast"""
        ws_url_host = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?token={self.token}&user_name=Host&is_host=true"
        ws_url_guest1 = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?user_name=Guest1&is_host=false"
        ws_url_guest2 = f"{WS_BASE_URL}/api/karau-meet/ws/{self.meeting_id}?user_name=Guest2&is_host=false"
        
        async with websockets.connect(ws_url_host, close_timeout=10) as ws_host:
            await asyncio.wait_for(ws_host.recv(), timeout=5)  # room_state
            
            async with websockets.connect(ws_url_guest1, close_timeout=10) as ws_guest1:
                await asyncio.wait_for(ws_guest1.recv(), timeout=5)  # room_state
                await asyncio.wait_for(ws_host.recv(), timeout=5)  # user_joined
                
                async with websockets.connect(ws_url_guest2, close_timeout=10) as ws_guest2:
                    await asyncio.wait_for(ws_guest2.recv(), timeout=5)  # room_state
                    await asyncio.wait_for(ws_host.recv(), timeout=5)  # user_joined
                    await asyncio.wait_for(ws_guest1.recv(), timeout=5)  # user_joined
                    
                    print("All 3 users connected")
                
                # Guest2 disconnected (websocket closed)
                await asyncio.sleep(0.5)  # Wait for disconnect to propagate
                
                # Host should receive user_left notification
                msg = await asyncio.wait_for(ws_host.recv(), timeout=5)
                data = json.loads(msg)
                assert data["type"] == "user_left"
                assert data["user_name"] == "Guest2"
                assert len(data["participants"]) == 2  # Only Host and Guest1 remain
                print("Host received Guest2 leave notification")
                
                # Guest1 should also receive user_left notification
                msg = await asyncio.wait_for(ws_guest1.recv(), timeout=5)
                data = json.loads(msg)
                assert data["type"] == "user_left"
                assert data["user_name"] == "Guest2"
                print("Guest1 received Guest2 leave notification")
                
                print("PASS: User leave notification broadcast working")


class TestRoomStatusAPI:
    """Test REST API endpoints for room status"""
    
    def test_room_status_endpoint(self):
        """Test /api/karau-meet/room/{meeting_id}/status endpoint"""
        meeting_id = f"test-status-{uuid.uuid4().hex[:8]}"
        
        # Check status before anyone joins
        response = requests.get(f"{BASE_URL}/api/karau-meet/room/{meeting_id}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["meeting_id"] == meeting_id
        assert data["active"] == False
        assert data["participant_count"] == 0
        print(f"Room status (empty): {data}")
        
        print("PASS: Room status endpoint working")
    
    def test_room_participants_endpoint(self):
        """Test /api/karau-meet/room/{meeting_id}/participants endpoint (requires auth)"""
        token = get_auth_token()
        meeting_id = f"test-participants-{uuid.uuid4().hex[:8]}"
        
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/room/{meeting_id}/participants",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["meeting_id"] == meeting_id
        assert data["count"] == 0
        assert data["participants"] == []
        print(f"Room participants (empty): {data}")
        
        print("PASS: Room participants endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
