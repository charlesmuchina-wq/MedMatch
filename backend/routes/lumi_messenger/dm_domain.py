# Auto-split route group: dm_domain

from fastapi import APIRouter

from ._common import *  # noqa: F401,F403



router = APIRouter()



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
