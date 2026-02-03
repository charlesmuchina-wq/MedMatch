"""
Push Notifications Routes
Handles: Web push subscriptions, notification sending, preferences
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Push Notifications"])

# ============== Models ==============

class PushSubscription(BaseModel):
    endpoint: str
    keys: Dict[str, str]  # p256dh and auth keys
    user_agent: Optional[str] = None

class NotificationPreferences(BaseModel):
    job_alerts: bool = True
    application_updates: bool = True
    messages: bool = True
    interview_reminders: bool = True
    weekly_digest: bool = True
    marketing: bool = False

class NotificationPayload(BaseModel):
    title: str
    body: str
    icon: Optional[str] = "/logo192.png"
    badge: Optional[str] = "/badge.png"
    tag: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, str]]] = None

class BulkNotification(BaseModel):
    user_ids: List[str]
    notification: NotificationPayload
    notification_type: str = "general"

# ============== Helper Functions ==============

async def store_notification(user_id: str, notification: Dict, status: str = "pending"):
    """Store notification in database for history/retry"""
    record = {
        "notification_id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": notification.get("title"),
        "body": notification.get("body"),
        "data": notification.get("data"),
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "read": False
    }
    await db.notification_history.insert_one(record)
    return record["notification_id"]

async def get_user_subscriptions(user_id: str) -> List[Dict]:
    """Get all push subscriptions for a user"""
    subscriptions = await db.push_subscriptions.find(
        {"user_id": user_id, "active": True},
        {"_id": 0}
    ).to_list(length=10)
    return subscriptions

# ============== Routes ==============

@router.post("/subscribe")
async def subscribe_to_push(subscription: PushSubscription, request: Request):
    """Subscribe device to push notifications"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user.get("user_id")
    
    # Check if subscription already exists
    existing = await db.push_subscriptions.find_one({
        "endpoint": subscription.endpoint
    })
    
    if existing:
        # Update existing subscription
        await db.push_subscriptions.update_one(
            {"endpoint": subscription.endpoint},
            {"$set": {
                "user_id": user_id,
                "keys": subscription.keys,
                "user_agent": subscription.user_agent,
                "active": True,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        return {"message": "Subscription updated", "subscription_id": str(existing.get("subscription_id"))}
    
    # Create new subscription
    subscription_id = str(uuid.uuid4())
    sub_doc = {
        "subscription_id": subscription_id,
        "user_id": user_id,
        "endpoint": subscription.endpoint,
        "keys": subscription.keys,
        "user_agent": subscription.user_agent,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.push_subscriptions.insert_one(sub_doc)
    
    return {"message": "Subscribed successfully", "subscription_id": subscription_id}

@router.delete("/unsubscribe")
async def unsubscribe_from_push(endpoint: str, request: Request):
    """Unsubscribe device from push notifications"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.push_subscriptions.update_one(
        {"endpoint": endpoint, "user_id": user.get("user_id")},
        {"$set": {"active": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return {"message": "Unsubscribed successfully"}

@router.get("/preferences")
async def get_notification_preferences(request: Request):
    """Get user's notification preferences"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    prefs = await db.notification_preferences.find_one(
        {"user_id": user.get("user_id")},
        {"_id": 0}
    )
    
    if not prefs:
        # Return defaults
        return {
            "user_id": user.get("user_id"),
            "job_alerts": True,
            "application_updates": True,
            "messages": True,
            "interview_reminders": True,
            "weekly_digest": True,
            "marketing": False
        }
    
    return prefs

@router.put("/preferences")
async def update_notification_preferences(prefs: NotificationPreferences, request: Request):
    """Update user's notification preferences"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user.get("user_id")
    
    await db.notification_preferences.update_one(
        {"user_id": user_id},
        {"$set": {
            **prefs.dict(),
            "user_id": user_id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    
    return {"message": "Preferences updated", "preferences": prefs.dict()}

@router.get("/history")
async def get_notification_history(request: Request, limit: int = 50, unread_only: bool = False):
    """Get user's notification history"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    query = {"user_id": user.get("user_id")}
    if unread_only:
        query["read"] = False
    
    notifications = await db.notification_history.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    # Get unread count
    unread_count = await db.notification_history.count_documents({
        "user_id": user.get("user_id"),
        "read": False
    })
    
    return {
        "notifications": notifications,
        "unread_count": unread_count,
        "total": len(notifications)
    }

@router.put("/mark-read/{notification_id}")
async def mark_notification_read(notification_id: str, request: Request):
    """Mark a notification as read"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.notification_history.update_one(
        {"notification_id": notification_id, "user_id": user.get("user_id")},
        {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Marked as read"}

@router.put("/mark-all-read")
async def mark_all_notifications_read(request: Request):
    """Mark all notifications as read"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.notification_history.update_many(
        {"user_id": user.get("user_id"), "read": False},
        {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": f"Marked {result.modified_count} notifications as read"}

@router.post("/send-test")
async def send_test_notification(request: Request):
    """Send a test notification to the current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Store test notification
    notification_id = await store_notification(
        user.get("user_id"),
        {
            "title": "Test Notification",
            "body": "This is a test notification from MedMatch!",
            "data": {"type": "test", "timestamp": datetime.now(timezone.utc).isoformat()}
        },
        status="sent"
    )
    
    return {
        "message": "Test notification sent",
        "notification_id": notification_id
    }

@router.get("/subscriptions")
async def get_user_push_subscriptions(request: Request):
    """Get user's active push subscriptions"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    subscriptions = await get_user_subscriptions(user.get("user_id"))
    
    return {
        "subscriptions": [
            {
                "subscription_id": s.get("subscription_id"),
                "user_agent": s.get("user_agent"),
                "created_at": s.get("created_at"),
                "active": s.get("active")
            }
            for s in subscriptions
        ],
        "total": len(subscriptions)
    }

# ============== Internal/Admin Routes ==============

@router.post("/internal/job-alert")
async def send_job_alert_notification(
    user_id: str,
    job_title: str,
    company: str,
    match_score: int,
    request: Request
):
    """Send job alert notification (internal use)"""
    # Store notification
    notification_id = await store_notification(
        user_id,
        {
            "title": f"New Job Match: {match_score}% Match!",
            "body": f"{job_title} at {company}",
            "data": {
                "type": "job_alert",
                "job_title": job_title,
                "company": company,
                "match_score": match_score
            }
        },
        status="queued"
    )
    
    return {"notification_id": notification_id, "status": "queued"}

@router.post("/internal/interview-reminder")
async def send_interview_reminder(
    user_id: str,
    interview_date: str,
    company: str,
    position: str,
    request: Request
):
    """Send interview reminder notification (internal use)"""
    notification_id = await store_notification(
        user_id,
        {
            "title": f"Interview Reminder: {company}",
            "body": f"Your interview for {position} is scheduled for {interview_date}",
            "data": {
                "type": "interview_reminder",
                "company": company,
                "position": position,
                "date": interview_date
            }
        },
        status="queued"
    )
    
    return {"notification_id": notification_id, "status": "queued"}
