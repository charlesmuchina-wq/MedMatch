"""
WebSocket Signaling Tests for AI KARAU Meeting
Tests WebRTC signaling WebSocket endpoint
"""
import pytest
import asyncio
import json
import os
import requests
import websockets
from websockets.exceptions import ConnectionClosed

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
WS_BASE_URL = BASE_URL.replace('https://', 'wss://').replace('http://', 'ws://')

class TestWebSocketSignaling:
    """Test WebSocket signaling for WebRTC"""
    
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
    
    @pytest.mark.asyncio
    async def test_websocket_connection_and_room_state(self, auth_token):
        """Test WebSocket connects and receives room_state"""
        meeting_id = "test-meeting-001"
        ws_url = f"{WS_BASE_URL}/api/karau-meet/ws/{meeting_id}?token={auth_token}&user_name=TestUser&is_host=true"
        
        try:
            async with websockets.connect(ws_url, close_timeout=5) as ws:
                # Should receive room_state on connect
                message = await asyncio.wait_for(ws.recv(), timeout=5)
                data = json.loads(message)
                
                assert data["type"] == "room_state", f"Expected room_state, got {data['type']}"
                assert "meeting_id" in data
                assert "participants" in data
                assert "your_id" in data
                print(f"PASS: Received room_state with meeting_id={data['meeting_id']}")
                print(f"PASS: Participant ID assigned: {data['your_id']}")
                
        except asyncio.TimeoutError:
            pytest.fail("Timeout waiting for room_state message")
        except Exception as e:
            pytest.fail(f"WebSocket connection failed: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_ping_pong(self, auth_token):
        """Test WebSocket ping/pong keep-alive"""
        meeting_id = "test-meeting-002"
        ws_url = f"{WS_BASE_URL}/api/karau-meet/ws/{meeting_id}?token={auth_token}&user_name=PingUser&is_host=false"
        
        try:
            async with websockets.connect(ws_url, close_timeout=5) as ws:
                # Wait for room_state first
                await asyncio.wait_for(ws.recv(), timeout=5)
                
                # Send ping
                await ws.send(json.dumps({"type": "ping"}))
                
                # Should receive pong
                message = await asyncio.wait_for(ws.recv(), timeout=5)
                data = json.loads(message)
                
                assert data["type"] == "pong", f"Expected pong, got {data['type']}"
                print("PASS: Ping/pong working correctly")
                
        except asyncio.TimeoutError:
            pytest.fail("Timeout waiting for pong response")
        except Exception as e:
            pytest.fail(f"Ping/pong test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_chat_message(self, auth_token):
        """Test WebSocket chat message broadcast"""
        meeting_id = "test-meeting-003"
        ws_url = f"{WS_BASE_URL}/api/karau-meet/ws/{meeting_id}?token={auth_token}&user_name=ChatUser&is_host=true"
        
        try:
            async with websockets.connect(ws_url, close_timeout=5) as ws:
                # Wait for room_state first
                await asyncio.wait_for(ws.recv(), timeout=5)
                
                # Send chat message
                chat_msg = {"type": "chat", "message": "Hello from test!"}
                await ws.send(json.dumps(chat_msg))
                
                # Chat messages are broadcast to others, not echoed back to sender
                # So we just verify the send didn't error
                print("PASS: Chat message sent successfully")
                
                # Send another ping to verify connection still works
                await ws.send(json.dumps({"type": "ping"}))
                message = await asyncio.wait_for(ws.recv(), timeout=5)
                data = json.loads(message)
                assert data["type"] == "pong"
                print("PASS: Connection still active after chat")
                
        except Exception as e:
            pytest.fail(f"Chat message test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_guest_connection(self):
        """Test WebSocket connection without token (guest mode)"""
        meeting_id = "test-meeting-004"
        ws_url = f"{WS_BASE_URL}/api/karau-meet/ws/{meeting_id}?user_name=GuestUser&is_host=false"
        
        try:
            async with websockets.connect(ws_url, close_timeout=5) as ws:
                # Should receive room_state even as guest
                message = await asyncio.wait_for(ws.recv(), timeout=5)
                data = json.loads(message)
                
                assert data["type"] == "room_state"
                assert "guest_" in data["your_id"], f"Expected guest ID, got {data['your_id']}"
                print(f"PASS: Guest connected with ID: {data['your_id']}")
                
        except Exception as e:
            pytest.fail(f"Guest connection failed: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_state_update(self, auth_token):
        """Test WebSocket state update (mute/video toggle)"""
        meeting_id = "test-meeting-005"
        ws_url = f"{WS_BASE_URL}/api/karau-meet/ws/{meeting_id}?token={auth_token}&user_name=StateUser&is_host=true"
        
        try:
            async with websockets.connect(ws_url, close_timeout=5) as ws:
                # Wait for room_state first
                await asyncio.wait_for(ws.recv(), timeout=5)
                
                # Send state update (mute audio)
                state_msg = {"type": "state_update", "state": {"audio_enabled": False}}
                await ws.send(json.dumps(state_msg))
                
                # Verify connection still works
                await ws.send(json.dumps({"type": "ping"}))
                message = await asyncio.wait_for(ws.recv(), timeout=5)
                data = json.loads(message)
                assert data["type"] == "pong"
                print("PASS: State update sent successfully")
                
        except Exception as e:
            pytest.fail(f"State update test failed: {e}")


class TestRoomStatusAPI:
    """Test room status REST API endpoints"""
    
    def test_room_status_endpoint(self):
        """Test GET /api/karau-meet/room/{meeting_id}/status"""
        meeting_id = "test-room-status"
        response = requests.get(f"{BASE_URL}/api/karau-meet/room/{meeting_id}/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "meeting_id" in data
        assert "active" in data
        assert "participant_count" in data
        assert data["meeting_id"] == meeting_id
        print(f"PASS: Room status endpoint working - active={data['active']}, count={data['participant_count']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
