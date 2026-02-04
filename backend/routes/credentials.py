"""
Credential Verification API Routes
Primary Source Verification (PSV) endpoints for MedMatch.
Includes Credly OAuth integration for automatic badge import.
"""

from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid
import os
import logging

from utils.database import db
from routes.auth import get_current_user
from services.psv_service import (
    PSVService, PSV_PROVIDERS, QUALITY_CERTIFICATIONS, QUALITY_HIERARCHY, INDUSTRY_BRIDGE,
    VerificationStatus, VerificationMethod, CredentialType,
    get_certification_info, get_certifications_by_tier, get_certifications_by_category
)
from services.credly_service import CredlyOAuthService, SUPPORTED_BADGE_ISSUERS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/credentials", tags=["Credential Verification"])

# Initialize Services
psv_service = PSVService(db)
credly_service = CredlyOAuthService(db)

# ============== Request/Response Models ==============

class VerificationRequest(BaseModel):
    credential_code: str
    credential_number: Optional[str] = None
    issuing_authority: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None

class CredentialSubmission(BaseModel):
    credential_code: str
    credential_number: Optional[str] = None
    issuing_authority: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    document_url: Optional[str] = None

class ConsentRequest(BaseModel):
    consent_given: bool
    consent_timestamp: Optional[str] = None
    purposes: List[str] = []

# ============== PSV Provider Endpoints ==============

@router.get("/providers")
async def get_verification_providers():
    """Get all available PSV providers"""
    
    providers_by_type = {
        "healthcare": [],
        "engineering": [],
        "digital_badge": []
    }
    
    for provider_id, provider in PSV_PROVIDERS.items():
        provider_type = provider.get("type", "other")
        if provider_type in providers_by_type:
            providers_by_type[provider_type].append({
                "id": provider_id,
                **provider
            })
    
    return {
        "providers": providers_by_type,
        "total": len(PSV_PROVIDERS)
    }

@router.get("/providers/{provider_id}")
async def get_provider_details(provider_id: str):
    """Get details for a specific PSV provider"""
    
    if provider_id not in PSV_PROVIDERS:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    provider = PSV_PROVIDERS[provider_id]
    
    # Get certifications that use this provider
    supported_certs = [
        {"code": code, "name": cert["name"]}
        for code, cert in QUALITY_CERTIFICATIONS.items()
        if provider_id in cert.get("verification_providers", [])
    ]
    
    return {
        "provider": {**provider, "id": provider_id},
        "supported_certifications": supported_certs
    }

# ============== Certification Database Endpoints ==============

@router.get("/certifications")
async def get_certifications(
    category: Optional[str] = None,
    tier: Optional[int] = None,
    sector: Optional[str] = None
):
    """Get all certifications with optional filters"""
    
    certs = []
    for code, cert in QUALITY_CERTIFICATIONS.items():
        if category and cert.get("category") != category:
            continue
        if tier and cert.get("tier") != tier:
            continue
        if sector and sector not in cert.get("sectors", []):
            continue
        
        certs.append({
            "code": code,
            **cert
        })
    
    return {
        "certifications": certs,
        "total": len(certs),
        "categories": list(set(c.get("category") for c in QUALITY_CERTIFICATIONS.values())),
        "tiers": list(range(1, 6))
    }

@router.get("/certifications/{code}")
async def get_certification_details(code: str):
    """Get detailed information about a certification"""
    
    cert_info = get_certification_info(code)
    if not cert_info:
        raise HTTPException(status_code=404, detail="Certification not found")
    
    # Get verification providers
    providers = psv_service.get_verification_providers(code)
    
    return {
        "certification": {**cert_info, "code": code},
        "verification_providers": providers
    }

@router.get("/hierarchy")
async def get_quality_hierarchy():
    """Get the unified quality hierarchy (Tier 1-5)"""
    
    return {
        "hierarchy": QUALITY_HIERARCHY,
        "description": "Universal seniority scale for Quality & Compliance roles"
    }

@router.get("/industry-bridges")
async def get_industry_bridges(from_sector: Optional[str] = None):
    """Get industry bridge pathways for career transitions"""
    
    if from_sector:
        bridges = psv_service.get_industry_bridges(from_sector)
    else:
        bridges = INDUSTRY_BRIDGE
    
    return {
        "bridges": bridges,
        "total": len(bridges),
        "available_sectors": list(set(b["from_sector"] for b in INDUSTRY_BRIDGE))
    }

# ============== User Credential Management ==============

@router.post("/verify")
async def verify_credential(request: Request, verification_req: VerificationRequest):
    """
    Submit a credential for verification.
    Uses waterfall approach: API Instant → Primary Source → Manual Review
    """
    
    user = await get_current_user(request)
    
    result = await psv_service.verify_credential(
        user_id=user["user_id"],
        credential_code=verification_req.credential_code,
        credential_number=verification_req.credential_number,
        issuing_authority=verification_req.issuing_authority
    )
    
    return result

