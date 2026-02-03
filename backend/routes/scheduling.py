"""
Interview Scheduling Routes
Handles: Schedule interviews, calendar integration, reminders
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/interviews", tags=["Interview Scheduling"])

# ============== Models ==============

class InterviewSlot(BaseModel):
    date: str  # ISO date string
    start_time: str  # "09:00"
    end_time: str  # "10:00"
    timezone: str = "UTC"

class ScheduleInterviewRequest(BaseModel):
    applicant_id: str
    job_id: str
    interview_type: str  # "phone", "video", "in_person"
    slot: InterviewSlot
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    notify_candidate: bool = True

class RescheduleRequest(BaseModel):
    new_slot: InterviewSlot
    reason: Optional[str] = None
    notify_candidate: bool = True

class AvailabilitySlot(BaseModel):
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: str  # "09:00"
    end_time: str  # "17:00"

class SetAvailabilityRequest(BaseModel):
    slots: List[AvailabilitySlot]
    timezone: str = "UTC"
    buffer_minutes: int = 15  # Buffer between interviews

class CandidateResponseRequest(BaseModel):
    response: str  # "accept", "decline", "reschedule"
    message: Optional[str] = None
    preferred_times: Optional[List[InterviewSlot]] = None

# ============== Recruiter Routes ==============

@router.post("/schedule")
async def schedule_interview(schedule_request: ScheduleInterviewRequest, request: Request):
    """Recruiter schedules an interview with a candidate"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can schedule interviews")
    
    # Verify applicant exists
    applicant = await db.job_applicants.find_one({"id": schedule_request.applicant_id})
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    # Get job details
    job = await db.posted_jobs.find_one({"id": schedule_request.job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Parse datetime
    try:
        datetime.fromisoformat(
            f"{schedule_request.slot.date}T{schedule_request.slot.start_time}:00"
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date/time format")
    
    # Create interview record
    interview = {
        "id": f"int_{uuid.uuid4().hex[:12]}",
        "recruiter_id": user["user_id"],
        "applicant_id": schedule_request.applicant_id,
        "applicant_email": applicant.get("applicant_email"),
        "applicant_name": applicant.get("applicant_name"),
        "job_id": schedule_request.job_id,
        "job_title": job.get("title"),
        "company": job.get("company"),
        "interview_type": schedule_request.interview_type,
        "scheduled_date": schedule_request.slot.date,
        "start_time": schedule_request.slot.start_time,
        "end_time": schedule_request.slot.end_time,
        "timezone": schedule_request.slot.timezone,
        "meeting_link": schedule_request.meeting_link,
        "location": schedule_request.location,
        "notes": schedule_request.notes,
        "status": "pending",  # pending, confirmed, declined, completed, cancelled, rescheduled
        "created_at": datetime.now(timezone.utc).isoformat(),
        "candidate_response": None,
        "reminders_sent": []
    }
    
    await db.interviews.insert_one(interview)
    
    # Update applicant status
    await db.job_applicants.update_one(
        {"id": schedule_request.applicant_id},
        {"$set": {
            "status": "interviewing",
            "interview_scheduled": interview["id"]
        }}
    )
    
    # Create notification for candidate
    notification = {
        "id": f"notif_{uuid.uuid4().hex[:8]}",
        "user_id": applicant.get("applicant_id"),
        "type": "interview_scheduled",
        "title": f"Interview Scheduled: {job.get('title')}",
        "message": f"You have an interview scheduled for {schedule_request.slot.date} at {schedule_request.slot.start_time}",
        "data": {
            "interview_id": interview["id"],
            "job_title": job.get("title"),
            "company": job.get("company"),
            "date": schedule_request.slot.date,
            "time": schedule_request.slot.start_time
        },
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification)
    
    # Generate calendar event (ICS format)
    ics_content = generate_ics_event(interview, job, user)
    
    return {
        "message": "Interview scheduled successfully",
        "interview_id": interview["id"],
        "interview": interview,
        "ics_content": ics_content
    }

@router.get("/recruiter/upcoming")
async def get_recruiter_interviews(request: Request, status: Optional[str] = None):
    """Get all upcoming interviews for recruiter"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can view interviews")
    
    query = {"recruiter_id": user["user_id"]}
    if status:
        query["status"] = status
    else:
        # Default to upcoming (not cancelled/completed)
        query["status"] = {"$in": ["pending", "confirmed"]}
    
    interviews = await db.interviews.find(
        query,
        {"_id": 0}
    ).sort("scheduled_date", 1).to_list(100)
    
    return {"interviews": interviews, "total": len(interviews)}

@router.put("/{interview_id}/reschedule")
async def reschedule_interview(interview_id: str, reschedule: RescheduleRequest, request: Request):
    """Reschedule an existing interview"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    interview = await db.interviews.find_one({"id": interview_id})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Check authorization
    is_recruiter = user.get("role") == "recruiter" and interview.get("recruiter_id") == user["user_id"]
    is_candidate = interview.get("applicant_id") == user.get("user_id")
    
    if not is_recruiter and not is_candidate:
        raise HTTPException(status_code=403, detail="Not authorized to modify this interview")
    
    # Update interview
    await db.interviews.update_one(
        {"id": interview_id},
        {"$set": {
            "scheduled_date": reschedule.new_slot.date,
            "start_time": reschedule.new_slot.start_time,
            "end_time": reschedule.new_slot.end_time,
            "timezone": reschedule.new_slot.timezone,
            "status": "pending",
            "reschedule_reason": reschedule.reason,
            "rescheduled_by": user["user_id"],
            "rescheduled_at": datetime.now(timezone.utc).isoformat()
        },
        "$push": {
            "history": {
                "action": "rescheduled",
                "by": user["user_id"],
                "at": datetime.now(timezone.utc).isoformat(),
                "reason": reschedule.reason
            }
        }}
    )
    
    return {"message": "Interview rescheduled", "interview_id": interview_id}

@router.put("/{interview_id}/cancel")
async def cancel_interview(interview_id: str, request: Request, reason: Optional[str] = None):
    """Cancel an interview"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    interview = await db.interviews.find_one({"id": interview_id})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Check authorization
    is_recruiter = user.get("role") == "recruiter" and interview.get("recruiter_id") == user["user_id"]
    if not is_recruiter:
        raise HTTPException(status_code=403, detail="Only recruiters can cancel interviews")
    
    await db.interviews.update_one(
        {"id": interview_id},
        {"$set": {
            "status": "cancelled",
            "cancelled_by": user["user_id"],
            "cancelled_at": datetime.now(timezone.utc).isoformat(),
            "cancel_reason": reason
        }}
    )
    
    return {"message": "Interview cancelled"}

# ============== Candidate Routes ==============

@router.get("/candidate/upcoming")
async def get_candidate_interviews(request: Request):
    """Get all upcoming interviews for the candidate"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Find applicant records for this user
    applicant_emails = [user.get("email")]
    
    interviews = await db.interviews.find(
        {
            "applicant_email": {"$in": applicant_emails},
            "status": {"$in": ["pending", "confirmed"]}
        },
        {"_id": 0}
    ).sort("scheduled_date", 1).to_list(50)
    
    return {"interviews": interviews, "total": len(interviews)}

@router.post("/{interview_id}/respond")
async def candidate_respond_to_interview(
    interview_id: str, 
    response: CandidateResponseRequest, 
    request: Request
):
    """Candidate responds to an interview invitation"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    interview = await db.interviews.find_one({"id": interview_id})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Verify this is the candidate
    if interview.get("applicant_email") != user.get("email"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_status = {
        "accept": "confirmed",
        "decline": "declined",
        "reschedule": "reschedule_requested"
    }.get(response.response)
    
    if not new_status:
        raise HTTPException(status_code=400, detail="Invalid response")
    
    update = {
        "status": new_status,
        "candidate_response": {
            "response": response.response,
            "message": response.message,
            "responded_at": datetime.now(timezone.utc).isoformat()
        }
    }
    
    if response.response == "reschedule" and response.preferred_times:
        update["candidate_preferred_times"] = [
            {"date": slot.date, "start_time": slot.start_time, "end_time": slot.end_time}
            for slot in response.preferred_times
        ]
    
    await db.interviews.update_one({"id": interview_id}, {"$set": update})
    
    # Notify recruiter
    notification = {
        "id": f"notif_{uuid.uuid4().hex[:8]}",
        "user_id": interview.get("recruiter_id"),
        "type": f"interview_{response.response}ed",
        "title": f"Interview {response.response.capitalize()}ed",
        "message": f"{interview.get('applicant_name', 'Candidate')} has {response.response}ed the interview",
        "data": {"interview_id": interview_id},
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification)
    
    return {"message": f"Response recorded: {response.response}"}

# ============== Availability Routes ==============

@router.post("/availability/set")
async def set_recruiter_availability(availability: SetAvailabilityRequest, request: Request):
    """Set recruiter's general availability for interviews"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can set availability")
    
    availability_doc = {
        "recruiter_id": user["user_id"],
        "slots": [slot.dict() for slot in availability.slots],
        "timezone": availability.timezone,
        "buffer_minutes": availability.buffer_minutes,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.recruiter_availability.update_one(
        {"recruiter_id": user["user_id"]},
        {"$set": availability_doc},
        upsert=True
    )
    
    return {"message": "Availability updated"}

@router.get("/availability/{recruiter_id}")
async def get_recruiter_availability(recruiter_id: str, date: Optional[str] = None):
    """Get recruiter's available time slots"""
    availability = await db.recruiter_availability.find_one(
        {"recruiter_id": recruiter_id},
        {"_id": 0}
    )
    
    if not availability:
        return {"available_slots": [], "message": "No availability set"}
    
    # If a specific date is requested, calculate available slots
    if date:
        try:
            request_date = datetime.fromisoformat(date)
            day_of_week = request_date.weekday()
            
            # Get slots for this day
            day_slots = [s for s in availability.get("slots", []) if s["day_of_week"] == day_of_week]
            
            # Get existing interviews for this date
            existing = await db.interviews.find({
                "recruiter_id": recruiter_id,
                "scheduled_date": date,
                "status": {"$in": ["pending", "confirmed"]}
            }).to_list(100)
            
            booked_times = [(e["start_time"], e["end_time"]) for e in existing]
            
            # Calculate available slots (simplified - would need proper time slot generation)
            available = []
            for slot in day_slots:
                # In a real implementation, generate 30-min slots and filter booked ones
                available.append({
                    "date": date,
                    "start_time": slot["start_time"],
                    "end_time": slot["end_time"],
                    "booked_times": booked_times
                })
            
            return {"available_slots": available, "timezone": availability.get("timezone")}
        except Exception:
            pass
    
    return {"availability": availability}

# ============== Calendar Integration ==============

@router.get("/{interview_id}/calendar")
async def get_calendar_event(interview_id: str, format: str = "ics"):
    """Get calendar event for an interview"""
    interview = await db.interviews.find_one({"id": interview_id}, {"_id": 0})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    job = await db.posted_jobs.find_one({"id": interview.get("job_id")}, {"_id": 0})
    recruiter = await db.users.find_one({"user_id": interview.get("recruiter_id")}, {"_id": 0})
    
    if format == "ics":
        ics_content = generate_ics_event(interview, job, recruiter)
        return {"ics_content": ics_content, "filename": f"interview_{interview_id}.ics"}
    
    elif format == "google":
        # Generate Google Calendar URL
        title = f"Interview: {interview.get('job_title')} at {interview.get('company')}"
        start = f"{interview['scheduled_date'].replace('-', '')}T{interview['start_time'].replace(':', '')}00"
        end = f"{interview['scheduled_date'].replace('-', '')}T{interview['end_time'].replace(':', '')}00"
        
        google_url = (
            f"https://calendar.google.com/calendar/render?action=TEMPLATE"
            f"&text={title}"
            f"&dates={start}/{end}"
            f"&details=Interview with {interview.get('company')}"
            f"&location={interview.get('location') or interview.get('meeting_link') or ''}"
        )
        
        return {"google_calendar_url": google_url}
    
    return interview

# ============== Notifications Routes ==============

notifications_router = APIRouter(prefix="/notifications", tags=["Notifications"])

@notifications_router.get("/")
async def get_notifications(request: Request, unread_only: bool = False):
    """Get user's notifications"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    query = {"user_id": user["user_id"]}
    if unread_only:
        query["read"] = False
    
    notifications = await db.notifications.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    unread_count = await db.notifications.count_documents({
        "user_id": user["user_id"],
        "read": False
    })
    
    return {"notifications": notifications, "unread_count": unread_count}

@notifications_router.put("/{notification_id}/read")
async def mark_notification_read(notification_id: str, request: Request):
    """Mark a notification as read"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    await db.notifications.update_one(
        {"id": notification_id, "user_id": user["user_id"]},
        {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Notification marked as read"}

@notifications_router.put("/read-all")
async def mark_all_notifications_read(request: Request):
    """Mark all notifications as read"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    await db.notifications.update_many(
        {"user_id": user["user_id"], "read": False},
        {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "All notifications marked as read"}

# ============== Helper Functions ==============

def generate_ics_event(interview: dict, job: dict, organizer: dict) -> str:
    """Generate ICS calendar event content"""
    uid = interview.get("id", uuid.uuid4().hex)
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    # Parse datetime
    date_str = interview.get("scheduled_date", "").replace("-", "")
    start_time = interview.get("start_time", "09:00").replace(":", "") + "00"
    end_time = interview.get("end_time", "10:00").replace(":", "") + "00"
    
    dtstart = f"{date_str}T{start_time}"
    dtend = f"{date_str}T{end_time}"
    
    title = f"Interview: {job.get('title', 'Job')} at {job.get('company', 'Company')}"
    location = interview.get("location") or interview.get("meeting_link") or ""
    
    # Build description
    desc_parts = [
        f"Interview for {job.get('title', 'Position')} at {job.get('company', 'Company')}",
        "",
        f"Type: {interview.get('interview_type', 'Video').title()}"
    ]
    if interview.get('meeting_link'):
        desc_parts.append(f"Meeting Link: {interview.get('meeting_link')}")
    if interview.get('location'):
        desc_parts.append(f"Location: {interview.get('location')}")
    desc_parts.append("")
    desc_parts.append(f"Notes: {interview.get('notes', '')}")
    
    newline = "\n"
    description = newline.join(desc_parts).replace(newline, "\\n")
    
    organizer_name = organizer.get('name', 'Recruiter')
    organizer_email = organizer.get('email', '')
    
    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//MedMatch//Interview Scheduler//EN
BEGIN:VEVENT
UID:{uid}@medmatch.com
DTSTAMP:{now}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{title}
DESCRIPTION:{description}
LOCATION:{location}
ORGANIZER;CN={organizer_name}:mailto:{organizer_email}
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR"""
    
    return ics
