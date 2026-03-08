"""
ENZI Invite & Security System
- Registration-gated invites: invited users MUST register before accessing ENZI
- Domain-based company discovery: users with same email domain can find each other
- Invite tokens with expiry to prevent unauthorized access
- Uses Resend API for email delivery
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import uuid
import os
import logging

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi/invite", tags=["ENZI Invites"])
logger = logging.getLogger(__name__)

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")
APP_URL = os.environ.get("REACT_APP_BACKEND_URL", "")
INVITE_EXPIRY_DAYS = 7


class InviteRequest(BaseModel):
    emails: List[str]
    message: Optional[str] = ""


class InviteRegister(BaseModel):
    invite_token: str
    name: str
    email: str
    password: str


def _extract_domain(email: str) -> str:
    """Extract domain from email address"""
    if "@" in email:
        return email.split("@")[1].lower()
    return ""


def _build_invite_email_html(sender_name: str, message: str, invite_url: str) -> str:
    custom_msg = f'<p style="color:#64748b;font-size:14px;margin:16px 0;font-style:italic;">"{message}"</p>' if message else ""
    return f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:520px;margin:0 auto;padding:32px;">
        <div style="text-align:center;margin-bottom:24px;">
            <h1 style="font-size:28px;font-weight:900;letter-spacing:0.1em;margin:0;">
                <span style="background:linear-gradient(135deg,#00CEC9,#6C5CE7,#E84393);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">ENZI</span>
            </h1>
            <p style="color:#94a3b8;font-size:11px;letter-spacing:0.15em;text-transform:uppercase;margin:4px 0 0;">Intelligence in Every Conversation</p>
        </div>
        <div style="background:#f8fafc;border-radius:12px;padding:24px;border:1px solid #e2e8f0;">
            <p style="color:#1e293b;font-size:16px;margin:0 0 8px;"><strong>{sender_name}</strong> invited you to join ENZI Messenger</p>
            <p style="color:#64748b;font-size:14px;margin:0;">A secure, AI-powered team communication platform with channels, direct messaging, and intelligent automation.</p>
            {custom_msg}
        </div>
        <div style="text-align:center;margin-top:24px;">
            <a href="{invite_url}" style="display:inline-block;padding:12px 32px;background:linear-gradient(135deg,#00CEC9,#6C5CE7);color:white;text-decoration:none;border-radius:8px;font-weight:600;font-size:14px;">
                Join ENZI Messenger
            </a>
        </div>
        <p style="color:#94a3b8;font-size:11px;text-align:center;margin-top:20px;">
            You'll need to create an account to get started. This invite expires in {INVITE_EXPIRY_DAYS} days.
        </p>
    </div>
    """


