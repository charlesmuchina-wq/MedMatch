"""
ENZI Channel Templates
- Pre-built channel structures: Project, Sprint, Incident, Standup
- Auto-create channels with default description and pinned messages
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi/templates/channels", tags=["ENZI Channel Templates"])

CHANNEL_TEMPLATES = {
    "project": {
        "name_suffix": "Project",
        "description": "Project coordination channel — tasks, updates, and deliverables",
        "channel_type": "project",
        "pinned_messages": [
            "Welcome to the project channel! Use this space for task updates, blockers, and decisions.",
            "Pin important links, docs, and deadlines here for quick reference."
        ]
    },
    "sprint": {
        "name_suffix": "Sprint",
        "description": "Sprint planning, daily standups, and retrospectives",
        "channel_type": "team",
        "pinned_messages": [
            "Sprint Goals: [Define sprint goals here]",
            "Daily Standup Format: 1) What I did yesterday 2) What I'm doing today 3) Any blockers"
        ]
    },
    "incident": {
        "name_suffix": "Incident",
        "description": "Incident response — status updates, resolution tracking, and post-mortem",
        "channel_type": "announcement",
        "pinned_messages": [
            "INCIDENT TEMPLATE:\n- Severity: P1/P2/P3\n- Impact: [Describe impact]\n- Status: Investigating / Identified / Monitoring / Resolved\n- Owner: [Assign]\n- ETA: [Time estimate]",
            "Post-Incident Review: What happened? What was the root cause? What can we improve?"
        ]
    },
    "standup": {
        "name_suffix": "Standup",
        "description": "Async daily standups — share your updates here",
        "channel_type": "team",
        "pinned_messages": [
            "Post your daily update: Done / Doing / Blocked",
            "Keep it concise — 2-3 bullet points max!"
        ]
    },
    "general": {
        "name_suffix": "General",
        "description": "General discussion and announcements",
        "channel_type": "public",
        "pinned_messages": [
            "Welcome! This is the general discussion channel."
        ]
    }
}


@router.get("/list")
async def list_channel_templates():
    """List available channel templates"""
    return {
        "templates": [
            {"id": k, "name": v["name_suffix"], "description": v["description"], "type": v["channel_type"]}
            for k, v in CHANNEL_TEMPLATES.items()
        ]
    }


class CreateFromTemplate(BaseModel):
    template_id: str
    name_prefix: str  # e.g., "Q1" → "Q1-Sprint"


@router.post("/create")
async def create_from_template(req: CreateFromTemplate, request: Request):
    """Create a new channel from a template"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    template = CHANNEL_TEMPLATES.get(req.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    channel_id = str(uuid.uuid4())
    channel_name = f"{req.name_prefix}-{template['name_suffix']}"
    now = datetime.now(timezone.utc).isoformat()

    channel = {
        "id": channel_id,
        "name": channel_name,
        "description": template["description"],
        "channel_type": template["channel_type"],
        "created_by": user.get("user_id"),
        "members": [user.get("user_id")],
        "is_private": False,
        "template_id": req.template_id,
        "created_at": now
    }
    await db.lumi_channels.insert_one(channel)

    # Add pinned messages
    for i, msg_content in enumerate(template.get("pinned_messages", [])):
        msg_id = str(uuid.uuid4())
        await db.lumi_messages.insert_one({
            "id": msg_id,
            "channel_id": channel_id,
            "content": msg_content,
            "sender_id": "system",
            "sender_name": "ENZI Bot",
            "type": "system",
            "is_pinned": True,
            "created_at": now
        })

    del channel["_id"]
    return channel
