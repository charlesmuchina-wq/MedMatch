"""
Company Routes
Handles: Company profiles, employer branding pages
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/companies", tags=["Companies"])

# ============== Models ==============

class CompanyProfile(BaseModel):
    name: str
    description: str
    industry: str
    size: Optional[str] = None  # "1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"
    website: Optional[str] = None
    logo_url: Optional[str] = None
    headquarters: Optional[str] = None
    founded: Optional[str] = None
    specialties: List[str] = []
    benefits: List[str] = []
    culture_values: List[str] = []
    social_links: Optional[dict] = {}

class CompanyReview(BaseModel):
    rating: int  # 1-5
    title: str
    pros: str
    cons: str
    position: Optional[str] = None
    is_current_employee: bool = False
    recommend: bool = True

# ============== Company Profile Routes ==============

@router.post("/")
async def create_company_profile(company: CompanyProfile, request: Request):
    """Create a company profile (recruiters only)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can create company profiles")
    
    # Check if company already exists
    existing = await db.companies.find_one({"name": {"$regex": f"^{company.name}$", "$options": "i"}})
    if existing:
        raise HTTPException(status_code=400, detail="Company profile already exists")
    
    company_doc = {
        "id": f"company_{uuid.uuid4().hex[:12]}",
        "name": company.name,
        "description": company.description,
        "industry": company.industry,
        "size": company.size,
        "website": company.website,
        "logo_url": company.logo_url,
        "headquarters": company.headquarters,
        "founded": company.founded,
        "specialties": company.specialties,
        "benefits": company.benefits,
        "culture_values": company.culture_values,
        "social_links": company.social_links,
        "created_by": user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "verified": False,
        "admins": [user["user_id"]],
        "stats": {
            "total_jobs": 0,
            "total_reviews": 0,
            "average_rating": 0,
            "followers": 0
        }
    }
    
    await db.companies.insert_one(company_doc)
    
    # Link recruiter to this company
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"company_id": company_doc["id"], "company_name": company.name}}
    )
    
    return {"message": "Company profile created", "company_id": company_doc["id"]}

@router.get("/")
async def list_companies(
    industry: Optional[str] = None,
    size: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20
):
    """List all company profiles with optional filters"""
    query = {}
    
    if industry:
        query["industry"] = {"$regex": industry, "$options": "i"}
    
    if size:
        query["size"] = size
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"specialties": {"$in": [search]}}
        ]
    
    companies = await db.companies.find(
        query,
        {"_id": 0}
    ).sort("stats.followers", -1).limit(limit).to_list(limit)
    
    return companies

@router.get("/{company_id}")
async def get_company_profile(company_id: str):
    """Get a specific company profile"""
    company = await db.companies.find_one({"id": company_id}, {"_id": 0})
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Get recent job postings
    jobs = await db.posted_jobs.find(
        {"company": {"$regex": f"^{company['name']}$", "$options": "i"}, "status": "active"},
        {"_id": 0}
    ).limit(10).to_list(10)
    
    company["recent_jobs"] = jobs
    
    return company

@router.put("/{company_id}")
async def update_company_profile(company_id: str, company: CompanyProfile, request: Request):
    """Update company profile (admin only)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if user is admin of this company
    existing = await db.companies.find_one({"id": company_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if user["user_id"] not in existing.get("admins", []):
        raise HTTPException(status_code=403, detail="Not authorized to update this company")
    
    await db.companies.update_one(
        {"id": company_id},
        {"$set": {
            "name": company.name,
            "description": company.description,
            "industry": company.industry,
            "size": company.size,
            "website": company.website,
            "logo_url": company.logo_url,
            "headquarters": company.headquarters,
            "founded": company.founded,
            "specialties": company.specialties,
            "benefits": company.benefits,
            "culture_values": company.culture_values,
            "social_links": company.social_links,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Company profile updated"}

@router.post("/{company_id}/follow")
async def follow_company(company_id: str, request: Request):
    """Follow a company to get job alerts"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check if already following
    existing = await db.company_followers.find_one({
        "company_id": company_id,
        "user_id": user["user_id"]
    })
    
    if existing:
        # Unfollow
        await db.company_followers.delete_one({
            "company_id": company_id,
            "user_id": user["user_id"]
        })
        await db.companies.update_one(
            {"id": company_id},
            {"$inc": {"stats.followers": -1}}
        )
        return {"message": "Unfollowed company", "following": False}
    else:
        # Follow
        await db.company_followers.insert_one({
            "company_id": company_id,
            "user_id": user["user_id"],
            "followed_at": datetime.now(timezone.utc).isoformat()
        })
        await db.companies.update_one(
            {"id": company_id},
            {"$inc": {"stats.followers": 1}}
        )
        return {"message": "Following company", "following": True}

