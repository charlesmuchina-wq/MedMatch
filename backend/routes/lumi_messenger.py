"""
LUMI Messenger - Real-time Channel-based Messaging
Standalone messaging platform integrated with KARAU auth
Features: Domain privacy, threads, presence, retention, voice calls
"""
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
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
    channel_type: str = "group"  # group, project, announcement, domain

class ThreadReply(BaseModel):
    content: str

class PresenceUpdate(BaseModel):
    status: str  # available, busy, in_meeting, ooo, vacation

class RetentionConfig(BaseModel):
    days: int = 90

class MessageSend(BaseModel):
    content: str
    reply_to: Optional[str] = None

class DMCreate(BaseModel):
    recipient_id: str

class ChannelNotifPrefs(BaseModel):
    channel_id: str
    mute: bool = False
    level: str = "all"  # all, mentions, none

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

# ============== Message Edit & Delete ==============

class MessageEdit(BaseModel):
    content: str

EDIT_WINDOW_MINUTES = 15

@router.put("/messages/{message_id}")
async def edit_message(message_id: str, data: MessageEdit, request: Request):
    """Edit a message within the edit window"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    msg = await db.lumi_messages.find_one({"id": message_id}, {"_id": 0})
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg["sender_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Can only edit your own messages")

    created = datetime.fromisoformat(msg["created_at"].replace('Z', '+00:00'))
    if (datetime.now(timezone.utc) - created).total_seconds() > EDIT_WINDOW_MINUTES * 60:
        raise HTTPException(status_code=403, detail=f"Edit window ({EDIT_WINDOW_MINUTES} min) has expired")

    if not data.content.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty")

    await db.lumi_messages.update_one(
        {"id": message_id},
        {"$set": {
            "content": data.content.strip(),
            "edited": True,
            "edited_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    await manager.send_to_channel(msg["channel_id"], {
        "type": "message_edited",
        "data": {"message_id": message_id, "content": data.content.strip(), "edited_at": datetime.now(timezone.utc).isoformat()}
    })

    return {"id": message_id, "content": data.content.strip(), "edited": True}


@router.delete("/messages/{message_id}")
async def delete_message(message_id: str, request: Request):
    """Delete a message within the edit window"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    msg = await db.lumi_messages.find_one({"id": message_id}, {"_id": 0})
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg["sender_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Can only delete your own messages")

    created = datetime.fromisoformat(msg["created_at"].replace('Z', '+00:00'))
    if (datetime.now(timezone.utc) - created).total_seconds() > EDIT_WINDOW_MINUTES * 60:
        raise HTTPException(status_code=403, detail=f"Delete window ({EDIT_WINDOW_MINUTES} min) has expired")

    await db.lumi_messages.delete_one({"id": message_id})

    await manager.send_to_channel(msg["channel_id"], {
        "type": "message_deleted",
        "data": {"message_id": message_id}
    })

    return {"deleted": True, "id": message_id}



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
    """Search users for starting a DM - filtered by same domain"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    email = user.get("email", "")
    domain = email.split("@")[-1] if "@" in email else ""

    base_query = {"user_id": {"$ne": user["user_id"]}}
    # Domain privacy: only show users from same domain
    if domain:
        base_query["email"] = {"$regex": f"@{domain}$", "$options": "i"}

    if q and len(q) >= 2:
        base_query["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"email": {"$regex": q, "$options": "i"}}
        ]

    users = await db.users.find(
        base_query,
        {"_id": 0, "user_id": 1, "name": 1, "email": 1}
    ).limit(20).to_list(20)

    # Add presence
    presences = await db.lumi_presence.find({}, {"_id": 0}).to_list(500)
    presence_map = {p["user_id"]: p["status"] for p in presences}
    online = manager.get_online_users()
    for u in users:
        uid = u["user_id"]
        u["status"] = presence_map.get(uid, "available" if uid in online else "offline")

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

# ============== Domain Channels ==============

@router.get("/domain/members")
async def get_domain_members(request: Request, last_name: str = ""):
    """Get members from the same email domain, optionally filtered by last name"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    email = user.get("email", "")
    domain = email.split("@")[-1] if "@" in email else ""
    if not domain:
        return {"members": [], "domain": ""}

    query = {"email": {"$regex": f"@{domain}$", "$options": "i"}}
    if last_name and len(last_name) >= 2:
        query["name"] = {"$regex": last_name, "$options": "i"}

    members = await db.users.find(
        query, {"_id": 0, "user_id": 1, "name": 1, "email": 1}
    ).limit(50).to_list(50)

    # Add presence info
    for m in members:
        presence = await db.lumi_presence.find_one({"user_id": m["user_id"]}, {"_id": 0})
        m["status"] = presence.get("status", "offline") if presence else "offline"

    return {"members": members, "domain": domain}

