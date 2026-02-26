"""
AI KARAU Meeting - Security & Compliance API Routes
Email-based MFA, GDPR/HIPAA compliance
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, Dict

from services.karau_meet.security_service import (
    # Email-based verification (simple MFA)
    send_verification_email,
    verify_email_code,
    get_email_verification_status,
    # TOTP MFA (advanced)
    setup_mfa,
    verify_mfa_setup,
    verify_mfa_code,
    disable_mfa,
    get_mfa_status,
    regenerate_backup_codes,
    # Security logging
    log_security_event,
    get_security_logs,
    # Consent management
    record_consent,
    get_user_consents,
    check_consent,
    # GDPR
    export_user_data,
    delete_user_data,
    get_compliance_status,
    set_data_retention_policy,
    get_data_retention_policy
)
from routes.auth import get_current_user, require_auth

router = APIRouter(prefix="/karau-meet/security", tags=["AI KARAU Security"])


# ============ EMAIL VERIFICATION (Simple MFA) ============

@router.post("/email/send-code")
async def send_email_verification_code(
    user: dict = Depends(require_auth)
):
    """Send a verification code to user's email"""
    
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await send_verification_email(
        user_id=user["user_id"],
        user_email=user.get("email", "")
    )
    
    return result


class EmailVerificationRequest(BaseModel):
    code: str


@router.post("/email/verify")
async def verify_email_verification_code(
    request: EmailVerificationRequest,
    user: dict = Depends(require_auth)
):
    """Verify the email verification code"""
    
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await verify_email_code(user["user_id"], request.code)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Verification failed"))
    
    return result


@router.get("/email/status")
async def get_email_verification_status_endpoint(
    user: dict = Depends(require_auth)
):
    """Check email verification status"""
    
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return await get_email_verification_status(user["user_id"])


# ============ TOTP MFA ENDPOINTS (Advanced) ============

class MFACodeRequest(BaseModel):
    code: str


@router.post("/mfa/setup")
async def setup_user_mfa(
    user: dict = Depends(require_auth)
):
    """Set up MFA for the current user"""
    
    result = await setup_mfa(
        user_id=user["user_id"],
        user_email=user.get("email", "")
    )
    
    return result


@router.post("/mfa/verify-setup")
async def verify_user_mfa_setup(
    request: MFACodeRequest,
    user: dict = Depends(require_auth)
):
    """Verify MFA setup with initial code"""
    
    result = await verify_mfa_setup(user["user_id"], request.code)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Verification failed"))
    
    return result


@router.post("/mfa/verify")
async def verify_user_mfa(
    request: MFACodeRequest,
    user: dict = Depends(require_auth)
):
    """Verify MFA code during login"""
    
    result = await verify_mfa_code(user["user_id"], request.code)
    
    if not result.get("success"):
        raise HTTPException(status_code=401, detail=result.get("error", "Invalid code"))
    
    return result


@router.post("/mfa/disable")
async def disable_user_mfa(
    request: MFACodeRequest,
    user: dict = Depends(require_auth)
):
    """Disable MFA (requires valid code)"""
    
    result = await disable_mfa(user["user_id"], request.code)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to disable MFA"))
    
    return result


@router.get("/mfa/status")
async def get_user_mfa_status(
    user: dict = Depends(require_auth)
):
    """Get MFA status for current user"""
    
    return await get_mfa_status(user["user_id"])


@router.post("/mfa/backup-codes")
async def regenerate_user_backup_codes(
    request: MFACodeRequest,
    user: dict = Depends(require_auth)
):
    """Regenerate backup codes (requires valid MFA code)"""
    
    result = await regenerate_backup_codes(user["user_id"], request.code)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to regenerate codes"))
    
    return result


# ============ SECURITY LOGS ============

@router.get("/logs")
async def get_user_security_logs(
    limit: int = 50,
    event_type: Optional[str] = None,
    user: dict = Depends(require_auth)
):
    """Get security logs for current user"""
    
    logs = await get_security_logs(
        user_id=user["user_id"],
        limit=limit,
        event_type=event_type
    )
    
    return {"logs": logs}


# ============ CONSENT MANAGEMENT ============

class ConsentRequest(BaseModel):
    consent_type: str
    consented: bool
    details: Optional[Dict] = None


@router.post("/consent")
async def record_user_consent(
    request: ConsentRequest,
    req: Request,
    user: dict = Depends(require_auth)
):
    """Record user consent"""
    
    ip_address = req.client.host if req.client else None
    
    consent = await record_consent(
        user_id=user["user_id"],
        consent_type=request.consent_type,
        consented=request.consented,
        ip_address=ip_address,
        details=request.details
    )
    
    return consent


@router.get("/consent")
async def get_user_consent_records(
    user: dict = Depends(require_auth)
):
    """Get all consent records for current user"""
    
    consents = await get_user_consents(user["user_id"])
    return {"consents": consents}


@router.get("/consent/{consent_type}")
async def check_user_consent(
    consent_type: str,
    user: dict = Depends(require_auth)
):
    """Check if user has given consent for a specific type"""
    
    has_consent = await check_consent(user["user_id"], consent_type)
    return {"consent_type": consent_type, "consented": has_consent}


# ============ GDPR DATA PORTABILITY ============

@router.get("/data/export")
async def export_user_data_endpoint(
    user: dict = Depends(require_auth)
):
    """Export all user data (GDPR data portability)"""
    
    data = await export_user_data(user["user_id"])
    return data


class DeleteDataRequest(BaseModel):
    confirmation: str


@router.delete("/data")
async def delete_user_data_endpoint(
    request: DeleteDataRequest,
    user: dict = Depends(require_auth)
):
    """Delete all user data (GDPR right to erasure)"""
    
    result = await delete_user_data(user["user_id"], request.confirmation)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Deletion failed"))
    
    return result


# ============ COMPLIANCE STATUS ============

@router.get("/compliance")
async def get_compliance_status_endpoint(
    user: dict = Depends(require_auth)
):
    """Get overall compliance status"""
    
    return get_compliance_status()


# ============ DATA RETENTION ============

class DataRetentionRequest(BaseModel):
    retention_days: int = 90
    auto_delete: bool = True


@router.post("/retention")
async def set_user_retention_policy(
    request: DataRetentionRequest,
    user: dict = Depends(require_auth)
):
    """Set data retention policy"""
    
    policy = await set_data_retention_policy(
        user_id=user["user_id"],
        retention_days=request.retention_days,
        auto_delete=request.auto_delete
    )
    
    return policy


@router.get("/retention")
async def get_user_retention_policy(
    user: dict = Depends(require_auth)
):
    """Get data retention policy"""
    
    return await get_data_retention_policy(user["user_id"])
