"""
AI KARAU Meeting API Routes
WebRTC signaling and meeting management
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import asyncio
from datetime import datetime, timezone

from services.karau_meet import (
    create_meeting,
    get_meeting,
    join_meeting,
    leave_meeting,
    end_meeting,
    get_participants,
    update_participant,
    add_chat_message,
    add_ai_note,
    create_breakout_room,
    start_breakout_session,
    get_breakout_session,
    close_breakout_session,
    move_participant_breakout,
    ai_auto_assign_breakout,
    get_user_meetings,
    get_ice_servers,
    meeting_participants,
    waiting_rooms,
    add_to_waiting_room,
    get_waiting_room,
    admit_from_waiting_room,
    admit_all_from_waiting_room,
    reject_from_waiting_room,
    is_user_admitted,
)
from services.karau_meet.webrtc_signaling import get_connection_manager
from routes.auth import get_current_user, require_auth

router = APIRouter(prefix="/karau-meet", tags=["AI KARAU Meeting"])

# WebSocket connections storage
connected_clients: Dict[str, Dict[str, WebSocket]] = {}  # meeting_id -> {user_id: websocket}


class CreateMeetingRequest(BaseModel):
    title: str = "AI KARAU Meeting"
    scheduled_time: Optional[str] = None
    settings: Optional[Dict] = None


class JoinMeetingRequest(BaseModel):
    video_enabled: bool = True
    audio_enabled: bool = True


class UpdateParticipantRequest(BaseModel):
    video_enabled: Optional[bool] = None
    audio_enabled: Optional[bool] = None
    screen_sharing: Optional[bool] = None
    hand_raised: Optional[bool] = None


class ChatMessageRequest(BaseModel):
    message: str
    message_type: str = "text"


class BreakoutRoomRequest(BaseModel):
    room_name: str
    participant_ids: List[str]


class BreakoutSessionRequest(BaseModel):
    rooms: List[Dict] = []  # [{"room_name": "Room 1", "participant_ids": ["u1","u2"]}]
    timer_minutes: int = 0  # 0 = no timer
    auto_assign: bool = False
    num_rooms: int = 2  # for auto-assign


class MoveParticipantRequest(BaseModel):
    user_id: str
    target_room_id: str


class SignalRequest(BaseModel):
    target_user_id: str
    signal_type: str  # "offer", "answer", "ice-candidate"
    signal_data: Dict


@router.post("/meetings")
async def create_new_meeting(
    request: CreateMeetingRequest,
    user: dict = Depends(require_auth)
):
    """Create a new AI KARAU meeting"""
    meeting = await create_meeting(
        host_id=user["user_id"],
        host_name=user.get("name", user.get("email", "Host")),
        title=request.title,
        scheduled_time=request.scheduled_time,
        settings=request.settings
    )
    return meeting


@router.get("/meetings")
async def get_my_meetings(
    limit: int = 20,
    user: dict = Depends(require_auth)
):
    """Get user's meetings (hosted and participated)"""
    meetings = await get_user_meetings(user["user_id"], limit)
    return {"meetings": meetings}



