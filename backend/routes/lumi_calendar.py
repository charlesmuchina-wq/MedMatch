"""
LUMI Calendar Status Sync - Sync user status from Microsoft Calendar via Graph API
Also provides user behavior tracking for predictive navigation
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone, timedelta
import os
import httpx

from motor.motor_asyncio import AsyncIOMotorClient
from routes.auth import get_current_user

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "MedMatch")
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

router = APIRouter(prefix="/lumi/ms-calendar", tags=["LUMI Calendar Sync"])

GRAPH_API = "https://graph.microsoft.com/v1.0"


async def get_ms_token(user_id: str):
    """Get stored Microsoft access token for a user"""
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "ms_access_token": 1})
    return user.get("ms_access_token") if user else None


@router.get("/status")
async def get_calendar_status(request: Request):
    """Get current calendar-derived status for the authenticated user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Check if user has Microsoft token
    ms_token = await get_ms_token(user["user_id"])
    if not ms_token:
        return {"status": "available", "source": "default", "event": None}

    try:
        now = datetime.now(timezone.utc)
        time_min = now.isoformat()
        time_max = (now + timedelta(minutes=30)).isoformat()

        async with httpx.AsyncClient() as client_http:
            res = await client_http.get(
                f"{GRAPH_API}/me/calendarView",
                params={"startDateTime": time_min, "endDateTime": time_max, "$top": 5, "$select": "subject,start,end,showAs,isAllDay"},
                headers={"Authorization": f"Bearer {ms_token}", "Prefer": 'outlook.timezone="UTC"'},
                timeout=10,
            )

        if res.status_code == 200:
            events = res.json().get("value", [])
            current_event = None
            status = "available"

            for event in events:
                show_as = event.get("showAs", "free")
                if show_as == "busy" or show_as == "tentative":
                    status = "in_meeting"
                    current_event = {
                        "subject": event.get("subject", "Meeting"),
                        "start": event.get("start", {}).get("dateTime", ""),
                        "end": event.get("end", {}).get("dateTime", ""),
                        "show_as": show_as,
                    }
                    break
                elif show_as == "oof":
                    status = "ooo"
                    current_event = {"subject": "Out of Office"}
                    break

            # Update presence in DB
            await db.lumi_presence.update_one(
                {"user_id": user["user_id"]},
                {"$set": {
                    "status": status,
                    "calendar_status": status,
                    "calendar_event": current_event,
                    "calendar_synced_at": now.isoformat(),
                    "last_seen": now.isoformat(),
                }},
                upsert=True,
            )

            return {"status": status, "source": "microsoft_calendar", "event": current_event}
        elif res.status_code == 401:
            return {"status": "available", "source": "token_expired", "event": None}
        else:
            return {"status": "available", "source": "error", "event": None}

    except Exception as e:
        return {"status": "available", "source": "error", "event": None, "error": str(e)}


@router.get("/events")
async def get_upcoming_events(request: Request):
    """Get upcoming calendar events for the user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    ms_token = await get_ms_token(user["user_id"])
    if not ms_token:
        return {"events": [], "source": "no_microsoft_account"}

    try:
        now = datetime.now(timezone.utc)
        time_max = (now + timedelta(hours=24)).isoformat()

        async with httpx.AsyncClient() as client_http:
            res = await client_http.get(
                f"{GRAPH_API}/me/calendarView",
                params={"startDateTime": now.isoformat(), "endDateTime": time_max, "$top": 10,
                         "$select": "subject,start,end,showAs,location,organizer,isAllDay",
                         "$orderby": "start/dateTime"},
                headers={"Authorization": f"Bearer {ms_token}", "Prefer": 'outlook.timezone="UTC"'},
                timeout=10,
            )

        if res.status_code == 200:
            events = []
            for e in res.json().get("value", []):
                events.append({
                    "subject": e.get("subject", ""),
                    "start": e.get("start", {}).get("dateTime", ""),
                    "end": e.get("end", {}).get("dateTime", ""),
                    "show_as": e.get("showAs", "free"),
                    "location": e.get("location", {}).get("displayName", ""),
                    "organizer": e.get("organizer", {}).get("emailAddress", {}).get("name", ""),
                    "is_all_day": e.get("isAllDay", False),
                })
            return {"events": events, "source": "microsoft_calendar"}
        else:
            return {"events": [], "source": "error"}

    except Exception:
        return {"events": [], "source": "error"}


@router.post("/sync")
async def sync_all_calendar_statuses(request: Request):
    """Sync calendar statuses for all Microsoft-connected users (admin or self)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Sync just the current user's status
    ms_token = await get_ms_token(user["user_id"])
    if not ms_token:
        return {"synced": 0, "message": "No Microsoft account linked"}

    try:
        now = datetime.now(timezone.utc)
        time_max = (now + timedelta(minutes=30)).isoformat()

        async with httpx.AsyncClient() as client_http:
            res = await client_http.get(
                f"{GRAPH_API}/me/calendarView",
                params={"startDateTime": now.isoformat(), "endDateTime": time_max, "$top": 3,
                         "$select": "subject,showAs"},
                headers={"Authorization": f"Bearer {ms_token}", "Prefer": 'outlook.timezone="UTC"'},
                timeout=10,
            )

        status = "available"
        if res.status_code == 200:
            for event in res.json().get("value", []):
                show_as = event.get("showAs", "free")
                if show_as in ("busy", "tentative"):
                    status = "in_meeting"
                    break
                elif show_as == "oof":
                    status = "ooo"
                    break

        await db.lumi_presence.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"status": status, "calendar_synced_at": now.isoformat(), "last_seen": now.isoformat()}},
            upsert=True,
        )
        return {"synced": 1, "status": status}

    except Exception as e:
        return {"synced": 0, "error": str(e)}
