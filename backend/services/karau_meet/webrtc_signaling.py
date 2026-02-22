"""
AI KARAU Meeting - WebRTC Signaling Service
Handles peer-to-peer connection setup for video/audio calls
"""

import os
import uuid
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "medmatch")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
meetings_collection = db.karau_meetings
participants_collection = db.karau_participants


class ConnectionManager:
    """Manages WebSocket connections for WebRTC signaling"""
    
    def __init__(self):
        # meeting_id -> {user_id -> websocket}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # user_id -> meeting_id
        self.user_meetings: Dict[str, str] = {}
        # meeting_id -> {user_id -> participant_info}
        self.participants: Dict[str, Dict[str, Dict]] = {}
    
    async def connect(
        self,
        websocket: WebSocket,
        meeting_id: str,
        user_id: str,
        user_name: str,
        is_host: bool = False
    ) -> bool:
        """Connect a user to a meeting room"""
        
        await websocket.accept()
        
        # Initialize meeting room if needed
        if meeting_id not in self.active_connections:
            self.active_connections[meeting_id] = {}
            self.participants[meeting_id] = {}
        
        # FIX: Check if user already exists in this meeting (duplicate connection)
        # If so, close the old connection first
        if user_id in self.active_connections.get(meeting_id, {}):
            old_websocket = self.active_connections[meeting_id][user_id]
            try:
                await old_websocket.close(code=4001, reason="Duplicate connection - reconnecting")
                logger.info(f"Closed duplicate connection for user {user_id} in meeting {meeting_id}")
            except Exception as e:
                logger.warning(f"Error closing duplicate connection: {e}")
        
        # Store connection
        self.active_connections[meeting_id][user_id] = websocket
        self.user_meetings[user_id] = meeting_id
        
        # FIX: Only add new participant if they don't already exist
        is_new_participant = user_id not in self.participants.get(meeting_id, {})
        
        # Store/Update participant info
        participant_info = {
            "user_id": user_id,
            "user_name": user_name,
            "is_host": is_host,
            "joined_at": datetime.now(timezone.utc).isoformat(),
            "audio_enabled": True,
            "video_enabled": True,
            "screen_sharing": False,
            "hand_raised": False
        }
        self.participants[meeting_id][user_id] = participant_info
        
        # Only notify others if this is a NEW participant (not a reconnect)
        if is_new_participant:
            # Notify existing participants
            await self.broadcast_to_meeting(
                meeting_id,
                {
                    "type": "user_joined",
                    "user_id": user_id,
                    "user_name": user_name,
                    "participant": participant_info,
                    "participants": list(self.participants[meeting_id].values())
                },
                exclude_user=user_id
            )
        else:
            # This is a reconnect - just notify about participant list update
            await self.broadcast_to_meeting(
                meeting_id,
                {
                    "type": "participant_state_changed",
                    "user_id": user_id,
                    "participant": participant_info,
                    "participants": list(self.participants[meeting_id].values())
                },
                exclude_user=user_id
            )
            logger.info(f"User {user_id} reconnected to meeting {meeting_id}")
        
        # Send current participants to new user
        await self.send_personal(
            websocket,
            {
                "type": "room_state",
                "meeting_id": meeting_id,
                "participants": list(self.participants[meeting_id].values()),
                "your_id": user_id
            }
        )
        
        logger.info(f"User {user_id} joined meeting {meeting_id}")
        
        return True
    
    async def disconnect(self, user_id: str):
        """Disconnect a user from their meeting"""
        
        meeting_id = self.user_meetings.get(user_id)
        if not meeting_id:
            return
        
        # Remove from connections
        if meeting_id in self.active_connections:
            self.active_connections[meeting_id].pop(user_id, None)
            
            # Clean up empty meeting rooms
            if not self.active_connections[meeting_id]:
                del self.active_connections[meeting_id]
        
        # Remove participant info
        participant_info = None
        if meeting_id in self.participants:
            participant_info = self.participants[meeting_id].pop(user_id, None)
            
            if not self.participants[meeting_id]:
                del self.participants[meeting_id]
        
        # Remove user mapping
        self.user_meetings.pop(user_id, None)
        
        # Notify remaining participants
        if meeting_id in self.active_connections:
            await self.broadcast_to_meeting(
                meeting_id,
                {
                    "type": "user_left",
                    "user_id": user_id,
                    "user_name": participant_info.get("user_name") if participant_info else "Unknown",
                    "participants": list(self.participants.get(meeting_id, {}).values())
                }
            )
        
        logger.info(f"User {user_id} left meeting {meeting_id}")
    
    async def send_personal(self, websocket: WebSocket, message: Dict):
        """Send a message to a specific websocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_meeting(
        self,
        meeting_id: str,
        message: Dict,
        exclude_user: str = None
    ):
        """Broadcast a message to all participants in a meeting"""
        
        if meeting_id not in self.active_connections:
            return
        
        for user_id, websocket in self.active_connections[meeting_id].items():
            if user_id != exclude_user:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {user_id}: {e}")
    
    async def send_to_user(self, meeting_id: str, target_user_id: str, message: Dict):
        """Send a message to a specific user in a meeting"""
        
        if meeting_id not in self.active_connections:
            return False
        
        websocket = self.active_connections[meeting_id].get(target_user_id)
        if websocket:
            try:
                await websocket.send_json(message)
                return True
            except Exception as e:
                logger.error(f"Error sending to {target_user_id}: {e}")
        
        return False
    
    def get_participants(self, meeting_id: str) -> List[Dict]:
        """Get list of participants in a meeting"""
        return list(self.participants.get(meeting_id, {}).values())
    
    def get_participant_count(self, meeting_id: str) -> int:
        """Get number of participants in a meeting"""
        return len(self.participants.get(meeting_id, {}))
    
    async def update_participant_state(
        self,
        meeting_id: str,
        user_id: str,
        updates: Dict
    ):
        """Update participant state (audio/video/screen share)"""
        
        if meeting_id not in self.participants:
            return
        
        if user_id not in self.participants[meeting_id]:
            return
        
        # Update local state
        allowed_keys = {"audio_enabled", "video_enabled", "screen_sharing", "hand_raised"}
        for key, value in updates.items():
            if key in allowed_keys:
                self.participants[meeting_id][user_id][key] = value
        
        # Broadcast state change
        await self.broadcast_to_meeting(
            meeting_id,
            {
                "type": "participant_state_changed",
                "user_id": user_id,
                "changes": updates,
                "participant": self.participants[meeting_id][user_id]
            }
        )


# Global connection manager instance
manager = ConnectionManager()


async def handle_webrtc_signaling(
    websocket: WebSocket,
    meeting_id: str,
    user_id: str,
    user_name: str,
    is_host: bool = False
):
    """
    Handle WebRTC signaling for a meeting participant
    
    This manages:
    - ICE candidate exchange
    - SDP offer/answer exchange
    - Participant state updates
    - Chat messages
    """
    
    # Connect the user
    await manager.connect(websocket, meeting_id, user_id, user_name, is_host)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "offer":
                # WebRTC offer - forward to target peer
                target_user = data.get("target")
                await manager.send_to_user(
                    meeting_id,
                    target_user,
                    {
                        "type": "offer",
                        "offer": data.get("offer"),
                        "from_user": user_id,
                        "from_name": user_name
                    }
                )
            
            elif message_type == "answer":
                # WebRTC answer - forward to target peer
                target_user = data.get("target")
                await manager.send_to_user(
                    meeting_id,
                    target_user,
                    {
                        "type": "answer",
                        "answer": data.get("answer"),
                        "from_user": user_id
                    }
                )
            
            elif message_type == "ice_candidate":
                # ICE candidate - forward to target peer
                target_user = data.get("target")
                await manager.send_to_user(
                    meeting_id,
                    target_user,
                    {
                        "type": "ice_candidate",
                        "candidate": data.get("candidate"),
                        "from_user": user_id
                    }
                )
            
            elif message_type == "state_update":
                # Participant state change (mute, video, screen share)
                await manager.update_participant_state(
                    meeting_id,
                    user_id,
                    data.get("state", {})
                )
            
            elif message_type == "chat":
                # Chat message - broadcast to all
                await manager.broadcast_to_meeting(
                    meeting_id,
                    {
                        "type": "chat",
                        "from_user": user_id,
                        "from_name": user_name,
                        "message": data.get("message", ""),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
            
            elif message_type == "raise_hand":
                # Hand raise toggle
                await manager.update_participant_state(
                    meeting_id,
                    user_id,
                    {"hand_raised": data.get("raised", False)}
                )
            
            elif message_type == "reaction":
                # Emoji reaction
                await manager.broadcast_to_meeting(
                    meeting_id,
                    {
                        "type": "reaction",
                        "from_user": user_id,
                        "from_name": user_name,
                        "emoji": data.get("emoji", "👍"),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
            
            elif message_type == "ping":
                # Keep-alive ping
                await manager.send_personal(websocket, {"type": "pong"})
            
            # Host controls
            elif message_type == "mute_participant" and is_host:
                target_user = data.get("target")
                await manager.send_to_user(
                    meeting_id,
                    target_user,
                    {
                        "type": "host_action",
                        "action": "mute_request",
                        "from_host": user_name
                    }
                )
            
            elif message_type == "remove_participant" and is_host:
                target_user = data.get("target")
                await manager.send_to_user(
                    meeting_id,
                    target_user,
                    {
                        "type": "host_action",
                        "action": "removed",
                        "reason": data.get("reason", "Removed by host")
                    }
                )
                # Force disconnect will happen on client side
            
    except WebSocketDisconnect:
        await manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
        await manager.disconnect(user_id)


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance"""
    return manager
