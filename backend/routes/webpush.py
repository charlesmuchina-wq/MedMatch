"""
Real Web Push Notifications Server
Uses VAPID keys for actual push notification delivery
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
import json
import os
import base64

from pywebpush import webpush, WebPushException
from py_vapid import Vapid

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/webpush", tags=["Real Web Push"])

# ============== VAPID Configuration ==============

# Generate VAPID keys if not present in environment
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY")
VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY")
VAPID_CLAIMS_EMAIL = os.environ.get("VAPID_CLAIMS_EMAIL", "mailto:admin@medmatch.com")

# Generate keys if not configured
if not VAPID_PRIVATE_KEY or not VAPID_PUBLIC_KEY:
    try:
        vapid = Vapid()
        vapid.generate_keys()
        VAPID_PRIVATE_KEY = vapid.private_key_pem.decode('utf-8') if hasattr(vapid.private_key_pem, 'decode') else str(vapid.private_key_pem)
        VAPID_PUBLIC_KEY = vapid.public_key_base64url
        logging.info(f"Generated new VAPID keys. Public key: {VAPID_PUBLIC_KEY[:50]}...")
    except Exception as e:
        logging.error(f"Failed to generate VAPID keys: {e}")
        VAPID_PRIVATE_KEY = None
        VAPID_PUBLIC_KEY = None

# ============== Models ==============

class WebPushSubscription(BaseModel):
    endpoint: str
    keys: Dict[str, str]  # p256dh and auth
    expiration_time: Optional[int] = None

class PushNotificationPayload(BaseModel):
    title: str
    body: str
    icon: str = "/logo192.png"
    badge: str = "/badge-icon.png"
    image: Optional[str] = None
    tag: Optional[str] = None
    require_interaction: bool = False
    renotify: bool = False
    silent: bool = False
    data: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, str]]] = None
    vibrate: Optional[List[int]] = None

class SendNotificationRequest(BaseModel):
    user_id: Optional[str] = None  # If None, send to current user
    payload: PushNotificationPayload
    ttl: int = 86400  # Time to live in seconds (default 24 hours)

# ============== Helper Functions ==============

async def send_push_notification(
    subscription: Dict,
    payload: Dict,
    ttl: int = 86400
) -> Dict:
    """Send a push notification to a subscription"""
    if not VAPID_PRIVATE_KEY:
        return {"success": False, "error": "VAPID keys not configured"}
    
    try:
        subscription_info = {
            "endpoint": subscription["endpoint"],
            "keys": subscription["keys"]
        }
        
        # Convert payload to JSON string
        payload_json = json.dumps(payload)
        
        response = webpush(
            subscription_info=subscription_info,
            data=payload_json,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": VAPID_CLAIMS_EMAIL
            },
            ttl=ttl
        )
        
        return {
            "success": True,
            "status_code": response.status_code if hasattr(response, 'status_code') else 201
        }
        
    except WebPushException as e:
        logging.error(f"WebPush error: {e}")
        
        # Handle different error scenarios
        if e.response and e.response.status_code == 410:
            # Subscription expired - mark as inactive
            await db.webpush_subscriptions.update_one(
                {"endpoint": subscription["endpoint"]},
                {"$set": {"active": False, "expired_at": datetime.now(timezone.utc).isoformat()}}
            )
            return {"success": False, "error": "Subscription expired", "should_remove": True}
        
        return {"success": False, "error": str(e)}
    
    except Exception as e:
        logging.error(f"Push notification error: {e}")
        return {"success": False, "error": str(e)}

async def send_to_user(user_id: str, payload: Dict, ttl: int = 86400) -> Dict:
    """Send push notification to all of a user's subscriptions"""
    subscriptions = await db.webpush_subscriptions.find(
        {"user_id": user_id, "active": True}
    ).to_list(length=10)
    
    if not subscriptions:
        return {"success": False, "error": "No active subscriptions", "sent": 0}
    
    results = []
    for sub in subscriptions:
        result = await send_push_notification(sub, payload, ttl)
        results.append(result)
        
        # If subscription expired, it's already marked inactive by send_push_notification
    
    successful = sum(1 for r in results if r.get("success"))
    
    return {
        "success": successful > 0,
        "sent": successful,
        "total_subscriptions": len(subscriptions),
        "results": results
    }

# ============== Routes ==============

@router.get("/vapid-public-key")
async def get_vapid_public_key():
    """Get the VAPID public key for client-side subscription"""
    if not VAPID_PUBLIC_KEY:
        raise HTTPException(status_code=503, detail="Push notifications not configured")
    
    return {
        "publicKey": VAPID_PUBLIC_KEY,
        "configured": True
    }

