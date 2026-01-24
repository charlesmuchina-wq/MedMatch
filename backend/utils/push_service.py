"""
Push Notification Service
Centralized service for triggering push notifications across the application
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from utils.database import db

logger = logging.getLogger(__name__)

# Import the send_to_user function from webpush
async def _get_send_to_user():
    """Lazy import to avoid circular dependencies"""
    from routes.webpush import send_to_user
    return send_to_user


async def check_user_notification_preference(user_id: str, notification_type: str) -> bool:
    """Check if user has enabled a specific notification type"""
    try:
        prefs = await db.notification_preferences.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        if not prefs:
            # Default: all notifications enabled
            return True
        
        return prefs.get("preferences", {}).get(notification_type, True)
    except Exception as e:
        logger.error(f"Error checking notification preferences: {e}")
        return True  # Default to sending


async def notify_job_match(
    user_id: str,
    job_title: str,
    company: str,
    match_score: int,
    job_id: Optional[str] = None
) -> Dict[str, Any]:
    """Send notification for new job match"""
    
    # Check user preference
    if not await check_user_notification_preference(user_id, "job_alerts"):
        return {"success": False, "reason": "User disabled job_alerts"}
    
    send_to_user = await _get_send_to_user()
    
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
    
    result = await send_to_user(user_id, payload)
    
    # Log notification
    await _log_notification(user_id, "job_match", payload, result)
    
    return result


async def notify_new_message(
    user_id: str,
    sender_name: str,
    preview: str,
    conversation_id: Optional[str] = None
) -> Dict[str, Any]:
    """Send notification for new message"""
    
    # Check user preference
    if not await check_user_notification_preference(user_id, "messages"):
        return {"success": False, "reason": "User disabled messages notifications"}
    
    send_to_user = await _get_send_to_user()
    
    payload = {
        "title": f"💬 New Message from {sender_name}",
        "body": preview[:100] if preview else "sent you a message",
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
    
    result = await send_to_user(user_id, payload)
    
    # Log notification
    await _log_notification(user_id, "message", payload, result)
    
    return result


async def notify_application_update(
    user_id: str,
    company: str,
    status: str,
    application_id: Optional[str] = None
) -> Dict[str, Any]:
    """Send notification for application status update"""
    
    # Check user preference
    if not await check_user_notification_preference(user_id, "application_updates"):
        return {"success": False, "reason": "User disabled application_updates"}
    
    send_to_user = await _get_send_to_user()
    
    # Emoji based on status
    emoji_map = {
        "viewed": "👀",
        "shortlisted": "⭐",
        "interview": "📅",
        "offer": "🎉",
        "rejected": "😔",
        "pending": "⏳"
    }
    emoji = emoji_map.get(status.lower(), "📋")
    
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
    
    result = await send_to_user(user_id, payload)
    
    # Log notification
    await _log_notification(user_id, "application_update", payload, result)
    
    return result


async def notify_interview_reminder(
    user_id: str,
    company: str,
    position: str,
    interview_time: str,
    interview_id: Optional[str] = None
) -> Dict[str, Any]:
    """Send notification for upcoming interview"""
    
    # Check user preference
    if not await check_user_notification_preference(user_id, "interview_reminders"):
        return {"success": False, "reason": "User disabled interview_reminders"}
    
    send_to_user = await _get_send_to_user()
    
    payload = {
        "title": "📅 Interview Reminder",
        "body": f"{position} at {company} - {interview_time}",
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
    
    result = await send_to_user(user_id, payload)
    
    # Log notification
    await _log_notification(user_id, "interview_reminder", payload, result)
    
    return result


async def notify_recruiter_new_applicant(
    recruiter_user_id: str,
    applicant_name: str,
    job_title: str,
    application_id: Optional[str] = None
) -> Dict[str, Any]:
    """Notify recruiter of new job application"""
    
    send_to_user = await _get_send_to_user()
    
    payload = {
        "title": "📥 New Application Received",
        "body": f"{applicant_name} applied for {job_title}",
        "icon": "/logo192.png",
        "badge": "/badge-icon.png",
        "tag": f"applicant-{application_id}" if application_id else "applicant",
        "data": {
            "type": "new_applicant",
            "application_id": application_id,
            "url": f"/recruiter/applications/{application_id}" if application_id else "/recruiter/applications"
        },
        "actions": [
            {"action": "review", "title": "Review"},
            {"action": "dismiss", "title": "Later"}
        ]
    }
    
    result = await send_to_user(recruiter_user_id, payload)
    
    # Log notification
    await _log_notification(recruiter_user_id, "new_applicant", payload, result)
    
    return result


async def _log_notification(
    user_id: str,
    notification_type: str,
    payload: Dict,
    result: Dict
) -> None:
    """Log notification for analytics"""
    try:
        await db.notification_logs.insert_one({
            "user_id": user_id,
            "type": notification_type,
            "title": payload.get("title", ""),
            "body": payload.get("body", ""),
            "success": result.get("success", False),
            "sent_count": result.get("sent", 0),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to log notification: {e}")
