"""
Interview Calendar Routes
Features: Google Calendar sync, AI preparation reminders, calendar view
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid
import logging
import os
import json
import httpx

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user
from utils.push_service import notify_interview_reminder

# Try to import LLM for AI preparation
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
except ImportError:
    LlmChat = None
    UserMessage = None

router = APIRouter(prefix="/interview-calendar", tags=["Interview Calendar"])
logger = logging.getLogger(__name__)

# Google Calendar API
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_CALENDAR_SCOPES = "https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/calendar.events"

# ============== Models ==============

class CalendarEvent(BaseModel):
    title: str
    company: str
    position: str
    interview_type: str  # phone, video, in_person
    start_time: str  # ISO datetime
    end_time: str  # ISO datetime
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    interviewer_name: Optional[str] = None
    interviewer_email: Optional[str] = None

class CalendarSyncRequest(BaseModel):
    access_token: str
    calendar_id: str = "primary"
    sync_direction: str = "import"  # import, export, both

class ReminderSettings(BaseModel):
    reminder_hours: List[int] = [24, 1]  # Hours before interview
    include_ai_prep: bool = True
    send_push: bool = True
    send_email: bool = False

class AIPreparationRequest(BaseModel):
    interview_id: str
    company: Optional[str] = None
    position: Optional[str] = None
    job_description: Optional[str] = None

# ============== AI Preparation Generator ==============

async def generate_interview_preparation(
    company: str,
    position: str,
    interview_type: str,
    job_description: str = "",
    user_skills: List[str] = []
) -> Dict[str, Any]:
    """Generate AI-powered interview preparation materials"""
    if not EMERGENT_LLM_KEY or LlmChat is None:
        return {
            "talking_points": ["Research the company beforehand", "Prepare questions to ask", "Review your resume"],
            "company_insights": "Company research unavailable - please research manually",
            "potential_questions": ["Tell me about yourself", "Why do you want to work here?", "What are your strengths?"],
            "tips": ["Arrive early", "Dress appropriately", "Bring copies of your resume"]
        }
    
    try:
        import uuid as uuid_module
        
        skills_text = ", ".join(user_skills) if user_skills else "general professional skills"
        
        system_message = """You are an expert career coach specializing in interview preparation. 
Provide actionable, specific advice. Always respond with valid JSON only."""

        prompt = f"""Generate comprehensive interview preparation materials for the following:

Company: {company}
Position: {position}
Interview Type: {interview_type}
Job Description: {job_description or "Not provided"}
Candidate Skills: {skills_text}

Provide a structured response in JSON format:
{{
    "talking_points": ["5-7 key talking points the candidate should emphasize"],
    "company_insights": "Brief insights about the company, culture, and what they look for",
    "potential_questions": ["10 likely interview questions based on the role"],
    "suggested_answers": {{"question": "answer framework"}} (for top 3 questions),
    "questions_to_ask": ["5 thoughtful questions to ask the interviewer"],
    "tips": ["5 specific tips for this type of interview"],
    "dress_code": "Recommended attire",
    "preparation_checklist": ["Items to prepare before the interview"]
}}

Return ONLY valid JSON."""

        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid_module.uuid4()),
            system_message=system_message
        ).with_model("openai", "gpt-4o-mini")
        
        response = await chat.send_message(prompt)
        
        # Parse JSON response
        try:
            response_text = response.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            return {
                "talking_points": [response[:500]],
                "company_insights": "See talking points",
                "potential_questions": [],
                "tips": []
            }
            
    except Exception as e:
        logger.error(f"AI preparation generation error: {e}")
        return {
            "talking_points": ["Prepare your elevator pitch", "Research the company", "Review common interview questions"],
            "company_insights": f"Error generating insights: {str(e)}",
            "potential_questions": [],
            "tips": ["Be confident", "Ask thoughtful questions", "Follow up after the interview"]
        }

# ============== Google Calendar Helpers ==============

async def fetch_google_calendar_events(
    access_token: str,
    calendar_id: str = "primary",
    time_min: str = None,
    time_max: str = None
) -> List[Dict]:
    """Fetch events from Google Calendar"""
    if not time_min:
        time_min = datetime.now(timezone.utc).isoformat()
    if not time_max:
        time_max = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    
    url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
    params = {
        "timeMin": time_min,
        "timeMax": time_max,
        "singleEvents": "true",
        "orderBy": "startTime",
        "q": "interview"  # Search for interview-related events
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Google Calendar API error: {response.text}")
            return []
        
        data = response.json()
        return data.get("items", [])


async def create_google_calendar_event(
    access_token: str,
    event: CalendarEvent,
    calendar_id: str = "primary"
) -> Optional[Dict]:
    """Create event in Google Calendar"""
    url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    event_body = {
        "summary": f"Interview: {event.position} at {event.company}",
        "description": f"""Interview Type: {event.interview_type}
