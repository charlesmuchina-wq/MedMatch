"""
ENZI Cross-Portal Integration
- Trigger AI KARAU meetings from ENZI chat
- Shared session across portals
- Meeting Bot that auto-creates meetings from meeting request messages
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, timezone, timedelta
import uuid
import logging

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi/meetings", tags=["ENZI Cross-Portal"])
logger = logging.getLogger(__name__)


class QuickMeetingRequest(BaseModel):
    title: Optional[str] = "ENZI Quick Meeting"
    channel_id: Optional[str] = None
    participants: Optional[list] = []


class ScheduleMeetingRequest(BaseModel):
    title: str
    scheduled_at: str  # ISO format
    channel_id: Optional[str] = None
    participants: Optional[list] = []
    description: Optional[str] = ""


@router.post("/quick")
async def create_quick_meeting(req: QuickMeetingRequest, request: Request):
    """Create an instant meeting from ENZI and get AI KARAU meeting link"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    meeting_id = str(uuid.uuid4())[:12]
    now = datetime.now(timezone.utc).isoformat()

    meeting = {
        "id": meeting_id,
        "title": req.title,
        "host_id": user.get("user_id"),
        "host_name": user.get("name", user.get("email", "Host")),
        "status": "waiting",
        "source": "enzi",
        "channel_id": req.channel_id,
        "participants": req.participants,
        "settings": {"type": "instant"},
        "created_at": now
    }
    await db.meetings.insert_one(meeting)

    # Post notification message to channel if specified
    if req.channel_id:
        await db.lumi_messages.insert_one({
            "id": str(uuid.uuid4()),
            "channel_id": req.channel_id,
            "content": f"**Meeting Started:** [{req.title}](/karau-meet/meeting/{meeting_id})\nJoin now to collaborate in real-time.",
            "sender_id": "system",
            "sender_name": "ENZI Meeting Bot",
            "type": "meeting",
            "meeting_id": meeting_id,
            "created_at": now
        })

    del meeting["_id"]
    return {
        "meeting_id": meeting_id,
        "title": req.title,
        "join_url": f"/karau-meet/meeting/{meeting_id}",
        "status": "waiting"
    }


@router.post("/schedule")
async def schedule_meeting(req: ScheduleMeetingRequest, request: Request):
    """Schedule a meeting from ENZI"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    meeting_id = str(uuid.uuid4())[:12]
    now = datetime.now(timezone.utc).isoformat()

    meeting = {
        "id": meeting_id,
        "title": req.title,
        "description": req.description,
        "host_id": user.get("user_id"),
        "host_name": user.get("name", user.get("email", "Host")),
        "status": "scheduled",
        "source": "enzi",
        "channel_id": req.channel_id,
        "participants": req.participants,
        "scheduled_time": req.scheduled_at,
        "settings": {"type": "scheduled"},
        "created_at": now
    }
    await db.meetings.insert_one(meeting)

    if req.channel_id:
        sched_time = req.scheduled_at[:16].replace('T', ' at ')
        await db.lumi_messages.insert_one({
            "id": str(uuid.uuid4()),
            "channel_id": req.channel_id,
            "content": f"**Meeting Scheduled:** {req.title}\nTime: {sched_time}\n[Join when it starts](/karau-meet/meeting/{meeting_id})",
            "sender_id": "system",
            "sender_name": "ENZI Meeting Bot",
            "type": "meeting",
            "meeting_id": meeting_id,
            "created_at": now
        })

    del meeting["_id"]
    return {
        "meeting_id": meeting_id,
        "title": req.title,
        "join_url": f"/karau-meet/meeting/{meeting_id}",
        "scheduled_at": req.scheduled_at,
        "status": "scheduled"
    }


@router.get("/active")
async def get_active_meetings(request: Request):
    """Get active/upcoming meetings for the user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    uid = user.get("user_id")
    meetings = await db.meetings.find(
        {"$or": [{"host_id": uid}, {"participants": uid}], "status": {"$in": ["waiting", "active", "scheduled"]}},
        {"_id": 0}
    ).sort("created_at", -1).limit(10).to_list(10)

    return {"meetings": meetings, "count": len(meetings)}
