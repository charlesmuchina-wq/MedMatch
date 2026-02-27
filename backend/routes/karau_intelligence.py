"""
AI Meeting Intelligence Routes
Real-time transcription processing, AI summaries, and action item extraction
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/karau-meet/ai", tags=["KARAU AI Intelligence"])

# --- Models ---

class TranscriptSegment(BaseModel):
    speaker: str = "Unknown"
    text: str
    timestamp: Optional[str] = None

class SummarizeRequest(BaseModel):
    meeting_id: str
    meeting_title: Optional[str] = "Meeting"
    transcript: List[TranscriptSegment]

class SummaryResponse(BaseModel):
    summary: str
    action_items: List[str]
    key_decisions: List[str]
    topics_discussed: List[str]
    meeting_id: str
    generated_at: str

class PollCreateRequest(BaseModel):
    meeting_id: str
    question: str
    options: List[str]
    allow_multiple: bool = False

class PollVoteRequest(BaseModel):
    option_index: int


# --- AI Summary Endpoint ---

@router.post("/summarize", response_model=SummaryResponse)
async def summarize_meeting(req: SummarizeRequest, request: Request):
    """Generate AI-powered meeting summary with action items from transcript"""
    if not req.transcript or len(req.transcript) == 0:
        raise HTTPException(status_code=400, detail="No transcript provided")

    # Build transcript text
    transcript_text = "\n".join(
        [f"[{seg.speaker}]: {seg.text}" for seg in req.transcript]
    )

    # Truncate if very long (keep last ~4000 words for context window)
    words = transcript_text.split()
    if len(words) > 4000:
        transcript_text = " ".join(words[-4000:])

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="LLM key not configured")

        chat = LlmChat(
            api_key=api_key,
            session_id=f"meeting-summary-{req.meeting_id}-{datetime.now(timezone.utc).isoformat()}",
            system_message="""You are a professional meeting assistant. Analyze meeting transcripts and produce structured summaries.
