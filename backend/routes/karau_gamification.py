"""
Gamification API - Leaderboard, Emoji Reactions, Participation Tracking
Real-time engagement features for AI KARAU webinars.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/karau/webinar", tags=["Gamification"])

VALID_REACTIONS = ["thumbsup", "clap", "heart", "laugh", "fire", "mindblown", "wave", "100"]
REACTION_EMOJIS = {
    "thumbsup": "\U0001f44d", "clap": "\U0001f44f", "heart": "\u2764\ufe0f", "laugh": "\U0001f602",
    "fire": "\U0001f525", "mindblown": "\U0001f92f", "wave": "\U0001f44b", "100": "\U0001f4af"
}


class ReactionRequest(BaseModel):
    reaction: str
    sender_name: Optional[str] = ""


class LeaderboardAction(BaseModel):
    action: str  # question, reaction, speaking, chat
    value: int = 1


@router.post("/{webinar_id}/reaction")
async def send_reaction(webinar_id: str, data: ReactionRequest, user=Depends(get_current_user)):
    """Send a floating emoji reaction in the webinar."""
    if data.reaction not in VALID_REACTIONS:
        raise HTTPException(400, f"Invalid reaction. Valid: {VALID_REACTIONS}")

    reaction = {
        "reaction_id": f"R-{uuid.uuid4().hex[:8]}",
        "reaction": data.reaction,
        "emoji": REACTION_EMOJIS.get(data.reaction, data.reaction),
        "sender_id": user["user_id"],
        "sender_name": data.sender_name or user.get("name", "User"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # Store reaction and update leaderboard
    await db.webinar_reactions.insert_one({
        **reaction,
        "webinar_id": webinar_id
    })

    # Increment reaction count in leaderboard
    await db.webinar_leaderboard.update_one(
        {"webinar_id": webinar_id, "user_id": user["user_id"]},
        {
            "$inc": {"reactions": 1, "total_score": 2},
            "$set": {"user_name": data.sender_name or user.get("name", "User"), "updated_at": datetime.now(timezone.utc).isoformat()},
            "$setOnInsert": {"questions": 0, "speaking_time": 0, "chat_messages": 0, "created_at": datetime.now(timezone.utc).isoformat()}
        },
        upsert=True
    )

    return {
        "success": True,
        "reaction_id": reaction["reaction_id"],
        "emoji": reaction["emoji"],
        "sender_name": reaction["sender_name"]
    }


@router.get("/{webinar_id}/reactions/recent")
async def get_recent_reactions(webinar_id: str, limit: int = 20):
    """Get recent emoji reactions for floating display."""
    reactions = await db.webinar_reactions.find(
        {"webinar_id": webinar_id},
        {"_id": 0, "reaction_id": 1, "reaction": 1, "emoji": 1, "sender_name": 1, "created_at": 1}
    ).sort("created_at", -1).to_list(length=limit)

    return {"reactions": reactions}


@router.get("/{webinar_id}/leaderboard")
async def get_leaderboard(webinar_id: str, limit: int = 10):
    """Get the participation leaderboard for a webinar."""
    entries = await db.webinar_leaderboard.find(
        {"webinar_id": webinar_id},
        {"_id": 0, "user_id": 1, "user_name": 1, "reactions": 1, "questions": 1,
         "speaking_time": 1, "chat_messages": 1, "total_score": 1}
    ).sort("total_score", -1).to_list(length=limit)

    # Add rank
    for i, entry in enumerate(entries):
        entry["rank"] = i + 1

    return {"leaderboard": entries, "total_participants": len(entries)}


@router.post("/{webinar_id}/leaderboard/track")
async def track_participation(webinar_id: str, data: LeaderboardAction, user=Depends(get_current_user)):
    """Track a participation action for the leaderboard."""
    score_map = {"question": 5, "reaction": 2, "speaking": 1, "chat": 1}
    score = score_map.get(data.action, 1) * data.value
    field = {
        "question": "questions",
        "reaction": "reactions",
        "speaking": "speaking_time",
        "chat": "chat_messages"
    }.get(data.action, "reactions")

    # Ensure document exists first
    exists = await db.webinar_leaderboard.find_one(
        {"webinar_id": webinar_id, "user_id": user["user_id"]}
    )
    if not exists:
        await db.webinar_leaderboard.insert_one({
            "webinar_id": webinar_id,
            "user_id": user["user_id"],
            "user_name": user.get("name", "User"),
            "reactions": 0, "questions": 0, "speaking_time": 0, "chat_messages": 0,
            "total_score": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        })

    await db.webinar_leaderboard.update_one(
        {"webinar_id": webinar_id, "user_id": user["user_id"]},
        {
            "$inc": {field: data.value, "total_score": score},
            "$set": {"user_name": user.get("name", "User"), "updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )

    return {"success": True, "action": data.action, "score_added": score}


@router.get("/{webinar_id}/reactions/summary")
async def get_reaction_summary(webinar_id: str):
    """Get aggregated reaction counts for the webinar."""
    pipeline = [
        {"$match": {"webinar_id": webinar_id}},
        {"$group": {"_id": "$reaction", "count": {"$sum": 1}, "emoji": {"$first": "$emoji"}}},
        {"$sort": {"count": -1}}
    ]
    results = await db.webinar_reactions.aggregate(pipeline).to_list(length=20)
    summary = {r["_id"]: {"count": r["count"], "emoji": r["emoji"]} for r in results}
    total = sum(r["count"] for r in results)
    return {"summary": summary, "total_reactions": total}
