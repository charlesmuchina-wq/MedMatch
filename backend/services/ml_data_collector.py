"""
ML Training Data Collector Service
Collects system events, errors, and user actions for future ML model training.
Data is stored in MongoDB for predictive issue detection and system optimization.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorClient
import os
import traceback
import psutil

logger = logging.getLogger(__name__)

# Event types for categorization
class EventType(str, Enum):
    # System events
    SYSTEM_ERROR = "system_error"
    SYSTEM_WARNING = "system_warning"
    SYSTEM_INFO = "system_info"
    PERFORMANCE_METRIC = "performance_metric"
    DATABASE_OPERATION = "database_operation"
    API_CALL = "api_call"
    SCHEDULER_EVENT = "scheduler_event"
    
    # User actions
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTRATION = "user_registration"
    JOB_SEARCH = "job_search"
    JOB_APPLICATION = "job_application"
    RESUME_UPLOAD = "resume_upload"
    RESUME_PARSE = "resume_parse"
    AI_INTERACTION = "ai_interaction"
    COVER_LETTER_GENERATION = "cover_letter_generation"
    INTERVIEW_PREP = "interview_prep"
    VOICE_COACHING = "voice_coaching"
    VIDEO_INTERVIEW = "video_interview"
    MESSAGE_SENT = "message_sent"
    NOTIFICATION_SENT = "notification_sent"
    PAYMENT_EVENT = "payment_event"
    
    # Diagnostic events
    HEALTH_CHECK = "health_check"
    AUTO_FIX = "auto_fix"
    MAINTENANCE = "maintenance"
    VERSION_RELEASE = "version_release"


class EventSeverity(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MLDataCollector:
    """
    Singleton service for collecting ML training data.
    Collects events asynchronously to avoid blocking the main thread.
    """
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.db = None
            self.collection = None
            self.buffer: List[Dict] = []
            self.buffer_size = 50  # Flush after 50 events
            self.flush_interval = 30  # Flush every 30 seconds
            self._flush_task = None
            self._running = False
            MLDataCollector._initialized = True
    
    async def initialize(self, mongo_url: str = None, db_name: str = None):
        """Initialize MongoDB connection"""
        try:
            mongo_url = mongo_url or os.environ.get('MONGO_URL')
            db_name = db_name or os.environ.get('DB_NAME', 'medmatch')
            
            client = AsyncIOMotorClient(mongo_url)
            self.db = client[db_name]
            self.collection = self.db['ml_training_data']
            
            # Create indexes for efficient querying
            await self.collection.create_index([("timestamp", -1)])
            await self.collection.create_index([("event_type", 1)])
            await self.collection.create_index([("severity", 1)])
            await self.collection.create_index([("user_id", 1)])
            await self.collection.create_index([("session_id", 1)])
            
            # Start background flush task
            self._running = True
            self._flush_task = asyncio.create_task(self._periodic_flush())
            
            logger.info("ML Data Collector initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize ML Data Collector: {e}")
            return False
    
    async def shutdown(self):
        """Graceful shutdown - flush remaining events"""
        self._running = False
        if self._flush_task:
            self._flush_task.cancel()
        await self._flush_buffer()
        logger.info("ML Data Collector shut down")
    
    async def _periodic_flush(self):
        """Periodically flush buffer to database"""
        while self._running:
            await asyncio.sleep(self.flush_interval)
            await self._flush_buffer()
    
    async def _flush_buffer(self):
        """Flush buffered events to MongoDB"""
        if not self.buffer or not self.collection:
            return
        
        events_to_insert = self.buffer.copy()
        self.buffer.clear()
        
        try:
            await self.collection.insert_many(events_to_insert)
            logger.debug(f"Flushed {len(events_to_insert)} events to ML training collection")
        except Exception as e:
            logger.error(f"Failed to flush ML data: {e}")
            # Re-add events to buffer on failure
            self.buffer.extend(events_to_insert)
    
    def _create_event(
        self,
        event_type: EventType,
        severity: EventSeverity,
        message: str,
        data: Optional[Dict] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_path: Optional[str] = None,
        response_time_ms: Optional[float] = None,
        error_trace: Optional[str] = None
    ) -> Dict:
        """Create a standardized event document"""
        # Get system metrics
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
        
        return {
            "timestamp": datetime.now(timezone.utc),
            "event_type": event_type.value,
            "severity": severity.value,
            "message": message,
            "data": data or {},
            "user_id": user_id,
            "session_id": session_id,
            "request_path": request_path,
            "response_time_ms": response_time_ms,
            "error_trace": error_trace,
            "system_metrics": system_metrics,
            "environment": os.environ.get("ENVIRONMENT", "development")
        }
    
    async def log_event(
        self,
        event_type: EventType,
        severity: EventSeverity,
        message: str,
        data: Optional[Dict] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_path: Optional[str] = None,
        response_time_ms: Optional[float] = None,
        error_trace: Optional[str] = None
    ):
        """Log an event to the ML training data collection"""
        event = self._create_event(
            event_type=event_type,
            severity=severity,
            message=message,
            data=data,
            user_id=user_id,
            session_id=session_id,
            request_path=request_path,
            response_time_ms=response_time_ms,
            error_trace=error_trace
        )
        
        self.buffer.append(event)
        
        # Flush if buffer is full
        if len(self.buffer) >= self.buffer_size:
            await self._flush_buffer()
    
    # Convenience methods for common events
    
    async def log_system_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        data: Optional[Dict] = None,
        request_path: Optional[str] = None
    ):
        """Log a system error"""
        error_trace = traceback.format_exc() if error else None
        await self.log_event(
            event_type=EventType.SYSTEM_ERROR,
            severity=EventSeverity.ERROR,
            message=message,
            data=data,
            error_trace=error_trace,
            request_path=request_path
        )
    
    async def log_api_call(
        self,
        path: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        user_id: Optional[str] = None,
        data: Optional[Dict] = None
    ):
        """Log an API call for performance tracking"""
        severity = EventSeverity.INFO if status_code < 400 else EventSeverity.WARNING
        if status_code >= 500:
            severity = EventSeverity.ERROR
            
        await self.log_event(
            event_type=EventType.API_CALL,
            severity=severity,
            message=f"{method} {path} -> {status_code}",
            data={
                "method": method,
                "status_code": status_code,
                **(data or {})
            },
            user_id=user_id,
            request_path=path,
            response_time_ms=response_time_ms
        )
    
    async def log_user_action(
        self,
        action: EventType,
        user_id: str,
        data: Optional[Dict] = None,
        session_id: Optional[str] = None
    ):
        """Log a user action for behavioral analysis"""
        await self.log_event(
            event_type=action,
            severity=EventSeverity.INFO,
            message=f"User action: {action.value}",
            data=data,
            user_id=user_id,
            session_id=session_id
        )
    
    async def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "",
        data: Optional[Dict] = None
    ):
        """Log a performance metric"""
        await self.log_event(
            event_type=EventType.PERFORMANCE_METRIC,
            severity=EventSeverity.INFO,
            message=f"Performance: {metric_name} = {value}{unit}",
            data={
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                **(data or {})
            }
        )
    
    async def log_ai_interaction(
        self,
        ai_type: str,
        user_id: str,
        input_summary: str,
        output_summary: str,
        tokens_used: Optional[int] = None,
        response_time_ms: Optional[float] = None,
        success: bool = True
    ):
        """Log an AI interaction for model improvement"""
        await self.log_event(
            event_type=EventType.AI_INTERACTION,
            severity=EventSeverity.INFO if success else EventSeverity.WARNING,
            message=f"AI interaction: {ai_type}",
            data={
                "ai_type": ai_type,
                "input_summary": input_summary[:500],  # Truncate for storage
                "output_summary": output_summary[:500],
                "tokens_used": tokens_used,
                "success": success
            },
            user_id=user_id,
            response_time_ms=response_time_ms
        )
    
    async def log_job_search(
        self,
        user_id: str,
        query: str,
        filters: Dict,
        results_count: int,
        response_time_ms: float
    ):
        """Log a job search for search optimization"""
        await self.log_event(
            event_type=EventType.JOB_SEARCH,
            severity=EventSeverity.INFO,
            message=f"Job search: {query}",
            data={
                "query": query,
                "filters": filters,
                "results_count": results_count
            },
            user_id=user_id,
            response_time_ms=response_time_ms
        )
    
    async def log_maintenance_event(
        self,
        action: str,
        details: Dict,
        success: bool = True
    ):
        """Log a maintenance/diagnostic event"""
        await self.log_event(
            event_type=EventType.MAINTENANCE,
            severity=EventSeverity.INFO if success else EventSeverity.WARNING,
            message=f"Maintenance: {action}",
            data={
                "action": action,
                "details": details,
                "success": success
            }
        )
    
    # Query methods for analysis
    
    async def get_recent_errors(
        self,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict]:
        """Get recent errors for analysis"""
        if self.collection is None:
            return []
        
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        cursor = self.collection.find(
            {
                "severity": {"$in": ["error", "critical"]},
                "timestamp": {"$gte": cutoff}
            },
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def get_event_stats(
        self,
        hours: int = 24
    ) -> Dict:
        """Get event statistics for the given time period"""
        if self.collection is None:
            return {}
        
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff}}},
            {"$group": {
                "_id": {
                    "event_type": "$event_type",
                    "severity": "$severity"
                },
                "count": {"$sum": 1},
                "avg_response_time": {"$avg": "$response_time_ms"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=100)
        
        return {
            "time_period_hours": hours,
            "event_breakdown": results,
            "total_events": sum(r["count"] for r in results)
        }
    
    async def get_user_activity_pattern(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """Get user activity pattern for personalization"""
        if self.collection is None:
            return {}
        
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        pipeline = [
            {"$match": {
                "user_id": user_id,
                "timestamp": {"$gte": cutoff}
            }},
            {"$group": {
                "_id": "$event_type",
                "count": {"$sum": 1},
                "last_occurrence": {"$max": "$timestamp"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=50)
        
        return {
            "user_id": user_id,
            "days_analyzed": days,
            "activity_breakdown": results
        }
    
    async def get_training_data_export(
        self,
        event_types: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10000
    ) -> List[Dict]:
        """Export training data for ML model training"""
        if self.collection is None:
            return []
        
        query = {}
        
        if event_types:
            query["event_type"] = {"$in": event_types}
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        cursor = self.collection.find(
            query,
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit)
        
        return await cursor.to_list(length=limit)


# Global instance
ml_collector = MLDataCollector()


# Export
__all__ = [
    'MLDataCollector',
    'ml_collector',
    'EventType',
    'EventSeverity'
]
