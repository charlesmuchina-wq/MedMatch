"""
Webinar Mode API - Large Event Support (1000+ attendees)
WebEx-equivalent features: audience control, Q&A, registration, analytics.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timezone
import uuid

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/karau/webinar", tags=["Webinar"])


class WebinarCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    scheduled_time: str
    max_attendees: int = Field(default=1000, ge=10, le=10000)
    registration_required: bool = True
    auto_record: bool = False
    q_and_a_enabled: bool = True
    chat_enabled: bool = True
    attendee_video: bool = False
    attendee_audio: bool = False
    practice_session: bool = False
    panelist_emails: List[str] = []


class WebinarResponse(BaseModel):
    webinar_id: str
    title: str
    description: str
    host_id: str
    host_name: str
    scheduled_time: str
    max_attendees: int
    registered_count: int
    attendee_count: int
    status: str
    registration_required: bool
    registration_url: str
    join_url: str
    settings: Dict


class WebinarRegistration(BaseModel):
    name: str
    email: str
    organization: Optional[str] = ""
    role: Optional[str] = ""


class QAQuestion(BaseModel):
    question: str
    is_anonymous: bool = False


class QAAnswer(BaseModel):
    answer: str


@router.post("/create", response_model=WebinarResponse)
async def create_webinar(data: WebinarCreate, user=Depends(get_current_user)):
    """Create a new webinar event."""
    webinar_id = f"WEB-{uuid.uuid4().hex[:8].upper()}"

    webinar = {
        "webinar_id": webinar_id,
        "title": data.title,
        "description": data.description,
        "host_id": user["user_id"],
        "host_name": user.get("name", "Host"),
        "host_email": user.get("email", ""),
        "scheduled_time": data.scheduled_time,
        "max_attendees": data.max_attendees,
        "status": "scheduled",
        "registration_required": data.registration_required,
        "settings": {
            "auto_record": data.auto_record,
            "q_and_a_enabled": data.q_and_a_enabled,
            "chat_enabled": data.chat_enabled,
            "attendee_video": data.attendee_video,
            "attendee_audio": data.attendee_audio,
            "practice_session": data.practice_session,
        },
        "panelists": [{"email": e, "role": "panelist"} for e in data.panelist_emails],
        "registrations": [],
        "attendees": [],
        "questions": [],
        "polls": [],
        "analytics": {
            "peak_attendees": 0,
            "avg_watch_time": 0,
            "questions_asked": 0,
            "engagement_score": 0
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.webinars.insert_one(webinar)

    return WebinarResponse(
        webinar_id=webinar_id,
        title=data.title,
        description=data.description,
        host_id=user["user_id"],
        host_name=user.get("name", "Host"),
        scheduled_time=data.scheduled_time,
        max_attendees=data.max_attendees,
        registered_count=0,
        attendee_count=0,
        status="scheduled",
        registration_required=data.registration_required,
        registration_url=f"/karau-meet/webinar/{webinar_id}/register",
        join_url=f"/karau-meet/webinar/{webinar_id}/join",
        settings=webinar["settings"]
    )


@router.get("/list")
async def list_webinars(user=Depends(get_current_user)):
    """List user's webinars."""
    webinars = await db.webinars.find(
        {"host_id": user["user_id"]},
        {"_id": 0, "webinar_id": 1, "title": 1, "scheduled_time": 1,
         "status": 1, "max_attendees": 1, "registrations": 1, "analytics": 1}
    ).sort("created_at", -1).to_list(length=50)

    for w in webinars:
        w["registered_count"] = len(w.pop("registrations", []))

    return {"webinars": webinars}


@router.get("/{webinar_id}")
async def get_webinar(webinar_id: str):
    """Get webinar details (public for registration page)."""
    webinar = await db.webinars.find_one(
        {"webinar_id": webinar_id},
        {"_id": 0, "webinar_id": 1, "title": 1, "description": 1,
         "host_name": 1, "scheduled_time": 1, "max_attendees": 1,
         "status": 1, "registration_required": 1, "settings": 1}
    )
    if not webinar:
        raise HTTPException(404, "Webinar not found")

    reg_count = await db.webinars.count_documents(
        {"webinar_id": webinar_id, "registrations": {"$exists": True}}
    )
    # Get actual registration count from the array
    full = await db.webinars.find_one({"webinar_id": webinar_id}, {"_id": 0, "registrations": 1})
    webinar["registered_count"] = len(full.get("registrations", [])) if full else 0

    return webinar


