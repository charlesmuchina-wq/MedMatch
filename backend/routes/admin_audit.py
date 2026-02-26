"""
Admin Audit Logging System
Tracks all admin actions for security and compliance.
"""
from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid
import logging

from utils.database import db
from routes.auth import get_current_user, require_auth

router = APIRouter(prefix="/admin-audit", tags=["Admin Audit"])

logger = logging.getLogger(__name__)

# ============== Models ==============

class AuditLogEntry(BaseModel):
    action: str
    target_type: str
    target_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogFilter(BaseModel):
    admin_id: Optional[str] = None
    action: Optional[str] = None
    target_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


# ============== Audit Categories ==============

AUDIT_ACTIONS = {
    # User Management
    "user_create": "Created a new user",
    "user_update": "Updated user information",
    "user_delete": "Deleted a user",
    "user_suspend": "Suspended a user account",
    "user_activate": "Activated a user account",
    "user_role_change": "Changed user role/permissions",
    
    # Content Management
    "job_approve": "Approved a job posting",
    "job_reject": "Rejected a job posting",
    "job_delete": "Deleted a job posting",
    "job_feature": "Featured a job posting",
    
    # System Settings
    "settings_update": "Updated system settings",
    "rate_limit_change": "Changed rate limit configuration",
    "maintenance_mode": "Toggled maintenance mode",
    
    # Data Access
    "data_export": "Exported user/system data",
    "data_view_sensitive": "Viewed sensitive data",
    "reports_access": "Accessed admin reports",
    
    # Security Actions
    "login_as_user": "Logged in as another user",
    "force_logout": "Force logged out a user",
    "password_reset_admin": "Admin-initiated password reset",
    "mfa_disable": "Disabled MFA for a user",
    
    # Financial/Subscription
    "subscription_modify": "Modified user subscription",
    "refund_issue": "Issued a refund",
    "payment_adjust": "Adjusted payment/credits",
    
    # System Maintenance
    "database_maintenance": "Performed database maintenance",
    "cache_clear": "Cleared system cache",
    "service_restart": "Restarted a service",
    "version_release": "Released a new version",
    "auto_fix_trigger": "Triggered system auto-fix"
}

TARGET_TYPES = [
    "user", "job", "application", "subscription", 
    "system", "settings", "report", "payment"
]


# ============== Helper Functions ==============

def is_admin_user(user: dict) -> bool:
    """Check if user has admin access"""
    if not user:
        return False
    return (
        user.get("role") == "admin" or
        user.get("is_admin") or
        "all" in user.get("permissions", [])
    )


async def log_admin_action(
    admin_id: str,
    admin_email: str,
    action: str,
    target_type: str,
    target_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """Log an admin action to the audit trail"""
    try:
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc),
            "admin_id": admin_id,
            "admin_email": admin_email,
            "action": action,
            "action_description": AUDIT_ACTIONS.get(action, action),
            "target_type": target_type,
            "target_id": target_id,
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        await db.admin_audit_logs.insert_one(log_entry)
        logger.info(f"Admin audit: {admin_email} - {action} - {target_type}:{target_id}")
        return log_entry
    except Exception as e:
        logger.error(f"Failed to log admin action: {e}")
        return None


# ============== Routes ==============

@router.get("/status")
async def get_audit_status(request: Request):
    """Get audit logging service status"""
    user = await require_auth(request)
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Count total logs
        total_logs = await db.admin_audit_logs.count_documents({})
        
        # Count logs in last 24 hours
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_logs = await db.admin_audit_logs.count_documents({
            "timestamp": {"$gte": cutoff}
        })
        
        # Get unique admins who have logs
        pipeline = [
            {"$group": {"_id": "$admin_email"}},
            {"$count": "unique_admins"}
        ]
        admin_count = await db.admin_audit_logs.aggregate(pipeline).to_list(1)
        
        return {
            "status": "active",
            "total_logs": total_logs,
            "logs_last_24h": recent_logs,
            "unique_admins": admin_count[0]["unique_admins"] if admin_count else 0,
            "supported_actions": list(AUDIT_ACTIONS.keys()),
            "target_types": TARGET_TYPES
        }
    except Exception as e:
        return {
            "status": "active",
            "error": str(e)
        }


