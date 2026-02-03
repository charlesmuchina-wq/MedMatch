"""
Interview Funnel Analytics Routes
Tracks: Applications → Callbacks → Interviews → Offers
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone, timedelta

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/funnel")
async def get_interview_funnel(request: Request, days: int = 30):
    """
    Get interview funnel analytics for the current user
    Shows conversion rates at each stage: Applied → Callback → Interview → Offer
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user["user_id"]
    
    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Get all applications in date range
    applications = await db.applications.find({
        "user_id": user_id,
        "applied_at": {"$gte": start_date.isoformat()}
    }, {"_id": 0}).to_list(1000)
    
    # Count by status
    total_applied = len(applications)
    callbacks = sum(1 for app in applications if app.get("status") in ["callback", "screening", "interview_scheduled", "interviewed", "offer", "accepted"])
    interviews = sum(1 for app in applications if app.get("status") in ["interview_scheduled", "interviewed", "offer", "accepted"])
    offers = sum(1 for app in applications if app.get("status") in ["offer", "accepted"])
    accepted = sum(1 for app in applications if app.get("status") == "accepted")
    rejected = sum(1 for app in applications if app.get("status") in ["rejected", "no_response"])
    
    # Calculate conversion rates
    callback_rate = (callbacks / total_applied * 100) if total_applied > 0 else 0
    interview_rate = (interviews / callbacks * 100) if callbacks > 0 else 0
    offer_rate = (offers / interviews * 100) if interviews > 0 else 0
    acceptance_rate = (accepted / offers * 100) if offers > 0 else 0
    overall_success_rate = (offers / total_applied * 100) if total_applied > 0 else 0
    
    # Funnel stages
    funnel = [
        {
            "stage": "Applied",
            "count": total_applied,
            "percentage": 100,
            "color": "#3B82F6"
        },
        {
            "stage": "Callback",
            "count": callbacks,
            "percentage": round(callback_rate, 1),
            "conversion_from_previous": round(callback_rate, 1),
            "color": "#8B5CF6"
        },
        {
            "stage": "Interview",
            "count": interviews,
            "percentage": round((interviews / total_applied * 100) if total_applied > 0 else 0, 1),
            "conversion_from_previous": round(interview_rate, 1),
            "color": "#EC4899"
        },
        {
            "stage": "Offer",
            "count": offers,
            "percentage": round((offers / total_applied * 100) if total_applied > 0 else 0, 1),
            "conversion_from_previous": round(offer_rate, 1),
            "color": "#10B981"
        },
        {
            "stage": "Accepted",
            "count": accepted,
            "percentage": round((accepted / total_applied * 100) if total_applied > 0 else 0, 1),
            "conversion_from_previous": round(acceptance_rate, 1),
            "color": "#20B2AA"
        }
    ]
    
    return {
        "funnel": funnel,
        "summary": {
            "total_applied": total_applied,
            "total_callbacks": callbacks,
            "total_interviews": interviews,
            "total_offers": offers,
            "total_accepted": accepted,
            "total_rejected": rejected,
            "overall_success_rate": round(overall_success_rate, 1),
            "callback_rate": round(callback_rate, 1),
            "interview_rate": round(interview_rate, 1),
            "offer_rate": round(offer_rate, 1)
        },
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "days": days
        }
    }


@router.get("/trends")
async def get_application_trends(request: Request, days: int = 30):
    """
    Get daily application trends over time
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user["user_id"]
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Get applications
    applications = await db.applications.find({
        "user_id": user_id,
        "applied_at": {"$gte": start_date.isoformat()}
    }, {"_id": 0, "applied_at": 1, "status": 1}).to_list(1000)
    
    # Group by date
    daily_counts = {}
    for app in applications:
        date_str = app.get("applied_at", "")[:10]  # Get YYYY-MM-DD
        if date_str:
            if date_str not in daily_counts:
                daily_counts[date_str] = {"applied": 0, "callbacks": 0, "offers": 0}
            daily_counts[date_str]["applied"] += 1
            if app.get("status") in ["callback", "screening", "interview_scheduled", "interviewed", "offer", "accepted"]:
                daily_counts[date_str]["callbacks"] += 1
            if app.get("status") in ["offer", "accepted"]:
                daily_counts[date_str]["offers"] += 1
    
    # Convert to sorted list
    trends = []
    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        data = daily_counts.get(date_str, {"applied": 0, "callbacks": 0, "offers": 0})
        trends.append({
            "date": date_str,
            "display_date": current.strftime("%b %d"),
            **data
        })
        current += timedelta(days=1)
    
    return {
        "trends": trends,
        "totals": {
            "total_applications": sum(t["applied"] for t in trends),
            "total_callbacks": sum(t["callbacks"] for t in trends),
            "total_offers": sum(t["offers"] for t in trends)
        }
    }


@router.get("/by-company")
async def get_analytics_by_company(request: Request, limit: int = 10):
    """
    Get application analytics grouped by company
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user["user_id"]
    
    # Aggregate by company
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$company",
            "total": {"$sum": 1},
            "callbacks": {"$sum": {"$cond": [{"$in": ["$status", ["callback", "screening", "interview_scheduled", "interviewed", "offer", "accepted"]]}, 1, 0]}},
            "interviews": {"$sum": {"$cond": [{"$in": ["$status", ["interview_scheduled", "interviewed", "offer", "accepted"]]}, 1, 0]}},
            "offers": {"$sum": {"$cond": [{"$in": ["$status", ["offer", "accepted"]]}, 1, 0]}},
            "rejected": {"$sum": {"$cond": [{"$in": ["$status", ["rejected", "no_response"]]}, 1, 0]}}
        }},
        {"$sort": {"total": -1}},
        {"$limit": limit}
    ]
    
    results = await db.applications.aggregate(pipeline).to_list(limit)
    
    companies = []
    for r in results:
        company_name = r["_id"] or "Unknown"
        total = r["total"]
        companies.append({
            "company": company_name,
            "total_applications": total,
            "callbacks": r["callbacks"],
            "interviews": r["interviews"],
            "offers": r["offers"],
            "rejected": r["rejected"],
            "success_rate": round((r["offers"] / total * 100) if total > 0 else 0, 1),
            "callback_rate": round((r["callbacks"] / total * 100) if total > 0 else 0, 1)
        })
    
    return {"companies": companies}


