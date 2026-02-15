"""
AI KARAU Meeting - Scheduling Service
Smart scheduling with calendar sync (Google, Outlook) and RSVP
"""

import os
import uuid
from datetime import datetime, timedelta
from datetime import timezone as tz
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import httpx

logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "medmatch")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collection for scheduled meetings
scheduled_meetings = db.karau_scheduled_meetings
meeting_invites = db.karau_meeting_invites


async def create_scheduled_meeting(
    host_id: str,
    host_name: str,
    host_email: str,
    title: str,
    description: str = "",
    start_time: str = None,
    end_time: str = None,
    duration_minutes: int = 60,
    timezone: str = "UTC",
    recurrence: Optional[Dict] = None,
    invitees: List[Dict] = None,
    settings: Optional[Dict] = None
) -> Dict:
    """Create a scheduled meeting with calendar integration"""
    
    meeting_id = str(uuid.uuid4())[:8].upper()
    
    # Calculate end time if not provided
    if start_time and not end_time:
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        end_time = end_dt.isoformat()
    
    default_settings = {
        "video_enabled": True,
        "audio_enabled": True,
        "waiting_room_enabled": True,
        "recording_enabled": False,
        "ai_notes_enabled": True,
        "allow_guests": False,
        "mute_on_entry": True,
        "require_rsvp": True,
        "send_reminders": True,
        "reminder_times": [24 * 60, 60, 15]  # 24 hours, 1 hour, 15 mins before
    }
    
    if settings:
        default_settings.update(settings)
    
    scheduled_meeting = {
        "meeting_id": meeting_id,
        "title": title,
        "description": description,
        "host_id": host_id,
        "host_name": host_name,
        "host_email": host_email,
        "start_time": start_time,
        "end_time": end_time,
        "duration_minutes": duration_minutes,
        "timezone": timezone,
        "recurrence": recurrence,  # {type: "daily|weekly|monthly", interval: 1, end_date: "..."}
        "settings": default_settings,
        "status": "scheduled",  # scheduled, in_progress, completed, cancelled
        "created_at": datetime.now(tz.utc).isoformat() if hasattr(datetime.now(), 'isoformat') else datetime.utcnow().isoformat(),
        "updated_at": datetime.now(tz.utc).isoformat() if hasattr(datetime.now(), 'isoformat') else datetime.utcnow().isoformat(),
        "join_url": f"/karau-meet/join/{meeting_id}",
        "calendar_event_ids": {},  # {google: "...", outlook: "..."}
        "invitees": [],
        "rsvp_responses": {}
    }
    
    # Store in database
    await scheduled_meetings.insert_one({**scheduled_meeting, "_id": meeting_id})
    
    # Process invitees
    if invitees:
        for invitee in invitees:
            await send_meeting_invite(
                meeting_id=meeting_id,
                meeting_title=title,
                start_time=start_time,
                host_name=host_name,
                invitee_email=invitee.get("email"),
                invitee_name=invitee.get("name", ""),
                join_url=f"/karau-meet/join/{meeting_id}"
            )
    
    logger.info(f"Scheduled meeting created: {meeting_id} by {host_name}")
    
    return {
        "meeting_id": meeting_id,
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "join_url": f"/karau-meet/join/{meeting_id}",
        "settings": default_settings
    }


async def send_meeting_invite(
    meeting_id: str,
    meeting_title: str,
    start_time: str,
    host_name: str,
    invitee_email: str,
    invitee_name: str = "",
    join_url: str = ""
) -> Dict:
    """Send meeting invite and track RSVP"""
    
    invite_id = str(uuid.uuid4())[:12]
    
    invite = {
        "invite_id": invite_id,
        "meeting_id": meeting_id,
        "meeting_title": meeting_title,
        "start_time": start_time,
        "host_name": host_name,
        "invitee_email": invitee_email,
        "invitee_name": invitee_name,
        "join_url": join_url,
        "status": "pending",  # pending, accepted, declined, tentative
        "sent_at": datetime.utcnow().isoformat(),
        "responded_at": None,
        "reminder_sent": False
    }
    
    await meeting_invites.insert_one({**invite, "_id": invite_id})
    
    # Update meeting invitees list
    await scheduled_meetings.update_one(
        {"meeting_id": meeting_id},
        {"$push": {"invitees": {
            "email": invitee_email,
            "name": invitee_name,
            "invite_id": invite_id,
            "status": "pending"
        }}}
    )
    
    # In production, send actual email here
    logger.info(f"Meeting invite sent to {invitee_email} for meeting {meeting_id}")
    
    return invite


