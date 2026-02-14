"""
AI KARAU Meeting API Routes
WebRTC signaling and meeting management
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import asyncio
from datetime import datetime, timezone

from services.karau_meet import (
    create_meeting,
    get_meeting,
    join_meeting,
    leave_meeting,
    end_meeting,
    get_participants,
    update_participant,
    add_chat_message,
    add_ai_note,
    create_breakout_room,
    get_user_meetings,
    get_ice_servers,
    meeting_participants
)
from routes.auth import get_current_user

router = APIRouter(prefix="/karau-meet", tags=["AI KARAU Meeting"])

# WebSocket connections storage
connected_clients: Dict[str, Dict[str, WebSocket]] = {}  # meeting_id -> {user_id: websocket}


class CreateMeetingRequest(BaseModel):
    title: str = "AI KARAU Meeting"
    scheduled_time: Optional[str] = None
    settings: Optional[Dict] = None


class JoinMeetingRequest(BaseModel):
    video_enabled: bool = True
    audio_enabled: bool = True


class UpdateParticipantRequest(BaseModel):
    video_enabled: Optional[bool] = None
    audio_enabled: Optional[bool] = None
    screen_sharing: Optional[bool] = None
    hand_raised: Optional[bool] = None


class ChatMessageRequest(BaseModel):
    message: str
    message_type: str = "text"


class BreakoutRoomRequest(BaseModel):
    room_name: str
    participant_ids: List[str]


class SignalRequest(BaseModel):
    target_user_id: str
    signal_type: str  # "offer", "answer", "ice-candidate"
    signal_data: Dict


@router.post("/meetings")
async def create_new_meeting(
    request: CreateMeetingRequest,
    user: dict = Depends(get_current_user)
):
    """Create a new AI KARAU meeting"""
    meeting = await create_meeting(
        host_id=user["user_id"],
        host_name=user.get("name", user.get("email", "Host")),
        title=request.title,
        scheduled_time=request.scheduled_time,
        settings=request.settings
    )
    return meeting


@router.get("/meetings")
async def get_my_meetings(
    limit: int = 20,
    user: dict = Depends(get_current_user)
):
    """Get user's meetings (hosted and participated)"""
    meetings = await get_user_meetings(user["user_id"], limit)
    return {"meetings": meetings}


@router.get("/meetings/{meeting_id}")
async def get_meeting_details(
    meeting_id: str,
    user: dict = Depends(get_current_user)
):
    """Get meeting details"""
    meeting = await get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return {
        "meeting": meeting,
        "ice_servers": get_ice_servers(),
        "participants": await get_participants(meeting_id)
    }


