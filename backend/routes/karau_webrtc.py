"""
AI KARAU Meeting - WebRTC Signaling API Routes
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException, Depends
from typing import Optional
import jwt
import os

from services.karau_meet.webrtc_signaling import (
    handle_webrtc_signaling,
    get_connection_manager
)
from routes.auth import get_current_user

router = APIRouter(prefix="/karau-meet", tags=["AI KARAU WebRTC"])

JWT_SECRET = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


@router.websocket("/ws/{meeting_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    meeting_id: str,
    token: str = Query(None),
    user_name: str = Query(default="Guest"),
    is_host: str = Query(default="false")
):
    """
    WebSocket endpoint for WebRTC signaling
    
    Connect with: ws://{host}/api/karau-meet/ws/{meeting_id}?token={jwt}&user_name={name}
    
    Message types:
    - offer: WebRTC SDP offer
    - answer: WebRTC SDP answer
    - ice_candidate: ICE candidate
    - state_update: Audio/video/screen share state
    - chat: Chat message
    - raise_hand: Hand raise toggle
    - reaction: Emoji reaction
    """
    
    # Verify token
    user_data = None
    user_id = None
    
    if token:
        user_data = verify_token(token)
        if user_data:
            user_id = user_data.get("user_id", user_data.get("sub"))
            user_name = user_data.get("name", user_name)
    
    # Generate guest ID if no valid token
    if not user_id:
        import uuid
        user_id = f"guest_{str(uuid.uuid4())[:8]}"
    
    # Handle signaling
    await handle_webrtc_signaling(
        websocket=websocket,
        meeting_id=meeting_id,
        user_id=user_id,
        user_name=user_name,
        is_host=is_host.lower() == "true"
    )


@router.get("/ice-servers")
async def get_ice_servers_endpoint():
    """
    Get ICE servers for WebRTC connection
    
    Returns STUN + TURN servers from Xirsys if configured,
    otherwise falls back to free Google STUN servers
    """
    from services.karau_meet.turn_service import get_ice_servers
    
    result = await get_ice_servers()
    return result


@router.get("/room/{meeting_id}/participants")
async def get_room_participants(
    meeting_id: str,
    user: dict = Depends(get_current_user)
):
    """Get current participants in a meeting room"""
    
    manager = get_connection_manager()
    participants = manager.get_participants(meeting_id)
    
    return {
        "meeting_id": meeting_id,
        "participants": participants,
        "count": len(participants)
    }


@router.get("/room/{meeting_id}/status")
async def get_room_status(
    meeting_id: str
):
    """Get meeting room status (public endpoint for join page)"""
    
    manager = get_connection_manager()
    count = manager.get_participant_count(meeting_id)
    
    return {
        "meeting_id": meeting_id,
        "active": count > 0,
        "participant_count": count
    }