Position: {event.position}
Company: {event.company}
{f"Meeting Link: {event.meeting_link}" if event.meeting_link else ""}
{f"Notes: {event.notes}" if event.notes else ""}

Powered by MedMatch""",
        "start": {
            "dateTime": event.start_time,
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": event.end_time,
            "timeZone": "UTC"
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 60},
                {"method": "popup", "minutes": 1440}  # 24 hours
            ]
        }
    }
    
    if event.location:
        event_body["location"] = event.location
    elif event.meeting_link:
        event_body["location"] = event.meeting_link
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=event_body, headers=headers)
        
        if response.status_code in [200, 201]:
            return response.json()
        
        logger.error(f"Failed to create Google Calendar event: {response.text}")
        return None

# ============== Routes ==============

@router.get("/status")
async def get_calendar_status(request: Request):
    """Get calendar service status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "available": True,
        "google_calendar_configured": bool(GOOGLE_CLIENT_ID),
        "ai_preparation_available": bool(EMERGENT_LLM_KEY and LlmChat),
        "features": {
            "calendar_sync": bool(GOOGLE_CLIENT_ID),
            "ai_preparation": bool(EMERGENT_LLM_KEY),
            "push_reminders": True,
            "export_to_calendar": bool(GOOGLE_CLIENT_ID)
        }
    }


@router.get("/events")
async def get_interview_events(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None
):
    """Get user's interview events"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    query = {"user_id": user["user_id"]}
    
    if start_date:
        query["start_time"] = {"$gte": start_date}
    if end_date:
        if "start_time" in query:
            query["start_time"]["$lte"] = end_date
        else:
            query["start_time"] = {"$lte": end_date}
    if status:
        query["status"] = status
    
    events = await db.interview_calendar.find(
        query,
        {"_id": 0}
    ).sort("start_time", 1).to_list(100)
    
    return {
        "events": events,
        "total": len(events)
    }


@router.post("/events")
async def create_interview_event(event: CalendarEvent, request: Request):
    """Create a new interview event"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    event_doc = {
        "id": f"interview_{uuid.uuid4().hex[:12]}",
        "user_id": user["user_id"],
        "title": event.title,
        "company": event.company,
        "position": event.position,
        "interview_type": event.interview_type,
        "start_time": event.start_time,
        "end_time": event.end_time,
        "location": event.location,
        "meeting_link": event.meeting_link,
        "notes": event.notes,
        "interviewer_name": event.interviewer_name,
        "interviewer_email": event.interviewer_email,
        "status": "scheduled",
        "preparation": None,
        "google_event_id": None,
        "reminders_sent": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.interview_calendar.insert_one(event_doc)
    event_doc.pop("_id", None)
    
    return {"message": "Interview scheduled", "event": event_doc}


