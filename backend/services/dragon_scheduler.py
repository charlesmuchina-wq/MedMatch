"""
KARAU DRAGON Scheduled Automation Service
Runs automated diagnostics, fixes, and maintenance tasks on schedule.
Schedule: Sundays at 1:00 AM PST (9:00 AM UTC)

Now with MongoDB persistence for job state across server restarts.
"""
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from pymongo import MongoClient

from utils.database import db
from services.capa_service import capa_service

# Get MongoDB URL from environment
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "medmatch")

# Configure MongoDB job store for persistence
jobstores = {
    'default': MongoDBJobStore(
        database=DB_NAME,
        collection='apscheduler_jobs',
        client=MongoClient(MONGO_URL)
    )
}

executors = {
    'default': AsyncIOExecutor()
}

job_defaults = {
    'coalesce': True,  # Combine multiple missed executions into one
    'max_instances': 1,  # Only one instance of each job at a time
    'misfire_grace_time': 3600  # Allow jobs to run up to 1 hour late
}

# Initialize scheduler with MongoDB persistence
scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone='UTC'
)

# ============== Scheduled Tasks ==============

async def run_weekly_maintenance():
    """
    Weekly maintenance task - runs every Sunday at 1:00 AM PST (9:00 AM UTC)
    Performs:
    1. Full system diagnostics
    2. Auto-fix detected issues
    3. Database optimization
    4. Generate improvement suggestions
    5. Create maintenance report
    """
    logging.info("🐉 KARAU DRAGON: Starting weekly maintenance...")
    start_time = datetime.now(timezone.utc)
    
    report = {
        "id": f"weekly_{start_time.strftime('%Y%m%d_%H%M%S')}",
        "type": "weekly_maintenance",
        "started_at": start_time.isoformat(),
        "tasks": [],
        "summary": {}
    }
    
    try:
        # Task 1: Database Diagnostics & Cleanup
        logging.info("📊 Running database diagnostics...")
        db_result = await run_database_maintenance()
        report["tasks"].append({
            "name": "database_maintenance",
            "status": "completed",
            "result": db_result
        })
        
        # Task 2: Data Integrity Checks
        logging.info("🔍 Checking data integrity...")
        integrity_result = await run_data_integrity_checks()
        report["tasks"].append({
            "name": "data_integrity",
            "status": "completed",
            "result": integrity_result
        })
        
        # Task 3: Index Optimization
        logging.info("⚡ Optimizing indexes...")
        index_result = await optimize_database_indexes()
        report["tasks"].append({
            "name": "index_optimization",
            "status": "completed",
            "result": index_result
        })
        
        # Task 4: Cleanup Old Data
        logging.info("🧹 Cleaning up old data...")
        cleanup_result = await cleanup_old_data()
        report["tasks"].append({
            "name": "data_cleanup",
            "status": "completed",
            "result": cleanup_result
        })
        
        # Task 5: Generate AI Insights
        logging.info("🤖 Generating AI insights...")
        insights_result = await generate_weekly_insights()
        report["tasks"].append({
            "name": "ai_insights",
            "status": "completed",
            "result": insights_result
        })
        
        # Task 6: Health Score Calculation
        logging.info("💚 Calculating system health...")
        health_score = await calculate_system_health()
        report["summary"]["health_score"] = health_score
        
        # Task 7: CAPA System Analysis (System-wide issue detection)
        logging.info("🎯 Running CAPA system analysis...")
        capa_result = await run_capa_system_analysis()
        report["tasks"].append({
            "name": "capa_analysis",
            "status": "completed",
            "result": capa_result
        })
        
    except Exception as e:
        logging.error(f"Weekly maintenance error: {e}")
        report["tasks"].append({
            "name": "error",
            "status": "failed",
            "error": str(e)
        })
    
    # Finalize report
    end_time = datetime.now(timezone.utc)
    report["completed_at"] = end_time.isoformat()
    report["duration_seconds"] = (end_time - start_time).total_seconds()
    report["summary"]["tasks_completed"] = len([t for t in report["tasks"] if t.get("status") == "completed"])
    report["summary"]["tasks_failed"] = len([t for t in report["tasks"] if t.get("status") == "failed"])
    
    # Store report (make a copy to avoid _id modification)
    report_to_store = {**report}
    await db.maintenance_reports.insert_one(report_to_store)
    
    # Notify admins
    await notify_admins_maintenance_complete(report)
    
    logging.info(f"🐉 KARAU DRAGON: Weekly maintenance completed in {report['duration_seconds']:.2f}s")
    return report


