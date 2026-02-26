"""
KARAU Calendar & Social Sharing
Handles: .ics file generation, social media share links
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response as FastAPIResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import urllib.parse

from utils.database import db
from routes.auth import get_current_user
from services.karau_meet import get_meeting

router = APIRouter(prefix="/karau-meet/share", tags=["KARAU Calendar & Sharing"])


# ============ CALENDAR .ICS EXPORT ============

@router.get("/calendar/{meeting_id}.ics")
async def export_ics(meeting_id: str):
    """Generate .ics calendar file for a meeting (works with Outlook, Google Calendar, iOS)."""
    meeting = await get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    title = meeting.get("title", "AI KARAU Meeting")
    host_name = meeting.get("host_name", "Host")
    created = meeting.get("created_at", datetime.now(timezone.utc).isoformat())
    join_url = f"https://aikarau.com/karau-meet/join/{meeting_id}"
    description = f"Join AI KARAU Meeting\\nHost: {host_name}\\nMeeting ID: {meeting_id}\\n\\nJoin: {join_url}"

    # Parse start time or default to now + 5 min
    try:
        start_dt = datetime.fromisoformat(meeting.get("scheduled_at", created).replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        start_dt = datetime.now(timezone.utc) + timedelta(minutes=5)

    end_dt = start_dt + timedelta(hours=1)
    now_dt = datetime.now(timezone.utc)

    def fmt(dt):
        return dt.strftime("%Y%m%dT%H%M%SZ")

    # Location
    location = meeting.get("location", "Virtual (AI KARAU)")
    if meeting.get("conference_room"):
        room = meeting["conference_room"]
        location = f"{room.get('name', '')} - {room.get('building', '')} Floor {room.get('floor', '')}"

    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AI KARAU//Meeting//EN
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
DTSTART:{fmt(start_dt)}
DTEND:{fmt(end_dt)}
DTSTAMP:{fmt(now_dt)}
UID:{meeting_id}@aikarau.com
SUMMARY:{title}
DESCRIPTION:{description}
LOCATION:{location}
ORGANIZER;CN={host_name}:mailto:meeting@aikarau.com
URL:{join_url}
STATUS:CONFIRMED
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-PT15M
ACTION:DISPLAY
DESCRIPTION:Meeting in 15 minutes
END:VALARM
END:VEVENT
END:VCALENDAR"""

    return FastAPIResponse(
        content=ics.strip(),
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="karau-meeting-{meeting_id}.ics"'
        }
    )


# ============ SOCIAL SHARING LINKS ============

@router.get("/social/{meeting_id}")
async def get_share_links(meeting_id: str):
    """Generate social media share links for a meeting."""
    meeting = await get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    title = meeting.get("title", "AI KARAU Meeting")
    host_name = meeting.get("host_name", "Host")
    join_url = f"https://aikarau.com/karau-meet/join/{meeting_id}"
    share_text = f"Join my AI KARAU meeting: {title}"
    encoded_url = urllib.parse.quote(join_url)
    encoded_text = urllib.parse.quote(share_text)
    encoded_title = urllib.parse.quote(title)

    return {
        "meeting_id": meeting_id,
        "title": title,
        "join_url": join_url,
        "share_links": {
            "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
            "twitter": f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}",
            "facebook": f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
            "email": f"mailto:?subject={encoded_title}&body={urllib.parse.quote(f'Join my AI KARAU meeting: {title}\\n\\nJoin here: {join_url}\\n\\nHost: {host_name}')}",
            "whatsapp": f"https://wa.me/?text={urllib.parse.quote(f'{share_text} - {join_url}')}",
        },
        "calendar_ics_url": f"/api/karau-meet/share/calendar/{meeting_id}.ics",
    }