@router.get("/events/{event_id}")
async def get_interview_event(event_id: str, request: Request):
    """Get specific interview event"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    event = await db.interview_calendar.find_one(
        {"id": event_id, "user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event


@router.put("/events/{event_id}")
async def update_interview_event(event_id: str, request: Request):
    """Update an interview event"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    body = await request.json()
    body["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Remove fields that shouldn't be updated
    body.pop("id", None)
    body.pop("user_id", None)
    body.pop("created_at", None)
    body.pop("_id", None)
    
    result = await db.interview_calendar.update_one(
        {"id": event_id, "user_id": user["user_id"]},
        {"$set": body}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"message": "Event updated"}


@router.delete("/events/{event_id}")
async def delete_interview_event(event_id: str, request: Request):
    """Delete an interview event"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.interview_calendar.delete_one(
        {"id": event_id, "user_id": user["user_id"]}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"message": "Event deleted"}


@router.post("/events/{event_id}/generate-preparation")
async def generate_event_preparation(event_id: str, request: Request):
    """Generate AI preparation materials for an interview"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    event = await db.interview_calendar.find_one(
        {"id": event_id, "user_id": user["user_id"]}
    )
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Get user's resume skills
    resume = await db.resumes.find_one(
        {"user_id": user["user_id"]},
        {"skills": 1, "_id": 0}
    )
    skills = resume.get("skills", []) if resume else []
    
    # Generate preparation
    preparation = await generate_interview_preparation(
        company=event.get("company", ""),
        position=event.get("position", ""),
        interview_type=event.get("interview_type", "video"),
        job_description=event.get("notes", ""),
        user_skills=skills
    )
    
    # Save preparation to event
    await db.interview_calendar.update_one(
        {"id": event_id},
        {"$set": {
            "preparation": preparation,
            "preparation_generated_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "success": True,
        "preparation": preparation
    }


@router.post("/sync/google")
async def sync_google_calendar(sync_request: CalendarSyncRequest, request: Request):
    """Sync with Google Calendar"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if sync_request.sync_direction in ["import", "both"]:
        # Fetch events from Google Calendar
        google_events = await fetch_google_calendar_events(
            access_token=sync_request.access_token,
            calendar_id=sync_request.calendar_id
        )
        
        imported_count = 0
        for g_event in google_events:
            # Check if event already exists
            existing = await db.interview_calendar.find_one({
                "google_event_id": g_event.get("id"),
                "user_id": user["user_id"]
            })
            
            if not existing:
                # Parse event
                start = g_event.get("start", {})
                end = g_event.get("end", {})
                
                event_doc = {
                    "id": f"interview_{uuid.uuid4().hex[:12]}",
                    "user_id": user["user_id"],
                    "title": g_event.get("summary", "Interview"),
                    "company": "",  # Will need to be filled by user
                    "position": "",
                    "interview_type": "video" if "meet.google" in g_event.get("location", "") else "in_person",
                    "start_time": start.get("dateTime", start.get("date")),
                    "end_time": end.get("dateTime", end.get("date")),
                    "location": g_event.get("location", ""),
                    "meeting_link": g_event.get("hangoutLink", ""),
                    "notes": g_event.get("description", ""),
                    "status": "scheduled",
                    "google_event_id": g_event.get("id"),
                    "source": "google_calendar",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                
                await db.interview_calendar.insert_one(event_doc)
                imported_count += 1
        
        return {
            "success": True,
            "imported": imported_count,
            "total_found": len(google_events)
        }
    
    return {"success": True, "message": "Sync completed"}


@router.post("/events/{event_id}/export-to-google")
async def export_to_google_calendar(event_id: str, request: Request):
    """Export interview to Google Calendar"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    body = await request.json()
    access_token = body.get("access_token")
    
    if not access_token:
        raise HTTPException(status_code=400, detail="Google access token required")
    
    event = await db.interview_calendar.find_one(
        {"id": event_id, "user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Create CalendarEvent from DB event
    calendar_event = CalendarEvent(
        title=event.get("title", "Interview"),
        company=event.get("company", ""),
        position=event.get("position", ""),
        interview_type=event.get("interview_type", "video"),
        start_time=event.get("start_time"),
        end_time=event.get("end_time"),
        location=event.get("location"),
        meeting_link=event.get("meeting_link"),
        notes=event.get("notes")
    )
    
    result = await create_google_calendar_event(access_token, calendar_event)
    
    if result:
        # Update event with Google Calendar ID
        await db.interview_calendar.update_one(
            {"id": event_id},
            {"$set": {
                "google_event_id": result.get("id"),
                "google_calendar_link": result.get("htmlLink"),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "success": True,
            "google_event_id": result.get("id"),
            "calendar_link": result.get("htmlLink")
        }
    
    raise HTTPException(status_code=500, detail="Failed to create Google Calendar event")


@router.get("/upcoming")
async def get_upcoming_interviews(request: Request, days: int = 7):
    """Get upcoming interviews for the next N days"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    now = datetime.now(timezone.utc)
    end_date = now + timedelta(days=days)
    
    events = await db.interview_calendar.find(
        {
            "user_id": user["user_id"],
            "start_time": {
                "$gte": now.isoformat(),
                "$lte": end_date.isoformat()
            },
            "status": {"$ne": "cancelled"}
        },
        {"_id": 0}
    ).sort("start_time", 1).to_list(50)
    
    # Add time until interview for each event
    for event in events:
        start = datetime.fromisoformat(event["start_time"].replace("Z", "+00:00"))
        delta = start - now
        event["time_until"] = {
            "days": delta.days,
            "hours": delta.seconds // 3600,
            "total_hours": delta.total_seconds() / 3600
        }
    
    return {
        "events": events,
        "total": len(events)
    }


@router.post("/send-reminders")
async def send_interview_reminders(request: Request, background_tasks: BackgroundTasks):
    """Send reminders for upcoming interviews (called by scheduler)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    now = datetime.now(timezone.utc)
    
    # Find interviews in the next 24 hours that haven't been reminded
    reminder_windows = [
        (24, "24h"),  # 24 hours before
        (1, "1h")     # 1 hour before
    ]
    
    reminders_sent = []
    
    for hours, window_name in reminder_windows:
        window_start = now + timedelta(hours=hours - 0.5)
        window_end = now + timedelta(hours=hours + 0.5)
        
        events = await db.interview_calendar.find({
            "user_id": user["user_id"],
            "start_time": {
                "$gte": window_start.isoformat(),
                "$lte": window_end.isoformat()
            },
            "status": "scheduled",
            f"reminders_sent.{window_name}": {"$ne": True}
        }).to_list(50)
        
        for event in events:
            # Send push notification
            background_tasks.add_task(
                notify_interview_reminder,
                user_id=user["user_id"],
                company=event.get("company", ""),
                position=event.get("position", ""),
                interview_time=event.get("start_time", ""),
                interview_id=event.get("id")
            )
            
            # Mark reminder as sent
            await db.interview_calendar.update_one(
                {"id": event["id"]},
                {"$set": {f"reminders_sent.{window_name}": True}}
            )
            
            reminders_sent.append({
                "event_id": event["id"],
                "window": window_name
            })
    
    return {
        "success": True,
        "reminders_sent": len(reminders_sent),
        "details": reminders_sent
    }


@router.get("/settings")
async def get_calendar_settings(request: Request):
    """Get user's calendar settings"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    settings = await db.user_settings.find_one(
        {"user_id": user["user_id"], "type": "calendar"},
        {"_id": 0}
    )
    
    if not settings:
        # Default settings
        settings = {
            "reminder_hours": [24, 1],
            "include_ai_prep": True,
            "send_push": True,
            "send_email": False,
            "default_interview_duration": 60,
            "auto_generate_prep": True
        }
    
    return settings


@router.put("/settings")
async def update_calendar_settings(settings: ReminderSettings, request: Request):
    """Update user's calendar settings"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    await db.user_settings.update_one(
        {"user_id": user["user_id"], "type": "calendar"},
        {"$set": {
            "user_id": user["user_id"],
            "type": "calendar",
            "reminder_hours": settings.reminder_hours,
            "include_ai_prep": settings.include_ai_prep,
            "send_push": settings.send_push,
            "send_email": settings.send_email,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    
    return {"message": "Settings updated"}


@router.get("/stats")
async def get_calendar_stats(request: Request):
    """Get interview calendar statistics"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    now = datetime.now(timezone.utc)
    
    # Total interviews
    total = await db.interview_calendar.count_documents({"user_id": user["user_id"]})
    
    # Upcoming interviews
    upcoming = await db.interview_calendar.count_documents({
        "user_id": user["user_id"],
        "start_time": {"$gte": now.isoformat()},
        "status": "scheduled"
    })
    
    # Completed interviews
    completed = await db.interview_calendar.count_documents({
        "user_id": user["user_id"],
        "status": "completed"
    })
    
    # This week
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=7)
    this_week = await db.interview_calendar.count_documents({
        "user_id": user["user_id"],
        "start_time": {
            "$gte": week_start.isoformat(),
            "$lte": week_end.isoformat()
        }
    })
    
    # By type
    pipeline = [
        {"$match": {"user_id": user["user_id"]}},
        {"$group": {"_id": "$interview_type", "count": {"$sum": 1}}}
    ]
    type_counts = {}
    async for doc in db.interview_calendar.aggregate(pipeline):
        type_counts[doc["_id"] or "unknown"] = doc["count"]
    
    return {
        "total_interviews": total,
        "upcoming": upcoming,
        "completed": completed,
        "this_week": this_week,
        "by_type": type_counts
    }
