"""Task reminders: nudge owners in ENZI when meeting action items stay open 2+ days."""
import asyncio
import logging
import re
import uuid
from datetime import datetime, timezone, timedelta

from utils.database import db

logger = logging.getLogger(__name__)

REMIND_AFTER_DAYS = 2
CHECK_INTERVAL_SECONDS = 6 * 3600

ENZI_AI_MEMBER = {"user_id": "enzi_ai", "name": "ENZI AI", "email": "", "role": "member"}


async def _resolve_recipient(task: dict) -> str:
    assignee = (task.get("assignee") or "").strip()
    if assignee:
        u = await db.users.find_one(
            {"name": {"$regex": f"^{re.escape(assignee)}$", "$options": "i"}},
            {"_id": 0, "user_id": 1},
        )
        if u:
            return u["user_id"]
    return task["user_id"]


async def _get_or_create_ai_dm(user_id: str) -> dict:
    dm_key = "_".join(sorted([user_id, "enzi_ai"]))
    existing = await db.lumi_channels.find_one({"dm_key": dm_key}, {"_id": 0})
    if existing:
        return existing
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "user_id": 1, "name": 1, "email": 1}) or {}
    now = datetime.now(timezone.utc).isoformat()
    channel = {
        "id": f"dm_{uuid.uuid4().hex[:10]}",
        "dm_key": dm_key,
        "name": "ENZI AI",
        "description": "Reminders and nudges from ENZI AI",
        "channel_type": "dm",
        "is_private": True,
        "created_by": "enzi_ai",
        "created_at": now,
        "members": [
            {"user_id": user_id, "name": user.get("name", ""), "email": user.get("email", ""),
             "role": "member", "joined_at": now},
            {**ENZI_AI_MEMBER, "joined_at": now},
        ],
        "last_message": None,
        "last_message_at": now,
        "message_count": 0,
    }
    await db.lumi_channels.insert_one(channel)
    channel.pop("_id", None)
    return channel


async def run_task_reminders() -> dict:
    """Find stale open meeting tasks and DM their owners in ENZI. Idempotent per cycle."""
    from routes.lumi_messenger import manager

    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=REMIND_AFTER_DAYS)).isoformat()
    tasks = await db.agent_tasks.find({
        "status": {"$in": ["open", "in_progress"]},
        "$or": [{"source": "transcript"}, {"source": {"$regex": "^meeting"}},
                {"source_label": {"$regex": "^Meeting"}}],
        "created_at": {"$lte": cutoff},
        "$and": [{"$or": [{"last_reminded_at": {"$exists": False}}, {"last_reminded_at": {"$lte": cutoff}}]}],
    }, {"_id": 0}).to_list(200)

    if not tasks:
        return {"reminded_tasks": 0, "recipients": 0}

    by_recipient: dict = {}
    for t in tasks:
        rid = await _resolve_recipient(t)
        by_recipient.setdefault(rid, []).append(t)

    now_iso = now.isoformat()
    for rid, items in by_recipient.items():
        dm = await _get_or_create_ai_dm(rid)
        bullets = "\n".join(
            f"- **{t['title']}**" + (f" _(from {t['source_label']})_" if t.get("source_label") else "")
            for t in items[:10]
        )
        plural = "s" if len(items) != 1 else ""
        msg = {
            "id": f"msg_{uuid.uuid4().hex[:10]}",
            "channel_id": dm["id"],
            "sender_id": "enzi_ai",
            "sender_name": "ENZI AI",
            "content": f"Friendly nudge: you have {len(items)} meeting action item{plural} still open after {REMIND_AFTER_DAYS}+ days:\n{bullets}\n\nOpen your Agents worklist to update or complete them.",
            "type": "ai_assistant",
            "ai_intent": "task_reminder",
            "reply_to": None,
            "created_at": now_iso,
            "reactions": {},
        }
        await db.lumi_messages.insert_one(msg)
        msg.pop("_id", None)
        await db.lumi_channels.update_one(
            {"id": dm["id"]},
            {"$set": {"last_message": {"content": msg["content"][:120], "sender_name": "ENZI AI"},
                      "last_message_at": now_iso},
             "$inc": {"message_count": 1}},
        )
        try:
            await manager.send_to_channel(dm["id"], {"type": "message", "data": msg})
            await manager.send_to_user(rid, {
                "type": "notification",
                "data": {"title": "Open action items", "body": f"{len(items)} meeting task{plural} still open", "channel_id": dm["id"]},
            })
        except Exception:
            pass

    task_ids = [t["id"] for t in tasks]
    await db.agent_tasks.update_many({"id": {"$in": task_ids}}, {"$set": {"last_reminded_at": now_iso}})
    return {"reminded_tasks": len(tasks), "recipients": len(by_recipient)}


async def task_reminder_loop():
    await asyncio.sleep(60)
    while True:
        try:
            result = await run_task_reminders()
            if result["reminded_tasks"]:
                logger.info(f"Task reminders sent: {result}")
        except Exception as e:
            logger.error(f"Task reminder cycle failed: {e}")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
