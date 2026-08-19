# Auto-split route group: core

from fastapi import APIRouter

from ._common import *  # noqa: F401,F403



router = APIRouter()



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

    # ENZI AI DM: process "done" replies against reminded tasks
    if "enzi_ai" in (channel.get("dm_key") or ""):
        try:
            import asyncio as _asyncio
            from services.task_reminder_service import handle_ai_dm_reply
            _asyncio.create_task(handle_ai_dm_reply(dict(user), content))
        except Exception:
            pass

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
