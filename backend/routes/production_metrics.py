"""
Production Metrics API Routes
Provides endpoints for tracking and querying production metrics.
"""
from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from services.production_metrics import production_metrics, MetricCategory
from routes.auth import get_current_user

router = APIRouter(prefix="/metrics", tags=["Production Metrics"])


# ============== Request Models ==============

class SessionStartRequest(BaseModel):
    session_id: str
    device_type: str = "web"
    referrer: Optional[str] = None


class PageViewRequest(BaseModel):
    session_id: str
    page_path: str
    page_title: Optional[str] = None
    time_on_page_ms: Optional[int] = None


class FeatureUsageRequest(BaseModel):
    feature_name: str
    feature_category: str
    duration_ms: Optional[int] = None
    success: bool = True
    metadata: Optional[Dict[str, Any]] = None


class JobApplicationRequest(BaseModel):
    job_id: str
    job_title: str
    company: str
    source: str
    application_method: str = "direct"
    used_ai_cover_letter: bool = False


class AIToolUsageRequest(BaseModel):
    tool_name: str
    input_type: str
    output_quality_score: Optional[float] = None
    tokens_used: int = 0
    response_time_ms: int = 0
    user_feedback: Optional[str] = None


class ConversionRequest(BaseModel):
    conversion_type: str
    source: str
    campaign: Optional[str] = None
    value: Optional[float] = None


# ============== Helper Functions ==============

def is_admin_user(user: dict) -> bool:
    """Check if user has admin access"""
    if not user:
        return False
    return (
        user.get("role") == "admin" or
        user.get("is_admin") == True or
        "all" in user.get("permissions", [])
    )


# ============== Tracking Endpoints ==============

@router.post("/session/start")
async def track_session_start(request: Request, data: SessionStartRequest):
    """Track session start"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    await production_metrics.track_session_start(
        user_id=user.get("user_id"),
        session_id=data.session_id,
        device_type=data.device_type,
        referrer=data.referrer
    )
    
    return {"success": True, "session_id": data.session_id}


@router.post("/session/end")
async def track_session_end(request: Request, session_id: str):
    """Track session end"""
    await production_metrics.track_session_end(session_id)
    return {"success": True}


@router.post("/page-view")
async def track_page_view(request: Request, data: PageViewRequest):
    """Track page view"""
    user = await get_current_user(request)
    user_id = user.get("user_id") if user else "anonymous"
    
    await production_metrics.track_page_view(
        user_id=user_id,
        session_id=data.session_id,
        page_path=data.page_path,
        page_title=data.page_title,
        time_on_page_ms=data.time_on_page_ms
    )
    
    return {"success": True}


@router.post("/feature-usage")
async def track_feature_usage(request: Request, data: FeatureUsageRequest):
    """Track feature usage"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    await production_metrics.track_feature_usage(
        user_id=user.get("user_id"),
        feature_name=data.feature_name,
        feature_category=data.feature_category,
        duration_ms=data.duration_ms,
        success=data.success,
        metadata=data.metadata
    )
    
    return {"success": True}


@router.post("/job-application")
async def track_job_application(request: Request, data: JobApplicationRequest):
    """Track job application"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    await production_metrics.track_job_application(
        user_id=user.get("user_id"),
        job_id=data.job_id,
        job_title=data.job_title,
        company=data.company,
        source=data.source,
        application_method=data.application_method,
        used_ai_cover_letter=data.used_ai_cover_letter
    )
    
    return {"success": True}


@router.post("/ai-tool-usage")
async def track_ai_tool_usage(request: Request, data: AIToolUsageRequest):
    """Track AI tool usage"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    await production_metrics.track_ai_tool_usage(
        user_id=user.get("user_id"),
        tool_name=data.tool_name,
        input_type=data.input_type,
        output_quality_score=data.output_quality_score,
        tokens_used=data.tokens_used,
        response_time_ms=data.response_time_ms,
        user_feedback=data.user_feedback
    )
    
    return {"success": True}


@router.post("/conversion")
async def track_conversion(request: Request, data: ConversionRequest):
    """Track conversion event"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    await production_metrics.track_conversion_event(
        user_id=user.get("user_id"),
        conversion_type=data.conversion_type,
        source=data.source,
        campaign=data.campaign,
        value=data.value
    )
    
    return {"success": True}


# ============== Analytics Endpoints (Admin Only) ==============

@router.get("/analytics/engagement")
async def get_engagement_analytics(
    request: Request,
    days: int = Query(default=7, ge=1, le=90)
):
    """Get user engagement analytics (admin only)"""
    user = await get_current_user(request)
    if not user or not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    summary = await production_metrics.get_engagement_summary(days=days)
    return summary


@router.get("/analytics/business")
async def get_business_analytics(
    request: Request,
    days: int = Query(default=7, ge=1, le=90)
):
    """Get business metrics analytics (admin only)"""
    user = await get_current_user(request)
    if not user or not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    summary = await production_metrics.get_business_summary(days=days)
    return summary


@router.get("/analytics/ai-usage")
async def get_ai_usage_analytics(
    request: Request,
    days: int = Query(default=7, ge=1, le=90)
):
    """Get AI tool usage analytics (admin only)"""
    user = await get_current_user(request)
    if not user or not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    summary = await production_metrics.get_ai_usage_summary(days=days)
    return summary


@router.get("/analytics/funnel")
async def get_conversion_funnel(
    request: Request,
    days: int = Query(default=30, ge=1, le=180)
):
    """Get conversion funnel analytics (admin only)"""
    user = await get_current_user(request)
    if not user or not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    funnel = await production_metrics.get_conversion_funnel(days=days)
    return funnel


@router.get("/analytics/dashboard")
async def get_analytics_dashboard(
    request: Request,
    days: int = Query(default=7, ge=1, le=90)
):
    """Get combined analytics dashboard (admin only)"""
    user = await get_current_user(request)
    if not user or not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    engagement = await production_metrics.get_engagement_summary(days=days)
    business = await production_metrics.get_business_summary(days=days)
    ai_usage = await production_metrics.get_ai_usage_summary(days=days)
    funnel = await production_metrics.get_conversion_funnel(days=days)
    
    return {
        "period_days": days,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engagement": engagement,
        "business": business,
        "ai_usage": ai_usage,
        "funnel": funnel
    }


@router.get("/categories")
async def get_metric_categories():
    """Get available metric categories"""
    return {
        "categories": [
            {"value": c.value, "name": c.name.replace("_", " ").title()}
            for c in MetricCategory
        ]
    }
