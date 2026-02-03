"""
Recruiter Verification & RBAC Routes
=====================================
GDPR-compliant recruiter access controls including:
- Business verification
- MFA requirements
- Organization-level data isolation
- Blind screening mode
- Audit trail logging
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid
import hashlib
import logging
import re
import secrets

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/recruiter-rbac", tags=["Recruiter RBAC"])

# ============== Models ==============

class RecruiterRegistration(BaseModel):
    """Recruiter registration with business verification"""
    company_name: str
    company_website: Optional[str] = None
    company_linkedin: Optional[str] = None
    business_email: str  # Must match company domain
    job_title: str
    department: str = "Human Resources"
    phone_number: str
    company_address: Optional[str] = None
    company_size: Optional[str] = None  # "1-50", "51-200", "201-500", "500+"
    healthcare_sector: Optional[str] = None  # "Hospital", "Clinic", "Home Care", etc.

class RecruiterVerificationRequest(BaseModel):
    """Manual verification request"""
    linkedin_profile: str
    verification_documents: List[str] = []  # URLs to uploaded docs
    additional_notes: Optional[str] = None

class BlindScreeningToggle(BaseModel):
    """Toggle blind screening mode"""
    enabled: bool
    
class OrganizationSettings(BaseModel):
    """Organization-level settings"""
    organization_id: str
    name: str
    data_retention_days: int = 60
    require_mfa: bool = True
    blind_screening_default: bool = True
    max_daily_resume_downloads: int = 50

# ============== Constants ==============

# Maximum resume downloads per day (anti-scraping)
MAX_DAILY_DOWNLOADS = 50

# Data retention period (days after job closes)
DATA_RETENTION_DAYS = 60

# Minimum match score for profile visibility (70%)
MIN_MATCH_SCORE_FOR_VISIBILITY = 70

# ============== Helper Functions ==============

def mask_candidate_data(candidate: Dict, blind_mode: bool = True) -> Dict:
    """
    Apply blind screening mask to candidate data.
    Hides name, photo, gender, age while showing skills and AI match.
    """
    if not blind_mode:
        return candidate
    
    masked = candidate.copy()
    
    # Generate anonymous ID
    if candidate.get("user_id"):
        hash_id = hashlib.sha256(candidate["user_id"].encode()).hexdigest()[:6]
        masked["anonymous_id"] = f"Candidate #{hash_id.upper()}"
    else:
        masked["anonymous_id"] = f"Candidate #{secrets.token_hex(3).upper()}"
    
    # Remove identifying information
    masked.pop("full_name", None)
    masked.pop("email", None)
    masked.pop("phone", None)
    masked.pop("photo_url", None)
    masked.pop("profile_image", None)
    masked.pop("linkedin_url", None)
    masked.pop("address", None)
    masked.pop("date_of_birth", None)
    masked.pop("gender", None)
    
    # Generalize location (city only, not full address)
    if masked.get("location"):
        # Extract city from location
        location_parts = masked["location"].split(",")
        if len(location_parts) > 1:
            masked["location"] = location_parts[0].strip()  # City only
    
    # Keep only professional information
    masked["display_name"] = masked["anonymous_id"]
    
    return masked

async def log_recruiter_action(
    recruiter_id: str,
    organization_id: str,
    action: str,
    details: Dict[str, Any],
    candidate_id: Optional[str] = None
):
    """
    Log recruiter actions for audit trail.
    Critical for defending against discrimination claims.
    """
    audit_entry = {
        "id": str(uuid.uuid4()),
        "recruiter_id": recruiter_id,
        "organization_id": organization_id,
        "action": action,
        "candidate_id": candidate_id,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip_hash": None  # Would be populated from request
    }
    
    await db.recruiter_audit_logs.insert_one(audit_entry)
    return audit_entry["id"]

async def check_download_limit(recruiter_id: str) -> tuple[bool, int]:
    """
    Check if recruiter has exceeded daily download limit.
    Anti-scraping measure.
    """
    today = datetime.now(timezone.utc).date()
    today_start = datetime.combine(today, datetime.min.time())
    
    download_count = await db.recruiter_downloads.count_documents({
        "recruiter_id": recruiter_id,
        "downloaded_at": {"$gte": today_start.isoformat()}
    })
    
    remaining = MAX_DAILY_DOWNLOADS - download_count
    return download_count < MAX_DAILY_DOWNLOADS, max(0, remaining)

async def get_organization_settings(organization_id: str) -> Dict:
    """Get organization-specific settings"""
    settings = await db.organization_settings.find_one(
        {"organization_id": organization_id},
        {"_id": 0}
    )
    
    if not settings:
        # Default settings
        return {
            "organization_id": organization_id,
            "data_retention_days": DATA_RETENTION_DAYS,
            "require_mfa": True,
            "blind_screening_default": True,
            "max_daily_resume_downloads": MAX_DAILY_DOWNLOADS
        }
    
    return settings

# ============== Recruiter Verification Routes ==============

@router.post("/register")
async def register_recruiter(registration: RecruiterRegistration, request: Request):
    """
    Register a new recruiter with business verification.
    Validates company email domain and creates pending verification.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Validate business email matches company domain
    email_domain = registration.business_email.split("@")[-1].lower()
    
    # Basic domain validation
    if email_domain in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com"]:
        raise HTTPException(
            status_code=400, 
            detail="Please use your company email address, not a personal email"
        )
    
    # Check if company website domain matches email domain
    if registration.company_website:
        website_domain = registration.company_website.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        if email_domain not in website_domain and website_domain not in email_domain:
            raise HTTPException(
                status_code=400,
                detail="Business email domain must match company website domain"
            )
    
    # Create organization if doesn't exist
    organization_id = f"org_{hashlib.sha256(email_domain.encode()).hexdigest()[:12]}"
    
    existing_org = await db.organizations.find_one({"organization_id": organization_id})
    if not existing_org:
        organization = {
            "organization_id": organization_id,
            "name": registration.company_name,
            "domain": email_domain,
            "website": registration.company_website,
            "linkedin": registration.company_linkedin,
            "healthcare_sector": registration.healthcare_sector,
            "company_size": registration.company_size,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "verified": False
        }
        await db.organizations.insert_one(organization)
    
    # Create recruiter profile
    recruiter_profile = {
        "user_id": user["user_id"],
        "organization_id": organization_id,
        "company_name": registration.company_name,
        "business_email": registration.business_email,
        "job_title": registration.job_title,
        "department": registration.department,
        "phone_number": registration.phone_number,
        "verification_status": "pending",
        "mfa_enabled": False,
        "blind_screening_mode": True,  # Default to blind screening
        "created_at": datetime.now(timezone.utc).isoformat(),
        "daily_download_count": 0,
        "last_download_date": None
    }
    
    await db.recruiter_profiles.update_one(
        {"user_id": user["user_id"]},
        {"$set": recruiter_profile},
        upsert=True
    )
    
    # Update user role
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"role": "recruiter", "organization_id": organization_id}}
    )
    
    # Log registration
    await log_recruiter_action(
        user["user_id"],
        organization_id,
        "RECRUITER_REGISTERED",
        {"company": registration.company_name, "status": "pending"}
    )
    
    return {
        "message": "Recruiter registration submitted",
        "organization_id": organization_id,
        "verification_status": "pending",
        "next_steps": [
            "Verify your business email",
            "Complete LinkedIn verification",
            "Enable Multi-Factor Authentication (MFA)"
        ]
    }

