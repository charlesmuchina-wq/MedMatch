"""
ID Verification Routes
Handles: Document verification for recruiters, identity checks, verification status
Note: This is a simplified implementation. For production, integrate with Persona, Veriff, or similar service.
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid


from utils.database import db
from routes.auth import get_current_user, require_auth

router = APIRouter(prefix="/id-verification", tags=["ID Verification"])

# ============== Models ==============

class VerificationRequest(BaseModel):
    document_type: str = "government_id"  # government_id, passport, drivers_license
    full_name: str
    date_of_birth: Optional[str] = None
    country: str = "US"

class VerificationStatus(BaseModel):
    status: str  # pending, approved, rejected, expired
    verified_at: Optional[str] = None
    expires_at: Optional[str] = None
    verification_level: int = 0  # 0-3

class CompanyVerificationRequest(BaseModel):
    company_name: str
    company_website: Optional[str] = None
    company_email_domain: str
    role_at_company: str
    linkedin_url: Optional[str] = None

# ============== Verification Levels ==============
# Level 0: Unverified
# Level 1: Email verified
# Level 2: Company/recruiter verification
# Level 3: Full ID verification (government ID + selfie)

VERIFICATION_LEVELS = {
    0: {"name": "Unverified", "badge": None, "features": ["basic_search"]},
    1: {"name": "Email Verified", "badge": "email_verified", "features": ["basic_search", "job_posting"]},
    2: {"name": "Company Verified", "badge": "company_verified", "features": ["basic_search", "job_posting", "candidate_contact"]},
    3: {"name": "ID Verified", "badge": "id_verified", "features": ["basic_search", "job_posting", "candidate_contact", "premium_features"]}
}

# ============== Routes ==============

@router.get("/status")
async def get_verification_status(request: Request):
    """Get current user's verification status"""
    user = await require_auth(request)
    
    # Get verification record
    verification = await db.id_verifications.find_one(
        {"user_id": user.get("user_id")},
        {"_id": 0}
    )
    
    if not verification:
        return {
            "status": "unverified",
            "verification_level": 0,
            "level_info": VERIFICATION_LEVELS[0],
            "can_verify": True
        }
    
    # Check if expired
    if verification.get("expires_at"):
        expires = datetime.fromisoformat(verification["expires_at"].replace("Z", "+00:00"))
        if expires < datetime.now(timezone.utc):
            verification["status"] = "expired"
    
    level = verification.get("verification_level", 0)
    
    return {
        "status": verification.get("status", "pending"),
        "verification_level": level,
        "level_info": VERIFICATION_LEVELS.get(level, VERIFICATION_LEVELS[0]),
        "verified_at": verification.get("verified_at"),
        "expires_at": verification.get("expires_at"),
        "document_type": verification.get("document_type"),
        "company_verified": verification.get("company_verified", False)
    }

@router.post("/request-verification")
async def request_id_verification(req: VerificationRequest, request: Request):
    """Start ID verification process"""
    user = await require_auth(request)
    
    user_id = user.get("user_id")
    
    # Check if already has pending verification
    existing = await db.id_verifications.find_one({
        "user_id": user_id,
        "status": {"$in": ["pending", "approved"]}
    })
    
    if existing and existing.get("status") == "approved":
        raise HTTPException(status_code=400, detail="Already verified")
    
    if existing and existing.get("status") == "pending":
        raise HTTPException(status_code=400, detail="Verification already in progress")
    
    # Create verification request
    verification_id = str(uuid.uuid4())
    verification = {
        "verification_id": verification_id,
        "user_id": user_id,
        "document_type": req.document_type,
        "full_name": req.full_name,
        "date_of_birth": req.date_of_birth,
        "country": req.country,
        "status": "pending",
        "verification_level": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "documents": []
    }
    
    await db.id_verifications.insert_one(verification)
    
    return {
        "verification_id": verification_id,
        "status": "pending",
        "message": "Verification request created. Please upload your document.",
        "next_step": "upload_document"
    }