@router.get("/by-role")
async def get_analytics_by_role(request: Request, limit: int = 10):
    """
    Get application analytics grouped by job role/title
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user["user_id"]
    
    # Aggregate by role
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$job_title",
            "total": {"$sum": 1},
            "callbacks": {"$sum": {"$cond": [{"$in": ["$status", ["callback", "screening", "interview_scheduled", "interviewed", "offer", "accepted"]]}, 1, 0]}},
            "interviews": {"$sum": {"$cond": [{"$in": ["$status", ["interview_scheduled", "interviewed", "offer", "accepted"]]}, 1, 0]}},
            "offers": {"$sum": {"$cond": [{"$in": ["$status", ["offer", "accepted"]]}, 1, 0]}}
        }},
        {"$sort": {"total": -1}},
        {"$limit": limit}
    ]
    
    results = await db.applications.aggregate(pipeline).to_list(limit)
    
    roles = []
    for r in results:
        role_name = r["_id"] or "Unknown"
        total = r["total"]
        roles.append({
            "role": role_name,
            "total_applications": total,
            "callbacks": r["callbacks"],
            "interviews": r["interviews"],
            "offers": r["offers"],
            "success_rate": round((r["offers"] / total * 100) if total > 0 else 0, 1),
            "callback_rate": round((r["callbacks"] / total * 100) if total > 0 else 0, 1)
        })
    
    return {"roles": roles}


@router.get("/insights")
async def get_ai_insights(request: Request):
    """
    Get AI-generated insights about the user's job search performance
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user["user_id"]
    
    # Get funnel data
    applications = await db.applications.find(
        {"user_id": user_id},
        {"_id": 0, "status": 1, "company": 1, "job_title": 1, "applied_at": 1}
    ).to_list(1000)
    
    total = len(applications)
    if total == 0:
        return {
            "insights": [
                {
                    "type": "info",
                    "icon": "📝",
                    "title": "Start Your Journey",
                    "message": "You haven't applied to any jobs yet. Start by uploading your resume and searching for jobs that match your skills!"
                }
            ],
            "score": 0
        }
    
    callbacks = sum(1 for app in applications if app.get("status") in ["callback", "screening", "interview_scheduled", "interviewed", "offer", "accepted"])
    offers = sum(1 for app in applications if app.get("status") in ["offer", "accepted"])
    
    callback_rate = (callbacks / total * 100) if total > 0 else 0
    offer_rate = (offers / total * 100) if total > 0 else 0
    
    insights = []
    
    # Generate insights based on data
    if callback_rate < 10:
        insights.append({
            "type": "warning",
            "icon": "⚠️",
            "title": "Low Callback Rate",
            "message": f"Your callback rate is {callback_rate:.1f}%. Consider tailoring your resume for each application and writing custom cover letters."
        })
    elif callback_rate >= 20:
        insights.append({
            "type": "success",
            "icon": "🎯",
            "title": "Strong Callback Rate",
            "message": f"Your {callback_rate:.1f}% callback rate is above average! Your resume is resonating with employers."
        })
    
    if total >= 10 and offer_rate == 0:
        insights.append({
            "type": "tip",
            "icon": "💡",
            "title": "Interview Preparation",
            "message": "Try using our AI Interview Prep and Video Practice tools to improve your interview performance."
        })
    
    if offers > 0:
        insights.append({
            "type": "success",
            "icon": "🏆",
            "title": "Congratulations!",
            "message": f"You've received {offers} offer(s)! That's a {offer_rate:.1f}% success rate."
        })
    
    # Calculate job search score (0-100)
    score = min(100, int(
        (callback_rate * 2) +  # Weight callback rate
        (offer_rate * 5) +     # Weight offer rate heavily
        min(20, total)         # Reward activity (max 20 points)
    ))
    
    insights.append({
        "type": "info",
        "icon": "📊",
        "title": "Activity Summary",
        "message": f"You've applied to {total} jobs with {callbacks} callbacks and {offers} offers."
    })
    
    return {
        "insights": insights,
        "score": score,
        "score_breakdown": {
            "activity_points": min(20, total),
            "callback_points": round(callback_rate * 2, 1),
            "offer_points": round(offer_rate * 5, 1)
        }
    }
