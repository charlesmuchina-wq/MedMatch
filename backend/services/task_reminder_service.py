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


async def send_ai_dm_message(user_id: str, content: str, intent: str) -> dict:
    """Post a message from ENZI AI into the user's ENZI-AI DM (+ WS push)."""
    from routes.lumi_messenger import manager
    dm = await _get_or_create_ai_dm(user_id)
    now_iso = datetime.now(timezone.utc).isoformat()
    msg = {
        "id": f"msg_{uuid.uuid4().hex[:10]}",
        "channel_id": dm["id"],
        "sender_id": "enzi_ai",
        "sender_name": "ENZI AI",
        "content": content,
        "type": "ai_assistant",
        "ai_intent": intent,
        "reply_to": None,
        "created_at": now_iso,
        "reactions": {},
    }
    await db.lumi_messages.insert_one(msg)
    msg.pop("_id", None)
    await db.lumi_channels.update_one(
        {"id": dm["id"]},
        {"$set": {"last_message": {"content": content[:120], "sender_name": "ENZI AI"},
                  "last_message_at": now_iso},
         "$inc": {"message_count": 1}},
    )
    try:
        await manager.send_to_channel(dm["id"], {"type": "message", "data": msg})
        await manager.send_to_user(user_id, {
            "type": "notification",
            "data": {"title": "ENZI AI", "body": content[:100], "channel_id": dm["id"]},
        })
    except Exception:
        pass
    return msg


async def run_task_reminders() -> dict:
    """Find stale open meeting tasks and DM their owners in ENZI. Idempotent per cycle."""
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=REMIND_AFTER_DAYS)).isoformat()
    tasks = await db.agent_tasks.find({
        "status": {"$in": ["open", "in_progress"]},
        "$or": [{"source": "transcript"}, {"source": {"$regex": "^meeting"}},
                {"source_label": {"$regex": "^Meeting"}}],
        "created_at": {"$lte": cutoff},
        "$and": [{"$or": [{"last_reminded_at": {"$exists": False}}, {"last_reminded_at": {"$lte": cutoff}}]}],
    }, {"_id": 0}).sort("created_at", 1).to_list(200)

    if not tasks:
        return {"reminded_tasks": 0, "recipients": 0}

    by_recipient: dict = {}
    for t in tasks:
        rid = await _resolve_recipient(t)
        by_recipient.setdefault(rid, []).append(t)

    now_iso = now.isoformat()
    for rid, items in by_recipient.items():
        bullets = "\n".join(
            f"{i + 1}. **{t['title']}**" + (f" _(from {t['source_label']})_" if t.get("source_label") else "")
            for i, t in enumerate(items[:10])
        )
        plural = "s" if len(items) != 1 else ""
        content = (f"Friendly nudge: you have {len(items)} meeting action item{plural} still open after "
                   f"{REMIND_AFTER_DAYS}+ days:\n{bullets}\n\n"
                   f"Reply **done** to complete them all, **done 2** for a specific one, or **done <task words>**.")
        await send_ai_dm_message(rid, content, "task_reminder")

    task_ids = [t["id"] for t in tasks]
    await db.agent_tasks.update_many({"id": {"$in": task_ids}}, {"$set": {"last_reminded_at": now_iso}})
    return {"reminded_tasks": len(tasks), "recipients": len(by_recipient)}


async def _user_open_reminded_tasks(user: dict) -> list:
    name = (user.get("name") or "").strip()
    ors = [{"user_id": user["user_id"]}]
    if name:
        ors.append({"assignee": {"$regex": f"^{re.escape(name)}$", "$options": "i"}})
    return await db.agent_tasks.find({
        "status": {"$in": ["open", "in_progress"]},
        "last_reminded_at": {"$exists": True},
        "$or": ors,
    }, {"_id": 0}).sort("created_at", 1).to_list(50)


async def handle_ai_dm_reply(user: dict, content: str):
    """Process replies in the ENZI-AI DM: 'done', 'done 2', 'done <task words>'."""
    text = (content or "").strip()
    low = text.lower()
    if "done" not in low:
        await send_ai_dm_message(
            user["user_id"],
            "I track your task reminders here. Reply **done** to complete all reminded tasks, "
            "**done 2** for a specific one, or **done <task words>**.",
            "task_reply_help")
        return

    tasks = await _user_open_reminded_tasks(user)
    if not tasks:
        await send_ai_dm_message(user["user_id"], "You have no open reminded tasks — all clear! 🎉", "task_done")
        return

    matched = []
    m_idx = re.match(r"^(?:all\s+)?done(?:\s+all)?$", low)
    m_nums = re.match(r"^done\s+([\d,\s]+)$", low)
    m_words = re.match(r"^done\s+(.+)$", low)
    if m_idx:
        matched = tasks
    elif m_nums:
        idxs = {int(n) for n in re.findall(r"\d+", m_nums.group(1))}
        matched = [t for i, t in enumerate(tasks, start=1) if i in idxs]
    elif m_words:
        frag = m_words.group(1).strip().lower()
        matched = [t for t in tasks if frag in t["title"].lower()]

    if not matched:
        await send_ai_dm_message(
            user["user_id"],
            "I couldn't match that to an open task. Reply **done** for all, **done 2** for the second "
            "in the list, or **done <task words>**.",
            "task_done")
        return

    now_iso = datetime.now(timezone.utc).isoformat()
    await db.agent_tasks.update_many(
        {"id": {"$in": [t["id"] for t in matched]}},
        {"$set": {"status": "done", "updated_at": now_iso}})
    titles = "\n".join(f"- ~~{t['title']}~~" for t in matched[:10])
    remaining = len(tasks) - len(matched)
    tail = f"\n{remaining} task{'s' if remaining != 1 else ''} still open." if remaining else "\nThat's everything — nice work! 🎉"
    await send_ai_dm_message(
        user["user_id"],
        f"✅ Marked {len(matched)} task{'s' if len(matched) != 1 else ''} done:\n{titles}{tail}",
        "task_done")


