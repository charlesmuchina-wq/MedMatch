"""
LUMI Predictive Navigation - Track user behavior and predict next actions
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone, timedelta
import os

from motor.motor_asyncio import AsyncIOMotorClient
from routes.auth import get_current_user

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "medmatch")
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

router = APIRouter(prefix="/lumi/predict", tags=["LUMI Predictive Navigation"])


@router.post("/track")
async def track_action(request: Request):
    """Track a user action for behavioral modeling"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    body = await request.json()
    action_type = body.get("action", "")  # channel_visit, dm_visit, search, command
    target_id = body.get("target_id", "")
    target_name = body.get("target_name", "")

    if not action_type:
        raise HTTPException(status_code=400, detail="action required")

    now = datetime.now(timezone.utc)
    doc = {
        "user_id": user["user_id"],
        "action": action_type,
        "target_id": target_id,
        "target_name": target_name,
        "hour": now.hour,
        "day_of_week": now.weekday(),
        "created_at": now.isoformat(),
    }
    await db.lumi_user_actions.insert_one(doc)

    # Update frequency counters
    await db.lumi_action_freq.update_one(
        {"user_id": user["user_id"], "action": action_type, "target_id": target_id},
        {"$inc": {"count": 1}, "$set": {"target_name": target_name, "last_at": now.isoformat()}},
        upsert=True,
    )

    return {"tracked": True}


@router.get("/suggestions")
async def get_suggestions(request: Request):
    """Get personalized navigation suggestions based on user behavior"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    now = datetime.now(timezone.utc)
    current_hour = now.hour
    current_dow = now.weekday()

    # Get most frequent actions overall
    freq = await db.lumi_action_freq.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("count", -1).to_list(30)

    # Get time-based patterns (actions at this hour +/- 1)
    hour_range = [(current_hour - 1) % 24, current_hour, (current_hour + 1) % 24]
    time_actions = await db.lumi_user_actions.find(
        {"user_id": user["user_id"], "hour": {"$in": hour_range}},
        {"_id": 0, "target_id": 1, "target_name": 1, "action": 1}
    ).sort("created_at", -1).to_list(50)

    # Score each target: frequency weight + time relevance weight
    scores = {}
    for f in freq:
        key = f"{f['action']}:{f['target_id']}"
        scores[key] = {
            "action": f["action"],
            "target_id": f["target_id"],
            "target_name": f.get("target_name", ""),
            "score": f["count"] * 1.0,
            "last_at": f.get("last_at", ""),
        }

    # Boost score for time-matching actions
    for ta in time_actions:
        key = f"{ta['action']}:{ta['target_id']}"
        if key in scores:
            scores[key]["score"] += 2.0  # Time bonus
        else:
            scores[key] = {
                "action": ta["action"],
                "target_id": ta["target_id"],
                "target_name": ta.get("target_name", ""),
                "score": 2.0,
                "last_at": "",
            }

    # Sort by score, take top suggestions
    sorted_suggestions = sorted(scores.values(), key=lambda x: x["score"], reverse=True)

    # Separate by type
    channel_suggestions = [s for s in sorted_suggestions if s["action"] == "channel_visit"][:5]
    dm_suggestions = [s for s in sorted_suggestions if s["action"] == "dm_visit"][:5]

    return {
        "channels": channel_suggestions,
        "dms": dm_suggestions,
        "time_context": {"hour": current_hour, "day": current_dow},
    }


@router.get("/stats")
async def get_behavior_stats(request: Request):
    """Get user behavior statistics"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Total actions
    total = await db.lumi_user_actions.count_documents({"user_id": user["user_id"]})

    # Actions by type
    pipeline = [
        {"$match": {"user_id": user["user_id"]}},
        {"$group": {"_id": "$action", "count": {"$sum": 1}}},
    ]
    by_type = {}
    async for doc in db.lumi_user_actions.aggregate(pipeline):
        by_type[doc["_id"]] = doc["count"]

    # Peak hours
    hour_pipeline = [
        {"$match": {"user_id": user["user_id"]}},
        {"$group": {"_id": "$hour", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 3},
    ]
    peak_hours = []
    async for doc in db.lumi_user_actions.aggregate(hour_pipeline):
        peak_hours.append({"hour": doc["_id"], "count": doc["count"]})

    return {
        "total_actions": total,
        "by_type": by_type,
        "peak_hours": peak_hours,
    }
