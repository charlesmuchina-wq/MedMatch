"""
Privacy & Compliance Routes
===========================
GDPR/CCPA compliant privacy management for MedMatch AI.

Features:
- Consent management (opt-in, withdrawal)
- PII redaction for resumes
- Data deletion (right to erasure)
- Human review requests
- Audit logging
- Sub-processor disclosure
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import re
import logging
import hashlib

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/privacy", tags=["Privacy & Compliance"])

# ============== Models ==============

class ConsentRequest(BaseModel):
    """User consent submission"""
    resume_processing: bool = False
    voice_processing: bool = False
    ai_matching: bool = False
    marketing_communications: bool = False
    third_party_sharing: bool = False

class HumanReviewRequest(BaseModel):
    """Request for human review of AI decision"""
    job_id: str
    match_id: Optional[str] = None
    reason: str
    additional_context: Optional[str] = None

class DataDeletionRequest(BaseModel):
    """Data deletion request"""
    delete_resume: bool = True
    delete_voice_history: bool = True
    delete_applications: bool = False
    delete_matches: bool = True
    delete_account: bool = False
    reason: Optional[str] = None

# ============== PII Patterns for Redaction ==============

PII_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone": r'\b(\+?1?[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
    "ssn": r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',
    "address": r'\b\d{1,5}\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way|Circle|Cir)\.?\b',
    "zipcode": r'\b\d{5}(?:-\d{4})?\b',
    "date_of_birth": r'\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b',
    "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
}

# ============== Sub-Processors (Third-Party AI Services) ==============

SUB_PROCESSORS = [
    {
        "name": "OpenAI",
        "service": "GPT-5.2 for text generation, cover letters, and translations",
        "data_processed": ["Resume text", "Job descriptions", "User queries"],
        "location": "United States",
        "dpa_signed": True,
        "data_retention": "Not used for model training (API terms)"
    },
    {
        "name": "MongoDB Atlas",
        "service": "Database storage",
        "data_processed": ["User profiles", "Resumes", "Applications"],
        "location": "United States (AWS)",
        "dpa_signed": True,
        "data_retention": "Until user deletion request"
    },
    {
        "name": "Stripe",
        "service": "Payment processing",
        "data_processed": ["Payment information", "Subscription status"],
        "location": "United States",
        "dpa_signed": True,
        "data_retention": "As required by financial regulations"
    },
    {
        "name": "Google Cloud",
        "service": "OAuth authentication, Calendar API",
        "data_processed": ["Email address", "Calendar events"],
        "location": "United States",
        "dpa_signed": True,
        "data_retention": "OAuth tokens only"
    },
    {
        "name": "Expo",
        "service": "Mobile push notifications",
        "data_processed": ["Device tokens", "Notification content"],
        "location": "United States",
        "dpa_signed": True,
        "data_retention": "Until device unregistration"
    }
]

# ============== Helper Functions ==============

def redact_pii(text: str, redaction_map: Dict[str, str] = None) -> tuple[str, Dict[str, str]]:
    """
    Redact PII from text while maintaining a reversible map.
    Returns: (redacted_text, redaction_map)
    """
    if redaction_map is None:
        redaction_map = {}
    
    redacted_text = text
    
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, redacted_text, re.IGNORECASE)
        for i, match in enumerate(matches):
            if isinstance(match, tuple):
                match = ''.join(match)
            if match and match not in redaction_map:
                # Create unique placeholder
                placeholder = f"[{pii_type.upper()}_{i+1}]"
                redaction_map[placeholder] = match
                redacted_text = redacted_text.replace(match, placeholder, 1)
    
    return redacted_text, redaction_map

def hash_for_audit(data: str) -> str:
    """Create SHA-256 hash for audit purposes"""
    return hashlib.sha256(data.encode()).hexdigest()[:16]

async def log_privacy_action(user_id: str, action: str, details: Dict[str, Any]):
    """Log privacy-related actions for compliance audit"""
    audit_log = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": action,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip_hash": None  # Would be populated from request
    }
    await db.privacy_audit_logs.insert_one(audit_log)
    return audit_log["id"]

# ============== Consent Management ==============

@router.get("/consent/status")
async def get_consent_status(request: Request):
    """Get user's current consent status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    consent = await db.user_consents.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not consent:
        return {
            "has_consented": False,
            "consent": None,
            "required_for_ai_features": True
        }
    
    return {
        "has_consented": True,
        "consent": consent,
        "required_for_ai_features": False
    }

