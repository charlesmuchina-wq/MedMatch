"""
KARAU Calendar Integration - Microsoft Outlook/365 + Apple Calendar
Handles: OAuth flow, event sync, calendar push
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import urllib.parse
import uuid
import logging
import httpx
import os

from utils.database import db
from routes.auth import require_auth

router = APIRouter(prefix="/karau-meet/calendar", tags=["KARAU Calendar Integration"])
logger = logging.getLogger(__name__)

# Microsoft Graph API config
MS_CLIENT_ID = os.environ.get("MS_CALENDAR_CLIENT_ID", "")
MS_CLIENT_SECRET = os.environ.get("MS_CALENDAR_CLIENT_SECRET", "")
MS_REDIRECT_URI = os.environ.get("MS_CALENDAR_REDIRECT_URI", "")
MS_AUTHORITY = "https://login.microsoftonline.com/common"
MS_GRAPH_URL = "https://graph.microsoft.com/v1.0"
MS_SCOPES = "Calendars.ReadWrite offline_access User.Read"

# Google Calendar API config
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CALENDAR_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CALENDAR_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_CALENDAR_REDIRECT_URI", "")
GOOGLE_SCOPES = "https://www.googleapis.com/auth/calendar.events"


class CalendarSyncRequest(BaseModel):
    meeting_id: str
    title: str
    start_time: str
    end_time: str
    description: Optional[str] = ""
    join_url: Optional[str] = ""


class CalendarDisconnectRequest(BaseModel):
    provider: str  # "microsoft" or "google"


# ============ CONNECTION STATUS ============

@router.get("/status")
async def get_calendar_status(user=Depends(require_auth)):
    """Check which calendar providers are connected."""
    user_id = user["user_id"]
    connections = await db.karau_calendar_connections.find(
        {"user_id": user_id}, {"_id": 0, "access_token": 0, "refresh_token": 0}
    ).to_list(10)

    providers = {}
    for conn in connections:
        providers[conn["provider"]] = {
            "connected": True,
            "email": conn.get("email", ""),
            "connected_at": conn.get("connected_at", ""),
            "last_sync": conn.get("last_sync", ""),
        }

    configured = {
        "microsoft": bool(MS_CLIENT_ID and MS_CLIENT_SECRET),
        "google": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET),
        "apple_ics": True,  # Always available via .ics export
    }

    return {"providers": providers, "configured": configured}


# ============ MICROSOFT OAUTH ============

@router.get("/microsoft/connect")
async def microsoft_connect(request: Request, user=Depends(require_auth)):
    """Start Microsoft OAuth flow for calendar access."""
    if not MS_CLIENT_ID or not MS_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="Microsoft Calendar integration not configured. Admin must set MS_CALENDAR_CLIENT_ID and MS_CALENDAR_CLIENT_SECRET.")

    state = f"{user['user_id']}:{uuid.uuid4().hex[:16]}"
    await db.karau_oauth_states.update_one(
        {"state": state},
        {"$set": {"user_id": user["user_id"], "provider": "microsoft", "created_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )

    params = urllib.parse.urlencode({
        "client_id": MS_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": MS_REDIRECT_URI,
        "response_mode": "query",
        "scope": MS_SCOPES,
        "state": state,
    })
    return {"auth_url": f"{MS_AUTHORITY}/oauth2/v2.0/authorize?{params}"}


@router.get("/microsoft/callback")
async def microsoft_callback(code: str, state: str):
    """Handle Microsoft OAuth callback."""
    record = await db.karau_oauth_states.find_one({"state": state})
    if not record:
        raise HTTPException(status_code=400, detail="Invalid state")

    user_id = record["user_id"]
    await db.karau_oauth_states.delete_one({"state": state})

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            f"{MS_AUTHORITY}/oauth2/v2.0/token",
            data={
                "client_id": MS_CLIENT_ID,
                "client_secret": MS_CLIENT_SECRET,
                "code": code,
                "redirect_uri": MS_REDIRECT_URI,
                "grant_type": "authorization_code",
                "scope": MS_SCOPES,
            },
        )
        if token_resp.status_code != 200:
            logger.error(f"Microsoft token exchange failed: {token_resp.text}")
            raise HTTPException(status_code=400, detail="Failed to connect Microsoft Calendar")

        tokens = token_resp.json()

        # Get user profile
        profile_resp = await client.get(
            f"{MS_GRAPH_URL}/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        profile = profile_resp.json() if profile_resp.status_code == 200 else {}

    await db.karau_calendar_connections.update_one(
        {"user_id": user_id, "provider": "microsoft"},
        {"$set": {
            "user_id": user_id,
            "provider": "microsoft",
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token", ""),
            "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=tokens.get("expires_in", 3600))).isoformat(),
            "email": profile.get("mail") or profile.get("userPrincipalName", ""),
            "display_name": profile.get("displayName", ""),
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )

    # Redirect to frontend settings
    return RedirectResponse(url="/karau-meet/settings?calendar=connected")


# ============ GOOGLE CALENDAR OAUTH ============

@router.get("/google/connect")
async def google_connect(user=Depends(require_auth)):
    """Start Google OAuth flow for calendar access."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="Google Calendar integration not configured. Admin must set GOOGLE_CALENDAR_CLIENT_ID and GOOGLE_CALENDAR_CLIENT_SECRET.")

    state = f"{user['user_id']}:{uuid.uuid4().hex[:16]}"
    await db.karau_oauth_states.update_one(
        {"state": state},
        {"$set": {"user_id": user["user_id"], "provider": "google", "created_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )

    params = urllib.parse.urlencode({
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": GOOGLE_SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    })
    return {"auth_url": f"https://accounts.google.com/o/oauth2/v2/auth?{params}"}


@router.get("/google/callback")
async def google_callback(code: str, state: str):
    """Handle Google OAuth callback."""
    record = await db.karau_oauth_states.find_one({"state": state})
    if not record:
        raise HTTPException(status_code=400, detail="Invalid state")

    user_id = record["user_id"]
    await db.karau_oauth_states.delete_one({"state": state})

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            logger.error(f"Google token exchange failed: {token_resp.text}")
            raise HTTPException(status_code=400, detail="Failed to connect Google Calendar")

        tokens = token_resp.json()

        profile_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        profile = profile_resp.json() if profile_resp.status_code == 200 else {}

    await db.karau_calendar_connections.update_one(
        {"user_id": user_id, "provider": "google"},
        {"$set": {
            "user_id": user_id,
            "provider": "google",
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token", ""),
            "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=tokens.get("expires_in", 3600))).isoformat(),
            "email": profile.get("email", ""),
            "display_name": profile.get("name", ""),
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )

    return RedirectResponse(url="/karau-meet/settings?calendar=connected")


# ============ SYNC EVENTS ============

@router.post("/sync")
async def sync_meeting_to_calendar(req: CalendarSyncRequest, user=Depends(require_auth)):
    """Push a KARAU meeting to the user's connected calendar."""
    user_id = user["user_id"]
    conn = await db.karau_calendar_connections.find_one(
        {"user_id": user_id, "provider": "microsoft"}
    )
    if not conn:
        raise HTTPException(status_code=400, detail="Microsoft Calendar not connected")

    access_token = conn["access_token"]

    # Refresh token if expired
    expires_at = conn.get("expires_at", "")
    if expires_at:
        exp_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        if exp_dt < datetime.now(timezone.utc):
            access_token = await _refresh_ms_token(user_id, conn.get("refresh_token", ""))
            if not access_token:
                raise HTTPException(status_code=401, detail="Calendar token expired. Please reconnect.")

    join_url = req.join_url or f"https://karau-enzi-nexus.preview.emergentagent.com/karau-meet/join/{req.meeting_id}"

    event_body = {
        "subject": req.title,
        "body": {"contentType": "HTML", "content": f"<p>{req.description}</p><p>Join: <a href='{join_url}'>{join_url}</a></p>"},
        "start": {"dateTime": req.start_time, "timeZone": "UTC"},
        "end": {"dateTime": req.end_time, "timeZone": "UTC"},
        "isOnlineMeeting": True,
        "onlineMeetingUrl": join_url,
        "isReminderOn": True,
        "reminderMinutesBeforeStart": 15,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{MS_GRAPH_URL}/me/events",
            json=event_body,
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        )

    if resp.status_code in (200, 201):
        event = resp.json()
        # Store mapping
        await db.karau_calendar_events.update_one(
            {"meeting_id": req.meeting_id, "user_id": user_id},
            {"$set": {
                "meeting_id": req.meeting_id,
                "user_id": user_id,
                "provider": "microsoft",
                "external_event_id": event.get("id", ""),
                "synced_at": datetime.now(timezone.utc).isoformat(),
            }},
            upsert=True,
        )
        await db.karau_calendar_connections.update_one(
            {"user_id": user_id, "provider": "microsoft"},
            {"$set": {"last_sync": datetime.now(timezone.utc).isoformat()}},
        )
        return {"success": True, "event_id": event.get("id", ""), "message": "Meeting synced to Outlook calendar"}
    else:
        logger.error(f"MS Graph create event failed: {resp.status_code} {resp.text}")
        raise HTTPException(status_code=502, detail="Failed to create calendar event")


@router.delete("/sync/{meeting_id}")
async def remove_from_calendar(meeting_id: str, user=Depends(require_auth)):
    """Remove a synced meeting from the user's calendar."""
    user_id = user["user_id"]
    mapping = await db.karau_calendar_events.find_one(
        {"meeting_id": meeting_id, "user_id": user_id}
    )
    if not mapping:
        raise HTTPException(status_code=404, detail="Meeting not synced to calendar")

    conn = await db.karau_calendar_connections.find_one(
        {"user_id": user_id, "provider": mapping["provider"]}
    )
    if conn:
        async with httpx.AsyncClient() as client:
            await client.delete(
                f"{MS_GRAPH_URL}/me/events/{mapping['external_event_id']}",
                headers={"Authorization": f"Bearer {conn['access_token']}"},
            )

    await db.karau_calendar_events.delete_one({"meeting_id": meeting_id, "user_id": user_id})
    return {"success": True, "message": "Meeting removed from calendar"}


# ============ DISCONNECT ============

@router.post("/disconnect")
async def disconnect_calendar(req: CalendarDisconnectRequest, user=Depends(require_auth)):
    """Disconnect a calendar provider."""
    user_id = user["user_id"]
    await db.karau_calendar_connections.delete_one({"user_id": user_id, "provider": req.provider})
    await db.karau_calendar_events.delete_many({"user_id": user_id, "provider": req.provider})
    return {"success": True, "message": f"{req.provider.title()} calendar disconnected"}


# ============ HELPERS ============

async def _refresh_ms_token(user_id: str, refresh_token: str) -> str:
    """Refresh expired Microsoft access token."""
    if not refresh_token:
        return ""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{MS_AUTHORITY}/oauth2/v2.0/token",
            data={
                "client_id": MS_CLIENT_ID,
                "client_secret": MS_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
                "scope": MS_SCOPES,
            },
        )
        if resp.status_code == 200:
            tokens = resp.json()
            await db.karau_calendar_connections.update_one(
                {"user_id": user_id, "provider": "microsoft"},
                {"$set": {
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens.get("refresh_token", refresh_token),
                    "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=tokens.get("expires_in", 3600))).isoformat(),
                }},
            )
            return tokens["access_token"]
    return ""
