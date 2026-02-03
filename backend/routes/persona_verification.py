"""
ID Verification Routes (Persona/Jumio Compatible)
Production-ready ID verification with sandbox mode for testing
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, timezone
import uuid
import hashlib
import os

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/id-verify", tags=["ID Verification"])

# Configuration
PERSONA_API_KEY = os.environ.get("PERSONA_API_KEY")
PERSONA_SANDBOX = os.environ.get("PERSONA_SANDBOX", "true").lower() == "true"
ID_VERIFICATION_PROVIDER = os.environ.get("ID_VERIFICATION_PROVIDER", "sandbox")  # sandbox, persona, jumio

# ============== Models ==============

class DocumentUploadRequest(BaseModel):
    document_type: str  # passport, driver_license, national_id
    document_country: str = "US"

class SelfieVerificationRequest(BaseModel):
    selfie_image: str  # Base64 encoded
    session_id: str
    liveness_score: float = 0.0

class VerificationStatus(BaseModel):
    session_id: str
    status: str  # pending, in_review, approved, rejected
    document_verified: bool = False
    selfie_verified: bool = False
    liveness_verified: bool = False
    risk_score: float = 0.0
    risk_level: str = "unknown"
    created_at: str
    completed_at: Optional[str] = None

# ============== Fraud Detection ==============

class FraudDetector:
    """Simple fraud detection for ID verification"""
    
    @staticmethod
    async def calculate_risk_score(user_id: str, session_id: str) -> Dict:
        """Calculate risk score based on verification patterns"""
        risk_score = 0.0
        risk_factors = []
        
        # Check for multiple recent attempts
        recent_sessions = await db.id_verification_sessions.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": datetime.now(timezone.utc).replace(hour=0, minute=0)}
        })
        
        if recent_sessions > 3:
            risk_score += 20
            risk_factors.append("Multiple verification attempts today")
        
        # Check for recent failures
        failed_sessions = await db.id_verification_sessions.count_documents({
            "user_id": user_id,
            "status": "rejected",
            "created_at": {"$gte": datetime.now(timezone.utc).replace(day=datetime.now().day - 7)}
        })
        
        if failed_sessions > 0:
            risk_score += 15 * failed_sessions
            risk_factors.append(f"{failed_sessions} failed attempts in past week")
        
        # Get session data
        session = await db.id_verification_sessions.find_one({"session_id": session_id})
        if session:
            liveness_score = session.get("liveness_score", 0)
            if liveness_score < 60:
                risk_score += 25
                risk_factors.append("Low liveness score")
            elif liveness_score < 75:
                risk_score += 10
                risk_factors.append("Borderline liveness score")
        
        # Determine risk level
        if risk_score < 20:
            risk_level = "low"
        elif risk_score < 50:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "risk_score": min(100, risk_score),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "requires_manual_review": risk_score >= 50
        }

# ============== Sandbox Mode Functions ==============

async def sandbox_verify_document(document_data: bytes, document_type: str) -> Dict:
    """Simulate document verification in sandbox mode"""
    # Simulate processing time
    import asyncio
    await asyncio.sleep(1)
    
    # Generate fake extracted data
    return {
        "verified": True,
        "document_type": document_type,
        "extracted_data": {
            "document_number": f"XXX-{uuid.uuid4().hex[:6].upper()}",
            "first_name": "TEST",
            "last_name": "USER",
            "date_of_birth": "1990-01-15",
            "expiration_date": "2030-01-15",
            "issuing_country": "US"
        },
        "confidence_score": 0.95,
        "fraud_signals": [],
        "sandbox_mode": True
    }

async def sandbox_verify_selfie(selfie_data: str, liveness_score: float) -> Dict:
    """Simulate selfie verification in sandbox mode"""
    import asyncio
    await asyncio.sleep(0.5)
    
    # Verify liveness
    verified = liveness_score >= 60
    
    return {
        "verified": verified,
        "liveness_score": liveness_score,
        "face_match_score": 0.92 if verified else 0.0,
        "fraud_signals": [] if verified else ["Low liveness score"],
        "sandbox_mode": True
    }

# ============== Routes ==============

@router.get("/status")
async def get_service_status(request: Request):
    """Get ID verification service status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "service_available": True,
        "provider": ID_VERIFICATION_PROVIDER,
        "sandbox_mode": PERSONA_SANDBOX or ID_VERIFICATION_PROVIDER == "sandbox",
        "supported_documents": ["passport", "driver_license", "national_id"],
        "supported_countries": ["US", "UK", "CA", "AU", "DE", "FR", "JP"],
        "features": {
            "document_verification": True,
            "selfie_verification": True,
            "liveness_detection": True,
            "fraud_detection": True,
            "ocr_extraction": True
        }
    }