@router.post("/domain/auto-channel")
async def create_domain_channel(request: Request):
    """Auto-create a domain-protected channel with all domain members"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    email = user.get("email", "")
    domain = email.split("@")[-1] if "@" in email else ""
    if not domain:
        raise HTTPException(status_code=400, detail="No domain found")

    # Check if domain channel exists
    existing = await db.lumi_channels.find_one({"domain": domain, "channel_type": "domain"}, {"_id": 0})
    if existing:
        return existing

    # Get all domain members
    domain_users = await db.users.find(
        {"email": {"$regex": f"@{domain}$", "$options": "i"}},
        {"_id": 0, "user_id": 1, "name": 1, "email": 1}
    ).to_list(200)

    channel_id = f"dom_{uuid.uuid4().hex[:10]}"
    members = [{
        "user_id": u["user_id"],
        "name": u.get("name", ""),
        "email": u.get("email", ""),
        "role": "admin" if u["user_id"] == user["user_id"] else "member",
        "joined_at": datetime.now(timezone.utc).isoformat()
    } for u in domain_users]

    org_name = domain.split(".")[0].capitalize()
    channel = {
        "id": channel_id,
        "name": f"{org_name} Team",
        "description": f"Protected channel for @{domain}",
        "channel_type": "domain",
        "domain": domain,
        "is_private": True,
        "threads_enabled": True,
        "created_by": user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "members": members,
        "last_message": None,
        "last_message_at": datetime.now(timezone.utc).isoformat(),
        "message_count": 0
    }
    await db.lumi_channels.insert_one(channel)
    channel.pop("_id", None)

    # Welcome message
    welcome = {
        "id": f"msg_{uuid.uuid4().hex[:10]}",
        "channel_id": channel_id,
        "sender_id": "system",
        "sender_name": "LUMI",
        "content": f"Welcome to the {org_name} team channel! This is a protected space for @{domain} members.",
        "type": "system",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.lumi_messages.insert_one(welcome)

    return channel

# ============== Message Threads ==============

@router.post("/messages/{message_id}/thread")
async def reply_to_thread(message_id: str, data: ThreadReply, request: Request):
    """Reply to a message in a thread"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    parent = await db.lumi_messages.find_one({"id": message_id}, {"_id": 0})
    if not parent:
        raise HTTPException(status_code=404, detail="Message not found")

    reply = {
        "id": f"msg_{uuid.uuid4().hex[:10]}",
        "channel_id": parent["channel_id"],
        "thread_parent_id": message_id,
        "sender_id": user["user_id"],
        "sender_name": user.get("name", user.get("email", "Unknown")),
        "content": data.content,
        "type": "thread_reply",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "reactions": {}
    }
    await db.lumi_messages.insert_one(reply)
    reply.pop("_id", None)

    # Update thread count on parent
    await db.lumi_messages.update_one(
        {"id": message_id},
        {"$inc": {"thread_count": 1}, "$set": {"last_thread_at": reply["created_at"]}}
    )

    # Broadcast
    await manager.send_to_channel(parent["channel_id"], {
        "type": "thread_reply",
        "data": {**reply, "parent_id": message_id}
    })

    return reply

