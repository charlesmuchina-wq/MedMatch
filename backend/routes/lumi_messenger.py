"""
LUMI Messenger - Real-time Channel-based Messaging
Standalone messaging platform integrated with KARAU auth
"""
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import json
import asyncio

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi", tags=["LUMI Messenger"])

# ============== Models ==============

class ChannelCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    is_private: bool = False
    channel_type: str = "group"  # group, project, announcement

class MessageSend(BaseModel):
    content: str
    reply_to: Optional[str] = None

class DMCreate(BaseModel):
    recipient_id: str

# ============== WebSocket Connection Manager ==============

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.user_channels: dict[str, set] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        # Update presence
        await db.lumi_presence.update_one(
            {"user_id": user_id},
            {"$set": {"status": "online", "last_seen": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        asyncio.create_task(self._set_offline(user_id))

    async def _set_offline(self, user_id: str):
        await db.lumi_presence.update_one(
            {"user_id": user_id},
            {"$set": {"status": "offline", "last_seen": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )

    async def send_to_channel(self, channel_id: str, message: dict):
        channel = await db.lumi_channels.find_one({"id": channel_id}, {"_id": 0, "members": 1})
        if not channel:
            return
        for member in channel.get("members", []):
            member_id = member.get("user_id")
            if member_id in self.active_connections:
                try:
                    await self.active_connections[member_id].send_json(message)
                except Exception:
                    pass

    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception:
                pass

    def get_online_users(self) -> list:
        return list(self.active_connections.keys())

manager = ConnectionManager()

# ============== Channel Routes ==============

@router.post("/channels")
async def create_channel(data: ChannelCreate, request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    channel_id = f"ch_{uuid.uuid4().hex[:10]}"
    channel = {
        "id": channel_id,
        "name": data.name,
        "description": data.description,
        "channel_type": data.channel_type,
        "is_private": data.is_private,
        "created_by": user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "members": [{
            "user_id": user["user_id"],
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "role": "admin",
            "joined_at": datetime.now(timezone.utc).isoformat()
        }],
        "last_message": None,
        "last_message_at": datetime.now(timezone.utc).isoformat(),
        "message_count": 0
    }
    await db.lumi_channels.insert_one(channel)
    channel.pop("_id", None)
    return channel

@router.get("/channels")
async def list_channels(request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    channels = await db.lumi_channels.find(
        {"members.user_id": user["user_id"], "channel_type": {"$ne": "dm"}},
        {"_id": 0}
    ).sort("last_message_at", -1).to_list(100)

    # Also get public channels user hasn't joined
    public_channels = await db.lumi_channels.find(
        {"is_private": False, "channel_type": {"$ne": "dm"}, "members.user_id": {"$ne": user["user_id"]}},
        {"_id": 0}
    ).sort("message_count", -1).to_list(20)

    return {
        "my_channels": channels,
        "discover": public_channels
    }

@router.get("/channels/{channel_id}")
async def get_channel(channel_id: str, request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    channel = await db.lumi_channels.find_one({"id": channel_id}, {"_id": 0})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel

@router.post("/channels/{channel_id}/join")
async def join_channel(channel_id: str, request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    channel = await db.lumi_channels.find_one({"id": channel_id}, {"_id": 0})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    existing = any(m["user_id"] == user["user_id"] for m in channel.get("members", []))
    if existing:
        return {"status": "already_member"}

    member = {
        "user_id": user["user_id"],
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "role": "member",
        "joined_at": datetime.now(timezone.utc).isoformat()
    }
    await db.lumi_channels.update_one(
        {"id": channel_id},
        {"$push": {"members": member}}
    )

    # Send system message
    sys_msg = {
        "id": f"msg_{uuid.uuid4().hex[:10]}",
        "channel_id": channel_id,
        "sender_id": "system",
        "sender_name": "LUMI",
        "content": f"{user.get('name', 'Someone')} joined the channel",
        "type": "system",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.lumi_messages.insert_one(sys_msg)
    sys_msg.pop("_id", None)
    await manager.send_to_channel(channel_id, {"type": "message", "data": sys_msg})

    return {"status": "joined"}

@router.post("/channels/{channel_id}/leave")
async def leave_channel(channel_id: str, request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    await db.lumi_channels.update_one(
        {"id": channel_id},
        {"$pull": {"members": {"user_id": user["user_id"]}}}
    )
    return {"status": "left"}

# ============== Message Routes ==============

@router.get("/channels/{channel_id}/messages")
async def get_messages(channel_id: str, request: Request, limit: int = 50, before: Optional[str] = None):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    query = {"channel_id": channel_id}
    if before:
        query["created_at"] = {"$lt": before}

    messages = await db.lumi_messages.find(
        query, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)

    messages.reverse()
    return {"messages": messages, "channel_id": channel_id}

@router.post("/channels/{channel_id}/messages")
async def send_message(channel_id: str, data: MessageSend, request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Verify user is a member
    channel = await db.lumi_channels.find_one(
        {"id": channel_id, "members.user_id": user["user_id"]},
        {"_id": 0}
    )
    if not channel:
        raise HTTPException(status_code=403, detail="Not a member of this channel")

    msg = {
        "id": f"msg_{uuid.uuid4().hex[:10]}",
        "channel_id": channel_id,
        "sender_id": user["user_id"],
        "sender_name": user.get("name", user.get("email", "Unknown")),
        "content": data.content,
        "type": "message",
        "reply_to": data.reply_to,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "reactions": {}
    }
    await db.lumi_messages.insert_one(msg)
    msg.pop("_id", None)

    # Update channel last message
    await db.lumi_channels.update_one(
        {"id": channel_id},
        {
            "$set": {
                "last_message": {"content": data.content, "sender_name": msg["sender_name"]},
                "last_message_at": msg["created_at"]
            },
            "$inc": {"message_count": 1}
        }
    )

    # Broadcast to channel via WebSocket
    await manager.send_to_channel(channel_id, {"type": "message", "data": msg})

    return msg

# ============== Reactions ==============

class ReactionAdd(BaseModel):
    emoji: str

@router.post("/messages/{message_id}/react")
async def add_reaction(message_id: str, data: ReactionAdd, request: Request):
    """Toggle a reaction on a message"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    msg = await db.lumi_messages.find_one({"id": message_id}, {"_id": 0})
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    reactions = msg.get("reactions", {})
    emoji = data.emoji
    user_id = user["user_id"]

    if emoji not in reactions:
        reactions[emoji] = []

    if user_id in reactions[emoji]:
        reactions[emoji].remove(user_id)
        if not reactions[emoji]:
            del reactions[emoji]
    else:
        reactions[emoji].append(user_id)

    await db.lumi_messages.update_one(
        {"id": message_id},
        {"$set": {"reactions": reactions}}
    )

    # Broadcast reaction update
    await manager.send_to_channel(msg["channel_id"], {
        "type": "reaction",
        "data": {"message_id": message_id, "reactions": reactions}
    })

    return {"reactions": reactions}

# ============== Search ==============

@router.get("/search")
async def search_messages(request: Request, q: str = "", limit: int = 20):
    """Search messages across all channels the user is a member of"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not q or len(q) < 2:
        return {"results": []}

    # Get channels user is in
    user_channels = await db.lumi_channels.find(
        {"members.user_id": user["user_id"]},
        {"_id": 0, "id": 1, "name": 1, "channel_type": 1}
    ).to_list(100)

    channel_ids = [ch["id"] for ch in user_channels]
    channel_map = {ch["id"]: ch for ch in user_channels}

    results = await db.lumi_messages.find(
        {
            "channel_id": {"$in": channel_ids},
            "content": {"$regex": q, "$options": "i"},
            "type": "message"
        },
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)

    # Enrich with channel info
    for r in results:
        ch = channel_map.get(r["channel_id"], {})
        r["channel_name"] = ch.get("name", "")
        r["channel_type"] = ch.get("channel_type", "")

    return {"results": results, "query": q}

# ============== Read Receipts ==============

@router.post("/channels/{channel_id}/read")
async def mark_as_read(channel_id: str, request: Request):
    """Mark all messages in a channel as read for the current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    await db.lumi_read_receipts.update_one(
        {"channel_id": channel_id, "user_id": user["user_id"]},
        {
            "$set": {
                "last_read_at": datetime.now(timezone.utc).isoformat(),
                "channel_id": channel_id,
                "user_id": user["user_id"]
            }
        },
        upsert=True
    )

    # Notify other channel members
    await manager.send_to_channel(channel_id, {
        "type": "read_receipt",
        "data": {"channel_id": channel_id, "user_id": user["user_id"], "name": user.get("name", "")}
    })

    return {"status": "read"}

@router.get("/channels/{channel_id}/read-status")
async def get_read_status(channel_id: str, request: Request):
    """Get read receipts for a channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    receipts = await db.lumi_read_receipts.find(
        {"channel_id": channel_id},
        {"_id": 0}
    ).to_list(100)

    return {"receipts": receipts}

@router.get("/unread-counts")
async def get_unread_counts(request: Request):
    """Get unread message counts for all user's channels"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Get all channels user is in
    all_channels = await db.lumi_channels.find(
        {"members.user_id": user["user_id"]},
        {"_id": 0, "id": 1}
    ).to_list(200)

    channel_ids = [ch["id"] for ch in all_channels]

    # Get read receipts
    receipts = await db.lumi_read_receipts.find(
        {"user_id": user["user_id"], "channel_id": {"$in": channel_ids}},
        {"_id": 0}
    ).to_list(200)
    receipt_map = {r["channel_id"]: r["last_read_at"] for r in receipts}

    counts = {}
    for ch_id in channel_ids:
        last_read = receipt_map.get(ch_id)
        if last_read:
            count = await db.lumi_messages.count_documents({
                "channel_id": ch_id,
                "created_at": {"$gt": last_read},
                "sender_id": {"$ne": user["user_id"]}
            })
        else:
            count = await db.lumi_messages.count_documents({
                "channel_id": ch_id,
                "sender_id": {"$ne": user["user_id"]}
            })
        if count > 0:
            counts[ch_id] = count

    return {"unread": counts}

# ============== Presence & Typing ==============

@router.get("/presence")
async def get_presence(request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    online_users = manager.get_online_users()
    return {"online": online_users}

@router.post("/channels/{channel_id}/typing")
async def notify_typing(channel_id: str, request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    await manager.send_to_channel(channel_id, {
        "type": "typing",
        "data": {"user_id": user["user_id"], "name": user.get("name", ""), "channel_id": channel_id}
    })
    return {"status": "ok"}

# ============== Direct Messages ==============

@router.post("/dm")
async def create_or_get_dm(data: DMCreate, request: Request):
    """Create a DM channel with a user, or return existing one"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if data.recipient_id == user["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot DM yourself")

    recipient = await db.users.find_one({"user_id": data.recipient_id}, {"_id": 0, "user_id": 1, "name": 1, "email": 1})
    if not recipient:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if DM already exists between these two users
    dm_key = "_".join(sorted([user["user_id"], data.recipient_id]))
    existing = await db.lumi_channels.find_one({"dm_key": dm_key}, {"_id": 0})
    if existing:
        return existing

    channel_id = f"dm_{uuid.uuid4().hex[:10]}"
    channel = {
        "id": channel_id,
        "dm_key": dm_key,
        "name": recipient.get("name", recipient.get("email", "User")),
        "description": "",
        "channel_type": "dm",
        "is_private": True,
        "created_by": user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "members": [
            {
                "user_id": user["user_id"],
                "name": user.get("name", ""),
                "email": user.get("email", ""),
                "role": "member",
                "joined_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "user_id": recipient["user_id"],
                "name": recipient.get("name", ""),
                "email": recipient.get("email", ""),
                "role": "member",
                "joined_at": datetime.now(timezone.utc).isoformat()
            }
        ],
        "last_message": None,
        "last_message_at": datetime.now(timezone.utc).isoformat(),
        "message_count": 0
    }
    await db.lumi_channels.insert_one(channel)
    channel.pop("_id", None)

    # Notify the recipient via WebSocket
    await manager.send_to_user(data.recipient_id, {
        "type": "dm_created",
        "data": {"channel_id": channel_id, "from_user": user.get("name", user.get("email", ""))}
    })

    return channel

@router.get("/dm")
async def list_dms(request: Request):
    """List all DM conversations for the current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    dms = await db.lumi_channels.find(
        {"channel_type": "dm", "members.user_id": user["user_id"]},
        {"_id": 0}
    ).sort("last_message_at", -1).to_list(50)

    # For each DM, resolve the "other" user's name for display
    for dm in dms:
        other = next((m for m in dm.get("members", []) if m["user_id"] != user["user_id"]), None)
        if other:
            dm["dm_partner"] = {"user_id": other["user_id"], "name": other.get("name", ""), "email": other.get("email", "")}
            dm["name"] = other.get("name", other.get("email", "User"))

    return {"dms": dms}

@router.get("/users/search")
async def search_users(request: Request, q: str = ""):
    """Search users for starting a DM"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not q or len(q) < 2:
        # Return recent users from the platform
        users = await db.users.find(
            {"user_id": {"$ne": user["user_id"]}},
            {"_id": 0, "user_id": 1, "name": 1, "email": 1}
        ).limit(20).to_list(20)
        return {"users": users}

    users = await db.users.find(
        {
            "user_id": {"$ne": user["user_id"]},
            "$or": [
                {"name": {"$regex": q, "$options": "i"}},
                {"email": {"$regex": q, "$options": "i"}}
            ]
        },
        {"_id": 0, "user_id": 1, "name": 1, "email": 1}
    ).limit(20).to_list(20)

    return {"users": users}

# ============== Seed Channels ==============

@router.post("/seed")
async def seed_channels(request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    existing = await db.lumi_channels.count_documents({})
    if existing > 0:
        return {"status": "already_seeded", "count": existing}

    seed_data = [
        {"name": "General", "description": "Open discussion for everyone", "channel_type": "group", "is_private": False},
        {"name": "Engineering", "description": "Development team discussions", "channel_type": "project", "is_private": False},
        {"name": "Design", "description": "UI/UX design conversations", "channel_type": "project", "is_private": False},
        {"name": "Announcements", "description": "Important updates and news", "channel_type": "announcement", "is_private": False},
        {"name": "Random", "description": "Off-topic fun and chat", "channel_type": "group", "is_private": False},
    ]

    for ch in seed_data:
        channel_id = f"ch_{uuid.uuid4().hex[:10]}"
        channel = {
            "id": channel_id,
            "name": ch["name"],
            "description": ch["description"],
            "channel_type": ch["channel_type"],
            "is_private": ch["is_private"],
            "created_by": user["user_id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "members": [{
                "user_id": user["user_id"],
                "name": user.get("name", ""),
                "email": user.get("email", ""),
                "role": "admin",
                "joined_at": datetime.now(timezone.utc).isoformat()
            }],
            "last_message": None,
            "last_message_at": datetime.now(timezone.utc).isoformat(),
            "message_count": 0
        }
        await db.lumi_channels.insert_one(channel)

        # Add a welcome message
        welcome = {
            "id": f"msg_{uuid.uuid4().hex[:10]}",
            "channel_id": channel_id,
            "sender_id": "system",
            "sender_name": "LUMI",
            "content": f"Welcome to #{ch['name']}! {ch['description']}",
            "type": "system",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.lumi_messages.insert_one(welcome)

    return {"status": "seeded", "count": len(seed_data)}

# ============== WebSocket ==============

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "typing":
                channel_id = msg.get("channel_id")
                if channel_id:
                    await manager.send_to_channel(channel_id, {
                        "type": "typing",
                        "data": {"user_id": user_id, "channel_id": channel_id}
                    })
            elif msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception:
        manager.disconnect(user_id)