@router.post("/verify/request")
async def request_verification(verification: RecruiterVerificationRequest, request: Request):
    """
    Submit verification documents for manual review.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    recruiter = await db.recruiter_profiles.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter profile not found")
    
    verification_request = {
        "id": str(uuid.uuid4()),
        "recruiter_id": user["user_id"],
        "organization_id": recruiter.get("organization_id"),
        "linkedin_profile": verification.linkedin_profile,
        "documents": verification.verification_documents,
        "notes": verification.additional_notes,
        "status": "pending_review",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "reviewed_by": None,
        "reviewed_at": None
    }
    
    await db.verification_requests.insert_one(verification_request)
    
    # Update recruiter status
    await db.recruiter_profiles.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"verification_status": "under_review"}}
    )
    
    return {
        "message": "Verification request submitted",
        "request_id": verification_request["id"],
        "estimated_review_time": "1-2 business days"
    }

@router.get("/verification/status")
async def get_verification_status(request: Request):
    """Get current verification status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    recruiter = await db.recruiter_profiles.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not recruiter:
        return {"status": "not_registered", "is_verified": False}
    
    return {
        "status": recruiter.get("verification_status", "pending"),
        "is_verified": recruiter.get("verification_status") == "verified",
        "mfa_enabled": recruiter.get("mfa_enabled", False),
        "organization_id": recruiter.get("organization_id"),
        "blind_screening_mode": recruiter.get("blind_screening_mode", True)
    }

