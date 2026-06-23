# Auto-split route group: voice

from fastapi import APIRouter

from ._common import *  # noqa: F401,F403



router = APIRouter()



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