@router.post("/subscribe")
async def subscribe_webpush(subscription: WebPushSubscription, request: Request):
    """Subscribe to web push notifications"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user.get("user_id")
    
    # Check for existing subscription
    existing = await db.webpush_subscriptions.find_one({"endpoint": subscription.endpoint})
    
    if existing:
        # Update existing
        await db.webpush_subscriptions.update_one(
            {"endpoint": subscription.endpoint},
            {"$set": {
                "user_id": user_id,
                "keys": subscription.keys,
                "expiration_time": subscription.expiration_time,
                "active": True,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        return {"success": True, "message": "Subscription updated", "subscription_id": str(existing.get("_id"))}
    
    # Create new subscription
    subscription_doc = {
        "subscription_id": str(uuid.uuid4()),
        "user_id": user_id,
        "endpoint": subscription.endpoint,
        "keys": subscription.keys,
        "expiration_time": subscription.expiration_time,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = await db.webpush_subscriptions.insert_one(subscription_doc)
    
    # Send welcome notification
    await send_push_notification(
        subscription_doc,
        {
            "title": "🎉 Notifications Enabled!",
            "body": "You'll now receive job alerts and updates from MedMatch.",
            "icon": "/logo192.png",
            "tag": "welcome",
            "data": {"type": "welcome"}
        }
    )
    
    return {
        "success": True,
        "message": "Subscribed successfully",
        "subscription_id": subscription_doc["subscription_id"]
    }

@router.delete("/unsubscribe")
async def unsubscribe_webpush(request: Request):
    """Unsubscribe from web push notifications"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    body = await request.json()
    endpoint = body.get("endpoint")
    
    if not endpoint:
        raise HTTPException(status_code=400, detail="Endpoint required")
    
    result = await db.webpush_subscriptions.update_one(
        {"endpoint": endpoint, "user_id": user.get("user_id")},
        {"$set": {"active": False, "unsubscribed_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"success": True, "modified": result.modified_count}

@router.post("/send")
async def send_notification(
    notification: SendNotificationRequest,
    request: Request,
    background_tasks: BackgroundTasks
):
    """Send a push notification"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    target_user_id = notification.user_id or user.get("user_id")
    
    payload = {
        "title": notification.payload.title,
        "body": notification.payload.body,
        "icon": notification.payload.icon,
        "badge": notification.payload.badge,
        "tag": notification.payload.tag,
        "data": notification.payload.data or {},
        "requireInteraction": notification.payload.require_interaction,
        "renotify": notification.payload.renotify,
        "silent": notification.payload.silent
    }
    
    if notification.payload.image:
        payload["image"] = notification.payload.image
    
    if notification.payload.actions:
        payload["actions"] = notification.payload.actions
    
    if notification.payload.vibrate:
        payload["vibrate"] = notification.payload.vibrate
    
    # Store notification in history
    notification_record = {
        "notification_id": str(uuid.uuid4()),
        "user_id": target_user_id,
        "sender_id": user.get("user_id"),
        "title": payload["title"],
        "body": payload["body"],
        "data": payload.get("data"),
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notification_history.insert_one(notification_record)
    
    # Send notification
    result = await send_to_user(target_user_id, payload, notification.ttl)
    
    # Update status
    await db.notification_history.update_one(
        {"notification_id": notification_record["notification_id"]},
        {"$set": {"status": "sent" if result["success"] else "failed", "result": result}}
    )
    
    return {
        "success": result["success"],
        "notification_id": notification_record["notification_id"],
        "sent_to": result.get("sent", 0),
        "total_subscriptions": result.get("total_subscriptions", 0)
    }

@router.post("/send-test")
async def send_test_notification(request: Request):
    """Send a test notification to the current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = {
        "title": "🧪 Test Notification",
        "body": "This is a test notification from MedMatch. Push notifications are working!",
        "icon": "/logo192.png",
        "badge": "/badge-icon.png",
        "tag": "test-" + str(uuid.uuid4())[:8],
        "data": {
            "type": "test",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "requireInteraction": False
    }
    
    result = await send_to_user(user.get("user_id"), payload)
    
    return {
        "success": result["success"],
        "message": "Test notification sent" if result["success"] else "Failed to send",
        "details": result
    }

@router.get("/status")
async def get_push_status(request: Request):
    """Get push notification status for current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    subscriptions = await db.webpush_subscriptions.find(
        {"user_id": user.get("user_id"), "active": True},
        {"_id": 0, "endpoint": 0, "keys": 0}  # Don't expose sensitive data
    ).to_list(length=10)
    
    return {
        "configured": bool(VAPID_PUBLIC_KEY),
        "vapid_public_key": VAPID_PUBLIC_KEY if VAPID_PUBLIC_KEY else None,
        "active_subscriptions": len(subscriptions),
        "subscriptions": [
            {
                "subscription_id": s.get("subscription_id"),
                "created_at": s.get("created_at"),
                "active": s.get("active")
            }
            for s in subscriptions
        ]
    }

# ============== Notification Types ==============

@router.post("/notify/job-match")
async def notify_job_match(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Send job match notification"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    body = await request.json()
    target_user_id = body.get("user_id", user.get("user_id"))
    job_title = body.get("job_title", "New Position")
    company = body.get("company", "A Company")
    match_score = body.get("match_score", 85)
    job_id = body.get("job_id")
    
    payload = {
        "title": f"🎯 {match_score}% Job Match!",
        "body": f"{job_title} at {company}",
        "icon": "/logo192.png",
        "badge": "/badge-icon.png",
        "tag": f"job-match-{job_id}" if job_id else "job-match",
        "data": {
            "type": "job_match",
            "job_id": job_id,
            "match_score": match_score,
            "url": f"/jobs/{job_id}" if job_id else "/search"
        },
        "actions": [
            {"action": "view", "title": "View Job"},
            {"action": "dismiss", "title": "Dismiss"}
        ],
        "requireInteraction": True
    }
    
    result = await send_to_user(target_user_id, payload)
    return result

@router.post("/notify/interview-reminder")
async def notify_interview_reminder(
    request: Request
):
    """Send interview reminder notification"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    body = await request.json()
    target_user_id = body.get("user_id", user.get("user_id"))
    company = body.get("company", "Company")
    position = body.get("position", "Position")
    time = body.get("time", "Soon")
    interview_id = body.get("interview_id")
    
    payload = {
        "title": "📅 Interview Reminder",
        "body": f"{position} at {company} - {time}",
        "icon": "/logo192.png",
        "badge": "/badge-icon.png",
        "tag": f"interview-{interview_id}" if interview_id else "interview",
        "data": {
            "type": "interview_reminder",
            "interview_id": interview_id,
            "url": f"/interviews/{interview_id}" if interview_id else "/interviews"
        },
        "actions": [
            {"action": "prepare", "title": "Prepare"},
            {"action": "view", "title": "View Details"}
        ],
        "requireInteraction": True,
        "vibrate": [200, 100, 200]
    }
    
    result = await send_to_user(target_user_id, payload)
    return result

@router.post("/notify/application-update")
async def notify_application_update(
    request: Request
):
    """Send application status update notification"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    body = await request.json()
    target_user_id = body.get("user_id", user.get("user_id"))
    company = body.get("company", "Company")
    status = body.get("status", "Updated")
    application_id = body.get("application_id")
    
    # Emoji based on status
    emoji = {
        "viewed": "👀",
        "shortlisted": "⭐",
        "interview": "📅",
        "offer": "🎉",
        "rejected": "😔"
    }.get(status.lower(), "📋")
    
    payload = {
        "title": f"{emoji} Application {status}",
        "body": f"Your application at {company} has been {status.lower()}",
        "icon": "/logo192.png",
        "badge": "/badge-icon.png",
        "tag": f"application-{application_id}" if application_id else "application",
        "data": {
            "type": "application_update",
            "application_id": application_id,
            "status": status,
            "url": f"/applications/{application_id}" if application_id else "/applications"
        },
        "requireInteraction": status.lower() in ["interview", "offer"]
    }
    
    result = await send_to_user(target_user_id, payload)
    return result

@router.post("/notify/message")
async def notify_new_message(
    request: Request
):
    """Send new message notification"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    body = await request.json()
    target_user_id = body.get("user_id", user.get("user_id"))
    sender_name = body.get("sender_name", "Someone")
    preview = body.get("preview", "sent you a message")
    conversation_id = body.get("conversation_id")
    
    payload = {
        "title": f"💬 New Message from {sender_name}",
        "body": preview[:100],
        "icon": "/logo192.png",
        "badge": "/badge-icon.png",
        "tag": f"message-{conversation_id}" if conversation_id else "message",
        "data": {
            "type": "message",
            "conversation_id": conversation_id,
            "url": f"/messages/{conversation_id}" if conversation_id else "/messages"
        },
        "actions": [
            {"action": "reply", "title": "Reply"},
            {"action": "view", "title": "View"}
        ],
        "renotify": True
    }
    
    result = await send_to_user(target_user_id, payload)
    return result
