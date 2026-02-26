"""
AI KARAU Meeting Service
WebRTC-based video conferencing with AI features
"""

import os
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "medmatch")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# In-memory storage for active meetings and participants
active_meetings: Dict[str, Dict] = {}
meeting_participants: Dict[str, Dict[str, Any]] = {}  # meeting_id -> {user_id: participant_data}
breakout_rooms: Dict[str, Dict[str, List[str]]] = {}  # meeting_id -> {room_id: [user_ids]}
breakout_sessions: Dict[str, Dict[str, Any]] = {}  # meeting_id -> session data (rooms, timer, status)
waiting_rooms: Dict[str, Dict[str, Any]] = {}  # meeting_id -> {user_id: user_data}
meeting_locks: Dict[str, bool] = {}  # meeting_id -> is_locked


async def create_meeting(
    host_id: str,
    host_name: str,
    title: str = "AI KARAU Meeting",
    scheduled_time: Optional[str] = None,
    settings: Optional[Dict] = None
) -> Dict:
    """Create a new meeting room"""
    meeting_id = str(uuid.uuid4())[:8].upper()
    
    default_settings = {
        "video_enabled": True,
        "audio_enabled": True,
        "screen_share_enabled": True,
        "chat_enabled": True,
        "recording_enabled": True,
        "ai_notes_enabled": True,
        "breakout_rooms_enabled": True,
        "waiting_room_enabled": True,  # Enabled by default
        "mute_on_entry": True,         # New: Mute participants on entry
        "allow_participants_unmute": True,
        "lock_meeting": False,         # New: Meeting lock status
        "max_participants": 100,
        "e2e_encryption": True
    }
    
    if settings:
        default_settings.update(settings)
    
    meeting = {
        "meeting_id": meeting_id,
        "title": title,
        "host_id": host_id,
        "host_name": host_name,
        "status": "waiting",  # waiting, active, ended
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scheduled_time": scheduled_time,
        "started_at": None,
        "ended_at": None,
        "settings": default_settings,
        "participants": [],
        "chat_messages": [],
        "ai_notes": [],
        "recordings": [],
        "breakout_rooms": [],
        "waiting_room": []
    }
    
    # Store in database
    await db.karau_meetings.insert_one({**meeting, "_id": meeting_id})
    
    # Store in memory for quick access
    active_meetings[meeting_id] = meeting
    meeting_participants[meeting_id] = {}
    breakout_rooms[meeting_id] = {}
    waiting_rooms[meeting_id] = {}
    meeting_locks[meeting_id] = False
    
    logger.info(f"Meeting created: {meeting_id} by {host_name}")
    
    return {
        "meeting_id": meeting_id,
        "title": title,
        "join_url": f"/karau-meet/join/{meeting_id}",
        "host_id": host_id,
        "settings": default_settings
    }


async def get_meeting(meeting_id: str) -> Optional[Dict]:
    """Get meeting details"""
    # Check memory first
    if meeting_id in active_meetings:
        return active_meetings[meeting_id]
    
    # Check database
    meeting = await db.karau_meetings.find_one(
        {"meeting_id": meeting_id},
        {"_id": 0}
    )
    
    if meeting:
        active_meetings[meeting_id] = meeting
        if meeting_id not in meeting_participants:
            meeting_participants[meeting_id] = {}
        if meeting_id not in breakout_rooms:
            breakout_rooms[meeting_id] = {}
        if meeting_id not in waiting_rooms:
            waiting_rooms[meeting_id] = {}
        if meeting_id not in meeting_locks:
            meeting_locks[meeting_id] = meeting.get("settings", {}).get("lock_meeting", False)
    
    return meeting


async def join_meeting(
    meeting_id: str,
    user_id: str,
    user_name: str,
    video_enabled: bool = True,
    audio_enabled: bool = True
) -> Optional[Dict]:
    """Join an existing meeting"""
    meeting = await get_meeting(meeting_id)
    
    if not meeting:
        return None
    
    if meeting["status"] == "ended":
        return {"error": "Meeting has ended"}
    
    participant = {
        "user_id": user_id,
        "user_name": user_name,
        "joined_at": datetime.now(timezone.utc).isoformat(),
        "video_enabled": video_enabled,
        "audio_enabled": audio_enabled,
        "screen_sharing": False,
        "hand_raised": False,
        "is_host": user_id == meeting["host_id"],
        "breakout_room": None
    }
    
    meeting_participants[meeting_id][user_id] = participant
    
    # Update meeting status if first join
    if meeting["status"] == "waiting":
        meeting["status"] = "active"
        meeting["started_at"] = datetime.now(timezone.utc).isoformat()
        await db.karau_meetings.update_one(
            {"meeting_id": meeting_id},
            {"$set": {"status": "active", "started_at": meeting["started_at"]}}
        )
    
    # Add to participants list
    await db.karau_meetings.update_one(
        {"meeting_id": meeting_id},
        {"$addToSet": {"participants": {"user_id": user_id, "user_name": user_name}}}
    )
    
    logger.info(f"User {user_name} joined meeting {meeting_id}")
    
    return {
        "meeting": meeting,
        "participant": participant,
        "other_participants": list(meeting_participants[meeting_id].values())
    }