async def respond_to_invite(
    invite_id: str,
    response: str,  # accepted, declined, tentative
    responder_email: str
) -> Dict:
    """Record RSVP response"""
    
    invite = await meeting_invites.find_one({"invite_id": invite_id})
    if not invite:
        return {"error": "Invite not found"}
    
    # Update invite
    await meeting_invites.update_one(
        {"invite_id": invite_id},
        {"$set": {
            "status": response,
            "responded_at": datetime.utcnow().isoformat()
        }}
    )
    
    # Update meeting RSVP responses
    await scheduled_meetings.update_one(
        {"meeting_id": invite["meeting_id"]},
        {"$set": {f"rsvp_responses.{responder_email}": {
            "response": response,
            "responded_at": datetime.utcnow().isoformat()
        }}}
    )
    
    # Update invitee status in meeting
    await scheduled_meetings.update_one(
        {"meeting_id": invite["meeting_id"], "invitees.email": responder_email},
        {"$set": {"invitees.$.status": response}}
    )
    
    logger.info(f"RSVP response '{response}' recorded for {responder_email}")
    
    return {
        "success": True,
        "meeting_id": invite["meeting_id"],
        "response": response
    }


async def get_scheduled_meetings(
    user_id: str = None,
    user_email: str = None,
    start_date: str = None,
    end_date: str = None,
    status: str = None
) -> List[Dict]:
    """Get scheduled meetings for a user"""
    
    query = {}
    
    if user_id:
        query["$or"] = [
            {"host_id": user_id},
            {"invitees.email": user_email}
        ]
    
    if status:
        query["status"] = status
    
    if start_date:
        query["start_time"] = {"$gte": start_date}
    
    if end_date:
        if "start_time" in query:
            query["start_time"]["$lte"] = end_date
        else:
            query["start_time"] = {"$lte": end_date}
    
    meetings = await scheduled_meetings.find(
        query,
        {"_id": 0}
    ).sort("start_time", 1).to_list(length=100)
    
    return meetings


async def update_scheduled_meeting(
    meeting_id: str,
    host_id: str,
    updates: Dict
) -> Dict:
    """Update a scheduled meeting"""
    
    meeting = await scheduled_meetings.find_one({"meeting_id": meeting_id})
    if not meeting:
        return {"error": "Meeting not found"}
    
    if meeting["host_id"] != host_id:
        return {"error": "Only the host can update the meeting"}
    
    allowed_updates = [
        "title", "description", "start_time", "end_time", 
        "duration_minutes", "timezone", "settings"
    ]
    
    update_data = {k: v for k, v in updates.items() if k in allowed_updates}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    await scheduled_meetings.update_one(
        {"meeting_id": meeting_id},
        {"$set": update_data}
    )
    
    return {"success": True, "meeting_id": meeting_id}


async def cancel_scheduled_meeting(
    meeting_id: str,
    host_id: str,
    reason: str = ""
) -> Dict:
    """Cancel a scheduled meeting"""
    
    meeting = await scheduled_meetings.find_one({"meeting_id": meeting_id})
    if not meeting:
        return {"error": "Meeting not found"}
    
    if meeting["host_id"] != host_id:
        return {"error": "Only the host can cancel the meeting"}
    
    await scheduled_meetings.update_one(
        {"meeting_id": meeting_id},
        {"$set": {
            "status": "cancelled",
            "cancelled_at": datetime.utcnow().isoformat(),
            "cancellation_reason": reason
        }}
    )
    
    # Notify invitees (in production, send emails)
    logger.info(f"Meeting {meeting_id} cancelled")
    
    return {"success": True, "meeting_id": meeting_id}


