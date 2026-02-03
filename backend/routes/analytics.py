"""
Analytics Routes
Handles: Dashboard analytics, application statistics, job market insights
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone, timedelta

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# ============== Routes ==============

@router.get("/dashboard")
async def get_analytics_dashboard(request: Request, days: int = 30):
    """Get comprehensive analytics dashboard data"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user["user_id"]
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    # Application stats
    total_applications = await db.applications.count_documents({"user_id": user_id})
    recent_applications = await db.applications.count_documents({
        "user_id": user_id,
        "applied_at": {"$gte": cutoff_date}
    })
    
    # Application status breakdown
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    status_results = await db.applications.aggregate(pipeline).to_list(20)
    status_breakdown = {item["_id"]: item["count"] for item in status_results}
    
    # Job status breakdown
    job_status_pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$job_status", "count": {"$sum": 1}}}
    ]
    job_status_results = await db.applications.aggregate(job_status_pipeline).to_list(20)
    job_status_breakdown = {item["_id"]: item["count"] for item in job_status_results}
    
    # Applications by source
    source_pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$job.source", "count": {"$sum": 1}}}
    ]
    source_results = await db.applications.aggregate(source_pipeline).to_list(20)
    by_source = {(item["_id"] or "Unknown"): item["count"] for item in source_results}
    
    # Applications over time (last 30 days)
    daily_pipeline = [
        {"$match": {"user_id": user_id, "applied_at": {"$gte": cutoff_date}}},
        {"$project": {
            "date": {"$substr": ["$applied_at", 0, 10]}
        }},
        {"$group": {"_id": "$date", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    daily_results = await db.applications.aggregate(daily_pipeline).to_list(60)
    applications_over_time = [{"date": item["_id"], "count": item["count"]} for item in daily_results]
    
    # Saved jobs count
    saved_jobs_count = await db.saved_jobs.count_documents({"user_id": user_id})
    
    # Cover letters generated
    cover_letters_count = await db.cover_letters.count_documents({"user_id": user_id})
    
    # Interview preps done
    interview_preps_count = await db.interview_questions.count_documents({"user_id": user_id})
    
    # Response rate estimate
    interviews = status_breakdown.get("Interview", 0)
    offers = status_breakdown.get("Offer", 0)
    response_rate = round((interviews + offers) / total_applications * 100, 1) if total_applications > 0 else 0
    
    # Top companies applied to
    company_pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$job.company", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    company_results = await db.applications.aggregate(company_pipeline).to_list(5)
    top_companies = [{"company": item["_id"], "count": item["count"]} for item in company_results if item["_id"]]
    
    # Skills most in demand (from applied jobs)
    skills_pipeline = [
        {"$match": {"user_id": user_id}},
        {"$unwind": {"path": "$job.tags", "preserveNullAndEmptyArrays": True}},
        {"$group": {"_id": "$job.tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    skills_results = await db.applications.aggregate(skills_pipeline).to_list(10)
    in_demand_skills = [{"skill": item["_id"], "count": item["count"]} for item in skills_results if item["_id"]]
    
    return {
        "summary": {
            "total_applications": total_applications,
            "recent_applications": recent_applications,
            "saved_jobs": saved_jobs_count,
            "cover_letters": cover_letters_count,
            "interview_preps": interview_preps_count,
            "response_rate": response_rate
        },
        "status_breakdown": status_breakdown,
        "job_status_breakdown": job_status_breakdown,
        "by_source": by_source,
        "applications_over_time": applications_over_time,
        "top_companies": top_companies,
        "in_demand_skills": in_demand_skills,
        "period_days": days
    }

@router.get("/activity")
async def get_recent_activity(request: Request, limit: int = 20):
    """Get recent user activity"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user["user_id"]
    activities = []
    
    # Recent applications
    recent_apps = await db.applications.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("applied_at", -1).limit(5).to_list(5)
    
    for app in recent_apps:
        activities.append({
            "type": "application",
            "title": f"Applied to {app.get('job', {}).get('title', 'Job')}",
            "subtitle": app.get('job', {}).get('company', ''),
            "timestamp": app.get("applied_at"),
            "id": app.get("id")
        })
    
    # Recent saved jobs
    recent_saved = await db.saved_jobs.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("saved_at", -1).limit(5).to_list(5)
    
    for saved in recent_saved:
        activities.append({
            "type": "saved",
            "title": f"Saved {saved.get('job', {}).get('title', 'Job')}",
            "subtitle": saved.get('job', {}).get('company', ''),
            "timestamp": saved.get("saved_at"),
            "id": saved.get("id")
        })
    
    # Recent cover letters
    recent_letters = await db.cover_letters.find(
        {"user_id": user_id},
        {"_id": 0, "cover_letter": 0}
    ).sort("created_at", -1).limit(3).to_list(3)
    
    for letter in recent_letters:
        activities.append({
            "type": "cover_letter",
            "title": f"Generated cover letter for {letter.get('job_title', 'Job')}",
            "subtitle": letter.get('company', ''),
            "timestamp": letter.get("created_at"),
            "id": letter.get("id")
        })
    
    # Sort all by timestamp
    activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return activities[:limit]

@router.get("/insights")
async def get_job_market_insights(request: Request):
    """Get general job market insights"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # These could be enhanced with real data aggregation
    return {
        "trending_skills": [
            {"skill": "Python", "growth": "+15%"},
            {"skill": "AWS", "growth": "+12%"},
            {"skill": "Machine Learning", "growth": "+20%"},
            {"skill": "React", "growth": "+8%"},
            {"skill": "Data Analysis", "growth": "+18%"}
        ],
        "hot_industries": [
            {"industry": "Healthcare Tech", "openings": "High"},
            {"industry": "FinTech", "openings": "High"},
            {"industry": "AI/ML", "openings": "Very High"},
            {"industry": "Cybersecurity", "openings": "High"}
        ],
        "salary_trends": {
            "tech_avg": "$125,000",
            "remote_premium": "+5-10%",
            "yoy_growth": "+4.5%"
        },
        "application_tips": [
            "Apply within 48 hours of job posting for best results",
            "Customize your resume for each application",
            "Follow up after 1 week if no response",
            "Network on LinkedIn with hiring managers"
        ]
    }

@router.get("/weekly-summary")
async def get_weekly_summary(request: Request):
    """Get weekly activity summary"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user["user_id"]
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    
    # This week's stats
    applications_this_week = await db.applications.count_documents({
        "user_id": user_id,
        "applied_at": {"$gte": week_ago}
    })
    
    saved_this_week = await db.saved_jobs.count_documents({
        "user_id": user_id,
        "saved_at": {"$gte": week_ago}
    })
    
    # Status updates this week
    interviews_this_week = await db.applications.count_documents({
        "user_id": user_id,
        "status": "Interview",
        "updated_at": {"$gte": week_ago}
    })
    
    return {
        "period": "Last 7 days",
        "applications_submitted": applications_this_week,
        "jobs_saved": saved_this_week,
        "interviews_scheduled": interviews_this_week,
        "recommendation": get_weekly_recommendation(applications_this_week)
    }

def get_weekly_recommendation(apps_count: int) -> str:
    """Generate personalized recommendation based on activity"""
    if apps_count == 0:
        return "Time to get started! Set a goal to apply to at least 5 jobs this week."
    elif apps_count < 5:
        return "Good start! Try to increase your applications to 10-15 per week for better results."
    elif apps_count < 15:
        return "Great momentum! Keep it up. Consider using our AI tools to speed up applications."
    else:
        return "Excellent work! Focus on quality applications now and prepare for interviews."
