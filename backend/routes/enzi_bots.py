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



class ToggleBotRequest(BaseModel):
    is_active: bool


@router.put("/toggle/{install_id}")
async def toggle_bot(install_id: str, req: ToggleBotRequest, request: Request):
    """Toggle a bot active/paused"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.enzi_installed_bots.update_one(
        {"id": install_id, "installed_by": user.get("user_id")},
        {"$set": {"is_active": req.is_active}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Installation not found")

    return {"status": "active" if req.is_active else "paused"}


class ConfigureBotRequest(BaseModel):
    config: dict


@router.put("/configure/{install_id}")
async def configure_bot(install_id: str, req: ConfigureBotRequest, request: Request):
    """Update bot configuration"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.enzi_installed_bots.update_one(
        {"id": install_id, "installed_by": user.get("user_id")},
        {"$set": {"config": req.config}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Installation not found")

    return {"status": "configured", "config": req.config}



class BotActionRequest(BaseModel):
    bot_id: str
    channel_id: str
    action: str  # e.g. "start_poll", "set_reminder", "run_standup"
    params: Optional[dict] = None


BOT_ACTIONS = {
    "standup": {
        "actions": [
            {"id": "run_standup", "label": "Run Standup", "icon": "clipboard"},
        ],
        "handler": lambda p: "**Daily Standup**\nPlease share your update:\n- What did you do yesterday?\n- What will you do today?\n- Any blockers?"
    },
    "reminder": {
        "actions": [
            {"id": "set_reminder", "label": "Set Reminder", "icon": "bell"},
        ],
        "handler": lambda p: f"**Reminder Set:** {p.get('text', 'Check back later!')} at {p.get('time', 'in 15 minutes')}"
    },
    "poll": {
        "actions": [
            {"id": "start_poll", "label": "Start Poll", "icon": "bar-chart"},
        ],
        "handler": lambda p: f"**Poll:** {p.get('question', 'What do you think?')}\n{chr(10).join(f'- {opt}' for opt in p.get('options', ['Option A', 'Option B', 'Option C']))}\n\n_React to vote!_"
    },
    "meeting": {
        "actions": [
            {"id": "start_meeting", "label": "Quick Meeting", "icon": "video"},
        ],
        "handler": lambda p: "**Meeting Starting Now**\nJoin the AI KARAU meeting to collaborate in real-time."
    },
    "welcome": {
        "actions": [
            {"id": "send_welcome", "label": "Welcome Message", "icon": "hand-wave"},
        ],
        "handler": lambda p: "**Welcome to the team!** Here's how to get started:\n1. Introduce yourself in this channel\n2. Check out pinned messages\n3. Set your status and profile"
    },
    "summary": {
        "actions": [
            {"id": "run_summary", "label": "Summarize Now", "icon": "brain"},
        ],
        "handler": lambda p: "**Channel Summary**\nGenerating summary of recent conversations..."
    },
    "translator": {
        "actions": [
            {"id": "translate", "label": "Translate", "icon": "globe"},
        ],
        "handler": lambda p: f"**Translation Bot Active**\nAuto-translating messages to {p.get('language', 'English')}."
    },
    "github_notify": {
        "actions": [
            {"id": "check_status", "label": "Check Repos", "icon": "github"},
        ],
        "handler": lambda p: "**GitHub Status**\nMonitoring repositories for push, PR, and issue events."
    },
}


@router.post("/action")
async def execute_bot_action(req: BotActionRequest, request: Request):
    """Execute a bot action in a channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Verify bot is installed in this channel
    installed = await db.enzi_installed_bots.find_one(
        {"bot_id": req.bot_id, "channel_id": req.channel_id, "is_active": True}
    )
    if not installed:
        raise HTTPException(status_code=404, detail="Bot not installed in this channel")

    bot_def = BOT_ACTIONS.get(req.bot_id)
    if not bot_def:
        raise HTTPException(status_code=404, detail="Bot actions not defined")

    # Generate bot response message
    content = bot_def["handler"](req.params or {})

    msg_id = str(uuid.uuid4())
    bot_info = BOT_CATALOG.get(req.bot_id, {})
    await db.lumi_messages.insert_one({
        "id": msg_id,
        "channel_id": req.channel_id,
        "content": content,
        "sender_id": f"bot_{req.bot_id}",
        "sender_name": f"[Bot] {bot_info.get('name', req.bot_id)}",
        "type": "bot_action",
        "bot_id": req.bot_id,
        "action": req.action,
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {"message_id": msg_id, "content": content, "bot_name": bot_info.get("name", req.bot_id)}


@router.get("/channel/{channel_id}")
async def get_channel_bots(channel_id: str, request: Request):
    """Get installed bots for a specific channel with available actions"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    bots = await db.enzi_installed_bots.find(
        {"channel_id": channel_id, "is_active": True},
        {"_id": 0}
    ).to_list(20)

    result = []
    for b in bots:
        bot_actions = BOT_ACTIONS.get(b["bot_id"], {})
        cat_info = BOT_CATALOG.get(b["bot_id"], {})
        result.append({
            "id": b["id"],
            "bot_id": b["bot_id"],
            "bot_name": b["bot_name"],
            "icon": cat_info.get("icon", "brain"),
            "actions": bot_actions.get("actions", []),
            "config": b.get("config", {})
        })

    return {"bots": result, "count": len(result)}
