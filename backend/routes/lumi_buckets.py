"""
LUMI Smart Buckets - AI-powered message categorization
"""
from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from datetime import datetime, timezone
import uuid
import os

from motor.motor_asyncio import AsyncIOMotorClient
from routes.auth import get_current_user

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "medmatch")
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")

router = APIRouter(prefix="/lumi/buckets", tags=["LUMI Smart Buckets"])


BUCKET_CATEGORIES = ["urgent", "action_required", "meeting_request", "fyi", "social"]


@router.get("/counts")
async def get_bucket_counts(request: Request):
    """Get message counts per smart bucket category for the current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Get user's channel IDs
    user_channels = await db.lumi_channels.find(
        {"members.user_id": user["user_id"]},
        {"_id": 0, "id": 1}
    ).to_list(100)
    channel_ids = [ch["id"] for ch in user_channels]

    if not channel_ids:
        return {"counts": {c: 0 for c in BUCKET_CATEGORIES}}

    # Get categorized message counts
    counts = {}
    for cat in BUCKET_CATEGORIES:
        count = await db.lumi_message_categories.count_documents({
            "channel_id": {"$in": channel_ids},
            "category": cat,
            "dismissed": {"$ne": True}
        })
        counts[cat] = count

    return {"counts": counts}


@router.get("/{category}")
async def get_bucket_messages(category: str, request: Request, limit: int = 20):
    """Get messages in a specific smart bucket category"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if category not in BUCKET_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category. Use: {BUCKET_CATEGORIES}")

    # Get user's channels
    user_channels = await db.lumi_channels.find(
        {"members.user_id": user["user_id"]},
        {"_id": 0, "id": 1, "name": 1}
    ).to_list(100)
    channel_ids = [ch["id"] for ch in user_channels]
    channel_map = {ch["id"]: ch["name"] for ch in user_channels}

    if not channel_ids:
        return {"messages": [], "category": category}

    # Get categorized messages
    cats = await db.lumi_message_categories.find(
        {"channel_id": {"$in": channel_ids}, "category": category, "dismissed": {"$ne": True}},
        {"_id": 0}
    ).sort("created_at", -1).to_list(limit)

    # Enrich with message content and channel name
    enriched = []
    for cat in cats:
        msg = await db.lumi_messages.find_one({"id": cat["message_id"]}, {"_id": 0})
        if msg:
            enriched.append({
                "id": cat["id"],
                "message_id": cat["message_id"],
                "channel_id": cat["channel_id"],
                "channel_name": channel_map.get(cat["channel_id"], "Unknown"),
                "category": category,
                "sender_name": msg.get("sender_name", ""),
                "content": msg.get("content", ""),
                "created_at": msg.get("created_at", cat.get("created_at", "")),
                "confidence": cat.get("confidence", 0),
            })

    return {"messages": enriched, "category": category}


@router.post("/{category}/{item_id}/dismiss")
async def dismiss_bucket_item(category: str, item_id: str, request: Request):
    """Dismiss a message from a smart bucket"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    await db.lumi_message_categories.update_one(
        {"id": item_id},
        {"$set": {"dismissed": True, "dismissed_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"status": "dismissed"}


@router.post("/scan")
async def scan_messages(request: Request):
    """AI-scan recent messages and categorize them into smart buckets"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not EMERGENT_KEY:
        raise HTTPException(status_code=500, detail="AI key not configured")

    # Get user's channels
    user_channels = await db.lumi_channels.find(
        {"members.user_id": user["user_id"]},
        {"_id": 0, "id": 1}
    ).to_list(100)
    channel_ids = [ch["id"] for ch in user_channels]

    if not channel_ids:
        return {"categorized": 0}

    # Get recent uncategorized messages (not from current user, not system)
    already_categorized = await db.lumi_message_categories.distinct("message_id")

    recent_msgs = await db.lumi_messages.find({
        "channel_id": {"$in": channel_ids},
        "sender_id": {"$ne": user["user_id"]},
        "type": {"$ne": "system"},
        "id": {"$nin": already_categorized}
    }, {"_id": 0}).sort("created_at", -1).to_list(30)

    if not recent_msgs:
        return {"categorized": 0}

    # Batch categorize with AI
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    messages_text = "\n".join([
        f"[{m.get('id')}] {m.get('sender_name','?')}: {m.get('content','')}"
        for m in recent_msgs[:20]
    ])

    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id=f"bucket-{uuid.uuid4().hex[:8]}",
        system_message="""Categorize each message into exactly ONE of these categories:
- urgent: Time-sensitive, critical requests, deadlines, emergencies
- action_required: Tasks, requests needing a response or action
- meeting_request: Meeting invites, scheduling, calendar items
- fyi: Informational updates, announcements, no action needed
- social: Casual chat, greetings, non-work conversation

Return ONLY a JSON object mapping message IDs to categories and confidence (0-1).
Example: {"msg_abc123": {"category": "urgent", "confidence": 0.9}, "msg_def456": {"category": "fyi", "confidence": 0.7}}
If a message doesn't clearly fit any category, use "fyi" with low confidence."""
    ).with_model("openai", "gpt-4.1-mini")

    try:
        response = await chat.send_message(UserMessage(text=messages_text))

        import json
        # Clean response (remove markdown fences if present)
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()

        categories = json.loads(clean)

        categorized_count = 0
        for msg in recent_msgs[:20]:
            msg_id = msg["id"]
            if msg_id in categories:
                cat_data = categories[msg_id]
                cat = cat_data.get("category", "fyi") if isinstance(cat_data, dict) else str(cat_data)
                confidence = cat_data.get("confidence", 0.5) if isinstance(cat_data, dict) else 0.5

                if cat in BUCKET_CATEGORIES:
                    doc = {
                        "id": f"bc_{uuid.uuid4().hex[:10]}",
                        "message_id": msg_id,
                        "channel_id": msg["channel_id"],
                        "category": cat,
                        "confidence": confidence,
                        "dismissed": False,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                    await db.lumi_message_categories.insert_one(doc)
                    categorized_count += 1

        return {"categorized": categorized_count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
