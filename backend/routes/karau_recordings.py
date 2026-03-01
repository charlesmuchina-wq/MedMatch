"""
AI KARAU Meeting - Recordings API Routes
Browser-side recordings with cloud storage upload support.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query, Header, BackgroundTasks
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid
import logging
import asyncio

from utils.database import db
from routes.auth import get_current_user, require_auth
from services.object_storage import put_object, get_object, generate_upload_path, init_storage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/karau-meet/recordings", tags=["AI KARAU Recordings"])

recordings = db.karau_recordings


class RecordingMetadata(BaseModel):
    meeting_id: str
    meeting_title: str
    duration_seconds: int
    file_size_bytes: int
    file_name: str
    recorded_by: Optional[str] = None


@router.post("/metadata")
async def save_recording_metadata(
    request: RecordingMetadata,
    user: dict = Depends(require_auth)
):
    """Save recording metadata after browser-side recording"""
    recording_doc = {
        "recording_id": str(uuid.uuid4())[:12],
        "meeting_id": request.meeting_id,
        "meeting_title": request.meeting_title,
        "duration_seconds": request.duration_seconds,
        "file_size_bytes": request.file_size_bytes,
        "file_name": request.file_name,
        "recorded_by": user["user_id"],
        "recorded_by_name": user.get("name", user.get("email", "Unknown")),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "storage_type": "browser_local",
        "status": "completed",
        "is_deleted": False
    }

    await recordings.insert_one(recording_doc)
    recording_doc.pop("_id", None)

    return {"success": True, "recording": recording_doc}


@router.post("/upload")
async def upload_recording(
    file: UploadFile = File(...),
    meeting_id: str = Form(...),
    meeting_title: str = Form(""),
    duration_seconds: int = Form(0),
    user: dict = Depends(require_auth)
):
    """Upload a recording to cloud storage (auto-upload after meeting ends)."""
    max_size = 500 * 1024 * 1024  # 500MB
    data = await file.read()

    if len(data) > max_size:
        raise HTTPException(413, "File too large (max 500MB)")

    content_type = file.content_type or "video/webm"
    storage_path = generate_upload_path(user["user_id"], file.filename or "recording.webm")

    try:
        result = put_object(storage_path, data, content_type)
    except Exception as e:
        logger.error(f"Cloud upload failed: {e}")
        raise HTTPException(500, f"Cloud upload failed: {str(e)}")

    recording_doc = {
        "recording_id": str(uuid.uuid4())[:12],
        "meeting_id": meeting_id,
        "meeting_title": meeting_title or "Untitled Meeting",
        "duration_seconds": duration_seconds,
        "file_size_bytes": len(data),
        "file_name": file.filename or "recording.webm",
        "storage_path": result["path"],
        "content_type": content_type,
        "recorded_by": user["user_id"],
        "recorded_by_name": user.get("name", user.get("email", "Unknown")),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "storage_type": "cloud",
        "status": "completed",
        "transcription_status": "queued",
        "is_deleted": False
    }

    await recordings.insert_one(recording_doc)
    recording_doc.pop("_id", None)

    # Auto-trigger transcription in background
    try:
        from services.transcription_service import auto_transcribe_and_store
        asyncio.create_task(auto_transcribe_and_store(
            recording_doc["recording_id"], result["path"], content_type, db
        ))
    except Exception as e:
        logger.warning(f"Transcription trigger failed: {e}")

    return {"success": True, "recording": recording_doc}


@router.get("/")
async def get_user_recordings(
    user: dict = Depends(require_auth),
    limit: int = 50,
    skip: int = 0
):
    """Get all recordings for the current user"""
    cursor = recordings.find(
        {"recorded_by": user["user_id"], "is_deleted": {"$ne": True}},
        {"_id": 0}
    ).sort("recorded_at", -1).skip(skip).limit(limit)

    user_recordings = await cursor.to_list(length=limit)
    total = await recordings.count_documents(
        {"recorded_by": user["user_id"], "is_deleted": {"$ne": True}}
    )

    return {"recordings": user_recordings, "total": total, "limit": limit, "skip": skip}


@router.get("/meeting/{meeting_id}")
async def get_meeting_recordings(meeting_id: str, user: dict = Depends(require_auth)):
    """Get all recordings for a specific meeting"""
    meeting_recordings = await recordings.find(
        {"meeting_id": meeting_id, "is_deleted": {"$ne": True}},
        {"_id": 0}
    ).sort("recorded_at", -1).to_list(length=50)

    return {"meeting_id": meeting_id, "recordings": meeting_recordings, "count": len(meeting_recordings)}


@router.get("/download/{recording_id}")
async def download_recording(
    recording_id: str,
    user: dict = Depends(require_auth)
):
    """Download a cloud recording"""
    record = await recordings.find_one(
        {"recording_id": recording_id, "is_deleted": {"$ne": True}},
        {"_id": 0}
    )
    if not record:
        raise HTTPException(404, "Recording not found")

    if record.get("storage_type") != "cloud":
        raise HTTPException(400, "Recording is stored locally, not in cloud")

    try:
        data, content_type = get_object(record["storage_path"])
    except Exception as e:
        logger.error(f"Cloud download failed: {e}")
        raise HTTPException(500, "Failed to download from cloud")

    return Response(
        content=data,
        media_type=record.get("content_type", content_type),
        headers={
            "Content-Disposition": f'attachment; filename="{record.get("file_name", "recording.webm")}"'
        }
    )


@router.delete("/{recording_id}")
async def delete_recording_metadata(recording_id: str, user: dict = Depends(require_auth)):
    """Soft-delete recording metadata"""
    result = await recordings.update_one(
        {"recording_id": recording_id, "recorded_by": user["user_id"]},
        {"$set": {"is_deleted": True}}
    )

    if result.modified_count == 0:
        raise HTTPException(404, "Recording not found or not authorized")

    return {"success": True, "deleted": recording_id}


@router.get("/transcript/{recording_id}")
async def get_transcript(recording_id: str, user: dict = Depends(require_auth)):
    """Get the transcription for a recording."""
    record = await recordings.find_one(
        {"recording_id": recording_id, "is_deleted": {"$ne": True}},
        {"_id": 0, "transcription": 1, "transcription_status": 1, "transcription_error": 1}
    )
    if not record:
        raise HTTPException(404, "Recording not found")

    return {
        "recording_id": recording_id,
        "status": record.get("transcription_status", "none"),
        "transcription": record.get("transcription"),
        "error": record.get("transcription_error")
    }



class SendNotesRequest(BaseModel):
    recipient_emails: list = []


@router.post("/{recording_id}/notes/generate")
async def generate_recording_notes(recording_id: str, user: dict = Depends(require_auth)):
    """Generate AI meeting notes from a recording's transcript."""
    record = await recordings.find_one(
        {"recording_id": recording_id, "recorded_by": user["user_id"]},
        {"_id": 0, "transcription_status": 1, "transcription": 1, "meeting_title": 1, "meeting_notes": 1}
    )
    if not record:
        raise HTTPException(404, "Recording not found")

    if record.get("transcription_status") != "completed":
        raise HTTPException(400, "Transcript not available for this recording")

    transcript_text = (record.get("transcription") or {}).get("text", "")
    if not transcript_text:
        raise HTTPException(400, "Transcript is empty")

    from services.meeting_notes_service import generate_meeting_notes
    result = await generate_meeting_notes(transcript_text, record.get("meeting_title", "Meeting"))

    if result.get("error"):
        raise HTTPException(500, result["error"])

    await recordings.update_one(
        {"recording_id": recording_id},
        {"$set": {"meeting_notes": result}}
    )

    return {"success": True, "notes": result}


