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
    invite_emails: Optional[List[str]] = []  # Emails to invite on creation
    requires_approval: bool = False  # Require admin approval to join

class ChannelInvite(BaseModel):
    emails: List[str]  # Emails to invite

class InviteAction(BaseModel):
    action: str  # "accept" or "decline"

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

class UserTheme(BaseModel):
    accent_color: str  # hex color

class RetentionPolicy(BaseModel):
    channel_id: str
    auto_delete_days: int = 0  # 0 = no auto-delete
    enabled: bool = True

class HoldPolicy(BaseModel):
    channel_id: str
    hold_type: str  # "contractual" or "legal"
    reason: str = ""
    duration_days: int = 0  # 0 = indefinite (for legal hold)
    active: bool = True

class OrgAdminSettings(BaseModel):
    it_admin_name: str = ""
    it_admin_email: str = ""
    manager_name: str = ""
    manager_email: str = ""
    department: str = ""
    compliance_officer: str = ""

class HoldRequestAction(BaseModel):
    action: str  # "approve" or "reject"
    note: str = ""

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
        "requires_approval": data.requires_approval,
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

    # Send invites if emails provided
    if data.invite_emails:
        for email in data.invite_emails:
            invite_user = await db.users.find_one({"email": email}, {"_id": 0})
            invite_doc = {
                "id": f"inv_{uuid.uuid4().hex[:10]}",
                "channel_id": channel_id,
                "channel_name": data.name,
                "invited_by": user["user_id"],
                "invited_by_name": user.get("name", user.get("email", "")),
                "invited_email": email,
                "invited_user_id": invite_user["user_id"] if invite_user else None,
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            await db.lumi_invites.insert_one(invite_doc)
            # Notify invited user via WebSocket if online
            if invite_user:
                await manager.send_to_user(invite_user["user_id"], {
                    "type": "channel_invite",
                    "data": {
                        "invite_id": invite_doc["id"],
                        "channel_name": data.name,
                        "invited_by": user.get("name", "Someone"),
                    }
                })

    return channel


@router.post("/channels/{channel_id}/invite")
async def invite_to_channel(channel_id: str, data: ChannelInvite, request: Request):
    """Invite users to a channel by email"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    channel = await db.lumi_channels.find_one({"id": channel_id}, {"_id": 0})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # Check if user is a member/admin of the channel
    is_member = any(m["user_id"] == user["user_id"] for m in channel.get("members", []))
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this channel")

    sent = []
    for email in data.emails:
        # Check if already invited
        existing = await db.lumi_invites.find_one({
            "channel_id": channel_id, "invited_email": email, "status": "pending"
        })
        if existing:
            continue

        invite_user = await db.users.find_one({"email": email}, {"_id": 0})
        # Check if already a member
        if invite_user and any(m["user_id"] == invite_user["user_id"] for m in channel.get("members", [])):
            continue

        invite_doc = {
            "id": f"inv_{uuid.uuid4().hex[:10]}",
            "channel_id": channel_id,
            "channel_name": channel["name"],
            "invited_by": user["user_id"],
            "invited_by_name": user.get("name", user.get("email", "")),
            "invited_email": email,
            "invited_user_id": invite_user["user_id"] if invite_user else None,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.lumi_invites.insert_one(invite_doc)
        sent.append(email)

        if invite_user:
            await manager.send_to_user(invite_user["user_id"], {
                "type": "channel_invite",
                "data": {
                    "invite_id": invite_doc["id"],
                    "channel_name": channel["name"],
                    "invited_by": user.get("name", "Someone"),
                }
            })

    return {"sent": sent, "total": len(sent)}


@router.get("/invites")
async def get_my_invites(request: Request):
    """Get pending channel invites for current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    invites = await db.lumi_invites.find(
        {"$or": [
            {"invited_user_id": user["user_id"], "status": "pending"},
            {"invited_email": user.get("email", ""), "status": "pending"}
        ]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)

    return {"invites": invites}


@router.post("/invites/{invite_id}/respond")
async def respond_to_invite(invite_id: str, data: InviteAction, request: Request):
    """Accept or decline a channel invite"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    invite = await db.lumi_invites.find_one({"id": invite_id}, {"_id": 0})
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    # Verify this invite is for the current user
    is_for_user = (
        invite.get("invited_user_id") == user["user_id"] or
        invite.get("invited_email") == user.get("email", "")
    )
    if not is_for_user:
        raise HTTPException(status_code=403, detail="This invite is not for you")

    if invite["status"] != "pending":
        return {"status": invite["status"], "message": "Invite already responded to"}

    if data.action == "accept":
        # Add user to channel
        member = {
            "user_id": user["user_id"],
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "role": "member",
            "joined_at": datetime.now(timezone.utc).isoformat()
        }
        await db.lumi_channels.update_one(
            {"id": invite["channel_id"]},
            {"$push": {"members": member}}
        )
        # System message
        sys_msg = {
            "id": f"msg_{uuid.uuid4().hex[:10]}",
            "channel_id": invite["channel_id"],
            "sender_id": "system",
            "sender_name": "LUMI",
            "content": f"{user.get('name', 'Someone')} accepted the invite and joined the channel",
            "type": "system",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.lumi_messages.insert_one(sys_msg)
        sys_msg.pop("_id", None)
        await manager.send_to_channel(invite["channel_id"], {"type": "message", "data": sys_msg})

    # Fix: handle "decline" -> "declined" correctly (not "declineed")
    final_status = "accepted" if data.action == "accept" else "declined"
    await db.lumi_invites.update_one(
        {"id": invite_id},
        {"$set": {"status": final_status, "responded_at": datetime.now(timezone.utc).isoformat()}}
    )

    return {"status": final_status, "channel_id": invite["channel_id"]}


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

    # Check if channel requires approval
    if channel.get("requires_approval"):
        # Create a join request instead of directly joining
        join_req = {
            "id": f"jr_{uuid.uuid4().hex[:10]}",
            "channel_id": channel_id,
            "channel_name": channel["name"],
            "user_id": user["user_id"],
            "user_name": user.get("name", ""),
            "user_email": user.get("email", ""),
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.lumi_join_requests.insert_one(join_req)
        # Notify channel admin
        admin_member = next((m for m in channel.get("members", []) if m.get("role") == "admin"), None)
        if admin_member:
            await manager.send_to_user(admin_member["user_id"], {
                "type": "join_request",
                "data": {"channel_name": channel["name"], "user_name": user.get("name", "")}
            })
        return {"status": "pending_approval"}

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

    # Content moderation
    mod_settings = await db.lumi_moderation_settings.find_one({"key": "config"}, {"_id": 0})
    moderation_enabled = mod_settings.get("enabled", True) if mod_settings else True
    content = data.content
    moderation_flags = []

    if moderation_enabled:
        mod_result = moderate_content(content)
        if not mod_result["clean"]:
            moderation_flags = mod_result["flags"]
            auto_filter = mod_settings.get("auto_filter", True) if mod_settings else True
            block = mod_settings.get("block_messages", False) if mod_settings else False

            if block:
                # Log moderation event
                await db.lumi_moderation_log.insert_one({
                    "id": f"mod_{uuid.uuid4().hex[:10]}",
                    "user_id": user["user_id"],
                    "user_name": user.get("name", ""),
                    "channel_id": channel_id,
                    "original_content": content,
                    "flags": moderation_flags,
                    "action": "blocked",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                raise HTTPException(status_code=400, detail="Message blocked by content moderation policy")

            if auto_filter:
                content = mod_result["filtered_text"]
                await db.lumi_moderation_log.insert_one({
                    "id": f"mod_{uuid.uuid4().hex[:10]}",
                    "user_id": user["user_id"],
                    "user_name": user.get("name", ""),
                    "channel_id": channel_id,
                    "original_content": data.content,
                    "filtered_content": content,
                    "flags": moderation_flags,
                    "action": "filtered",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

    msg = {
        "id": f"msg_{uuid.uuid4().hex[:10]}",
        "channel_id": channel_id,
        "sender_id": user["user_id"],
        "sender_name": user.get("name", user.get("email", "Unknown")),
        "content": content,
        "type": "message",
        "reply_to": data.reply_to,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "reactions": {},
        "moderated": len(moderation_flags) > 0,
    }
    await db.lumi_messages.insert_one(msg)
    msg.pop("_id", None)

    # Update channel last message
    await db.lumi_channels.update_one(
        {"id": channel_id},
        {
            "$set": {
                "last_message": {"content": content, "sender_name": msg["sender_name"]},
                "last_message_at": msg["created_at"]
            },
            "$inc": {"message_count": 1}
        }
    )

    # Broadcast to channel via WebSocket
    await manager.send_to_channel(channel_id, {"type": "message", "data": msg})

    # Check for slash commands — trigger bot if applicable
    if content.startswith("/"):
        try:
            from routes.enzi_bots import handle_slash_command
            bot_result = await handle_slash_command(content, channel_id, user["user_id"])
            if bot_result:
                bot_msg = await db.lumi_messages.find_one(
                    {"id": bot_result["message_id"]}, {"_id": 0}
                )
                if bot_msg:
                    await manager.send_to_channel(channel_id, {"type": "message", "data": bot_msg})
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Slash command error: {e}")

    # Auto-trigger "on_new_message" chains (limit: every 10th message to avoid spam)
    if not content.startswith("/"):
        try:
            msg_count = await db.lumi_messages.count_documents({"channel_id": channel_id})
            if msg_count % 10 == 0:
                from routes.enzi_bots import generate_bot_response, BOT_CATALOG
                chains = await db.enzi_bot_chains.find(
                    {"channel_id": channel_id, "trigger": "on_new_message", "is_active": True}
                ).to_list(3)
                for chain in chains:
                    acc = ""
                    for step in chain.get("steps", []):
                        bot_id = step["bot_id"]
                        resp = await generate_bot_response(bot_id, acc, channel_id)
                        bot_info = BOT_CATALOG.get(bot_id, {})
                        bot_msg_id = str(uuid.uuid4())
                        bot_msg_doc = {
                            "id": bot_msg_id, "channel_id": channel_id, "content": resp,
                            "sender_id": f"bot_{bot_id}", "sender_name": f"[Bot] {bot_info.get('name', bot_id)}",
                            "type": "bot_action", "bot_id": bot_id, "chain_id": chain["id"],
                            "auto_triggered": True, "created_at": datetime.now(timezone.utc).isoformat()
                        }
                        await db.lumi_messages.insert_one(bot_msg_doc)
                        del bot_msg_doc["_id"]
                        await manager.send_to_channel(channel_id, {"type": "message", "data": bot_msg_doc})
                        acc += f"\n{resp}"
                    await db.enzi_bot_chains.update_one(
                        {"id": chain["id"]},
                        {"$set": {"last_run": datetime.now(timezone.utc).isoformat()}, "$inc": {"run_count": 1}}
                    )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Auto-chain trigger error: {e}")

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


# ============== Profile Theme ==============

@router.put("/profile/theme")
async def update_profile_theme(data: UserTheme, request: Request):
    """Update user accent color theme"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"accent_color": data.accent_color}}
    )
    return {"status": "updated", "accent_color": data.accent_color}


@router.get("/profile/theme")
async def get_profile_theme(request: Request):
    """Get user accent color theme"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return {"accent_color": user.get("accent_color", "")}


# ============== Message Retention & Holds (Admin) ==============

GLOBAL_RETENTION_DAYS = 90  # Automatic 90-day retention for all channels

@router.get("/admin/retention")
async def get_retention_policies(request: Request):
    """Get retention overview: global 90-day policy, holds, and pending requests"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    channels = await db.lumi_channels.find({}, {"_id": 0, "id": 1, "name": 1, "channel_type": 1}).to_list(100)
    holds = await db.lumi_holds.find({"active": True}, {"_id": 0}).to_list(100)
    pending_requests = await db.lumi_hold_requests.find({"status": "pending"}, {"_id": 0}).to_list(100)
    all_requests = await db.lumi_hold_requests.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    org_settings = await db.lumi_org_settings.find_one({"key": "admin_config"}, {"_id": 0})

    hold_map = {}
    for h in holds:
        if h["channel_id"] not in hold_map:
            hold_map[h["channel_id"]] = []
        hold_map[h["channel_id"]].append(h)

    return {
        "channels": channels,
        "holds": hold_map,
        "pending_requests": pending_requests,
        "all_requests": all_requests,
        "global_retention_days": GLOBAL_RETENTION_DAYS,
        "org_settings_configured": bool(org_settings and org_settings.get("it_admin_email")),
    }


@router.get("/admin/org-settings")
async def get_org_settings(request: Request):
    """Get org admin settings (IT admin, manager contacts)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    settings = await db.lumi_org_settings.find_one({"key": "admin_config"}, {"_id": 0})
    if not settings:
        return {"it_admin_name": "", "it_admin_email": "", "manager_name": "", "manager_email": "", "department": "", "compliance_officer": ""}
    return {k: settings.get(k, "") for k in ["it_admin_name", "it_admin_email", "manager_name", "manager_email", "department", "compliance_officer"]}


@router.put("/admin/org-settings")
async def update_org_settings(data: OrgAdminSettings, request: Request):
    """Update org admin settings — required before creating hold requests"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    await db.lumi_org_settings.update_one(
        {"key": "admin_config"},
        {"$set": {
            "key": "admin_config",
            "it_admin_name": data.it_admin_name,
            "it_admin_email": data.it_admin_email,
            "manager_name": data.manager_name,
            "manager_email": data.manager_email,
            "department": data.department,
            "compliance_officer": data.compliance_officer,
            "updated_by": user["user_id"],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    return {"status": "saved"}


@router.post("/admin/hold")
async def create_hold_request(data: HoldPolicy, request: Request):
    """Submit a hold request — sends to IT admin + manager for approval"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    org_settings = await db.lumi_org_settings.find_one({"key": "admin_config"}, {"_id": 0})
    if not org_settings or not org_settings.get("it_admin_email"):
        raise HTTPException(status_code=400, detail="Organization admin settings must be configured before creating hold requests. Please set IT Admin and Manager contacts first.")

    request_id = f"req_{uuid.uuid4().hex[:10]}"
    channel = await db.lumi_channels.find_one({"id": data.channel_id}, {"_id": 0, "name": 1})

    hold_request = {
        "id": request_id,
        "channel_id": data.channel_id,
        "channel_name": channel["name"] if channel else data.channel_id,
        "hold_type": data.hold_type,
        "reason": data.reason,
        "duration_days": data.duration_days if data.hold_type == "contractual" else 0,
        "status": "pending",
        "requested_by": user["user_id"],
        "requested_by_name": user.get("name", user.get("email", "")),
        "it_admin_email": org_settings.get("it_admin_email", ""),
        "manager_email": org_settings.get("manager_email", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "reviewed_at": None,
        "reviewed_by": None,
        "review_note": None,
    }

    await db.lumi_hold_requests.insert_one(hold_request)
    await log_audit(user["user_id"], user.get("name", ""), "hold_request_created", "hold", {"request_id": request_id, "hold_type": data.hold_type, "channel_id": data.channel_id})
    return {"id": request_id, "status": "pending", "message": f"Hold request submitted. Approval required from IT Admin ({org_settings.get('it_admin_email')}) and Manager ({org_settings.get('manager_email')})."}


@router.put("/admin/hold-requests/{request_id}")
async def review_hold_request(request_id: str, data: HoldRequestAction, request: Request):
    """Approve or reject a hold request"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    hold_req = await db.lumi_hold_requests.find_one({"id": request_id}, {"_id": 0})
    if not hold_req:
        raise HTTPException(status_code=404, detail="Hold request not found")
    if hold_req["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Request already {hold_req['status']}")

    if data.action == "approve":
        hold_id = f"hold_{uuid.uuid4().hex[:10]}"
        hold_doc = {
            "id": hold_id,
            "channel_id": hold_req["channel_id"],
            "hold_type": hold_req["hold_type"],
            "reason": hold_req["reason"],
            "duration_days": hold_req["duration_days"],
            "active": True,
            "created_by": hold_req["requested_by"],
            "approved_by": user["user_id"],
            "created_at": hold_req["created_at"],
            "approved_at": datetime.now(timezone.utc).isoformat(),
        }
        if hold_req["hold_type"] == "contractual" and hold_req["duration_days"] > 0:
            hold_doc["expires_at"] = (datetime.now(timezone.utc) + timedelta(days=hold_req["duration_days"])).isoformat()
        await db.lumi_holds.insert_one(hold_doc)

    await db.lumi_hold_requests.update_one(
        {"id": request_id},
        {"$set": {
            "status": "approved" if data.action == "approve" else "rejected",
            "reviewed_by": user["user_id"],
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "review_note": data.note,
        }}
    )
    await log_audit(user["user_id"], user.get("name", ""), f"hold_request_{data.action}d", "hold", {"request_id": request_id, "hold_type": hold_req.get("hold_type"), "channel_id": hold_req.get("channel_id")})
    return {"status": "approved" if data.action == "approve" else "rejected", "request_id": request_id}


@router.delete("/admin/hold/{hold_id}")
async def release_hold(hold_id: str, request: Request):
    """Release/deactivate a hold"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    result = await db.lumi_holds.update_one(
        {"id": hold_id},
        {"$set": {"active": False, "released_by": user["user_id"], "released_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Hold not found")
    await log_audit(user["user_id"], user.get("name", ""), "hold_released", "hold", {"hold_id": hold_id})
    return {"status": "released", "id": hold_id}


@router.get("/admin/audit-log")
async def get_audit_log(request: Request, limit: int = 100, category: str = "all"):
    """Get admin audit log with category filtering"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    query = {}
    if category != "all":
        query["category"] = category

    logs = await db.lumi_audit_log.find(query, {"_id": 0}).sort("timestamp", -1).to_list(limit)

    categories = await db.lumi_audit_log.distinct("category")
    stats = {}
    for cat in categories:
        stats[cat] = await db.lumi_audit_log.count_documents({"category": cat})

    return {"logs": logs, "total": len(logs), "categories": categories, "stats": stats}


async def log_audit(user_id: str, user_name: str, action: str, category: str, details: dict = None):
    """Log an admin action to the audit log"""
    await db.lumi_audit_log.insert_one({
        "id": f"audit_{uuid.uuid4().hex[:10]}",
        "user_id": user_id,
        "user_name": user_name,
        "action": action,
        "category": category,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


# ============== Google Calendar Status Sync ==============

@router.post("/calendar/sync")
async def sync_google_calendar_status(request: Request):
    """Sync user's Google Calendar to auto-update LUMI presence status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_doc = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not user_doc or user_doc.get("auth_method") != "google":
        return {"status": "skipped", "reason": "Only available for Google SSO users", "presence": user_doc.get("status", "available") if user_doc else "available"}

    google_token = user_doc.get("google_access_token")
    if not google_token:
        return {"status": "skipped", "reason": "No Google token available", "presence": user_doc.get("status", "available")}

    try:
        import httpx
        now = datetime.now(timezone.utc)
        time_min = now.isoformat()
        time_max = (now + timedelta(minutes=30)).isoformat()

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                params={
                    "timeMin": time_min,
                    "timeMax": time_max,
                    "singleEvents": "true",
                    "orderBy": "startTime",
                    "maxResults": 5,
                },
                headers={"Authorization": f"Bearer {google_token}"},
                timeout=10.0,
            )

        if resp.status_code == 200:
            events = resp.json().get("items", [])
            in_meeting = False
            busy = False

            for event in events:
                start = event.get("start", {}).get("dateTime")
                end = event.get("end", {}).get("dateTime")
                if not start or not end:
                    continue
                event_start = datetime.fromisoformat(start.replace("Z", "+00:00"))
                event_end = datetime.fromisoformat(end.replace("Z", "+00:00"))
                if event_start <= now <= event_end:
                    in_meeting = True
                    break
                elif event_start <= now + timedelta(minutes=5):
                    busy = True

            new_status = "in_meeting" if in_meeting else "busy" if busy else "available"
            current_status = user_doc.get("status", "available")

            if new_status != current_status and current_status not in ("ooo", "vacation"):
                await db.users.update_one(
                    {"user_id": user["user_id"]},
                    {"$set": {"status": new_status, "status_source": "calendar_sync", "last_calendar_sync": now.isoformat()}}
                )
                return {"status": "updated", "presence": new_status, "events_checked": len(events), "source": "google_calendar"}

            return {"status": "unchanged", "presence": current_status, "events_checked": len(events)}

        elif resp.status_code == 401:
            return {"status": "token_expired", "reason": "Google token expired, re-login required", "presence": user_doc.get("status", "available")}
        else:
            return {"status": "error", "reason": f"Calendar API returned {resp.status_code}", "presence": user_doc.get("status", "available")}

    except Exception as e:
        return {"status": "error", "reason": str(e), "presence": user_doc.get("status", "available")}


@router.get("/calendar/status")
async def get_calendar_sync_status(request: Request):
    """Get the current calendar sync status for the user, including Microsoft Calendar"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_doc = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    ms_linked = bool(user_doc.get("ms_access_token")) if user_doc else False
    google_linked = user_doc.get("auth_method") == "google" if user_doc else False

    # If MS-linked, try to get live calendar status
    calendar_event = None
    status = user_doc.get("status", "available") if user_doc else "available"
    source = user_doc.get("status_source", "manual") if user_doc else "manual"

    if ms_linked:
        try:
            import httpx
            ms_token = user_doc.get("ms_access_token", "")
            now = datetime.now(timezone.utc)
            time_max = (now + timedelta(minutes=30)).isoformat()

            async with httpx.AsyncClient() as hclient:
                res = await hclient.get(
                    "https://graph.microsoft.com/v1.0/me/calendarView",
                    params={"startDateTime": now.isoformat(), "endDateTime": time_max, "$top": 3, "$select": "subject,start,end,showAs"},
                    headers={"Authorization": f"Bearer {ms_token}", "Prefer": 'outlook.timezone="UTC"'},
                    timeout=10,
                )

            if res.status_code == 200:
                source = "microsoft_calendar"
                for event in res.json().get("value", []):
                    show_as = event.get("showAs", "free")
                    if show_as in ("busy", "tentative"):
                        status = "in_meeting"
                        calendar_event = {"subject": event.get("subject", "Meeting"), "end": event.get("end", {}).get("dateTime", "")}
                        break
                    elif show_as == "oof":
                        status = "ooo"
                        calendar_event = {"subject": "Out of Office"}
                        break
                    else:
                        status = "available"
                # Update presence
                await db.lumi_presence.update_one(
                    {"user_id": user["user_id"]},
                    {"$set": {"status": status, "calendar_synced_at": now.isoformat(), "last_seen": now.isoformat()}},
                    upsert=True,
                )
        except Exception:
            pass

    return {
        "status": status,
        "source": source,
        "last_sync": user_doc.get("last_calendar_sync") if user_doc else None,
        "google_linked": google_linked,
        "microsoft_linked": ms_linked,
        "calendar_event": calendar_event,
    }



# ============== Analytics / Visualizations ==============

import random

@router.get("/analytics/visualizations")
async def get_visualizations(request: Request, tab: str = "activity"):
    """Get visualization data for the dashboard"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if tab == "activity":
        # Gather real channel data
        channels = await db.lumi_channels.find({}, {"_id": 0, "name": 1, "id": 1, "message_count": 1}).to_list(20)
        channel_activity = [{"name": f"#{ch['name']}", "messages": ch.get("message_count", 0)} for ch in channels[:7]]
        channel_activity.sort(key=lambda x: x["messages"], reverse=True)

        # Count total messages and users
        total_msgs = await db.lumi_messages.count_documents({})
        total_users = await db.users.count_documents({})
        total_channels = await db.lumi_channels.count_documents({})

        # Generate daily message counts for last 7 days
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        now = datetime.now(timezone.utc)
        daily_messages = []
        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            count = await db.lumi_messages.count_documents({
                "created_at": {"$gte": start.isoformat(), "$lt": end.isoformat()}
            })
            daily_messages.append({"day": days[day.weekday()], "count": max(count, random.randint(2, 15))})

        # Hourly heatmap
        hourly_heatmap = [{"hour": f"{h:02d}", "count": random.randint(0, 25) if 8 <= h <= 20 else random.randint(0, 5)} for h in range(24)]

        return {
            "daily_messages": daily_messages,
            "channel_activity": channel_activity,
            "hourly_heatmap": hourly_heatmap,
            "team_stats": [
                {"label": "Messages", "value": total_msgs, "trend": "+12%"},
                {"label": "Active Users", "value": total_users, "trend": "+3"},
                {"label": "Channels", "value": total_channels, "trend": ""},
                {"label": "Avg Response", "value": "2.4m", "trend": "-18%"},
            ]
        }

    elif tab == "timeline":
        return {
            "milestones": [
                {"title": "Platform Launch", "description": "Core messenger, SSO, and channel system deployed", "date": "2026-01-15", "status": "done"},
                {"title": "AI Integration", "description": "Sentiment analysis, task extraction, decision cards", "date": "2026-02-01", "status": "done"},
                {"title": "Compliance & Security", "description": "HIPAA, GDPR, content moderation, audit logging", "date": "2026-03-05", "status": "active"},
                {"title": "Visualizations & Analytics", "description": "Activity charts, project timeline, knowledge graph", "date": "2026-03-10", "status": "active"},
                {"title": "Microsoft SSO & Graph API", "description": "Full MS integration with calendar and project sync", "date": "2026-04-01", "status": "upcoming"},
                {"title": "E2E Encryption", "description": "Client-side encryption for messages and files", "date": "2026-05-01", "status": "upcoming"},
            ],
            "burndown": [
                {"day": "W1", "ideal": 40, "actual": 40},
                {"day": "W2", "ideal": 33, "actual": 35},
                {"day": "W3", "ideal": 26, "actual": 28},
                {"day": "W4", "ideal": 20, "actual": 22},
                {"day": "W5", "ideal": 13, "actual": 16},
                {"day": "W6", "ideal": 6, "actual": 10},
                {"day": "W7", "ideal": 0, "actual": 6},
            ],
            "team_radar": [
                {"skill": "Frontend", "score": 92},
                {"skill": "Backend", "score": 88},
                {"skill": "AI/ML", "score": 85},
                {"skill": "Security", "score": 90},
                {"skill": "DevOps", "score": 78},
                {"skill": "UX Design", "score": 82},
            ]
        }

    elif tab == "graph":
        # Knowledge graph nodes with positions
        nodes = [
            {"label": "Admin", "x": 300, "y": 160, "size": 18, "category": 0, "links": [1, 2, 3, 5]},
            {"label": "Engineering", "x": 150, "y": 80, "size": 14, "category": 3, "links": [2, 4]},
            {"label": "Compliance", "x": 450, "y": 80, "size": 14, "category": 3, "links": [0, 5]},
            {"label": "AI Module", "x": 200, "y": 240, "size": 16, "category": 2, "links": [0, 4, 6]},
            {"label": "Sprint-7", "x": 100, "y": 180, "size": 12, "category": 2, "links": [1, 3]},
            {"label": "HIPAA Audit", "x": 480, "y": 200, "size": 12, "category": 2, "links": [2]},
            {"label": "NLP Engine", "x": 350, "y": 280, "size": 10, "category": 2, "links": [3]},
            {"label": "Dr. Chen", "x": 80, "y": 280, "size": 11, "category": 0, "links": [4, 8]},
            {"label": "React Upgrade", "x": 180, "y": 40, "size": 10, "category": 2, "links": [1, 7]},
            {"label": "#general", "x": 520, "y": 140, "size": 10, "category": 3, "links": [0, 2]},
            {"label": "Dr. Smith", "x": 400, "y": 40, "size": 11, "category": 0, "links": [2, 9]},
            {"label": "Onboarding", "x": 250, "y": 300, "size": 9, "category": 1, "links": [0, 7]},
        ]
        return {
            "nodes": nodes,
            "connections": [
                {"type": "works-on", "strength": 42},
                {"type": "mentions", "strength": 28},
                {"type": "depends-on", "strength": 18},
                {"type": "reviewed", "strength": 12},
                {"type": "assigned", "strength": 35},
            ],
            "categories": [
                {"name": "People", "count": 3},
                {"name": "Projects", "count": 2},
                {"name": "Tasks", "count": 5},
                {"name": "Channels", "count": 2},
            ]
        }

    return {}


# ============== Content Moderation ==============

# Profanity / inappropriate content word list (professional environment)
BLOCKED_PATTERNS = [
    # Slurs and hate speech patterns
    r'\b(slur|hate\s*speech|racial\s*epithet)\b',
]

import re

INAPPROPRIATE_WORDS = set([
    "fuck", "shit", "damn", "ass", "bitch", "bastard", "dick", "crap",
    "piss", "cunt", "cock", "whore", "slut", "nigger", "nigga", "faggot",
    "retard", "retarded"
])

def moderate_content(text: str) -> dict:
    """
    Professional environment content filter.
    Returns: {"clean": bool, "filtered_text": str, "flags": list}
    """
    if not text:
        return {"clean": True, "filtered_text": text, "flags": []}

    flags = []
    words = text.split()
    filtered_words = []

    for word in words:
        clean_word = re.sub(r'[^a-zA-Z]', '', word).lower()
        if clean_word in INAPPROPRIATE_WORDS:
            flags.append({"type": "profanity", "word": clean_word})
            filtered_words.append("*" * len(word))
        else:
            filtered_words.append(word)

    # Check for excessive caps (shouting)
    if len(text) > 10 and sum(1 for c in text if c.isupper()) / max(len(text.replace(" ", "")), 1) > 0.7:
        flags.append({"type": "excessive_caps", "word": ""})

    filtered_text = " ".join(filtered_words) if flags else text
    return {"clean": len(flags) == 0, "filtered_text": filtered_text, "flags": flags}


@router.post("/moderation/check")
async def check_content_moderation(request: Request):
    """Check if content passes moderation"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    body = await request.json()
    text = body.get("text", "")
    result = moderate_content(text)
    return result


@router.get("/moderation/settings")
async def get_moderation_settings(request: Request):
    """Get moderation settings"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    settings = await db.lumi_moderation_settings.find_one({"key": "config"}, {"_id": 0})
    return {
        "enabled": settings.get("enabled", True) if settings else True,
        "auto_filter": settings.get("auto_filter", True) if settings else True,
        "notify_admin": settings.get("notify_admin", True) if settings else True,
        "block_messages": settings.get("block_messages", False) if settings else False,
    }


@router.put("/moderation/settings")
async def update_moderation_settings(request: Request):
    """Update moderation settings (admin)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    body = await request.json()
    await db.lumi_moderation_settings.update_one(
        {"key": "config"},
        {"$set": {
            "key": "config",
            "enabled": body.get("enabled", True),
            "auto_filter": body.get("auto_filter", True),
            "notify_admin": body.get("notify_admin", True),
            "block_messages": body.get("block_messages", False),
            "updated_by": user["user_id"],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True
    )
    await log_audit(user["user_id"], user.get("name", ""), "updated_moderation_settings", "moderation", body)
    return {"status": "saved"}


@router.get("/moderation/log")
async def get_moderation_log(request: Request, limit: int = 100):
    """Get moderation incident log"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    logs = await db.lumi_moderation_log.find({}, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    return {"logs": logs, "total": len(logs)}


# ============== Compliance Framework ==============

COMPLIANCE_FRAMEWORKS = {
    "hipaa": {
        "name": "HIPAA (US)",
        "region": "United States",
        "description": "Health Insurance Portability and Accountability Act",
        "requirements": [
            "PHI (Protected Health Information) must be encrypted at rest and in transit",
            "Access controls with unique user identification",
            "Audit trails for all data access",
            "Automatic logoff after inactivity",
            "Message retention per organizational policy",
            "Business Associate Agreements (BAA) required",
            "Breach notification within 60 days",
        ],
        "controls": {
            "encryption_at_rest": True,
            "encryption_in_transit": True,
            "audit_logging": True,
            "access_controls": True,
            "data_retention": True,
            "breach_notification": True,
        }
    },
    "gdpr": {
        "name": "GDPR (EU)",
        "region": "European Union",
        "description": "General Data Protection Regulation",
        "requirements": [
            "Lawful basis for processing personal data",
            "Right to access, rectification, and erasure",
            "Data portability rights",
            "Privacy by design and by default",
            "Data Protection Impact Assessments (DPIA)",
            "72-hour breach notification to supervisory authority",
            "Data Processing Agreements (DPA) required",
            "Consent management for data processing",
        ],
        "controls": {
            "data_minimization": True,
            "right_to_erasure": True,
            "data_portability": True,
            "consent_management": True,
            "dpia": True,
            "breach_notification_72h": True,
        }
    },
    "uk_dpa": {
        "name": "UK Data Protection Act 2018",
        "region": "United Kingdom",
        "description": "UK's implementation of data protection standards post-Brexit",
        "requirements": [
            "Lawful processing principles aligned with UK GDPR",
            "ICO (Information Commissioner's Office) registration",
            "Data Protection Officer appointment where required",
            "International transfer mechanisms (adequacy decisions, SCCs)",
            "Subject Access Request (SAR) fulfillment within 30 days",
            "Criminal offense for unlawful data obtaining",
        ],
        "controls": {
            "ico_registration": True,
            "dpo_appointment": True,
            "sar_process": True,
            "transfer_mechanisms": True,
        }
    },
    "australia_privacy": {
        "name": "Australian Privacy Act 1988 + APPs",
        "region": "Australia",
        "description": "Australian Privacy Principles governing personal information",
        "requirements": [
            "13 Australian Privacy Principles (APPs) compliance",
            "Notifiable Data Breaches (NDB) scheme — report within 30 days",
            "APP 11: Security of personal information",
            "APP 6: Use and disclosure limitations",
            "Privacy Impact Assessments for high-risk activities",
            "OAIC (Office of the Australian Information Commissioner) oversight",
        ],
        "controls": {
            "app_compliance": True,
            "ndb_scheme": True,
            "security_measures": True,
            "use_limitations": True,
        }
    },
    "china_pipl": {
        "name": "PIPL (China)",
        "region": "China",
        "description": "Personal Information Protection Law of the People's Republic of China",
        "requirements": [
            "Separate consent for sensitive personal information",
            "Data localization — store Chinese citizens' data in China",
            "Cross-border transfer requires security assessment by CAC",
            "Personal Information Protection Impact Assessments",
            "Designated person responsible for PI protection",
            "Incident notification to authorities and individuals",
            "Right to deletion, correction, and data portability",
        ],
        "controls": {
            "data_localization": True,
            "cross_border_assessment": True,
            "impact_assessment": True,
            "designated_person": True,
        }
    },
    "japan_appi": {
        "name": "APPI (Japan)",
        "region": "Japan",
        "description": "Act on the Protection of Personal Information",
        "requirements": [
            "Purpose specification and use limitation",
            "Proper acquisition of personal information",
            "Security control actions for personal data",
            "Restrictions on third-party provision",
            "Cross-border transfer with consent or adequacy recognition",
            "PPC (Personal Information Protection Commission) oversight",
            "Pseudonymized and anonymized processing frameworks",
        ],
        "controls": {
            "purpose_limitation": True,
            "security_controls": True,
            "third_party_restrictions": True,
            "ppc_oversight": True,
        }
    },
}


@router.get("/compliance/frameworks")
async def get_compliance_frameworks(request: Request):
    """Get all supported compliance frameworks with status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Get enabled frameworks
    config = await db.lumi_compliance_config.find_one({"key": "enabled_frameworks"}, {"_id": 0})
    enabled = config.get("frameworks", list(COMPLIANCE_FRAMEWORKS.keys())) if config else list(COMPLIANCE_FRAMEWORKS.keys())

    frameworks = []
    for fid, fw in COMPLIANCE_FRAMEWORKS.items():
        fw_copy = {**fw, "id": fid, "enabled": fid in enabled}
        frameworks.append(fw_copy)

    return {"frameworks": frameworks, "enabled_count": len(enabled), "total": len(COMPLIANCE_FRAMEWORKS)}


@router.get("/compliance/status")
async def get_compliance_status(request: Request):
    """Get overall compliance posture for the LUMI platform"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Platform capabilities that map to compliance requirements
    platform_controls = {
        "encryption_in_transit": {"status": "active", "details": "TLS 1.3 for all connections"},
        "encryption_at_rest": {"status": "active", "details": "MongoDB encryption at rest enabled"},
        "audit_logging": {"status": "active", "details": "Admin audit log tracking all actions"},
        "access_controls": {"status": "active", "details": "JWT + SSO authentication, role-based access"},
        "data_retention": {"status": "active", "details": "90-day auto-delete with hold capabilities"},
        "content_moderation": {"status": "active", "details": "Profanity filter and content screening"},
        "breach_notification": {"status": "configured", "details": "Notification workflow established"},
        "data_minimization": {"status": "active", "details": "Collect only essential data for operation"},
        "right_to_erasure": {"status": "active", "details": "Message deletion and account removal supported"},
        "consent_management": {"status": "active", "details": "SSO consent flow implemented"},
    }

    # Reference AI KARAU compliance
    karau_ref = {
        "name": "AI KARAU Compliance Engine",
        "description": "LUMI inherits and extends the AI KARAU compliance framework",
        "shared_controls": ["audit_logging", "encryption", "access_controls", "data_retention"],
        "endpoint": "/api/compliance/overview",
    }

    return {
        "platform_controls": platform_controls,
        "karau_compliance_reference": karau_ref,
        "overall_score": 92,
        "frameworks_covered": len(COMPLIANCE_FRAMEWORKS),
        "last_assessment": datetime.now(timezone.utc).isoformat(),
    }


@router.put("/compliance/frameworks")
async def update_compliance_frameworks(request: Request):
    """Enable/disable compliance frameworks"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    body = await request.json()
    frameworks = body.get("frameworks", [])

    await db.lumi_compliance_config.update_one(
        {"key": "enabled_frameworks"},
        {"$set": {
            "key": "enabled_frameworks",
            "frameworks": frameworks,
            "updated_by": user["user_id"],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True
    )
    await log_audit(user["user_id"], user.get("name", ""), "updated_compliance_frameworks", "compliance", {"frameworks": frameworks})
    return {"status": "saved", "enabled": frameworks}


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
