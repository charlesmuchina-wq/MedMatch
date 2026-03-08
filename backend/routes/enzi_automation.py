"""
ENZI Scheduled Messages & Bot/Automation Platform
- Schedule messages for later delivery
- Webhook endpoints for incoming/outgoing messages
- Auto-responder bots per channel
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import uuid
import os
import logging
import asyncio

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi/automation", tags=["ENZI Automation"])
logger = logging.getLogger(__name__)


class ScheduleMessageRequest(BaseModel):
    channel_id: str
    content: str
    scheduled_at: str  # ISO format datetime


class WebhookCreate(BaseModel):
    channel_id: str
    name: str
    events: List[str] = ["message"]  # message, member_join, member_leave


class AutoResponderCreate(BaseModel):
    channel_id: str
    trigger: str  # keyword or regex
    response: str
    is_active: bool = True


# ===== Scheduled Messages =====

@router.post("/schedule")
async def schedule_message(req: ScheduleMessageRequest, request: Request):
    """Schedule a message for later delivery"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        scheduled_time = datetime.fromisoformat(req.scheduled_at.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")

    if scheduled_time <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Scheduled time must be in the future")

    msg_id = str(uuid.uuid4())
    await db.enzi_scheduled_messages.insert_one({
        "id": msg_id,
        "channel_id": req.channel_id,
        "content": req.content,
        "sender_id": user.get("user_id"),
        "sender_name": user.get("name", user.get("email", "User")),
        "scheduled_at": scheduled_time.isoformat(),
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {"id": msg_id, "status": "scheduled", "scheduled_at": scheduled_time.isoformat()}


@router.get("/schedule")
async def get_scheduled_messages(request: Request):
    """Get all pending scheduled messages for the user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    msgs = await db.enzi_scheduled_messages.find(
        {"sender_id": user.get("user_id"), "status": "pending"},
        {"_id": 0}
    ).sort("scheduled_at", 1).to_list(50)

    return {"scheduled": msgs, "count": len(msgs)}


@router.delete("/schedule/{msg_id}")
async def cancel_scheduled_message(msg_id: str, request: Request):
    """Cancel a scheduled message"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.enzi_scheduled_messages.update_one(
        {"id": msg_id, "sender_id": user.get("user_id"), "status": "pending"},
        {"$set": {"status": "cancelled"}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Scheduled message not found")

    return {"status": "cancelled"}


# ===== Webhooks =====

@router.post("/webhooks")
async def create_webhook(req: WebhookCreate, request: Request):
    """Create an incoming webhook for a channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    webhook_id = str(uuid.uuid4())
    webhook_token = str(uuid.uuid4())
    app_url = os.environ.get("REACT_APP_BACKEND_URL", "")

    await db.enzi_webhooks.insert_one({
        "id": webhook_id,
        "token": webhook_token,
        "channel_id": req.channel_id,
        "name": req.name,
        "events": req.events,
        "created_by": user.get("user_id"),
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {
        "id": webhook_id,
        "token": webhook_token,
        "url": f"{app_url}/api/lumi/automation/webhooks/{webhook_id}/send",
        "events": req.events
    }


@router.post("/webhooks/{webhook_id}/send")
async def webhook_send_message(webhook_id: str, request: Request):
    """Receive a message via webhook and post it to the channel"""
    body = await request.json()
    content = body.get("content") or body.get("text") or body.get("message", "")
    sender_name = body.get("username") or body.get("sender", "Webhook Bot")

    if not content:
        raise HTTPException(status_code=400, detail="Message content required")

    webhook = await db.enzi_webhooks.find_one({"id": webhook_id, "is_active": True})
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found or inactive")

    msg_id = str(uuid.uuid4())
    await db.lumi_messages.insert_one({
        "id": msg_id,
        "channel_id": webhook["channel_id"],
        "content": content,
        "sender_id": f"webhook_{webhook_id}",
        "sender_name": f"[Bot] {sender_name}",
        "type": "webhook",
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {"status": "sent", "message_id": msg_id}


@router.get("/webhooks")
async def list_webhooks(request: Request, channel_id: Optional[str] = None):
    """List webhooks for the user or a specific channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    query = {"created_by": user.get("user_id")}
    if channel_id:
        query["channel_id"] = channel_id

    webhooks = await db.enzi_webhooks.find(query, {"_id": 0}).to_list(50)
    return {"webhooks": webhooks, "count": len(webhooks)}


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str, request: Request):
    """Delete a webhook"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.enzi_webhooks.delete_one({"id": webhook_id, "created_by": user.get("user_id")})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return {"status": "deleted"}


# ===== Auto-Responders =====

@router.post("/auto-responders")
async def create_auto_responder(req: AutoResponderCreate, request: Request):
    """Create an auto-responder for a channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    responder_id = str(uuid.uuid4())
    await db.enzi_auto_responders.insert_one({
        "id": responder_id,
        "channel_id": req.channel_id,
        "trigger": req.trigger,
        "response": req.response,
        "is_active": req.is_active,
        "created_by": user.get("user_id"),
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {"id": responder_id, "status": "created"}


@router.get("/auto-responders")
async def list_auto_responders(request: Request, channel_id: Optional[str] = None):
    """List auto-responders"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    query = {"created_by": user.get("user_id")}
    if channel_id:
        query["channel_id"] = channel_id

    responders = await db.enzi_auto_responders.find(query, {"_id": 0}).to_list(50)
    return {"auto_responders": responders, "count": len(responders)}


@router.delete("/auto-responders/{responder_id}")
async def delete_auto_responder(responder_id: str, request: Request):
    """Delete an auto-responder"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.enzi_auto_responders.delete_one({"id": responder_id, "created_by": user.get("user_id")})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Auto-responder not found")

    return {"status": "deleted"}


# ===== Background Task: Process Scheduled Messages =====

async def process_scheduled_messages():
    """Background task to send scheduled messages that are due"""
    while True:
        try:
            now = datetime.now(timezone.utc).isoformat()
            due_msgs = await db.enzi_scheduled_messages.find(
                {"status": "pending", "scheduled_at": {"$lte": now}},
                {"_id": 0}
            ).to_list(50)

            for msg in due_msgs:
                msg_id = str(uuid.uuid4())
                await db.lumi_messages.insert_one({
                    "id": msg_id,
                    "channel_id": msg["channel_id"],
                    "content": msg["content"],
                    "sender_id": msg["sender_id"],
                    "sender_name": msg.get("sender_name", "User"),
                    "type": "scheduled",
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
                await db.enzi_scheduled_messages.update_one(
                    {"id": msg["id"]},
                    {"$set": {"status": "sent", "sent_at": datetime.now(timezone.utc).isoformat()}}
                )
                logger.info(f"Sent scheduled message {msg['id']} to channel {msg['channel_id']}")
        except Exception as e:
            logger.error(f"Error processing scheduled messages: {e}")

        await asyncio.sleep(30)  # Check every 30 seconds