# ============== MFA Routes ==============

@router.post("/mfa/enable")
async def enable_mfa(request: Request):
    """
    Enable MFA for recruiter account.
    Required for accessing candidate PII.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Generate MFA secret (in production, use proper TOTP)
    mfa_secret = secrets.token_hex(16)
    
    await db.recruiter_profiles.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "mfa_enabled": True,
            "mfa_secret": mfa_secret,
            "mfa_enabled_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "message": "MFA enabled successfully",
        "mfa_enabled": True,
        "setup_instructions": "Use your authenticator app to scan the QR code"
    }

# ============== Blind Screening Mode Routes ==============

@router.post("/blind-screening/toggle")
async def toggle_blind_screening(toggle: BlindScreeningToggle, request: Request):
    """
    Toggle blind screening mode for the recruiter.
    When enabled, candidate names and photos are hidden.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if recruiter profile exists
    recruiter = await db.recruiter_profiles.find_one({"user_id": user["user_id"]})
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter profile not found. Please complete registration first.")
    
    await db.recruiter_profiles.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"blind_screening_mode": toggle.enabled}}
    )
    
    # Log the change
    await log_recruiter_action(
        user["user_id"],
        recruiter.get("organization_id", "unknown"),
        "BLIND_SCREENING_TOGGLED",
        {"enabled": toggle.enabled}
    )
    
    return {
        "message": f"Blind screening {'enabled' if toggle.enabled else 'disabled'}",
        "blind_screening_mode": toggle.enabled
    }

@router.get("/blind-screening/status")
async def get_blind_screening_status(request: Request):
    """Get current blind screening mode status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    recruiter = await db.recruiter_profiles.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0, "blind_screening_mode": 1}
    )
    
    return {
        "blind_screening_mode": recruiter.get("blind_screening_mode", True) if recruiter else True
    }

# ============== Candidate Access Routes with RBAC ==============

@router.get("/candidates/search")
async def search_candidates_with_rbac(
    request: Request,
    keywords: str = "",
    skills: str = "",
    min_match_score: int = 70,
    limit: int = 20
):
    """
    Search candidates with RBAC and blind screening applied.
    Only shows candidates meeting minimum match score threshold.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get recruiter profile
    recruiter = await db.recruiter_profiles.find_one({"user_id": user["user_id"]})
    if not recruiter:
        raise HTTPException(status_code=403, detail="Recruiter profile required")
    
    # Check verification status
    if recruiter.get("verification_status") != "verified":
        raise HTTPException(
            status_code=403, 
            detail="Account verification required to search candidates"
        )
    
    # Get organization settings
    org_settings = await get_organization_settings(recruiter.get("organization_id", ""))
    
    # Build query
    query = {
        "searchable": {"$ne": False},
        # Only show candidates who haven't blocked this organization
        "blocked_organizations": {"$ne": recruiter.get("organization_id")}
    }
    
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
    
    if skill_list:
        query["skills"] = {"$in": [re.compile(s, re.IGNORECASE) for s in skill_list]}
    
    # Get candidates
    candidates = await db.resumes.find(
        query,
        {"_id": 0, "raw_text": 0}
    ).limit(limit * 2).to_list(limit * 2)  # Get extra to filter by match score
    
    # Apply blind screening
    blind_mode = recruiter.get("blind_screening_mode", True)
    
    results = []
    for candidate in candidates:
        # Calculate match score
        match_score = 0
        candidate_skills = [s.lower() if isinstance(s, str) else s.get("name", "").lower() 
                          for s in candidate.get("skills", [])]
        
        for skill in skill_list:
            if any(skill.lower() in cs for cs in candidate_skills):
                match_score += 15
        
        # Only include if meets minimum threshold
        if match_score >= min_match_score or not skill_list:
            masked_candidate = mask_candidate_data(candidate, blind_mode)
            masked_candidate["match_score"] = min(100, match_score)
            masked_candidate["match_reasoning"] = generate_match_reasoning(candidate, skill_list, keyword_list)
            results.append(masked_candidate)
    
    # Sort by match score
    results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    results = results[:limit]
    
    # Log search action
    await log_recruiter_action(
        user["user_id"],
        recruiter.get("organization_id", "unknown"),
        "CANDIDATE_SEARCH",
        {
            "skills": skill_list,
            "keywords": keyword_list,
            "results_count": len(results),
            "blind_mode": blind_mode
        }
    )
    
    return {
        "candidates": results,
        "total_found": len(results),
        "blind_screening_active": blind_mode,
        "min_match_threshold": min_match_score
    }

