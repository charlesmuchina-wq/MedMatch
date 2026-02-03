"""
ML Data Collection API Routes
Provides endpoints for viewing and exporting ML training data.
Admin-only access for data analysis and export.
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
from typing import Optional

from services.ml_data_collector import ml_collector, EventType, EventSeverity
from services.ml_data_generator import ml_data_generator

router = APIRouter(prefix="/ml-data", tags=["ML Data Collection"])

# Helper to check admin access
def is_admin_user(user: dict) -> bool:
    """Check if user has admin access"""
    if not user:
        return False
    return (
        user.get("role") == "admin" or
        user.get("is_admin") or
        "all" in user.get("permissions", [])
    )


@router.get("/status")
async def get_ml_collector_status():
    """Get ML data collector service status"""
    try:
        stats = await ml_collector.get_event_stats(hours=24)
        return {
            "status": "active" if ml_collector.collection is not None else "not_initialized",
            "buffer_size": len(ml_collector.buffer),
            "flush_interval_seconds": ml_collector.flush_interval,
            "last_24h_stats": stats
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/events/recent-errors")
async def get_recent_errors(
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=100, ge=1, le=500)
):
    """Get recent system errors for analysis"""
    try:
        errors = await ml_collector.get_recent_errors(hours=hours, limit=limit)
        return {
            "time_period_hours": hours,
            "error_count": len(errors),
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/stats")
async def get_event_statistics(
    hours: int = Query(default=24, ge=1, le=168)
):
    """Get event statistics for the given time period"""
    try:
        stats = await ml_collector.get_event_stats(hours=hours)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/user/{user_id}")
async def get_user_activity(
    user_id: str,
    days: int = Query(default=30, ge=1, le=90)
):
    """Get user activity pattern for personalization"""
    try:
        pattern = await ml_collector.get_user_activity_pattern(user_id=user_id, days=days)
        return pattern
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_training_data(
    event_types: Optional[str] = Query(default=None, description="Comma-separated event types"),
    start_date: Optional[str] = Query(default=None, description="ISO format: 2026-01-01"),
    end_date: Optional[str] = Query(default=None, description="ISO format: 2026-01-31"),
    limit: int = Query(default=1000, ge=1, le=10000)
):
    """Export ML training data for model training (admin only)"""
    try:
        # Parse event types
        event_type_list = None
        if event_types:
            event_type_list = [e.strip() for e in event_types.split(",")]
        
        # Parse dates
        start = None
        end = None
        if start_date:
            start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        if end_date:
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        
        data = await ml_collector.get_training_data_export(
            event_types=event_type_list,
            start_date=start,
            end_date=end,
            limit=limit
        )
        
        return {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "filters": {
                "event_types": event_type_list,
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit
            },
            "record_count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/event-types")
async def get_available_event_types():
    """Get list of available event types for filtering"""
    return {
        "event_types": [
            {"value": e.value, "name": e.name, "category": _get_event_category(e)}
            for e in EventType
        ],
        "severities": [
            {"value": s.value, "name": s.name}
            for s in EventSeverity
        ]
    }


def _get_event_category(event_type: EventType) -> str:
    """Categorize event types for UI grouping"""
    system_events = [
        EventType.SYSTEM_ERROR, EventType.SYSTEM_WARNING, EventType.SYSTEM_INFO,
        EventType.PERFORMANCE_METRIC, EventType.DATABASE_OPERATION, EventType.API_CALL,
        EventType.SCHEDULER_EVENT
    ]
    user_events = [
        EventType.USER_LOGIN, EventType.USER_LOGOUT, EventType.USER_REGISTRATION,
        EventType.JOB_SEARCH, EventType.JOB_APPLICATION, EventType.RESUME_UPLOAD,
        EventType.RESUME_PARSE, EventType.AI_INTERACTION, EventType.COVER_LETTER_GENERATION,
        EventType.INTERVIEW_PREP, EventType.VOICE_COACHING, EventType.VIDEO_INTERVIEW,
        EventType.MESSAGE_SENT, EventType.NOTIFICATION_SENT, EventType.PAYMENT_EVENT
    ]
    
    if event_type in system_events:
        return "system"
    elif event_type in user_events:
        return "user_action"
    else:
        return "diagnostic"


@router.post("/flush")
async def flush_buffer():
    """Manually flush the event buffer to database"""
    try:
        buffer_count = len(ml_collector.buffer)
        await ml_collector._flush_buffer()
        return {
            "success": True,
            "events_flushed": buffer_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-event")
async def log_test_event():
    """Log a test event to verify the collector is working"""
    try:
        await ml_collector.log_event(
            event_type=EventType.SYSTEM_INFO,
            severity=EventSeverity.INFO,
            message="Test event from ML data API",
            data={"test": True, "timestamp": datetime.now(timezone.utc).isoformat()}
        )
        return {
            "success": True,
            "message": "Test event logged",
            "buffer_size": len(ml_collector.buffer)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_training_data(
    count: int = Query(default=10, ge=1, le=100, description="Number of event batches to generate")
):
    """Generate synthetic training data for ML model improvement"""
    try:
        result = await ml_data_generator.generate_batch(count=count)
        await ml_collector._flush_buffer()
        
        return {
            "success": True,
            "generated": result,
            "message": f"Generated {sum(result.values())} events"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-historical")
async def generate_historical_data(
    hours: int = Query(default=24, ge=1, le=168, description="Hours of historical data to generate"),
    events_per_hour: int = Query(default=20, ge=5, le=100, description="Events per hour")
):
    """Generate historical training data for ML model bootstrapping (admin only)"""
    try:
        result = await ml_data_generator.generate_historical_data(
            hours=hours,
            events_per_hour=events_per_hour
        )
        
        return {
            "success": True,
            "generated": result,
            "message": f"Generated {hours} hours of historical data"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generator/start")
async def start_data_generator(
    interval_seconds: int = Query(default=60, ge=10, le=3600, description="Generation interval in seconds")
):
    """Start automatic background data generation"""
    try:
        await ml_data_generator.start(interval_seconds=interval_seconds)
        return {
            "success": True,
            "message": f"Data generator started with {interval_seconds}s interval"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generator/stop")
async def stop_data_generator():
    """Stop automatic background data generation"""
    try:
        await ml_data_generator.stop()
        return {
            "success": True,
            "message": "Data generator stopped"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