DIGEST_HOUR_UTC = 7


async def _build_digest(user: dict) -> str:
    uid = user["user_id"]
    name = (user.get("name") or "").strip()
    ors = [{"user_id": uid}]
    if name:
        ors.append({"assignee": {"$regex": f"^{re.escape(name)}$", "$options": "i"}})
    open_tasks = await db.agent_tasks.find(
        {"status": {"$in": ["open", "in_progress"]}, "$or": ors},
        {"_id": 0, "title": 1, "priority": 1}).sort("created_at", 1).to_list(50)
    meetings = await db.karau_meetings.find(
        {"$or": [{"host_id": uid}, {"participants.user_id": uid}],
         "status": {"$in": ["waiting", "scheduled"]}},
        {"_id": 0, "title": 1, "scheduled_time": 1}).sort("created_at", -1).limit(3).to_list(3)

    channels = await db.lumi_channels.find(
        {"members.user_id": uid}, {"_id": 0, "id": 1, "name": 1}).to_list(200)
    ch_ids = [c["id"] for c in channels]
    ch_names = {c["id"]: c.get("name", "channel") for c in channels}
    receipts = await db.lumi_read_receipts.find(
        {"user_id": uid, "channel_id": {"$in": ch_ids}}, {"_id": 0}).to_list(200)
    receipt_map = {r["channel_id"]: r["last_read_at"] for r in receipts}
    unread = {}
    for cid in ch_ids:
        q = {"channel_id": cid, "sender_id": {"$ne": uid, "$nin": [uid, "enzi_ai"]}}
        if receipt_map.get(cid):
            q["created_at"] = {"$gt": receipt_map[cid]}
        n = await db.lumi_messages.count_documents(q)
        if n:
            unread[cid] = n

    if not open_tasks and not meetings and not unread:
        return ""

    parts = [f"Good morning{', ' + name.split(' ')[0] if name else ''}! Here's your daily digest:"]
    if open_tasks:
        parts.append(f"\n**Open tasks ({len(open_tasks)})**")
        parts += [f"- {t['title']}" + (" 🔴" if t.get("priority") == "high" else "") for t in open_tasks[:5]]
        if len(open_tasks) > 5:
            parts.append(f"- …and {len(open_tasks) - 5} more in your Agents worklist")
    if meetings:
        parts.append(f"\n**Upcoming meetings ({len(meetings)})**")
        parts += [f"- {m.get('title', 'Meeting')}" + (f" — {m['scheduled_time']}" if m.get("scheduled_time") else "") for m in meetings]
    if unread:
        total = sum(unread.values())
        top = sorted(unread.items(), key=lambda kv: -kv[1])[:3]
        parts.append(f"\n**Unread messages ({total})**")
        parts += [f"- #{ch_names.get(cid, 'channel')}: {n} unread" for cid, n in top]
    parts.append("\nReply **done** here anytime to close out reminded tasks.")
    return "\n".join(parts)


async def run_daily_digest(only_user_id: str = None, force: bool = False) -> dict:
    """Send the morning digest to eligible users (once per day, skipped when empty)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if only_user_id:
        user_ids = [only_user_id]
    else:
        user_ids = [u for u in await db.lumi_channels.distinct("members.user_id") if u != "enzi_ai"]
    sent = skipped = 0
    for uid in user_ids:
        if not force and await db.enzi_daily_digests.find_one({"user_id": uid, "date": today}):
            skipped += 1
            continue
        user = await db.users.find_one({"user_id": uid}, {"_id": 0, "user_id": 1, "name": 1})
        if not user:
            continue
        digest = await _build_digest(user)
        if not digest:
            skipped += 1
            continue
        await send_ai_dm_message(uid, digest, "daily_digest")
        await db.enzi_daily_digests.update_one(
            {"user_id": uid, "date": today},
            {"$set": {"user_id": uid, "date": today, "sent_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True)
        sent += 1
    return {"sent": sent, "skipped": skipped, "date": today}


async def daily_digest_loop():
    await asyncio.sleep(120)
    while True:
        try:
            if datetime.now(timezone.utc).hour == DIGEST_HOUR_UTC:
                result = await run_daily_digest()
                if result["sent"]:
                    logger.info(f"Daily digests sent: {result}")
        except Exception as e:
            logger.error(f"Daily digest cycle failed: {e}")
        await asyncio.sleep(3600)


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
