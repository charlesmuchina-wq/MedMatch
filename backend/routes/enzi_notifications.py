"""
ENZI Notification Preferences
- Per-channel mute/unmute
- DND (Do Not Disturb) schedule
- Keyword alerts
- Notification level per channel
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi/notifications", tags=["ENZI Notifications"])


class ChannelNotifPref(BaseModel):
    channel_id: str
    level: str = "all"  # all, mentions, none


class DNDSchedule(BaseModel):
    enabled: bool
    start_time: Optional[str] = "22:00"  # HH:MM
    end_time: Optional[str] = "08:00"
    timezone: Optional[str] = "UTC"


class KeywordAlert(BaseModel):
    keyword: str


@router.get("/preferences")
async def get_notification_preferences(request: Request):
    """Get notification preferences for the current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    prefs = await db.enzi_notification_prefs.find_one(
        {"user_id": user.get("user_id")}, {"_id": 0}
    )
    if not prefs:
        prefs = {
            "user_id": user.get("user_id"),
            "channel_prefs": {},
            "dnd": {"enabled": False, "start_time": "22:00", "end_time": "08:00", "timezone": "UTC"},
            "keyword_alerts": [],
            "global_level": "all"
        }

    return prefs


@router.put("/channel")
async def set_channel_notification(req: ChannelNotifPref, request: Request):
    """Set notification level for a specific channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if req.level not in ("all", "mentions", "none"):
        raise HTTPException(status_code=400, detail="Invalid level. Use: all, mentions, none")

    await db.enzi_notification_prefs.update_one(
        {"user_id": user.get("user_id")},
        {"$set": {f"channel_prefs.{req.channel_id}": req.level}},
        upsert=True
    )

    return {"status": "updated", "channel_id": req.channel_id, "level": req.level}


@router.put("/dnd")
async def set_dnd_schedule(req: DNDSchedule, request: Request):
    """Set Do Not Disturb schedule"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    await db.enzi_notification_prefs.update_one(
        {"user_id": user.get("user_id")},
        {"$set": {"dnd": req.dict()}},
        upsert=True
    )

    return {"status": "updated", "dnd": req.dict()}


@router.post("/keywords")
async def add_keyword_alert(req: KeywordAlert, request: Request):
    """Add a keyword to alert on"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    await db.enzi_notification_prefs.update_one(
        {"user_id": user.get("user_id")},
        {"$addToSet": {"keyword_alerts": req.keyword.lower()}},
        upsert=True
    )

    return {"status": "added", "keyword": req.keyword}


@router.delete("/keywords/{keyword}")
async def remove_keyword_alert(keyword: str, request: Request):
    """Remove a keyword alert"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    await db.enzi_notification_prefs.update_one(
        {"user_id": user.get("user_id")},
        {"$pull": {"keyword_alerts": keyword.lower()}}
    )

    return {"status": "removed", "keyword": keyword}
