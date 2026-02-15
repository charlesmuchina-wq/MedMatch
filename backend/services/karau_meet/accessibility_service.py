"""
AI KARAU Meeting - Accessibility Service
Screen reader support, adjustable fonts, live captions
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "medmatch")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
accessibility_settings = db.karau_accessibility_settings
live_captions = db.karau_live_captions


# Default accessibility settings
DEFAULT_ACCESSIBILITY_SETTINGS = {
    "high_contrast": False,
    "large_text": False,
    "font_size": "medium",  # small, medium, large, x-large
    "font_family": "system",  # system, dyslexic, monospace
    "reduce_motion": False,
    "screen_reader_optimized": False,
    "live_captions_enabled": True,
    "caption_font_size": "medium",
    "caption_background": "dark",  # dark, light, transparent
    "caption_position": "bottom",  # top, bottom
    "keyboard_shortcuts_enabled": True,
    "focus_indicators": True,
    "audio_descriptions": False,
    "color_blind_mode": "none"  # none, protanopia, deuteranopia, tritanopia
}


async def get_accessibility_settings(user_id: str) -> Dict:
    """Get accessibility settings for a user"""
    
    settings = await accessibility_settings.find_one(
        {"user_id": user_id},
        {"_id": 0}
    )
    
    if not settings:
        return {**DEFAULT_ACCESSIBILITY_SETTINGS, "user_id": user_id}
    
    # Merge with defaults for any missing keys
    for key, value in DEFAULT_ACCESSIBILITY_SETTINGS.items():
        if key not in settings:
            settings[key] = value
    
    return settings


async def update_accessibility_settings(
    user_id: str,
    updates: Dict
) -> Dict:
    """Update accessibility settings"""
    
    allowed_keys = set(DEFAULT_ACCESSIBILITY_SETTINGS.keys())
    filtered_updates = {k: v for k, v in updates.items() if k in allowed_keys}
    
    filtered_updates["user_id"] = user_id
    filtered_updates["updated_at"] = datetime.utcnow().isoformat()
    
    await accessibility_settings.update_one(
        {"user_id": user_id},
        {"$set": filtered_updates},
        upsert=True
    )
    
    return await get_accessibility_settings(user_id)


# ============ LIVE CAPTIONS ============

async def start_live_captions(meeting_id: str, language: str = "en") -> Dict:
    """Start live captions for a meeting"""
    
    caption_session = {
        "meeting_id": meeting_id,
        "language": language,
        "started_at": datetime.utcnow().isoformat(),
        "status": "active",
        "captions": []
    }
    
    await live_captions.update_one(
        {"meeting_id": meeting_id},
        {"$set": caption_session},
        upsert=True
    )
    
    return {"success": True, "meeting_id": meeting_id, "language": language}


async def add_caption(
    meeting_id: str,
    speaker_id: str,
    speaker_name: str,
    text: str,
    timestamp: str = None,
    confidence: float = 1.0
) -> Dict:
    """Add a caption entry"""
    
    caption = {
        "caption_id": str(uuid.uuid4())[:8],
        "speaker_id": speaker_id,
        "speaker_name": speaker_name,
        "text": text,
        "timestamp": timestamp or datetime.utcnow().isoformat(),
        "confidence": confidence
    }
    
    await live_captions.update_one(
        {"meeting_id": meeting_id},
        {"$push": {"captions": caption}}
    )
    
    return caption


async def get_captions(
    meeting_id: str,
    since: str = None,
    limit: int = 100
) -> List[Dict]:
    """Get captions for a meeting"""
    
    session = await live_captions.find_one(
        {"meeting_id": meeting_id},
        {"_id": 0}
    )
    
    if not session:
        return []
    
    captions = session.get("captions", [])
    
    if since:
        captions = [c for c in captions if c.get("timestamp", "") > since]
    
    return captions[-limit:]


async def stop_live_captions(meeting_id: str) -> Dict:
    """Stop live captions and finalize"""
    
    await live_captions.update_one(
        {"meeting_id": meeting_id},
        {"$set": {
            "status": "completed",
            "ended_at": datetime.utcnow().isoformat()
        }}
    )
    
    return {"success": True, "meeting_id": meeting_id}


async def get_caption_transcript(meeting_id: str) -> Dict:
    """Get full transcript from captions"""
    
    session = await live_captions.find_one(
        {"meeting_id": meeting_id},
        {"_id": 0}
    )
    
    if not session:
        return {"transcript": "", "speakers": []}
    
    captions = session.get("captions", [])
    
    # Build transcript
    transcript_lines = []
    speakers = set()
    
    for caption in captions:
        speaker = caption.get("speaker_name", "Unknown")
        text = caption.get("text", "")
        speakers.add(speaker)
        transcript_lines.append(f"{speaker}: {text}")
    
    return {
        "meeting_id": meeting_id,
        "transcript": "\n".join(transcript_lines),
        "speakers": list(speakers),
        "caption_count": len(captions),
        "language": session.get("language", "en")
    }


# ============ KEYBOARD SHORTCUTS ============

KEYBOARD_SHORTCUTS = {
    "toggle_mute": {"key": "M", "ctrl": True, "description": "Toggle microphone"},
    "toggle_video": {"key": "V", "ctrl": True, "description": "Toggle camera"},
    "toggle_screen_share": {"key": "S", "ctrl": True, "shift": True, "description": "Toggle screen share"},
    "raise_hand": {"key": "H", "ctrl": True, "description": "Raise/lower hand"},
    "toggle_chat": {"key": "C", "ctrl": True, "description": "Toggle chat panel"},
    "toggle_participants": {"key": "P", "ctrl": True, "description": "Toggle participants panel"},
    "toggle_captions": {"key": "L", "ctrl": True, "description": "Toggle live captions"},
    "leave_meeting": {"key": "Q", "ctrl": True, "shift": True, "description": "Leave meeting"},
    "toggle_fullscreen": {"key": "F", "ctrl": True, "description": "Toggle fullscreen"},
    "focus_next": {"key": "Tab", "description": "Focus next element"},
    "focus_prev": {"key": "Tab", "shift": True, "description": "Focus previous element"}
}


def get_keyboard_shortcuts() -> Dict:
    """Get all keyboard shortcuts"""
    return KEYBOARD_SHORTCUTS


# ============ ARIA LABELS & SCREEN READER SUPPORT ============

ARIA_LABELS = {
    "meeting_room": "Meeting room main content area",
    "video_grid": "Video participants grid",
    "local_video": "Your video feed",
    "remote_video": "Participant video feed",
    "mute_button": "Toggle microphone, currently {state}",
    "video_button": "Toggle camera, currently {state}",
    "screen_share_button": "Toggle screen sharing, currently {state}",
    "chat_panel": "Chat messages panel",
    "participants_panel": "Meeting participants panel",
    "hand_raise_button": "Raise or lower hand, currently {state}",
    "leave_button": "Leave meeting",
    "settings_button": "Open meeting settings",
    "captions_display": "Live captions display area"
}


def get_aria_labels() -> Dict:
    """Get ARIA labels for screen readers"""
    return ARIA_LABELS


# ============ COLOR BLIND MODES ============

COLOR_BLIND_PALETTES = {
    "none": {
        "primary": "#14b8a6",
        "secondary": "#8b5cf6",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#3b82f6"
    },
    "protanopia": {
        "primary": "#0ea5e9",
        "secondary": "#a855f7",
        "success": "#14b8a6",
        "warning": "#fbbf24",
        "error": "#f97316",
        "info": "#6366f1"
    },
    "deuteranopia": {
        "primary": "#06b6d4",
        "secondary": "#a855f7",
        "success": "#0891b2",
        "warning": "#f59e0b",
        "error": "#ea580c",
        "info": "#8b5cf6"
    },
    "tritanopia": {
        "primary": "#ec4899",
        "secondary": "#f43f5e",
        "success": "#10b981",
        "warning": "#f97316",
        "error": "#dc2626",
        "info": "#8b5cf6"
    }
}


def get_color_palette(mode: str = "none") -> Dict:
    """Get color palette for color blind mode"""
    return COLOR_BLIND_PALETTES.get(mode, COLOR_BLIND_PALETTES["none"])


# ============ FONT SETTINGS ============

FONT_SIZES = {
    "small": {
        "base": "14px",
        "heading": "18px",
        "caption": "12px"
    },
    "medium": {
        "base": "16px",
        "heading": "20px",
        "caption": "14px"
    },
    "large": {
        "base": "18px",
        "heading": "24px",
        "caption": "16px"
    },
    "x-large": {
        "base": "20px",
        "heading": "28px",
        "caption": "18px"
    }
}

FONT_FAMILIES = {
    "system": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "dyslexic": "OpenDyslexic, Arial, sans-serif",
    "monospace": "'Fira Code', 'Courier New', monospace"
}


def get_font_settings(size: str = "medium", family: str = "system") -> Dict:
    """Get font settings"""
    return {
        "sizes": FONT_SIZES.get(size, FONT_SIZES["medium"]),
        "family": FONT_FAMILIES.get(family, FONT_FAMILIES["system"])
    }
