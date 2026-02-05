"""
Smart Job Notifications Service
Sends targeted notifications for new jobs that match user profiles.

Features:
- Match-based alerts (only notify when match score > 85%)
- In-app notification center
- Browser push notifications
- Email digest (daily/weekly)
- Real-time job posting detection
"""
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
import uuid

from utils.database import db

logger = logging.getLogger(__name__)

# Notification types
NOTIFICATION_TYPES = {
    "new_job_match": {
        "title": "New Job Match!",
        "icon": "briefcase",
        "priority": "high"
    },
    "job_alert": {
        "title": "Job Alert",
        "icon": "bell",
        "priority": "medium"
    },
    "application_update": {
        "title": "Application Update",
        "icon": "file-text",
        "priority": "high"
    },
    "interview_reminder": {
        "title": "Interview Reminder",
        "icon": "calendar",
        "priority": "urgent"
    },
    "weekly_digest": {
        "title": "Weekly Job Digest",
        "icon": "mail",
        "priority": "low"
    },
    "profile_tip": {
        "title": "Profile Tip",
        "icon": "lightbulb",
        "priority": "low"
    }
}

# Match score threshold for notifications
DEFAULT_MATCH_THRESHOLD = 85


class SmartNotificationService:
    """
    Service to manage smart job notifications.
    """
    
    def __init__(self):
        self.match_threshold = DEFAULT_MATCH_THRESHOLD
    
    async def create_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Dict = None,
        priority: str = "medium",
        action_url: str = None
    ) -> Dict:
        """
        Create a new notification for a user.
        """
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "data": data or {},
            "priority": priority,
            "action_url": action_url,
            "is_read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            await db.notifications.insert_one(notification)
            notification.pop("_id", None)
            
            # Update unread count
            await self._update_unread_count(user_id)
            
            logger.info(f"Created notification for user {user_id}: {title}")
            return notification
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            return None
    
    async def _update_unread_count(self, user_id: str):
        """Update the user's unread notification count"""
        try:
            count = await db.notifications.count_documents({
                "user_id": user_id,
                "is_read": False
            })
            
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {"unread_notifications": count}}
            )
        except Exception as e:
            logger.error(f"Failed to update unread count: {e}")
    
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict]:
        """Get notifications for a user"""
        try:
            query = {"user_id": user_id}
            if unread_only:
                query["is_read"] = False
            
            notifications = await db.notifications.find(
                query,
                {"_id": 0}
            ).sort("created_at", -1).limit(limit).to_list(limit)
            
            return notifications
        except Exception as e:
            logger.error(f"Failed to get notifications: {e}")
            return []
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read"""
        try:
            result = await db.notifications.update_one(
                {"id": notification_id, "user_id": user_id},
                {"$set": {"is_read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            if result.modified_count > 0:
                await self._update_unread_count(user_id)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {e}")
            return False
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        try:
            result = await db.notifications.update_many(
                {"user_id": user_id, "is_read": False},
                {"$set": {"is_read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            await self._update_unread_count(user_id)
            return result.modified_count
        except Exception as e:
            logger.error(f"Failed to mark all as read: {e}")
            return 0
    
    async def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        try:
            result = await db.notifications.delete_one({
                "id": notification_id,
                "user_id": user_id
            })
            
            if result.deleted_count > 0:
                await self._update_unread_count(user_id)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete notification: {e}")
            return False
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get unread notification count"""
        try:
            count = await db.notifications.count_documents({
                "user_id": user_id,
                "is_read": False
            })
            return count
        except Exception as e:
            logger.error(f"Failed to get unread count: {e}")
            return 0
    
    async def notify_job_match(
        self,
        user_id: str,
        job: Dict,
        match_score: int
    ) -> Optional[Dict]:
        """
        Send notification for a high-match job.
        Only sends if match_score >= threshold.
        """
        if match_score < self.match_threshold:
            return None
        
        # Calculate freshness badge
        freshness = job.get("freshness", {})
        freshness_badge = freshness.get("badge", "Recently posted")
        
        title = f"🎯 {match_score}% Match Found!"
        message = f"{job.get('title', 'New Job')} at {job.get('company', 'Unknown')} - {freshness_badge}"
        
        return await self.create_notification(
            user_id=user_id,
            notification_type="new_job_match",
            title=title,
            message=message,
            data={
                "job_id": job.get("id"),
                "job_title": job.get("title"),
                "company": job.get("company"),
                "match_score": match_score,
                "freshness": freshness_badge,
                "source": job.get("source")
            },
            priority="high",
            action_url=f"/jobs?highlight={job.get('id')}"
        )
    
    async def check_and_notify_matches(
        self,
        user_id: str,
        jobs: List[Dict],
        user_profile: Dict
    ) -> List[Dict]:
        """
        Check a list of jobs against user profile and send notifications
        for high matches.
        """
        notifications_sent = []
        
        # Get user's notification preferences
        user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
        if not user:
            return []
        
        # Check if user has job notifications enabled
        preferences = user.get("notification_preferences", {})
        if not preferences.get("job_matches", True):
            return []
        
        # Get match threshold from preferences or use default
        threshold = preferences.get("match_threshold", self.match_threshold)
        
        for job in jobs:
            match_score = job.get("match_score", 0)
            
            if match_score >= threshold:
                # Check if we already notified about this job
                existing = await db.notifications.find_one({
                    "user_id": user_id,
                    "data.job_id": job.get("id")
                })
                
                if not existing:
                    notification = await self.notify_job_match(user_id, job, match_score)
                    if notification:
                        notifications_sent.append(notification)
        
        return notifications_sent
    
    async def get_notification_preferences(self, user_id: str) -> Dict:
        """Get user's notification preferences"""
        try:
            user = await db.users.find_one(
                {"user_id": user_id},
                {"_id": 0, "notification_preferences": 1}
            )
            
            # Default preferences
            defaults = {
                "job_matches": True,
                "job_alerts": True,
                "application_updates": True,
                "interview_reminders": True,
                "weekly_digest": True,
                "profile_tips": True,
                "match_threshold": DEFAULT_MATCH_THRESHOLD,
                "push_enabled": True,
                "email_enabled": True,
                "quiet_hours": {
                    "enabled": False,
                    "start": "22:00",
                    "end": "08:00"
                }
            }
            
            if user and user.get("notification_preferences"):
                return {**defaults, **user["notification_preferences"]}
            
            return defaults
        except Exception as e:
            logger.error(f"Failed to get preferences: {e}")
            return {}
    
    async def update_notification_preferences(
        self,
        user_id: str,
        preferences: Dict
    ) -> bool:
        """Update user's notification preferences"""
        try:
            result = await db.users.update_one(
                {"user_id": user_id},
                {"$set": {"notification_preferences": preferences}},
                upsert=False
            )
            # Return True if matched (even if not modified - same data)
            return result.matched_count > 0 or result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update preferences: {e}")
            return False
    
    async def send_application_update(
        self,
        user_id: str,
        application_id: str,
        status: str,
        company: str,
        job_title: str
    ) -> Optional[Dict]:
        """Send notification for application status update"""
        status_messages = {
            "viewed": f"Your application for {job_title} at {company} was viewed",
            "shortlisted": f"Great news! You've been shortlisted for {job_title} at {company}",
            "interview": f"Interview scheduled for {job_title} at {company}",
            "rejected": f"Update on your application for {job_title} at {company}",
            "offer": f"Congratulations! You have an offer for {job_title} at {company}"
        }
        
        message = status_messages.get(status, f"Update on {job_title} at {company}: {status}")
        
        return await self.create_notification(
            user_id=user_id,
            notification_type="application_update",
            title="Application Update",
            message=message,
            data={
                "application_id": application_id,
                "status": status,
                "company": company,
                "job_title": job_title
            },
            priority="high",
            action_url=f"/applications?id={application_id}"
        )
    
    async def send_interview_reminder(
        self,
        user_id: str,
        interview_id: str,
        company: str,
        job_title: str,
        scheduled_time: str,
        minutes_before: int = 30
    ) -> Optional[Dict]:
        """Send interview reminder notification"""
        message = f"Interview for {job_title} at {company} in {minutes_before} minutes"
        
        return await self.create_notification(
            user_id=user_id,
            notification_type="interview_reminder",
            title=f"⏰ Interview in {minutes_before} min",
            message=message,
            data={
                "interview_id": interview_id,
                "company": company,
                "job_title": job_title,
                "scheduled_time": scheduled_time
            },
            priority="urgent",
            action_url=f"/interviews?id={interview_id}"
        )
    
    async def generate_weekly_digest(self, user_id: str) -> Optional[Dict]:
        """Generate and send weekly job digest"""
        try:
            # Get user's saved searches and preferences
            user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
            if not user:
                return None
            
            # Get job stats from the past week
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            
            # Count new applications
            new_apps = await db.applications.count_documents({
                "user_id": user_id,
                "applied_at": {"$gte": week_ago.isoformat()}
            })
            
            # Count saved jobs
            saved_jobs = await db.saved_jobs.count_documents({
                "user_id": user_id,
                "saved_at": {"$gte": week_ago.isoformat()}
            })
            
            message = f"This week: {new_apps} applications submitted, {saved_jobs} jobs saved"
            
            return await self.create_notification(
                user_id=user_id,
                notification_type="weekly_digest",
                title="📊 Your Weekly Job Search Summary",
                message=message,
                data={
                    "applications_count": new_apps,
                    "saved_jobs_count": saved_jobs,
                    "period": "weekly"
                },
                priority="low",
                action_url="/analytics-funnel"
            )
        except Exception as e:
            logger.error(f"Failed to generate digest: {e}")
            return None
    
    async def cleanup_old_notifications(self, days_old: int = 30) -> int:
        """Remove notifications older than X days"""
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days_old)
            result = await db.notifications.delete_many({
                "created_at": {"$lt": cutoff.isoformat()},
                "is_read": True  # Only delete read notifications
            })
            return result.deleted_count
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return 0


# Singleton instance
_notification_service = None

def get_notification_service() -> SmartNotificationService:
    global _notification_service
    if _notification_service is None:
        _notification_service = SmartNotificationService()
    return _notification_service