def generate_google_calendar_link(
    title: str,
    description: str,
    start_time: str,
    end_time: str,
    join_url: str
) -> str:
    """Generate Google Calendar add event link"""
    
    import urllib.parse
    
    # Format dates for Google Calendar
    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    
    start_str = start_dt.strftime("%Y%m%dT%H%M%SZ")
    end_str = end_dt.strftime("%Y%m%dT%H%M%SZ")
    
    details = f"{description}\n\nJoin AI KARAU Meeting: {join_url}"
    
    params = {
        "action": "TEMPLATE",
        "text": title,
        "dates": f"{start_str}/{end_str}",
        "details": details,
        "sf": "true"
    }
    
    return f"https://calendar.google.com/calendar/render?{urllib.parse.urlencode(params)}"


def generate_outlook_calendar_link(
    title: str,
    description: str,
    start_time: str,
    end_time: str,
    join_url: str
) -> str:
    """Generate Outlook Calendar add event link"""
    
    import urllib.parse
    
    # Format dates for Outlook
    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    
    start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S")
    end_str = end_dt.strftime("%Y-%m-%dT%H:%M:%S")
    
    details = f"{description}\n\nJoin AI KARAU Meeting: {join_url}"
    
    params = {
        "subject": title,
        "startdt": start_str,
        "enddt": end_str,
        "body": details,
        "path": "/calendar/action/compose"
    }
    
    return f"https://outlook.live.com/calendar/0/deeplink/compose?{urllib.parse.urlencode(params)}"


def generate_ics_file(
    meeting_id: str,
    title: str,
    description: str,
    start_time: str,
    end_time: str,
    host_name: str,
    host_email: str,
    join_url: str
) -> str:
    """Generate ICS calendar file content"""
    
    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    
    start_str = start_dt.strftime("%Y%m%dT%H%M%SZ")
    end_str = end_dt.strftime("%Y%m%dT%H%M%SZ")
    now_str = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AI KARAU Meeting//EN
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
UID:{meeting_id}@karau-meet
DTSTAMP:{now_str}
DTSTART:{start_str}
DTEND:{end_str}
SUMMARY:{title}
DESCRIPTION:{description}\\n\\nJoin AI KARAU Meeting: {join_url}
ORGANIZER;CN={host_name}:mailto:{host_email}
URL:{join_url}
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
END:VCALENDAR"""
    
    return ics_content


async def get_upcoming_reminders() -> List[Dict]:
    """Get meetings that need reminder notifications"""
    
    now = datetime.utcnow()
    
    # Check for meetings in next 24 hours
    upcoming = now + timedelta(hours=24)
    
    meetings = await scheduled_meetings.find({
        "status": "scheduled",
        "start_time": {
            "$gte": now.isoformat(),
            "$lte": upcoming.isoformat()
        },
        "settings.send_reminders": True
    }).to_list(length=100)
    
    reminders = []
    for meeting in meetings:
        start_time = datetime.fromisoformat(meeting["start_time"].replace('Z', '+00:00'))
        time_until = (start_time - now).total_seconds() / 60  # minutes
        
        reminder_times = meeting.get("settings", {}).get("reminder_times", [60, 15])
        
        for reminder_mins in reminder_times:
            if abs(time_until - reminder_mins) < 5:  # Within 5 minute window
                reminders.append({
                    "meeting_id": meeting["meeting_id"],
                    "title": meeting["title"],
                    "start_time": meeting["start_time"],
                    "host_name": meeting["host_name"],
                    "invitees": meeting.get("invitees", []),
                    "minutes_until": int(time_until)
                })
                break
    
    return reminders