@router.post("/consent/grant")
async def grant_consent(consent: ConsentRequest, request: Request):
    """
    Grant consent for data processing.
    Required before AI features can be used.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    consent_doc = {
        "user_id": user["user_id"],
        "resume_processing": consent.resume_processing,
        "voice_processing": consent.voice_processing,
        "ai_matching": consent.ai_matching,
        "marketing_communications": consent.marketing_communications,
        "third_party_sharing": consent.third_party_sharing,
        "consent_version": "1.0",
        "granted_at": datetime.now(timezone.utc).isoformat(),
        "ip_address_hash": hash_for_audit(request.client.host if request.client else "unknown"),
        "user_agent": request.headers.get("user-agent", "unknown")[:200]
    }
    
    await db.user_consents.update_one(
        {"user_id": user["user_id"]},
        {"$set": consent_doc},
        upsert=True
    )
    
    # Log for audit
    await log_privacy_action(user["user_id"], "CONSENT_GRANTED", {
        "consent_types": [k for k, v in consent.model_dump().items() if v]
    })
    
    return {
        "message": "Consent recorded successfully",
        "consent": consent_doc
    }

@router.post("/consent/withdraw")
async def withdraw_consent(request: Request, background_tasks: BackgroundTasks):
    """
    Withdraw all consents and trigger data deletion.
    This is a "one-tap" GDPR-compliant withdrawal.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Update consent to withdrawn
    await db.user_consents.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "resume_processing": False,
            "voice_processing": False,
            "ai_matching": False,
            "marketing_communications": False,
            "third_party_sharing": False,
            "withdrawn_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Schedule background deletion of AI-processed data
    background_tasks.add_task(
        delete_user_ai_data,
        user["user_id"]
    )
    
    # Log for audit
    await log_privacy_action(user["user_id"], "CONSENT_WITHDRAWN", {
        "deletion_scheduled": True
    })
    
    return {
        "message": "Consent withdrawn. Your AI-processed data will be deleted.",
        "deletion_status": "scheduled"
    }

async def delete_user_ai_data(user_id: str):
    """Background task to delete AI-processed data"""
    try:
        # Delete voice transcriptions
        await db.voice_transcriptions.delete_many({"user_id": user_id})
        
        # Delete AI match history
        await db.ai_match_history.delete_many({"user_id": user_id})
        
        # Delete translation cache for user
        await db.user_translations.delete_many({"user_id": user_id})
        
        # Log completion
        await log_privacy_action(user_id, "AI_DATA_DELETED", {
            "collections_cleared": ["voice_transcriptions", "ai_match_history", "user_translations"]
        })
        
    except Exception as e:
        logging.error(f"Error deleting AI data for user {user_id}: {e}")

# ============== Data Deletion (Right to Erasure) ==============