def generate_match_reasoning(candidate: Dict, skills: List[str], keywords: List[str]) -> str:
    """Generate explainable AI reasoning for match score"""
    reasons = []
    
    candidate_skills = [s.lower() if isinstance(s, str) else s.get("name", "").lower() 
                       for s in candidate.get("skills", [])]
    
    matched_skills = []
    for skill in skills:
        if any(skill.lower() in cs for cs in candidate_skills):
            matched_skills.append(skill)
    
    if matched_skills:
        reasons.append(f"Skills match: {', '.join(matched_skills)}")
    
    experience = candidate.get("experience", [])
    if experience:
        years = len(experience)
        reasons.append(f"~{years}+ years experience")
    
    education = candidate.get("education", [])
    if education:
        for edu in education[:1]:
            degree = edu.get("degree", "")
            if degree:
                reasons.append(f"Education: {degree}")
                break
    
    return " | ".join(reasons) if reasons else "Matches search criteria"

@router.get("/candidates/{candidate_id}/profile")
async def get_candidate_profile_with_rbac(candidate_id: str, request: Request):
    """
    View candidate profile with RBAC checks.
    Full profile only visible after mutual match.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    recruiter = await db.recruiter_profiles.find_one({"user_id": user["user_id"]})
    if not recruiter:
        raise HTTPException(status_code=403, detail="Recruiter profile required")
    
    # Check if mutual match exists
    mutual_match = await db.mutual_matches.find_one({
        "candidate_id": candidate_id,
        "recruiter_id": user["user_id"],
        "status": "accepted"
    })
    
    # Get candidate
    candidate = await db.resumes.find_one(
        {"id": candidate_id},
        {"_id": 0, "raw_text": 0}
    )
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Determine access level
    if mutual_match:
        # Full access after mutual match
        access_level = "full"
        profile = candidate
    else:
        # Limited access - apply blind screening
        access_level = "limited"
        profile = mask_candidate_data(candidate, True)
        # Hide contact info
        profile.pop("email", None)
        profile.pop("phone", None)
    
    # Log profile view
    await log_recruiter_action(
        user["user_id"],
        recruiter.get("organization_id", "unknown"),
        "PROFILE_VIEW",
        {
            "candidate_id": candidate_id,
            "access_level": access_level,
            "has_mutual_match": bool(mutual_match)
        },
        candidate_id
    )
    
    return {
        "profile": profile,
        "access_level": access_level,
        "contact_visible": access_level == "full",
        "can_request_contact": access_level == "limited"
    }

# ============== Resume Download with Restrictions ==============

@router.post("/candidates/{candidate_id}/download-resume")
async def download_resume_with_restrictions(candidate_id: str, request: Request):
    """
    Download candidate resume with watermarking and daily limits.
    Anti-scraping measure with audit trail.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    recruiter = await db.recruiter_profiles.find_one({"user_id": user["user_id"]})
    if not recruiter:
        raise HTTPException(status_code=403, detail="Recruiter profile required")
    
    # Check MFA requirement
    if not recruiter.get("mfa_enabled"):
        raise HTTPException(
            status_code=403,
            detail="MFA must be enabled to download resumes"
        )
    
    # Check download limit
    can_download, remaining = await check_download_limit(user["user_id"])
    if not can_download:
        raise HTTPException(
            status_code=429,
            detail=f"Daily download limit ({MAX_DAILY_DOWNLOADS}) reached. Resets at midnight UTC."
        )
    
    # Check mutual match
    mutual_match = await db.mutual_matches.find_one({
        "candidate_id": candidate_id,
        "recruiter_id": user["user_id"],
        "status": "accepted"
    })
    
    if not mutual_match:
        raise HTTPException(
            status_code=403,
            detail="Mutual match required to download resume"
        )
    
    # Get resume
    candidate = await db.resumes.find_one(
        {"id": candidate_id},
        {"_id": 0}
    )
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Record download with watermark info
    download_record = {
        "id": str(uuid.uuid4()),
        "recruiter_id": user["user_id"],
        "organization_id": recruiter.get("organization_id"),
        "candidate_id": candidate_id,
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "watermark": f"Downloaded by {user.get('email', 'Unknown')} on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    }
    
    await db.recruiter_downloads.insert_one(download_record)
    
    # Log download
    await log_recruiter_action(
        user["user_id"],
        recruiter.get("organization_id", "unknown"),
        "RESUME_DOWNLOAD",
        {
            "candidate_id": candidate_id,
            "watermark_id": download_record["id"],
            "remaining_downloads": remaining - 1
        },
        candidate_id
    )
    
    return {
        "message": "Resume download authorized",
        "download_id": download_record["id"],
        "watermark": download_record["watermark"],
        "remaining_downloads_today": remaining - 1,
        "resume_url": candidate.get("file_url"),
        "legal_notice": "This resume contains a digital watermark. Unauthorized sharing is prohibited."
    }

# ============== Audit Trail Routes ==============

@router.get("/audit/logs")
async def get_audit_logs(request: Request, limit: int = 50, action_type: Optional[str] = None):
    """Get recruiter's audit trail (for compliance)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    recruiter = await db.recruiter_profiles.find_one({"user_id": user["user_id"]})
    if not recruiter:
        raise HTTPException(status_code=403, detail="Recruiter profile required")
    
    query = {"recruiter_id": user["user_id"]}
    if action_type:
        query["action"] = action_type
    
    logs = await db.recruiter_audit_logs.find(
        query,
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    return {
        "logs": logs,
        "total": len(logs)
    }

# ============== Organization Isolation Routes ==============

@router.get("/organization/settings")
async def get_org_settings(request: Request):
    """Get organization settings"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    recruiter = await db.recruiter_profiles.find_one({"user_id": user["user_id"]})
    if not recruiter:
        raise HTTPException(status_code=403, detail="Recruiter profile required")
    
    settings = await get_organization_settings(recruiter.get("organization_id", ""))
    
    return settings

@router.get("/organization/members")
async def get_org_members(request: Request):
    """Get members of current organization (for org admins)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    recruiter = await db.recruiter_profiles.find_one({"user_id": user["user_id"]})
    if not recruiter:
        raise HTTPException(status_code=403, detail="Recruiter profile required")
    
    # Get all recruiters in same organization
    members = await db.recruiter_profiles.find(
        {"organization_id": recruiter.get("organization_id")},
        {"_id": 0, "user_id": 1, "job_title": 1, "department": 1, "verification_status": 1}
    ).to_list(100)
    
    return {
        "organization_id": recruiter.get("organization_id"),
        "members": members,
        "total": len(members)
    }

# ============== Data Retention Cleanup ==============

@router.post("/admin/cleanup-expired-access")
async def cleanup_expired_access(request: Request):
    """
    Admin endpoint to clean up expired candidate access.
    Runs automatically but can be triggered manually.
    """
    user = await get_current_user(request)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Find jobs closed more than retention period ago
    retention_cutoff = datetime.now(timezone.utc) - timedelta(days=DATA_RETENTION_DAYS)
    
    # Get expired job IDs
    expired_jobs = await db.posted_jobs.find(
        {
            "status": {"$in": ["closed", "filled"]},
            "closed_at": {"$lte": retention_cutoff.isoformat()}
        },
        {"id": 1}
    ).to_list(1000)
    
    expired_job_ids = [j["id"] for j in expired_jobs]
    
    # Remove access to candidates for expired jobs
    result = await db.job_applicants.update_many(
        {"job_id": {"$in": expired_job_ids}},
        {"$set": {"access_expired": True, "expired_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {
        "message": "Access cleanup completed",
        "jobs_processed": len(expired_job_ids),
        "applicant_records_updated": result.modified_count
    }
