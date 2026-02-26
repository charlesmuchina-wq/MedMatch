"""
Notifications API Routes
Handles in-app notifications, preferences, and smart job alerts.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone

from routes.auth import get_current_user, require_auth
from services.smart_notifications import get_notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationPreferences(BaseModel):
    job_matches: bool = True
    job_alerts: bool = True
    application_updates: bool = True
    interview_reminders: bool = True
    weekly_digest: bool = True
    profile_tips: bool = True
    match_threshold: int = 85
    push_enabled: bool = True
    email_enabled: bool = True
    quiet_hours: Optional[Dict] = None


# ============== Notification Endpoints ==============

@router.get("")
async def get_notifications(
    request: Request,
    unread_only: bool = False,
    limit: int = 50
):
    """Get user's notifications"""
    user = await require_auth(request)
    
    service = get_notification_service()
    notifications = await service.get_user_notifications(
        user_id=user["user_id"],
        unread_only=unread_only,
        limit=limit
    )
    
    unread_count = await service.get_unread_count(user["user_id"])
    
    return {
        "notifications": notifications,
        "unread_count": unread_count,
        "total": len(notifications)
    }


@router.get("/unread-count")
async def get_unread_count(request: Request):
    """Get unread notification count"""
    user = await require_auth(request)
    
    service = get_notification_service()
    count = await service.get_unread_count(user["user_id"])
    
    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_notification_read(notification_id: str, request: Request):
    """Mark a notification as read"""
    user = await require_auth(request)
    
    service = get_notification_service()
    success = await service.mark_as_read(notification_id, user["user_id"])
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}


@router.post("/read-all")
async def mark_all_read(request: Request):
    """Mark all notifications as read"""
    user = await require_auth(request)
    
    service = get_notification_service()
    count = await service.mark_all_as_read(user["user_id"])
    
    return {"message": f"Marked {count} notifications as read", "count": count}


@router.delete("/{notification_id}")
async def delete_notification(notification_id: str, request: Request):
    """Delete a notification"""
    user = await require_auth(request)
    
    service = get_notification_service()
    success = await service.delete_notification(notification_id, user["user_id"])
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification deleted"}


# ============== Preferences Endpoints ==============

@router.get("/preferences")
async def get_notification_preferences(request: Request):
    """Get user's notification preferences"""
    user = await require_auth(request)
    
    service = get_notification_service()
    preferences = await service.get_notification_preferences(user["user_id"])
    
    return preferences


@router.put("/preferences")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    request: Request
):
    """Update user's notification preferences"""
    user = await require_auth(request)
    
    service = get_notification_service()
    success = await service.update_notification_preferences(
        user["user_id"],
        preferences.model_dump()
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update preferences")
    
    return {"message": "Preferences updated", "preferences": preferences.model_dump()}


# ============== Test Endpoint ==============

@router.post("/test")
async def send_test_notification(request: Request):
    """Send a test notification (for development)"""
    user = await require_auth(request)
    
    service = get_notification_service()
    notification = await service.create_notification(
        user_id=user["user_id"],
        notification_type="profile_tip",
        title="🔔 Test Notification",
        message="This is a test notification to verify the system is working.",
        data={"test": True},
        priority="medium",
        action_url="/dashboard"
    )
    
    if not notification:
        raise HTTPException(status_code=500, detail="Failed to create notification")
    
    return notification