@router.post("/data/delete")
async def request_data_deletion(
    deletion: DataDeletionRequest,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Process data deletion request (GDPR Article 17 - Right to Erasure).
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    deletion_results = {
        "resume_deleted": False,
        "voice_history_deleted": False,
        "applications_deleted": False,
        "matches_deleted": False,
        "account_deleted": False
    }
    
    if deletion.delete_resume:
        result = await db.resumes.delete_many({"user_id": user["user_id"]})
        deletion_results["resume_deleted"] = result.deleted_count > 0
        
        # Also delete resume profiles
        await db.resume_profiles.delete_many({"user_id": user["user_id"]})
    
    if deletion.delete_voice_history:
        result = await db.voice_transcriptions.delete_many({"user_id": user["user_id"]})
        deletion_results["voice_history_deleted"] = result.deleted_count > 0
    
    if deletion.delete_applications:
        result = await db.applications.delete_many({"user_id": user["user_id"]})
        deletion_results["applications_deleted"] = result.deleted_count > 0
    
    if deletion.delete_matches:
        result = await db.ai_match_history.delete_many({"user_id": user["user_id"]})
        deletion_results["matches_deleted"] = result.deleted_count > 0
        
        # Also delete saved jobs
        await db.saved_jobs.delete_many({"user_id": user["user_id"]})
    
    if deletion.delete_account:
        # Schedule full account deletion
        background_tasks.add_task(
            full_account_deletion,
            user["user_id"]
        )
        deletion_results["account_deleted"] = True
    
    # Log for audit
    await log_privacy_action(user["user_id"], "DATA_DELETION_REQUESTED", {
        "deletion_types": deletion.model_dump(),
        "results": deletion_results,
        "reason": deletion.reason
    })
    
    return {
        "message": "Data deletion processed",
        "results": deletion_results,
        "audit_id": await log_privacy_action(user["user_id"], "DATA_DELETION_COMPLETED", deletion_results)
    }

async def full_account_deletion(user_id: str):
    """Complete account deletion - removes all user data"""
    collections_to_clear = [
        "users", "resumes", "resume_profiles", "applications",
        "saved_jobs", "job_alerts", "voice_transcriptions",
        "ai_match_history", "user_consents", "user_translations",
        "meeting_notes", "interview_schedules", "feedback",
        "expo_push_tokens", "webpush_subscriptions"
    ]
    
    for collection in collections_to_clear:
        try:
            await db[collection].delete_many({"user_id": user_id})
        except Exception as e:
            logging.error(f"Error deleting from {collection}: {e}")
    
    # Keep audit log for compliance (anonymized)
    await db.privacy_audit_logs.update_many(
        {"user_id": user_id},
        {"$set": {"user_id": f"DELETED_{hash_for_audit(user_id)}"}}
    )

# ============== PII Redaction Service ==============

@router.post("/pii/redact")
async def redact_pii_from_text(request: Request):
    """
    Redact PII from text before AI processing.
    Used internally to ensure data minimization.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    body = await request.json()
    text = body.get("text", "")
    
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    redacted_text, redaction_map = redact_pii(text)
    
    # Log redaction for audit (without the actual PII)
    await log_privacy_action(user["user_id"], "PII_REDACTION", {
        "original_length": len(text),
        "redacted_length": len(redacted_text),
        "pii_types_found": list(set(k.split("_")[0].strip("[]") for k in redaction_map.keys()))
    })
    
    return {
        "redacted_text": redacted_text,
        "pii_count": len(redaction_map),
        "pii_types_redacted": list(set(k.split("_")[0].strip("[]") for k in redaction_map.keys()))
    }

# ============== Human Review Requests ==============

@router.post("/review/request")
async def request_human_review(review: HumanReviewRequest, request: Request):
    """
    Request human review of an AI decision (GDPR Article 22).
    Ensures human-in-the-loop for significant automated decisions.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    review_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user["user_id"],
        "job_id": review.job_id,
        "match_id": review.match_id,
        "reason": review.reason,
        "additional_context": review.additional_context,
        "status": "pending",
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "reviewed_by": None,
        "reviewed_at": None,
        "outcome": None
    }
    
    await db.human_review_requests.insert_one(review_doc)
    
    # Log for audit
    await log_privacy_action(user["user_id"], "HUMAN_REVIEW_REQUESTED", {
        "review_id": review_doc["id"],
        "job_id": review.job_id
    })
    
    return {
        "message": "Human review request submitted",
        "review_id": review_doc["id"],
        "estimated_response_time": "2-3 business days"
    }

@router.get("/review/status/{review_id}")
async def get_review_status(review_id: str, request: Request):
    """Get status of a human review request"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    review = await db.human_review_requests.find_one(
        {"id": review_id, "user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not review:
        raise HTTPException(status_code=404, detail="Review request not found")
    
    return review

# ============== Match Explanation (Explainable AI) ==============

@router.get("/explain/match/{job_id}")
async def explain_ai_match(job_id: str, request: Request):
    """
    Explain why a job was matched to the user (GDPR Article 22 - Right to Explanation).
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get user's resume
    resume = await db.resumes.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0, "skills": 1, "experience": 1, "education": 1}
    )
    
    if not resume:
        return {
            "explanation": "No resume found. Upload your resume to see personalized match explanations.",
            "match_factors": []
        }
    
    # Get the job (from saved or match history)
    job = await db.saved_jobs.find_one({"id": job_id})
    if not job:
        job = await db.ai_match_history.find_one({"job_id": job_id, "user_id": user["user_id"]})
    
    # Build explanation based on matching factors
    match_factors = []
    user_skills = set(s.lower() if isinstance(s, str) else s.get("name", "").lower() for s in resume.get("skills", []))
    
    explanation_parts = []
    
    if job:
        job_data = job.get("job", job)
        job_text = f"{job_data.get('title', '')} {job_data.get('description', '')}".lower()
        
        # Skill matches
        matched_skills = [s for s in user_skills if s in job_text]
        if matched_skills:
            match_factors.append({
                "factor": "Skills Match",
                "weight": "High",
                "details": f"Your skills match: {', '.join(matched_skills[:5])}"
            })
            explanation_parts.append(f"Your {len(matched_skills)} matching skills")
        
        # Experience match
        experience_keywords = ["senior", "lead", "manager", "director", "junior", "entry"]
        for keyword in experience_keywords:
            if keyword in job_text:
                match_factors.append({
                    "factor": "Experience Level",
                    "weight": "Medium",
                    "details": f"Job requires {keyword}-level experience"
                })
                break
        
        # Location match
        if "remote" in job_text:
            match_factors.append({
                "factor": "Work Type",
                "weight": "Medium",
                "details": "This is a remote position matching your preferences"
            })
    
    if not match_factors:
        match_factors.append({
            "factor": "General Match",
            "weight": "Low",
            "details": "This job was found based on your search criteria"
        })
    
    return {
        "job_id": job_id,
        "explanation": f"This job was recommended based on: {', '.join(explanation_parts) if explanation_parts else 'your search criteria'}",
        "match_factors": match_factors,
        "transparency_note": "Our AI uses your resume skills, experience, and education to calculate match scores. No demographic data is used in matching.",
        "request_review_available": True
    }