@router.post("/log")
async def create_audit_log(
    request: Request,
    entry: AuditLogEntry
):
    """Manually log an admin action"""
    user = await require_auth(request)
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get request metadata
    forwarded = request.headers.get("X-Forwarded-For")
    ip_address = forwarded.split(",")[0].strip() if forwarded else (
        request.client.host if request.client else "unknown"
    )
    user_agent = request.headers.get("User-Agent", "unknown")
    
    log_entry = await log_admin_action(
        admin_id=user.get("user_id"),
        admin_email=user.get("email"),
        action=entry.action,
        target_type=entry.target_type,
        target_id=entry.target_id,
        details=entry.details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if not log_entry:
        raise HTTPException(status_code=500, detail="Failed to create audit log")
    
    # Remove MongoDB _id for response
    log_entry.pop("_id", None)
    
    return {
        "success": True,
        "log_entry": log_entry
    }


@router.get("/logs")
async def get_audit_logs(
    request: Request,
    admin_id: Optional[str] = None,
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200)
):
    """Get audit logs with filtering and pagination"""
    user = await require_auth(request)
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Build query
    query = {}
    
    if admin_id:
        query["admin_id"] = admin_id
    
    if action:
        query["action"] = action
    
    if target_type:
        query["target_type"] = target_type
    
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            query["timestamp"]["$gte"] = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        if end_date:
            query["timestamp"]["$lte"] = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    
    # Get total count
    total = await db.admin_audit_logs.count_documents(query)
    
    # Get paginated results
    skip = (page - 1) * limit
    cursor = db.admin_audit_logs.find(
        query,
        {"_id": 0}
    ).sort("timestamp", -1).skip(skip).limit(limit)
    
    logs = await cursor.to_list(length=limit)
    
    # Convert datetime to ISO format
    for log in logs:
        if "timestamp" in log:
            log["timestamp"] = log["timestamp"].isoformat()
    
    return {
        "logs": logs,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/logs/{log_id}")
async def get_audit_log_detail(request: Request, log_id: str):
    """Get detailed information about a specific audit log"""
    user = await require_auth(request)
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    log = await db.admin_audit_logs.find_one(
        {"id": log_id},
        {"_id": 0}
    )
    
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    if "timestamp" in log:
        log["timestamp"] = log["timestamp"].isoformat()
    
    return log


@router.get("/summary")
async def get_audit_summary(
    request: Request,
    days: int = Query(default=7, ge=1, le=90)
):
    """Get summary statistics of admin actions"""
    user = await require_auth(request)
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Actions by type
    actions_pipeline = [
        {"$match": {"timestamp": {"$gte": cutoff}}},
        {"$group": {
            "_id": "$action",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    actions_by_type = await db.admin_audit_logs.aggregate(actions_pipeline).to_list(20)
    
    # Actions by admin
    admins_pipeline = [
        {"$match": {"timestamp": {"$gte": cutoff}}},
        {"$group": {
            "_id": "$admin_email",
            "count": {"$sum": 1},
            "last_action": {"$max": "$timestamp"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    actions_by_admin = await db.admin_audit_logs.aggregate(admins_pipeline).to_list(10)
    
    # Actions by target type
    targets_pipeline = [
        {"$match": {"timestamp": {"$gte": cutoff}}},
        {"$group": {
            "_id": "$target_type",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    actions_by_target = await db.admin_audit_logs.aggregate(targets_pipeline).to_list(20)
    
    # Daily activity
    daily_pipeline = [
        {"$match": {"timestamp": {"$gte": cutoff}}},
        {"$group": {
            "_id": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": "$timestamp"
                }
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    daily_activity = await db.admin_audit_logs.aggregate(daily_pipeline).to_list(90)
    
    # Format responses
    for item in actions_by_admin:
        if item.get("last_action"):
            item["last_action"] = item["last_action"].isoformat()
    
    return {
        "time_period_days": days,
        "actions_by_type": [
            {"action": a["_id"], "count": a["count"], 
             "description": AUDIT_ACTIONS.get(a["_id"], a["_id"])}
            for a in actions_by_type
        ],
        "actions_by_admin": [
            {"admin": a["_id"], "count": a["count"], "last_action": a.get("last_action")}
            for a in actions_by_admin
        ],
        "actions_by_target": [
            {"target_type": t["_id"], "count": t["count"]}
            for t in actions_by_target
        ],
        "daily_activity": [
            {"date": d["_id"], "count": d["count"]}
            for d in daily_activity
        ]
    }


@router.get("/export")
async def export_audit_logs(
    request: Request,
    days: int = Query(default=30, ge=1, le=365),
    format: str = Query(default="json", enum=["json", "csv"])
):
    """Export audit logs for compliance/reporting"""
    user = await require_auth(request)
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    cursor = db.admin_audit_logs.find(
        {"timestamp": {"$gte": cutoff}},
        {"_id": 0}
    ).sort("timestamp", -1)
    
    logs = await cursor.to_list(length=10000)
    
    # Convert timestamps
    for log in logs:
        if "timestamp" in log:
            log["timestamp"] = log["timestamp"].isoformat()
    
    # Log this export action
    await log_admin_action(
        admin_id=user.get("user_id"),
        admin_email=user.get("email"),
        action="data_export",
        target_type="report",
        details={
            "export_type": "audit_logs",
            "format": format,
            "days": days,
            "record_count": len(logs)
        }
    )
    
    if format == "csv":
        # Generate CSV content
        import csv
        import io
        
        output = io.StringIO()
        if logs:
            writer = csv.DictWriter(output, fieldnames=logs[0].keys())
            writer.writeheader()
            writer.writerows(logs)
        
        return {
            "format": "csv",
            "record_count": len(logs),
            "content": output.getvalue()
        }
    
    return {
        "format": "json",
        "record_count": len(logs),
        "logs": logs
    }


@router.delete("/logs/cleanup")
async def cleanup_old_logs(
    request: Request,
    days_to_keep: int = Query(default=365, ge=90, le=3650)
):
    """Delete audit logs older than specified days (compliance cleanup)"""
    user = await require_auth(request)
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
    
    # Count logs to be deleted
    count_to_delete = await db.admin_audit_logs.count_documents({
        "timestamp": {"$lt": cutoff}
    })
    
    if count_to_delete == 0:
        return {
            "success": True,
            "deleted_count": 0,
            "message": f"No logs older than {days_to_keep} days found"
        }
    
    # Delete old logs
    result = await db.admin_audit_logs.delete_many({
        "timestamp": {"$lt": cutoff}
    })
    
    # Log this cleanup action
    await log_admin_action(
        admin_id=user.get("user_id"),
        admin_email=user.get("email"),
        action="database_maintenance",
        target_type="system",
        details={
            "maintenance_type": "audit_log_cleanup",
            "days_kept": days_to_keep,
            "deleted_count": result.deleted_count
        }
    )
    
    return {
        "success": True,
        "deleted_count": result.deleted_count,
        "message": f"Deleted {result.deleted_count} logs older than {days_to_keep} days"
    }


@router.post("/database/maintenance")
async def run_database_maintenance(request: Request):
    """Run comprehensive database maintenance: cleanup stale data, verify indexes, report health"""
    user = await require_auth(request)
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    now = datetime.now(timezone.utc)
    results = {"timestamp": now.isoformat(), "actions": []}
    
    # 1. Clean expired sessions
    expired_sessions = await db.user_sessions.delete_many({
        "expires_at": {"$lt": now.isoformat()}
    })
    results["actions"].append({
        "action": "clean_expired_sessions",
        "deleted": expired_sessions.deleted_count
    })
    
    # 2. Clean stale meetings (waiting > 7 days, never started)
    stale_cutoff = (now - timedelta(days=7)).isoformat()
    stale_meetings = await db.karau_meetings.update_many(
        {"status": "waiting", "created_at": {"$lt": stale_cutoff}},
        {"$set": {"status": "expired"}}
    )
    results["actions"].append({
        "action": "expire_stale_meetings",
        "updated": stale_meetings.modified_count
    })
    
    # 3. Clean old ML training data (keep last 30 days)
    ml_cutoff = (now - timedelta(days=30)).isoformat()
    old_ml = await db.ml_training_data.delete_many({
        "timestamp": {"$lt": ml_cutoff}
    })
    results["actions"].append({
        "action": "clean_old_ml_data",
        "deleted": old_ml.deleted_count
    })
    
    # 4. Clean expired OAuth states
    expired_oauth = await db.credly_oauth_states.delete_many({
        "expires_at": {"$lt": now.isoformat()}
    })
    results["actions"].append({
        "action": "clean_expired_oauth",
        "deleted": expired_oauth.deleted_count
    })
    
    # 5. Clean expired WebAuthn challenges
    expired_challenges = await db.webauthn_challenges.delete_many({
        "expires_at": {"$lt": now.isoformat()}
    })
    results["actions"].append({
        "action": "clean_expired_challenges",
        "deleted": expired_challenges.deleted_count
    })
    
    # 6. Ensure critical indexes exist
    indexes_created = []
    try:
        await db.users.create_index("user_id", unique=True)
        indexes_created.append("users.user_id")
    except Exception:
        pass
    try:
        await db.users.create_index("email", unique=True)
        indexes_created.append("users.email")
    except Exception:
        pass
    try:
        await db.user_sessions.create_index("session_token")
        indexes_created.append("user_sessions.session_token")
    except Exception:
        pass
    try:
        await db.user_sessions.create_index("expires_at")
        indexes_created.append("user_sessions.expires_at")
    except Exception:
        pass
    try:
        await db.karau_meetings.create_index("meeting_id", unique=True)
        indexes_created.append("karau_meetings.meeting_id")
    except Exception:
        pass
    try:
        await db.karau_meetings.create_index("host_id")
        indexes_created.append("karau_meetings.host_id")
    except Exception:
        pass
    try:
        await db.applications.create_index("user_id")
        indexes_created.append("applications.user_id")
    except Exception:
        pass
    try:
        await db.ml_training_data.create_index("timestamp")
        indexes_created.append("ml_training_data.timestamp")
    except Exception:
        pass
    try:
        await db.notification_history.create_index([("user_id", 1), ("created_at", -1)])
        indexes_created.append("notification_history.user_id+created_at")
    except Exception:
        pass
    results["actions"].append({
        "action": "ensure_indexes",
        "indexes": indexes_created
    })
    
    # 7. Collection stats
    stats = {}
    for coll_name in ["users", "user_sessions", "karau_meetings", "applications", "ml_training_data"]:
        stats[coll_name] = await db[coll_name].count_documents({})
    results["collection_stats"] = stats
    
    # Log this maintenance action
    await log_admin_action(
        admin_id=user.get("user_id"),
        admin_email=user.get("email"),
        action="database_maintenance",
        target_type="system",
        details=results
    )
    
    return {"success": True, **results}


@router.get("/database/health")
async def get_database_health(request: Request):
    """Get database health report: collection sizes, index status, stale data counts"""
    user = await require_auth(request)
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    now = datetime.now(timezone.utc)
    
    # Collection sizes
    collections = {}
    for name in await db.list_collection_names():
        count = await db[name].count_documents({})
        if count > 0:
            collections[name] = count
    
    # Stale data counts
    stale_data = {
        "expired_sessions": await db.user_sessions.count_documents({
            "expires_at": {"$lt": now.isoformat()}
        }),
        "stale_waiting_meetings": await db.karau_meetings.count_documents({
            "status": "waiting",
            "created_at": {"$lt": (now - timedelta(days=7)).isoformat()}
        }),
        "old_ml_data_30d": await db.ml_training_data.count_documents({
            "timestamp": {"$lt": (now - timedelta(days=30)).isoformat()}
        }),
        "expired_oauth_states": await db.credly_oauth_states.count_documents({
            "expires_at": {"$lt": now.isoformat()}
        }),
    }
    
    # Index info for critical collections
    indexes = {}
    for coll_name in ["users", "user_sessions", "karau_meetings", "applications"]:
        idx_list = await db[coll_name].index_information()
        indexes[coll_name] = list(idx_list.keys())
    
    # ID pattern summary
    total_collections = len(collections)
    total_documents = sum(collections.values())
    
    return {
        "total_collections": total_collections,
        "total_documents": total_documents,
        "collections": dict(sorted(collections.items(), key=lambda x: -x[1])[:20]),
        "stale_data": stale_data,
        "indexes": indexes,
        "recommendations": [
            f"Clean {stale_data['expired_sessions']} expired sessions" if stale_data['expired_sessions'] > 100 else None,
            f"Archive {stale_data['stale_waiting_meetings']} stale meetings" if stale_data['stale_waiting_meetings'] > 10 else None,
            f"Purge {stale_data['old_ml_data_30d']} old ML records" if stale_data['old_ml_data_30d'] > 10000 else None,
        ]
    }
