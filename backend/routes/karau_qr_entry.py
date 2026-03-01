"""
QR Code Touchless Meeting Entry API
Generate QR codes for instant meeting join without manual credentials.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid
import hashlib
import logging

from utils.database import db
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/karau-meet/qr", tags=["QR Code Entry"])


class QRGenerateRequest(BaseModel):
    meeting_id: str
    expires_minutes: int = 60
    max_uses: int = 100
    label: Optional[str] = ""


@router.post("/generate")
async def generate_qr_code(data: QRGenerateRequest, user=Depends(require_auth)):
    """Generate a unique QR code token for a meeting."""
    # Verify meeting exists and user is host
    meeting = await db.karau_meetings.find_one({"meeting_id": data.meeting_id}, {"_id": 0, "host_id": 1, "title": 1})
    if not meeting:
        # Check webinars too
        meeting = await db.webinars.find_one({"webinar_id": data.meeting_id}, {"_id": 0, "host_id": 1, "title": 1})

    if not meeting:
        raise HTTPException(404, "Meeting not found")

    host_id = meeting.get("host_id", "")
    if host_id != user["user_id"]:
        raise HTTPException(403, "Only the host can generate QR codes")

    # Generate unique token
    qr_token = f"QR-{uuid.uuid4().hex[:12]}"
    qr_hash = hashlib.sha256(qr_token.encode()).hexdigest()[:16]
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=data.expires_minutes)).isoformat()

    qr_doc = {
        "qr_token": qr_token,
        "qr_hash": qr_hash,
        "meeting_id": data.meeting_id,
        "meeting_title": meeting.get("title", "Meeting"),
        "host_id": user["user_id"],
        "host_name": user.get("name", user.get("email", "")),
        "label": data.label or f"QR for {meeting.get('title', 'Meeting')}",
        "expires_at": expires_at,
        "max_uses": data.max_uses,
        "use_count": 0,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    await db.meeting_qr_codes.insert_one(qr_doc)

    return {
        "qr_token": qr_token,
        "qr_hash": qr_hash,
        "meeting_id": data.meeting_id,
        "meeting_title": meeting.get("title", "Meeting"),
        "expires_at": expires_at,
        "max_uses": data.max_uses,
        "join_url": f"/karau-meet/join/qr/{qr_token}"
    }


@router.get("/validate/{qr_token}")
async def validate_qr_code(qr_token: str):
    """Validate a QR code token and return meeting info for joining."""
    qr = await db.meeting_qr_codes.find_one({"qr_token": qr_token}, {"_id": 0})
    if not qr:
        raise HTTPException(404, "Invalid QR code")

    if not qr.get("active"):
        raise HTTPException(410, "QR code has been deactivated")

    # Check expiry
    expires_at = qr.get("expires_at", "")
    if expires_at:
        try:
            exp_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            if exp_dt < datetime.now(timezone.utc):
                raise HTTPException(410, "QR code has expired")
        except (ValueError, TypeError):
            pass

    # Check max uses
    if qr.get("use_count", 0) >= qr.get("max_uses", 100):
        raise HTTPException(410, "QR code max uses reached")

    # Increment use count
    await db.meeting_qr_codes.update_one(
        {"qr_token": qr_token},
        {"$inc": {"use_count": 1}}
    )

    return {
        "valid": True,
        "meeting_id": qr["meeting_id"],
        "meeting_title": qr.get("meeting_title", "Meeting"),
        "host_name": qr.get("host_name", ""),
        "join_url": f"/karau-meet/webinar/{qr['meeting_id']}/live"
    }


@router.get("/meeting/{meeting_id}")
async def list_qr_codes(meeting_id: str, user=Depends(require_auth)):
    """List all QR codes for a meeting."""
    qrs = await db.meeting_qr_codes.find(
        {"meeting_id": meeting_id, "host_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(20)

    return {"qr_codes": qrs}


@router.delete("/{qr_token}")
async def deactivate_qr_code(qr_token: str, user=Depends(require_auth)):
    """Deactivate a QR code."""
    result = await db.meeting_qr_codes.update_one(
        {"qr_token": qr_token, "host_id": user["user_id"]},
        {"$set": {"active": False}}
    )
    if result.modified_count == 0:
        raise HTTPException(404, "QR code not found or not yours")
    return {"success": True, "deactivated": qr_token}
