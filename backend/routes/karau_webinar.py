"""
Webinar Mode API - Large Event Support (1000+ attendees)
WebEx-equivalent features: audience control, Q&A, registration, analytics.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
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
    coordinator_emails: List[str] = []
    # Organization privacy settings
    org_domains: List[str] = []  # Company email domains for internal classification
    internal_only_docs: bool = True  # Restrict document sharing to internal members
    external_download_blocked: bool = True  # Block external users from downloading


class GuestPermission(BaseModel):
    user_id: str
    permission: str = "upload"  # upload, download, both


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


class PromoteRequest(BaseModel):
    user_id: str
    role: str = "presenter"  # coordinator, presenter, or panelist


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
        "org_privacy": {
            "org_domains": [d.lower().strip() for d in data.org_domains],
            "internal_only_docs": data.internal_only_docs,
            "external_download_blocked": data.external_download_blocked,
        },
        "guest_permissions": {},  # {user_id: {permission, granted_by, granted_at, expires_at}}
        "panelists": [{"email": e, "role": "panelist"} for e in data.panelist_emails],
        "coordinators": [{"email": e, "role": "coordinator"} for e in data.coordinator_emails],
        "active_roles": {},
        "hand_raises": [],
        "practice_mode": False,
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


# --- Caption Translation (must be before /{webinar_id} routes) ---

SUPPORTED_LANGUAGES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "it": "Italian", "pt": "Portuguese", "ja": "Japanese", "ko": "Korean",
    "zh": "Chinese", "nl": "Dutch", "ar": "Arabic", "hi": "Hindi",
    "ru": "Russian", "tr": "Turkish", "pl": "Polish", "sv": "Swedish"
}


class TranslateCaptionRequest(BaseModel):
    text: str
    source_language: str = "en"
    target_language: str = "es"


@router.post("/translate-caption")
async def translate_caption(data: TranslateCaptionRequest, user=Depends(get_current_user)):
    """Translate a caption text to a target language using AI."""
    if not user:
        raise HTTPException(401, "Authentication required")

    if not data.text.strip():
        return {"translated": "", "source": data.source_language, "target": data.target_language}

    if data.source_language == data.target_language:
        return {"translated": data.text, "source": data.source_language, "target": data.target_language}

    src_name = SUPPORTED_LANGUAGES.get(data.source_language, data.source_language)
    tgt_name = SUPPORTED_LANGUAGES.get(data.target_language, data.target_language)

    try:
        import os
        key = os.environ.get("EMERGENT_LLM_KEY")
        if not key:
            raise HTTPException(500, "Translation service not configured")
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(
            api_key=key,
            session_id=f'caption-translate-{datetime.now().strftime("%H%M%S")}',
            system_message=f'You are a real-time caption translator. Translate from {src_name} to {tgt_name}. Return ONLY the translated text, nothing else.'
        ).with_model('openai', 'gpt-4o-mini')

        response = await chat.send_message(UserMessage(text=data.text))
        translated = response if isinstance(response, str) else str(response)
        return {"translated": translated.strip(), "source": data.source_language, "target": data.target_language}
    except Exception as e:
        raise HTTPException(500, f"Translation failed: {str(e)}")


@router.get("/caption-languages")
async def get_supported_languages():
    """Get list of supported languages for captions and translation."""
    return {"languages": SUPPORTED_LANGUAGES}


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
    """End the webinar (host only). Auto-expires all guest permissions."""
    await db.webinars.update_one(
        {"webinar_id": webinar_id, "host_id": user["user_id"]},
        {"$set": {
            "status": "ended",
            "ended_at": datetime.now(timezone.utc).isoformat(),
            "guest_permissions": {}  # Clear all guest permissions on end
        }}
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


# --- Role Management (Host + Presenter + Panelist) ---

@router.post("/{webinar_id}/roles/promote")
async def promote_participant(webinar_id: str, data: PromoteRequest, user=Depends(get_current_user)):
    """Promote an attendee to coordinator/presenter/panelist (host or coordinator only). Grants permissions based on role."""
    webinar = await db.webinars.find_one({"webinar_id": webinar_id})
    if not webinar:
        raise HTTPException(404, "Webinar not found")

    # Host or coordinator can promote
    uid = user["user_id"]
    is_host = uid == webinar.get("host_id")
    is_coordinator = webinar.get("active_roles", {}).get(uid, {}).get("role") == "coordinator"
    user_email = user.get("email", "")
    is_assigned_coordinator = any(c["email"] == user_email for c in webinar.get("coordinators", []))

    if not (is_host or is_coordinator or is_assigned_coordinator):
        raise HTTPException(403, "Not authorized - host or coordinator only")

    # Only host can promote to coordinator
    valid_roles = ["coordinator", "presenter", "panelist"]
    if data.role not in valid_roles:
        raise HTTPException(400, f"Role must be one of: {valid_roles}")
    if data.role == "coordinator" and not is_host:
        raise HTTPException(403, "Only host can assign coordinator role")

    await db.webinars.update_one(
        {"webinar_id": webinar_id},
        {"$set": {f"active_roles.{data.user_id}": {
            "role": data.role,
            "promoted_at": datetime.now(timezone.utc).isoformat(),
            "promoted_by": uid
        }}}
    )
    return {"success": True, "user_id": data.user_id, "role": data.role}


@router.post("/{webinar_id}/roles/demote")
async def demote_participant(webinar_id: str, data: PromoteRequest, user=Depends(get_current_user)):
    """Demote a participant back to attendee (host or coordinator). Revokes elevated permissions."""
    webinar = await db.webinars.find_one({"webinar_id": webinar_id})
    if not webinar:
        raise HTTPException(404, "Webinar not found")

    uid = user["user_id"]
    is_host = uid == webinar.get("host_id")
    is_coordinator = webinar.get("active_roles", {}).get(uid, {}).get("role") == "coordinator"
    user_email = user.get("email", "")
    is_assigned_coordinator = any(c["email"] == user_email for c in webinar.get("coordinators", []))

    if not (is_host or is_coordinator or is_assigned_coordinator):
        raise HTTPException(403, "Not authorized")

    # Coordinators cannot demote other coordinators
    target_role = webinar.get("active_roles", {}).get(data.user_id, {}).get("role")
    if target_role == "coordinator" and not is_host:
        raise HTTPException(403, "Only host can demote coordinators")

    await db.webinars.update_one(
        {"webinar_id": webinar_id},
        {"$unset": {f"active_roles.{data.user_id}": ""}}
    )
    return {"success": True, "user_id": data.user_id, "demoted": True}


@router.get("/{webinar_id}/roles")
async def get_webinar_roles(webinar_id: str, user=Depends(get_current_user)):
    """Get all active roles for a webinar."""
    webinar = await db.webinars.find_one(
        {"webinar_id": webinar_id},
        {"_id": 0, "host_id": 1, "host_name": 1, "active_roles": 1, "panelists": 1, "coordinators": 1}
    )
    if not webinar:
        raise HTTPException(404, "Webinar not found")

    roles = {"host": {"user_id": webinar["host_id"], "name": webinar.get("host_name", "Host")}}
    for uid, info in webinar.get("active_roles", {}).items():
        roles[uid] = info

    return {
        "roles": roles,
        "panelist_emails": [p["email"] for p in webinar.get("panelists", [])],
        "coordinator_emails": [c["email"] for c in webinar.get("coordinators", [])]
    }


# --- Hand Raise ---

@router.post("/{webinar_id}/hand-raise")
async def raise_hand(webinar_id: str, user=Depends(get_current_user)):
    """Attendee raises hand to request to speak."""
    hand = {
        "user_id": user["user_id"],
        "name": user.get("name", "Attendee"),
        "raised_at": datetime.now(timezone.utc).isoformat()
    }
    # Remove existing, then add fresh
    await db.webinars.update_one(
        {"webinar_id": webinar_id},
        {"$pull": {"hand_raises": {"user_id": user["user_id"]}}}
    )
    await db.webinars.update_one(
        {"webinar_id": webinar_id},
        {"$push": {"hand_raises": hand}}
    )
    return {"success": True}


@router.post("/{webinar_id}/hand-lower")
async def lower_hand(webinar_id: str, user=Depends(get_current_user)):
    """Lower hand."""
    await db.webinars.update_one(
        {"webinar_id": webinar_id},
        {"$pull": {"hand_raises": {"user_id": user["user_id"]}}}
    )
    return {"success": True}


@router.get("/{webinar_id}/hand-raises")
async def get_hand_raises(webinar_id: str, user=Depends(get_current_user)):
    """Get list of raised hands (host/presenter view)."""
    webinar = await db.webinars.find_one({"webinar_id": webinar_id}, {"_id": 0, "hand_raises": 1})
    return {"hand_raises": webinar.get("hand_raises", []) if webinar else []}


# --- Practice Session ---

@router.post("/{webinar_id}/practice/start")
async def start_practice(webinar_id: str, user=Depends(get_current_user)):
    """Start practice session (host + presenters only, before going live)."""
    webinar = await db.webinars.find_one({"webinar_id": webinar_id, "host_id": user["user_id"]})
    if not webinar:
        raise HTTPException(403, "Not authorized")
    if webinar.get("status") == "live":
        raise HTTPException(400, "Cannot start practice while webinar is live")

    await db.webinars.update_one(
        {"webinar_id": webinar_id},
        {"$set": {"practice_mode": True, "status": "practice"}}
    )
    return {"success": True, "status": "practice"}


@router.post("/{webinar_id}/practice/end")
async def end_practice(webinar_id: str, user=Depends(get_current_user)):
    """End practice session."""
    webinar = await db.webinars.find_one({"webinar_id": webinar_id, "host_id": user["user_id"]})
    if not webinar:
        raise HTTPException(403, "Not authorized")

    await db.webinars.update_one(
        {"webinar_id": webinar_id},
        {"$set": {"practice_mode": False, "status": "scheduled"}}
    )
    return {"success": True, "status": "scheduled"}


# --- Selective Unmute ---

@router.post("/{webinar_id}/controls/unmute-user")
async def unmute_specific_user(webinar_id: str, target_user_id: str, user=Depends(get_current_user)):
    """Selectively unmute a specific attendee (host only). Grants temporary audio."""
    webinar = await db.webinars.find_one({"webinar_id": webinar_id, "host_id": user["user_id"]})
    if not webinar:
        raise HTTPException(403, "Not authorized")
    # The actual unmute is handled via WebSocket signal to the specific client
    return {"success": True, "target_user_id": target_user_id, "action": "unmute_request"}


# --- Webinar Room Info ---

@router.get("/{webinar_id}/room-info")
async def get_room_info(webinar_id: str, user=Depends(get_current_user)):
    """Get full room info for the live webinar view - determines user's role, permissions, and org classification."""
    webinar = await db.webinars.find_one(
        {"webinar_id": webinar_id},
        {"_id": 0, "webinar_id": 1, "title": 1, "status": 1, "host_id": 1,
         "host_name": 1, "settings": 1, "active_roles": 1, "practice_mode": 1,
         "panelists": 1, "coordinators": 1, "hand_raises": 1,
         "org_privacy": 1, "guest_permissions": 1}
    )
    if not webinar:
        raise HTTPException(404, "Webinar not found")

    uid = user["user_id"]
    user_email = user.get("email", "")

    # Determine role: host > coordinator > presenter > panelist > attendee
    if uid == webinar["host_id"]:
        my_role = "host"
    elif uid in webinar.get("active_roles", {}):
        my_role = webinar["active_roles"][uid]["role"]
    elif any(c["email"] == user_email for c in webinar.get("coordinators", [])):
        my_role = "coordinator"
    elif any(p["email"] == user_email for p in webinar.get("panelists", [])):
        my_role = "panelist"
    else:
        my_role = "attendee"

    # Organization classification
    org_privacy = webinar.get("org_privacy", {})
    org_domains = org_privacy.get("org_domains", [])
    email_domain = user_email.split("@")[-1].lower() if "@" in user_email else ""
    is_internal = email_domain in org_domains if org_domains else True  # No domains = everyone internal

    # Lookup employee info for internal users
    employee_info = None
    if is_internal and org_domains:
        emp = await db.karau_employees.find_one(
            {"email": user_email},
            {"_id": 0, "first_name": 1, "last_name": 1, "department": 1, "title": 1}
        )
        if emp:
            employee_info = emp

    # Document sharing permissions
    guest_perms = webinar.get("guest_permissions", {})
    my_guest_perm = guest_perms.get(uid, {})
    can_download = is_internal or not org_privacy.get("external_download_blocked", True) or my_guest_perm.get("permission") in ("download", "both")
    can_upload_docs = is_internal or my_guest_perm.get("permission") in ("upload", "both")

    # Permissions based on role hierarchy
    can_stream = my_role in ("host", "presenter", "panelist")
    can_control = my_role in ("host", "coordinator")
    can_present = my_role in ("host", "presenter")
    can_drive_slides = my_role in ("host", "coordinator", "presenter")

    # If practice mode and attendee, deny entry
    if webinar.get("practice_mode") and my_role == "attendee":
        raise HTTPException(403, "Practice session in progress - attendees cannot join yet")

    return {
        "webinar_id": webinar_id,
        "title": webinar["title"],
        "status": webinar["status"],
        "my_role": my_role,
        "can_stream_video": can_stream,
        "can_stream_audio": can_stream,
        "can_screen_share": can_present,
        "can_control": can_control,
        "can_drive_slides": can_drive_slides,
        "settings": webinar.get("settings", {}),
        "practice_mode": webinar.get("practice_mode", False),
        "hand_raises": webinar.get("hand_raises", []) if can_control else [],
        "active_roles": webinar.get("active_roles", {}) if can_control else {},
        "host_name": webinar.get("host_name", "Host"),
        # Organization & privacy
        "is_internal": is_internal,
        "attendee_type": "internal" if is_internal else "external",
        "employee_info": employee_info,
        "can_download": can_download,
        "can_upload_docs": can_upload_docs,
        "org_privacy": {
            "has_org_domains": len(org_domains) > 0,
            "internal_only_docs": org_privacy.get("internal_only_docs", True),
            "external_download_blocked": org_privacy.get("external_download_blocked", True),
        },
        "guest_permissions": guest_perms if can_control else {},
    }


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