@router.get("/{recording_id}/notes")
async def get_recording_notes(recording_id: str, user: dict = Depends(require_auth)):
    """Get existing meeting notes for a recording."""
    record = await recordings.find_one(
        {"recording_id": recording_id, "recorded_by": user["user_id"]},
        {"_id": 0, "meeting_notes": 1}
    )
    if not record:
        raise HTTPException(404, "Recording not found")
    return {"notes": record.get("meeting_notes")}


@router.post("/{recording_id}/notes/send")
async def send_recording_notes(recording_id: str, data: SendNotesRequest, user: dict = Depends(require_auth)):
    """Send meeting notes to recipients via email record."""
    record = await recordings.find_one(
        {"recording_id": recording_id, "recorded_by": user["user_id"]},
        {"_id": 0, "meeting_notes": 1, "meeting_title": 1}
    )
    if not record or not record.get("meeting_notes"):
        raise HTTPException(400, "No meeting notes to send")

    send_record = {
        "sent_by": user["user_id"],
        "sent_by_name": user.get("name", user.get("email")),
        "sent_to": data.recipient_emails,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "recording_id": recording_id,
        "meeting_title": record.get("meeting_title", "Meeting")
    }
    await db.meeting_notes_sent.insert_one(send_record)

    return {
        "success": True,
        "sent_to": data.recipient_emails,
        "notes_preview": record["meeting_notes"]["notes"][:200] + "..."
    }


@router.get("/stats")
async def get_recording_stats(user: dict = Depends(require_auth)):
    """Get recording statistics for user"""
    pipeline = [
        {"$match": {"recorded_by": user["user_id"], "is_deleted": {"$ne": True}}},
        {"$group": {
            "_id": None,
            "total_recordings": {"$sum": 1},
            "total_duration_seconds": {"$sum": "$duration_seconds"},
            "total_size_bytes": {"$sum": "$file_size_bytes"},
            "cloud_count": {"$sum": {"$cond": [{"$eq": ["$storage_type", "cloud"]}, 1, 0]}},
            "local_count": {"$sum": {"$cond": [{"$eq": ["$storage_type", "browser_local"]}, 1, 0]}}
        }}
    ]

    result = await recordings.aggregate(pipeline).to_list(length=1)

    if result:
        stats = result[0]
        stats.pop("_id", None)
        return stats

    return {
        "total_recordings": 0,
        "total_duration_seconds": 0,
        "total_size_bytes": 0,
        "cloud_count": 0,
        "local_count": 0
    }
