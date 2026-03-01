"""
Ghost Booking Prevention API
Detect idle meetings, auto-release unused rooms, and manage activity tracking.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import logging

from utils.database import db
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/karau-meet/ghost", tags=["Ghost Booking Prevention"])

DEFAULT_IDLE_TIMEOUT_MINUTES = 10


class ActivityPing(BaseModel):
    meeting_id: str
    activity_type: str = "presence"  # presence, audio, video, interaction


class GhostSettings(BaseModel):
    idle_timeout_minutes: int = 10
    auto_release: bool = True
    notify_before_release_minutes: int = 2


@router.post("/ping")
async def activity_ping(data: ActivityPing, user=Depends(require_auth)):
    """Record activity for a meeting to prevent ghost booking detection."""
    await db.meeting_activity.update_one(
        {"meeting_id": data.meeting_id, "user_id": user["user_id"]},
        {"$set": {
            "meeting_id": data.meeting_id,
            "user_id": user["user_id"],
            "user_name": user.get("name", "User"),
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "activity_type": data.activity_type
        }},
        upsert=True
    )
    return {"success": True, "pinged": data.meeting_id}


@router.get("/check/{meeting_id}")
async def check_ghost_status(meeting_id: str, user=Depends(require_auth)):
    """Check if a meeting is idle (no activity within timeout window)."""
    # Get ghost settings for this meeting
    settings = await db.ghost_settings.find_one(
        {"meeting_id": meeting_id}, {"_id": 0}
    )
    timeout_minutes = settings.get("idle_timeout_minutes", DEFAULT_IDLE_TIMEOUT_MINUTES) if settings else DEFAULT_IDLE_TIMEOUT_MINUTES
    auto_release = settings.get("auto_release", True) if settings else True

    # Get latest activity across all users
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)).isoformat()

    active_users = await db.meeting_activity.find(
        {"meeting_id": meeting_id, "last_activity": {"$gte": cutoff}},
        {"_id": 0, "user_id": 1, "user_name": 1, "last_activity": 1, "activity_type": 1}
    ).to_list(100)

    is_idle = len(active_users) == 0
    idle_since = None

    if is_idle:
        # Find last activity timestamp
        last = await db.meeting_activity.find_one(
            {"meeting_id": meeting_id},
            {"_id": 0, "last_activity": 1},
            sort=[("last_activity", -1)]
        )
        idle_since = last.get("last_activity") if last else None

    # Check warning threshold
    warn_cutoff = (datetime.now(timezone.utc) - timedelta(minutes=max(0, timeout_minutes - 2))).isoformat()
    warn_users = await db.meeting_activity.find(
        {"meeting_id": meeting_id, "last_activity": {"$gte": warn_cutoff}},
        {"_id": 0}
    ).to_list(1)
    approaching_idle = len(warn_users) == 0 and not is_idle

    return {
        "meeting_id": meeting_id,
        "is_idle": is_idle,
        "approaching_idle": approaching_idle,
        "idle_since": idle_since,
        "active_users": len(active_users),
        "timeout_minutes": timeout_minutes,
        "auto_release": auto_release,
        "active_user_list": active_users[:5]
    }


@router.post("/release/{meeting_id}")
async def release_meeting(meeting_id: str, user=Depends(require_auth)):
    """Release an idle meeting room (set status to released)."""
    # Mark meeting as ghost-released
    result = await db.karau_meetings.update_one(
        {"meeting_id": meeting_id},
        {"$set": {
            "status": "ghost_released",
            "ghost_released_at": datetime.now(timezone.utc).isoformat(),
            "released_by": user["user_id"]
        }}
    )

    # Also check webinars
    if result.modified_count == 0:
        await db.webinars.update_one(
            {"webinar_id": meeting_id},
            {"$set": {
                "ghost_released": True,
                "ghost_released_at": datetime.now(timezone.utc).isoformat()
            }}
        )

    # Clean up activity records
    await db.meeting_activity.delete_many({"meeting_id": meeting_id})

    return {"success": True, "meeting_id": meeting_id, "status": "released"}


@router.post("/settings/{meeting_id}")
async def update_ghost_settings(meeting_id: str, data: GhostSettings, user=Depends(require_auth)):
    """Update ghost booking prevention settings for a meeting."""
    await db.ghost_settings.update_one(
        {"meeting_id": meeting_id},
        {"$set": {
            "meeting_id": meeting_id,
            "idle_timeout_minutes": data.idle_timeout_minutes,
            "auto_release": data.auto_release,
            "notify_before_release_minutes": data.notify_before_release_minutes,
            "updated_by": user["user_id"],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    return {"success": True, "settings": data.dict()}


@router.post("/keep/{meeting_id}")
async def keep_meeting_alive(meeting_id: str, user=Depends(require_auth)):
    """Explicitly keep a meeting alive (dismiss ghost warning)."""
    await db.meeting_activity.update_one(
        {"meeting_id": meeting_id, "user_id": user["user_id"]},
        {"$set": {
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "activity_type": "manual_keep_alive"
        }},
        upsert=True
    )
    return {"success": True, "kept_alive": meeting_id}