Always respond in this exact JSON format:
{
  "summary": "A concise 2-4 paragraph summary of the meeting discussion",
  "action_items": ["Action item 1 - assigned to Person", "Action item 2"],
  "key_decisions": ["Decision 1", "Decision 2"],
  "topics_discussed": ["Topic 1", "Topic 2"]
}
If the transcript is too short or unclear, still provide your best analysis. Always return valid JSON."""
        )

        user_message = UserMessage(
            text=f"Meeting: {req.meeting_title}\n\nTranscript:\n{transcript_text}\n\nPlease provide a structured summary."
        )

        response = await chat.send_message(user_message)
        
        # Parse the LLM response
        import json
        try:
            # Try to extract JSON from the response
            response_text = response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            parsed = json.loads(response_text.strip())
            summary = parsed.get("summary", response_text)
            action_items = parsed.get("action_items", [])
            key_decisions = parsed.get("key_decisions", [])
            topics = parsed.get("topics_discussed", [])
        except json.JSONDecodeError:
            summary = response_text
            action_items = []
            key_decisions = []
            topics = []

        # Store in DB
        db = request.app.state.db if hasattr(request.app.state, 'db') else request.app.extra.get('db')
        if not db:
            from server import db as server_db
            db = server_db

        await db.meeting_summaries.insert_one({
            "meeting_id": req.meeting_id,
            "meeting_title": req.meeting_title,
            "summary": summary,
            "action_items": action_items,
            "key_decisions": key_decisions,
            "topics_discussed": topics,
            "transcript_length": len(req.transcript),
            "created_at": datetime.now(timezone.utc).isoformat()
        })

        return SummaryResponse(
            summary=summary,
            action_items=action_items,
            key_decisions=key_decisions,
            topics_discussed=topics,
            meeting_id=req.meeting_id,
            generated_at=datetime.now(timezone.utc).isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Summary generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


@router.get("/summaries/{meeting_id}")
async def get_meeting_summaries(meeting_id: str, request: Request):
    """Get all summaries for a meeting"""
    try:
        from server import db
        summaries = await db.meeting_summaries.find(
            {"meeting_id": meeting_id}, {"_id": 0}
        ).sort("created_at", -1).to_list(10)
        return {"summaries": summaries}
    except Exception as e:
        logger.error(f"Error fetching summaries: {e}")
        return {"summaries": []}


# --- Polls ---

@router.post("/polls")
async def create_poll(req: PollCreateRequest, request: Request):
    """Create a new poll for a meeting"""
    try:
        from server import db
        poll = {
            "meeting_id": req.meeting_id,
            "question": req.question,
            "options": [{"text": opt, "votes": 0, "voters": []} for opt in req.options],
            "allow_multiple": req.allow_multiple,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "total_votes": 0
        }
        result = await db.meeting_polls.insert_one(poll)
        poll_id = str(result.inserted_id)
        poll.pop("_id", None)
        poll["poll_id"] = poll_id
        return poll
    except Exception as e:
        logger.error(f"Error creating poll: {e}")
        raise HTTPException(status_code=500, detail="Failed to create poll")


@router.get("/polls/{meeting_id}")
async def get_polls(meeting_id: str, request: Request):
    """Get all polls for a meeting"""
    try:
        from server import db
        polls = await db.meeting_polls.find(
            {"meeting_id": meeting_id}
        ).sort("created_at", -1).to_list(50)
        for p in polls:
            p["poll_id"] = str(p.pop("_id"))
        return {"polls": polls}
    except Exception as e:
        logger.error(f"Error fetching polls: {e}")
        return {"polls": []}


@router.post("/polls/{poll_id}/vote")
async def vote_on_poll(poll_id: str, req: PollVoteRequest, request: Request):
    """Vote on a poll option"""
    try:
        from server import db
        from bson import ObjectId
        
        poll = await db.meeting_polls.find_one({"_id": ObjectId(poll_id)})
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        if not poll.get("is_active"):
            raise HTTPException(status_code=400, detail="Poll is closed")
        if req.option_index < 0 or req.option_index >= len(poll["options"]):
            raise HTTPException(status_code=400, detail="Invalid option")
        
        await db.meeting_polls.update_one(
            {"_id": ObjectId(poll_id)},
            {
                "$inc": {
                    f"options.{req.option_index}.votes": 1,
                    "total_votes": 1
                }
            }
        )
        
        updated = await db.meeting_polls.find_one({"_id": ObjectId(poll_id)})
        updated["poll_id"] = str(updated.pop("_id"))
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error voting: {e}")
        raise HTTPException(status_code=500, detail="Failed to vote")


@router.post("/polls/{poll_id}/close")
async def close_poll(poll_id: str, request: Request):
    """Close a poll"""
    try:
        from server import db
        from bson import ObjectId
        await db.meeting_polls.update_one(
            {"_id": ObjectId(poll_id)},
            {"$set": {"is_active": False}}
        )
        return {"status": "closed"}
    except Exception as e:
        logger.error(f"Error closing poll: {e}")
        raise HTTPException(status_code=500, detail="Failed to close poll")



# --- Whiteboard Snapshot Persistence ---

class WhiteboardSnapshot(BaseModel):
    meeting_id: str
    snapshot_data: str  # base64 canvas data URL
    name: Optional[str] = "Whiteboard"

@router.post("/whiteboard/save")
async def save_whiteboard_snapshot(req: WhiteboardSnapshot, request: Request):
    """Save a whiteboard canvas snapshot to the database"""
    try:
        from server import db
        snapshot = {
            "meeting_id": req.meeting_id,
            "name": req.name,
            "snapshot_data": req.snapshot_data,
            "saved_at": datetime.now(timezone.utc).isoformat()
        }
        # Upsert — one snapshot per meeting
        await db.whiteboard_snapshots.update_one(
            {"meeting_id": req.meeting_id},
            {"$set": snapshot},
            upsert=True
        )
        return {"status": "saved", "meeting_id": req.meeting_id}
    except Exception as e:
        logger.error(f"Whiteboard save error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save whiteboard")


@router.get("/whiteboard/{meeting_id}")
async def load_whiteboard_snapshot(meeting_id: str, request: Request):
    """Load a saved whiteboard canvas snapshot"""
    try:
        from server import db
        snapshot = await db.whiteboard_snapshots.find_one(
            {"meeting_id": meeting_id}, {"_id": 0}
        )
        if not snapshot:
            return {"snapshot": None}
        return {"snapshot": snapshot}
    except Exception as e:
        logger.error(f"Whiteboard load error: {e}")
        return {"snapshot": None}