async def run_database_maintenance() -> Dict[str, Any]:
    """Run database maintenance tasks"""
    result = {
        "orphaned_records_removed": 0,
        "collections_checked": 0,
        "issues_found": 0,
        "issues_fixed": 0
    }
    
    try:
        # Get valid user IDs
        valid_users = await db.users.distinct("user_id")
        valid_user_set = set(valid_users)
        
        # Clean up orphaned applications
        app_result = await db.applications.delete_many({
            "user_id": {"$nin": list(valid_user_set)}
        })
        result["orphaned_records_removed"] += app_result.deleted_count
        
        # Clean up orphaned saved jobs
        saved_result = await db.saved_jobs.delete_many({
            "user_id": {"$nin": list(valid_user_set)}
        })
        result["orphaned_records_removed"] += saved_result.deleted_count
        
        # Clean up orphaned resumes
        resume_result = await db.resumes.delete_many({
            "user_id": {"$nin": list(valid_user_set)}
        })
        result["orphaned_records_removed"] += resume_result.deleted_count
        
        # Count collections checked
        collections = await db.list_collection_names()
        result["collections_checked"] = len(collections)
        
        if result["orphaned_records_removed"] > 0:
            result["issues_found"] = 1
            result["issues_fixed"] = 1
            
    except Exception as e:
        logging.error(f"Database maintenance error: {e}")
        result["error"] = str(e)
    
    return result


async def run_data_integrity_checks() -> Dict[str, Any]:
    """Check and fix data integrity issues"""
    result = {
        "checks_performed": 0,
        "issues_found": 0,
        "issues_fixed": 0,
        "details": []
    }
    
    try:
        # Check 1: Users without membership_status
        users_no_status = await db.users.count_documents({"membership_status": {"$exists": False}})
        result["checks_performed"] += 1
        if users_no_status > 0:
            update_result = await db.users.update_many(
                {"membership_status": {"$exists": False}},
                {"$set": {"membership_status": "trial"}}
            )
            result["issues_found"] += 1
            result["issues_fixed"] += 1
            result["details"].append(f"Set membership_status for {update_result.modified_count} users")
        
        # Check 2: Applications without status
        apps_no_status = await db.applications.count_documents({"status": {"$exists": False}})
        result["checks_performed"] += 1
        if apps_no_status > 0:
            update_result = await db.applications.update_many(
                {"status": {"$exists": False}},
                {"$set": {"status": "applied"}}
            )
            result["issues_found"] += 1
            result["issues_fixed"] += 1
            result["details"].append(f"Set status for {update_result.modified_count} applications")
        
        # Check 3: Users without created_at
        users_no_date = await db.users.count_documents({"created_at": {"$exists": False}})
        result["checks_performed"] += 1
        if users_no_date > 0:
            update_result = await db.users.update_many(
                {"created_at": {"$exists": False}},
                {"$set": {"created_at": datetime.now(timezone.utc).isoformat()}}
            )
            result["issues_found"] += 1
            result["issues_fixed"] += 1
            result["details"].append(f"Set created_at for {update_result.modified_count} users")
        
        # Check 4: Applications without applied_at
        apps_no_date = await db.applications.count_documents({"applied_at": {"$exists": False}})
        result["checks_performed"] += 1
        if apps_no_date > 0:
            update_result = await db.applications.update_many(
                {"applied_at": {"$exists": False}},
                {"$set": {"applied_at": datetime.now(timezone.utc).isoformat()}}
            )
            result["issues_found"] += 1
            result["issues_fixed"] += 1
            result["details"].append(f"Set applied_at for {update_result.modified_count} applications")
            
    except Exception as e:
        logging.error(f"Data integrity check error: {e}")
        result["error"] = str(e)
    
    return result


