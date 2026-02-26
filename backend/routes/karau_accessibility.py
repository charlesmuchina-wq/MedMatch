"""
AI KARAU Meeting - Accessibility API Routes
Screen reader support, live captions, accessibility settings
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List

from services.karau_meet.accessibility_service import (
    get_accessibility_settings,
    update_accessibility_settings,
    start_live_captions,
    add_caption,
    get_captions,
    stop_live_captions,
    get_caption_transcript,
    get_keyboard_shortcuts,
    get_aria_labels,
    get_color_palette,
    get_font_settings,
    DEFAULT_ACCESSIBILITY_SETTINGS
)
from routes.auth import get_current_user, require_auth

router = APIRouter(prefix="/karau-meet/accessibility", tags=["AI KARAU Accessibility"])


# ============ ACCESSIBILITY SETTINGS ============

class AccessibilitySettingsUpdate(BaseModel):
    high_contrast: Optional[bool] = None
    large_text: Optional[bool] = None
    font_size: Optional[str] = None  # small, medium, large, x-large
    font_family: Optional[str] = None  # system, dyslexic, monospace
    reduce_motion: Optional[bool] = None
    screen_reader_optimized: Optional[bool] = None
    live_captions_enabled: Optional[bool] = None
    caption_font_size: Optional[str] = None
    caption_background: Optional[str] = None  # dark, light, transparent
    caption_position: Optional[str] = None  # top, bottom
    keyboard_shortcuts_enabled: Optional[bool] = None
    focus_indicators: Optional[bool] = None
    audio_descriptions: Optional[bool] = None
    color_blind_mode: Optional[str] = None  # none, protanopia, deuteranopia, tritanopia


@router.get("/settings")
async def get_user_accessibility_settings(
    user: dict = Depends(require_auth)
):
    """Get accessibility settings for current user"""
    
    settings = await get_accessibility_settings(user["user_id"])
    return settings


@router.put("/settings")
async def update_user_accessibility_settings(
    request: AccessibilitySettingsUpdate,
    user: dict = Depends(require_auth)
):
    """Update accessibility settings"""
    
    updates = {k: v for k, v in request.dict().items() if v is not None}
    settings = await update_accessibility_settings(user["user_id"], updates)
    return settings


@router.get("/settings/defaults")
async def get_default_settings():
    """Get default accessibility settings"""
    
    return DEFAULT_ACCESSIBILITY_SETTINGS


# ============ LIVE CAPTIONS ============

class StartCaptionsRequest(BaseModel):
    meeting_id: str
    language: str = "en"


class AddCaptionRequest(BaseModel):
    speaker_id: str
    speaker_name: str
    text: str
    timestamp: Optional[str] = None
    confidence: float = 1.0


@router.post("/captions/start")
async def start_meeting_captions(
    request: StartCaptionsRequest,
    user: dict = Depends(require_auth)
):
    """Start live captions for a meeting"""
    
    result = await start_live_captions(request.meeting_id, request.language)
    return result


@router.post("/captions/{meeting_id}/add")
async def add_meeting_caption(
    meeting_id: str,
    request: AddCaptionRequest,
    user: dict = Depends(require_auth)
):
    """Add a caption entry"""
    
    caption = await add_caption(
        meeting_id=meeting_id,
        speaker_id=request.speaker_id,
        speaker_name=request.speaker_name,
        text=request.text,
        timestamp=request.timestamp,
        confidence=request.confidence
    )
    return caption


@router.get("/captions/{meeting_id}")
async def get_meeting_captions(
    meeting_id: str,
    since: Optional[str] = None,
    limit: int = 100,
    user: dict = Depends(require_auth)
):
    """Get captions for a meeting"""
    
    captions = await get_captions(meeting_id, since, limit)
    return {"meeting_id": meeting_id, "captions": captions, "count": len(captions)}


@router.post("/captions/{meeting_id}/stop")
async def stop_meeting_captions(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Stop live captions"""
    
    result = await stop_live_captions(meeting_id)
    return result


@router.get("/captions/{meeting_id}/transcript")
async def get_meeting_transcript(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Get full transcript from captions"""
    
    transcript = await get_caption_transcript(meeting_id)
    return transcript


# ============ KEYBOARD SHORTCUTS ============

@router.get("/keyboard-shortcuts")
async def get_shortcuts():
    """Get all keyboard shortcuts"""
    
    return {"shortcuts": get_keyboard_shortcuts()}


# ============ ARIA LABELS ============

@router.get("/aria-labels")
async def get_aria():
    """Get ARIA labels for screen readers"""
    
    return {"labels": get_aria_labels()}


# ============ COLOR BLIND SUPPORT ============

@router.get("/color-palette/{mode}")
async def get_color_blind_palette(mode: str):
    """Get color palette for color blind mode"""
    
    valid_modes = ["none", "protanopia", "deuteranopia", "tritanopia"]
    if mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Valid modes: {valid_modes}")
    
    return {"mode": mode, "palette": get_color_palette(mode)}


@router.get("/color-palettes")
async def get_all_color_palettes():
    """Get all color blind palettes"""
    
    return {
        "palettes": {
            mode: get_color_palette(mode) 
            for mode in ["none", "protanopia", "deuteranopia", "tritanopia"]
        }
    }


# ============ FONT SETTINGS ============

@router.get("/fonts")
async def get_fonts(
    size: str = "medium",
    family: str = "system"
):
    """Get font settings"""
    
    return get_font_settings(size, family)


@router.get("/fonts/options")
async def get_font_options():
    """Get available font options"""
    
    return {
        "sizes": ["small", "medium", "large", "x-large"],
        "families": ["system", "dyslexic", "monospace"]
    }
