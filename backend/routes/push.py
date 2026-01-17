"""
Push Notifications Routes
Handles: Web push subscriptions, notification sending
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import logging
import json
import os

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/push", tags=["Push Notifications"])

# VAPID keys for web push (would be generated and stored securely)
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY', '')
VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY', '')
VAPID_CLAIMS_EMAIL = os.environ.get('VAPID_CLAIMS_EMAIL', 'mailto:admin@medmatch.com')

# ============== Models ==============

class PushSubscription(BaseModel):
    endpoint: str
    keys: dict  # {p256dh: str, auth: str}
    
class NotificationPreferences(BaseModel):
    job_matches: bool = True
    application_updates: bool = True
    interview_reminders: bool = True
    messages: bool = True
    weekly_digest: bool = True

class SendNotificationRequest(BaseModel):
    user_ids: Optional[List[str]] = None  # If None, send to all subscribed users
    title: str
    body: str
    icon: Optional[str] = None
    url: Optional[str] = None
    tag: Optional[str] = None
    data: Optional[dict] = None

# ============== Subscription Routes ==============

@router.get("/vapid-public-key")
async def get_vapid_public_key():
    """Get the VAPID public key for push subscription"""
    if not VAPID_PUBLIC_KEY:
        # Generate a placeholder response for development
        return {
            "publicKey": "",
            "configured": False,
            "message": "Push notifications not configured. Set VAPID_PUBLIC_KEY in environment."
        }
    
    return {"publicKey": VAPID_PUBLIC_KEY, "configured": True}

@router.post("/subscribe")
async def subscribe_to_push(subscription: PushSubscription, request: Request):
    """Subscribe user to push notifications"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Store subscription
    sub_doc = {
        "id": f"sub_{uuid.uuid4().hex[:12]}",
        "user_id": user["user_id"],
        "endpoint": subscription.endpoint,
        "keys": subscription.keys,
        "subscribed_at": datetime.now(timezone.utc).isoformat(),
        "active": True,
        "user_agent": request.headers.get("user-agent", "")
    }
    
    # Update or insert subscription (use endpoint as unique identifier)
    await db.push_subscriptions.update_one(
        {"user_id": user["user_id"], "endpoint": subscription.endpoint},
        {"$set": sub_doc},
        upsert=True
    )
    
    return {"message": "Subscription saved", "subscription_id": sub_doc["id"]}

@router.delete("/unsubscribe")
async def unsubscribe_from_push(request: Request, endpoint: Optional[str] = None):
    """Unsubscribe from push notifications"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if endpoint:
        # Unsubscribe specific endpoint
        await db.push_subscriptions.delete_one({
            "user_id": user["user_id"],
            "endpoint": endpoint
        })
    else:
        # Unsubscribe all devices
        await db.push_subscriptions.delete_many({"user_id": user["user_id"]})
    
    return {"message": "Unsubscribed from push notifications"}

@router.get("/subscriptions")
async def get_user_subscriptions(request: Request):
    """Get user's push notification subscriptions"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    subscriptions = await db.push_subscriptions.find(
        {"user_id": user["user_id"], "active": True},
        {"_id": 0, "keys": 0}  # Don't expose keys
    ).to_list(10)
    
    return {"subscriptions": subscriptions, "count": len(subscriptions)}

# ============== Preferences Routes ==============

