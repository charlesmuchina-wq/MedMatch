"""
Meeting Replay with Director Cuts API
Save director view recommendations as a timeline, then replay meetings
with optimized camera angles — a cinematic experience of past meetings.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import os
import logging

from utils.database import db
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/karau/replay", tags=["Meeting Replay & Director Cuts"])


class DirectorCut(BaseModel):
    timestamp_seconds: float
    view_mode: str  # panoramic, speaker_closeup, conversation
    focus_users: List[str] = []
    active_speaker_count: int = 0
    transition: str = "smooth"  # smooth, cut, dissolve


class SaveReplayRequest(BaseModel):
    meeting_id: str
    title: str
    duration_seconds: float = 0
    director_cuts: List[DirectorCut] = []
    transcript_segments: List[dict] = []  # [{"ts": 0, "speaker": "x", "text": "..."}]
    key_moments: List[dict] = []  # [{"ts": 30, "type": "decision", "label": "..."}]


class GenerateHighlightsRequest(BaseModel):
    meeting_id: str
    style: str = "executive_summary"  # executive_summary, action_items, full_replay


@router.post("/save")
async def save_replay(data: SaveReplayRequest, user=Depends(require_auth)):
    """Save a meeting replay with director cut timeline."""
    now = datetime.now(timezone.utc).isoformat()

    cuts_data = [c.dict() for c in data.director_cuts]

    # Auto-detect key moments from cuts if not provided
    key_moments = data.key_moments or _auto_detect_key_moments(cuts_data, data.transcript_segments)

    replay_doc = {
        "meeting_id": data.meeting_id,
        "title": data.title,
        "duration_seconds": data.duration_seconds,
        "director_cuts": cuts_data,
        "transcript_segments": data.transcript_segments[:500],
        "key_moments": key_moments,
        "cut_count": len(cuts_data),
        "view_distribution": _calculate_view_distribution(cuts_data),
        "saved_by": user["user_id"],
        "saved_at": now,
        "status": "ready"
    }

    await db.meeting_replays.update_one(
        {"meeting_id": data.meeting_id},
        {"$set": replay_doc},
        upsert=True
    )

    return {
        "success": True,
        "meeting_id": data.meeting_id,
        "title": data.title,
        "cut_count": len(cuts_data),
        "key_moments": len(key_moments),
        "duration_seconds": data.duration_seconds,
        "replay_url": f"/karau-meet/replay/{data.meeting_id}"
    }


@router.get("/list")
async def list_replays(user=Depends(require_auth)):
    """List all saved meeting replays."""
    replays = await db.meeting_replays.find(
        {},
        {"_id": 0, "meeting_id": 1, "title": 1, "duration_seconds": 1,
         "cut_count": 1, "key_moments": 1, "saved_at": 1, "status": 1,
         "view_distribution": 1}
    ).sort("saved_at", -1).to_list(50)

    return {"replays": replays}


@router.get("/{meeting_id}")
async def get_replay(meeting_id: str, user=Depends(require_auth)):
    """Get a full meeting replay with director cut timeline."""
    replay = await db.meeting_replays.find_one(
        {"meeting_id": meeting_id}, {"_id": 0}
    )
    if not replay:
        # Try to generate from director recommendations
        replay = await _generate_replay_from_history(meeting_id)
        if not replay:
            raise HTTPException(404, "Replay not found")

    return replay


@router.get("/{meeting_id}/timeline")
async def get_replay_timeline(meeting_id: str, user=Depends(require_auth)):
    """Get just the director cut timeline for playback control."""
    replay = await db.meeting_replays.find_one(
        {"meeting_id": meeting_id},
        {"_id": 0, "director_cuts": 1, "key_moments": 1, "duration_seconds": 1}
    )
    if not replay:
        replay = await _generate_replay_from_history(meeting_id)
        if not replay:
            raise HTTPException(404, "Replay not found")

    return {
        "meeting_id": meeting_id,
        "director_cuts": replay.get("director_cuts", []),
        "key_moments": replay.get("key_moments", []),
        "duration_seconds": replay.get("duration_seconds", 0)
    }


@router.post("/generate-highlights")
async def generate_highlights(data: GenerateHighlightsRequest, user=Depends(require_auth)):
    """AI-generate a highlights reel from a meeting replay."""
    replay = await db.meeting_replays.find_one(
        {"meeting_id": data.meeting_id}, {"_id": 0}
    )
    if not replay:
        replay = await _generate_replay_from_history(data.meeting_id)
        if not replay:
            raise HTTPException(404, "No replay data found for this meeting")

    cuts = replay.get("director_cuts", [])
    transcript = replay.get("transcript_segments", [])
    key_moments = replay.get("key_moments", [])
    duration = replay.get("duration_seconds", 0)

    # Generate AI highlights based on style
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise Exception("LLM key not configured")

        transcript_text = "\n".join([
            f"[{s.get('ts', 0):.0f}s] {s.get('speaker', '?')}: {s.get('text', '')}"
            for s in transcript[:100]
        ])

        moments_text = "\n".join([
            f"[{m.get('ts', 0):.0f}s] {m.get('type', '?')}: {m.get('label', '')}"
            for m in key_moments
        ])

        style_prompts = {
            "executive_summary": "Create a concise executive summary with the 3-5 most important moments. Include timestamps for each highlight.",
            "action_items": "Extract all action items, decisions, and follow-ups with timestamps and assigned owners.",
            "full_replay": "Create a detailed scene-by-scene breakdown of the meeting, noting camera angle changes and key discussion points."
        }

        chat = LlmChat(
            api_key=api_key,
            session_id=f"replay-highlights-{data.meeting_id}",
            system_message=f"""You are an AI Meeting Director creating a highlights reel for a {duration:.0f}-second meeting.
