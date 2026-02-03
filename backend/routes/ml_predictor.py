"""
ML Issue Predictor API Routes
Provides endpoints for issue prediction and analysis.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from services.ml_issue_predictor import issue_predictor

router = APIRouter(prefix="/ml-predictor", tags=["ML Issue Predictor"])


@router.get("/analyze")
async def analyze_and_predict(
    hours: int = Query(default=24, ge=1, le=168, description="Hours of data to analyze")
):
    """
    Analyze recent system data and predict potential issues.
    Uses rule-based analysis on ML training data.
    """
    try:
        result = await issue_predictor.analyze(hours=hours)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-score")
async def get_health_score(
    hours: int = Query(default=24, ge=1, le=168)
):
    """Get current system health score based on recent data"""
    try:
        result = await issue_predictor.analyze(hours=hours)
        
        if result.get("status") == "insufficient_data":
            return {
                "status": "insufficient_data",
                "health_score": None,
                "message": f"Need at least {result.get('min_required')} events for analysis"
            }
        
        return {
            "status": "analyzed",
            "timestamp": result.get("timestamp"),
            "health_score": result.get("health_score"),
            "events_analyzed": result.get("events_analyzed")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions")
async def get_predictions(
    hours: int = Query(default=24, ge=1, le=168),
    severity: Optional[str] = Query(default=None, enum=["low", "medium", "high", "critical"]),
    category: Optional[str] = Query(default=None)
):
    """
    Get issue predictions filtered by severity and/or category.
    """
    try:
        result = await issue_predictor.analyze(hours=hours)
        
        if result.get("status") == "insufficient_data":
            return {
                "status": "insufficient_data",
                "predictions": [],
                "message": f"Need at least {result.get('min_required')} events for analysis"
            }
        
        predictions = result.get("predictions", [])
        
        # Filter by severity
        if severity:
            predictions = [p for p in predictions if p.get("severity") == severity]
        
        # Filter by category
        if category:
            predictions = [p for p in predictions if p.get("category") == category]
        
        return {
            "status": "analyzed",
            "timestamp": result.get("timestamp"),
            "total_predictions": len(predictions),
            "predictions": predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_prediction_summary():
    """Get a quick summary of current system status and predictions"""
    try:
        result = await issue_predictor.analyze(hours=24)
        
        if result.get("status") == "insufficient_data":
            return {
                "status": "insufficient_data",
                "events_analyzed": result.get("events_analyzed", 0),
                "summary": "Not enough data to generate predictions"
            }
        
        predictions = result.get("predictions", [])
        health = result.get("health_score", {})
        metrics = result.get("metrics_summary", {})
        
        # Count by severity
        critical_count = len([p for p in predictions if p.get("severity") == "critical"])
        high_count = len([p for p in predictions if p.get("severity") == "high"])
        medium_count = len([p for p in predictions if p.get("severity") == "medium"])
        low_count = len([p for p in predictions if p.get("severity") == "low"])
        
        # Determine overall status
        if critical_count > 0:
            status = "critical"
            status_message = f"{critical_count} critical issue(s) detected - immediate action required"
        elif high_count > 0:
            status = "warning"
            status_message = f"{high_count} high priority issue(s) detected"
        elif medium_count > 0:
            status = "attention"
            status_message = f"{medium_count} issue(s) need attention"
        elif low_count > 0:
            status = "monitoring"
            status_message = f"{low_count} low priority issue(s) to monitor"
        else:
            status = "healthy"
            status_message = "No issues detected - system is healthy"
        
        return {
            "status": status,
            "status_message": status_message,
            "health_score": health.get("overall", 0),
            "predictions_by_severity": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count
            },
            "metrics": {
                "error_rate": f"{metrics.get('error_rate', 0):.1f}%",
                "avg_latency": f"{metrics.get('avg_response_time_ms', 0):.0f}ms",
                "total_errors": metrics.get("total_errors", 0)
            },
            "top_issues": predictions[:3] if predictions else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_issue_categories():
    """Get available issue categories and severities"""
    return {
        "categories": [
            {"value": "performance", "name": "Performance", "description": "CPU, memory, and resource issues"},
            {"value": "error_rate", "name": "Error Rate", "description": "API and application errors"},
            {"value": "api_latency", "name": "API Latency", "description": "Slow response times"},
            {"value": "database", "name": "Database", "description": "Database performance issues"},
            {"value": "memory", "name": "Memory", "description": "Memory usage and leaks"},
            {"value": "user_experience", "name": "User Experience", "description": "UX-impacting issues"},
            {"value": "security", "name": "Security", "description": "Security-related concerns"}
        ],
        "severities": [
            {"value": "critical", "name": "Critical", "color": "red", "description": "Immediate action required"},
            {"value": "high", "name": "High", "color": "orange", "description": "Address soon"},
            {"value": "medium", "name": "Medium", "color": "yellow", "description": "Monitor closely"},
            {"value": "low", "name": "Low", "color": "blue", "description": "Informational"}
        ]
    }