@router.post("/meetings/{meeting_id}/join")
async def join_meeting_room(
    meeting_id: str,
    request: JoinMeetingRequest,
    user: dict = Depends(get_current_user)
):
    """Join a meeting"""
    result = await join_meeting(
        meeting_id=meeting_id,
        user_id=user["user_id"],
        user_name=user.get("name", user.get("email", "Participant")),
        video_enabled=request.video_enabled,
        audio_enabled=request.audio_enabled
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Add ICE servers for WebRTC
    result["ice_servers"] = get_ice_servers()
    
    return result


@router.post("/meetings/{meeting_id}/leave")
async def leave_meeting_room(
    meeting_id: str,
    user: dict = Depends(get_current_user)
):
    """Leave a meeting"""
    success = await leave_meeting(meeting_id, user["user_id"])
    
    if not success:
        raise HTTPException(status_code=404, detail="Meeting or participant not found")
    
    # Notify other participants via WebSocket
    await broadcast_to_meeting(meeting_id, {
        "type": "participant_left",
        "user_id": user["user_id"]
    }, exclude_user=user["user_id"])
    
    return {"success": True}


@router.post("/meetings/{meeting_id}/end")
async def end_meeting_room(
    meeting_id: str,
    user: dict = Depends(get_current_user)
):
    """End a meeting (host only)"""
    success = await end_meeting(meeting_id, user["user_id"])
    
    if not success:
        raise HTTPException(status_code=403, detail="Only host can end the meeting")
    
    # Notify all participants
    await broadcast_to_meeting(meeting_id, {
        "type": "meeting_ended",
        "ended_by": user["user_id"]
    })
    
    # Close all WebSocket connections
    if meeting_id in connected_clients:
        for ws in connected_clients[meeting_id].values():
            try:
                await ws.close()
            except:
                pass
        del connected_clients[meeting_id]
    
    return {"success": True}


@router.get("/meetings/{meeting_id}/participants")
async def get_meeting_participants(
    meeting_id: str,
    user: dict = Depends(get_current_user)
):
    """Get all participants in a meeting"""
    participants = await get_participants(meeting_id)
    return {"participants": participants}


@router.put("/meetings/{meeting_id}/participant")
async def update_my_participant_status(
    meeting_id: str,
    request: UpdateParticipantRequest,
    user: dict = Depends(get_current_user)
):
    """Update participant status (video, audio, etc.)"""
    updates = {}
    if request.video_enabled is not None:
        updates["video_enabled"] = request.video_enabled
    if request.audio_enabled is not None:
        updates["audio_enabled"] = request.audio_enabled
    if request.screen_sharing is not None:
        updates["screen_sharing"] = request.screen_sharing
    if request.hand_raised is not None:
        updates["hand_raised"] = request.hand_raised
    
    success = await update_participant(meeting_id, user["user_id"], updates)
    
    if not success:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    # Broadcast update to other participants
    await broadcast_to_meeting(meeting_id, {
        "type": "participant_updated",
        "user_id": user["user_id"],
        "updates": updates
    })
    
    return {"success": True}


@router.post("/meetings/{meeting_id}/chat")
async def send_chat_message(
    meeting_id: str,
    request: ChatMessageRequest,
    user: dict = Depends(get_current_user)
):
    """Send a chat message in the meeting"""
    message = await add_chat_message(
        meeting_id=meeting_id,
        user_id=user["user_id"],
        user_name=user.get("name", user.get("email", "Unknown")),
        message=request.message,
        message_type=request.message_type
    )
    
    # Broadcast to all participants
    await broadcast_to_meeting(meeting_id, {
        "type": "chat_message",
        "message": message
    })
    
    return message


@router.post("/meetings/{meeting_id}/ai-note")
async def add_meeting_ai_note(
    meeting_id: str,
    note_type: str,
    content: str,
    user: dict = Depends(get_current_user)
):
    """Add an AI-generated note (transcription, summary, etc.)"""
    note = await add_ai_note(
        meeting_id=meeting_id,
        note_type=note_type,
        content=content
    )
    
    # Broadcast to all participants
    await broadcast_to_meeting(meeting_id, {
        "type": "ai_note",
        "note": note
    })
    
    return note


@router.post("/meetings/{meeting_id}/breakout-rooms")
async def create_meeting_breakout_room(
    meeting_id: str,
    request: BreakoutRoomRequest,
    user: dict = Depends(get_current_user)
):
    """Create a breakout room (host only)"""
    meeting = await get_meeting(meeting_id)
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meeting["host_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Only host can create breakout rooms")
    
    room = await create_breakout_room(
        meeting_id=meeting_id,
        room_name=request.room_name,
        participant_ids=request.participant_ids
    )
    
    # Notify affected participants
    for participant_id in request.participant_ids:
        await send_to_user(meeting_id, participant_id, {
            "type": "breakout_room_assigned",
            "room": room
        })
    
    return room


@router.post("/meetings/{meeting_id}/signal")
async def send_webrtc_signal(
    meeting_id: str,
    request: SignalRequest,
    user: dict = Depends(get_current_user)
):
    """Send WebRTC signaling data to another participant"""
    # Send signal to target user via WebSocket
    await send_to_user(meeting_id, request.target_user_id, {
        "type": "webrtc_signal",
        "from_user_id": user["user_id"],
        "signal_type": request.signal_type,
        "signal_data": request.signal_data
    })
    
    return {"success": True}


# WebSocket endpoint for real-time communication
@router.websocket("/ws/{meeting_id}")
async def meeting_websocket(
    websocket: WebSocket,
    meeting_id: str
):
    """WebSocket connection for real-time meeting communication"""
    await websocket.accept()
    
    # Get user from token in query params
    token = websocket.query_params.get("token", "")
    user_id = websocket.query_params.get("user_id", "")
    user_name = websocket.query_params.get("user_name", "Anonymous")
    
    if not user_id:
        await websocket.close(code=4001, reason="User ID required")
        return
    
    # Initialize meeting connections if needed
    if meeting_id not in connected_clients:
        connected_clients[meeting_id] = {}
    
    # Store connection
    connected_clients[meeting_id][user_id] = websocket
    
    # Notify others of new participant
    await broadcast_to_meeting(meeting_id, {
        "type": "participant_joined",
        "user_id": user_id,
        "user_name": user_name
    }, exclude_user=user_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            msg_type = message.get("type")
            
            if msg_type == "webrtc_signal":
                # Forward WebRTC signal to target
                target_id = message.get("target_user_id")
                if target_id and target_id in connected_clients.get(meeting_id, {}):
                    await connected_clients[meeting_id][target_id].send_json({
                        "type": "webrtc_signal",
                        "from_user_id": user_id,
                        "signal_type": message.get("signal_type"),
                        "signal_data": message.get("signal_data")
                    })
            
            elif msg_type == "chat_message":
                # Broadcast chat message
                chat_msg = await add_chat_message(
                    meeting_id=meeting_id,
                    user_id=user_id,
                    user_name=user_name,
                    message=message.get("message", ""),
                    message_type=message.get("message_type", "text")
                )
                await broadcast_to_meeting(meeting_id, {
                    "type": "chat_message",
                    "message": chat_msg
                })
            
            elif msg_type == "participant_update":
                # Update and broadcast participant status
                updates = message.get("updates", {})
                await update_participant(meeting_id, user_id, updates)
                await broadcast_to_meeting(meeting_id, {
                    "type": "participant_updated",
                    "user_id": user_id,
                    "updates": updates
                })
            
            elif msg_type == "ai_transcription":
                # Handle AI transcription from client
                note = await add_ai_note(
                    meeting_id=meeting_id,
                    note_type="transcription",
                    content=message.get("content", "")
                )
                await broadcast_to_meeting(meeting_id, {
                    "type": "ai_note",
                    "note": note
                })
            
            elif msg_type == "raise_hand":
                await update_participant(meeting_id, user_id, {"hand_raised": True})
                await broadcast_to_meeting(meeting_id, {
                    "type": "hand_raised",
                    "user_id": user_id,
                    "user_name": user_name
                })
            
            elif msg_type == "lower_hand":
                await update_participant(meeting_id, user_id, {"hand_raised": False})
                await broadcast_to_meeting(meeting_id, {
                    "type": "hand_lowered",
                    "user_id": user_id
                })
            
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Clean up connection
        if meeting_id in connected_clients and user_id in connected_clients[meeting_id]:
            del connected_clients[meeting_id][user_id]
        
        # Notify others
        await broadcast_to_meeting(meeting_id, {
            "type": "participant_left",
            "user_id": user_id
        })
        
        # Leave meeting
        await leave_meeting(meeting_id, user_id)


async def broadcast_to_meeting(meeting_id: str, message: dict, exclude_user: str = None):
    """Broadcast a message to all participants in a meeting"""
    if meeting_id not in connected_clients:
        return
    
    for user_id, ws in list(connected_clients[meeting_id].items()):
        if exclude_user and user_id == exclude_user:
            continue
        try:
            await ws.send_json(message)
        except:
            # Remove dead connection
            del connected_clients[meeting_id][user_id]


async def send_to_user(meeting_id: str, user_id: str, message: dict):
    """Send a message to a specific user"""
    if meeting_id not in connected_clients:
        return False
    
    if user_id not in connected_clients[meeting_id]:
        return False
    
    try:
        await connected_clients[meeting_id][user_id].send_json(message)
        return True
    except:
        return False