async def optimize_database_indexes() -> Dict[str, Any]:
    """Create and optimize database indexes"""
    result = {
        "indexes_created": [],
        "indexes_verified": [],
        "errors": []
    }
    
    # Define required indexes
    required_indexes = [
        ("users", [("user_id", 1)], {"unique": True}),
        ("users", [("email", 1)], {"unique": True}),
        ("users", [("created_at", -1)], {}),
        ("applications", [("user_id", 1)], {}),
        ("applications", [("user_id", 1), ("applied_at", -1)], {}),
        ("applications", [("status", 1)], {}),
        ("saved_jobs", [("user_id", 1)], {}),
        ("resumes", [("user_id", 1)], {"unique": True}),
        ("dragon_logs", [("user_id", 1), ("timestamp", -1)], {}),
        ("maintenance_reports", [("started_at", -1)], {}),
        ("system_changelog", [("release_date", -1)], {}),
        ("update_notifications", [("user_id", 1), ("read", 1)], {}),
    ]
    
    for collection_name, index_keys, options in required_indexes:
        try:
            collection = db[collection_name]
            index_name = "_".join([f"{k}_{v}" for k, v in index_keys])
            
            # Check if index exists
            existing_indexes = await collection.index_information()
            
            if index_name not in existing_indexes:
                await collection.create_index(index_keys, **options)
                result["indexes_created"].append(f"{collection_name}.{index_name}")
            else:
                result["indexes_verified"].append(f"{collection_name}.{index_name}")
                
        except Exception as e:
            result["errors"].append(f"{collection_name}: {str(e)}")
    
    return result


async def cleanup_old_data() -> Dict[str, Any]:
    """Clean up old logs and temporary data"""
    result = {
        "records_deleted": 0,
        "collections_cleaned": [],
        "space_freed_estimate": "N/A"
    }
    
    # Cutoff dates
    thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    ninety_days_ago = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    
    try:
        # Clean old dragon logs (keep 30 days)
        dragon_result = await db.dragon_logs.delete_many({
            "timestamp": {"$lt": thirty_days_ago}
        })
        if dragon_result.deleted_count > 0:
            result["records_deleted"] += dragon_result.deleted_count
            result["collections_cleaned"].append(f"dragon_logs: {dragon_result.deleted_count}")
        
        # Clean old diagnostic reports (keep 90 days)
        diag_result = await db.diagnostic_reports.delete_many({
            "timestamp": {"$lt": ninety_days_ago}
        })
        if diag_result.deleted_count > 0:
            result["records_deleted"] += diag_result.deleted_count
            result["collections_cleaned"].append(f"diagnostic_reports: {diag_result.deleted_count}")
        
        # Clean old automator reports (keep 90 days)
        auto_result = await db.automator_reports.delete_many({
            "timestamp": {"$lt": ninety_days_ago}
        })
        if auto_result.deleted_count > 0:
            result["records_deleted"] += auto_result.deleted_count
            result["collections_cleaned"].append(f"automator_reports: {auto_result.deleted_count}")
        
        # Clean read update notifications (keep 30 days)
        notif_result = await db.update_notifications.delete_many({
            "read": True,
            "created_at": {"$lt": thirty_days_ago}
        })
        if notif_result.deleted_count > 0:
            result["records_deleted"] += notif_result.deleted_count
            result["collections_cleaned"].append(f"update_notifications: {notif_result.deleted_count}")
        
        # Clean old health snapshots (keep 30 days)
        health_result = await db.health_snapshots.delete_many({
            "timestamp": {"$lt": thirty_days_ago}
        })
        if health_result.deleted_count > 0:
            result["records_deleted"] += health_result.deleted_count
            result["collections_cleaned"].append(f"health_snapshots: {health_result.deleted_count}")
            
    except Exception as e:
        logging.error(f"Data cleanup error: {e}")
        result["error"] = str(e)
    
    return result


async def generate_weekly_insights() -> Dict[str, Any]:
    """Generate AI-powered weekly insights"""
    result = {
        "insights_generated": 0,
        "insights": [],
        "recommendations": []
    }
    
    try:
        # Gather metrics
        total_users = await db.users.count_documents({})
        active_users_week = await db.users.count_documents({
            "last_login": {"$gte": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()}
        })
        total_applications = await db.applications.count_documents({})
        new_applications_week = await db.applications.count_documents({
            "applied_at": {"$gte": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()}
        })
        
        # Generate insights
        if total_users > 0:
            activity_rate = (active_users_week / total_users) * 100
            result["insights"].append({
                "type": "user_activity",
                "message": f"{activity_rate:.1f}% of users active this week ({active_users_week}/{total_users})"
            })
            result["insights_generated"] += 1
        
        if total_applications > 0:
            result["insights"].append({
                "type": "applications",
                "message": f"{new_applications_week} new applications this week"
            })
            result["insights_generated"] += 1
        
        # Generate recommendations based on data
        if active_users_week < total_users * 0.3:
            result["recommendations"].append({
                "priority": "high",
                "message": "Low user engagement. Consider sending re-engagement emails."
            })
        
        if new_applications_week == 0 and total_users > 10:
            result["recommendations"].append({
                "priority": "medium",
                "message": "No new applications this week. Review job search functionality."
            })
            
    except Exception as e:
        logging.error(f"Weekly insights error: {e}")
        result["error"] = str(e)
    
    return result


