"""
Email Settings Management
Allows admins to view and update Resend API key and sender email
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import os
import logging

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/admin/email-settings", tags=["Email Settings"])
logger = logging.getLogger(__name__)

COLLECTION = "app_settings"


class EmailSettingsUpdate(BaseModel):
    resend_api_key: Optional[str] = None
    sender_email: Optional[str] = None


class EmailTestRequest(BaseModel):
    to_email: str


@router.get("")
async def get_email_settings(request: Request):
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    settings = await db.app_settings.find_one({"type": "email"}, {"_id": 0})
    env_key = os.environ.get("RESEND_API_KEY", "")
    env_sender = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")

    if settings:
        masked = ""
        key = settings.get("resend_api_key", env_key)
        if key:
            masked = key[:6] + "..." + key[-4:] if len(key) > 10 else "****"
        return {
            "resend_api_key_masked": masked,
            "sender_email": settings.get("sender_email", env_sender),
            "is_configured": bool(key),
            "source": "database",
            "updated_at": settings.get("updated_at"),
        }

    masked = ""
    if env_key:
        masked = env_key[:6] + "..." + env_key[-4:] if len(env_key) > 10 else "****"
    return {
        "resend_api_key_masked": masked,
        "sender_email": env_sender,
        "is_configured": bool(env_key),
        "source": "environment",
        "updated_at": None,
    }


@router.put("")
async def update_email_settings(body: EmailSettingsUpdate, request: Request):
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    update = {"type": "email", "updated_at": datetime.now(timezone.utc).isoformat(), "updated_by": user.get("id", "")}
    if body.resend_api_key is not None:
        update["resend_api_key"] = body.resend_api_key
        os.environ["RESEND_API_KEY"] = body.resend_api_key
    if body.sender_email is not None:
        update["sender_email"] = body.sender_email
        os.environ["SENDER_EMAIL"] = body.sender_email

    await db.app_settings.update_one({"type": "email"}, {"$set": update}, upsert=True)

    return {"success": True, "message": "Email settings updated"}


@router.post("/test")
async def test_email_settings(body: EmailTestRequest, request: Request):
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    settings = await db.app_settings.find_one({"type": "email"}, {"_id": 0})
    api_key = (settings or {}).get("resend_api_key", os.environ.get("RESEND_API_KEY", ""))
    sender = (settings or {}).get("sender_email", os.environ.get("SENDER_EMAIL", "onboarding@resend.dev"))

    if not api_key:
        raise HTTPException(status_code=400, detail="No Resend API key configured")

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "from": sender,
                    "to": [body.to_email],
                    "subject": "AI Suite - Email Configuration Test",
                    "html": "<h2>Email Configuration Verified</h2><p>Your Resend integration is working correctly.</p><p style='color:#64748b;font-size:12px;'>Sent from AI Suite (AI KARAU + ENZI + MedMatch)</p>",
                },
                timeout=10.0,
            )
        if resp.status_code in (200, 201):
            return {"success": True, "message": f"Test email sent to {body.to_email}"}
        else:
            detail = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text
            return {"success": False, "message": f"Resend API error: {resp.status_code}", "detail": detail}
    except Exception as e:
        logger.error(f"Email test failed: {e}")
        return {"success": False, "message": str(e)}