async def leave_meeting(meeting_id: str, user_id: str) -> bool:
    """Leave a meeting"""
    if meeting_id not in meeting_participants:
        return False
    
    if user_id in meeting_participants[meeting_id]:
        user_name = meeting_participants[meeting_id][user_id].get("user_name", "Unknown")
        del meeting_participants[meeting_id][user_id]
        logger.info(f"User {user_name} left meeting {meeting_id}")
        
        # If no participants left and host left, end meeting
        if len(meeting_participants[meeting_id]) == 0:
            await end_meeting(meeting_id, user_id)
        
        return True
    
    return False


async def end_meeting(meeting_id: str, host_id: str) -> bool:
    """End a meeting (host only)"""
    meeting = await get_meeting(meeting_id)
    
    if not meeting:
        return False
    
    if meeting["host_id"] != host_id:
        return False
    
    meeting["status"] = "ended"
    meeting["ended_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.karau_meetings.update_one(
        {"meeting_id": meeting_id},
        {"$set": {"status": "ended", "ended_at": meeting["ended_at"]}}
    )
    
    # Clean up memory
    if meeting_id in active_meetings:
        del active_meetings[meeting_id]
    if meeting_id in meeting_participants:
        del meeting_participants[meeting_id]
    if meeting_id in breakout_rooms:
        del breakout_rooms[meeting_id]
    
    logger.info(f"Meeting {meeting_id} ended")
    
    return True


async def get_participants(meeting_id: str) -> List[Dict]:
    """Get all participants in a meeting"""
    if meeting_id not in meeting_participants:
        return []
    return list(meeting_participants[meeting_id].values())


async def update_participant(
    meeting_id: str,
    user_id: str,
    updates: Dict
) -> bool:
    """Update participant status (video, audio, etc.)"""
    if meeting_id not in meeting_participants:
        return False
    
    if user_id not in meeting_participants[meeting_id]:
        return False
    
    allowed_updates = ["video_enabled", "audio_enabled", "screen_sharing", "hand_raised"]
    for key, value in updates.items():
        if key in allowed_updates:
            meeting_participants[meeting_id][user_id][key] = value
    
    return True