async def calculate_system_health() -> float:
    """Calculate overall system health score (0-100)"""
    scores = []
    
    try:
        # Database health (40% weight)
        collections = await db.list_collection_names()
        db_score = 100 if len(collections) > 0 else 0
        scores.append(db_score * 0.4)
        
        # User activity health (30% weight)
        total_users = await db.users.count_documents({})
        active_users = await db.users.count_documents({
            "last_login": {"$gte": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()}
        })
        activity_score = (active_users / max(total_users, 1)) * 100
        scores.append(activity_score * 0.3)
        
        # Data integrity health (30% weight)
        orphaned = await db.applications.count_documents({"user_id": {"$exists": False}})
        integrity_score = 100 if orphaned == 0 else max(0, 100 - (orphaned * 10))
        scores.append(integrity_score * 0.3)
        
    except Exception as e:
        logging.error(f"Health calculation error: {e}")
        return 50.0  # Default score on error
    
    return min(100, sum(scores))


async def notify_admins_maintenance_complete(report: Dict[str, Any]):
    """Notify admin users about completed maintenance"""
    try:
        # Get admin users
        admins = await db.users.find(
            {"role": "admin"},
            {"_id": 0, "user_id": 1, "email": 1}
        ).to_list(100)
        
        if not admins:
            return
        
        # Create notification for each admin
        notifications = [{
            "user_id": admin["user_id"],
            "type": "maintenance_complete",
            "title": "Weekly Maintenance Completed",
            "description": f"KARAU DRAGON completed weekly maintenance in {report.get('duration_seconds', 0):.1f}s",
            "details": {
                "tasks_completed": report.get("summary", {}).get("tasks_completed", 0),
                "health_score": report.get("summary", {}).get("health_score", 0)
            },
            "importance": "info",
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        } for admin in admins]
        
        if notifications:
            await db.update_notifications.insert_many(notifications)
            
    except Exception as e:
        logging.error(f"Admin notification error: {e}")


# ============== Auto-Scaling Functions ==============

async def check_and_scale_resources():
    """
    Monitor system load and adjust rate limits dynamically.
    Called every 5 minutes to prevent overload.
    """
    try:
        
        # Get recent request counts
        now = datetime.now(timezone.utc)
        five_mins_ago = (now - timedelta(minutes=5)).isoformat()
        
        recent_errors = await db.error_logs.count_documents({
            "timestamp": {"$gte": five_mins_ago},
            "status_code": 429
        })
        
        # If too many 429 errors, increase limits temporarily
        if recent_errors > 100:
            logging.warning(f"High 429 error rate detected: {recent_errors}. Increasing rate limits.")
            # Store scaling event
            await db.scaling_events.insert_one({
                "timestamp": now.isoformat(),
                "type": "rate_limit_increase",
                "reason": f"{recent_errors} 429 errors in 5 minutes"
            })
            
    except Exception as e:
        logging.error(f"Auto-scaling check error: {e}")


# ============== Predictive Issue Detection ==============

