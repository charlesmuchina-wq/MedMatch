"""
Company Feedback Learning Routes
Handles: Rejection feedback from recruiters, AI learning from feedback, insights for job seekers
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import logging
import json

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user

router = APIRouter(prefix="/feedback", tags=["Feedback Learning"])

# ============== Models ==============

class RejectionFeedback(BaseModel):
    application_id: str
    candidate_id: str
    job_id: str
    feedback_type: str  # skills_gap, experience_mismatch, culture_fit, salary_mismatch, overqualified, underqualified, other
    specific_skills_missing: Optional[List[str]] = []
    experience_gap: Optional[str] = None
    additional_notes: Optional[str] = None
    would_consider_for_other_roles: bool = False
    suggested_improvements: Optional[List[str]] = []

class FeedbackCategory(BaseModel):
    category: str
    description: str
    count: int
    percentage: float

# ============== Feedback Categories ==============

FEEDBACK_CATEGORIES = {
    "skills_gap": "Missing required technical or soft skills",
    "experience_mismatch": "Experience level doesn't match job requirements",
    "culture_fit": "May not align with company culture or values",
    "salary_mismatch": "Salary expectations don't align with budget",
    "overqualified": "Candidate is overqualified for the position",
    "underqualified": "Candidate needs more experience/education",
    "location": "Geographic or remote work constraints",
    "communication": "Communication skills need improvement",
    "portfolio": "Portfolio/work samples didn't meet expectations",
    "other": "Other reasons"
}

# ============== Recruiter Feedback Submission ==============

@router.post("/rejection")
async def submit_rejection_feedback(feedback: RejectionFeedback, request: Request):
    """Recruiter submits feedback on why a candidate was rejected"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can submit feedback")
    
    if feedback.feedback_type not in FEEDBACK_CATEGORIES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid feedback type. Must be one of: {list(FEEDBACK_CATEGORIES.keys())}"
        )
    
    feedback_doc = {
        "id": f"feedback_{uuid.uuid4().hex[:12]}",
        "application_id": feedback.application_id,
        "candidate_id": feedback.candidate_id,
        "job_id": feedback.job_id,
        "recruiter_id": user["user_id"],
        "feedback_type": feedback.feedback_type,
        "feedback_category_description": FEEDBACK_CATEGORIES[feedback.feedback_type],
        "specific_skills_missing": feedback.specific_skills_missing,
        "experience_gap": feedback.experience_gap,
        "additional_notes": feedback.additional_notes,
        "would_consider_for_other_roles": feedback.would_consider_for_other_roles,
        "suggested_improvements": feedback.suggested_improvements,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "is_anonymous": True  # Always anonymous to candidates
    }
    
    await db.rejection_feedback.insert_one(feedback_doc)
    
    # Update application with feedback flag
    await db.job_applicants.update_one(
        {"id": feedback.application_id},
        {"$set": {
            "has_feedback": True,
            "feedback_type": feedback.feedback_type,
            "feedback_submitted_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Update candidate's feedback history (aggregated, anonymous)
    await update_candidate_feedback_stats(feedback.candidate_id, feedback.feedback_type)
    
    return {
        "message": "Feedback submitted successfully",
        "feedback_id": feedback_doc["id"]
    }

async def update_candidate_feedback_stats(candidate_id: str, feedback_type: str):
    """Update aggregated feedback statistics for a candidate"""
    await db.candidate_feedback_stats.update_one(
        {"candidate_id": candidate_id},
        {
            "$inc": {
                f"feedback_counts.{feedback_type}": 1,
                "total_feedback_count": 1
            },
            "$set": {
                "last_updated": datetime.now(timezone.utc).isoformat()
            },
            "$setOnInsert": {
                "candidate_id": candidate_id,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )

# ============== Feedback Categories ==============

@router.get("/categories")
async def get_feedback_categories():
    """Get all available feedback categories"""
    return {
        "categories": [
            {"id": key, "name": key.replace("_", " ").title(), "description": desc}
            for key, desc in FEEDBACK_CATEGORIES.items()
        ]
    }

# ============== Job Seeker Insights ==============

@router.get("/insights")
async def get_candidate_insights(request: Request):
    """Get aggregated, anonymous feedback insights for job seeker"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get candidate's feedback stats
    stats = await db.candidate_feedback_stats.find_one(
        {"candidate_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not stats or stats.get("total_feedback_count", 0) == 0:
        return {
            "has_feedback": False,
            "message": "No feedback received yet. Keep applying!",
            "insights": None
        }
    
    total = stats.get("total_feedback_count", 0)
    feedback_counts = stats.get("feedback_counts", {})
    
    # Calculate percentages and create insights
    insights = []
    for feedback_type, count in feedback_counts.items():
        if count > 0:
            percentage = (count / total) * 100
            insights.append({
                "category": feedback_type.replace("_", " ").title(),
                "description": FEEDBACK_CATEGORIES.get(feedback_type, ""),
                "count": count,
                "percentage": round(percentage, 1)
            })
    
    # Sort by percentage descending
    insights.sort(key=lambda x: x["percentage"], reverse=True)
    
    # Generate AI improvement suggestions if enough feedback
    improvement_suggestions = []
    if total >= 3 and EMERGENT_LLM_KEY:
        improvement_suggestions = await generate_improvement_suggestions(insights, user["user_id"])
    
    return {
        "has_feedback": True,
        "total_applications_with_feedback": total,
        "insights": insights,
        "top_area_for_improvement": insights[0]["category"] if insights else None,
        "improvement_suggestions": improvement_suggestions,
        "last_updated": stats.get("last_updated")
    }

async def generate_improvement_suggestions(insights: List[dict], user_id: str) -> List[str]:
    """Generate AI-powered improvement suggestions based on feedback patterns"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        # Get user's resume for context
        resume = await db.resumes.find_one({"user_id": user_id}, {"_id": 0})
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message="""You are a career coach providing actionable improvement suggestions.
Based on the feedback patterns from recruiters, provide 3-5 specific, actionable suggestions.
Be encouraging and constructive. Focus on what the candidate can actually improve.
Return ONLY a JSON array of strings, each being one suggestion."""
        ).with_model("openai", "gpt-5.2")
        
        context = f"""
Feedback patterns received:
{json.dumps(insights, indent=2)}

Candidate skills: {', '.join(resume.get('skills', [])[:20]) if resume else 'Unknown'}

Based on this feedback, what specific improvements would you suggest?
"""
        
        response = await chat.send_message(UserMessage(text=context))
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        suggestions = json.loads(clean_response)
        return suggestions if isinstance(suggestions, list) else []
        
    except Exception as e:
        logging.error(f"Failed to generate improvement suggestions: {e}")
        return []

# ============== Industry Benchmarks ==============

@router.get("/benchmarks")
async def get_industry_benchmarks(request: Request):
    """Get anonymous industry-wide feedback benchmarks"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Aggregate all feedback across the platform
    pipeline = [
        {"$group": {
            "_id": "$feedback_type",
            "count": {"$sum": 1}
        }}
    ]
    
    results = await db.rejection_feedback.aggregate(pipeline).to_list(100)
    
    total = sum(r["count"] for r in results)
    if total == 0:
        return {
            "has_data": False,
            "message": "Not enough data for benchmarks yet"
        }
    
    benchmarks = [
        {
            "category": r["_id"].replace("_", " ").title(),
            "description": FEEDBACK_CATEGORIES.get(r["_id"], ""),
            "percentage": round((r["count"] / total) * 100, 1)
        }
        for r in results
    ]
    
    benchmarks.sort(key=lambda x: x["percentage"], reverse=True)
    
    return {
        "has_data": True,
        "total_feedback_collected": total,
        "benchmarks": benchmarks,
        "insight": f"The most common rejection reason across all candidates is '{benchmarks[0]['category']}' at {benchmarks[0]['percentage']}%." if benchmarks else ""
    }

# ============== Feedback for Specific Application ==============

@router.get("/application/{application_id}")
async def get_application_feedback(application_id: str, request: Request):
    """Get feedback for a specific application (recruiter only)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can view detailed feedback")
    
    feedback = await db.rejection_feedback.find_one(
        {"application_id": application_id, "recruiter_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not feedback:
        return {"has_feedback": False}
    
    return {
        "has_feedback": True,
        "feedback": feedback
    }

# ============== Feedback Analytics for Recruiters ==============

@router.get("/recruiter/analytics")
async def get_recruiter_feedback_analytics(request: Request):
    """Get feedback analytics for recruiter's hiring patterns"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can view analytics")
    
    # Get feedback distribution for this recruiter
    pipeline = [
        {"$match": {"recruiter_id": user["user_id"]}},
        {"$group": {
            "_id": "$feedback_type",
            "count": {"$sum": 1}
        }}
    ]
    
    results = await db.rejection_feedback.aggregate(pipeline).to_list(100)
    
    total = sum(r["count"] for r in results)
    
    distribution = [
        {
            "category": r["_id"].replace("_", " ").title(),
            "count": r["count"],
            "percentage": round((r["count"] / total) * 100, 1) if total > 0 else 0
        }
        for r in results
    ]
    
    distribution.sort(key=lambda x: x["count"], reverse=True)
    
    return {
        "total_feedback_given": total,
        "distribution": distribution,
        "insight": f"You most commonly reject candidates for '{distribution[0]['category']}' ({distribution[0]['percentage']}%)." if distribution else "Start providing feedback to see insights."
    }
