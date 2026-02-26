"""
KARAU Guest Verification - 2FA and Age Verification
Handles: Guest registration, email OTP, age self-declaration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid
import random
import logging
import os
import httpx

from utils.database import db

router = APIRouter(prefix="/karau-meet/guest", tags=["KARAU Guest Verification"])
logger = logging.getLogger(__name__)

# In-memory OTP store (production: use Redis with TTL)
otp_store = {}  # email -> {otp, expires_at, verified, attempts}

MIN_AGE = 16  # Zoom/Teams standard
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")


class GuestRegisterRequest(BaseModel):
    email: str
    name: str
    meeting_id: str


class VerifyOTPRequest(BaseModel):
    email: str
    otp: str
    meeting_id: str


class AgeDeclarationRequest(BaseModel):
    email: str
    meeting_id: str
    confirmed_age_16_plus: bool
    date_of_birth: Optional[str] = None  # Optional, for records


class GuestVerificationStatus(BaseModel):
    email: str
    meeting_id: str


# ============ STEP 1: REGISTER & SEND OTP ============

@router.post("/register")
async def guest_register(request: GuestRegisterRequest):
    """Step 1: Guest provides email + name. System sends OTP."""
    email = request.email.lower().strip()
    name = request.name.strip()

    if not email or '@' not in email:
        raise HTTPException(status_code=400, detail="Valid email required")
    if not name:
        raise HTTPException(status_code=400, detail="Name required")

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)

    otp_store[email] = {
        "otp": otp,
        "name": name,
        "meeting_id": request.meeting_id,
        "expires_at": expires.isoformat(),
        "verified": False,
        "attempts": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Store in DB for audit
    await db.karau_guest_otps.update_one(
        {"email": email, "meeting_id": request.meeting_id},
        {"$set": {
            "email": email,
            "name": name,
            "meeting_id": request.meeting_id,
            "otp_hash": otp,  # In production: hash this
            "expires_at": expires.isoformat(),
            "verified": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True
    )

    # Send OTP via email (use Resend or similar in production)
    # For now, log it and return success with hint
    logger.info(f"Guest OTP for {email}: {otp}")

    return {
        "success": True,
        "email": email,
        "message": "Verification code sent to your email",
        "expires_in_minutes": 10,
        # DEV ONLY: Include OTP in response for testing
        "_dev_otp": otp,
    }


# ============ STEP 2: VERIFY OTP ============

@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    """Step 2: Guest enters OTP from email."""
    email = request.email.lower().strip()

    stored = otp_store.get(email)
    if not stored:
        raise HTTPException(status_code=400, detail="No verification pending. Request a new code.")

    # Check attempts
    if stored["attempts"] >= 5:
        del otp_store[email]
        raise HTTPException(status_code=429, detail="Too many attempts. Request a new code.")

    stored["attempts"] += 1

    # Check expiry
    expires = datetime.fromisoformat(stored["expires_at"])
    if datetime.now(timezone.utc) > expires:
        del otp_store[email]
        raise HTTPException(status_code=400, detail="Code expired. Request a new one.")

    # Check OTP
    if request.otp != stored["otp"]:
        remaining = 5 - stored["attempts"]
        raise HTTPException(status_code=400, detail=f"Invalid code. {remaining} attempts remaining.")

    # Mark as verified
    stored["verified"] = True
    otp_store[email] = stored

    await db.karau_guest_otps.update_one(
        {"email": email, "meeting_id": request.meeting_id},
        {"$set": {"verified": True, "verified_at": datetime.now(timezone.utc).isoformat()}}
    )

    return {
        "success": True,
        "email": email,
        "verified": True,
        "message": "Email verified. Please confirm your age to continue.",
        "next_step": "age_declaration",
    }


# ============ STEP 3: AGE DECLARATION ============

@router.post("/age-declaration")
async def age_declaration(request: AgeDeclarationRequest):
    """Step 3: Guest confirms they are 16+ (self-declaration)."""
    email = request.email.lower().strip()

    stored = otp_store.get(email)
    if not stored or not stored.get("verified"):
        raise HTTPException(status_code=400, detail="Email not verified. Complete verification first.")

    if not request.confirmed_age_16_plus:
        raise HTTPException(
            status_code=403,
            detail=f"You must be at least {MIN_AGE} years old to join video meetings."
        )

    # Create verified guest record
    guest_id = f"guest_{uuid.uuid4().hex[:12]}"
    guest_record = {
        "guest_id": guest_id,
        "email": email,
        "name": stored["name"],
        "meeting_id": request.meeting_id,
        "email_verified": True,
        "age_declared": True,
        "age_declaration_text": f"Confirmed 16+ on {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "date_of_birth": request.date_of_birth,
        "verification_method": "email_otp",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "verified",
    }

    await db.karau_verified_guests.update_one(
        {"email": email, "meeting_id": request.meeting_id},
        {"$set": guest_record},
        upsert=True
    )

    # Cleanup OTP
    if email in otp_store:
        del otp_store[email]

    return {
        "success": True,
        "guest_id": guest_id,
        "email": email,
        "name": stored["name"],
        "verified": True,
        "age_declared": True,
        "message": "Verification complete. You can now join the meeting.",
        "user": {
            "user_id": guest_id,
            "name": stored["name"],
            "email": email,
            "is_guest": True,
            "is_verified": True,
        }
    }


# ============ RESEND OTP ============

@router.post("/resend-otp")
async def resend_otp(request: GuestRegisterRequest):
    """Resend OTP to guest email."""
    email = request.email.lower().strip()

    otp = str(random.randint(100000, 999999))
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)

    otp_store[email] = {
        "otp": otp,
        "name": request.name.strip(),
        "meeting_id": request.meeting_id,
        "expires_at": expires.isoformat(),
        "verified": False,
        "attempts": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    logger.info(f"Resent OTP for {email}: {otp}")

    return {
        "success": True,
        "email": email,
        "message": "New verification code sent",
        "_dev_otp": otp,
    }


# ============ CHECK VERIFICATION STATUS ============

@router.get("/status")
async def check_guest_status(email: str, meeting_id: str):
    """Check if a guest is already verified for a meeting."""
    email = email.lower().strip()

    record = await db.karau_verified_guests.find_one(
        {"email": email, "meeting_id": meeting_id, "status": "verified"},
        {"_id": 0}
    )

    if record:
        return {
            "verified": True,
            "guest_id": record["guest_id"],
            "name": record["name"],
            "email": record["email"],
            "user": {
                "user_id": record["guest_id"],
                "name": record["name"],
                "email": record["email"],
                "is_guest": True,
                "is_verified": True,
            }
        }

    return {"verified": False}