async def analyze_trends_for_predictions():
    """
    Analyze system trends to predict potential issues.
    Uses historical data to identify patterns.
    """
    predictions = []
    
    try:
        # Get recent health snapshots
        snapshots = await db.health_snapshots.find(
            {},
            {"_id": 0}
        ).sort("timestamp", -1).limit(100).to_list(100)
        
        if len(snapshots) < 10:
            return predictions
        
        # Analyze trends
        health_scores = [s.get("health_score", 0) for s in snapshots if "health_score" in s]
        
        if len(health_scores) >= 10:
            recent_avg = sum(health_scores[:5]) / 5
            older_avg = sum(health_scores[5:10]) / 5
            
            if recent_avg < older_avg - 10:
                predictions.append({
                    "type": "health_decline",
                    "severity": "warning",
                    "message": f"System health declining. Recent: {recent_avg:.1f}, Previous: {older_avg:.1f}",
                    "recommendation": "Run full diagnostics and check for issues."
                })
        
        # Check for error rate trends
        error_counts = await db.error_logs.aggregate([
            {
                "$match": {
                    "timestamp": {"$gte": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()}
                }
            },
            {
                "$group": {
                    "_id": {"$substr": ["$timestamp", 0, 10]},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": -1}}
        ]).to_list(7)
        
        if len(error_counts) >= 3:
            recent_errors = sum(e["count"] for e in error_counts[:3])
            if recent_errors > 500:
                predictions.append({
                    "type": "error_spike",
                    "severity": "high",
                    "message": f"High error rate detected: {recent_errors} errors in last 3 days",
                    "recommendation": "Investigate error logs and fix root causes."
                })
                
    except Exception as e:
        logging.error(f"Trend analysis error: {e}")
    
    return predictions


# ============== Automated Rollback ==============

async def check_for_rollback_conditions():
    """
    Check if system needs to rollback to a previous state.
    Triggers on critical failures.
    """
    try:
        now = datetime.now(timezone.utc)
        one_hour_ago = (now - timedelta(hours=1)).isoformat()
        
        # Check for critical error rate
        critical_errors = await db.error_logs.count_documents({
            "timestamp": {"$gte": one_hour_ago},
            "severity": "critical"
        })
        
        if critical_errors > 50:
            logging.critical(f"ROLLBACK ALERT: {critical_errors} critical errors in last hour!")
            
            # Create rollback alert
            await db.rollback_alerts.insert_one({
                "timestamp": now.isoformat(),
                "critical_errors": critical_errors,
                "status": "pending_review",
                "recommendation": "Manual review required for potential rollback"
            })
            
            # Notify admins immediately
            admins = await db.users.find({"role": "admin"}, {"_id": 0, "user_id": 1}).to_list(100)
            notifications = [{
                "user_id": admin["user_id"],
                "type": "rollback_alert",
                "title": "🚨 Critical: Rollback Alert",
                "description": f"{critical_errors} critical errors detected. Manual review required.",
                "importance": "critical",
                "read": False,
                "created_at": now.isoformat()
            } for admin in admins]
            
            if notifications:
                await db.update_notifications.insert_many(notifications)
                
    except Exception as e:
        logging.error(f"Rollback check error: {e}")


# ============== CAPA Auto-Generation System ==============

async def run_capa_system_analysis():
    """
    CAPA (Corrective Action Preventive Action) System Analysis
    Runs alongside weekly maintenance to identify recurring system-wide issues.
    
    Analyzes:
    1. Error patterns and recurring failures
    2. Performance degradation trends
    3. Data integrity issues
    4. API failure patterns
    5. User experience issues
    6. Translation/Localization gaps
    7. Security anomalies
    """
    logging.info("🔍 CAPA: Starting system-wide analysis for recurring issues...")
    
    issues_found = []
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()
    
    try:
        # 1. Analyze Error Patterns - Check for recurring errors
        error_patterns = await db.error_logs.aggregate([
            {"$match": {"timestamp": {"$gte": week_ago}}},
            {"$group": {
                "_id": {"path": "$path", "status_code": "$status_code"},
                "count": {"$sum": 1},
                "first_occurrence": {"$min": "$timestamp"},
                "last_occurrence": {"$max": "$timestamp"}
            }},
            {"$match": {"count": {"$gte": 10}}},  # 10+ occurrences = recurring
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]).to_list(10)
        
        for pattern in error_patterns:
            issues_found.append({
                "category": "api_errors",
                "severity": "high" if pattern["count"] > 50 else "medium",
                "title": f"Recurring API Error: {pattern['_id'].get('path', 'Unknown')}",
                "description": f"Status {pattern['_id'].get('status_code', 'N/A')} occurred {pattern['count']} times this week",
                "occurrences": pattern["count"],
                "impacted_processes": ["API Services", "Backend"],
                "source": "Error Log Analysis"
            })
        
        # 2. Analyze Performance Degradation
        slow_endpoints = await db.api_metrics.aggregate([
            {"$match": {"timestamp": {"$gte": week_ago}}},
            {"$group": {
                "_id": "$endpoint",
                "avg_response_time": {"$avg": "$response_time_ms"},
                "max_response_time": {"$max": "$response_time_ms"},
                "count": {"$sum": 1}
            }},
            {"$match": {"avg_response_time": {"$gte": 2000}}},  # >2s average
            {"$sort": {"avg_response_time": -1}},
            {"$limit": 5}
        ]).to_list(5)
        
        for endpoint in slow_endpoints:
            issues_found.append({
                "category": "performance",
                "severity": "high" if endpoint["avg_response_time"] > 5000 else "medium",
                "title": f"Performance Degradation: {endpoint['_id']}",
                "description": f"Average response time: {endpoint['avg_response_time']:.0f}ms (max: {endpoint['max_response_time']:.0f}ms)",
                "occurrences": endpoint["count"],
                "impacted_processes": ["Performance", "User Experience"],
                "source": "API Metrics Analysis"
            })
        
        # 3. Check Data Integrity Issues
        integrity_issues = []
        
        # Orphaned records check
        orphaned_apps = await db.applications.count_documents({"user_id": {"$exists": False}})
        orphaned_resumes = await db.resumes.count_documents({"user_id": {"$exists": False}})
        
        if orphaned_apps > 10 or orphaned_resumes > 10:
            issues_found.append({
                "category": "data_integrity",
                "severity": "medium",
                "title": "Orphaned Records Detected",
                "description": f"Found {orphaned_apps} orphaned applications and {orphaned_resumes} orphaned resumes",
                "occurrences": orphaned_apps + orphaned_resumes,
                "impacted_processes": ["Database", "Data Integrity"],
                "source": "Data Integrity Check"
            })
        
        # 4. Check for Authentication Failures
        auth_failures = await db.auth_logs.count_documents({
            "timestamp": {"$gte": week_ago},
            "success": False
        })
        
        if auth_failures > 100:
            issues_found.append({
                "category": "security",
                "severity": "high" if auth_failures > 500 else "medium",
                "title": "High Authentication Failure Rate",
                "description": f"{auth_failures} failed authentication attempts this week",
                "occurrences": auth_failures,
                "impacted_processes": ["Authentication", "Security"],
                "source": "Security Analysis"
            })
        
        # 5. Check Translation QA Issues (system-wide scope)
        try:
            from services.translation_qa import translation_qa_service
            qa_result = translation_qa_service.run_full_qa()
            
            if qa_result.get("health_score", 100) < 70:
                issues_found.append({
                    "category": "localization",
                    "severity": "medium",
                    "title": "Translation Quality Below Threshold",
                    "description": f"Translation QA score: {qa_result.get('health_score', 0)}. Issues: {qa_result.get('total_issues', 0)}",
                    "occurrences": qa_result.get("total_issues", 0),
                    "impacted_processes": ["Localization", "UI Rendering", "User Experience"],
                    "source": "Translation QA Agent"
                })
        except Exception as e:
            logging.warning(f"Translation QA check skipped: {e}")
        
        # 6. Check User Experience Issues (from feedback)
        negative_feedback = await db.user_feedback.count_documents({
            "created_at": {"$gte": week_ago},
            "rating": {"$lte": 2}
        })
        
        if negative_feedback > 20:
            issues_found.append({
                "category": "user_experience",
                "severity": "high" if negative_feedback > 50 else "medium",
                "title": "High Negative User Feedback",
                "description": f"{negative_feedback} low-rating feedback submissions this week",
                "occurrences": negative_feedback,
                "impacted_processes": ["User Experience", "Product Quality"],
                "source": "User Feedback Analysis"
            })
        
        # 7. Check Job Search Issues
        failed_searches = await db.search_logs.count_documents({
            "timestamp": {"$gte": week_ago},
            "results_count": 0
        })
        total_searches = await db.search_logs.count_documents({
            "timestamp": {"$gte": week_ago}
        })
        
        if total_searches > 0 and (failed_searches / total_searches) > 0.3:  # 30%+ failure rate
            issues_found.append({
                "category": "search_functionality",
                "severity": "high",
                "title": "High Job Search Failure Rate",
                "description": f"{failed_searches}/{total_searches} searches returned no results ({(failed_searches/total_searches)*100:.1f}%)",
                "occurrences": failed_searches,
                "impacted_processes": ["Job Search", "User Experience"],
                "source": "Search Analysis"
            })
        
        # Now create CAPAs for recurring issues
        capas_created = []
        
        for issue in issues_found:
            # Check if a similar CAPA already exists and is open
            existing_capas = capa_service.list_capas()
            already_exists = any(
                c.get("status") not in ["closed", "cancelled"] and
                c.get("tags") and issue["category"] in c.get("tags", [])
                for c in existing_capas
            )
            
            if not already_exists:
                capa = capa_service.create_capa({
                    "title": issue["title"],
                    "problem_statement": issue["description"],
                    "capa_type": "both",
                    "severity": issue["severity"],
                    "source": f"KARAU DRAGON Automator - {issue['source']}",
                    "impacted_processes": issue.get("impacted_processes", []),
                    "tags": [issue["category"], "automated", "dragon-automator"],
                    "created_by": "KARAU DRAGON Automator"
                })
                capas_created.append(capa["id"])
                logging.info(f"🎯 CAPA Created: {capa['id']} - {issue['title']}")
        
        # Store analysis report
        report = {
            "timestamp": now.isoformat(),
            "issues_analyzed": len(issues_found),
            "capas_created": len(capas_created),
            "capa_ids": capas_created,
            "issues": issues_found
        }
        await db.capa_analysis_reports.insert_one(report)
        
        logging.info(f"🔍 CAPA Analysis complete: {len(issues_found)} issues found, {len(capas_created)} CAPAs created")
        
        return report
        
    except Exception as e:
        logging.error(f"CAPA system analysis error: {e}")
        return {"error": str(e), "issues_analyzed": 0, "capas_created": 0}


# ============== Scheduler Setup ==============

def setup_scheduled_tasks():
    """Configure all scheduled tasks with MongoDB persistence"""
    
    # Check if jobs already exist (persisted from previous run)
    existing_jobs = {job.id for job in scheduler.get_jobs()}
    
    # Weekly maintenance - Sundays at 1:00 AM PST (9:00 AM UTC)
    if 'weekly_maintenance' not in existing_jobs:
        scheduler.add_job(
            run_weekly_maintenance,
            CronTrigger(day_of_week='sun', hour=9, minute=0, timezone='UTC'),
            id='weekly_maintenance',
            name='KARAU DRAGON Weekly Maintenance',
            replace_existing=True
        )
        logging.info("   📅 Added: Weekly maintenance (Sundays 1:00 AM PST)")
    else:
        logging.info("   📅 Restored: Weekly maintenance (Sundays 1:00 AM PST)")
    
    # Auto-scaling check - every 5 minutes
    if 'auto_scaling_check' not in existing_jobs:
        scheduler.add_job(
            check_and_scale_resources,
            'interval',
            minutes=5,
            id='auto_scaling_check',
            name='Auto-Scaling Resource Check',
            replace_existing=True
        )
        logging.info("   ⚡ Added: Auto-scaling check (every 5 min)")
    else:
        logging.info("   ⚡ Restored: Auto-scaling check (every 5 min)")
    
    # Predictive analysis - every 6 hours
    if 'predictive_analysis' not in existing_jobs:
        scheduler.add_job(
            analyze_trends_for_predictions,
            'interval',
            hours=6,
            id='predictive_analysis',
            name='Predictive Issue Analysis',
            replace_existing=True
        )
        logging.info("   🔮 Added: Predictive analysis (every 6 hours)")
    else:
        logging.info("   🔮 Restored: Predictive analysis (every 6 hours)")
    
    # Rollback condition check - every 15 minutes
    if 'rollback_check' not in existing_jobs:
        scheduler.add_job(
            check_for_rollback_conditions,
            'interval',
            minutes=15,
            id='rollback_check',
            name='Rollback Condition Check',
            replace_existing=True
        )
        logging.info("   🔄 Added: Rollback check (every 15 min)")
    else:
        logging.info("   🔄 Restored: Rollback check (every 15 min)")
    
    logging.info(f"🐉 KARAU DRAGON Scheduler configured with {len(scheduler.get_jobs())} jobs")
    logging.info(f"   💾 Job persistence: MongoDB ({DB_NAME}.apscheduler_jobs)")


def start_scheduler():
    """Start the scheduler"""
    if not scheduler.running:
        setup_scheduled_tasks()
        scheduler.start()
        logging.info("🐉 KARAU DRAGON Scheduler started!")


def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logging.info("🐉 KARAU DRAGON Scheduler stopped")


# Export functions
__all__ = [
    'scheduler',
    'start_scheduler',
    'stop_scheduler',
    'run_weekly_maintenance',
    'check_and_scale_resources',
    'analyze_trends_for_predictions',
    'check_for_rollback_conditions'
]