@router.post("/submit")
async def submit_credential(request: Request, submission: CredentialSubmission):
    """
    Submit a credential with optional document upload URL.
    For manual verification workflow.
    """
    
    user = await get_current_user(request)
    
    # Create credential record
    credential_id = str(uuid.uuid4())
    credential_record = {
        "id": credential_id,
        "user_id": user["user_id"],
        "credential_code": submission.credential_code,
        "credential_number": submission.credential_number,
        "issuing_authority": submission.issuing_authority,
        "issue_date": submission.issue_date,
        "expiry_date": submission.expiry_date,
        "document_url": submission.document_url,
        "status": VerificationStatus.PENDING if submission.document_url else VerificationStatus.PENDING,
        "method": VerificationMethod.MANUAL_UPLOAD if submission.document_url else VerificationMethod.SELF_ATTESTATION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Get certification info
    cert_info = get_certification_info(submission.credential_code)
    if cert_info:
        credential_record["credential_name"] = cert_info.get("name")
        credential_record["tier"] = cert_info.get("tier")
        credential_record["category"] = cert_info.get("category")
    
    await db.user_credentials.insert_one(credential_record)
    
    # If document provided, trigger verification
    if submission.document_url:
        verification_result = await psv_service.verify_credential(
            user_id=user["user_id"],
            credential_code=submission.credential_code,
            credential_number=submission.credential_number,
            issuing_authority=submission.issuing_authority,
            document_url=submission.document_url
        )
        credential_record["verification"] = verification_result
    
    return {
        "credential_id": credential_id,
        "status": credential_record["status"],
        "message": "Credential submitted successfully",
        "credential": credential_record
    }

@router.get("/my-credentials")
async def get_my_credentials(request: Request):
    """Get all credentials for the current user"""
    
    user = await get_current_user(request)
    
    credentials = await db.user_credentials.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).to_list(100)
    
    # Group by status
    by_status = {
        "verified": [],
        "pending": [],
        "expired": [],
        "manual_review": []
    }
    
    for cred in credentials:
        status = cred.get("status", "pending")
        if status in by_status:
            by_status[status].append(cred)
        else:
            by_status["pending"].append(cred)
    
    return {
        "credentials": credentials,
        "by_status": by_status,
        "total": len(credentials),
        "verified_count": len(by_status["verified"])
    }

@router.get("/expiration-alerts")
async def get_expiration_alerts(request: Request):
    """Get alerts for expiring or expired credentials"""
    
    user = await get_current_user(request)
    
    alerts = await psv_service.check_expiration_status(user["user_id"])
    
    return {
        "alerts": alerts,
        "total": len(alerts),
        "action_required": len([a for a in alerts if a["status"] == "expired"])
    }

@router.post("/reverify/{verification_id}")
async def reverify_credential(request: Request, verification_id: str):
    """Trigger re-verification of a credential"""
    
    user = await get_current_user(request)
    
    # Verify ownership
    existing = await db.credential_verifications.find_one({
        "verification_id": verification_id,
        "user_id": user["user_id"]
    })
    
    if not existing:
        raise HTTPException(status_code=404, detail="Verification record not found")
    
    result = await psv_service.trigger_reverification(verification_id)
    
    return result

# ============== Document Upload ==============