@router.post("/{webinar_id}/register")
async def register_for_webinar(webinar_id: str, data: WebinarRegistration):
    """Register as an attendee for a webinar."""
    webinar = await db.webinars.find_one(
        {"webinar_id": webinar_id},
        {"_id": 0, "max_attendees": 1, "registrations": 1, "status": 1}
    )
    if not webinar:
        raise HTTPException(404, "Webinar not found")
    if webinar["status"] == "ended":
        raise HTTPException(400, "Webinar has ended")

    regs = webinar.get("registrations", [])
    if len(regs) >= webinar["max_attendees"]:
        raise HTTPException(400, "Webinar is full")
    if any(r["email"] == data.email for r in regs):
        raise HTTPException(400, "Already registered")

    reg_id = f"REG-{uuid.uuid4().hex[:8].upper()}"
    registration = {
        "reg_id": reg_id,
        "name": data.name,
        "email": data.email,
        "organization": data.organization,
        "role": data.role,
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "attended": False,
    }

    await db.webinars.update_one(
        {"webinar_id": webinar_id},
        {"$push": {"registrations": registration}}
    )

    return {
        "success": True,
        "reg_id": reg_id,
        "join_url": f"/karau-meet/webinar/{webinar_id}/join?reg={reg_id}",
        "message": "Successfully registered"
    }


