"""
ENZI Advanced Behavioral Modeling
Context-aware triggers, smart suggestions, and personalization
based on user behavior patterns and conversation analysis.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid
from collections import Counter

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi/behavior", tags=["ENZI Behavioral Modeling"])


class TriggerResponse(BaseModel):
    trigger_id: str
    type: str
    title: str
    message: str
    action: Optional[str] = None
    priority: str = "low"


@router.get("/context-triggers")
async def get_context_triggers(request: Request):
    """Get context-aware triggers based on current user behavior"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    uid = user["user_id"]
    now = datetime.now(timezone.utc)
    triggers = []

    # 1. Check for unread messages in high-priority channels
    unread = await db.lumi_unread.find({"user_id": uid}, {"_id": 0}).to_list(50)
    total_unread = sum(u.get("count", 0) for u in unread)
    if total_unread > 10:
        triggers.append({
            "trigger_id": str(uuid.uuid4()), "type": "unread_overload",
            "title": "Message Catch-Up", "priority": "medium",
            "message": f"You have {total_unread} unread messages across channels. Want a quick summary?",
            "action": "summarize_unread"
        })

    # 2. Check for inactive channels (user hasn't visited in 3+ days)
    recent_visits = await db.lumi_nav_actions.find(
        {"user_id": uid, "action": "channel_visit"},
        {"_id": 0}
    ).sort("timestamp", -1).limit(50).to_list(50)

    visited_channels = set()
    for v in recent_visits:
        ts = v.get("timestamp", "")
        if ts:
            try:
                vt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if (now - vt).days < 3:
                    visited_channels.add(v.get("target_id"))
            except (ValueError, TypeError):
                pass

    user_channels = await db.lumi_channels.find(
        {"members": uid, "channel_type": {"$ne": "dm"}}, {"_id": 0, "id": 1, "name": 1}
    ).to_list(20)
    inactive = [ch for ch in user_channels if ch["id"] not in visited_channels]
    if inactive:
        triggers.append({
            "trigger_id": str(uuid.uuid4()), "type": "inactive_channels",
            "title": "Channels Need Attention",
            "message": f"{len(inactive)} channel(s) you haven't checked recently: {', '.join(ch['name'] for ch in inactive[:3])}",
            "action": "visit_channel", "priority": "low"
        })

    # 3. Time-based triggers
    hour = now.hour
    if 8 <= hour <= 10:
        triggers.append({
            "trigger_id": str(uuid.uuid4()), "type": "morning_routine",
            "title": "Good Morning!", "priority": "low",
            "message": "Start your day with a quick standup or check scheduled messages.",
            "action": "run_standup"
        })
    elif 16 <= hour <= 18:
        triggers.append({
            "trigger_id": str(uuid.uuid4()), "type": "end_of_day",
            "title": "End of Day", "priority": "low",
            "message": "Review today's conversations and schedule any follow-ups.",
            "action": "daily_summary"
        })

    # 4. Check for scheduled messages due soon
    upcoming = await db.scheduled_messages.count_documents({
        "user_id": uid,
        "send_at": {"$lte": (now + timedelta(hours=2)).isoformat(), "$gt": now.isoformat()},
        "status": "pending"
    })
    if upcoming > 0:
        triggers.append({
            "trigger_id": str(uuid.uuid4()), "type": "scheduled_messages",
            "title": "Upcoming Messages",
            "message": f"{upcoming} scheduled message(s) will be sent in the next 2 hours.",
            "action": "view_scheduled", "priority": "medium"
        })

    return {"triggers": triggers, "count": len(triggers)}