@router.get("/messages/{message_id}/thread")
async def get_thread(message_id: str, request: Request):
    """Get all replies in a thread"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    parent = await db.lumi_messages.find_one({"id": message_id}, {"_id": 0})
    if not parent:
        raise HTTPException(status_code=404, detail="Message not found")

    replies = await db.lumi_messages.find(
        {"thread_parent_id": message_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(200)

    return {"parent": parent, "replies": replies}

# ============== Presence ==============

@router.put("/presence")
async def update_presence(data: PresenceUpdate, request: Request):
    """Update user presence status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    valid = ["available", "busy", "in_meeting", "ooo", "vacation"]
    if data.status not in valid:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {valid}")

    await db.lumi_presence.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "status": data.status,
            "last_seen": datetime.now(timezone.utc).isoformat(),
            "user_id": user["user_id"]
        }},
        upsert=True
    )

    # Broadcast presence change
    for uid in manager.get_online_users():
        await manager.send_to_user(uid, {
            "type": "presence_change",
            "data": {"user_id": user["user_id"], "status": data.status, "name": user.get("name", "")}
        })

    return {"status": data.status}

@router.get("/presence/all")
async def get_all_presence(request: Request):
    """Get presence for all domain users"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    presences = await db.lumi_presence.find({}, {"_id": 0}).to_list(500)
    # Also check who is in active KARAU meetings
    active_meetings = await db.karau_meetings.find(
        {"status": "active"},
        {"_id": 0, "participants": 1}
    ).to_list(100)
    in_meeting = set()
    for m in active_meetings:
        for p in m.get("participants", []):
            in_meeting.add(p.get("user_id"))

    presence_map = {p["user_id"]: p["status"] for p in presences}
    online_users = manager.get_online_users()

    # Auto-set in_meeting for users in active KARAU meetings
    for uid in in_meeting:
        presence_map[uid] = "in_meeting"

    # Set online users to available if no explicit status
    for uid in online_users:
        if uid not in presence_map:
            presence_map[uid] = "available"

    return {"presence": presence_map}

# ============== Retention ==============

@router.get("/settings/retention")
async def get_retention(request: Request):
    """Get message retention settings"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    settings = await db.lumi_settings.find_one({"key": "retention"}, {"_id": 0})
    return {"retention_days": settings.get("days", 90) if settings else 90}

@router.put("/settings/retention")
async def update_retention(data: RetentionConfig, request: Request):
    """Update message retention (admin only)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    await db.lumi_settings.update_one(
        {"key": "retention"},
        {"$set": {"key": "retention", "days": data.days, "updated_by": user["user_id"], "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"retention_days": data.days}

@router.post("/settings/cleanup")
async def cleanup_old_messages(request: Request):
    """Run retention cleanup"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    settings = await db.lumi_settings.find_one({"key": "retention"}, {"_id": 0})
    days = settings.get("days", 90) if settings else 90
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    result = await db.lumi_messages.delete_many({"created_at": {"$lt": cutoff}})
    return {"deleted": result.deleted_count, "retention_days": days}

# ============== Channel Members ==============

@router.get("/channels/{channel_id}/members")
async def get_channel_members(channel_id: str, request: Request):
    """Get channel members with presence"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    channel = await db.lumi_channels.find_one({"id": channel_id}, {"_id": 0})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    members = channel.get("members", [])
    presences = await db.lumi_presence.find({}, {"_id": 0}).to_list(500)
    presence_map = {p["user_id"]: p["status"] for p in presences}
    online = manager.get_online_users()

    for m in members:
        uid = m["user_id"]
        if uid in presence_map:
            m["status"] = presence_map[uid]
        elif uid in online:
            m["status"] = "available"
        else:
            m["status"] = "offline"

    return {"members": members, "channel_id": channel_id}

@router.post("/channels/{channel_id}/members/add")
async def add_member(channel_id: str, request: Request):
    """Add a member to a channel (admin only)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    body = await request.json()
    target_id = body.get("user_id")
    if not target_id:
        raise HTTPException(status_code=400, detail="user_id required")

    channel = await db.lumi_channels.find_one({"id": channel_id}, {"_id": 0})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # Check admin
    is_admin = any(m["user_id"] == user["user_id"] and m.get("role") == "admin" for m in channel.get("members", []))
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin only")

    # Get target user
    target = await db.users.find_one({"user_id": target_id}, {"_id": 0, "user_id": 1, "name": 1, "email": 1})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    # Domain check for domain channels
    if channel.get("channel_type") == "domain" and channel.get("domain"):
        target_domain = target.get("email", "").split("@")[-1]
        if target_domain != channel["domain"]:
            raise HTTPException(status_code=403, detail="User not in this domain")

    existing = any(m["user_id"] == target_id for m in channel.get("members", []))
    if existing:
        return {"status": "already_member"}

    member = {
        "user_id": target["user_id"],
        "name": target.get("name", ""),
        "email": target.get("email", ""),
        "role": "member",
        "joined_at": datetime.now(timezone.utc).isoformat()
    }
    await db.lumi_channels.update_one({"id": channel_id}, {"$push": {"members": member}})
    return {"status": "added"}

