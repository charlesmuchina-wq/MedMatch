"""
AI KARAU Meeting - WebRTC Signaling Service
Handles peer-to-peer connection setup for video/audio calls

Enhanced with:
- Server-side heartbeats (ping/pong) for zombie connection detection
- Idempotency keys for event deduplication
- Session recovery tokens for reconnection state
- Proper connection lifecycle management
"""

import os
import uuid
import json
import asyncio
import random
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

# Heartbeat settings
HEARTBEAT_INTERVAL = 15  # seconds
HEARTBEAT_TIMEOUT = 30   # seconds - mark as zombie if no pong received


class ConnectionManager:
    """Manages WebSocket connections for WebRTC signaling with robust lifecycle handling"""
    
    def __init__(self):
        # meeting_id -> {user_id -> websocket}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # user_id -> meeting_id
        self.user_meetings: Dict[str, str] = {}
        # meeting_id -> {user_id -> participant_info}
        self.participants: Dict[str, Dict[str, Dict]] = {}
        # Session tokens for reconnection: user_id -> session_token
        self.session_tokens: Dict[str, str] = {}
        # Last pong received: user_id -> timestamp
        self.last_pong: Dict[str, datetime] = {}
        # Processed event IDs for idempotency: Set of event_ids
        self.processed_events: Set[str] = set()
        # Max size for processed events cache
        self.max_processed_events = 10000
        # Connection state: user_id -> "active" | "reconnecting" | "disconnected"
        self.connection_states: Dict[str, str] = {}
        # Heartbeat tasks
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}
        # Sequence numbers for message ordering: meeting_id -> sequence
        self.message_sequences: Dict[str, int] = {}
        # Message history for replay: meeting_id -> list of recent messages
        self.message_history: Dict[str, List[Dict]] = {}
        self.max_message_history = 100  # Keep last 100 messages per meeting
    
    def _get_next_sequence(self, meeting_id: str) -> int:
        """Get next sequence number for a meeting"""
        if meeting_id not in self.message_sequences:
            self.message_sequences[meeting_id] = 0
        self.message_sequences[meeting_id] += 1
        return self.message_sequences[meeting_id]
    
    def _store_message(self, meeting_id: str, message: Dict):
        """Store message in history for replay"""
        if meeting_id not in self.message_history:
            self.message_history[meeting_id] = []
        
        self.message_history[meeting_id].append(message)
        
        # Trim to max size
        if len(self.message_history[meeting_id]) > self.max_message_history:
            self.message_history[meeting_id] = self.message_history[meeting_id][-self.max_message_history:]
    
    def get_messages_since(self, meeting_id: str, last_sequence: int) -> List[Dict]:
        """Get all messages since a sequence number for replay"""
        if meeting_id not in self.message_history:
            return []
        
        return [
            msg for msg in self.message_history[meeting_id]
            if msg.get('sequence', 0) > last_sequence
        ]
    
    async def connect(
        self,
        websocket: WebSocket,
        meeting_id: str,
        user_id: str,
        user_name: str,
        is_host: bool = False,
        session_token: Optional[str] = None
    ) -> bool:
        """Connect a user to a meeting room with robust lifecycle management"""
        
        await websocket.accept()
        
        # Initialize meeting room if needed
        if meeting_id not in self.active_connections:
            self.active_connections[meeting_id] = {}
            self.participants[meeting_id] = {}
        
        # Check connection state - handle reconnection vs new connection
        is_reconnection = False
        
        # Validate session token for reconnection
        if session_token and session_token == self.session_tokens.get(user_id):
            is_reconnection = True
            logger.info(f"Valid session token for user {user_id} - resuming session")
        
        # Check if user already has an active connection (duplicate)
        if user_id in self.active_connections.get(meeting_id, {}):
            old_websocket = self.active_connections[meeting_id][user_id]
            # Cancel old heartbeat task
            if user_id in self.heartbeat_tasks:
                self.heartbeat_tasks[user_id].cancel()
                del self.heartbeat_tasks[user_id]
            try:
                await old_websocket.close(code=4001, reason="Duplicate connection - reconnecting")
                logger.info(f"Closed duplicate connection for user {user_id} in meeting {meeting_id}")
            except Exception as e:
                logger.warning(f"Error closing duplicate connection: {e}")
            is_reconnection = True
        
        # Generate new session token for this connection
        new_session_token = str(uuid.uuid4())
        self.session_tokens[user_id] = new_session_token
        
        # Store connection
        self.active_connections[meeting_id][user_id] = websocket
        self.user_meetings[user_id] = meeting_id
        self.connection_states[user_id] = "active"
        self.last_pong[user_id] = datetime.now(timezone.utc)
        
        # Determine if this is a new participant or reconnection
        is_new_participant = user_id not in self.participants.get(meeting_id, {}) and not is_reconnection
        
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
        
        # Generate idempotent event ID
        event_id = f"join_{user_id}_{meeting_id}_{int(datetime.now(timezone.utc).timestamp())}"
        
        # Only notify others if this is a NEW participant (not a reconnect)
        if is_new_participant:
            # Notify existing participants with idempotency key
            await self.broadcast_to_meeting(
                meeting_id,
                {
                    "type": "user_joined",
                    "event_id": event_id,
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
                    "event_id": event_id,
                    "user_id": user_id,
                    "participant": participant_info,
                    "participants": list(self.participants[meeting_id].values()),
                    "is_reconnection": True
                },
                exclude_user=user_id
            )
            logger.info(f"User {user_id} reconnected to meeting {meeting_id}")
        
        # Send current state to user with session token for future reconnection
        await self.send_personal(
            websocket,
            {
                "type": "room_state",
                "meeting_id": meeting_id,
                "participants": list(self.participants[meeting_id].values()),
                "your_id": user_id,
                "session_token": new_session_token,
                "is_reconnection": is_reconnection
            }
        )
        
        # Start heartbeat monitoring for this user
        self.heartbeat_tasks[user_id] = asyncio.create_task(
            self._heartbeat_monitor(meeting_id, user_id)
        )
        
        logger.info(f"User {user_id} joined meeting {meeting_id} (reconnection: {is_reconnection})")
        
        return True
    
    async def _heartbeat_monitor(self, meeting_id: str, user_id: str):
        """Monitor connection health with ping/pong mechanism"""
        try:
            while True:
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                
                # Check if user is still connected
                if user_id not in self.active_connections.get(meeting_id, {}):
                    break
                
                websocket = self.active_connections[meeting_id].get(user_id)
                if not websocket:
                    break
                
                # Send ping
                try:
                    await websocket.send_json({
                        "type": "ping",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                except Exception as e:
                    logger.warning(f"Failed to send ping to {user_id}: {e}")
                    # Mark as zombie and trigger disconnect
                    await self._handle_zombie_connection(meeting_id, user_id)
                    break
                
                # Check if we received a pong recently
                last_pong_time = self.last_pong.get(user_id)
                if last_pong_time:
                    time_since_pong = (datetime.now(timezone.utc) - last_pong_time).total_seconds()
                    if time_since_pong > HEARTBEAT_TIMEOUT:
                        logger.warning(f"User {user_id} hasn't responded in {time_since_pong}s - marking as zombie")
                        await self._handle_zombie_connection(meeting_id, user_id)
                        break
                        
        except asyncio.CancelledError:
            logger.debug(f"Heartbeat monitor cancelled for {user_id}")
        except Exception as e:
            logger.error(f"Heartbeat monitor error for {user_id}: {e}")
    
    async def _handle_zombie_connection(self, meeting_id: str, user_id: str):
        """Handle a connection that's become unresponsive"""
        self.connection_states[user_id] = "disconnected"
        
        # Close the websocket if possible
        websocket = self.active_connections.get(meeting_id, {}).get(user_id)
        if websocket:
            try:
                await websocket.close(code=4002, reason="Connection timeout - zombie detected")
            except Exception:
                pass
        
        # Don't fully disconnect yet - allow time for reconnection
        # Mark participant as temporarily disconnected
        if meeting_id in self.participants and user_id in self.participants[meeting_id]:
            self.participants[meeting_id][user_id]["connection_status"] = "disconnected"
            
            # Notify others
            await self.broadcast_to_meeting(
                meeting_id,
                {
                    "type": "participant_connection_changed",
                    "user_id": user_id,
                    "status": "disconnected",
                    "participants": list(self.participants[meeting_id].values())
                },
                exclude_user=user_id
            )
        
        logger.info(f"Marked user {user_id} as disconnected (zombie) in meeting {meeting_id}")
    
    def handle_pong(self, user_id: str):
        """Handle pong response from client"""
        self.last_pong[user_id] = datetime.now(timezone.utc)
        self.connection_states[user_id] = "active"
    
    def is_event_processed(self, event_id: str) -> bool:
        """Check if an event has already been processed (idempotency)"""
        if event_id in self.processed_events:
            return True
        
        # Clean up old events if cache is too large
        if len(self.processed_events) > self.max_processed_events:
            # Remove oldest half
            self.processed_events = set(list(self.processed_events)[self.max_processed_events // 2:])
        
        self.processed_events.add(event_id)
        return False
    
    async def disconnect(self, user_id: str):
        """Disconnect a user from their meeting"""
        
        meeting_id = self.user_meetings.get(user_id)
        if not meeting_id:
            return
        
        # Cancel heartbeat task
        if user_id in self.heartbeat_tasks:
            self.heartbeat_tasks[user_id].cancel()
            del self.heartbeat_tasks[user_id]
        
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
        
        # Remove user mapping and state
        self.user_meetings.pop(user_id, None)
        self.connection_states.pop(user_id, None)
        self.last_pong.pop(user_id, None)
        # Keep session token briefly for potential reconnection
        
        # Generate idempotent event ID for leave
        event_id = f"leave_{user_id}_{meeting_id}_{int(datetime.now(timezone.utc).timestamp())}"
        
        # Notify remaining participants
        if meeting_id in self.active_connections:
            await self.broadcast_to_meeting(
                meeting_id,
                {
                    "type": "user_left",
                    "event_id": event_id,
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
        exclude_user: str = None,
        store_in_history: bool = True
    ):
        """Broadcast a message to all participants in a meeting with sequence numbers"""
        
        if meeting_id not in self.active_connections:
            return
        
        # Add sequence number to message
        message['sequence'] = self._get_next_sequence(meeting_id)
        message['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        # Store important messages in history for replay
        if store_in_history and message.get('type') in ['chat', 'ai_note', 'user_joined', 'user_left']:
            self._store_message(meeting_id, message)
        
        # Broadcast to all participants
        for user_id, websocket in list(self.active_connections[meeting_id].items()):
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
    is_host: bool = False,
    session_token: Optional[str] = None
):
    """
    Handle WebRTC signaling for a meeting participant
    
    This manages:
    - ICE candidate exchange
    - SDP offer/answer exchange
    - Participant state updates
    - Chat messages
    - Heartbeat ping/pong
    - Session recovery on reconnection
    """
    
    # Connect the user with session token for reconnection support
    await manager.connect(websocket, meeting_id, user_id, user_name, is_host, session_token)
    
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
            
            elif message_type == "whiteboard_stroke":
                # Broadcast drawing stroke to all other participants
                await manager.broadcast_to_meeting(
                    meeting_id,
                    {
                        "type": "whiteboard_stroke",
                        "from_user": user_id,
                        "from_name": user_name,
                        "stroke": data.get("stroke"),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    exclude_user=user_id,
                    store_in_history=False
                )
            
            elif message_type == "whiteboard_cursor":
                # Broadcast cursor position for presence awareness
                await manager.broadcast_to_meeting(
                    meeting_id,
                    {
                        "type": "whiteboard_cursor",
                        "from_user": user_id,
                        "from_name": user_name,
                        "x": data.get("x"),
                        "y": data.get("y"),
                        "color": data.get("color", "#20b2aa")
                    },
                    exclude_user=user_id,
                    store_in_history=False
                )
            
            elif message_type == "whiteboard_clear":
                # Broadcast clear event
                await manager.broadcast_to_meeting(
                    meeting_id,
                    {
                        "type": "whiteboard_clear",
                        "from_user": user_id,
                        "from_name": user_name,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    exclude_user=user_id,
                    store_in_history=False
                )
            
            elif message_type == "ping":
                # Keep-alive ping from client
                await manager.send_personal(websocket, {"type": "pong"})
            
            elif message_type == "pong":
                # Pong response from client - update last activity
                manager.handle_pong(user_id)
            
            # Host controls
            elif message_type == "mute_participant" and is_host:
                target_user = data.get("target")
                await manager.send_to_user(
                    meeting_id,
                    target_user,
                    {
                        "type": "host_action",
                        "action": "force_mute",
                        "from_host": user_name
                    }
                )
            
            elif message_type == "mute_all" and is_host:
                # Mute all participants except host
                await manager.broadcast_to_meeting(
                    meeting_id,
                    {
                        "type": "host_action",
                        "action": "force_mute",
                        "from_host": user_name
                    },
                    exclude_user=user_id,
                    store_in_history=False
                )
            
            elif message_type == "pass_mic" and is_host:
                # Pass mic to a participant - unmute them, mute everyone else
                target_user = data.get("target")
                # Mute all except host and target
                for pid in manager.active_connections.get(meeting_id, {}):
                    if pid != user_id and pid != target_user:
                        await manager.send_to_user(
                            meeting_id,
                            pid,
                            {
                                "type": "host_action",
                                "action": "force_mute",
                                "from_host": user_name
                            }
                        )
                # Tell target to unmute
                await manager.send_to_user(
                    meeting_id,
                    target_user,
                    {
                        "type": "host_action",
                        "action": "pass_mic",
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