@router.get("/stats")
async def get_dashboard_stats(user: dict = Depends(require_auth)):
    """Get real dashboard statistics from MongoDB."""
    from utils.database import db

    user_id = user["user_id"]

    # Total meetings for this user (hosted or participated)
    total_meetings = await db.karau_meetings.count_documents({
        "$or": [{"host_id": user_id}, {"participants.user_id": user_id}]
    })

    # Active meetings
    active_meetings = await db.karau_meetings.count_documents({
        "$or": [{"host_id": user_id}, {"participants.user_id": user_id}],
        "status": "active"
    })

    # Calculate total hours from ended meetings
    pipeline = [
        {"$match": {
            "$or": [{"host_id": user_id}, {"participants.user_id": user_id}],
            "started_at": {"$exists": True},
            "ended_at": {"$exists": True}
        }},
        {"$project": {
            "duration_str": {"$subtract": [
                {"$dateFromString": {"dateString": "$ended_at", "onError": None}},
                {"$dateFromString": {"dateString": "$started_at", "onError": None}}
            ]}
        }},
        {"$match": {"duration_str": {"$ne": None}}},
        {"$group": {"_id": None, "total_ms": {"$sum": "$duration_str"}}}
    ]
    hours_result = await db.karau_meetings.aggregate(pipeline).to_list(1)
    total_hours = round(hours_result[0]["total_ms"] / 3600000, 1) if hours_result else 0

    # Recordings count
    recordings = await db.karau_meetings.count_documents({
        "$or": [{"host_id": user_id}, {"participants.user_id": user_id}],
        "recordings": {"$exists": True, "$ne": []}
    })

    # Unique participants across all user's meetings
    part_pipeline = [
        {"$match": {"$or": [{"host_id": user_id}, {"participants.user_id": user_id}]}},
        {"$unwind": "$participants"},
        {"$group": {"_id": "$participants.user_id"}},
        {"$count": "total"}
    ]
    part_result = await db.karau_meetings.aggregate(part_pipeline).to_list(1)
    total_participants = part_result[0]["total"] if part_result else 0

    # AI insights count
    insights_pipeline = [
        {"$match": {"$or": [{"host_id": user_id}, {"participants.user_id": user_id}]}},
        {"$project": {"notes_count": {"$size": {"$ifNull": ["$ai_notes", []]}}}},
        {"$group": {"_id": None, "total": {"$sum": "$notes_count"}}}
    ]
    insights_result = await db.karau_meetings.aggregate(insights_pipeline).to_list(1)
    total_insights = insights_result[0]["total"] if insights_result else 0

    return {
        "total_meetings": total_meetings,
        "active_meetings": active_meetings,
        "total_hours": total_hours,
        "recordings": recordings,
        "total_participants": total_participants,
        "ai_insights": total_insights
    }


@router.get("/activity-feed")
async def get_activity_feed(limit: int = 15, user: dict = Depends(require_auth)):
    """Get live activity feed for dashboard."""
    from utils.database import db

    user_id = user["user_id"]
    activities = []

    # Recent meetings (created, started, ended)
    recent_meetings = await db.karau_meetings.find(
        {"$or": [{"host_id": user_id}, {"participants.user_id": user_id}]},
        {"_id": 0, "meeting_id": 1, "title": 1, "status": 1, "host_name": 1,
         "created_at": 1, "started_at": 1, "ended_at": 1,
         "participants": 1, "ai_notes": 1}
    ).sort("created_at", -1).limit(limit).to_list(limit)

    for m in recent_meetings:
        meeting_title = m.get("title", "Meeting")
        host = m.get("host_name", "Someone")
        participants = m.get("participants", [])

        # Meeting created
        activities.append({
            "type": "meeting_created",
            "text": f"{host} created \"{meeting_title}\"",
            "timestamp": m.get("created_at", ""),
            "meeting_id": m.get("meeting_id"),
            "icon": "video"
        })

        # Meeting started
        if m.get("started_at"):
            activities.append({
                "type": "meeting_started",
                "text": f"\"{meeting_title}\" started with {len(participants)} participant{'s' if len(participants) != 1 else ''}",
                "timestamp": m.get("started_at", ""),
                "meeting_id": m.get("meeting_id"),
                "icon": "play"
            })

        # Meeting ended
        if m.get("ended_at"):
            activities.append({
                "type": "meeting_ended",
                "text": f"\"{meeting_title}\" ended",
                "timestamp": m.get("ended_at", ""),
                "meeting_id": m.get("meeting_id"),
                "icon": "check"
            })

        # Participant joined
        for p in participants[:3]:
            if p.get("joined_at"):
                activities.append({
                    "type": "participant_joined",
                    "text": f"{p.get('user_name', 'Someone')} joined \"{meeting_title}\"",
                    "timestamp": p.get("joined_at", ""),
                    "meeting_id": m.get("meeting_id"),
                    "icon": "user"
                })

        # AI notes detected
        ai_notes = m.get("ai_notes", [])
        action_items = [n for n in ai_notes if n.get("type") == "action_item"]
        if action_items:
            activities.append({
                "type": "ai_insight",
                "text": f"{len(action_items)} action item{'s' if len(action_items) != 1 else ''} detected in \"{meeting_title}\"",
                "timestamp": action_items[-1].get("timestamp", m.get("created_at", "")),
                "meeting_id": m.get("meeting_id"),
                "icon": "sparkles"
            })

    # Sort by timestamp descending and limit
    activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {"activities": activities[:limit]}