@router.get("/{company_id}/followers")
async def get_company_followers(company_id: str, request: Request):
    """Get follower count (company admins only)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if user["user_id"] not in company.get("admins", []):
        return {"followers": company.get("stats", {}).get("followers", 0)}
    
    # Get detailed follower list for admins
    followers = await db.company_followers.find(
        {"company_id": company_id},
        {"_id": 0}
    ).to_list(1000)
    
    return {
        "followers": len(followers),
        "follower_details": followers if user["user_id"] in company.get("admins", []) else []
    }

# ============== Company Reviews Routes ==============

@router.post("/{company_id}/reviews")
async def add_company_review(company_id: str, review: CompanyReview, request: Request):
    """Add a review for a company (job seekers only)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check if user already reviewed this company
    existing = await db.company_reviews.find_one({
        "company_id": company_id,
        "user_id": user["user_id"]
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this company")
    
    if not 1 <= review.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    review_doc = {
        "id": f"review_{uuid.uuid4().hex[:12]}",
        "company_id": company_id,
        "user_id": user["user_id"],
        "user_name": user.get("name", "Anonymous"),
        "rating": review.rating,
        "title": review.title,
        "pros": review.pros,
        "cons": review.cons,
        "position": review.position,
        "is_current_employee": review.is_current_employee,
        "recommend": review.recommend,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "helpful_count": 0,
        "verified": False
    }
    
    await db.company_reviews.insert_one(review_doc)
    
    # Update company stats
    all_reviews = await db.company_reviews.find({"company_id": company_id}).to_list(1000)
    avg_rating = sum(r["rating"] for r in all_reviews) / len(all_reviews) if all_reviews else 0
    
    await db.companies.update_one(
        {"id": company_id},
        {"$set": {
            "stats.total_reviews": len(all_reviews),
            "stats.average_rating": round(avg_rating, 1)
        }}
    )
    
    return {"message": "Review submitted", "review_id": review_doc["id"]}

@router.get("/{company_id}/reviews")
async def get_company_reviews(company_id: str, limit: int = 20):
    """Get reviews for a company"""
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    reviews = await db.company_reviews.find(
        {"company_id": company_id},
        {"_id": 0, "user_id": 0}  # Hide user_id for privacy
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Calculate rating distribution
    all_ratings = await db.company_reviews.find({"company_id": company_id}, {"rating": 1}).to_list(1000)
    rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in all_ratings:
        rating_dist[r["rating"]] = rating_dist.get(r["rating"], 0) + 1
    
    return {
        "reviews": reviews,
        "total_reviews": len(all_ratings),
        "average_rating": company.get("stats", {}).get("average_rating", 0),
        "rating_distribution": rating_dist,
        "recommend_percentage": round(
            sum(1 for r in reviews if r.get("recommend", False)) / len(reviews) * 100, 1
        ) if reviews else 0
    }

@router.post("/{company_id}/reviews/{review_id}/helpful")
async def mark_review_helpful(company_id: str, review_id: str, request: Request):
    """Mark a review as helpful"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.company_reviews.update_one(
        {"id": review_id, "company_id": company_id},
        {"$inc": {"helpful_count": 1}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return {"message": "Marked as helpful"}