@router.post("/channels/{channel_id}/members/remove")
async def remove_member(channel_id: str, request: Request):
    """Remove a member from a channel (admin only)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    body = await request.json()
    target_id = body.get("user_id")
    if not target_id:
        raise HTTPException(status_code=400, detail="user_id required")

    channel = await db.lumi_channels.find_one({"id": channel_id}, {"_id": 0})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    is_admin = any(m["user_id"] == user["user_id"] and m.get("role") == "admin" for m in channel.get("members", []))
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin only")

    await db.lumi_channels.update_one({"id": channel_id}, {"$pull": {"members": {"user_id": target_id}}})
    return {"status": "removed"}

# ============== Voice Call ==============

@router.post("/voice/call")
async def initiate_call(request: Request):
    """Initiate a 1:1 voice call"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    body = await request.json()
    recipient_id = body.get("recipient_id")
    call_type = body.get("type", "voice")  # voice or video

    if not recipient_id:
        raise HTTPException(status_code=400, detail="recipient_id required")

    call_id = f"call_{uuid.uuid4().hex[:10]}"
    call = {
        "id": call_id,
        "caller_id": user["user_id"],
        "caller_name": user.get("name", ""),
        "recipient_id": recipient_id,
        "type": call_type,
        "status": "ringing",
        "started_at": datetime.now(timezone.utc).isoformat()
    }
    await db.lumi_calls.insert_one(call)
    call.pop("_id", None)

    # Notify recipient
    await manager.send_to_user(recipient_id, {
        "type": "incoming_call",
        "data": call
    })

    return call

