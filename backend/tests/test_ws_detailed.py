"""
Detailed WebSocket tests with better error handling
"""
import asyncio
import json
import os
import requests
import websockets
import traceback

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

async def test_chat_detailed(token):
    """Test chat with detailed error output"""
    meeting_id = "test-chat-detailed"
    ws_url = f"{WS_BASE_URL}/api/karau-meet/ws/{meeting_id}?token={token}&user_name=ChatUser&is_host=true"
    
    try:
        async with websockets.connect(ws_url, close_timeout=10) as ws:
            # Wait for room_state
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)
            print(f"  Received: {data['type']}")
            
            # Send chat message
            chat_msg = {"type": "chat", "message": "Test message"}
            await ws.send(json.dumps(chat_msg))
            print(f"  Sent chat message")
            
            # Wait a bit for any response
            await asyncio.sleep(0.5)
            
            # Send ping to verify connection
            await ws.send(json.dumps({"type": "ping"}))
            print(f"  Sent ping")
            
            # Wait for pong
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)
            print(f"  Received: {data['type']}")
            
            if data["type"] == "pong":
                print("PASS: Chat message sent, connection still active")
                return True
            else:
                print(f"FAIL: Expected pong, got {data['type']}")
                return False
                
    except asyncio.TimeoutError as e:
        print(f"FAIL: Timeout - {e}")
        return False
    except Exception as e:
        print(f"FAIL: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False

async def test_state_update_detailed(token):
    """Test state update with detailed error output"""
    meeting_id = "test-state-detailed"
    ws_url = f"{WS_BASE_URL}/api/karau-meet/ws/{meeting_id}?token={token}&user_name=StateUser&is_host=true"
    
    try:
        async with websockets.connect(ws_url, close_timeout=10) as ws:
            # Wait for room_state
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)
            print(f"  Received: {data['type']}")
            
            # Send state update
            state_msg = {"type": "state_update", "state": {"audio_enabled": False, "video_enabled": True}}
            await ws.send(json.dumps(state_msg))
            print(f"  Sent state update")
            
            # Wait a bit
            await asyncio.sleep(0.5)
            
            # Send ping to verify connection
            await ws.send(json.dumps({"type": "ping"}))
            print(f"  Sent ping")
            
            # Wait for pong
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)
            print(f"  Received: {data['type']}")
            
            if data["type"] == "pong":
                print("PASS: State update sent, connection still active")
                return True
            else:
                print(f"FAIL: Expected pong, got {data['type']}")
                return False
                
    except asyncio.TimeoutError as e:
        print(f"FAIL: Timeout - {e}")
        return False
    except Exception as e:
        print(f"FAIL: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False

async def test_two_users_chat():
    """Test chat between two users"""
    meeting_id = "test-two-users"
    token = get_auth_token()
    
    ws_url1 = f"{WS_BASE_URL}/api/karau-meet/ws/{meeting_id}?token={token}&user_name=User1&is_host=true"
    ws_url2 = f"{WS_BASE_URL}/api/karau-meet/ws/{meeting_id}?user_name=User2&is_host=false"
    
    try:
        async with websockets.connect(ws_url1, close_timeout=10) as ws1:
            # User 1 joins
            msg = await asyncio.wait_for(ws1.recv(), timeout=5)
            data = json.loads(msg)
            print(f"  User1 received: {data['type']}")
            
            async with websockets.connect(ws_url2, close_timeout=10) as ws2:
                # User 2 joins
                msg = await asyncio.wait_for(ws2.recv(), timeout=5)
                data = json.loads(msg)
                print(f"  User2 received: {data['type']}")
                
                # User 1 should receive user_joined notification
                msg = await asyncio.wait_for(ws1.recv(), timeout=5)
                data = json.loads(msg)
                print(f"  User1 received: {data['type']}")
                
                if data["type"] == "user_joined":
                    print("PASS: User1 received user_joined notification")
                
                # User 1 sends chat
                await ws1.send(json.dumps({"type": "chat", "message": "Hello User2!"}))
                print("  User1 sent chat message")
                
                # User 2 should receive chat
                msg = await asyncio.wait_for(ws2.recv(), timeout=5)
                data = json.loads(msg)
                print(f"  User2 received: {data['type']}")
                
                if data["type"] == "chat":
                    print(f"PASS: User2 received chat: {data.get('message')}")
                    return True
                else:
                    print(f"FAIL: Expected chat, got {data['type']}")
                    return False
                    
    except Exception as e:
        print(f"FAIL: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False

async def main():
    print("=" * 60)
    print("Detailed WebSocket Tests")
    print("=" * 60)
    
    token = get_auth_token()
    if not token:
        print("FAIL: Could not get auth token")
        return
    
    print("\nTest 1: Chat Message (single user)")
    await test_chat_detailed(token)
    
    print("\nTest 2: State Update (single user)")
    await test_state_update_detailed(token)
    
    print("\nTest 3: Two Users Chat")
    await test_two_users_chat()

if __name__ == "__main__":
    asyncio.run(main())
