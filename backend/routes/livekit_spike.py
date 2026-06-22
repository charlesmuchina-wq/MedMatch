"""
LiveKit Phase 0 spike — SFU token minting + webhook (provider-agnostic).

POST /api/livekit/token   : mint a room access token for the authenticated user
POST /api/livekit/webhook : verified LiveKit room/egress events
GET  /api/livekit/status  : config presence check

Keys live in backend/.env only; the browser receives only the short-lived JWT.
"""
import os
import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from livekit import api

from routes.auth import require_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/livekit", tags=["LiveKit SFU"])

LIVEKIT_API_KEY = os.environ.get("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.environ.get("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.environ.get("LIVEKIT_URL")


class TokenRequest(BaseModel):
    room_name: str
    can_publish: bool = True


@router.get("/status")
async def livekit_status():
    return {
        "configured": bool(LIVEKIT_API_KEY and LIVEKIT_API_SECRET and LIVEKIT_URL),
        "url": LIVEKIT_URL,
    }


def create_access_token(room: str, identity: str, name: str, can_publish: bool = True, ttl_hours: int = 2) -> str:
    """Mint a LiveKit access token. Raises HTTPException if unconfigured."""
    if not (LIVEKIT_API_KEY and LIVEKIT_API_SECRET and LIVEKIT_URL):
        raise HTTPException(status_code=503, detail="LiveKit is not configured")
    import datetime as _dt
    grants = api.VideoGrants(
        room_join=True, room=room,
        can_publish=can_publish, can_subscribe=True, can_publish_data=True,
    )
    return (
        api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(identity)
        .with_name(name)
        .with_grants(grants)
        .with_ttl(_dt.timedelta(hours=ttl_hours))
        .to_jwt()
    )


def get_lk_api():
    """Return a LiveKit server API client (https endpoint)."""
    if not (LIVEKIT_API_KEY and LIVEKIT_API_SECRET and LIVEKIT_URL):
        raise HTTPException(status_code=503, detail="LiveKit is not configured")
    http_url = LIVEKIT_URL.replace("wss://", "https://").replace("ws://", "http://")
    return api.LiveKitAPI(http_url, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)


@router.post("/token")
async def mint_token(body: TokenRequest, request: Request):
    user = await require_auth(request)
    room = (body.room_name or "").strip()
    if not room:
        raise HTTPException(status_code=400, detail="room_name is required")
    identity = f"{user['user_id']}"
    display = user.get("name") or user.get("email") or identity
    token = create_access_token(room, identity, display, body.can_publish)
    return {"token": token, "url": LIVEKIT_URL, "room": room, "identity": identity}


@router.post("/webhook")
async def livekit_webhook(request: Request):
    """Verify LiveKit webhook using the RAW body (HMAC-SHA256 over bytes)."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    raw_body = (await request.body()).decode("utf-8")
    try:
        verifier = api.TokenVerifier(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        receiver = api.WebhookReceiver(verifier)
        event = receiver.receive(raw_body, auth_header)
        logger.info(f"LiveKit webhook verified: {event.event} room={getattr(event.room, 'name', None)}")
        # Acknowledge fast; downstream sync (recordings/participants) handled elsewhere.
        return {"status": "ok", "event": event.event}
    except Exception as e:
        logger.warning(f"LiveKit webhook verification failed: {e}")
        raise HTTPException(status_code=403, detail="Webhook verification failed")
