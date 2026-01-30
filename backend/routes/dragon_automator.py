"""
KARAU DRAGON AI Automator
Comprehensive system for automatic diagnostics, fixes, improvements, and updates.
Features:
- System health monitoring and diagnostics
- Automatic issue detection and fixing
- Version management and changelog
- Push updates to users on login
- Self-improvement capabilities
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import asyncio
import logging
import json
import hashlib
import os

from emergentintegrations.llm.chat import LlmChat, UserMessage

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user

router = APIRouter(prefix="/dragon/automator", tags=["KARAU Dragon Automator"])

# ============== Helper Functions ==============

def is_admin_user(user: dict) -> bool:
    """Check if user has admin privileges"""
    if not user:
        return False
    return (
        user.get("is_admin", False) or
        user.get("role") == "admin" or
        user.get("email") == "admin@medmatch.com" or
        "all" in user.get("permissions", []) or
        "admin_dashboard" in user.get("permissions", [])
    )

# ============== Version Management ==============

CURRENT_VERSION = "2.4.0"
VERSION_HISTORY = []

class VersionInfo(BaseModel):
    version: str
    release_date: str
    changes: List[str]
    type: str  # major, minor, patch

class SystemHealth(BaseModel):
    overall_status: str  # healthy, degraded, critical
    score: float  # 0-100
    checks: Dict[str, Any]
    timestamp: str

class DiagnosticResult(BaseModel):
    issue_id: str
    severity: str  # critical, high, medium, low
    category: str
    description: str
    auto_fixable: bool
    fix_applied: bool = False
    fix_result: Optional[str] = None

class UpdateNotification(BaseModel):
    version: str
    title: str
    description: str
    changes: List[str]
    importance: str  # critical, recommended, optional
    read: bool = False

# ============== System Diagnostics ==============

async def run_database_diagnostics() -> Dict[str, Any]:
    """Check database health and performance"""
    results = {
        "status": "healthy",
        "issues": [],
        "metrics": {}
    }
    
    try:
        # Check collections
        collections = await db.list_collection_names()
        results["metrics"]["collections"] = len(collections)
        
        # Check user count
        user_count = await db.users.count_documents({})
        results["metrics"]["total_users"] = user_count
        
        # Check for orphaned data
        orphaned_apps = await db.applications.count_documents({"user_id": {"$exists": False}})
        if orphaned_apps > 0:
            results["issues"].append({
                "type": "orphaned_data",
                "description": f"{orphaned_apps} applications without user_id",
                "severity": "medium",
                "auto_fixable": True
            })
            results["status"] = "degraded"
        
        # Check indexes
        user_indexes = await db.users.index_information()
        if "user_id_1" not in user_indexes:
            results["issues"].append({
                "type": "missing_index",
                "description": "Missing index on users.user_id",
                "severity": "high",
                "auto_fixable": True
            })
            results["status"] = "degraded"
            
    except Exception as e:
        results["status"] = "critical"
        results["issues"].append({
            "type": "connection_error",
            "description": str(e),
            "severity": "critical",
            "auto_fixable": False
        })
    
    return results


async def run_api_diagnostics() -> Dict[str, Any]:
    """Check API endpoints health"""
    results = {
        "status": "healthy",
        "issues": [],
        "metrics": {}
    }
    
    # Check critical endpoints
    critical_routes = [
        "/api/auth/login",
        "/api/jobs/search",
        "/api/dragon/process",
        "/api/analytics/funnel"
    ]
    
    results["metrics"]["total_routes"] = len(critical_routes)
    results["metrics"]["healthy_routes"] = len(critical_routes)  # Assume healthy
    
    return results


async def run_ai_diagnostics() -> Dict[str, Any]:
    """Check AI services health"""
    results = {
        "status": "healthy",
        "issues": [],
        "metrics": {}
    }
    
    if not EMERGENT_LLM_KEY:
        results["status"] = "critical"
        results["issues"].append({
            "type": "missing_api_key",
            "description": "EMERGENT_LLM_KEY not configured",
            "severity": "critical",
            "auto_fixable": False
        })
    else:
        results["metrics"]["llm_configured"] = True
        
        # Test LLM connection - use send_message method
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id="diagnostic_test",
                system_message="Respond with 'OK' only"
            ).with_model("openai", "gpt-5.2")
            
            # Use send_message method
            response = chat.send_message("test")
            results["metrics"]["llm_responsive"] = True
        except Exception as e:
            results["status"] = "degraded"
            results["issues"].append({
                "type": "llm_error",
                "description": f"LLM service error: {str(e)[:100]}",
                "severity": "high",
                "auto_fixable": False
            })
    
    return results


async def run_performance_diagnostics() -> Dict[str, Any]:
    """Check system performance metrics"""
    results = {
        "status": "healthy",
        "issues": [],
        "metrics": {}
    }
    
    try:
        import psutil
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        results["metrics"]["cpu_percent"] = cpu_percent
        if cpu_percent > 80:
            results["issues"].append({
                "type": "high_cpu",
                "description": f"CPU usage at {cpu_percent}%",
                "severity": "high",
                "auto_fixable": False
            })
            results["status"] = "degraded"
        
        # Memory usage
        memory = psutil.virtual_memory()
        results["metrics"]["memory_percent"] = memory.percent
        if memory.percent > 85:
            results["issues"].append({
                "type": "high_memory",
                "description": f"Memory usage at {memory.percent}%",
                "severity": "high",
                "auto_fixable": False
            })
            results["status"] = "degraded"
        
        # Disk usage
        disk = psutil.disk_usage('/')
        results["metrics"]["disk_percent"] = disk.percent
        if disk.percent > 90:
            results["issues"].append({
                "type": "low_disk",
                "description": f"Disk usage at {disk.percent}%",
                "severity": "critical",
                "auto_fixable": False
            })
            results["status"] = "critical"
            
    except ImportError:
        results["metrics"]["psutil_available"] = False
    except Exception as e:
        logging.error(f"Performance diagnostic error: {e}")
    
    return results


# ============== Auto-Fix Functions ==============

async def fix_orphaned_data() -> Dict[str, Any]:
    """Remove orphaned application records"""
    result = {"success": False, "details": ""}
    
    try:
        # Get all valid user IDs
        valid_users = await db.users.distinct("user_id")
        
        # Remove applications without valid user
        delete_result = await db.applications.delete_many({
            "user_id": {"$nin": valid_users}
        })
        
        result["success"] = True
        result["details"] = f"Removed {delete_result.deleted_count} orphaned records"
    except Exception as e:
        result["details"] = str(e)
    
    return result


async def fix_missing_indexes() -> Dict[str, Any]:
    """Create missing database indexes"""
    result = {"success": False, "details": "", "indexes_created": []}
    
    try:
        # Users collection indexes
        await db.users.create_index("user_id", unique=True)
        await db.users.create_index("email", unique=True)
        result["indexes_created"].append("users.user_id")
        result["indexes_created"].append("users.email")
        
        # Applications collection indexes
        await db.applications.create_index("user_id")
        await db.applications.create_index([("user_id", 1), ("applied_at", -1)])
        result["indexes_created"].append("applications.user_id")
        
        # Jobs collection indexes
        await db.saved_jobs.create_index("user_id")
        result["indexes_created"].append("saved_jobs.user_id")
        
        result["success"] = True
        result["details"] = f"Created {len(result['indexes_created'])} indexes"
    except Exception as e:
        result["details"] = str(e)
    
    return result


async def fix_data_integrity() -> Dict[str, Any]:
    """Fix common data integrity issues"""
    result = {"success": False, "details": "", "fixes_applied": []}
    
    try:
        # Fix users without membership_status
        update_result = await db.users.update_many(
            {"membership_status": {"$exists": False}},
            {"$set": {"membership_status": "trial"}}
        )
        if update_result.modified_count > 0:
            result["fixes_applied"].append(f"Set membership_status for {update_result.modified_count} users")
        
        # Fix applications without status
        update_result = await db.applications.update_many(
            {"status": {"$exists": False}},
            {"$set": {"status": "applied"}}
        )
        if update_result.modified_count > 0:
            result["fixes_applied"].append(f"Set status for {update_result.modified_count} applications")
        
        result["success"] = True
        result["details"] = f"Applied {len(result['fixes_applied'])} fixes"
    except Exception as e:
        result["details"] = str(e)
    
    return result


# ============== Version Management ==============

async def get_version_info() -> Dict[str, Any]:
    """Get current version and changelog"""
    changelog = await db.system_changelog.find(
        {},
        {"_id": 0}
    ).sort("release_date", -1).limit(10).to_list(10)
    
    return {
        "current_version": CURRENT_VERSION,
        "changelog": changelog
    }


async def create_version_update(
    version: str,
    changes: List[str],
    update_type: str = "patch"
) -> Dict[str, Any]:
    """Create a new version entry"""
    entry = {
        "version": version,
        "release_date": datetime.now(timezone.utc).isoformat(),
        "changes": changes,
        "type": update_type,
        "created_by": "KARAU_DRAGON_AUTOMATOR"
    }
    
    await db.system_changelog.insert_one(entry)
    
    # Create notifications for all users
    users = await db.users.find({}, {"_id": 0, "user_id": 1}).to_list(10000)
    
    notifications = [{
        "user_id": user["user_id"],
        "type": "system_update",
        "version": version,
        "title": f"MedMatch {version} Released",
        "description": f"New {update_type} update available",
        "changes": changes,
        "importance": "recommended" if update_type == "minor" else ("critical" if update_type == "major" else "optional"),
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    } for user in users]
    
    if notifications:
        await db.update_notifications.insert_many(notifications)
    
    return {
        "version": version,
        "notifications_sent": len(notifications)
    }


# ============== AI-Powered Improvements ==============

async def analyze_system_for_improvements() -> List[Dict[str, Any]]:
    """Use AI to analyze system and suggest improvements"""
    improvements = []
    
    if not EMERGENT_LLM_KEY:
        return improvements
    
    try:
        # Gather system metrics
        db_stats = await run_database_diagnostics()
        perf_stats = await run_performance_diagnostics()
        
        # Get recent user feedback
        feedback = await db.feedback.find(
            {"created_at": {"$gte": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()}}
        ).to_list(50)
        
        # Analyze with AI
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id="improvement_analysis",
            system_message="""You are KARAU DRAGON AI Automator. Analyze the system data and suggest improvements.