@router.post("/upload-document")
async def upload_credential_document(
    request: Request,
    file: UploadFile = File(...),
    credential_code: str = Form(...),
    credential_number: str = Form(None)
):
    """Upload a credential document (PDF/image) for manual verification"""
    
    user = await get_current_user(request)
    
    # Validate file type
    allowed_types = ["application/pdf", "image/png", "image/jpeg", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Limit file size (10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum 10MB.")
    
    # Generate secure filename
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "pdf"
    secure_filename = f"{user['user_id']}_{credential_code}_{uuid.uuid4()}.{file_ext}"
    
    # Store file (in production, use S3/GCS)
    upload_dir = "/tmp/credential_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, secure_filename)
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Create verification record
    document_id = str(uuid.uuid4())
    document_record = {
        "id": document_id,
        "user_id": user["user_id"],
        "credential_code": credential_code,
        "credential_number": credential_number,
        "filename": secure_filename,
        "original_filename": file.filename,
        "content_type": file.content_type,
        "file_size": len(contents),
        "file_path": file_path,
        "status": VerificationStatus.MANUAL_REVIEW,
        "uploaded_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.credential_documents.insert_one(document_record)
    
    # Submit for verification
    verification_result = await psv_service.verify_credential(
        user_id=user["user_id"],
        credential_code=credential_code,
        credential_number=credential_number,
        document_url=file_path
    )
    
    return {
        "document_id": document_id,
        "message": "Document uploaded successfully",
        "status": "pending_review",
        "verification": verification_result
    }

# ============== Consent Management ==============

@router.post("/consent")
async def submit_verification_consent(request: Request, consent: ConsentRequest):
    """
    Record user consent for credential verification.
    Required before triggering PSV API calls per GDPR/HIPAA.
    """
    
    user = await get_current_user(request)
    
    consent_record = {
        "id": str(uuid.uuid4()),
        "user_id": user["user_id"],
        "consent_given": consent.consent_given,
        "consent_timestamp": consent.consent_timestamp or datetime.now(timezone.utc).isoformat(),
        "purposes": consent.purposes or [
            "primary_source_verification",
            "credential_sharing_with_employers",
            "automated_reverification"
        ],
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.verification_consents.insert_one(consent_record)
    
    # Update user profile
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "psv_consent": consent.consent_given,
            "psv_consent_timestamp": consent_record["consent_timestamp"]
        }}
    )
    
    return {
        "success": True,
        "consent_id": consent_record["id"],
        "message": "Consent recorded successfully"
    }

@router.get("/consent/status")
async def get_consent_status(request: Request):
    """Check if user has given PSV consent"""
    
    user = await get_current_user(request)
    
    latest_consent = await db.verification_consents.find_one(
        {"user_id": user["user_id"]},
        sort=[("created_at", -1)]
    )
    
    return {
        "has_consent": user.get("psv_consent", False),
        "consent_timestamp": user.get("psv_consent_timestamp"),
        "latest_consent": {
            "id": latest_consent["id"],
            "purposes": latest_consent.get("purposes", []),
            "timestamp": latest_consent.get("consent_timestamp")
        } if latest_consent else None
    }

# ============== Admin Endpoints ==============

@router.get("/admin/pending-reviews")
async def get_pending_reviews(request: Request):
    """Get credentials pending manual review (admin only)"""
    
    user = await get_current_user(request)
    
    # Check admin access
    if user.get("role") != "admin" and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    pending = await db.credential_verifications.find(
        {"status": VerificationStatus.MANUAL_REVIEW},
        {"_id": 0}
    ).to_list(100)
    
    return {
        "pending_reviews": pending,
        "total": len(pending)
    }

@router.post("/admin/approve/{verification_id}")
async def approve_credential(request: Request, verification_id: str):
    """Approve a credential after manual review (admin only)"""
    
    user = await get_current_user(request)
    
    if user.get("role") != "admin" and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.credential_verifications.update_one(
        {"verification_id": verification_id},
        {"$set": {
            "status": VerificationStatus.VERIFIED,
            "reviewed_by": user["user_id"],
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "next_reverification": (
                datetime.now(timezone.utc).replace(year=datetime.now().year + 1)
            ).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    return {
        "success": True,
        "message": "Credential approved",
        "verification_id": verification_id
    }

@router.post("/admin/reject/{verification_id}")
async def reject_credential(request: Request, verification_id: str, reason: str = ""):
    """Reject a credential after manual review (admin only)"""
    
    user = await get_current_user(request)
    
    if user.get("role") != "admin" and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.credential_verifications.update_one(
        {"verification_id": verification_id},
        {"$set": {
            "status": VerificationStatus.FAILED,
            "rejection_reason": reason,
            "reviewed_by": user["user_id"],
            "reviewed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    return {
        "success": True,
        "message": "Credential rejected",
        "verification_id": verification_id
    }

# ============== Trust Score ==============

@router.get("/trust-score")
async def get_trust_score(request: Request):
    """Calculate user's credential trust score"""
    
    user = await get_current_user(request)
    
    credentials = await db.user_credentials.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).to_list(100)
    
    # Calculate trust score
    score = 0
    max_score = 100
    
    verified_count = sum(1 for c in credentials if c.get("status") == "verified")
    pending_count = sum(1 for c in credentials if c.get("status") == "pending")
    
    # Points for verified credentials (max 50)
    score += min(verified_count * 10, 50)
    
    # Points for PSV consent (10)
    if user.get("psv_consent"):
        score += 10
    
    # Points for profile completeness (20)
    if user.get("resume"):
        score += 10
    if user.get("linkedin_url"):
        score += 5
    if user.get("phone_verified"):
        score += 5
    
    # Points for ID verification (20)
    if user.get("id_verification_status") == "verified":
        score += 20
    
    # Determine badge level
    if score >= 80:
        badge = "gold"
    elif score >= 60:
        badge = "silver"
    elif score >= 40:
        badge = "bronze"
    else:
        badge = "none"
    
    return {
        "trust_score": score,
        "max_score": max_score,
        "badge_level": badge,
        "breakdown": {
            "verified_credentials": verified_count,
            "pending_credentials": pending_count,
            "psv_consent": user.get("psv_consent", False),
            "id_verified": user.get("id_verification_status") == "verified"
        },
        "recommendations": [
            "Verify more credentials" if verified_count < 3 else None,
            "Complete ID verification" if user.get("id_verification_status") != "verified" else None,
            "Add LinkedIn profile" if not user.get("linkedin_url") else None,
            "Grant PSV consent" if not user.get("psv_consent") else None
        ]
    }