@router.get("/preferences")
async def get_notification_preferences(request: Request):
    """Get user's notification preferences"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    prefs = await db.notification_preferences.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0}
    )
    
    # Return defaults if not set
    if not prefs:
        prefs = {
            "user_id": user["user_id"],
            "job_matches": True,
            "application_updates": True,
            "interview_reminders": True,
            "messages": True,
            "weekly_digest": True
        }
    
    return prefs

@router.put("/preferences")
async def update_notification_preferences(prefs: NotificationPreferences, request: Request):
    """Update user's notification preferences"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    prefs_doc = {
        "user_id": user["user_id"],
        **prefs.dict(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.notification_preferences.update_one(
        {"user_id": user["user_id"]},
        {"$set": prefs_doc},
        upsert=True
    )
    
    return {"message": "Preferences updated"}

# ============== Send Notification Routes ==============

@router.post("/send")
async def send_push_notification(notification: SendNotificationRequest, request: Request):
    """Send push notification to users (admin only)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Only admins can send bulk notifications
    if not (user.get("is_admin") or user.get("email") == "admin@medmatch.com"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not VAPID_PRIVATE_KEY:
        raise HTTPException(status_code=500, detail="Push notifications not configured")
    
    # Get subscriptions
    query = {"active": True}
    if notification.user_ids:
        query["user_id"] = {"$in": notification.user_ids}
    
    subscriptions = await db.push_subscriptions.find(query).to_list(1000)
    
    if not subscriptions:
        return {"message": "No active subscriptions", "sent": 0}
    
    # Prepare notification payload
    payload = {
        "title": notification.title,
        "body": notification.body,
        "icon": notification.icon or "/logo192.png",
        "badge": "/logo192.png",
        "tag": notification.tag,
        "data": {
            "url": notification.url or "/",
            **(notification.data or {})
        }
    }
    
    # Send notifications (would use pywebpush in production)
    sent_count = 0
    failed_count = 0
    
    try:
        from pywebpush import webpush, WebPushException
        
        for sub in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub["endpoint"],
                        "keys": sub["keys"]
                    },
                    data=json.dumps(payload),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": VAPID_CLAIMS_EMAIL}
                )
                sent_count += 1
            except WebPushException as e:
                logging.error(f"Push notification failed: {e}")
                failed_count += 1
                
                # Mark subscription as inactive if it failed permanently
                if e.response and e.response.status_code in [404, 410]:
                    await db.push_subscriptions.update_one(
                        {"id": sub["id"]},
                        {"$set": {"active": False}}
                    )
                    
    except ImportError:
        # pywebpush not installed - log for later
        logging.warning("pywebpush not installed - notifications queued but not sent")
        
        # Store notification for later delivery
        for sub in subscriptions:
            await db.pending_notifications.insert_one({
                "subscription_id": sub["id"],
                "user_id": sub["user_id"],
                "payload": payload,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "pending"
            })
        
        return {
            "message": "Notifications queued (pywebpush not installed)",
            "queued": len(subscriptions)
        }
    
    return {
        "message": f"Notifications sent",
        "sent": sent_count,
        "failed": failed_count
    }

# ============== Helper Functions ==============

async def send_notification_to_user(user_id: str, title: str, body: str, data: dict = None):
    """Helper function to send notification to a specific user"""
    subscriptions = await db.push_subscriptions.find({
        "user_id": user_id,
        "active": True
    }).to_list(10)
    
    if not subscriptions:
        return False
    
    # Check user preferences
    prefs = await db.notification_preferences.find_one({"user_id": user_id})
    notification_type = data.get("type") if data else None
    
    if prefs and notification_type:
        pref_map = {
            "job_match": "job_matches",
            "application_update": "application_updates",
            "interview_reminder": "interview_reminders",
            "message": "messages"
        }
        pref_key = pref_map.get(notification_type)
        if pref_key and not prefs.get(pref_key, True):
            return False  # User disabled this notification type
    
    payload = {
        "title": title,
        "body": body,
        "icon": "/logo192.png",
        "data": data or {}
    }
    
    # Store in notifications collection
    await db.notifications.insert_one({
        "id": f"notif_{uuid.uuid4().hex[:8]}",
        "user_id": user_id,
        "type": notification_type or "general",
        "title": title,
        "message": body,
        "data": data,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Try to send push notification
    if not VAPID_PRIVATE_KEY:
        return True  # In-app notification created, push not configured
    
    try:
        from pywebpush import webpush
        
        for sub in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub["endpoint"],
                        "keys": sub["keys"]
                    },
                    data=json.dumps(payload),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": VAPID_CLAIMS_EMAIL}
                )
            except Exception as e:
                logging.error(f"Push failed for user {user_id}: {e}")
                
    except ImportError:
        pass
    
    return True

# Export helper
__all__ = ['router', 'send_notification_to_user']
