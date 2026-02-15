"""
AI KARAU Meeting - AI Transcription & Summary API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List

from services.karau_meet.ai_transcription_service import (
    transcribe_audio,
    get_meeting_transcript,
    generate_meeting_summary,
    get_meeting_summary,
    extract_action_items,
    get_action_items,
    update_action_item_status
)
from routes.auth import get_current_user

router = APIRouter(prefix="/karau-meet/ai", tags=["AI KARAU AI Features"])


# ============ TRANSCRIPTION ============

@router.post("/transcribe")
async def transcribe_audio_endpoint(
    audio_file: UploadFile = File(...),
    meeting_id: str = Form(...),
    speaker_name: str = Form(default="Unknown"),
    language: str = Form(default="en"),
    user: dict = Depends(get_current_user)
):
    """
    Transcribe audio using OpenAI Whisper
    
    - Upload audio file (mp3, wav, webm, etc.)
    - Returns transcribed text with timestamps
    """
    
    # Validate file type
    allowed_types = ["audio/webm", "audio/mp3", "audio/wav", "audio/mpeg", "audio/mp4", "audio/m4a"]
    content_type = audio_file.content_type or ""
    
    # Read audio data
    audio_data = await audio_file.read()
    
    if len(audio_data) > 25 * 1024 * 1024:  # 25MB limit
        raise HTTPException(status_code=400, detail="Audio file too large. Max 25MB.")
    
    # Get file extension
    filename = audio_file.filename or "audio.webm"
    file_format = filename.split(".")[-1] if "." in filename else "webm"
    
    result = await transcribe_audio(
        audio_data=audio_data,
        meeting_id=meeting_id,
        speaker_id=user["user_id"],
        speaker_name=speaker_name or user.get("name", "Unknown"),
        language=language,
        file_format=file_format
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Transcription failed"))
    
    return result


@router.get("/transcript/{meeting_id}")
async def get_transcript_endpoint(
    meeting_id: str,
    user: dict = Depends(get_current_user)
):
    """Get full transcript for a meeting"""
    
    transcript = await get_meeting_transcript(meeting_id)
    return transcript


# ============ MEETING SUMMARIES ============

class GenerateSummaryRequest(BaseModel):
    meeting_title: str = "Meeting"
    participants: Optional[List[str]] = None


@router.post("/summary/{meeting_id}")
async def generate_summary_endpoint(
    meeting_id: str,
    request: GenerateSummaryRequest,
    user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered meeting summary using GPT-5.2
    
    - Analyzes meeting transcript
    - Generates summary, key points, decisions, action items
    """
    
    result = await generate_meeting_summary(
        meeting_id=meeting_id,
        meeting_title=request.meeting_title,
        participants=request.participants
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Summary generation failed"))
    
    return result


@router.get("/summary/{meeting_id}")
async def get_summary_endpoint(
    meeting_id: str,
    user: dict = Depends(get_current_user)
):
    """Get summary for a meeting"""
    
    summary = await get_meeting_summary(meeting_id)
    
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found. Generate one first.")
    
    return summary


# ============ ACTION ITEMS ============

@router.post("/action-items/extract/{meeting_id}")
async def extract_action_items_endpoint(
    meeting_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Extract action items from meeting transcript using GPT-5.2
    
    - Identifies tasks, assignees, deadlines
    - Stores action items for tracking
    """
    
    result = await extract_action_items(meeting_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Extraction failed"))
    
    return result


@router.get("/action-items/{meeting_id}")
async def get_action_items_endpoint(
    meeting_id: str,
    user: dict = Depends(get_current_user)
):
    """Get action items for a meeting"""
    
    items = await get_action_items(meeting_id)
    return {"meeting_id": meeting_id, "action_items": items, "count": len(items)}


class UpdateActionItemRequest(BaseModel):
    status: str  # pending, in_progress, completed, cancelled


@router.put("/action-items/{action_id}/status")
async def update_action_item_endpoint(
    action_id: str,
    request: UpdateActionItemRequest,
    user: dict = Depends(get_current_user)
):
    """Update action item status"""
    
    result = await update_action_item_status(
        action_id=action_id,
        status=request.status,
        user_id=user["user_id"]
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Update failed"))
    
    return result
