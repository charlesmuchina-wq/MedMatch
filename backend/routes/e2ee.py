"""
ENZI End-to-End Encryption
- Key pair generation initiation
- Public key exchange 
- Encrypted DM key storage
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi/e2ee", tags=["ENZI E2EE"])


class PublishKeyRequest(BaseModel):
    public_key: str  # JWK format public key


class EncryptedMessageRequest(BaseModel):
    channel_id: str
    encrypted_content: str  # Base64 encrypted content
    iv: str  # Initialization vector for AES-GCM
    sender_public_key: Optional[str] = ""


@router.post("/keys/publish")
async def publish_public_key(req: PublishKeyRequest, request: Request):
    """Publish user's public key for E2EE key exchange"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    await db.e2ee_keys.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "user_id": user["user_id"],
            "public_key": req.public_key,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )

    return {"status": "published", "user_id": user["user_id"]}


@router.get("/keys/{user_id}")
async def get_public_key(user_id: str, request: Request):
    """Get a user's public key for E2EE"""
    auth_user = await get_current_user(request)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    key_doc = await db.e2ee_keys.find_one({"user_id": user_id}, {"_id": 0})
    if not key_doc:
        raise HTTPException(status_code=404, detail="Public key not found. User hasn't enabled E2EE.")

    return {
        "user_id": user_id,
        "public_key": key_doc["public_key"],
        "updated_at": key_doc.get("updated_at", "")
    }


@router.get("/keys/status/me")
async def get_my_e2ee_status(request: Request):
    """Check if current user has published E2EE keys"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    key_doc = await db.e2ee_keys.find_one({"user_id": user["user_id"]}, {"_id": 0})
    return {
        "enabled": key_doc is not None,
        "has_public_key": key_doc is not None,
        "updated_at": key_doc.get("updated_at", "") if key_doc else None
    }


@router.post("/enable")
async def enable_e2ee(request: Request):
    """Enable E2EE for the current user (marks user as E2EE-ready)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"e2ee_enabled": True}}
    )

    return {"status": "enabled", "message": "E2EE enabled. Generate and publish your key pair."}


@router.post("/disable")
async def disable_e2ee(request: Request):
    """Disable E2EE for the current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"e2ee_enabled": False}}
    )
    await db.e2ee_keys.delete_one({"user_id": user["user_id"]})

    return {"status": "disabled", "message": "E2EE disabled. Keys removed."}


@router.get("/dm/{channel_id}/status")
async def get_dm_e2ee_status(channel_id: str, request: Request):
    """Check if both participants in a DM have E2EE keys"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Find the DM channel
    channel = await db.lumi_channels.find_one({"id": channel_id, "channel_type": "dm"}, {"_id": 0})
    if not channel:
        return {"encrypted": False, "reason": "Not a DM channel"}

    members = channel.get("members", [])
    if len(members) < 2:
        return {"encrypted": False, "reason": "Insufficient members"}

    # Check both members have keys
    keys = await db.e2ee_keys.find(
        {"user_id": {"$in": members}},
        {"_id": 0}
    ).to_list(2)

    both_have_keys = len(keys) == 2
    partner_id = [m for m in members if m != user["user_id"]]
    partner_key = next((k for k in keys if k["user_id"] != user["user_id"]), None)

    return {
        "encrypted": both_have_keys,
        "my_key_published": any(k["user_id"] == user["user_id"] for k in keys),
        "partner_key_available": partner_key is not None,
        "partner_id": partner_id[0] if partner_id else None,
        "partner_public_key": partner_key["public_key"] if partner_key else None
    }
