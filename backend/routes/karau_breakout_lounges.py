"""
Virtual Breakout Lounges API
Interactive spaces where avatars move freely between conversation groups.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import math
import logging

from utils.database import db
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/karau/breakout", tags=["Breakout Lounges"])


class LoungeCreate(BaseModel):
    name: str
    topic: str = ""
    capacity: int = 10
    time_limit_minutes: int = 0  # 0 = unlimited
    position: dict = {"x": 0, "y": 0}  # position on the 2D map
    radius: float = 120  # pixel radius of the lounge zone


class AvatarMove(BaseModel):
    user_id: str
    user_name: str
    x: float
    y: float
    avatar_color: str = "#6366f1"


class LoungeUpdate(BaseModel):
    name: Optional[str] = None
    topic: Optional[str] = None
    capacity: Optional[int] = None
    time_limit_minutes: Optional[int] = None


PROXIMITY_THRESHOLD = 150  # pixels - within this range, users can hear each other


@router.post("/{meeting_id}/lounge")
async def create_lounge(meeting_id: str, data: LoungeCreate, user=Depends(require_auth)):
    """Create a new breakout lounge zone."""
    now = datetime.now(timezone.utc).isoformat()
    lounge_id = f"lounge-{int(datetime.now(timezone.utc).timestamp() * 1000) % 100000}"

    doc = {
        "meeting_id": meeting_id,
        "lounge_id": lounge_id,
        "name": data.name,
        "topic": data.topic,
        "capacity": data.capacity,
        "time_limit_minutes": data.time_limit_minutes,
        "position": data.position,
        "radius": data.radius,
        "created_by": user["user_id"],
        "created_at": now,
        "participants": [],
        "status": "active"
    }

    if data.time_limit_minutes > 0:
        from datetime import timedelta
        doc["expires_at"] = (datetime.now(timezone.utc) + timedelta(minutes=data.time_limit_minutes)).isoformat()

    await db.breakout_lounges.insert_one(doc)

    return {"success": True, "lounge_id": lounge_id, "name": data.name}


@router.get("/{meeting_id}/lounges")
async def list_lounges(meeting_id: str, user=Depends(require_auth)):
    """List all breakout lounges for a meeting."""
    lounges = await db.breakout_lounges.find(
        {"meeting_id": meeting_id, "status": "active"}, {"_id": 0}
    ).to_list(20)

    # Get all avatar positions
    avatars = await db.breakout_avatars.find(
        {"meeting_id": meeting_id}, {"_id": 0}
    ).to_list(100)

    # Calculate which avatars are in which lounges
    for lounge in lounges:
        lx, ly = lounge["position"]["x"], lounge["position"]["y"]
        r = lounge.get("radius", 120)
        in_lounge = []
        for av in avatars:
            dx = av["x"] - lx
            dy = av["y"] - ly
            if math.sqrt(dx*dx + dy*dy) <= r:
                in_lounge.append({"user_id": av["user_id"], "user_name": av["user_name"]})
        lounge["participants"] = in_lounge
        lounge["participant_count"] = len(in_lounge)

    return {"meeting_id": meeting_id, "lounges": lounges, "avatars": avatars}


@router.post("/{meeting_id}/move")
async def move_avatar(meeting_id: str, data: AvatarMove, user=Depends(require_auth)):
    """Update an avatar's position on the breakout map."""
    now = datetime.now(timezone.utc).isoformat()

    await db.breakout_avatars.update_one(
        {"meeting_id": meeting_id, "user_id": data.user_id},
        {"$set": {
            "meeting_id": meeting_id,
            "user_id": data.user_id,
            "user_name": data.user_name,
            "x": data.x, "y": data.y,
            "avatar_color": data.avatar_color,
            "updated_at": now
        }},
        upsert=True
    )

    # Calculate proximity to other users
    all_avatars = await db.breakout_avatars.find(
        {"meeting_id": meeting_id, "user_id": {"$ne": data.user_id}},
        {"_id": 0, "user_id": 1, "user_name": 1, "x": 1, "y": 1}
    ).to_list(100)

    nearby = []
    for av in all_avatars:
        dx = av["x"] - data.x
        dy = av["y"] - data.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist <= PROXIMITY_THRESHOLD:
            nearby.append({
                "user_id": av["user_id"],
                "user_name": av["user_name"],
                "distance": round(dist, 1),
                "audio_volume": round(max(0.1, 1.0 - dist / PROXIMITY_THRESHOLD), 2)
            })

    # Determine current lounge
    lounges = await db.breakout_lounges.find(
        {"meeting_id": meeting_id, "status": "active"},
        {"_id": 0, "lounge_id": 1, "name": 1, "position": 1, "radius": 1}
    ).to_list(20)

    current_lounge = None
    for l in lounges:
        dx = data.x - l["position"]["x"]
        dy = data.y - l["position"]["y"]
        if math.sqrt(dx*dx + dy*dy) <= l.get("radius", 120):
            current_lounge = {"lounge_id": l["lounge_id"], "name": l["name"]}
            break

    return {
        "success": True,
        "position": {"x": data.x, "y": data.y},
        "nearby_users": nearby,
        "current_lounge": current_lounge,
        "audio_connections": len(nearby)
    }


@router.put("/{meeting_id}/lounge/{lounge_id}")
async def update_lounge(meeting_id: str, lounge_id: str, data: LoungeUpdate, user=Depends(require_auth)):
    """Update a breakout lounge settings."""
    update = {}
    if data.name is not None: update["name"] = data.name
    if data.topic is not None: update["topic"] = data.topic
    if data.capacity is not None: update["capacity"] = data.capacity
    if data.time_limit_minutes is not None: update["time_limit_minutes"] = data.time_limit_minutes

    if not update:
        raise HTTPException(400, "No fields to update")

    result = await db.breakout_lounges.update_one(
        {"meeting_id": meeting_id, "lounge_id": lounge_id},
        {"$set": update}
    )

    return {"success": result.modified_count > 0, "lounge_id": lounge_id}


@router.delete("/{meeting_id}/lounge/{lounge_id}")
async def delete_lounge(meeting_id: str, lounge_id: str, user=Depends(require_auth)):
    """Delete a breakout lounge."""
    await db.breakout_lounges.update_one(
        {"meeting_id": meeting_id, "lounge_id": lounge_id},
        {"$set": {"status": "closed"}}
    )
    return {"success": True, "closed": lounge_id}


@router.get("/{meeting_id}/proximity/{user_id}")
async def get_proximity(meeting_id: str, user_id: str, user=Depends(require_auth)):
    """Get proximity data for a specific user."""
    me = await db.breakout_avatars.find_one(
        {"meeting_id": meeting_id, "user_id": user_id}, {"_id": 0}
    )
    if not me:
        return {"user_id": user_id, "nearby": [], "current_lounge": None}

    all_avatars = await db.breakout_avatars.find(
        {"meeting_id": meeting_id, "user_id": {"$ne": user_id}}, {"_id": 0}
    ).to_list(100)

    nearby = []
    for av in all_avatars:
        dx = av["x"] - me["x"]
        dy = av["y"] - me["y"]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist <= PROXIMITY_THRESHOLD:
            nearby.append({
                "user_id": av["user_id"], "user_name": av["user_name"],
                "distance": round(dist, 1),
                "audio_volume": round(max(0.1, 1.0 - dist / PROXIMITY_THRESHOLD), 2)
            })

    return {"user_id": user_id, "position": {"x": me["x"], "y": me["y"]}, "nearby": nearby}
