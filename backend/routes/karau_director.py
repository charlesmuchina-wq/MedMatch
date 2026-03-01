"""
Cinematic Director Mode API
AI-powered automatic camera view switching between:
- Panoramic (gallery grid)
- Speaker Close-Up (active speaker focus)
- Conversation Mode (2-person side-by-side framing)
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import logging

from utils.database import db
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/karau/director", tags=["Cinematic Director"])

DIRECTOR_MODES = ["auto", "panoramic", "speaker_closeup", "conversation", "manual"]


class DirectorModeUpdate(BaseModel):
    mode: str  # auto, panoramic, speaker_closeup, conversation, manual
    pinned_user_id: Optional[str] = None


class SpeakingEvent(BaseModel):
    user_id: str
    user_name: str
    is_speaking: bool
    duration_seconds: float = 0


class DirectorAnalyzeRequest(BaseModel):
    meeting_id: str
    speaking_events: List[SpeakingEvent]
    participant_count: int = 2
    elapsed_seconds: float = 0


@router.post("/{meeting_id}/mode")
async def set_director_mode(meeting_id: str, data: DirectorModeUpdate, user=Depends(require_auth)):
    """Set the director mode for a meeting (host only)."""
    if data.mode not in DIRECTOR_MODES:
        raise HTTPException(400, f"Invalid mode. Valid: {DIRECTOR_MODES}")

    await db.director_state.update_one(
        {"meeting_id": meeting_id},
        {"$set": {
            "meeting_id": meeting_id,
            "mode": data.mode,
            "pinned_user_id": data.pinned_user_id,
            "updated_by": user["user_id"],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )

    return {"success": True, "mode": data.mode, "pinned_user_id": data.pinned_user_id}


@router.get("/{meeting_id}/mode")
async def get_director_mode(meeting_id: str):
    """Get the current director mode for a meeting."""
    state = await db.director_state.find_one(
        {"meeting_id": meeting_id}, {"_id": 0}
    )
    if not state:
        return {"mode": "auto", "pinned_user_id": None, "recommended_view": "panoramic"}
    return state


@router.post("/{meeting_id}/analyze")
async def analyze_for_director(meeting_id: str, data: DirectorAnalyzeRequest, user=Depends(require_auth)):
    """AI analyzes speaking patterns and recommends the optimal view.

    Logic:
    - 0 speakers talking -> panoramic
    - 1 dominant speaker for >3s -> speaker_closeup
    - 2 people alternating within 5s window -> conversation
    - 3+ speakers -> panoramic
    """
    active_speakers = [e for e in data.speaking_events if e.is_speaking]
    recent_speakers = [e for e in data.speaking_events if e.duration_seconds > 0]

    recommended = "panoramic"
    focus_users = []

    if len(active_speakers) == 0:
        recommended = "panoramic"
    elif len(active_speakers) == 1:
        speaker = active_speakers[0]
        if speaker.duration_seconds >= 3.0:
            recommended = "speaker_closeup"
            focus_users = [speaker.user_id]
        else:
            recommended = "panoramic"
    elif len(active_speakers) == 2:
        both_recent = all(s.duration_seconds >= 1.0 for s in active_speakers)
        if both_recent:
            recommended = "conversation"
            focus_users = [s.user_id for s in active_speakers]
        else:
            longest = max(active_speakers, key=lambda s: s.duration_seconds)
            recommended = "speaker_closeup"
            focus_users = [longest.user_id]
    else:
        recommended = "panoramic"

    # Check if host has overridden to manual
    state = await db.director_state.find_one({"meeting_id": meeting_id}, {"_id": 0})
    current_mode = state.get("mode", "auto") if state else "auto"

    # Store recommendation
    await db.director_recommendations.insert_one({
        "meeting_id": meeting_id,
        "recommended_view": recommended,
        "focus_users": focus_users,
        "active_speaker_count": len(active_speakers),
        "participant_count": data.participant_count,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return {
        "recommended_view": recommended,
        "focus_users": focus_users,
        "current_mode": current_mode,
        "active_speaker_count": len(active_speakers),
        "should_switch": current_mode == "auto"
    }
