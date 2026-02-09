"""
Translation QA API Routes
Part of Karau Automator
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import asyncio

from services.translation_qa import translation_qa_service, TranslationQAService


router = APIRouter(prefix="/translation-qa", tags=["Translation QA"])


# In-memory storage for QA results (in production, use database)
qa_history = []
scheduled_qa_enabled = False
last_scheduled_run = None


class QARunResponse(BaseModel):
    run_id: str
    status: str
    timestamp: str
    summary: Dict[str, Any]
    duration_ms: Optional[int] = None


class QADetailResponse(BaseModel):
    run_id: str
    timestamp: str
    status: str
    summary: Dict[str, Any]
    languages: Dict[str, Any]
    critical_issues: List[Dict]
    warnings: List[Dict]
    recommendations: List[Dict]
    duration_ms: Optional[int] = None


class ScheduleConfig(BaseModel):
    enabled: bool
    interval_hours: int = 24


@router.post("/run", response_model=QARunResponse)
async def run_translation_qa():
    """
    Run complete translation QA suite
    
    Performs:
    - JSON syntax validation
    - Missing key detection
    - Placeholder validation
    - Text expansion analysis
    - UI length checks
    - RTL language validation
    """
    try:
        # Run QA
        results = translation_qa_service.run_full_qa()
        
        # Store in history
        qa_history.insert(0, results)
        if len(qa_history) > 50:
            qa_history.pop()
        
        return QARunResponse(
            run_id=results["run_id"],
            status=results["status"],
            timestamp=results["timestamp"],
            summary=results["summary"],
            duration_ms=results.get("duration_ms")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest", response_model=QADetailResponse)
async def get_latest_qa_results():
    """Get the most recent QA run results"""
    if not qa_history:
        # Run QA if no history exists
        results = translation_qa_service.run_full_qa()
        qa_history.insert(0, results)
    
    latest = qa_history[0]
    return QADetailResponse(**latest)


@router.get("/history")
async def get_qa_history(limit: int = 10):
    """Get QA run history"""
    return {
        "total": len(qa_history),
        "runs": qa_history[:limit]
    }


@router.get("/run/{run_id}", response_model=QADetailResponse)
async def get_qa_run(run_id: str):
    """Get specific QA run by ID"""
    for run in qa_history:
        if run["run_id"] == run_id:
            return QADetailResponse(**run)
    raise HTTPException(status_code=404, detail="QA run not found")


@router.get("/missing-keys")
async def get_missing_keys():
    """Get detailed report of missing translation keys per language"""
    report = translation_qa_service.get_missing_keys_report()
    
    # Calculate totals
    total_missing = sum(len(keys) for keys in report.values())
    languages_affected = len(report)
    
    return {
        "total_missing_keys": total_missing,
        "languages_affected": languages_affected,
        "by_language": report
    }


@router.get("/expansion-issues")
async def get_expansion_issues():
    """Get detailed report of text expansion issues"""
    report = translation_qa_service.get_expansion_report()
    
    total_issues = sum(len(issues) for issues in report.values())
    
    return {
        "total_issues": total_issues,
        "by_language": report
    }


@router.get("/language/{lang_code}")
async def get_language_qa(lang_code: str):
    """Get QA results for a specific language"""
    if not translation_qa_service.qa_results:
        translation_qa_service.run_full_qa()
    
    results = translation_qa_service.qa_results
    if lang_code not in results.get("languages", {}):
        raise HTTPException(status_code=404, detail=f"Language '{lang_code}' not found")
    
    return {
        "language_code": lang_code,
        "results": results["languages"][lang_code],
        "master_key_count": results["summary"]["total_keys"]
    }


@router.post("/pseudo-localize")
async def generate_pseudo_localization():
    """
    Generate pseudo-localized strings for testing
    
    Converts English text to accented characters to help identify
    hard-coded strings that aren't being translated
    """
    pseudo_keys = translation_qa_service.generate_pseudo_localization()
    
    return {
        "total_keys": len(pseudo_keys),
        "sample": dict(list(pseudo_keys.items())[:10]),
        "description": "Use these pseudo-localized strings to test for hard-coded text"
    }


@router.get("/score")
async def get_translation_score():
    """Get overall translation quality score"""
    if not translation_qa_service.qa_results:
        translation_qa_service.run_full_qa()
    
    results = translation_qa_service.qa_results
    
    # Calculate per-language scores
    language_scores = {}
    for lang_code, lang_data in results.get("languages", {}).items():
        language_scores[lang_code] = {
            "score": lang_data["score"],
            "missing_keys": lang_data["missing_keys_count"],
            "placeholder_errors": len(lang_data["placeholder_errors"]),
            "status": "healthy" if lang_data["score"] >= 90 else 
                     "warning" if lang_data["score"] >= 70 else "critical"
        }
    
    return {
        "overall_score": results["summary"]["overall_score"],
        "total_languages": results["summary"]["total_languages"],
        "total_keys": results["summary"]["total_keys"],
        "language_scores": language_scores,
        "last_run": results["timestamp"]
    }


@router.get("/recommendations")
async def get_recommendations():
    """Get prioritized recommendations for improving translations"""
    if not translation_qa_service.qa_results:
        translation_qa_service.run_full_qa()
    
    results = translation_qa_service.qa_results
    
    return {
        "recommendations": results.get("recommendations", []),
        "critical_issues_count": len(results.get("critical_issues", [])),
        "overall_score": results["summary"]["overall_score"]
    }


@router.post("/schedule")
async def configure_scheduled_qa(config: ScheduleConfig):
    """Configure scheduled QA runs (for Karau Automator integration)"""
    global scheduled_qa_enabled
    scheduled_qa_enabled = config.enabled
    
    return {
        "scheduled_qa_enabled": scheduled_qa_enabled,
        "interval_hours": config.interval_hours,
        "message": f"Scheduled QA {'enabled' if config.enabled else 'disabled'}"
    }


@router.get("/schedule/status")
async def get_schedule_status():
    """Get current scheduled QA status"""
    return {
        "enabled": scheduled_qa_enabled,
        "last_run": last_scheduled_run,
        "next_run": None  # Would be calculated based on schedule
    }


# Karau Automator Integration
@router.post("/automator/trigger")
async def trigger_from_automator(background_tasks: BackgroundTasks):
    """
    Endpoint for Karau Automator to trigger QA runs
    
    Called by the automator on schedule to run translation QA
    and store results for the dashboard
    """
    global last_scheduled_run
    
    async def run_qa_background():
        global last_scheduled_run
        results = translation_qa_service.run_full_qa()
        qa_history.insert(0, results)
        if len(qa_history) > 50:
            qa_history.pop()
        last_scheduled_run = datetime.now(timezone.utc).isoformat()
    
    background_tasks.add_task(run_qa_background)
    
    return {
        "status": "triggered",
        "message": "Translation QA run started in background"
    }


@router.get("/dashboard-summary")
async def get_dashboard_summary():
    """
    Get summary data for the QA dashboard widget
    
    Returns condensed data suitable for dashboard display
    """
    if not translation_qa_service.qa_results:
        translation_qa_service.run_full_qa()
    
    results = translation_qa_service.qa_results
    summary = results["summary"]
    
    # Determine health status
    score = summary["overall_score"]
    if score >= 90:
        health = "excellent"
        health_color = "green"
    elif score >= 75:
        health = "good"
        health_color = "blue"
    elif score >= 50:
        health = "needs_attention"
        health_color = "yellow"
    else:
        health = "critical"
        health_color = "red"
    
    # Count languages by status
    status_counts = {"healthy": 0, "warning": 0, "critical": 0}
    for lang_data in results.get("languages", {}).values():
        if lang_data["score"] >= 90:
            status_counts["healthy"] += 1
        elif lang_data["score"] >= 70:
            status_counts["warning"] += 1
        else:
            status_counts["critical"] += 1
    
    return {
        "overall_score": score,
        "health": health,
        "health_color": health_color,
        "total_languages": summary["total_languages"],
        "total_keys": summary["total_keys"],
        "issues": {
            "critical": len(results.get("critical_issues", [])),
            "missing_keys": summary["missing_keys"],
            "placeholder_errors": summary["placeholder_errors"],
            "expansion_warnings": summary["expansion_warnings"]
        },
        "language_status": status_counts,
        "last_run": results["timestamp"],
        "top_recommendations": results.get("recommendations", [])[:3]
    }