async def add_chat_message(
    meeting_id: str,
    user_id: str,
    user_name: str,
    message: str,
    message_type: str = "text"
) -> Dict:
    """Add a chat message to the meeting"""
    chat_message = {
        "id": str(uuid.uuid4())[:8],
        "user_id": user_id,
        "user_name": user_name,
        "message": message,
        "type": message_type,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await db.karau_meetings.update_one(
        {"meeting_id": meeting_id},
        {"$push": {"chat_messages": chat_message}}
    )
    
    return chat_message


async def add_ai_note(
    meeting_id: str,
    note_type: str,
    content: str,
    timestamp: Optional[str] = None
) -> Dict:
    """Add an AI-generated note to the meeting"""
    ai_note = {
        "id": str(uuid.uuid4())[:8],
        "type": note_type,  # "transcription", "summary", "action_item", "highlight"
        "content": content,
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat()
    }
    
    await db.karau_meetings.update_one(
        {"meeting_id": meeting_id},
        {"$push": {"ai_notes": ai_note}}
    )
    
    return ai_note


async def create_breakout_room(
    meeting_id: str,
    room_name: str,
    participant_ids: List[str]
) -> Dict:
    """Create a breakout room within a meeting"""
    room_id = str(uuid.uuid4())[:6].upper()
    
    breakout_room = {
        "room_id": room_id,
        "room_name": room_name,
        "participants": participant_ids,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    if meeting_id not in breakout_rooms:
        breakout_rooms[meeting_id] = {}
    
    breakout_rooms[meeting_id][room_id] = participant_ids
    
    # Update participants' breakout room assignment
    for user_id in participant_ids:
        if user_id in meeting_participants.get(meeting_id, {}):
            meeting_participants[meeting_id][user_id]["breakout_room"] = room_id
    
    await db.karau_meetings.update_one(
        {"meeting_id": meeting_id},
        {"$push": {"breakout_rooms": breakout_room}}
    )
    
    return breakout_room


async def get_user_meetings(user_id: str, limit: int = 20) -> List[Dict]:
    """Get meetings for a user (hosted or participated)"""
    meetings = await db.karau_meetings.find(
        {
            "$or": [
                {"host_id": user_id},
                {"participants.user_id": user_id}
            ]
        },
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    return meetings


# STUN/TURN server configuration for WebRTC
def get_ice_servers() -> List[Dict]:
    """Get ICE server configuration for WebRTC"""
    return [
        {"urls": "stun:stun.l.google.com:19302"},
        {"urls": "stun:stun1.l.google.com:19302"},
        {"urls": "stun:stun2.l.google.com:19302"},
        {"urls": "stun:stun3.l.google.com:19302"},
        {"urls": "stun:stun4.l.google.com:19302"},
    ]


# ============ WAITING ROOM FUNCTIONS ============

async def add_to_waiting_room(
    meeting_id: str,
    user_id: str,
    user_name: str,
    user_email: str = ""
) -> Dict:
    """Add a participant to the waiting room"""
    
    if meeting_id not in waiting_rooms:
        waiting_rooms[meeting_id] = {}
    
    waiting_user = {
        "user_id": user_id,
        "user_name": user_name,
        "user_email": user_email,
        "joined_at": datetime.now(timezone.utc).isoformat(),
        "status": "waiting"  # waiting, admitted, rejected
    }
    
    waiting_rooms[meeting_id][user_id] = waiting_user
    
    logger.info(f"User {user_name} added to waiting room for meeting {meeting_id}")
    
    return waiting_user


async def get_waiting_room(meeting_id: str) -> List[Dict]:
    """Get all users in the waiting room"""
    
    if meeting_id not in waiting_rooms:
        return []
    
    return [
        user for user in waiting_rooms[meeting_id].values()
        if user.get("status") == "waiting"
    ]


async def admit_from_waiting_room(
    meeting_id: str,
    user_id: str,
    host_id: str
) -> Dict:
    """Admit a user from the waiting room (host only)"""
    
    meeting = await get_meeting(meeting_id)
    if not meeting:
        return {"error": "Meeting not found"}
    
    if meeting["host_id"] != host_id:
        return {"error": "Only the host can admit participants"}
    
    if meeting_id not in waiting_rooms or user_id not in waiting_rooms[meeting_id]:
        return {"error": "User not in waiting room"}
    
    # Update status
    waiting_rooms[meeting_id][user_id]["status"] = "admitted"
    
    logger.info(f"User {user_id} admitted from waiting room in meeting {meeting_id}")
    
    return {
        "success": True,
        "user_id": user_id,
        "admitted": True
    }


async def admit_all_from_waiting_room(meeting_id: str, host_id: str) -> Dict:
    """Admit all users from the waiting room"""
    
    meeting = await get_meeting(meeting_id)
    if not meeting:
        return {"error": "Meeting not found"}
    
    if meeting["host_id"] != host_id:
        return {"error": "Only the host can admit participants"}
    
    if meeting_id not in waiting_rooms:
        return {"admitted": 0}
    
    admitted = 0
    for user_id in waiting_rooms[meeting_id]:
        if waiting_rooms[meeting_id][user_id].get("status") == "waiting":
            waiting_rooms[meeting_id][user_id]["status"] = "admitted"
            admitted += 1
    
    return {"admitted": admitted}


async def reject_from_waiting_room(
    meeting_id: str,
    user_id: str,
    host_id: str
) -> Dict:
    """Reject a user from joining the meeting"""
    
    meeting = await get_meeting(meeting_id)
    if not meeting:
        return {"error": "Meeting not found"}
    
    if meeting["host_id"] != host_id:
        return {"error": "Only the host can reject participants"}
    
    if meeting_id in waiting_rooms and user_id in waiting_rooms[meeting_id]:
        waiting_rooms[meeting_id][user_id]["status"] = "rejected"
    
    return {"success": True, "user_id": user_id, "rejected": True}


def is_user_admitted(meeting_id: str, user_id: str) -> bool:
    """Check if user has been admitted from waiting room"""
    
    if meeting_id not in waiting_rooms:
        return True  # No waiting room, allow entry
    
    if user_id not in waiting_rooms[meeting_id]:
        return False  # Not in waiting room yet
    
    return waiting_rooms[meeting_id][user_id].get("status") == "admitted"


# ============ MEETING LOCK FUNCTIONS ============

async def lock_meeting(meeting_id: str, host_id: str) -> Dict:
    """Lock a meeting to prevent new participants"""
    
    meeting = await get_meeting(meeting_id)
    if not meeting:
        return {"error": "Meeting not found"}
    
    if meeting["host_id"] != host_id:
        return {"error": "Only the host can lock the meeting"}
    
    meeting_locks[meeting_id] = True
    
    # Update in database
    await db.karau_meetings.update_one(
        {"meeting_id": meeting_id},
        {"$set": {"settings.lock_meeting": True}}
    )
    
    logger.info(f"Meeting {meeting_id} locked by host")
    
    return {"success": True, "locked": True}


async def unlock_meeting(meeting_id: str, host_id: str) -> Dict:
    """Unlock a meeting to allow new participants"""
    
    meeting = await get_meeting(meeting_id)
    if not meeting:
        return {"error": "Meeting not found"}
    
    if meeting["host_id"] != host_id:
        return {"error": "Only the host can unlock the meeting"}
    
    meeting_locks[meeting_id] = False
    
    # Update in database
    await db.karau_meetings.update_one(
        {"meeting_id": meeting_id},
        {"$set": {"settings.lock_meeting": False}}
    )
    
    logger.info(f"Meeting {meeting_id} unlocked by host")
    
    return {"success": True, "locked": False}


def is_meeting_locked(meeting_id: str) -> bool:
    """Check if meeting is locked"""
    return meeting_locks.get(meeting_id, False)


# ============ HOST CONTROL FUNCTIONS ============

async def mute_participant(
    meeting_id: str,
    target_user_id: str,
    host_id: str
) -> Dict:
    """Mute a participant (host only)"""
    
    meeting = await get_meeting(meeting_id)
    if not meeting:
        return {"error": "Meeting not found"}
    
    if meeting["host_id"] != host_id:
        return {"error": "Only the host can mute participants"}
    
    if meeting_id in meeting_participants and target_user_id in meeting_participants[meeting_id]:
        meeting_participants[meeting_id][target_user_id]["audio_enabled"] = False
        return {"success": True, "user_id": target_user_id, "muted": True}
    
    return {"error": "Participant not found"}


async def mute_all_participants(meeting_id: str, host_id: str) -> Dict:
    """Mute all participants except host"""
    
    meeting = await get_meeting(meeting_id)
    if not meeting:
        return {"error": "Meeting not found"}
    
    if meeting["host_id"] != host_id:
        return {"error": "Only the host can mute participants"}
    
    muted = 0
    if meeting_id in meeting_participants:
        for user_id, participant in meeting_participants[meeting_id].items():
            if user_id != host_id:
                participant["audio_enabled"] = False
                muted += 1
    
    return {"success": True, "muted_count": muted}


async def remove_participant(
    meeting_id: str,
    target_user_id: str,
    host_id: str
) -> Dict:
    """Remove a participant from the meeting (host only)"""
    
    meeting = await get_meeting(meeting_id)
    if not meeting:
        return {"error": "Meeting not found"}
    
    if meeting["host_id"] != host_id:
        return {"error": "Only the host can remove participants"}
    
    if target_user_id == host_id:
        return {"error": "Host cannot remove themselves"}
    
    if meeting_id in meeting_participants and target_user_id in meeting_participants[meeting_id]:
        del meeting_participants[meeting_id][target_user_id]
        logger.info(f"User {target_user_id} removed from meeting {meeting_id}")
        return {"success": True, "user_id": target_user_id, "removed": True}
    
    return {"error": "Participant not found"}


async def update_meeting_settings(
    meeting_id: str,
    host_id: str,
    settings: Dict
) -> Dict:
    """Update meeting settings (host only)"""
    
    meeting = await get_meeting(meeting_id)
    if not meeting:
        return {"error": "Meeting not found"}
    
    if meeting["host_id"] != host_id:
        return {"error": "Only the host can update settings"}
    
    allowed_settings = [
        "waiting_room_enabled", "mute_on_entry", "allow_participants_unmute",
        "screen_share_enabled", "chat_enabled", "recording_enabled",
        "ai_notes_enabled", "breakout_rooms_enabled"
    ]
    
    update_data = {f"settings.{k}": v for k, v in settings.items() if k in allowed_settings}
    
    if update_data:
        await db.karau_meetings.update_one(
            {"meeting_id": meeting_id},
            {"$set": update_data}
        )
        
        # Update in-memory
        if meeting_id in active_meetings:
            for key, value in settings.items():
                if key in allowed_settings:
                    active_meetings[meeting_id]["settings"][key] = value
    
    return {"success": True, "updated": list(update_data.keys())}