@router.post("/upload-document")
async def upload_verification_document(
    file: UploadFile = File(...),
    document_side: str = Form("front"),  # front, back, selfie
    request: Request = None
):
    """Upload verification document"""
    user = await require_auth(request)
    
    # Get pending verification
    verification = await db.id_verifications.find_one({
        "user_id": user.get("user_id"),
        "status": "pending"
    })
    
    if not verification:
        raise HTTPException(status_code=404, detail="No pending verification found")
    
    # Validate file
    allowed_types = ["image/jpeg", "image/png", "image/webp", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Use JPEG, PNG, WebP, or PDF.")
    
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large. Max 10MB.")
    
    # Store document reference (in production, upload to secure storage)
    doc_id = str(uuid.uuid4())
    document = {
        "document_id": doc_id,
        "side": document_side,
        "filename": file.filename,
        "content_type": file.content_type,
        "uploaded_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Update verification with document
    await db.id_verifications.update_one(
        {"verification_id": verification["verification_id"]},
        {"$push": {"documents": document}}
    )
    
    # Check if we have all required documents
    updated = await db.id_verifications.find_one(
        {"verification_id": verification["verification_id"]}
    )
    
    docs = updated.get("documents", [])
    has_front = any(d["side"] == "front" for d in docs)
    has_selfie = any(d["side"] == "selfie" for d in docs)
    
    next_step = None
    if not has_front:
        next_step = "upload_front"
    elif not has_selfie:
        next_step = "upload_selfie"
    else:
        next_step = "processing"
        # Auto-approve for demo (in production, this would go to review)
        await process_verification(verification["verification_id"])
    
    return {
        "document_id": doc_id,
        "message": f"Document uploaded ({document_side})",
        "next_step": next_step,
        "documents_uploaded": len(docs)
    }

async def process_verification(verification_id: str):
    """Process verification (simplified - auto-approve for demo)"""
    # In production, this would:
    # 1. Use OCR to extract document data
    # 2. Compare selfie with document photo
    # 3. Check document authenticity
    # 4. Human review for edge cases
    
    await db.id_verifications.update_one(
        {"verification_id": verification_id},
        {"$set": {
            "status": "approved",
            "verification_level": 3,
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
            "processed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Update user record
    verification = await db.id_verifications.find_one({"verification_id": verification_id})
    if verification:
        await db.users.update_one(
            {"user_id": verification["user_id"]},
            {"$set": {
                "id_verified": True,
                "verification_level": 3,
                "verified_at": datetime.now(timezone.utc).isoformat()
            }}
        )

@router.post("/verify-company")
async def verify_company_affiliation(req: CompanyVerificationRequest, request: Request):
    """Verify recruiter's company affiliation"""
    user = await require_auth(request)
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can verify company affiliation")
    
    user_id = user.get("user_id")
    user_email = user.get("email", "")
    
    # Check if email domain matches company domain
    email_domain = user_email.split("@")[-1] if "@" in user_email else ""
    domain_matches = email_domain.lower() == req.company_email_domain.lower()
    
    # Create company verification
    verification_id = str(uuid.uuid4())
    company_verification = {
        "verification_id": verification_id,
        "user_id": user_id,
        "company_name": req.company_name,
        "company_website": req.company_website,
        "company_email_domain": req.company_email_domain,
        "role_at_company": req.role_at_company,
        "linkedin_url": req.linkedin_url,
        "email_domain_match": domain_matches,
        "status": "approved" if domain_matches else "pending",
        "verification_level": 2 if domain_matches else 1,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.company_verifications.insert_one(company_verification)
    
    if domain_matches:
        # Auto-approve if email domain matches
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "company_verified": True,
                "company_name": req.company_name,
                "verification_level": 2
            }}
        )
        
        return {
            "verification_id": verification_id,
            "status": "approved",
            "message": "Company affiliation verified automatically (email domain match)",
            "verification_level": 2
        }
    else:
        return {
            "verification_id": verification_id,
            "status": "pending",
            "message": "Verification pending manual review (email domain mismatch)",
            "verification_level": 1
        }

@router.get("/levels")
async def get_verification_levels():
    """Get available verification levels and their features"""
    return {
        "levels": [
            {
                "level": level,
                **info
            }
            for level, info in VERIFICATION_LEVELS.items()
        ]
    }

@router.get("/check/{user_id}")
async def check_user_verification(user_id: str, request: Request):
    """Check another user's verification status (for recruiters viewing candidates)"""
    user = await require_auth(request)
    
    # Get target user's verification
    target_user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "is_verified": target_user.get("id_verified", False),
        "verification_level": target_user.get("verification_level", 0),
        "is_biometric_verified": target_user.get("is_biometric_verified", False),
        "company_verified": target_user.get("company_verified", False)
    }
