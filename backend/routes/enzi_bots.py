"""
ENZI Bot Store
- Pre-built bots: Standup, Reminder, Poll, Meeting, Welcome
- Browse, install, configure bots per channel
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi/bots", tags=["ENZI Bot Store"])

BOT_CATALOG = {
    "standup": {
        "name": "Standup Bot",
        "description": "Automated daily standup prompts. Posts at a set time asking team members: Done / Doing / Blocked.",
        "icon": "clipboard",
        "category": "Productivity",
        "default_config": {"schedule": "09:00", "timezone": "UTC", "prompt": "Share your standup: Done / Doing / Blocked"}
    },
    "reminder": {
        "name": "Reminder Bot",
        "description": "Set reminders for yourself or the channel. Never miss a deadline.",
        "icon": "bell",
        "category": "Productivity",
        "default_config": {"default_snooze": 15}
    },
    "poll": {
        "name": "Poll Bot",
        "description": "Create quick polls in any channel. Supports multiple choice and anonymous voting.",
        "icon": "bar-chart",
        "category": "Engagement",
        "default_config": {"allow_anonymous": True, "max_options": 10}
    },
    "meeting": {
        "name": "Meeting Bot",
        "description": "Auto-detect meeting requests in chat and create AI KARAU meetings. Syncs with calendar.",
        "icon": "video",
        "category": "Collaboration",
        "default_config": {"auto_detect": True, "default_duration": 30}
    },
    "welcome": {
        "name": "Welcome Bot",
        "description": "Greet new members with a custom welcome message and onboarding checklist.",
        "icon": "hand-wave",
        "category": "Onboarding",
        "default_config": {"message": "Welcome to the team! Here's how to get started:", "show_checklist": True}
    },
    "summary": {
        "name": "Summary Bot",
        "description": "Auto-summarize long conversations daily. Never miss important updates.",
        "icon": "brain",
        "category": "AI",
        "default_config": {"frequency": "daily", "time": "18:00"}
    },
    "translator": {
        "name": "Translator Bot",
        "description": "Auto-translate messages in multilingual channels. Supports 50+ languages.",
        "icon": "globe",
        "category": "Communication",
        "default_config": {"target_language": "en", "auto_translate": False}
    },
    "github_notify": {
        "name": "GitHub Notify Bot",
        "description": "Get real-time notifications for commits, PRs, and issues from your repositories.",
        "icon": "github",
        "category": "DevOps",
        "default_config": {"events": ["push", "pull_request", "issues"]}
    }
}


@router.get("/catalog")
async def get_bot_catalog():
    """Browse available bots"""
    return {
        "bots": [
            {"id": k, "name": v["name"], "description": v["description"], "icon": v["icon"], "category": v["category"]}
            for k, v in BOT_CATALOG.items()
        ],
        "categories": list(set(v["category"] for v in BOT_CATALOG.values()))
    }


class InstallBotRequest(BaseModel):
    bot_id: str
    channel_id: str
    config: Optional[dict] = None


@router.post("/install")
async def install_bot(req: InstallBotRequest, request: Request):
    """Install a bot in a channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    bot = BOT_CATALOG.get(req.bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Check if already installed
    existing = await db.enzi_installed_bots.find_one(
        {"bot_id": req.bot_id, "channel_id": req.channel_id}
    )
    if existing:
        raise HTTPException(status_code=400, detail="Bot already installed in this channel")

    install_id = str(uuid.uuid4())
    config = {**bot["default_config"], **(req.config or {})}

    await db.enzi_installed_bots.insert_one({
        "id": install_id,
        "bot_id": req.bot_id,
        "bot_name": bot["name"],
        "channel_id": req.channel_id,
        "config": config,
        "installed_by": user.get("user_id"),
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    # Post welcome message
    await db.lumi_messages.insert_one({
        "id": str(uuid.uuid4()),
        "channel_id": req.channel_id,
        "content": f"**{bot['name']}** has been installed in this channel. {bot['description']}",
        "sender_id": f"bot_{req.bot_id}",
        "sender_name": f"[Bot] {bot['name']}",
        "type": "system",
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {"id": install_id, "bot_id": req.bot_id, "bot_name": bot["name"], "config": config, "status": "installed"}


@router.get("/installed")
async def get_installed_bots(request: Request, channel_id: Optional[str] = None):
    """Get installed bots"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    query = {"installed_by": user.get("user_id")}
    if channel_id:
        query["channel_id"] = channel_id

    bots = await db.enzi_installed_bots.find(query, {"_id": 0}).to_list(50)
    return {"bots": bots, "count": len(bots)}


@router.delete("/uninstall/{install_id}")
async def uninstall_bot(install_id: str, request: Request):
    """Uninstall a bot"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.enzi_installed_bots.delete_one({"id": install_id, "installed_by": user.get("user_id")})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Installation not found")

    return {"status": "uninstalled"}
