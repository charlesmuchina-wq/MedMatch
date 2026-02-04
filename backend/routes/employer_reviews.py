"""
Employer Review System
Allows employers/recruiters to leave reviews for candidates after interviews/placements.
Integrates with Trust Score to boost candidate credibility.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid
import logging

from utils.database import db
from routes.auth import get_current_user
from services.trust_score import TrustScoreCalculator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reviews", tags=["Employer Reviews"])

# Initialize trust score calculator for cache invalidation
trust_calculator = TrustScoreCalculator(db)


# ============== Models ==============

class ReviewCreate(BaseModel):
    candidate_id: str
    job_id: Optional[str] = None
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5 stars")
    review_type: str = Field(..., description="interview, placement, general")
    strengths: List[str] = []
    areas_for_improvement: List[str] = []
    comment: Optional[str] = None
    would_hire_again: Optional[bool] = None
    professionalism: Optional[int] = Field(None, ge=1, le=5)
    communication: Optional[int] = Field(None, ge=1, le=5)
    technical_skills: Optional[int] = Field(None, ge=1, le=5)
    reliability: Optional[int] = Field(None, ge=1, le=5)
    is_anonymous: bool = False


class ReviewResponse(BaseModel):
    candidate_id: str
    rating: int = Field(None, ge=1, le=5)
    response_text: str
    is_public: bool = True


# ============== Review Creation ==============

@router.post("/create")
async def create_review(review: ReviewCreate, request: Request):
    """
    Create a review for a candidate.
    Only recruiters who have interacted with the candidate can leave reviews.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Verify user is a recruiter
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can leave reviews")
    
    # Verify candidate exists
    candidate = await db.users.find_one({"user_id": review.candidate_id})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Check for existing review from same recruiter for same job
    if review.job_id:
        existing = await db.employer_reviews.find_one({
            "recruiter_id": user["user_id"],
            "candidate_id": review.candidate_id,
            "job_id": review.job_id
        })
        if existing:
            raise HTTPException(status_code=400, detail="You have already reviewed this candidate for this job")
    
    # Calculate overall score
    scores = [s for s in [review.professionalism, review.communication, 
                          review.technical_skills, review.reliability] if s is not None]
    detailed_avg = sum(scores) / len(scores) if scores else None
    
    review_doc = {
        "id": f"review_{uuid.uuid4().hex[:12]}",
        "recruiter_id": user["user_id"],
        "recruiter_name": user.get("name") if not review.is_anonymous else "Anonymous Employer",
        "recruiter_company": user.get("company_name", ""),
        "candidate_id": review.candidate_id,
        "job_id": review.job_id,
        "rating": review.rating,
        "review_type": review.review_type,
        "strengths": review.strengths,
        "areas_for_improvement": review.areas_for_improvement,
        "comment": review.comment,
        "would_hire_again": review.would_hire_again,
        "detailed_scores": {
            "professionalism": review.professionalism,
            "communication": review.communication,
            "technical_skills": review.technical_skills,
            "reliability": review.reliability,
            "average": round(detailed_avg, 1) if detailed_avg else None
        },
        "is_anonymous": review.is_anonymous,
        "status": "pending",  # pending, approved, rejected
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    
    await db.employer_reviews.insert_one(review_doc)
    
    # Notify candidate
    await db.notifications.insert_one({
        "id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": review.candidate_id,
        "type": "new_review",
        "title": "New Employer Review",
        "message": f"You received a {review.rating}-star review from an employer",
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "success": True,
        "review_id": review_doc["id"],
        "message": "Review submitted and pending approval"
    }


# ============== Review Retrieval ==============

@router.get("/candidate/{candidate_id}")
async def get_candidate_reviews(candidate_id: str, request: Request):
    """
    Get all approved reviews for a candidate.
    Returns summary statistics and individual reviews.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Only approved reviews are shown
    reviews = await db.employer_reviews.find(
        {"candidate_id": candidate_id, "status": "approved"},
        {"_id": 0, "recruiter_id": 0}  # Hide recruiter ID for privacy
    ).to_list(100)
    
    if not reviews:
        return {
            "candidate_id": candidate_id,
            "total_reviews": 0,
            "average_rating": None,
            "reviews": [],
            "summary": None
        }
    
    # Calculate statistics
    ratings = [r["rating"] for r in reviews]
    avg_rating = sum(ratings) / len(ratings)
    
    # Calculate detailed averages
    prof_scores = [r["detailed_scores"]["professionalism"] for r in reviews if r.get("detailed_scores", {}).get("professionalism")]
    comm_scores = [r["detailed_scores"]["communication"] for r in reviews if r.get("detailed_scores", {}).get("communication")]
    tech_scores = [r["detailed_scores"]["technical_skills"] for r in reviews if r.get("detailed_scores", {}).get("technical_skills")]
    rel_scores = [r["detailed_scores"]["reliability"] for r in reviews if r.get("detailed_scores", {}).get("reliability")]
    
    # Count hire again
    hire_again = [r for r in reviews if r.get("would_hire_again") is True]
    
    # Aggregate strengths
    all_strengths = []
    for r in reviews:
        all_strengths.extend(r.get("strengths", []))
    strength_counts = {}
    for s in all_strengths:
        strength_counts[s] = strength_counts.get(s, 0) + 1
    top_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    summary = {
        "average_rating": round(avg_rating, 1),
        "total_reviews": len(reviews),
        "rating_distribution": {
            5: len([r for r in reviews if r["rating"] == 5]),
            4: len([r for r in reviews if r["rating"] == 4]),
            3: len([r for r in reviews if r["rating"] == 3]),
            2: len([r for r in reviews if r["rating"] == 2]),
            1: len([r for r in reviews if r["rating"] == 1]),
        },
        "detailed_averages": {
            "professionalism": round(sum(prof_scores) / len(prof_scores), 1) if prof_scores else None,
            "communication": round(sum(comm_scores) / len(comm_scores), 1) if comm_scores else None,
            "technical_skills": round(sum(tech_scores) / len(tech_scores), 1) if tech_scores else None,
            "reliability": round(sum(rel_scores) / len(rel_scores), 1) if rel_scores else None,
        },
        "would_hire_again_percentage": round((len(hire_again) / len(reviews)) * 100) if reviews else 0,
        "top_strengths": [{"strength": s, "count": c} for s, c in top_strengths],
        "review_types": {
            "interview": len([r for r in reviews if r["review_type"] == "interview"]),
            "placement": len([r for r in reviews if r["review_type"] == "placement"]),
            "general": len([r for r in reviews if r["review_type"] == "general"]),
        }
    }
    
    return {
        "candidate_id": candidate_id,
        "total_reviews": len(reviews),
        "average_rating": round(avg_rating, 1),
        "reviews": reviews,
        "summary": summary
    }


@router.get("/my-reviews")
async def get_my_reviews(request: Request):
    """Get reviews received by the current user (candidate view)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    reviews = await db.employer_reviews.find(
        {"candidate_id": user["user_id"]},
        {"_id": 0, "recruiter_id": 0}
    ).to_list(100)
    
    # Separate by status
    approved = [r for r in reviews if r["status"] == "approved"]
    pending = [r for r in reviews if r["status"] == "pending"]
    
    avg_rating = None
    if approved:
        ratings = [r["rating"] for r in approved]
        avg_rating = round(sum(ratings) / len(ratings), 1)
    
    return {
        "total_reviews": len(reviews),
        "approved_reviews": len(approved),
        "pending_reviews": len(pending),
        "average_rating": avg_rating,
        "reviews": approved,  # Only show approved reviews
        "pending_count": len(pending)
    }


@router.get("/given")
async def get_reviews_given(request: Request):
    """Get reviews given by the current recruiter"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can view given reviews")
    
    reviews = await db.employer_reviews.find(
        {"recruiter_id": user["user_id"]},
        {"_id": 0}
    ).to_list(100)
    
    return {
        "total_given": len(reviews),
        "reviews": reviews
    }


# ============== Candidate Response ==============

@router.post("/respond/{review_id}")
async def respond_to_review(review_id: str, response: ReviewResponse, request: Request):
    """Allow candidate to respond to a review"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    review = await db.employer_reviews.find_one({"id": review_id})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review["candidate_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="You can only respond to your own reviews")
    
    if review.get("candidate_response"):
        raise HTTPException(status_code=400, detail="You have already responded to this review")
    
    await db.employer_reviews.update_one(
        {"id": review_id},
        {"$set": {
            "candidate_response": {
                "text": response.response_text,
                "is_public": response.is_public,
                "responded_at": datetime.now(timezone.utc).isoformat()
            },
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"success": True, "message": "Response added successfully"}


# ============== Admin Moderation ==============

@router.get("/admin/pending")
async def get_pending_reviews(request: Request):
    """Admin: Get all pending reviews for moderation"""
    user = await get_current_user(request)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    reviews = await db.employer_reviews.find(
        {"status": "pending"},
        {"_id": 0}
    ).to_list(100)
    
    return {"pending_reviews": reviews, "total": len(reviews)}


@router.post("/admin/approve/{review_id}")
async def approve_review(review_id: str, request: Request):
    """Admin: Approve a pending review"""
    user = await get_current_user(request)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get the review first to find candidate_id for cache invalidation
    review = await db.employer_reviews.find_one({"id": review_id, "status": "pending"})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found or already processed")
    
    result = await db.employer_reviews.update_one(
        {"id": review_id, "status": "pending"},
        {"$set": {
            "status": "approved",
            "approved_by": user["user_id"],
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Review not found or already processed")
    
    # Invalidate trust score cache for the candidate since reviews affect trust score
    await trust_calculator.invalidate_cache(review["candidate_id"])
    
    return {"success": True, "message": "Review approved"}


@router.post("/admin/reject/{review_id}")
async def reject_review(review_id: str, reason: str, request: Request):
    """Admin: Reject a pending review"""
    user = await get_current_user(request)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.employer_reviews.update_one(
        {"id": review_id, "status": "pending"},
        {"$set": {
            "status": "rejected",
            "rejection_reason": reason,
            "rejected_by": user["user_id"],
            "rejected_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Review not found or already processed")
    
    return {"success": True, "message": "Review rejected"}


@router.get("/admin/stats")
async def get_review_stats(request: Request):
    """Admin: Get review moderation statistics"""
    user = await get_current_user(request)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    pending_count = await db.employer_reviews.count_documents({"status": "pending"})
    approved_count = await db.employer_reviews.count_documents({"status": "approved"})
    rejected_count = await db.employer_reviews.count_documents({"status": "rejected"})
    
    # Recent activity (last 7 days)
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    recent_approved = await db.employer_reviews.count_documents({
        "status": "approved",
        "approved_at": {"$gte": week_ago}
    })
    recent_rejected = await db.employer_reviews.count_documents({
        "status": "rejected",
        "rejected_at": {"$gte": week_ago}
    })
    
    return {
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "recent_activity": {
            "approved_this_week": recent_approved,
            "rejected_this_week": recent_rejected
        }
    }


# ============== Strength/Tag Suggestions ==============

@router.get("/strength-suggestions")
async def get_strength_suggestions():
    """Get predefined strength tags for reviews"""
    return {
        "strengths": [
            "Strong communication skills",
            "Technical expertise",
            "Problem solver",
            "Team player",
            "Reliable and punctual",
            "Fast learner",
            "Attention to detail",
            "Leadership qualities",
            "Adaptable",
            "Professional demeanor",
            "Strong work ethic",
            "Initiative taker",
            "Creative thinker",
            "Well-organized",
            "Domain expertise"
        ],
        "areas_for_improvement": [
            "Communication could improve",
            "Time management",
            "Technical skills development",
            "More proactive approach",
            "Attention to detail",
            "Team collaboration",
            "Meeting deadlines",
            "Documentation skills",
            "Presentation skills",
            "Scope management"
        ]
    }