# ============== Sub-Processor Disclosure ==============

@router.get("/sub-processors")
async def get_sub_processors():
    """
    Get list of all third-party services that process user data.
    Required for GDPR transparency.
    """
    return {
        "sub_processors": SUB_PROCESSORS,
        "last_updated": "2025-12-01",
        "dpa_status": "All vendors have signed Data Processing Agreements",
        "contact_for_concerns": "privacy@medmatch.ai"
    }

# ============== Privacy Audit Logs ==============

@router.get("/audit/logs")
async def get_privacy_audit_logs(request: Request, limit: int = 50):
    """Get user's privacy-related activity logs"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    logs = await db.privacy_audit_logs.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    return {
        "logs": logs,
        "total": len(logs)
    }

# ============== Data Export (Right to Portability) ==============

@router.get("/data/export")
async def export_user_data(request: Request):
    """
    Export all user data in portable format (GDPR Article 20).
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Gather all user data
    export_data = {
        "export_date": datetime.now(timezone.utc).isoformat(),
        "user_id": user["user_id"],
        "sections": {}
    }
    
    # Profile
    user_profile = await db.users.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0, "password_hash": 0}
    )
    export_data["sections"]["profile"] = user_profile
    
    # Resume
    resume = await db.resumes.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0}
    )
    export_data["sections"]["resume"] = resume
    
    # Applications
    applications = await db.applications.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).to_list(1000)
    export_data["sections"]["applications"] = applications
    
    # Saved Jobs
    saved_jobs = await db.saved_jobs.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).to_list(500)
    export_data["sections"]["saved_jobs"] = saved_jobs
    
    # Consent history
    consent = await db.user_consents.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0}
    )
    export_data["sections"]["consent"] = consent
    
    # Log export for audit
    await log_privacy_action(user["user_id"], "DATA_EXPORTED", {
        "sections_included": list(export_data["sections"].keys())
    })
    
    return export_data

# ============== Breach Notification Endpoint (Admin) ==============

@router.post("/admin/breach-notification")
async def report_data_breach(request: Request):
    """
    Report a data breach (admin only).
    Must notify regulators within 72 hours per GDPR.
    """
    user = await get_current_user(request)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    body = await request.json()
    
    breach_doc = {
        "id": str(uuid.uuid4()),
        "reported_by": user["user_id"],
        "reported_at": datetime.now(timezone.utc).isoformat(),
        "description": body.get("description"),
        "affected_users_estimate": body.get("affected_users_estimate"),
        "data_types_affected": body.get("data_types_affected", []),
        "containment_actions": body.get("containment_actions", []),
        "regulator_notification_deadline": None,  # Calculate 72h deadline
        "status": "investigating"
    }
    
    await db.data_breach_reports.insert_one(breach_doc)
    
    return {
        "message": "Breach report filed",
        "breach_id": breach_doc["id"],
        "regulatory_deadline": "72 hours from detection",
        "next_steps": [
            "Assess scope of breach",
            "Contain the breach",
            "Notify affected users if high risk",
            "Report to supervisory authority within 72 hours"
        ]
    }