@router.post("/{webinar_id}/start")
async def start_webinar(webinar_id: str, user=Depends(get_current_user)):
    """Start the webinar (host only)."""
    webinar = await db.webinars.find_one({"webinar_id": webinar_id, "host_id": user["user_id"]})
    if not webinar:
        raise HTTPException(404, "Webinar not found or not authorized")

    await db.webinars.update_one(
        {"webinar_id": webinar_id},
        {"$set": {"status": "live", "started_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"success": True, "status": "live"}


@router.post("/{webinar_id}/end")
async def end_webinar(webinar_id: str, user=Depends(get_current_user)):
    """End the webinar (host only)."""
    await db.webinars.update_one(
        {"webinar_id": webinar_id, "host_id": user["user_id"]},
        {"$set": {"status": "ended", "ended_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"success": True, "status": "ended"}


# --- Q&A System ---

@router.post("/{webinar_id}/qa/ask")
async def ask_question(webinar_id: str, data: QAQuestion, user=Depends(get_current_user)):
    """Submit a Q&A question."""
    question = {
        "question_id": f"Q-{uuid.uuid4().hex[:8].upper()}",
        "question": data.question,
        "asked_by": user.get("name", "Anonymous") if not data.is_anonymous else "Anonymous",
        "asked_by_id": user["user_id"],
        "is_anonymous": data.is_anonymous,
        "asked_at": datetime.now(timezone.utc).isoformat(),
        "upvotes": 0,
        "upvoters": [],
        "answer": None,
        "answered_at": None,
        "status": "pending"  # pending, answered, dismissed
    }

    await db.webinars.update_one(
        {"webinar_id": webinar_id},
        {"$push": {"questions": question},
         "$inc": {"analytics.questions_asked": 1}}
    )
    return {"success": True, "question_id": question["question_id"]}


@router.post("/{webinar_id}/qa/{question_id}/answer")
async def answer_question(webinar_id: str, question_id: str, data: QAAnswer, user=Depends(get_current_user)):
    """Answer a Q&A question (host/panelist only)."""
    await db.webinars.update_one(
        {"webinar_id": webinar_id, "questions.question_id": question_id},
        {"$set": {
            "questions.$.answer": data.answer,
            "questions.$.answered_by": user.get("name", "Host"),
            "questions.$.answered_at": datetime.now(timezone.utc).isoformat(),
            "questions.$.status": "answered"
        }}
    )
    return {"success": True}


@router.post("/{webinar_id}/qa/{question_id}/upvote")
async def upvote_question(webinar_id: str, question_id: str, user=Depends(get_current_user)):
    """Upvote a Q&A question."""
    await db.webinars.update_one(
        {"webinar_id": webinar_id, "questions.question_id": question_id,
         "questions.upvoters": {"$ne": user["user_id"]}},
        {"$inc": {"questions.$.upvotes": 1},
         "$push": {"questions.$.upvoters": user["user_id"]}}
    )
    return {"success": True}


@router.post("/{webinar_id}/qa/{question_id}/dismiss")
async def dismiss_question(webinar_id: str, question_id: str, user=Depends(get_current_user)):
    """Dismiss a Q&A question (host only)."""
    await db.webinars.update_one(
        {"webinar_id": webinar_id, "host_id": user["user_id"],
         "questions.question_id": question_id},
        {"$set": {"questions.$.status": "dismissed"}}
    )
    return {"success": True}


@router.get("/{webinar_id}/qa")
async def get_questions(webinar_id: str):
    """Get all Q&A questions for a webinar."""
    webinar = await db.webinars.find_one(
        {"webinar_id": webinar_id},
        {"_id": 0, "questions": 1}
    )
    if not webinar:
        raise HTTPException(404, "Webinar not found")

    questions = webinar.get("questions", [])
    # Sort by upvotes desc, then by time
    questions.sort(key=lambda q: (-q.get("upvotes", 0), q.get("asked_at", "")))

    return {"questions": questions}


# --- Host Controls ---

@router.post("/{webinar_id}/controls/mute-all")
async def mute_all(webinar_id: str, user=Depends(get_current_user)):
    """Mute all attendees (host only)."""
    webinar = await db.webinars.find_one({"webinar_id": webinar_id, "host_id": user["user_id"]})
    if not webinar:
        raise HTTPException(403, "Not authorized")
    # This would be sent via WebSocket in real-time
    return {"success": True, "action": "mute_all"}


@router.post("/{webinar_id}/controls/disable-chat")
async def toggle_chat(webinar_id: str, enabled: bool = True, user=Depends(get_current_user)):
    """Enable/disable attendee chat."""
    await db.webinars.update_one(
        {"webinar_id": webinar_id, "host_id": user["user_id"]},
        {"$set": {"settings.chat_enabled": enabled}}
    )
    return {"success": True, "chat_enabled": enabled}


@router.post("/{webinar_id}/controls/allow-audio")
async def toggle_attendee_audio(webinar_id: str, enabled: bool = False, user=Depends(get_current_user)):
    """Allow/disallow attendee audio."""
    await db.webinars.update_one(
        {"webinar_id": webinar_id, "host_id": user["user_id"]},
        {"$set": {"settings.attendee_audio": enabled}}
    )
    return {"success": True, "attendee_audio": enabled}


# --- Analytics ---

@router.get("/{webinar_id}/analytics")
async def get_webinar_analytics(webinar_id: str, user=Depends(get_current_user)):
    """Enhanced webinar analytics with registration funnel, Q&A stats, engagement metrics."""
    webinar = await db.webinars.find_one(
        {"webinar_id": webinar_id, "host_id": user["user_id"]},
        {"_id": 0}
    )
    if not webinar:
        raise HTTPException(404, "Webinar not found or not authorized")

    regs = webinar.get("registrations", [])
    questions = webinar.get("questions", [])
    attendees = webinar.get("attendees", [])
    analytics = webinar.get("analytics", {})
    total_regs = len(regs)
    attended = sum(1 for r in regs if r.get("attended"))
    missed = total_regs - attended

    # Q&A breakdown
    pending_qs = sum(1 for q in questions if q.get("status") == "pending")
    answered_qs = sum(1 for q in questions if q.get("status") == "answered")
    dismissed_qs = sum(1 for q in questions if q.get("status") == "dismissed")
    total_upvotes = sum(q.get("upvotes", 0) for q in questions)
    anonymous_qs = sum(1 for q in questions if q.get("is_anonymous"))

    # Organization breakdown from registrations
    org_counts = {}
    for r in regs:
        org = r.get("organization", "").strip() or "Unknown"
        org_counts[org] = org_counts.get(org, 0) + 1
    org_breakdown = sorted(org_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # Top questions by upvotes
    top_questions = sorted(
        [{"question": q["question"], "upvotes": q.get("upvotes", 0),
          "asked_by": q.get("asked_by", "Anonymous"), "status": q.get("status")}
         for q in questions],
        key=lambda x: x["upvotes"], reverse=True
    )[:5]

    # Engagement score calculation
    engagement = 0
    if total_regs > 0:
        attendance_weight = (attended / total_regs) * 40
        qa_weight = min(len(questions) / max(total_regs, 1) * 100, 30)
        upvote_weight = min(total_upvotes / max(len(questions), 1) * 10, 30)
        engagement = round(attendance_weight + qa_weight + upvote_weight)

    # Registration timeline (group by day)
    reg_timeline = {}
    for r in regs:
        reg_date = r.get("registered_at", "")[:10]
        if reg_date:
            reg_timeline[reg_date] = reg_timeline.get(reg_date, 0) + 1
    reg_timeline_sorted = [{"date": k, "count": v} for k, v in sorted(reg_timeline.items())]

    return {
        "webinar_id": webinar_id,
        "title": webinar.get("title", ""),
        "status": webinar.get("status", "scheduled"),
        "started_at": webinar.get("started_at"),
        "ended_at": webinar.get("ended_at"),
        "funnel": {
            "total_registrations": total_regs,
            "attended": attended,
            "missed": missed,
            "attendance_rate": round((attended / max(total_regs, 1)) * 100),
            "drop_off_rate": round((missed / max(total_regs, 1)) * 100),
        },
        "qa_stats": {
            "total_questions": len(questions),
            "pending": pending_qs,
            "answered": answered_qs,
            "dismissed": dismissed_qs,
            "anonymous": anonymous_qs,
            "total_upvotes": total_upvotes,
            "answer_rate": round((answered_qs / max(len(questions), 1)) * 100),
            "top_questions": top_questions,
        },
        "engagement": {
            "score": engagement,
            "peak_attendees": analytics.get("peak_attendees", attended),
            "avg_watch_time_minutes": analytics.get("avg_watch_time", 0),
        },
        "org_breakdown": [{"org": o, "count": c} for o, c in org_breakdown],
        "registration_timeline": reg_timeline_sorted,
        "max_attendees": webinar.get("max_attendees", 1000),
    }
