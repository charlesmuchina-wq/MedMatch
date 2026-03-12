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
import random
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
    """Generate a cinematic demo replay with rich chapters, dialogue, and transitions."""
    speakers = [
        {"name": "Alex Chen", "role": "CEO", "color": "#f43f5e"},
        {"name": "Sarah Miller", "role": "CTO", "color": "#3b82f6"},
        {"name": "James Park", "role": "Head of Design", "color": "#f59e0b"},
        {"name": "Maria Garcia", "role": "VP Product", "color": "#10b981"},
        {"name": "David Kim", "role": "Lead Engineer", "color": "#8b5cf6"},
        {"name": "Emma Wilson", "role": "Data Analyst", "color": "#ec4899"},
    ]
    duration = 1800

    chapters = [
        {"title": "Opening & Welcome", "start": 0, "end": 120, "icon": "intro"},
        {"title": "Q4 Performance Review", "start": 120, "end": 420, "icon": "presentation"},
        {"title": "Product Roadmap 2026", "start": 420, "end": 720, "icon": "discussion"},
        {"title": "Budget & Resources", "start": 720, "end": 1020, "icon": "decision"},
        {"title": "Technical Deep-Dive", "start": 1020, "end": 1320, "icon": "presentation"},
        {"title": "Action Items & Owners", "start": 1320, "end": 1560, "icon": "action_item"},
        {"title": "Open Discussion", "start": 1560, "end": 1700, "icon": "discussion"},
        {"title": "Wrap-Up & Next Steps", "start": 1700, "end": 1800, "icon": "wrap_up"},
    ]

    transcript = [
        {"ts": 5, "speaker": "Alex Chen", "text": "Good morning everyone. Let's get started with our quarterly strategy review.", "energy": 0.6},
        {"ts": 18, "speaker": "Alex Chen", "text": "We have a packed agenda today, so let's dive right in.", "energy": 0.7},
        {"ts": 35, "speaker": "Alex Chen", "text": "First, Sarah will walk us through the Q4 numbers, then we'll discuss the 2026 roadmap.", "energy": 0.65},
        {"ts": 60, "speaker": "Sarah Miller", "text": "Thanks Alex. I'll share my screen with the quarterly dashboard.", "energy": 0.5},
        {"ts": 90, "speaker": "Alex Chen", "text": "Before we begin, any questions on the agenda?", "energy": 0.5},
        {"ts": 105, "speaker": "Maria Garcia", "text": "Can we add 10 minutes for the customer feedback analysis?", "energy": 0.6},
        {"ts": 115, "speaker": "Alex Chen", "text": "Absolutely. Sarah, please go ahead.", "energy": 0.5},
        {"ts": 130, "speaker": "Sarah Miller", "text": "Q4 revenue came in at $4.2M, that's 23% above our target.", "energy": 0.8},
        {"ts": 155, "speaker": "Sarah Miller", "text": "Our user growth accelerated to 18% month-over-month in December.", "energy": 0.85},
        {"ts": 180, "speaker": "Sarah Miller", "text": "The Distance Zero platform specifically drove 40% of new enterprise deals.", "energy": 0.9},
        {"ts": 210, "speaker": "James Park", "text": "That's impressive. The new UI we shipped in November clearly resonated.", "energy": 0.7},
        {"ts": 240, "speaker": "Sarah Miller", "text": "Exactly. Customer satisfaction scores are at an all-time high of 4.8 out of 5.", "energy": 0.75},
        {"ts": 270, "speaker": "David Kim", "text": "On the infrastructure side, we reduced latency by 35% with the edge deployment.", "energy": 0.7},
        {"ts": 300, "speaker": "Emma Wilson", "text": "The data shows our churn rate dropped to 2.1%, lowest in company history.", "energy": 0.65},
        {"ts": 330, "speaker": "Alex Chen", "text": "These are outstanding results. The team should be very proud.", "energy": 0.8},
        {"ts": 360, "speaker": "Maria Garcia", "text": "I want to highlight that enterprise retention is now at 98.5%.", "energy": 0.75},
        {"ts": 390, "speaker": "Sarah Miller", "text": "Wrapping up Q4: we exceeded every KPI. Now let's look forward.", "energy": 0.7},
        {"ts": 430, "speaker": "Maria Garcia", "text": "For the 2026 roadmap, I've identified three strategic pillars.", "energy": 0.8},
        {"ts": 460, "speaker": "Maria Garcia", "text": "Pillar one: Immersive AI - making every meeting feel like you're in the same room.", "energy": 0.85},
        {"ts": 490, "speaker": "Maria Garcia", "text": "Pillar two: Enterprise Scale - supporting 10,000+ concurrent meetings.", "energy": 0.8},
        {"ts": 520, "speaker": "Maria Garcia", "text": "Pillar three: Hardware Integration - our Distance Zero hardware ecosystem.", "energy": 0.9},
        {"ts": 560, "speaker": "James Park", "text": "For the immersive AI pillar, we're designing spatial audio that adapts to room geometry.", "energy": 0.75},
        {"ts": 590, "speaker": "David Kim", "text": "We've prototyped the SLAM integration. The 3D tracking is incredibly precise.", "energy": 0.8},
        {"ts": 620, "speaker": "Sarah Miller", "text": "What's the timeline for the SLAM hardware availability?", "energy": 0.6},
        {"ts": 650, "speaker": "David Kim", "text": "Beta units ship in March. Full production by Q2.", "energy": 0.7},
        {"ts": 680, "speaker": "Alex Chen", "text": "This aligns perfectly with our enterprise launch window.", "energy": 0.75},
        {"ts": 710, "speaker": "Maria Garcia", "text": "Let me transition to the budget discussion.", "energy": 0.6},
        {"ts": 740, "speaker": "Sarah Miller", "text": "We're proposing a 15% increase in R&D spending for 2026.", "energy": 0.8},
        {"ts": 770, "speaker": "Sarah Miller", "text": "The bulk goes to the hardware team and AI infrastructure.", "energy": 0.75},
        {"ts": 800, "speaker": "Alex Chen", "text": "I'm supportive of this. The ROI from Q4 justifies the investment.", "energy": 0.7},
        {"ts": 830, "speaker": "James Park", "text": "We'll need three additional designers for the spatial UI work.", "energy": 0.65},
        {"ts": 860, "speaker": "Emma Wilson", "text": "Based on my analysis, the hardware investment has a 14-month payback period.", "energy": 0.7},
        {"ts": 900, "speaker": "Alex Chen", "text": "Let's vote on the budget proposal.", "energy": 0.8},
        {"ts": 920, "speaker": "Alex Chen", "text": "All in favor? ...That's unanimous. The budget is approved.", "energy": 0.9},
        {"ts": 950, "speaker": "Maria Garcia", "text": "Excellent. I'll send the final allocation breakdown by Friday.", "energy": 0.7},
        {"ts": 980, "speaker": "Sarah Miller", "text": "One more item: we need to decide on the hardware partner selection.", "energy": 0.65},
        {"ts": 1010, "speaker": "Alex Chen", "text": "Good point. David, can you take us through the technical evaluation?", "energy": 0.6},
        {"ts": 1040, "speaker": "David Kim", "text": "We evaluated three SLAM vendors. Vendor A leads in accuracy at sub-centimeter precision.", "energy": 0.85},
        {"ts": 1080, "speaker": "David Kim", "text": "The beamforming array from Vendor B achieves 48dB signal-to-noise ratio.", "energy": 0.8},
        {"ts": 1120, "speaker": "David Kim", "text": "For the 360 camera system, we're recommending the OWL Pro 4K.", "energy": 0.75},
        {"ts": 1160, "speaker": "James Park", "text": "The OWL Pro integrates seamlessly with our spatial audio framework.", "energy": 0.7},
        {"ts": 1200, "speaker": "Sarah Miller", "text": "What about the biometric verification module?", "energy": 0.6},
        {"ts": 1230, "speaker": "David Kim", "text": "We've built our own. It uses visual watermarking and real-time integrity hashing.", "energy": 0.8},
        {"ts": 1260, "speaker": "Emma Wilson", "text": "Our internal testing shows 99.7% deepfake detection accuracy.", "energy": 0.85},
        {"ts": 1290, "speaker": "Alex Chen", "text": "Impressive. Let's formalize the vendor selections.", "energy": 0.7},
        {"ts": 1330, "speaker": "Maria Garcia", "text": "Now for action items. Sarah, you'll own the revised budget timeline.", "energy": 0.7},
        {"ts": 1360, "speaker": "Maria Garcia", "text": "David, finalize the hardware vendor contracts by end of February.", "energy": 0.75},
        {"ts": 1390, "speaker": "Maria Garcia", "text": "James, prepare the spatial UI design spec for review next week.", "energy": 0.7},
        {"ts": 1420, "speaker": "Maria Garcia", "text": "Emma, deliver the full ROI analysis with hardware cost projections.", "energy": 0.65},
        {"ts": 1450, "speaker": "Alex Chen", "text": "I'll handle the board presentation. Any blockers on these items?", "energy": 0.6},
        {"ts": 1480, "speaker": "David Kim", "text": "I need final sign-off on the security audit before vendor contracts.", "energy": 0.65},
        {"ts": 1510, "speaker": "Sarah Miller", "text": "I'll expedite the security review. Should have it by Wednesday.", "energy": 0.6},
        {"ts": 1540, "speaker": "Maria Garcia", "text": "All items assigned. Let's move to open discussion.", "energy": 0.55},
        {"ts": 1570, "speaker": "James Park", "text": "Quick topic: the new meeting replay feature is getting amazing user feedback.", "energy": 0.8},
        {"ts": 1600, "speaker": "Emma Wilson", "text": "Usage data confirms it. Replay views increased 300% since launch.", "energy": 0.85},
        {"ts": 1630, "speaker": "Alex Chen", "text": "That validates our investment in the Director's Cut feature.", "energy": 0.75},
        {"ts": 1660, "speaker": "Sarah Miller", "text": "We should showcase this at the industry conference next month.", "energy": 0.7},
        {"ts": 1690, "speaker": "Alex Chen", "text": "Great idea. I'll add it to the keynote deck.", "energy": 0.65},
        {"ts": 1710, "speaker": "Alex Chen", "text": "Alright, let's wrap up. This was an exceptional quarter for the team.", "energy": 0.7},
        {"ts": 1740, "speaker": "Alex Chen", "text": "We have clear direction for 2026 and the budget to execute.", "energy": 0.75},
        {"ts": 1770, "speaker": "Alex Chen", "text": "Next sync is in two weeks. Thanks everyone for a productive session.", "energy": 0.65},
        {"ts": 1790, "speaker": "Maria Garcia", "text": "Thanks all. Let's make 2026 our best year yet.", "energy": 0.7},
    ]

    cuts = []
    for seg in transcript:
        if seg["ts"] < 35:
            mode = "panoramic"
            focus = []
        elif seg["energy"] > 0.8:
            mode = "speaker_closeup"
            focus = [seg["speaker"]]
        elif any(seg["ts"] >= ch["start"] and seg["ts"] < ch["start"] + 15 for ch in chapters):
            mode = "panoramic"
            focus = []
        else:
            is_dialogue = seg["ts"] > 0 and transcript[max(0, transcript.index(seg) - 1)]["speaker"] != seg["speaker"]
            if is_dialogue:
                prev_speaker = transcript[max(0, transcript.index(seg) - 1)]["speaker"]
                mode = "conversation"
                focus = [seg["speaker"], prev_speaker]
            else:
                mode = "speaker_closeup"
                focus = [seg["speaker"]]

        transition = "dissolve" if mode == "panoramic" else "smooth" if mode == "conversation" else "cut"
        cuts.append({
            "timestamp_seconds": seg["ts"],
            "view_mode": mode,
            "focus_users": focus,
            "active_speaker_count": len(focus),
            "transition": transition,
            "energy": seg.get("energy", 0.5),
        })

    key_moments = [
        {"ts": 0, "type": "intro", "label": "Meeting started - Welcome & agenda review"},
        {"ts": 130, "type": "presentation", "label": "Q4 revenue: $4.2M (23% above target)"},
        {"ts": 180, "type": "presentation", "label": "Distance Zero drove 40% of enterprise deals"},
        {"ts": 300, "type": "speaker_change", "label": "Emma presents churn analysis"},
        {"ts": 430, "type": "presentation", "label": "2026 Roadmap: Three strategic pillars revealed"},
        {"ts": 520, "type": "discussion", "label": "Hardware ecosystem deep-dive begins"},
        {"ts": 590, "type": "discussion", "label": "SLAM integration prototype demo results"},
        {"ts": 720, "type": "decision", "label": "Budget discussion: 15% R&D increase proposed"},
        {"ts": 920, "type": "decision", "label": "Unanimous vote: Budget APPROVED"},
        {"ts": 1040, "type": "presentation", "label": "Technical evaluation: SLAM vendor comparison"},
        {"ts": 1260, "type": "presentation", "label": "Biometric module: 99.7% deepfake detection"},
        {"ts": 1330, "type": "action_item", "label": "Sarah: Revised budget timeline"},
        {"ts": 1360, "type": "action_item", "label": "David: Hardware vendor contracts by Feb"},
        {"ts": 1390, "type": "action_item", "label": "James: Spatial UI design spec"},
        {"ts": 1420, "type": "action_item", "label": "Emma: Full ROI analysis"},
        {"ts": 1570, "type": "discussion", "label": "Replay feature: 300% usage increase"},
        {"ts": 1710, "type": "wrap_up", "label": "Meeting wrap-up and next steps"},
    ]

    waveform = []
    for i in range(0, duration, 2):
        matching = [s for s in transcript if abs(s["ts"] - i) < 15]
        energy = max((s["energy"] for s in matching), default=0.1)
        waveform.append(round(energy + random.uniform(-0.1, 0.1), 2))

    return {
        "meeting_id": meeting_id,
        "title": "Q4 Executive Strategy Review - Director's Cut",
        "duration_seconds": duration,
        "director_cuts": cuts,
        "transcript_segments": transcript,
        "key_moments": key_moments,
        "chapters": chapters,
        "speakers": speakers,
        "waveform": waveform,
        "cut_count": len(cuts),
        "view_distribution": _calculate_view_distribution(cuts),
        "status": "demo",
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


# ═══════════════════════════════════════════════════════════════
# AI CHAPTERS & TRANSCRIPT SEARCH
# ═══════════════════════════════════════════════════════════════

@router.post("/{meeting_id}/generate-chapters")
async def generate_ai_chapters(meeting_id: str, user=Depends(require_auth)):
    """AI-generate searchable chapters from meeting transcript."""
    replay = await db.meeting_replays.find_one({"meeting_id": meeting_id}, {"_id": 0})
    if not replay:
        replay = await _generate_replay_from_history(meeting_id)
        if not replay:
            raise HTTPException(404, "No replay data")

    transcript = replay.get("transcript_segments", [])
    key_moments = replay.get("key_moments", [])
    duration = replay.get("duration_seconds", 0)

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise Exception("LLM key not configured")

        transcript_text = "\n".join([
            f"[{s.get('ts', 0):.0f}s] {s.get('speaker', '?')}: {s.get('text', '')}"
            for s in transcript[:120]
        ])

        chat = LlmChat(
            api_key=api_key,
            session_id=f"chapters-{meeting_id}",
            system_message="You generate meeting chapters from transcripts. Return valid JSON array."
        )
        chat.with_model("openai", "gpt-4o")

        prompt = f"""Analyze this {int(duration // 60)}-minute meeting transcript and generate 4-8 chapters.
Each chapter: {{"title": "...", "start_ts": <seconds>, "end_ts": <seconds>, "summary": "1-2 sentence summary", "type": "intro|discussion|decision|action_item|wrap_up"}}

Transcript:
{transcript_text[:4000]}

Return ONLY a JSON array of chapters, no markdown."""

        response = await chat.send_message(UserMessage(text=prompt))
        resp_text = response if isinstance(response, str) else str(response)

        import json as json_mod
        # Try to parse JSON from response
        try:
            chapters = json_mod.loads(resp_text)
        except json_mod.JSONDecodeError:
            # Extract JSON array from markdown
            import re
            match = re.search(r'\[.*\]', resp_text, re.DOTALL)
            chapters = json_mod.loads(match.group()) if match else []

    except Exception as e:
        logger.error(f"Chapter generation error: {e}")
        # Fallback: generate basic chapters from key_moments
        chapters = []
        for i, m in enumerate(key_moments[:8]):
            chapters.append({
                "title": m.get("label", f"Section {i + 1}"),
                "start_ts": m.get("ts", 0),
                "end_ts": key_moments[i + 1]["ts"] if i + 1 < len(key_moments) else duration,
                "summary": f"{m.get('type', '').title()} section",
                "type": m.get("type", "discussion")
            })

    # Store chapters
    await db.meeting_replays.update_one(
        {"meeting_id": meeting_id},
        {"$set": {"ai_chapters": chapters, "chapters_generated_at": datetime.now(timezone.utc).isoformat()}}
    )

    return {"meeting_id": meeting_id, "chapters": chapters, "count": len(chapters)}


@router.get("/{meeting_id}/search")
async def search_transcript(meeting_id: str, q: str, user=Depends(require_auth)):
    """Search through meeting transcript segments."""
    replay = await db.meeting_replays.find_one({"meeting_id": meeting_id}, {"_id": 0, "transcript_segments": 1})
    if not replay:
        raise HTTPException(404, "Replay not found")

    segments = replay.get("transcript_segments", [])
    q_lower = q.lower()
    results = []
    for seg in segments:
        text = seg.get("text", "")
        if q_lower in text.lower():
            results.append({
                "ts": seg.get("ts", 0),
                "speaker": seg.get("speaker", "Unknown"),
                "text": text,
                "match_start": text.lower().index(q_lower),
            })

    return {"query": q, "results": results, "count": len(results)}
