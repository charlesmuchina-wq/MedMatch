"""
D-ID Avatar Video API Routes

Endpoints for creating AI-powered talking head videos.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Optional
from pydantic import BaseModel

from services.did_avatar_service import did_service

router = APIRouter(prefix="/avatar", tags=["AI Avatar"])


class CreateVideoRequest(BaseModel):
    script: str
    presenter_id: Optional[str] = None
    source_url: Optional[str] = None
    voice_id: str = "en-US-JennyNeural"
    background_color: str = "#1a1a2e"
    title: str = "MedMatch Video"


@router.get("/status")
async def get_avatar_status():
    """Check D-ID service status and credits."""
    credits = await did_service.get_credits()
    return {
        "service": "D-ID AI Avatar",
        "status": "active" if did_service.api_key else "mock_mode",
        "credits": credits
    }


@router.get("/presenters")
async def get_presenters():
    """Get available D-ID presenters."""
    presenters = await did_service.get_presenters()
    return {"presenters": presenters}


@router.get("/voices")
async def get_voices():
    """Get available text-to-speech voices."""
    voices = await did_service.get_voices()
    return {"voices": voices}


@router.post("/create")
async def create_avatar_video(request: CreateVideoRequest):
    """
    Create an AI talking head video.
    
    - **script**: The text for the avatar to speak
    - **presenter_id**: Optional D-ID presenter ID
    - **source_url**: Optional custom image URL for the avatar (must be a clear portrait)
    - **voice_id**: Microsoft Azure voice ID (default: en-US-JennyNeural)
    - **background_color**: Hex color for background (default: #1a1a2e)
    - **title**: Video title for storage
    """
    result = await did_service.create_talk_video(
        script=request.script,
        presenter_id=request.presenter_id,
        source_url=request.source_url,
        voice_id=request.voice_id,
        background_color=request.background_color,
        title=request.title
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Video creation failed"))
    
    return result


@router.post("/create/medmatch-overview")
async def create_medmatch_overview(duration: str = "60s"):
    """
    Create a MedMatch overview video with predefined scripts.
    
    - **duration**: "15s", "30s", or "60s"
    """
    if duration not in ["15s", "30s", "60s"]:
        raise HTTPException(status_code=400, detail="Duration must be 15s, 30s, or 60s")
    
    result = await did_service.create_medmatch_overview(duration)
    return result


@router.post("/create/custom")
async def create_custom_video(
    script: str = Body(..., description="The text script for the avatar to speak"),
    voice: str = Body("en-US-JennyNeural", description="Voice ID"),
    language: str = Body("en-US", description="Language code")
):
    """Create a custom avatar video with any script."""
    
    # Map language to appropriate voice if not specified
    language_voices = {
        "en-US": "en-US-JennyNeural",
        "en-GB": "en-GB-SoniaNeural",
        "es-ES": "es-ES-ElviraNeural",
        "fr-FR": "fr-FR-DeniseNeural",
        "de-DE": "de-DE-KatjaNeural",
        "ja-JP": "ja-JP-NanamiNeural",
        "zh-CN": "zh-CN-XiaoxiaoNeural",
    }
    
    voice_id = language_voices.get(language, voice)
    
    result = await did_service.create_talk_video(
        script=script,
        voice_id=voice_id,
        title=f"Custom Video ({language})"
    )
    
    return result
