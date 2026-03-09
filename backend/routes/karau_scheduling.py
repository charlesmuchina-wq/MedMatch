"""
AI KARAU Meeting - Scheduling API Routes
Smart scheduling with calendar sync and RSVP
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

from services.karau_meet.scheduling_service import (
    create_scheduled_meeting,
    send_meeting_invite,
    respond_to_invite,
    get_scheduled_meetings,
    update_scheduled_meeting,
    cancel_scheduled_meeting,
    generate_google_calendar_link,
    generate_outlook_calendar_link,
    generate_ics_file,
    get_upcoming_reminders
)
from routes.auth import get_current_user, require_auth

router = APIRouter(prefix="/karau-meet/schedule", tags=["AI KARAU Scheduling"])


class ScheduleMeetingRequest(BaseModel):
    title: str
    description: str = ""
    start_time: str  # ISO format
    end_time: Optional[str] = None
    duration_minutes: int = 60
    timezone: str = "UTC"
    recurrence: Optional[Dict] = None
    invitees: Optional[List[Dict]] = None  # [{email: "...", name: "..."}]
    settings: Optional[Dict] = None


class UpdateMeetingRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    settings: Optional[Dict] = None


class InviteRequest(BaseModel):
    invitee_email: str
    invitee_name: str = ""


class RSVPRequest(BaseModel):
    response: str  # accepted, declined, tentative


@router.post("/meetings")
async def schedule_meeting(
    request: ScheduleMeetingRequest,
    user: dict = Depends(require_auth)
):
    """Schedule a new meeting with optional invitees"""
    
    meeting = await create_scheduled_meeting(
        host_id=user["user_id"],
        host_name=user.get("name", user.get("email", "Host")),
        host_email=user.get("email", ""),
        title=request.title,
        description=request.description,
        start_time=request.start_time,
        end_time=request.end_time,
        duration_minutes=request.duration_minutes,
        timezone=request.timezone,
        recurrence=request.recurrence,
        invitees=request.invitees,
        settings=request.settings
    )
    
    # Generate calendar links
    if meeting.get("start_time") and meeting.get("end_time"):
        meeting["calendar_links"] = {
            "google": generate_google_calendar_link(
                title=request.title,
                description=request.description,
                start_time=meeting["start_time"],
                end_time=meeting["end_time"],
                join_url=f"https://ai-karau.preview.emergentagent.com{meeting['join_url']}"
            ),
            "outlook": generate_outlook_calendar_link(
                title=request.title,
                description=request.description,
                start_time=meeting["start_time"],
                end_time=meeting["end_time"],
                join_url=f"https://ai-karau.preview.emergentagent.com{meeting['join_url']}"
            )
        }
    
    return meeting


@router.get("/meetings")
async def list_scheduled_meetings(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    user: dict = Depends(require_auth)
):
    """Get all scheduled meetings for the user"""
    
    meetings = await get_scheduled_meetings(
        user_id=user["user_id"],
        user_email=user.get("email"),
        start_date=start_date,
        end_date=end_date,
        status=status
    )
    
    return {"meetings": meetings}


@router.get("/meetings/{meeting_id}")
async def get_scheduled_meeting(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Get details of a scheduled meeting"""
    
    meetings = await get_scheduled_meetings(user_id=user["user_id"])
    meeting = next((m for m in meetings if m["meeting_id"] == meeting_id), None)
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Add calendar links
    if meeting.get("start_time") and meeting.get("end_time"):
        meeting["calendar_links"] = {
            "google": generate_google_calendar_link(
                title=meeting["title"],
                description=meeting.get("description", ""),
                start_time=meeting["start_time"],
                end_time=meeting["end_time"],
                join_url=f"https://ai-karau.preview.emergentagent.com{meeting['join_url']}"
            ),
            "outlook": generate_outlook_calendar_link(
                title=meeting["title"],
                description=meeting.get("description", ""),
                start_time=meeting["start_time"],
                end_time=meeting["end_time"],
                join_url=f"https://ai-karau.preview.emergentagent.com{meeting['join_url']}"
            )
        }
    
    return meeting


@router.put("/meetings/{meeting_id}")
async def update_meeting(
    meeting_id: str,
    request: UpdateMeetingRequest,
    user: dict = Depends(require_auth)
):
    """Update a scheduled meeting"""
    
    updates = request.dict(exclude_none=True)
    result = await update_scheduled_meeting(
        meeting_id=meeting_id,
        host_id=user["user_id"],
        updates=updates
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.delete("/meetings/{meeting_id}")
async def cancel_meeting(
    meeting_id: str,
    reason: str = "",
    user: dict = Depends(require_auth)
):
    """Cancel a scheduled meeting"""
    
    result = await cancel_scheduled_meeting(
        meeting_id=meeting_id,
        host_id=user["user_id"],
        reason=reason
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/meetings/{meeting_id}/invite")
async def invite_to_meeting(
    meeting_id: str,
    request: InviteRequest,
    user: dict = Depends(require_auth)
):
    """Send meeting invite to a new participant"""
    
    # Get meeting details first
    meetings = await get_scheduled_meetings(user_id=user["user_id"])
    meeting = next((m for m in meetings if m["meeting_id"] == meeting_id), None)
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meeting["host_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Only the host can send invites")
    
    invite = await send_meeting_invite(
        meeting_id=meeting_id,
        meeting_title=meeting["title"],
        start_time=meeting["start_time"],
        host_name=meeting["host_name"],
        invitee_email=request.invitee_email,
        invitee_name=request.invitee_name,
        join_url=meeting["join_url"]
    )
    
    return invite


@router.post("/invites/{invite_id}/rsvp")
async def rsvp_to_invite(
    invite_id: str,
    request: RSVPRequest,
    user: dict = Depends(require_auth)
):
    """Respond to a meeting invite"""
    
    if request.response not in ["accepted", "declined", "tentative"]:
        raise HTTPException(status_code=400, detail="Invalid response. Use: accepted, declined, or tentative")
    
    result = await respond_to_invite(
        invite_id=invite_id,
        response=request.response,
        responder_email=user.get("email", "")
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/meetings/{meeting_id}/ics")
async def download_ics(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Download ICS calendar file for a meeting"""
    
    meetings = await get_scheduled_meetings(user_id=user["user_id"])
    meeting = next((m for m in meetings if m["meeting_id"] == meeting_id), None)
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    ics_content = generate_ics_file(
        meeting_id=meeting_id,
        title=meeting["title"],
        description=meeting.get("description", ""),
        start_time=meeting["start_time"],
        end_time=meeting["end_time"],
        host_name=meeting["host_name"],
        host_email=meeting.get("host_email", ""),
        join_url=f"https://ai-karau.preview.emergentagent.com{meeting['join_url']}"
    )
    
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="karau-meeting-{meeting_id}.ics"'
        }
    )


@router.get("/reminders")
async def get_reminders(
    user: dict = Depends(require_auth)
):
    """Get upcoming meeting reminders"""
    
    reminders = await get_upcoming_reminders()
    
    # Filter for user's meetings
    user_reminders = [
        r for r in reminders 
        if r.get("host_id") == user["user_id"] or 
        any(i.get("email") == user.get("email") for i in r.get("invitees", []))
    ]
    
    return {"reminders": user_reminders}
