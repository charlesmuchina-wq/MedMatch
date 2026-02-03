"""
Production Metrics Collector
Tracks user engagement, business metrics, and performance for analytics and ML.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
from enum import Enum

from utils.database import db
from services.ml_data_collector import ml_collector, EventType, EventSeverity

logger = logging.getLogger(__name__)


class MetricCategory(str, Enum):
    USER_ENGAGEMENT = "user_engagement"
    BUSINESS = "business"
    PERFORMANCE = "performance"
    AI_USAGE = "ai_usage"
    CONVERSION = "conversion"


class ProductionMetrics:
    """
    Comprehensive production metrics tracking for MedMatch.
    Tracks user engagement, business metrics, AI usage, and conversions.
    """
    
    def __init__(self):
        self.session_cache: Dict[str, Dict] = {}  # Active sessions
    
    # ============== User Engagement Metrics ==============
    
    async def track_session_start(
        self,
        user_id: str,
        session_id: str,
        device_type: str = "web",
        referrer: Optional[str] = None
    ):
        """Track when a user starts a session"""
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "started_at": datetime.now(timezone.utc),
            "device_type": device_type,
            "referrer": referrer,
            "page_views": 0,
            "actions": [],
            "ended_at": None
        }
        
        self.session_cache[session_id] = session_data
        
        await db.user_sessions.insert_one({
            **session_data,
            "started_at": session_data["started_at"].isoformat()
        })
        
        await ml_collector.log_user_action(
            action=EventType.USER_LOGIN,
            user_id=user_id,
            session_id=session_id,
            data={
                "device_type": device_type,
                "referrer": referrer,
                "metric_type": MetricCategory.USER_ENGAGEMENT.value
            }
        )
    
    async def track_page_view(
        self,
        user_id: str,
        session_id: str,
        page_path: str,
        page_title: Optional[str] = None,
        time_on_page_ms: Optional[int] = None
    ):
        """Track page views"""
        await db.page_views.insert_one({
            "user_id": user_id,
            "session_id": session_id,
            "page_path": page_path,
            "page_title": page_title,
            "time_on_page_ms": time_on_page_ms,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Update session cache
        if session_id in self.session_cache:
            self.session_cache[session_id]["page_views"] += 1
    
    async def track_feature_usage(
        self,
        user_id: str,
        feature_name: str,
        feature_category: str,
        duration_ms: Optional[int] = None,
        success: bool = True,
        metadata: Optional[Dict] = None
    ):
        """Track feature usage (e.g., AI tools, resume parser)"""
        await db.feature_usage.insert_one({
            "user_id": user_id,
            "feature_name": feature_name,
            "feature_category": feature_category,
            "duration_ms": duration_ms,
            "success": success,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        await ml_collector.log_event(
            event_type=EventType.AI_INTERACTION if "ai" in feature_category.lower() else EventType.SYSTEM_INFO,
            severity=EventSeverity.INFO,
            message=f"Feature used: {feature_name}",
            user_id=user_id,
            data={
                "feature_name": feature_name,
                "category": feature_category,
                "success": success,
                "metric_type": MetricCategory.USER_ENGAGEMENT.value
            }
        )
    
    async def track_session_end(self, session_id: str):
        """Track when a user ends a session"""
        if session_id in self.session_cache:
            session = self.session_cache[session_id]
            ended_at = datetime.now(timezone.utc)
            duration = (ended_at - session["started_at"]).total_seconds()
            
            await db.user_sessions.update_one(
                {"session_id": session_id},
                {"$set": {
                    "ended_at": ended_at.isoformat(),
                    "duration_seconds": duration,
                    "page_views": session["page_views"]
                }}
            )
            
            del self.session_cache[session_id]
    
    # ============== Business Metrics ==============
    
    async def track_job_application(
        self,
        user_id: str,
        job_id: str,
        job_title: str,
        company: str,
        source: str,
        application_method: str = "direct",
        used_ai_cover_letter: bool = False
    ):
        """Track job applications"""
        await db.application_metrics.insert_one({
            "user_id": user_id,
            "job_id": job_id,
            "job_title": job_title,
            "company": company,
            "source": source,
            "application_method": application_method,
            "used_ai_cover_letter": used_ai_cover_letter,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        await ml_collector.log_user_action(
            action=EventType.JOB_APPLICATION,
            user_id=user_id,
            data={
                "job_id": job_id,
                "company": company,
                "source": source,
                "used_ai": used_ai_cover_letter,
                "metric_type": MetricCategory.BUSINESS.value
            }
        )
    
    async def track_resume_upload(
        self,
        user_id: str,
        file_type: str,
        file_size_kb: int,
        parse_success: bool,
        skills_extracted: int = 0,
        experience_years: Optional[float] = None
    ):
        """Track resume uploads and parsing"""
        await db.resume_metrics.insert_one({
            "user_id": user_id,
            "file_type": file_type,
            "file_size_kb": file_size_kb,
            "parse_success": parse_success,
            "skills_extracted": skills_extracted,
            "experience_years": experience_years,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        await ml_collector.log_user_action(
            action=EventType.RESUME_UPLOAD,
            user_id=user_id,
            data={
                "file_type": file_type,
                "parse_success": parse_success,
                "skills_count": skills_extracted,
                "metric_type": MetricCategory.BUSINESS.value
            }
        )
    
    async def track_subscription_event(
        self,
        user_id: str,
        event_type: str,  # "signup", "upgrade", "downgrade", "cancel", "renew"
        plan_name: str,
        plan_price: float,
        currency: str = "USD",
        previous_plan: Optional[str] = None
    ):
        """Track subscription events"""
        await db.subscription_metrics.insert_one({
            "user_id": user_id,
            "event_type": event_type,
            "plan_name": plan_name,
            "plan_price": plan_price,
            "currency": currency,
            "previous_plan": previous_plan,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        await ml_collector.log_event(
            event_type=EventType.PAYMENT_EVENT,
            severity=EventSeverity.INFO,
            message=f"Subscription: {event_type}",
            user_id=user_id,
            data={
                "event_type": event_type,
                "plan": plan_name,
                "price": plan_price,
                "metric_type": MetricCategory.BUSINESS.value
            }
        )
    
    # ============== AI Usage Metrics ==============
    
    async def track_ai_tool_usage(
        self,
        user_id: str,
        tool_name: str,  # "cover_letter", "interview_prep", "voice_coach", "dragon_ai"
        input_type: str,
        output_quality_score: Optional[float] = None,
        tokens_used: int = 0,
        response_time_ms: int = 0,
        user_feedback: Optional[str] = None  # "positive", "negative", "neutral"
    ):
        """Track AI tool usage and effectiveness"""
        await db.ai_usage_metrics.insert_one({
            "user_id": user_id,
            "tool_name": tool_name,
            "input_type": input_type,
            "output_quality_score": output_quality_score,
            "tokens_used": tokens_used,
            "response_time_ms": response_time_ms,
            "user_feedback": user_feedback,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        await ml_collector.log_ai_interaction(
            ai_type=tool_name,
            user_id=user_id,
            input_summary=f"Input type: {input_type}",
            output_summary=f"Quality: {output_quality_score}, Feedback: {user_feedback}",
            tokens_used=tokens_used,
            response_time_ms=response_time_ms,
            success=output_quality_score is None or output_quality_score >= 0.5
        )
    
    # ============== Conversion Metrics ==============
    
    async def track_conversion_event(
        self,
        user_id: str,
        conversion_type: str,  # "signup", "first_application", "first_interview", "subscription"
        source: str,
        campaign: Optional[str] = None,
        value: Optional[float] = None
    ):
        """Track conversion events for funnel analysis"""
        await db.conversion_metrics.insert_one({
            "user_id": user_id,
            "conversion_type": conversion_type,
            "source": source,
            "campaign": campaign,
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        await ml_collector.log_event(
            event_type=EventType.SYSTEM_INFO,
            severity=EventSeverity.INFO,
            message=f"Conversion: {conversion_type}",
            user_id=user_id,
            data={
                "conversion_type": conversion_type,
                "source": source,
                "campaign": campaign,
                "value": value,
                "metric_type": MetricCategory.CONVERSION.value
            }
        )
    
    # ============== Analytics Queries ==============
    
    async def get_engagement_summary(self, days: int = 7) -> Dict:
        """Get user engagement summary"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        # Active users
        active_users = await db.user_sessions.distinct(
            "user_id",
            {"started_at": {"$gte": cutoff_str}}
        )
        
        # Total sessions
        total_sessions = await db.user_sessions.count_documents(
            {"started_at": {"$gte": cutoff_str}}
        )
        
        # Total page views
        total_page_views = await db.page_views.count_documents(
            {"timestamp": {"$gte": cutoff_str}}
        )
        
        # Feature usage
        feature_pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_str}}},
            {"$group": {
                "_id": "$feature_name",
                "count": {"$sum": 1},
                "success_rate": {"$avg": {"$cond": ["$success", 1, 0]}}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_features = await db.feature_usage.aggregate(feature_pipeline).to_list(10)
        
        return {
            "period_days": days,
            "active_users": len(active_users),
            "total_sessions": total_sessions,
            "total_page_views": total_page_views,
            "avg_sessions_per_user": total_sessions / max(len(active_users), 1),
            "top_features": top_features
        }
    
    async def get_business_summary(self, days: int = 7) -> Dict:
        """Get business metrics summary"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        # Applications
        total_applications = await db.application_metrics.count_documents(
            {"timestamp": {"$gte": cutoff_str}}
        )
        
        ai_assisted_apps = await db.application_metrics.count_documents(
            {"timestamp": {"$gte": cutoff_str}, "used_ai_cover_letter": True}
        )
        
        # Resumes
        total_resumes = await db.resume_metrics.count_documents(
            {"timestamp": {"$gte": cutoff_str}}
        )
        
        successful_parses = await db.resume_metrics.count_documents(
            {"timestamp": {"$gte": cutoff_str}, "parse_success": True}
        )
        
        # Subscriptions
        subscription_pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_str}}},
            {"$group": {
                "_id": "$event_type",
                "count": {"$sum": 1},
                "total_value": {"$sum": "$plan_price"}
            }}
        ]
        subscription_events = await db.subscription_metrics.aggregate(subscription_pipeline).to_list(10)
        
        return {
            "period_days": days,
            "total_applications": total_applications,
            "ai_assisted_applications": ai_assisted_apps,
            "ai_assist_rate": ai_assisted_apps / max(total_applications, 1) * 100,
            "total_resumes": total_resumes,
            "parse_success_rate": successful_parses / max(total_resumes, 1) * 100,
            "subscription_events": subscription_events
        }
    
    async def get_ai_usage_summary(self, days: int = 7) -> Dict:
        """Get AI tool usage summary"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_str}}},
            {"$group": {
                "_id": "$tool_name",
                "total_uses": {"$sum": 1},
                "total_tokens": {"$sum": "$tokens_used"},
                "avg_response_time": {"$avg": "$response_time_ms"},
                "positive_feedback": {
                    "$sum": {"$cond": [{"$eq": ["$user_feedback", "positive"]}, 1, 0]}
                },
                "negative_feedback": {
                    "$sum": {"$cond": [{"$eq": ["$user_feedback", "negative"]}, 1, 0]}
                }
            }},
            {"$sort": {"total_uses": -1}}
        ]
        
        ai_tools = await db.ai_usage_metrics.aggregate(pipeline).to_list(20)
        
        total_uses = sum(t.get("total_uses", 0) for t in ai_tools)
        total_tokens = sum(t.get("total_tokens", 0) for t in ai_tools)
        
        return {
            "period_days": days,
            "total_ai_uses": total_uses,
            "total_tokens_used": total_tokens,
            "tools_breakdown": ai_tools
        }
    
    async def get_conversion_funnel(self, days: int = 30) -> Dict:
        """Get conversion funnel data"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_str}}},
            {"$group": {
                "_id": "$conversion_type",
                "count": {"$sum": 1},
                "total_value": {"$sum": {"$ifNull": ["$value", 0]}}
            }},
            {"$sort": {"count": -1}}
        ]
        
        conversions = await db.conversion_metrics.aggregate(pipeline).to_list(20)
        
        # Define funnel stages
        funnel_stages = ["signup", "resume_upload", "first_search", "first_application", "first_interview", "subscription"]
        
        funnel_data = []
        for stage in funnel_stages:
            stage_data = next((c for c in conversions if c["_id"] == stage), {"count": 0, "total_value": 0})
            funnel_data.append({
                "stage": stage,
                "count": stage_data.get("count", 0),
                "value": stage_data.get("total_value", 0)
            })
        
        return {
            "period_days": days,
            "funnel": funnel_data,
            "all_conversions": conversions
        }


# Global instance
production_metrics = ProductionMetrics()


# Export
__all__ = ['ProductionMetrics', 'production_metrics', 'MetricCategory']