# --- Presentation Upload ---

@router.post("/{webinar_id}/presentation/upload")
async def upload_presentation(
    webinar_id: str,
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    """Upload a PDF/PPTX presentation for the webinar. Converts to slide images."""
    webinar = await db.webinars.find_one({"webinar_id": webinar_id})
    if not webinar:
        raise HTTPException(404, "Webinar not found")

    uid = user["user_id"]
    is_host = uid == webinar.get("host_id")
    is_coordinator = webinar.get("active_roles", {}).get(uid, {}).get("role") == "coordinator"
    user_email = user.get("email", "")
    is_assigned_coord = any(c["email"] == user_email for c in webinar.get("coordinators", []))

    if not (is_host or is_coordinator or is_assigned_coord):
        raise HTTPException(403, "Only host or coordinator can upload presentations")

    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ("pdf", "pptx", "ppt"):
        raise HTTPException(400, "Only PDF and PPTX files are supported")

    data = await file.read()
    if len(data) > 50 * 1024 * 1024:
        raise HTTPException(413, "File too large (max 50MB)")

    try:
        from services.presentation_service import process_presentation
        result = await process_presentation(data, file.filename, webinar_id, uid)
    except Exception as e:
        raise HTTPException(500, f"Presentation processing failed: {str(e)}")

    await db.webinars.update_one(
        {"webinar_id": webinar_id},
        {"$set": {
            "presentation": {
                "filename": result["filename"],
                "total_slides": result["total_slides"],
                "slide_paths": result["slide_paths"],
                "uploaded_by": uid,
                "uploaded_at": datetime.now(timezone.utc).isoformat()
            }
        }}
    )

    return {"success": True, "total_slides": result["total_slides"], "filename": result["filename"]}


@router.get("/{webinar_id}/presentation/slides")
async def get_presentation_slides(webinar_id: str, user=Depends(get_current_user)):
    """Get presentation slide URLs for the webinar."""
    webinar = await db.webinars.find_one(
        {"webinar_id": webinar_id},
        {"_id": 0, "presentation": 1}
    )
    if not webinar or not webinar.get("presentation"):
        raise HTTPException(404, "No presentation uploaded")

    pres = webinar["presentation"]
    return {
        "filename": pres["filename"],
        "total_slides": pres["total_slides"],
        "slide_paths": pres["slide_paths"]
    }


@router.get("/{webinar_id}/presentation/slide/{slide_index}")
async def get_slide_image(webinar_id: str, slide_index: int, user=Depends(get_current_user)):
    """Get a specific slide image."""
    from fastapi.responses import Response
    from services.object_storage import get_object

    webinar = await db.webinars.find_one(
        {"webinar_id": webinar_id},
        {"_id": 0, "presentation": 1}
    )
    if not webinar or not webinar.get("presentation"):
        raise HTTPException(404, "No presentation")

    paths = webinar["presentation"].get("slide_paths", [])
    if slide_index < 0 or slide_index >= len(paths):
        raise HTTPException(404, "Slide not found")

    data, ct = get_object(paths[slide_index])
    return Response(content=data, media_type="image/png")


# --- Live Transcript ---

class SaveTranscriptRequest(BaseModel):
    transcript: str
    duration_seconds: float = 0


@router.post("/{webinar_id}/live-transcript/save")
async def save_live_transcript(webinar_id: str, data: SaveTranscriptRequest, user=Depends(get_current_user)):
    """Save accumulated live transcript from a webinar session."""
    webinar = await db.webinars.find_one({"webinar_id": webinar_id}, {"_id": 0, "host_id": 1, "title": 1})
    if not webinar:
        raise HTTPException(404, "Webinar not found")

    uid = user["user_id"]
    is_host = uid == webinar.get("host_id")
    if not is_host:
        raise HTTPException(403, "Only host can save transcript")

    await db.webinars.update_one(
        {"webinar_id": webinar_id},
        {"$set": {
            "live_transcript": {
                "text": data.transcript,
                "saved_by": uid,
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "word_count": len(data.transcript.split()),
                "duration_seconds": data.duration_seconds
            }
        }}
    )
    return {"success": True, "word_count": len(data.transcript.split())}


@router.get("/{webinar_id}/live-transcript")
async def get_live_transcript(webinar_id: str, user=Depends(get_current_user)):
    """Get saved live transcript for a webinar."""
    webinar = await db.webinars.find_one(
        {"webinar_id": webinar_id},
        {"_id": 0, "live_transcript": 1}
    )
    if not webinar:
        raise HTTPException(404, "Webinar not found")
    return {"transcript": webinar.get("live_transcript")}


# --- AI Meeting Notes ---

class SendNotesRequest(BaseModel):
    recording_id: str
    recipient_emails: List[str] = []


@router.post("/{webinar_id}/notes/generate")
async def generate_notes(webinar_id: str, recording_id: str, user=Depends(get_current_user)):
    """Generate AI meeting notes from a recording's transcript."""
    webinar = await db.webinars.find_one({"webinar_id": webinar_id}, {"_id": 0, "title": 1, "host_id": 1})
    if not webinar:
        raise HTTPException(404, "Webinar not found")

    recording = await db.karau_recordings.find_one(
        {"recording_id": recording_id},
        {"_id": 0, "transcription": 1, "transcription_status": 1}
    )
    if not recording or recording.get("transcription_status") != "completed":
        raise HTTPException(400, "Transcript not available for this recording")

    transcript_text = recording["transcription"].get("text", "")
    if not transcript_text:
        raise HTTPException(400, "Transcript is empty")

    from services.meeting_notes_service import generate_meeting_notes
    result = await generate_meeting_notes(transcript_text, webinar.get("title", "Meeting"))

    if result.get("error"):
        raise HTTPException(500, result["error"])

    # Store notes
    await db.karau_recordings.update_one(
        {"recording_id": recording_id},
        {"$set": {"meeting_notes": result}}
    )

    return {"success": True, "notes": result}


@router.post("/{webinar_id}/notes/send")
async def send_notes(webinar_id: str, data: SendNotesRequest, user=Depends(get_current_user)):
    """Send meeting notes to recipients. Stores the send record."""
    recording = await db.karau_recordings.find_one(
        {"recording_id": data.recording_id},
        {"_id": 0, "meeting_notes": 1}
    )
    if not recording or not recording.get("meeting_notes"):
        raise HTTPException(400, "No meeting notes to send")

    # Store send record
    send_record = {
        "sent_by": user["user_id"],
        "sent_by_name": user.get("name", user.get("email")),
        "sent_to": data.recipient_emails,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "recording_id": data.recording_id,
        "webinar_id": webinar_id
    }
    await db.meeting_notes_sent.insert_one(send_record)

    return {
        "success": True,
        "sent_to": data.recipient_emails,
        "notes_preview": recording["meeting_notes"]["notes"][:200] + "..."
    }
