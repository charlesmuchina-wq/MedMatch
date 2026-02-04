"""
Trust Score Calculator Service
Calculates a comprehensive trust score based on verified credentials,
profile completeness, and platform engagement.
Includes caching for performance optimization.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import logging
import hashlib
import json

logger = logging.getLogger(__name__)

# Cache configuration
TRUST_SCORE_CACHE_TTL = 300  # 5 minutes in seconds
_trust_score_cache: Dict[str, Dict] = {}

# Score weights and points configuration
TRUST_SCORE_CONFIG = {
    # Credential-based points
    "credly_badge": 15,  # Per verified Credly badge
    "credly_badge_max": 75,  # Max points from Credly (5 badges max contribution)
    
    "psv_license": 25,  # Per PSV-verified license
    "psv_license_max": 100,  # Max points from PSV licenses
    
    "manual_credential": 5,  # Per manually added (unverified) credential
    "manual_credential_max": 25,  # Max points from manual credentials
    
    # Profile completeness points
    "profile_name": 5,
    "profile_email_verified": 10,
    "profile_phone": 5,
    "profile_location": 5,
    "profile_bio": 10,
    "profile_photo": 10,
    "profile_linkedin": 10,
    "profile_resume": 20,
    "profile_skills": 15,  # Has at least 5 skills
    
    # Engagement points
    "applications_submitted": 2,  # Per application (max 20)
    "applications_max": 20,
    "interviews_completed": 5,  # Per interview (max 25)
    "interviews_max": 25,
    "offers_received": 10,  # Per offer (max 30)
    "offers_max": 30,
    
    # Platform tenure
    "account_age_30_days": 5,
    "account_age_90_days": 10,
    "account_age_180_days": 15,
    "account_age_365_days": 25,
    
    # Employer reviews
    "employer_review": 10,  # Per positive review
    "employer_review_max": 50,
}

# Trust level thresholds
TRUST_LEVELS = [
    {"min": 0, "max": 49, "level": "Building", "color": "gray", "description": "Just getting started"},
    {"min": 50, "max": 99, "level": "Emerging", "color": "blue", "description": "Profile taking shape"},
    {"min": 100, "max": 149, "level": "Established", "color": "green", "description": "Solid foundation"},
    {"min": 150, "max": 199, "level": "Trusted", "color": "purple", "description": "Well-verified professional"},
    {"min": 200, "max": 249, "level": "Elite", "color": "gold", "description": "Highly credentialed"},
    {"min": 250, "max": 999, "level": "Expert", "color": "platinum", "description": "Top-tier verified talent"},
]


class TrustScoreCalculator:
    """Calculates and manages user trust scores with caching"""
    
    def __init__(self, db):
        self.db = db
        self.config = TRUST_SCORE_CONFIG
    
    def _get_cache_key(self, user_id: str) -> str:
        """Generate cache key for user"""
        return f"trust_score_{user_id}"
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        if not cache_entry:
            return False
        cached_at = cache_entry.get("cached_at")
        if not cached_at:
            return False
        try:
            cached_time = datetime.fromisoformat(cached_at)
            return (datetime.now(timezone.utc) - cached_time).total_seconds() < TRUST_SCORE_CACHE_TTL
        except Exception:
            return False
    
    async def calculate_score(self, user_id: str, bypass_cache: bool = False) -> Dict:
        """
        Calculate comprehensive trust score for a user.
        Uses caching to improve performance (5-minute TTL).
        Returns breakdown of points and overall score.
        """
        global _trust_score_cache
        
        cache_key = self._get_cache_key(user_id)
        
        # Check cache first
        if not bypass_cache and cache_key in _trust_score_cache:
            cache_entry = _trust_score_cache[cache_key]
            if self._is_cache_valid(cache_entry):
                logger.debug(f"Trust score cache hit for user {user_id}")
                cached_result = cache_entry["data"].copy()
                cached_result["from_cache"] = True
                return cached_result
        
        # Calculate fresh score
        logger.debug(f"Calculating fresh trust score for user {user_id}")
        
        breakdown = {
            "credentials": {"points": 0, "details": []},
            "profile": {"points": 0, "details": []},
            "engagement": {"points": 0, "details": []},
            "tenure": {"points": 0, "details": []},
            "reviews": {"points": 0, "details": []},
        }
        
        # Get user data
        user = await self.db.users.find_one({"user_id": user_id})
        if not user:
            return self._build_response(0, breakdown, user_id)
        
        # 1. Credential-based scoring
        credentials = await self.db.user_credentials.find(
            {"user_id": user_id}
        ).to_list(100)
        
        credly_verified = [c for c in credentials if c.get("source") == "credly" and c.get("status") == "verified"]
        psv_verified = [c for c in credentials if c.get("verification_type") == "psv" and c.get("status") == "verified"]
        manual_creds = [c for c in credentials if c.get("source") == "manual"]
        
        # Credly badges
        credly_points = min(len(credly_verified) * self.config["credly_badge"], self.config["credly_badge_max"])
        if credly_points > 0:
            breakdown["credentials"]["points"] += credly_points
            breakdown["credentials"]["details"].append({
                "item": f"{len(credly_verified)} Credly badge(s)",
                "points": credly_points,
                "icon": "award"
            })
        
        # PSV licenses
        psv_points = min(len(psv_verified) * self.config["psv_license"], self.config["psv_license_max"])
        if psv_points > 0:
            breakdown["credentials"]["points"] += psv_points
            breakdown["credentials"]["details"].append({
                "item": f"{len(psv_verified)} PSV-verified license(s)",
                "points": psv_points,
                "icon": "shield-check"
            })
        
        # Manual credentials
        manual_points = min(len(manual_creds) * self.config["manual_credential"], self.config["manual_credential_max"])
        if manual_points > 0:
            breakdown["credentials"]["points"] += manual_points
            breakdown["credentials"]["details"].append({
                "item": f"{len(manual_creds)} manual credential(s)",
                "points": manual_points,
                "icon": "file-text"
            })
        
        # 2. Profile completeness scoring
        profile_points = 0
        
        if user.get("name"):
            profile_points += self.config["profile_name"]
            breakdown["profile"]["details"].append({"item": "Name", "points": self.config["profile_name"], "icon": "user"})
        
        if user.get("email_verified"):
            profile_points += self.config["profile_email_verified"]
            breakdown["profile"]["details"].append({"item": "Email verified", "points": self.config["profile_email_verified"], "icon": "mail-check"})
        
        if user.get("phone"):
            profile_points += self.config["profile_phone"]
            breakdown["profile"]["details"].append({"item": "Phone number", "points": self.config["profile_phone"], "icon": "phone"})
        
        if user.get("location"):
            profile_points += self.config["profile_location"]
            breakdown["profile"]["details"].append({"item": "Location", "points": self.config["profile_location"], "icon": "map-pin"})
        
        if user.get("bio") and len(user.get("bio", "")) > 50:
            profile_points += self.config["profile_bio"]
            breakdown["profile"]["details"].append({"item": "Bio", "points": self.config["profile_bio"], "icon": "align-left"})
        
        if user.get("profile_picture") or user.get("avatar"):
            profile_points += self.config["profile_photo"]
            breakdown["profile"]["details"].append({"item": "Profile photo", "points": self.config["profile_photo"], "icon": "image"})
        
        if user.get("linkedin_url"):
            profile_points += self.config["profile_linkedin"]
            breakdown["profile"]["details"].append({"item": "LinkedIn connected", "points": self.config["profile_linkedin"], "icon": "linkedin"})
        
        # Check for resume
        resume = await self.db.resumes.find_one({"user_id": user_id})
        if resume:
            profile_points += self.config["profile_resume"]
            breakdown["profile"]["details"].append({"item": "Resume uploaded", "points": self.config["profile_resume"], "icon": "file-text"})
            
            if resume.get("skills") and len(resume.get("skills", [])) >= 5:
                profile_points += self.config["profile_skills"]
                breakdown["profile"]["details"].append({"item": "Skills listed (5+)", "points": self.config["profile_skills"], "icon": "zap"})
        
        breakdown["profile"]["points"] = profile_points
        
        # 3. Engagement scoring
        applications = await self.db.applications.find({"user_id": user_id}).to_list(100)
        
        app_points = min(len(applications) * self.config["applications_submitted"], self.config["applications_max"])
        if app_points > 0:
            breakdown["engagement"]["points"] += app_points
            breakdown["engagement"]["details"].append({
                "item": f"{len(applications)} application(s)",
                "points": app_points,
                "icon": "send"
            })
        
        interviews = [a for a in applications if a.get("status") in ["Interview", "Interviewed"]]
        interview_points = min(len(interviews) * self.config["interviews_completed"], self.config["interviews_max"])
        if interview_points > 0:
            breakdown["engagement"]["points"] += interview_points
            breakdown["engagement"]["details"].append({
                "item": f"{len(interviews)} interview(s)",
                "points": interview_points,
                "icon": "video"
            })
        
        offers = [a for a in applications if a.get("status") == "Offer"]
        offer_points = min(len(offers) * self.config["offers_received"], self.config["offers_max"])
        if offer_points > 0:
            breakdown["engagement"]["points"] += offer_points
            breakdown["engagement"]["details"].append({
                "item": f"{len(offers)} offer(s) received",
                "points": offer_points,
                "icon": "gift"
            })
        
        # 4. Account tenure scoring
        created_at = user.get("created_at")
        if created_at:
            try:
                if isinstance(created_at, str):
                    created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                else:
                    created_date = created_at
                
                days_old = (datetime.now(timezone.utc) - created_date).days
                
                if days_old >= 365:
                    tenure_points = self.config["account_age_365_days"]
                    tenure_label = "1+ year member"
                elif days_old >= 180:
                    tenure_points = self.config["account_age_180_days"]
                    tenure_label = "6+ month member"
                elif days_old >= 90:
                    tenure_points = self.config["account_age_90_days"]
                    tenure_label = "3+ month member"
                elif days_old >= 30:
                    tenure_points = self.config["account_age_30_days"]
                    tenure_label = "1+ month member"
                else:
                    tenure_points = 0
                    tenure_label = None
                
                if tenure_points > 0:
                    breakdown["tenure"]["points"] = tenure_points
                    breakdown["tenure"]["details"].append({
                        "item": tenure_label,
                        "points": tenure_points,
                        "icon": "calendar"
                    })
            except Exception as e:
                logger.warning(f"Failed to parse created_at date: {e}")
        
        # 5. Employer reviews (now integrated with employer_reviews collection)
        reviews = await self.db.employer_reviews.find(
            {"candidate_id": user_id, "status": "approved", "rating": {"$gte": 4}}
        ).to_list(20)
        
        review_points = min(len(reviews) * self.config["employer_review"], self.config["employer_review_max"])
        if review_points > 0:
            breakdown["reviews"]["points"] = review_points
            breakdown["reviews"]["details"].append({
                "item": f"{len(reviews)} positive review(s)",
                "points": review_points,
                "icon": "star"
            })
        
        # Calculate total
        total_score = sum(cat["points"] for cat in breakdown.values())
        
        result = self._build_response(total_score, breakdown, user_id)
        
        # Cache the result (using the global declared at function start)
        cache_key = self._get_cache_key(user_id)
        _trust_score_cache[cache_key] = {
            "data": result,
            "cached_at": datetime.now(timezone.utc).isoformat()
        }
        
        result["from_cache"] = False
        return result
    
    async def invalidate_cache(self, user_id: str):
        """Invalidate cached trust score for a user"""
        global _trust_score_cache
        cache_key = self._get_cache_key(user_id)
        if cache_key in _trust_score_cache:
            del _trust_score_cache[cache_key]
            logger.debug(f"Invalidated trust score cache for user {user_id}")
    
    async def record_score_snapshot(self, user_id: str, score_data: Dict):
        """Record a trust score snapshot for history tracking"""
        try:
            snapshot = {
                "user_id": user_id,
                "total_score": score_data.get("total_score", 0),
                "level_name": score_data.get("level", {}).get("name", "Building"),
                "breakdown": score_data.get("breakdown", {}),
                "recorded_at": datetime.now(timezone.utc).isoformat()
            }
            await self.db.trust_score_history.insert_one(snapshot)
            logger.debug(f"Recorded trust score snapshot for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to record score snapshot: {e}")
    
    async def get_score_history(self, user_id: str, days: int = 90) -> List[Dict]:
        """Get trust score history for a user over the specified period"""
        try:
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            cursor = self.db.trust_score_history.find(
                {
                    "user_id": user_id,
                    "recorded_at": {"$gte": cutoff_date}
                },
                {"_id": 0}
            ).sort("recorded_at", 1)
            
            history = await cursor.to_list(length=500)
            return history
        except Exception as e:
            logger.error(f"Failed to get score history: {e}")
            return []
    
    @staticmethod
    def clear_all_cache():
        """Clear entire trust score cache"""
        global _trust_score_cache
        _trust_score_cache = {}
        logger.info("Cleared all trust score cache")
    
    def _build_response(self, total_score: int, breakdown: Dict, user_id: str) -> Dict:
        """Build the complete trust score response"""
        level = self._get_trust_level(total_score)
        
        # Calculate max possible score
        max_score = (
            self.config["credly_badge_max"] +
            self.config["psv_license_max"] +
            self.config["manual_credential_max"] +
            sum([
                self.config["profile_name"],
                self.config["profile_email_verified"],
                self.config["profile_phone"],
                self.config["profile_location"],
                self.config["profile_bio"],
                self.config["profile_photo"],
                self.config["profile_linkedin"],
                self.config["profile_resume"],
                self.config["profile_skills"],
            ]) +
            self.config["applications_max"] +
            self.config["interviews_max"] +
            self.config["offers_max"] +
            self.config["account_age_365_days"] +
            self.config["employer_review_max"]
        )
        
        # Calculate category percentages
        category_max = {
            "credentials": self.config["credly_badge_max"] + self.config["psv_license_max"] + self.config["manual_credential_max"],
            "profile": 90,  # Sum of all profile points
            "engagement": self.config["applications_max"] + self.config["interviews_max"] + self.config["offers_max"],
            "tenure": self.config["account_age_365_days"],
            "reviews": self.config["employer_review_max"],
        }
        
        for category in breakdown:
            max_cat = category_max.get(category, 100)
            breakdown[category]["percentage"] = min(100, int((breakdown[category]["points"] / max_cat) * 100)) if max_cat > 0 else 0
        
        return {
            "user_id": user_id,
            "total_score": total_score,
            "max_score": max_score,
            "percentage": min(100, int((total_score / max_score) * 100)) if max_score > 0 else 0,
            "level": level,
            "breakdown": breakdown,
            "calculated_at": datetime.now(timezone.utc).isoformat(),
            "next_level": self._get_next_level(total_score),
            "improvement_tips": self._get_improvement_tips(breakdown),
        }
    
    def _get_trust_level(self, score: int) -> Dict:
        """Get trust level based on score"""
        for level in TRUST_LEVELS:
            if level["min"] <= score <= level["max"]:
                return {
                    "name": level["level"],
                    "color": level["color"],
                    "description": level["description"],
                    "min_score": level["min"],
                    "max_score": level["max"],
                }
        return TRUST_LEVELS[-1]  # Return highest level if score exceeds all
    
    def _get_next_level(self, current_score: int) -> Optional[Dict]:
        """Get the next level to achieve"""
        for i, level in enumerate(TRUST_LEVELS):
            if current_score < level["max"]:
                if i + 1 < len(TRUST_LEVELS):
                    next_level = TRUST_LEVELS[i + 1]
                    return {
                        "name": next_level["level"],
                        "points_needed": next_level["min"] - current_score,
                        "color": next_level["color"],
                    }
        return None
    
    def _get_improvement_tips(self, breakdown: Dict) -> List[Dict]:
        """Generate personalized improvement tips based on breakdown"""
        tips = []
        
        # Check credentials
        cred_points = breakdown["credentials"]["points"]
        if cred_points < 50:
            tips.append({
                "category": "credentials",
                "tip": "Import badges from Credly to boost your score by up to 75 points",
                "potential_points": 75 - min(cred_points, 75),
                "action": "/credentials",
                "priority": "high"
            })
        
        # Check profile
        profile_points = breakdown["profile"]["points"]
        if profile_points < 70:
            tips.append({
                "category": "profile",
                "tip": "Complete your profile - add bio, photo, and LinkedIn for extra points",
                "potential_points": 90 - profile_points,
                "action": "/settings",
                "priority": "medium"
            })
        
        # Check resume
        has_resume = any(d["item"] == "Resume uploaded" for d in breakdown["profile"]["details"])
        if not has_resume:
            tips.append({
                "category": "profile",
                "tip": "Upload your resume to add 20 points and unlock AI job matching",
                "potential_points": 20,
                "action": "/resume",
                "priority": "high"
            })
        
        # Check engagement
        engagement_points = breakdown["engagement"]["points"]
        if engagement_points < 30:
            tips.append({
                "category": "engagement",
                "tip": "Apply to jobs to demonstrate active job seeking",
                "potential_points": 75 - engagement_points,
                "action": "/search",
                "priority": "low"
            })
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        tips.sort(key=lambda x: priority_order.get(x["priority"], 2))
        
        return tips[:3]  # Return top 3 tips


# Export for use in routes
def get_trust_score_calculator(db):
    return TrustScoreCalculator(db)