@router.post("/voice/call/{call_id}/answer")
async def answer_call(call_id: str, request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    await db.lumi_calls.update_one({"id": call_id}, {"$set": {"status": "active"}})
    call = await db.lumi_calls.find_one({"id": call_id}, {"_id": 0})
    if call:
        await manager.send_to_user(call["caller_id"], {"type": "call_answered", "data": {"call_id": call_id}})
    return {"status": "active"}

@router.post("/voice/call/{call_id}/end")
async def end_call(call_id: str, request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    call = await db.lumi_calls.find_one({"id": call_id}, {"_id": 0})
    await db.lumi_calls.update_one({"id": call_id}, {"$set": {"status": "ended", "ended_at": datetime.now(timezone.utc).isoformat()}})
    if call:
        other = call["recipient_id"] if call["caller_id"] == user["user_id"] else call["caller_id"]
        await manager.send_to_user(other, {"type": "call_ended", "data": {"call_id": call_id}})
    return {"status": "ended"}

# ============== User Profile & Capabilities ==============

AI_CAPABILITIES = [
    {"id": "sentiment", "name": "Sentiment Analysis", "description": "Analyze team morale and mood from channel conversations", "category": "Productivity AI"},
    {"id": "tasks", "name": "Task Extraction", "description": "AI extracts action items and tasks from chat messages", "category": "Productivity AI"},
    {"id": "reports", "name": "Weekly Reports", "description": "Auto-generate channel activity and progress reports", "category": "Productivity AI"},
    {"id": "ask_ai", "name": "Ask LUMI AI", "description": "Conversational AI to query projects, tasks, and meetings", "category": "Actionable Intelligence"},
    {"id": "decision_cards", "name": "Decision Cards", "description": "AI-generated interactive cards for quick team decisions", "category": "Actionable Intelligence"},
    {"id": "anomaly_alerts", "name": "Anomaly Alerts", "description": "Proactive alerts when unusual patterns are detected", "category": "Actionable Intelligence"},
    {"id": "knowledge_graph", "name": "Knowledge Graph", "description": "Visualize relationships between people, tasks, and projects", "category": "Graph Intelligence"},
    {"id": "bottleneck_detection", "name": "Bottleneck Detection", "description": "Identify workload imbalances and project blockers", "category": "Graph Intelligence"},
    {"id": "what_if", "name": "What-If Simulator", "description": "Simulate project scenarios and predict outcomes", "category": "Advanced Collaboration"},
    {"id": "smart_notifications", "name": "Smart Notifications", "description": "AI-prioritized alerts based on urgency and relevance", "category": "Advanced Collaboration"},
    {"id": "translation", "name": "Real-time Translation", "description": "Translate messages into 20+ languages instantly", "category": "Communication"},
    {"id": "command_bar", "name": "Command Bar (Ctrl+K)", "description": "Quick search and AI queries from anywhere", "category": "Navigation"},
    {"id": "threading", "name": "Message Threading", "description": "Organize conversations with threaded replies", "category": "Core"},
    {"id": "file_sharing", "name": "File Sharing", "description": "Share images, documents, and files securely", "category": "Core"},
    {"id": "reactions", "name": "Reactions", "description": "React to messages with emoji reactions", "category": "Core"},
]

@router.get("/profile/capabilities")
async def get_user_capabilities(request: Request):
    """Get user profile with LUMI capabilities"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Get user's channels
    my_channels = await db.lumi_channels.find(
        {"members.user_id": user["user_id"]},
        {"_id": 0, "id": 1, "name": 1, "channel_type": 1, "description": 1, "is_private": 1}
    ).to_list(100)

    # Get user's DMs
    dms = await db.lumi_dms.find(
        {"participants": user["user_id"]},
        {"_id": 0, "id": 1, "participants": 1}
    ).to_list(100)

    # Get presence
    presence = await db.lumi_presence.find_one(
        {"user_id": user["user_id"]}, {"_id": 0}
    )
    current_status = presence.get("status", "available") if presence else "available"

    # Get notification preferences
    notif_prefs = await db.lumi_notif_prefs.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).to_list(200)
    prefs_map = {p["channel_id"]: {"mute": p.get("mute", False), "level": p.get("level", "all")} for p in notif_prefs}

    # Activity stats
    msg_count = await db.lumi_messages.count_documents({"sender_id": user["user_id"]})

    return {
        "user": {
            "user_id": user["user_id"],
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "profile_picture": user.get("profile_picture", ""),
            "role": user.get("role", "member"),
            "auth_method": user.get("auth_method", "email"),
            "status": current_status,
            "messages_sent": msg_count,
        },
        "capabilities": AI_CAPABILITIES,
        "channels": my_channels,
        "dm_count": len(dms),
        "notification_preferences": prefs_map,
    }


@router.put("/profile/notification-prefs")
async def update_notification_prefs(data: ChannelNotifPrefs, request: Request):
    """Update notification preferences for a channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    await db.lumi_notif_prefs.update_one(
        {"user_id": user["user_id"], "channel_id": data.channel_id},
        {"$set": {
            "user_id": user["user_id"],
            "channel_id": data.channel_id,
            "mute": data.mute,
            "level": data.level,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )

    return {"status": "updated", "channel_id": data.channel_id, "mute": data.mute, "level": data.level}


@router.get("/notifications/hub")
async def get_notification_hub(request: Request):
    """Centralized notification hub - aggregates all notification sources"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    notifications = []

    # 1. Unread mentions (messages containing @user)
    user_channels = await db.lumi_channels.find(
        {"members.user_id": user["user_id"]}, {"_id": 0, "id": 1, "name": 1}
    ).to_list(100)
    channel_ids = [ch["id"] for ch in user_channels]
    channel_names = {ch["id"]: ch["name"] for ch in user_channels}

    mentions = await db.lumi_messages.find(
        {"channel_id": {"$in": channel_ids}, "content": {"$regex": f"@{user.get('name', '')}", "$options": "i"}, "sender_id": {"$ne": user["user_id"]}},
        {"_id": 0}
    ).sort("created_at", -1).to_list(10)
    for m in mentions:
        notifications.append({
            "id": f"mention_{m['id']}", "type": "mention", "source": "chat",
            "title": f"Mentioned in #{channel_names.get(m['channel_id'], 'channel')}",
            "body": m.get("content", "")[:120], "channel_id": m.get("channel_id"),
            "priority": "high", "timestamp": m.get("created_at", "")
        })

    # 2. AI anomaly alerts
    try:
        anomalies = await db.lumi_anomalies.find({}, {"_id": 0}).sort("created_at", -1).to_list(5)
        for a in anomalies:
            notifications.append({
                "id": f"anomaly_{a.get('id', '')}", "type": "anomaly", "source": "ai",
                "title": a.get("title", "Anomaly Detected"),
                "body": a.get("description", ""), "priority": a.get("severity", "medium"),
                "timestamp": a.get("created_at", "")
            })
    except Exception:
        pass

    # 3. Assigned tasks
    try:
        tasks = await db.lumi_tasks.find(
            {"assignee_id": user["user_id"], "status": {"$ne": "done"}},
            {"_id": 0}
        ).sort("created_at", -1).to_list(10)
        for t in tasks:
            prio = t.get("priority", "medium")
            notifications.append({
                "id": f"task_{t.get('id', '')}", "type": "task", "source": "ai",
                "title": f"Task: {t.get('task', '')[:60]}",
                "body": f"Assigned by AI from channel conversation",
                "priority": prio, "deadline": t.get("deadline", ""),
                "timestamp": t.get("created_at", "")
            })
    except Exception:
        pass

    # 4. Unread DMs
    dms = await db.lumi_dms.find(
        {"participants": user["user_id"]}, {"_id": 0, "id": 1}
    ).to_list(50)
    dm_ids = [d["id"] for d in dms]
    if dm_ids:
        last_reads = {}
        read_records = await db.lumi_read_receipts.find(
            {"user_id": user["user_id"], "channel_id": {"$in": dm_ids}}, {"_id": 0}
        ).to_list(50)
        for r in read_records:
            last_reads[r["channel_id"]] = r.get("last_read_at", "")

        for dm_id in dm_ids:
            last_read = last_reads.get(dm_id, "2000-01-01T00:00:00")
            unread = await db.lumi_messages.find(
                {"channel_id": dm_id, "sender_id": {"$ne": user["user_id"]}, "created_at": {"$gt": last_read}},
                {"_id": 0}
            ).sort("created_at", -1).to_list(3)
            for m in unread:
                notifications.append({
                    "id": f"dm_{m['id']}", "type": "dm", "source": "chat",
                    "title": f"Message from {m.get('sender_name', 'Someone')}",
                    "body": m.get("content", "")[:120], "channel_id": dm_id,
                    "priority": "medium", "timestamp": m.get("created_at", "")
                })

    # Sort by timestamp desc and priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    notifications.sort(key=lambda n: (priority_order.get(n.get("priority", "low"), 3), -(hash(n.get("timestamp", "")))), reverse=False)

    return {
        "notifications": notifications[:30],
        "total": len(notifications),
        "sources": {
            "mentions": sum(1 for n in notifications if n["type"] == "mention"),
            "anomalies": sum(1 for n in notifications if n["type"] == "anomaly"),
            "tasks": sum(1 for n in notifications if n["type"] == "task"),
            "dms": sum(1 for n in notifications if n["type"] == "dm"),
        }
    }



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