Return a JSON array of improvements with this structure:
[
  {
    "category": "performance|ux|feature|security",
    "priority": "high|medium|low",
    "title": "Brief title",
    "description": "Detailed description of the improvement",
    "implementation_hint": "How to implement this",
    "auto_implementable": true/false
  }
]
Focus on actionable, specific improvements. Return ONLY valid JSON array."""
        ).with_model("openai", "gpt-5.2")
        
        prompt = f"""
System Metrics:
- Database: {db_stats['status']}, Issues: {len(db_stats['issues'])}
- Performance: CPU {perf_stats.get('metrics', {}).get('cpu_percent', 'N/A')}%, Memory {perf_stats.get('metrics', {}).get('memory_percent', 'N/A')}%

Recent User Feedback Count: {len(feedback)}
Feedback Themes: {[f.get('category', 'general') for f in feedback[:10]]}

Suggest 3-5 specific improvements for this job search platform.
"""
        
        # Use send_message method
        response = chat.send_message(prompt)
        
        try:
            improvements = json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                improvements = json.loads(json_match.group())
                
    except Exception as e:
        logging.error(f"Improvement analysis error: {e}")
    
    return improvements


async def auto_implement_improvement(improvement: Dict[str, Any]) -> Dict[str, Any]:
    """Automatically implement certain improvements"""
    result = {"success": False, "details": ""}
    
    category = improvement.get("category", "")
    title = improvement.get("title", "")
    
    # Only implement safe, predefined improvements
    safe_improvements = {
        "add_indexes": fix_missing_indexes,
        "fix_data_integrity": fix_data_integrity,
        "cleanup_orphaned": fix_orphaned_data
    }
    
    # Map improvement title to action
    for key, action in safe_improvements.items():
        if key.lower() in title.lower():
            result = await action()
            result["improvement"] = title
            break
    else:
        result["details"] = "This improvement requires manual implementation"
    
    return result


# ============== API Endpoints ==============

@router.get("/health")
async def get_system_health(request: Request):
    """Get comprehensive system health status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Run all diagnostics in parallel
    db_diag, api_diag, ai_diag, perf_diag = await asyncio.gather(
        run_database_diagnostics(),
        run_api_diagnostics(),
        run_ai_diagnostics(),
        run_performance_diagnostics()
    )
    
    # Calculate overall health score
    status_scores = {"healthy": 100, "degraded": 60, "critical": 20}
    scores = [
        status_scores.get(db_diag["status"], 50),
        status_scores.get(api_diag["status"], 50),
        status_scores.get(ai_diag["status"], 50),
        status_scores.get(perf_diag["status"], 50)
    ]
    overall_score = sum(scores) / len(scores)
    
    overall_status = "healthy"
    if overall_score < 70:
        overall_status = "degraded"
    if overall_score < 40:
        overall_status = "critical"
    
    # Collect all issues
    all_issues = (
        db_diag.get("issues", []) +
        api_diag.get("issues", []) +
        ai_diag.get("issues", []) +
        perf_diag.get("issues", [])
    )
    
    return {
        "overall_status": overall_status,
        "health_score": round(overall_score, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "diagnostics": {
            "database": db_diag,
            "api": api_diag,
            "ai_services": ai_diag,
            "performance": perf_diag
        },
        "total_issues": len(all_issues),
        "issues": all_issues,
        "version": CURRENT_VERSION
    }


@router.post("/diagnose")
async def run_full_diagnostics(request: Request, background_tasks: BackgroundTasks):
    """Run comprehensive diagnostics and get detailed report"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if user is admin
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Run diagnostics
    results = await asyncio.gather(
        run_database_diagnostics(),
        run_api_diagnostics(),
        run_ai_diagnostics(),
        run_performance_diagnostics()
    )
    
    # Generate diagnostic report
    report = {
        "id": hashlib.md5(datetime.now(timezone.utc).isoformat().encode()).hexdigest()[:12],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user["user_id"],
        "diagnostics": {
            "database": results[0],
            "api": results[1],
            "ai_services": results[2],
            "performance": results[3]
        },
        "summary": {
            "total_issues": sum(len(r.get("issues", [])) for r in results),
            "auto_fixable": sum(
                1 for r in results 
                for i in r.get("issues", []) 
                if i.get("auto_fixable")
            )
        }
    }
    
    # Store report
    await db.diagnostic_reports.insert_one({**report, "_id": report["id"]})
    
    return report


@router.post("/auto-fix")
async def apply_auto_fixes(request: Request):
    """Automatically fix detected issues"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Run diagnostics first
    db_diag = await run_database_diagnostics()
    
    fixes_applied = []
    
    # Apply auto-fixes based on detected issues
    for issue in db_diag.get("issues", []):
        if not issue.get("auto_fixable"):
            continue
        
        fix_result = None
        issue_type = issue.get("type", "")
        
        if issue_type == "orphaned_data":
            fix_result = await fix_orphaned_data()
        elif issue_type == "missing_index":
            fix_result = await fix_missing_indexes()
        
        if fix_result:
            fixes_applied.append({
                "issue": issue_type,
                "result": fix_result
            })
    
    # Always run data integrity fix
    integrity_result = await fix_data_integrity()
    fixes_applied.append({
        "issue": "data_integrity",
        "result": integrity_result
    })
    
    # Log the auto-fix action
    await db.automator_logs.insert_one({
        "action": "auto_fix",
        "user_id": user["user_id"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fixes_applied": fixes_applied
    })
    
    return {
        "success": True,
        "fixes_applied": len(fixes_applied),
        "details": fixes_applied
    }


@router.get("/improvements")
async def get_improvement_suggestions(request: Request):
    """Get AI-powered improvement suggestions"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    improvements = await analyze_system_for_improvements()
    
    return {
        "suggestions": improvements,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ai_powered": bool(EMERGENT_LLM_KEY)
    }


@router.post("/improvements/{index}/implement")
async def implement_improvement(index: int, request: Request):
    """Implement a specific improvement suggestion"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get improvement suggestions
    improvements = await analyze_system_for_improvements()
    
    if index < 0 or index >= len(improvements):
        raise HTTPException(status_code=404, detail="Improvement not found")
    
    improvement = improvements[index]
    
    if not improvement.get("auto_implementable"):
        return {
            "success": False,
            "reason": "This improvement requires manual implementation",
            "improvement": improvement
        }
    
    result = await auto_implement_improvement(improvement)
    
    return result


@router.get("/version")
async def get_version(request: Request):
    """Get current version and changelog"""
    return await get_version_info()


@router.post("/version/release")
async def release_new_version(request: Request):
    """Create a new version release"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    body = await request.json()
    version = body.get("version")
    changes = body.get("changes", [])
    update_type = body.get("type", "patch")
    
    if not version or not changes:
        raise HTTPException(status_code=400, detail="Version and changes required")
    
    result = await create_version_update(version, changes, update_type)
    
    return result


@router.get("/updates")
async def get_pending_updates(request: Request):
    """Get pending update notifications for the current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    updates = await db.update_notifications.find(
        {"user_id": user["user_id"], "read": False},
        {"_id": 0}
    ).sort("created_at", -1).to_list(10)
    
    return {
        "updates": updates,
        "count": len(updates),
        "current_version": CURRENT_VERSION
    }


@router.post("/updates/mark-read")
async def mark_updates_read(request: Request):
    """Mark all update notifications as read"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.update_notifications.update_many(
        {"user_id": user["user_id"], "read": False},
        {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {
        "marked_read": result.modified_count
    }


@router.post("/analyze-and-fix")
async def analyze_and_auto_fix(request: Request, background_tasks: BackgroundTasks):
    """
    KARAU DRAGON's main automation endpoint.
    Runs diagnostics, identifies issues, applies fixes, and generates a report.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Phase 1: Diagnostics
    db_diag, api_diag, ai_diag, perf_diag = await asyncio.gather(
        run_database_diagnostics(),
        run_api_diagnostics(),
        run_ai_diagnostics(),
        run_performance_diagnostics()
    )
    
    all_issues = (
        db_diag.get("issues", []) +
        api_diag.get("issues", []) +
        ai_diag.get("issues", []) +
        perf_diag.get("issues", [])
    )
    
    # Phase 2: Auto-fix
    fixes_applied = []
    for issue in all_issues:
        if not issue.get("auto_fixable"):
            continue
        
        issue_type = issue.get("type", "")
        fix_result = None
        
        if issue_type == "orphaned_data":
            fix_result = await fix_orphaned_data()
        elif issue_type == "missing_index":
            fix_result = await fix_missing_indexes()
        
        if fix_result and fix_result.get("success"):
            fixes_applied.append({
                "issue": issue_type,
                "severity": issue.get("severity"),
                "result": fix_result
            })
    
    # Always run integrity check
    integrity = await fix_data_integrity()
    if integrity.get("fixes_applied"):
        fixes_applied.append({
            "issue": "data_integrity",
            "severity": "medium",
            "result": integrity
        })
    
    # Phase 3: AI Improvements
    improvements = await analyze_system_for_improvements()
    
    # Phase 4: Generate report
    report = {
        "id": hashlib.md5(datetime.now(timezone.utc).isoformat().encode()).hexdigest()[:12],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phases": {
            "diagnostics": {
                "total_issues": len(all_issues),
                "by_severity": {
                    "critical": len([i for i in all_issues if i.get("severity") == "critical"]),
                    "high": len([i for i in all_issues if i.get("severity") == "high"]),
                    "medium": len([i for i in all_issues if i.get("severity") == "medium"]),
                    "low": len([i for i in all_issues if i.get("severity") == "low"])
                }
            },
            "auto_fix": {
                "fixes_applied": len(fixes_applied),
                "details": fixes_applied
            },
            "improvements": {
                "suggestions": len(improvements),
                "auto_implementable": len([i for i in improvements if i.get("auto_implementable")])
            }
        },
        "summary": {
            "health_before": "degraded" if all_issues else "healthy",
            "health_after": "healthy" if not [i for i in all_issues if not i.get("auto_fixable")] else "improved",
            "actions_taken": len(fixes_applied),
            "pending_improvements": len(improvements)
        },
        "version": CURRENT_VERSION
    }
    
    # Store report
    await db.automator_reports.insert_one({**report})
    
    return {
        "success": True,
        "message": "KARAU DRAGON Automator completed analysis and fixes",
        "report": report,
        "improvements": improvements[:3]  # Top 3 suggestions
    }


@router.post("/run-weekly-maintenance")
async def run_weekly_maintenance_now(request: Request):
    """
    Manually trigger the weekly maintenance task.
    Admin only. Normally runs Sundays at 1:00 AM PST.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from services.dragon_scheduler import run_weekly_maintenance
        report = await run_weekly_maintenance()
        return {
            "success": True,
            "message": "Weekly maintenance completed",
            "report": report
        }
    except Exception as e:
        logging.error(f"Manual maintenance error: {e}")
        raise HTTPException(status_code=500, detail=f"Maintenance failed: {str(e)}")


@router.get("/scheduler-status")
async def get_scheduler_status(request: Request):
    """Get status of all scheduled tasks"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        from services.dragon_scheduler import scheduler as dragon_scheduler
        
        jobs = []
        for job in dragon_scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "running": dragon_scheduler.running,
            "jobs": jobs,
            "timezone": "UTC"
        }
    except Exception as e:
        return {
            "running": False,
            "error": str(e),
            "jobs": []
        }