@router.post("/send")
async def send_invites(req: InviteRequest, request: Request):
    """Send email invitations to join ENZI Messenger (registration required)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    sender_name = user.get("name", user.get("email", "Someone"))
    results = []

    for email in req.emails[:10]:
        email = email.strip().lower()
        if not email or "@" not in email:
            continue

        # Check if already a user
        existing = await db.users.find_one({"email": email})
        if existing:
            results.append({"email": email, "status": "already_registered", "email_sent": False})
            continue

        # Check for existing pending invite
        existing_invite = await db.enzi_invites.find_one({
            "invited_email": email, "status": "pending",
            "expires_at": {"$gt": datetime.now(timezone.utc).isoformat()}
        })
        if existing_invite:
            results.append({"email": email, "status": "already_invited", "email_sent": False, "invite_id": existing_invite["id"]})
            continue

        invite_id = str(uuid.uuid4())
        invite_url = f"{APP_URL}/lumi?invite_token={invite_id}"
        expires_at = (datetime.now(timezone.utc) + timedelta(days=INVITE_EXPIRY_DAYS)).isoformat()

        await db.enzi_invites.insert_one({
            "id": invite_id,
            "invited_email": email,
            "invited_by": user.get("user_id"),
            "invited_by_name": sender_name,
            "invited_by_domain": _extract_domain(user.get("email", "")),
            "message": req.message,
            "status": "pending",
            "type": "email",
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc).isoformat()
        })

        email_sent = False
        if RESEND_API_KEY:
            try:
                import resend
                resend.api_key = RESEND_API_KEY
                resend.Emails.send({
                    "from": f"ENZI <{SENDER_EMAIL}>",
                    "to": [email],
                    "subject": f"{sender_name} invited you to ENZI Messenger",
                    "html": _build_invite_email_html(sender_name, req.message, invite_url)
                })
                email_sent = True
                logger.info(f"Invite email sent to {email}")
            except Exception as e:
                logger.error(f"Failed to send invite to {email}: {e}")

        results.append({"email": email, "status": "invited", "invite_id": invite_id, "email_sent": email_sent})

    return {"results": results, "count": len(results)}


@router.get("/validate/{invite_token}")
async def validate_invite(invite_token: str):
    """Validate an invite token - public endpoint for registration page"""
    invite = await db.enzi_invites.find_one({"id": invite_token}, {"_id": 0})
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid invite link")

    if invite.get("status") == "accepted":
        return {"valid": False, "reason": "already_used", "invite": None}

    if invite.get("expires_at") and invite["expires_at"] < datetime.now(timezone.utc).isoformat():
        return {"valid": False, "reason": "expired", "invite": None}

    return {
        "valid": True,
        "invite": {
            "id": invite["id"],
            "invited_by_name": invite.get("invited_by_name", "Someone"),
            "invited_email": invite.get("invited_email", ""),
            "message": invite.get("message", ""),
            "type": invite.get("type", "email")
        }
    }


@router.post("/register")
async def register_via_invite(req: InviteRegister):
    """Register a new user via invite token - enforces invite-gated registration"""
    invite = await db.enzi_invites.find_one({"id": req.invite_token})
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid invite token")

    if invite.get("status") == "accepted":
        raise HTTPException(status_code=400, detail="This invite has already been used")

    if invite.get("expires_at") and invite["expires_at"] < datetime.now(timezone.utc).isoformat():
        raise HTTPException(status_code=400, detail="This invite has expired")

    # Check if email already registered
    existing = await db.users.find_one({"email": req.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered. Please sign in instead.")

    import hashlib
    user_id = str(uuid.uuid4())
    domain = _extract_domain(req.email)

    new_user = {
        "user_id": user_id,
        "email": req.email.lower(),
        "name": req.name,
        "password_hash": hashlib.sha256(req.password.encode()).hexdigest(),
        "role": "user",
        "auth_method": "invite",
        "invited_by": invite.get("invited_by"),
        "domain": domain,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_verified": True
    }
    await db.users.insert_one(new_user)

    # Mark invite as accepted
    await db.enzi_invites.update_one(
        {"id": req.invite_token},
        {"$set": {"status": "accepted", "accepted_by": user_id, "accepted_at": datetime.now(timezone.utc).isoformat()}}
    )

    # Generate JWT
    import jwt
    jwt_secret = os.environ.get("JWT_SECRET_KEY", "secret")
    token = jwt.encode(
        {"user_id": user_id, "email": req.email.lower(), "exp": datetime.now(timezone.utc) + timedelta(days=30)},
        jwt_secret, algorithm="HS256"
    )

    return {
        "access_token": token,
        "user": {
            "user_id": user_id,
            "email": req.email.lower(),
            "name": req.name,
            "role": "user",
            "domain": domain
        }
    }


@router.get("/link")
async def get_invite_link(request: Request):
    """Generate a shareable invite link"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    invite_id = str(uuid.uuid4())
    invite_url = f"{APP_URL}/lumi?invite_token={invite_id}"

    await db.enzi_invites.insert_one({
        "id": invite_id,
        "type": "link",
        "invited_by": user.get("user_id"),
        "invited_by_name": user.get("name", user.get("email", "User")),
        "invited_by_domain": _extract_domain(user.get("email", "")),
        "status": "active",
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=INVITE_EXPIRY_DAYS)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {
        "invite_url": invite_url,
        "invite_id": invite_id,
        "sms_text": f"Join me on ENZI Messenger — secure, AI-powered team communication: {invite_url}",
        "linkedin_url": f"https://www.linkedin.com/sharing/share-offsite/?url={invite_url}",
        "twitter_url": f"https://twitter.com/intent/tweet?text=Join+me+on+ENZI+Messenger&url={invite_url}"
    }


@router.get("/history")
async def get_invite_history(request: Request):
    """Get invite history for current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    invites = await db.enzi_invites.find(
        {"invited_by": user.get("user_id")},
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)

    return {"invites": invites, "count": len(invites)}