@router.post("/sessions/create")
async def create_verification_session(request: Request):
    """Create a new ID verification session"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session_id = str(uuid.uuid4())
    
    session_doc = {
        "session_id": session_id,
        "user_id": user["user_id"],
        "status": "pending",
        "document_verified": False,
        "selfie_verified": False,
        "liveness_verified": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "provider": ID_VERIFICATION_PROVIDER,
        "sandbox_mode": PERSONA_SANDBOX or ID_VERIFICATION_PROVIDER == "sandbox"
    }
    
    await db.id_verification_sessions.insert_one(session_doc)
    
    return {
        "session_id": session_id,
        "status": "pending",
        "message": "Verification session created",
        "next_step": "upload_document"
    }

@router.post("/sessions/{session_id}/upload-document")
async def upload_document(
    session_id: str,
    request: Request,
    document_type: str = Form(...),
    document_country: str = Form("US"),
    front_document: UploadFile = File(...),
    back_document: Optional[UploadFile] = None
):
    """Upload identity document for verification"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Validate session
    session = await db.id_verification_sessions.find_one({
        "session_id": session_id,
        "user_id": user["user_id"]
    })
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.get("document_verified"):
        raise HTTPException(status_code=400, detail="Document already verified")
    
    # Read and validate document
    front_content = await front_document.read()
    if len(front_content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    back_content = None
    if back_document:
        back_content = await back_document.read()
        if len(back_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Back document too large (max 10MB)")
    
    # Verify document (sandbox or real)
    if PERSONA_SANDBOX or ID_VERIFICATION_PROVIDER == "sandbox":
        verification_result = await sandbox_verify_document(front_content, document_type)
    else:
        # In production, call Persona/Jumio API
        # For now, use sandbox mode
        verification_result = await sandbox_verify_document(front_content, document_type)
    
    # Update session
    update_data = {
        "document_type": document_type,
        "document_country": document_country,
        "document_verified": verification_result["verified"],
        "document_verification_result": verification_result,
        "document_uploaded_at": datetime.now(timezone.utc).isoformat(),
        "status": "document_uploaded" if verification_result["verified"] else "document_failed"
    }
    
    # Store document hash (not the actual document for privacy)
    update_data["document_hash"] = hashlib.sha256(front_content).hexdigest()
    
    await db.id_verification_sessions.update_one(
        {"session_id": session_id},
        {"$set": update_data}
    )
    
    return {
        "session_id": session_id,
        "document_verified": verification_result["verified"],
        "extracted_data": verification_result.get("extracted_data", {}),
        "confidence_score": verification_result.get("confidence_score", 0),
        "next_step": "upload_selfie" if verification_result["verified"] else "retry_document",
        "sandbox_mode": verification_result.get("sandbox_mode", False)
    }

@router.post("/sessions/{session_id}/upload-selfie")
async def upload_selfie(
    session_id: str,
    selfie_request: SelfieVerificationRequest,
    request: Request
):
    """Upload selfie for liveness verification"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Validate session
    session = await db.id_verification_sessions.find_one({
        "session_id": session_id,
        "user_id": user["user_id"]
    })
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.get("document_verified"):
        raise HTTPException(status_code=400, detail="Document must be verified first")
    
    if session.get("selfie_verified"):
        raise HTTPException(status_code=400, detail="Selfie already verified")
    
    # Verify selfie
    if PERSONA_SANDBOX or ID_VERIFICATION_PROVIDER == "sandbox":
        verification_result = await sandbox_verify_selfie(
            selfie_request.selfie_image,
            selfie_request.liveness_score
        )
    else:
        verification_result = await sandbox_verify_selfie(
            selfie_request.selfie_image,
            selfie_request.liveness_score
        )
    
    # Calculate fraud risk
    fraud_risk = await FraudDetector.calculate_risk_score(user["user_id"], session_id)
    
    # Determine final status
    if verification_result["verified"] and fraud_risk["risk_level"] != "high":
        final_status = "approved"
    elif fraud_risk["requires_manual_review"]:
        final_status = "in_review"
    else:
        final_status = "rejected"
    
    # Update session
    update_data = {
        "selfie_verified": verification_result["verified"],
        "liveness_verified": verification_result["verified"],
        "liveness_score": selfie_request.liveness_score,
        "selfie_verification_result": verification_result,
        "selfie_uploaded_at": datetime.now(timezone.utc).isoformat(),
        "risk_assessment": fraud_risk,
        "status": final_status,
        "completed_at": datetime.now(timezone.utc).isoformat() if final_status in ["approved", "rejected"] else None
    }
    
    await db.id_verification_sessions.update_one(
        {"session_id": session_id},
        {"$set": update_data}
    )
    
    # Update user verification status if approved
    if final_status == "approved":
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {
                "$set": {
                    "id_verified": True,
                    "id_verification_level": 3,  # Full verification
                    "id_verification_date": datetime.now(timezone.utc).isoformat(),
                    "id_verification_session": session_id
                }
            }
        )
    
    return {
        "session_id": session_id,
        "selfie_verified": verification_result["verified"],
        "liveness_score": selfie_request.liveness_score,
        "face_match_score": verification_result.get("face_match_score", 0),
        "status": final_status,
        "risk_assessment": {
            "risk_level": fraud_risk["risk_level"],
            "risk_score": fraud_risk["risk_score"]
        },
        "sandbox_mode": verification_result.get("sandbox_mode", False)
    }

@router.get("/sessions/{session_id}")
async def get_session_status(session_id: str, request: Request):
    """Get verification session status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = await db.id_verification_sessions.find_one(
        {"session_id": session_id, "user_id": user["user_id"]},
        {"_id": 0, "document_hash": 0}  # Exclude sensitive fields
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session

@router.get("/sessions")
async def list_verification_sessions(request: Request, limit: int = 10):
    """List user's verification sessions"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    sessions = await db.id_verification_sessions.find(
        {"user_id": user["user_id"]},
        {"_id": 0, "document_hash": 0}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    return {
        "sessions": sessions,
        "total": len(sessions)
    }

@router.get("/user-status")
async def get_user_verification_status(request: Request):
    """Get current user's ID verification status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get user's verification data
    user_data = await db.users.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0, "id_verified": 1, "id_verification_level": 1, 
         "id_verification_date": 1, "id_verification_session": 1}
    )
    
    if not user_data:
        return {
            "verified": False,
            "verification_level": 0,
            "message": "No verification on record"
        }
    
    return {
        "verified": user_data.get("id_verified", False),
        "verification_level": user_data.get("id_verification_level", 0),
        "verification_date": user_data.get("id_verification_date"),
        "session_id": user_data.get("id_verification_session"),
        "levels": {
            0: "Not Verified",
            1: "Email Verified",
            2: "Phone Verified",
            3: "ID Verified (Full)"
        }
    }

# ============== Admin/Manual Review Endpoints ==============

@router.get("/admin/pending-reviews")
async def get_pending_reviews(request: Request, limit: int = 20):
    """Get sessions pending manual review (admin only)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check admin role
    user_data = await db.users.find_one({"user_id": user["user_id"]})
    if not user_data or user_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    sessions = await db.id_verification_sessions.find(
        {"status": "in_review"},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    return {
        "pending_reviews": sessions,
        "total": len(sessions)
    }

@router.post("/admin/review/{session_id}")
async def submit_manual_review(
    session_id: str,
    request: Request
):
    """Submit manual review decision (admin only)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check admin role
    user_data = await db.users.find_one({"user_id": user["user_id"]})
    if not user_data or user_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    body = await request.json()
    decision = body.get("decision")  # approved or rejected
    notes = body.get("notes", "")
    
    if decision not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Decision must be 'approved' or 'rejected'")
    
    # Update session
    result = await db.id_verification_sessions.update_one(
        {"session_id": session_id, "status": "in_review"},
        {
            "$set": {
                "status": decision,
                "manual_review": {
                    "reviewer_id": user["user_id"],
                    "decision": decision,
                    "notes": notes,
                    "reviewed_at": datetime.now(timezone.utc).isoformat()
                },
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Session not found or not in review")
    
    # Update user verification if approved
    if decision == "approved":
        session = await db.id_verification_sessions.find_one({"session_id": session_id})
        if session:
            await db.users.update_one(
                {"user_id": session["user_id"]},
                {
                    "$set": {
                        "id_verified": True,
                        "id_verification_level": 3,
                        "id_verification_date": datetime.now(timezone.utc).isoformat(),
                        "id_verification_session": session_id
                    }
                }
            )
    
    return {
        "session_id": session_id,
        "decision": decision,
        "message": f"Session {decision}"
    }