@router.get("/meetings/{meeting_id}/info")
async def get_meeting_public_info(meeting_id: str):
    """Get basic meeting info (public, no auth required) for guest join page"""
    meeting = await get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return {
        "meeting_id": meeting.get("meeting_id", meeting_id),
        "title": meeting.get("title", "AI KARAU Meeting"),
        "status": meeting.get("status", "active"),
        "host_name": meeting.get("host_name", "Host"),
        "created_at": meeting.get("created_at", ""),
    }


@router.get("/meetings/{meeting_id}")
async def get_meeting_details(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Get meeting details"""
    meeting = await get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return {
        "meeting": meeting,
        "ice_servers": get_ice_servers(),
        "participants": await get_participants(meeting_id)
    }


@router.post("/meetings/{meeting_id}/join")
async def join_meeting_room(
    meeting_id: str,
    request: JoinMeetingRequest,
    user: dict = Depends(require_auth)
):
    """Join a meeting"""
    result = await join_meeting(
        meeting_id=meeting_id,
        user_id=user["user_id"],
        user_name=user.get("name", user.get("email", "Participant")),
        video_enabled=request.video_enabled,
        audio_enabled=request.audio_enabled
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Add ICE servers for WebRTC
    result["ice_servers"] = get_ice_servers()
    
    return result


class GuestJoinRequest(BaseModel):
    guest_name: str = "Guest"
    video_enabled: bool = True
    audio_enabled: bool = True


@router.post("/meetings/{meeting_id}/join-guest")
async def join_meeting_as_guest(
    meeting_id: str,
    request: GuestJoinRequest
):
    """Join a meeting as a guest (no authentication required)"""
    import uuid
    
    # Generate a guest user ID
    guest_id = f"guest_{uuid.uuid4().hex[:12]}"
    guest_name = request.guest_name or "Guest"
    
    result = await join_meeting(
        meeting_id=meeting_id,
        user_id=guest_id,
        user_name=guest_name,
        video_enabled=request.video_enabled,
        audio_enabled=request.audio_enabled
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Add ICE servers for WebRTC
    result["ice_servers"] = get_ice_servers()
    # Include the generated guest ID for the client
    result["guest_user_id"] = guest_id
    result["guest_name"] = guest_name
    
    return result


@router.post("/meetings/{meeting_id}/leave")
async def leave_meeting_room(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Leave a meeting"""
    success = await leave_meeting(meeting_id, user["user_id"])
    
    if not success:
        raise HTTPException(status_code=404, detail="Meeting or participant not found")
    
    # Notify other participants via WebSocket
    await broadcast_to_meeting(meeting_id, {
        "type": "participant_left",
        "user_id": user["user_id"]
    }, exclude_user=user["user_id"])
    
    return {"success": True}


@router.post("/meetings/{meeting_id}/end")
async def end_meeting_room(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """End a meeting (host only)"""
    success = await end_meeting(meeting_id, user["user_id"])
    
    if not success:
        raise HTTPException(status_code=403, detail="Only host can end the meeting")
    
    # Notify all participants
    await broadcast_to_meeting(meeting_id, {
        "type": "meeting_ended",
        "ended_by": user["user_id"]
    })
    
    # Close all WebSocket connections
    if meeting_id in connected_clients:
        for ws in connected_clients[meeting_id].values():
            try:
                await ws.close()
            except:
                pass
        del connected_clients[meeting_id]
    
    return {"success": True}


@router.get("/meetings/{meeting_id}/participants")
async def get_meeting_participants(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Get all participants in a meeting"""
    participants = await get_participants(meeting_id)
    return {"participants": participants}


@router.put("/meetings/{meeting_id}/participant")
async def update_my_participant_status(
    meeting_id: str,
    request: UpdateParticipantRequest,
    user: dict = Depends(require_auth)
):
    """Update participant status (video, audio, etc.)"""
    updates = {}
    if request.video_enabled is not None:
        updates["video_enabled"] = request.video_enabled
    if request.audio_enabled is not None:
        updates["audio_enabled"] = request.audio_enabled
    if request.screen_sharing is not None:
        updates["screen_sharing"] = request.screen_sharing
    if request.hand_raised is not None:
        updates["hand_raised"] = request.hand_raised
    
    success = await update_participant(meeting_id, user["user_id"], updates)
    
    if not success:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    # Broadcast update to other participants
    await broadcast_to_meeting(meeting_id, {
        "type": "participant_updated",
        "user_id": user["user_id"],
        "updates": updates
    })
    
    return {"success": True}


@router.post("/meetings/{meeting_id}/chat")
async def send_chat_message(
    meeting_id: str,
    request: ChatMessageRequest,
    user: dict = Depends(require_auth)
):
    """Send a chat message in the meeting"""
    message = await add_chat_message(
        meeting_id=meeting_id,
        user_id=user["user_id"],
        user_name=user.get("name", user.get("email", "Unknown")),
        message=request.message,
        message_type=request.message_type
    )
    
    # Broadcast to all participants
    await broadcast_to_meeting(meeting_id, {
        "type": "chat_message",
        "message": message
    })
    
    return message


@router.post("/meetings/{meeting_id}/ai-note")
async def add_meeting_ai_note(
    meeting_id: str,
    note_type: str,
    content: str,
    user: dict = Depends(require_auth)
):
    """Add an AI-generated note (transcription, summary, etc.)"""
    note = await add_ai_note(
        meeting_id=meeting_id,
        note_type=note_type,
        content=content
    )
    
    # Broadcast to all participants
    await broadcast_to_meeting(meeting_id, {
        "type": "ai_note",
        "note": note
    })
    
    return note


@router.get("/meetings/{meeting_id}/summary/pdf")
async def export_meeting_summary_pdf(meeting_id: str, user: dict = Depends(require_auth)):
    """Generate and download a meeting summary PDF with highlights and key takeaways"""
    from fastapi.responses import StreamingResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm, inch
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from utils.database import db
    import io

    meeting = await get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Fetch org branding for enterprise users
    org_branding = None
    if meeting.get("org_id"):
        org_branding = await db.karau_organizations.find_one(
            {"org_id": meeting["org_id"]}, {"_id": 0}
        )

    # Fetch AI notes from the meeting
    ai_notes = meeting.get("ai_notes", [])
    summaries = [n for n in ai_notes if n.get("type") == "summary"]
    action_items = [n for n in ai_notes if n.get("type") == "action_item"]
    highlights = [n for n in ai_notes if n.get("type") in ("highlight", "transcription")]
    participants = meeting.get("participants", [])

    # Colors
    turquoise = HexColor("#2DD4BF")
    text_dark = HexColor("#1E293B")
    text_gray = HexColor("#64748B")
    accent = HexColor(org_branding.get("primary_color", "#2DD4BF")) if org_branding else turquoise

    # Build PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='MeetingTitle', fontSize=22, leading=28, textColor=text_dark, fontName='Helvetica-Bold', spaceAfter=4))
    styles.add(ParagraphStyle(name='Subtitle', fontSize=10, leading=14, textColor=text_gray, spaceAfter=12))
    styles.add(ParagraphStyle(name='SectionHead', fontSize=14, leading=18, textColor=text_dark, fontName='Helvetica-Bold', spaceBefore=16, spaceAfter=8))
    styles.add(ParagraphStyle(name='BodyText2', fontSize=10, leading=15, textColor=text_dark, spaceAfter=4))
    styles.add(ParagraphStyle(name='BulletItem', fontSize=10, leading=15, textColor=text_dark, leftIndent=12, bulletIndent=0, spaceAfter=3))
    styles.add(ParagraphStyle(name='FooterStyle', fontSize=8, leading=10, textColor=text_gray, alignment=TA_CENTER))

    elements = []

    # Header with branding
    org_name = org_branding.get("name", "") if org_branding else "AI KARAU"
    elements.append(Paragraph(f'<font color="#{accent.hexval()[2:]}">{org_name}</font> Meeting Summary', styles['MeetingTitle']))

    # Meeting metadata
    title = meeting.get("title", "Untitled Meeting")
    created = meeting.get("created_at", "")
    started = meeting.get("started_at", "")
    ended = meeting.get("ended_at", "")
    duration_str = ""
    if started and ended:
        try:
            s = datetime.fromisoformat(started.replace("Z", "+00:00"))
            e = datetime.fromisoformat(ended.replace("Z", "+00:00"))
            mins = int((e - s).total_seconds() / 60)
            duration_str = f"{mins} minutes"
        except:
            pass

    meta_lines = [f"<b>Meeting:</b> {title}"]
    if created:
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            meta_lines.append(f"<b>Date:</b> {dt.strftime('%B %d, %Y at %I:%M %p UTC')}")
        except:
            meta_lines.append(f"<b>Date:</b> {created}")
    if duration_str:
        meta_lines.append(f"<b>Duration:</b> {duration_str}")
    meta_lines.append(f"<b>Participants:</b> {len(participants)}")

    for line in meta_lines:
        elements.append(Paragraph(line, styles['Subtitle']))

    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1, color=HexColor("#E2E8F0")))
    elements.append(Spacer(1, 8))

    # Participants
    if participants:
        elements.append(Paragraph("Participants", styles['SectionHead']))
        participant_names = []
        for p in participants:
            name = p.get("user_name", "Unknown") if isinstance(p, dict) else str(p)
            role = ""
            if isinstance(p, dict) and p.get("is_host"):
                role = " (Host)"
            participant_names.append(f"{name}{role}")
        elements.append(Paragraph(", ".join(participant_names), styles['BodyText2']))
        elements.append(Spacer(1, 6))

    # Key Takeaways / Summary
    if summaries:
        elements.append(Paragraph("Key Takeaways", styles['SectionHead']))
        for note in summaries:
            content = note.get("content", "")
            for line in content.split("\n"):
                line = line.strip()
                if line:
                    elements.append(Paragraph(f"&bull; {line}", styles['BulletItem']))
        elements.append(Spacer(1, 6))

    # Action Items
    if action_items:
        elements.append(Paragraph("Action Items", styles['SectionHead']))
        for i, item in enumerate(action_items, 1):
            content = item.get("content", "")
            elements.append(Paragraph(f"<b>{i}.</b> {content}", styles['BulletItem']))
        elements.append(Spacer(1, 6))

    # Highlights
    if highlights:
        elements.append(Paragraph("Discussion Highlights", styles['SectionHead']))
        shown = 0
        for note in highlights[-20:]:
            content = note.get("content", "")
            if content and shown < 20:
                ts = note.get("timestamp", "")
                time_label = ""
                if ts:
                    try:
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        time_label = f'<font color="#94A3B8">[{dt.strftime("%H:%M")}]</font> '
                    except:
                        pass
                elements.append(Paragraph(f"{time_label}{content}", styles['BodyText2']))
                shown += 1
        elements.append(Spacer(1, 6))

    # If no AI notes at all
    if not summaries and not action_items and not highlights:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("No AI notes or transcription data available for this meeting.", styles['BodyText2']))
        elements.append(Paragraph("Enable AI Transcription during meetings to generate summaries and action items.", styles['Subtitle']))

    # Footer
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0")))
    elements.append(Spacer(1, 6))
    footer_text = org_branding.get("watermark_text", "AI KARAU") if org_branding else "AI KARAU"
    elements.append(Paragraph(f"Generated by {footer_text} | {datetime.now(timezone.utc).strftime('%B %d, %Y')}", styles['FooterStyle']))

    doc.build(elements)
    buffer.seek(0)

    safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()[:50]
    filename = f"Meeting_Summary_{safe_title}_{meeting_id[:8]}.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.post("/meetings/{meeting_id}/breakout-rooms")
async def create_meeting_breakout_room(
    meeting_id: str,
    request: BreakoutRoomRequest,
    user: dict = Depends(require_auth)
):
    """Create a single breakout room (host only)"""
    meeting = await get_meeting(meeting_id)
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meeting["host_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Only host can create breakout rooms")
    
    room = await create_breakout_room(
        meeting_id=meeting_id,
        room_name=request.room_name,
        participant_ids=request.participant_ids
    )
    
    manager = get_connection_manager()
    for participant_id in request.participant_ids:
        await manager.send_to_user(meeting_id, participant_id, {
            "type": "breakout_room_assigned",
            "room": room
        })
    
    return room


@router.post("/meetings/{meeting_id}/breakout-session/start")
async def start_breakout(
    meeting_id: str,
    request: BreakoutSessionRequest,
    user: dict = Depends(require_auth)
):
    """Start a breakout session with multiple rooms (host only)."""
    meeting = await get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    if meeting["host_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Only host can manage breakout rooms")

    rooms = request.rooms
    if request.auto_assign:
        rooms = await ai_auto_assign_breakout(meeting_id, request.num_rooms)
        if not rooms:
            raise HTTPException(status_code=400, detail="No participants to assign")

    session = await start_breakout_session(meeting_id, rooms, request.timer_minutes)

    # Notify all participants
    manager = get_connection_manager()
    await manager.broadcast_to_meeting(meeting_id, {
        "type": "breakout_session_started",
        "session": session
    }, store_in_history=False)

    return session


@router.get("/meetings/{meeting_id}/breakout-session")
async def get_breakout(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Get current breakout session status."""
    session = await get_breakout_session(meeting_id)
    if not session:
        return {"status": "none", "session": None}
    return {"status": session["status"], "session": session}


@router.post("/meetings/{meeting_id}/breakout-session/close")
async def close_breakout(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Close breakout session and return everyone to main room (host only)."""
    meeting = await get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    if meeting["host_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Only host can close breakout rooms")

    result = await close_breakout_session(meeting_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    manager = get_connection_manager()
    await manager.broadcast_to_meeting(meeting_id, {
        "type": "breakout_session_closed",
        "returned_count": result.get("returned_count", 0)
    }, store_in_history=False)

    return result


@router.post("/meetings/{meeting_id}/breakout-session/move")
async def move_participant(
    meeting_id: str,
    request: MoveParticipantRequest,
    user: dict = Depends(require_auth)
):
    """Move a participant between breakout rooms (host only)."""
    meeting = await get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    if meeting["host_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Only host can move participants")

    result = await move_participant_breakout(meeting_id, request.user_id, request.target_room_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    manager = get_connection_manager()
    await manager.send_to_user(meeting_id, request.user_id, {
        "type": "breakout_room_moved",
        "room_id": request.target_room_id
    })

    return result


@router.post("/meetings/{meeting_id}/breakout-session/auto-assign")
async def auto_assign_breakout(
    meeting_id: str,
    num_rooms: int = 2,
    user: dict = Depends(require_auth)
):
    """Preview AI auto-assignment without starting (host only)."""
    meeting = await get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    if meeting["host_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Only host can manage breakout rooms")

    rooms = await ai_auto_assign_breakout(meeting_id, num_rooms)

    # Resolve user names
    participants = meeting_participants.get(meeting_id, {})
    for room in rooms:
        room["participants_detail"] = [
            {"user_id": uid, "user_name": participants.get(uid, {}).get("user_name", uid)}
            for uid in room.get("participant_ids", [])
        ]

    return {"rooms": rooms, "total_participants": sum(len(r.get("participant_ids", [])) for r in rooms)}


@router.post("/meetings/{meeting_id}/signal")
async def send_webrtc_signal(
    meeting_id: str,
    request: SignalRequest,
    user: dict = Depends(require_auth)
):
    """Send WebRTC signaling data to another participant"""
    # Send signal to target user via WebSocket
    await send_to_user(meeting_id, request.target_user_id, {
        "type": "webrtc_signal",
        "from_user_id": user["user_id"],
        "signal_type": request.signal_type,
        "signal_data": request.signal_data
    })
    
    return {"success": True}


# Note: WebSocket endpoint has been moved to karau_webrtc.py for better organization
# Use /api/karau-meet/ws/{meeting_id}?token=xxx&user_name=xxx from karau_webrtc router


async def broadcast_to_meeting(meeting_id: str, message: dict, exclude_user: str = None):
    """Broadcast a message to all participants in a meeting (legacy - use webrtc_signaling)"""
    if meeting_id not in connected_clients:
        return
    
    for user_id, ws in list(connected_clients[meeting_id].items()):
        if exclude_user and user_id == exclude_user:
            continue
        try:
            await ws.send_json(message)
        except:
            # Remove dead connection
            del connected_clients[meeting_id][user_id]


async def send_to_user(meeting_id: str, user_id: str, message: dict):
    """Send a message to a specific user"""
    if meeting_id not in connected_clients:
        return False
    
    if user_id not in connected_clients[meeting_id]:
        return False
    
    try:
        await connected_clients[meeting_id][user_id].send_json(message)
        return True
    except:
        return False


# ============ LOBBY / WAITING ROOM ENDPOINTS ============

class LobbyJoinRequest(BaseModel):
    guest_name: str = "Guest"
    guest_email: str = ""
    is_guest: bool = True


@router.post("/meetings/{meeting_id}/lobby/join")
async def join_lobby(meeting_id: str, request: LobbyJoinRequest):
    """Join the meeting lobby (waiting room). No auth required for guests."""
    import uuid

    meeting = await get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting.get("status") == "ended":
        raise HTTPException(status_code=400, detail="Meeting has ended")

    settings = meeting.get("settings", {})
    require_admission = settings.get("waiting_room_enabled", True)

    user_id = f"guest_{uuid.uuid4().hex[:12]}"
    user_name = request.guest_name or "Guest"

    if require_admission:
        waiting_user = await add_to_waiting_room(
            meeting_id, user_id, user_name, request.guest_email
        )
        # Notify host via WebRTC connection manager
        host_id = meeting.get("host_id")
        if host_id:
            manager = get_connection_manager()
            await manager.send_to_user(meeting_id, host_id, {
                "type": "lobby_guest_waiting",
                "user_id": user_id,
                "user_name": user_name,
                "user_email": request.guest_email,
                "joined_at": waiting_user["joined_at"]
            })
        return {
            "status": "waiting",
            "user_id": user_id,
            "user_name": user_name,
            "meeting_title": meeting.get("title", "AI KARAU Meeting"),
            "host_name": meeting.get("host_name", "Host"),
            "require_admission": True,
            "message": "Waiting for the host to admit you"
        }
    else:
        return {
            "status": "admitted",
            "user_id": user_id,
            "user_name": user_name,
            "meeting_title": meeting.get("title", "AI KARAU Meeting"),
            "host_name": meeting.get("host_name", "Host"),
            "require_admission": False,
            "message": "You can join directly"
        }


@router.post("/meetings/{meeting_id}/lobby/join-auth")
async def join_lobby_authenticated(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Join the meeting lobby as an authenticated user."""
    meeting = await get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting.get("status") == "ended":
        raise HTTPException(status_code=400, detail="Meeting has ended")

    # Host always gets admitted
    is_host = meeting.get("host_id") == user["user_id"]
    settings = meeting.get("settings", {})
    require_admission = settings.get("waiting_room_enabled", True) and not is_host

    if require_admission:
        waiting_user = await add_to_waiting_room(
            meeting_id,
            user["user_id"],
            user.get("name", user.get("email", "Participant")),
            user.get("email", "")
        )
        host_id = meeting.get("host_id")
        if host_id:
            manager = get_connection_manager()
            await manager.send_to_user(meeting_id, host_id, {
                "type": "lobby_guest_waiting",
                "user_id": user["user_id"],
                "user_name": user.get("name", user.get("email", "Participant")),
                "user_email": user.get("email", ""),
                "joined_at": waiting_user["joined_at"]
            })
        return {
            "status": "waiting",
            "user_id": user["user_id"],
            "user_name": user.get("name", user.get("email", "Participant")),
            "meeting_title": meeting.get("title", "AI KARAU Meeting"),
            "host_name": meeting.get("host_name", "Host"),
            "require_admission": True,
            "is_host": False,
            "message": "Waiting for the host to admit you"
        }
    else:
        return {
            "status": "admitted",
            "user_id": user["user_id"],
            "user_name": user.get("name", user.get("email", "Participant")),
            "meeting_title": meeting.get("title", "AI KARAU Meeting"),
            "host_name": meeting.get("host_name", "Host"),
            "require_admission": False,
            "is_host": is_host,
            "message": "You can join directly"
        }


@router.get("/meetings/{meeting_id}/lobby/status")
async def check_lobby_status(meeting_id: str, user_id: str):
    """Check if a user has been admitted from the lobby. Polled by guests."""
    if meeting_id not in waiting_rooms:
        return {"status": "admitted", "admitted": True}

    if user_id not in waiting_rooms.get(meeting_id, {}):
        return {"status": "not_found", "admitted": False}

    user_data = waiting_rooms[meeting_id][user_id]
    status = user_data.get("status", "waiting")

    return {
        "status": status,
        "admitted": status == "admitted",
        "rejected": status == "rejected"
    }


@router.get("/meetings/{meeting_id}/lobby/waiting")
async def get_lobby_waiting_list(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Get the list of users waiting in the lobby (host only)."""
    meeting = await get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting["host_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Only the host can view the waiting list")

    waiting_list = await get_waiting_room(meeting_id)
    return {"waiting": waiting_list, "count": len(waiting_list)}


class AdmitRequest(BaseModel):
    user_id: str


@router.post("/meetings/{meeting_id}/lobby/admit")
async def admit_from_lobby(
    meeting_id: str,
    request: AdmitRequest,
    user: dict = Depends(require_auth)
):
    """Admit a user from the lobby (host only)."""
    result = await admit_from_waiting_room(meeting_id, request.user_id, user["user_id"])
    if "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return result


@router.post("/meetings/{meeting_id}/lobby/admit-all")
async def admit_all_from_lobby(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Admit all waiting users from the lobby (host only)."""
    result = await admit_all_from_waiting_room(meeting_id, user["user_id"])
    if "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return result


@router.post("/meetings/{meeting_id}/lobby/deny")
async def deny_from_lobby(
    meeting_id: str,
    request: AdmitRequest,
    user: dict = Depends(require_auth)
):
    """Deny/reject a user from the lobby (host only)."""
    result = await reject_from_waiting_room(meeting_id, request.user_id, user["user_id"])
    if "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return result


@router.put("/meetings/{meeting_id}/settings/waiting-room")
async def toggle_waiting_room(
    meeting_id: str,
    enabled: bool = True,
    user: dict = Depends(require_auth)
):
    """Toggle waiting room requirement for a meeting (host only)."""
    meeting = await get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting["host_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Only the host can change settings")

    meeting.setdefault("settings", {})["waiting_room_enabled"] = enabled
    return {"success": True, "waiting_room_enabled": enabled}