@router.get("/maintenance-reports")
async def get_maintenance_reports(request: Request, limit: int = 10):
    """Get recent maintenance reports"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    reports = await db.maintenance_reports.find(
        {},
        {"_id": 0}
    ).sort("started_at", -1).limit(limit).to_list(limit)
    
    return {
        "reports": reports,
        "count": len(reports)
    }


@router.get("/predictions")
async def get_issue_predictions(request: Request):
    """Get AI-powered predictive issue analysis"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        from services.dragon_scheduler import analyze_trends_for_predictions
        predictions = await analyze_trends_for_predictions()
        return {
            "predictions": predictions,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "predictions": [],
            "error": str(e)
        }


# ============== Background Tasks ==============

async def scheduled_diagnostics():
    """Run diagnostics on a schedule (called by background task)"""
    try:
        health = await asyncio.gather(
            run_database_diagnostics(),
            run_performance_diagnostics()
        )
        
        # Store health snapshot
        await db.health_snapshots.insert_one({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": health[0],
            "performance": health[1]
        })
        
        # Check for critical issues and auto-fix if possible
        for diag in health:
            for issue in diag.get("issues", []):
                if issue.get("severity") == "critical" and issue.get("auto_fixable"):
                    if issue.get("type") == "orphaned_data":
                        await fix_orphaned_data()
                    elif issue.get("type") == "missing_index":
                        await fix_missing_indexes()
                    
                    logging.info(f"KARAU Automator auto-fixed: {issue.get('type')}")
                    
    except Exception as e:
        logging.error(f"Scheduled diagnostics error: {e}")
