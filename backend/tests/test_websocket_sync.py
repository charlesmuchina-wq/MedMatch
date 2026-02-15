"""
WebSocket Signaling Tests for AI KARAU Meeting
Uses synchronous wrapper for async WebSocket tests
"""
import asyncio
import json
import os
import requests
import websockets
from websockets.exceptions import ConnectionClosed

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

async def test_ws_connection_and_room_state(token):
    """Test WebSocket connects and receives room_state"""
    meeting_id = "test-meeting-001"
    ws_url = f"{WS_BASE_URL}/api/karau-meet/ws/{meeting_id}?token={token}&user_name=TestUser&is_host=true"
    
    try:
        async with websockets.connect(ws_url, close_timeout=5) as ws:
            message = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(message)
            
            assert data["type"] == "room_state", f"Expected room_state, got {data['type']}"
            assert "meeting_id" in data
            assert "participants" in data
            assert "your_id" in data
            print(f"PASS: WebSocket connection - received room_state")
            print(f"  meeting_id: {data['meeting_id']}")
            print(f"  your_id: {data['your_id']}")
            print(f"  participants: {len(data['participants'])}")
            return True
    except Exception as e:
        print(f"FAIL: WebSocket connection - {e}")
        return False

async def test_ws_ping_pong(token):
    """Test WebSocket ping/pong"""
    meeting_id = "test-meeting-002"
    ws_url = f"{WS_BASE_URL}/api/karau-meet/ws/{meeting_id}?token={token}&user_name=PingUser&is_host=false"
    
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
            return True
    except Exception as e:
        print(f"FAIL: Ping/pong - {e}")
        return False

async def test_ws_chat_message(token):
    """Test WebSocket chat message"""
    meeting_id = "test-meeting-003"
    ws_url = f"{WS_BASE_URL}/api/karau-meet/ws/{meeting_id}?token={token}&user_name=ChatUser&is_host=true"
    
    try:
        async with websockets.connect(ws_url, close_timeout=5) as ws:
            # Wait for room_state first
            await asyncio.wait_for(ws.recv(), timeout=5)
            
            # Send chat message
            chat_msg = {"type": "chat", "message": "Hello from test!"}
            await ws.send(json.dumps(chat_msg))
            
            # Verify connection still works with ping
            await ws.send(json.dumps({"type": "ping"}))
            message = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(message)
            assert data["type"] == "pong"
            print("PASS: Chat message sent successfully")
            return True
    except Exception as e:
        print(f"FAIL: Chat message - {e}")
        return False

async def test_ws_guest_connection():
    """Test WebSocket guest connection (no token)"""
    meeting_id = "test-meeting-004"
    ws_url = f"{WS_BASE_URL}/api/karau-meet/ws/{meeting_id}?user_name=GuestUser&is_host=false"
    
    try:
        async with websockets.connect(ws_url, close_timeout=5) as ws:
            message = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(message)
            
            assert data["type"] == "room_state"
            assert "guest_" in data["your_id"], f"Expected guest ID, got {data['your_id']}"
            print(f"PASS: Guest connection - ID: {data['your_id']}")
            return True
    except Exception as e:
        print(f"FAIL: Guest connection - {e}")
        return False

async def test_ws_state_update(token):
    """Test WebSocket state update"""
    meeting_id = "test-meeting-005"
    ws_url = f"{WS_BASE_URL}/api/karau-meet/ws/{meeting_id}?token={token}&user_name=StateUser&is_host=true"
    
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
            return True
    except Exception as e:
        print(f"FAIL: State update - {e}")
        return False

def test_room_status_api():
    """Test room status REST API"""
    meeting_id = "test-room-status"
    response = requests.get(f"{BASE_URL}/api/karau-meet/room/{meeting_id}/status")
    
    if response.status_code == 200:
        data = response.json()
        if "meeting_id" in data and "active" in data and "participant_count" in data:
            print(f"PASS: Room status API - active={data['active']}, count={data['participant_count']}")
            return True
    print(f"FAIL: Room status API - status={response.status_code}")
    return False

async def run_all_tests():
    """Run all WebSocket tests"""
    print("=" * 60)
    print("WebSocket Signaling Tests for AI KARAU Meeting")
    print("=" * 60)
    print(f"BASE_URL: {BASE_URL}")
    print(f"WS_URL: {WS_BASE_URL}")
    print()
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("FAIL: Could not get auth token")
        return
    print(f"Auth token obtained: {token[:20]}...")
    print()
    
    results = {}
    
    # Test 1: Room status API (REST)
    print("Test 1: Room Status API")
    results["room_status_api"] = test_room_status_api()
    print()
    
    # Test 2: WebSocket connection and room_state
    print("Test 2: WebSocket Connection & Room State")
    results["ws_connection"] = await test_ws_connection_and_room_state(token)
    print()
    
    # Test 3: Ping/pong
    print("Test 3: WebSocket Ping/Pong")
    results["ws_ping_pong"] = await test_ws_ping_pong(token)
    print()
    
    # Test 4: Chat message
    print("Test 4: WebSocket Chat Message")
    results["ws_chat"] = await test_ws_chat_message(token)
    print()
    
    # Test 5: Guest connection
    print("Test 5: WebSocket Guest Connection")
    results["ws_guest"] = await test_ws_guest_connection()
    print()
    
    # Test 6: State update
    print("Test 6: WebSocket State Update")
    results["ws_state_update"] = await test_ws_state_update(token)
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    for test, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  {test}: {status}")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_all_tests())