@router.get("/smart-suggestions")
async def get_smart_suggestions(request: Request, channel_id: Optional[str] = None):
    """Get AI-powered smart suggestions based on conversation context"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    uid = user["user_id"]
    suggestions = []

    # Analyze recent message patterns
    query = {"sender_id": uid}
    if channel_id:
        query["channel_id"] = channel_id

    recent_msgs = await db.lumi_messages.find(
        query, {"_id": 0, "content": 1, "created_at": 1}
    ).sort("created_at", -1).limit(30).to_list(30)

    # Pattern: user asks questions often -> suggest bot
    question_count = sum(1 for m in recent_msgs if m.get("content", "").endswith("?"))
    if question_count > 3:
        suggestions.append({
            "id": str(uuid.uuid4()), "type": "bot_suggestion",
            "title": "Install Summary Bot",
            "description": "You ask a lot of questions. A Summary Bot can help catch you up on conversations.",
            "action": "install_bot", "action_data": {"bot_id": "summary"}
        })

    # Pattern: frequent meetings mentioned
    meeting_mentions = sum(1 for m in recent_msgs
                          if any(w in m.get("content", "").lower() for w in ["meeting", "call", "standup", "sync"]))
    if meeting_mentions > 2:
        suggestions.append({
            "id": str(uuid.uuid4()), "type": "meeting_suggestion",
            "title": "Schedule a Meeting",
            "description": "You've mentioned meetings several times. Would you like to start one?",
            "action": "create_meeting"
        })

    # Pattern: user active at unusual hours
    now = datetime.now(timezone.utc)
    if now.hour < 6 or now.hour > 22:
        suggestions.append({
            "id": str(uuid.uuid4()), "type": "wellbeing",
            "title": "Working Late?",
            "description": "Consider scheduling messages for tomorrow instead.",
            "action": "schedule_message"
        })

    # Pattern: no E2EE setup
    e2ee_key = await db.e2ee_keys.find_one({"user_id": uid}, {"_id": 0})
    if not e2ee_key:
        suggestions.append({
            "id": str(uuid.uuid4()), "type": "security",
            "title": "Enable End-to-End Encryption",
            "description": "Secure your DMs with E2EE. Generate your encryption keys now.",
            "action": "enable_e2ee"
        })

    return {"suggestions": suggestions, "count": len(suggestions)}


@router.get("/usage-insights")
async def get_usage_insights(request: Request):
    """Get personalized usage insights and analytics"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    uid = user["user_id"]
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()

    # Count messages sent this week
    msg_count = await db.lumi_messages.count_documents({
        "sender_id": uid, "created_at": {"$gte": week_ago}
    })

    # Count channels active in
    active_channels = await db.lumi_nav_actions.distinct(
        "target_id", {"user_id": uid, "action": "channel_visit", "timestamp": {"$gte": week_ago}}
    )

    # Most active hours
    actions = await db.lumi_nav_actions.find(
        {"user_id": uid, "timestamp": {"$gte": week_ago}},
        {"_id": 0, "timestamp": 1}
    ).to_list(200)

    hour_counts = Counter()
    for a in actions:
        try:
            ts = datetime.fromisoformat(a["timestamp"].replace("Z", "+00:00"))
            hour_counts[ts.hour] += 1
        except (ValueError, TypeError, KeyError):
            pass

    peak_hours = sorted(hour_counts.items(), key=lambda x: -x[1])[:3]

    # Meetings this week
    meeting_count = await db.meetings.count_documents({
        "$or": [{"host_id": uid}, {"participants": uid}],
        "created_at": {"$gte": week_ago}
    })

    return {
        "period": "last_7_days",
        "messages_sent": msg_count,
        "active_channels": len(active_channels),
        "meetings_attended": meeting_count,
        "peak_hours": [{"hour": h, "count": c} for h, c in peak_hours],
        "engagement_score": min(100, int((msg_count * 2 + len(active_channels) * 10 + meeting_count * 15))),
        "insights": [
            f"You sent {msg_count} messages this week" if msg_count > 0 else "Start a conversation today!",
            f"Active in {len(active_channels)} channels" if active_channels else "Explore some channels",
            f"Attended {meeting_count} meetings" if meeting_count > 0 else "No meetings this week"
        ]
    }
