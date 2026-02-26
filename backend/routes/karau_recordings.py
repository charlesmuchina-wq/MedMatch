"""
AI KARAU Meeting - Recordings API Routes
Browser-side recordings metadata and retrieval
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import os
import uuid

from motor.motor_asyncio import AsyncIOMotorClient
from routes.auth import get_current_user, require_auth

router = APIRouter(prefix="/karau-meet/recordings", tags=["AI KARAU Recordings"])

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "medmatch")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
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
        "storage_type": "browser_local",  # Indicates saved to user's local device
        "status": "completed"
    }
    
    await recordings.insert_one(recording_doc)
    recording_doc.pop("_id", None)
    
    return {
        "success": True,
        "recording": recording_doc
    }


@router.get("/")
async def get_user_recordings(
    user: dict = Depends(require_auth),
    limit: int = 50,
    skip: int = 0
):
    """Get all recordings for the current user"""
    
    
    cursor = recordings.find(
        {"recorded_by": user["user_id"]},
        {"_id": 0}
    ).sort("recorded_at", -1).skip(skip).limit(limit)
    
    user_recordings = await cursor.to_list(length=limit)
    total = await recordings.count_documents({"recorded_by": user["user_id"]})
    
    return {
        "recordings": user_recordings,
        "total": total,
        "limit": limit,
        "skip": skip
    }


@router.get("/meeting/{meeting_id}")
async def get_meeting_recordings(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Get all recordings for a specific meeting"""
    
    
    meeting_recordings = await recordings.find(
        {"meeting_id": meeting_id},
        {"_id": 0}
    ).sort("recorded_at", -1).to_list(length=50)
    
    return {
        "meeting_id": meeting_id,
        "recordings": meeting_recordings,
        "count": len(meeting_recordings)
    }


@router.delete("/{recording_id}")
async def delete_recording_metadata(
    recording_id: str,
    user: dict = Depends(require_auth)
):
    """Delete recording metadata"""
    
    
    # Only allow deletion of own recordings
    result = await recordings.delete_one({
        "recording_id": recording_id,
        "recorded_by": user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Recording not found or not authorized")
    
    return {"success": True, "deleted": recording_id}


@router.get("/stats")
async def get_recording_stats(
    user: dict = Depends(require_auth)
):
    """Get recording statistics for user"""
    
    
    pipeline = [
        {"$match": {"recorded_by": user["user_id"]}},
        {"$group": {
            "_id": None,
            "total_recordings": {"$sum": 1},
            "total_duration_seconds": {"$sum": "$duration_seconds"},
            "total_size_bytes": {"$sum": "$file_size_bytes"}
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
        "total_size_bytes": 0
    }