The meeting had {len(cuts)} director cuts (camera angle changes) and {len(key_moments)} key moments.
{style_prompts.get(data.style, style_prompts['executive_summary'])}

Transcript:
{transcript_text[:3000]}

Key Moments:
{moments_text}

Format your response as a structured highlights reel with timestamps."""
        )

        response = await chat.send_message(UserMessage(text="Generate the highlights reel."))
        highlights_text = response if isinstance(response, str) else str(response)

    except Exception as e:
        logger.error(f"Highlights generation error: {e}")
        highlights_text = _generate_fallback_highlights(replay, data.style)

    # Save highlights
    await db.meeting_highlights.update_one(
        {"meeting_id": data.meeting_id, "style": data.style},
        {"$set": {
            "meeting_id": data.meeting_id,
            "style": data.style,
            "highlights": highlights_text,
            "key_moments": key_moments,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )

    return {
        "meeting_id": data.meeting_id,
        "style": data.style,
        "highlights": highlights_text,
        "key_moments": key_moments,
        "cut_count": len(cuts)
    }


@router.get("/{meeting_id}/highlights")
async def get_highlights(meeting_id: str, style: str = "executive_summary", user=Depends(require_auth)):
    """Get previously generated highlights."""
    hl = await db.meeting_highlights.find_one(
        {"meeting_id": meeting_id, "style": style}, {"_id": 0}
    )
    if not hl:
        raise HTTPException(404, "Highlights not generated yet")
    return hl


@router.delete("/{meeting_id}")
async def delete_replay(meeting_id: str, user=Depends(require_auth)):
    """Delete a meeting replay."""
    await db.meeting_replays.delete_one({"meeting_id": meeting_id})
    await db.meeting_highlights.delete_many({"meeting_id": meeting_id})
    return {"success": True, "deleted": meeting_id}


def _calculate_view_distribution(cuts: list) -> dict:
    """Calculate percentage distribution of view modes."""
    dist = {}
    for c in cuts:
        mode = c.get("view_mode", "panoramic")
        dist[mode] = dist.get(mode, 0) + 1
    total = max(len(cuts), 1)
    return {k: round(v / total * 100, 1) for k, v in dist.items()}


def _auto_detect_key_moments(cuts: list, transcript: list) -> list:
    """Auto-detect key moments from director cuts and transcript."""
    moments = []

    # Detect speaker changes (close-up switches)
    prev_focus = None
    for c in cuts:
        if c.get("view_mode") == "speaker_closeup" and c.get("focus_users"):
            current = c["focus_users"][0] if c["focus_users"] else None
            if current and current != prev_focus:
                moments.append({
                    "ts": c.get("timestamp_seconds", 0),
                    "type": "speaker_change",
                    "label": f"New speaker: {current}"
                })
            prev_focus = current
        elif c.get("view_mode") == "conversation":
            moments.append({
                "ts": c.get("timestamp_seconds", 0),
                "type": "discussion",
                "label": "Active dialogue between participants"
            })

    # Detect long panoramic segments (potential intro/wrap-up)
    if cuts and cuts[0].get("view_mode") == "panoramic":
        moments.insert(0, {"ts": 0, "type": "intro", "label": "Meeting opening"})

    return moments[:20]


async def _generate_replay_from_history(meeting_id: str) -> dict:
    """Generate a replay from stored director recommendations."""
    recs = await db.director_recommendations.find(
        {"meeting_id": meeting_id}, {"_id": 0}
    ).sort("timestamp", 1).to_list(200)

    if not recs:
        # Return simulated demo replay
        return _generate_demo_replay(meeting_id)

    cuts = []
    for i, r in enumerate(recs):
        cuts.append({
            "timestamp_seconds": i * 3.0,
            "view_mode": r.get("recommended_view", "panoramic"),
            "focus_users": r.get("focus_users", []),
            "active_speaker_count": r.get("active_speaker_count", 0),
            "transition": "smooth"
        })

    return {
        "meeting_id": meeting_id,
        "title": "Auto-Generated Replay",
        "duration_seconds": len(cuts) * 3.0,
        "director_cuts": cuts,
        "transcript_segments": [],
        "key_moments": _auto_detect_key_moments(cuts, []),
        "view_distribution": _calculate_view_distribution(cuts),
        "status": "auto_generated"
    }


def _generate_demo_replay(meeting_id: str) -> dict:
    """Generate a demo replay for showcase purposes."""
    import random
    cuts = []
    speakers = ["Alex Chen", "Sarah Miller", "James Park", "Maria Garcia"]
    transcript = []
    duration = 1800  # 30 min meeting

    t = 0
    while t < duration:
        mode = random.choice(["panoramic", "speaker_closeup", "speaker_closeup", "conversation"])
        focus = []
        if mode == "speaker_closeup":
            focus = [random.choice(speakers)]
        elif mode == "conversation":
            focus = random.sample(speakers, 2)

        segment_len = random.uniform(8, 45)
        cuts.append({
            "timestamp_seconds": round(t, 1),
            "view_mode": mode,
            "focus_users": focus,
            "active_speaker_count": len(focus) if focus else 0,
            "transition": random.choice(["smooth", "cut", "dissolve"])
        })

        if focus:
            transcript.append({
                "ts": round(t, 1),
                "speaker": focus[0],
                "text": f"[Segment at {int(t)}s] Discussion point about the quarterly strategy..."
            })

        t += segment_len

    key_moments = [
        {"ts": 0, "type": "intro", "label": "Meeting started - Welcome & agenda review"},
        {"ts": 120, "type": "presentation", "label": "Q4 results presentation by Alex"},
        {"ts": 480, "type": "discussion", "label": "Budget allocation debate"},
        {"ts": 720, "type": "decision", "label": "Decision: Approved 15% increase for R&D"},
        {"ts": 1080, "type": "action_item", "label": "Action: Sarah to draft revised timeline"},
        {"ts": 1440, "type": "discussion", "label": "Cross-team collaboration planning"},
        {"ts": 1680, "type": "wrap_up", "label": "Next steps and follow-up scheduling"},
    ]

    return {
        "meeting_id": meeting_id,
        "title": "Executive Strategy Review - Director's Cut",
        "duration_seconds": duration,
        "director_cuts": cuts,
        "transcript_segments": transcript,
        "key_moments": key_moments,
        "cut_count": len(cuts),
        "view_distribution": _calculate_view_distribution(cuts),
        "status": "demo"
    }


def _generate_fallback_highlights(replay: dict, style: str) -> str:
    """Generate basic highlights without AI."""
    moments = replay.get("key_moments", [])
    duration = replay.get("duration_seconds", 0)
    cuts = replay.get("director_cuts", [])

    lines = [f"Meeting Duration: {int(duration // 60)} minutes", f"Camera Cuts: {len(cuts)}", ""]
    for m in moments:
        ts = m.get("ts", 0)
        mins = int(ts // 60)
        secs = int(ts % 60)
        lines.append(f"[{mins:02d}:{secs:02d}] {m.get('type', '').title()}: {m.get('label', '')}")

    return "\n".join(lines)
