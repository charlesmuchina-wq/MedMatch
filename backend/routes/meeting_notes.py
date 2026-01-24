"""
Meeting Notes Routes
AI-powered meeting transcription with automatic summarization
Features: Real-time transcription, AI summaries, key points extraction, action items
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
import os
import tempfile
import json

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user

# Import from emergent integrations
try:
    from emergentintegrations.llm.openai import OpenAISpeechToText
    from emergentintegrations.llm.chat import LlmChat, UserMessage
except ImportError:
    OpenAISpeechToText = None
    LlmChat = None
    UserMessage = None

router = APIRouter(prefix="/meeting-notes", tags=["Meeting Notes"])

logger = logging.getLogger(__name__)

# ============== Models ==============

class MeetingCreate(BaseModel):
    title: str
    meeting_type: str = "interview"  # interview, general, follow_up
    company: Optional[str] = None
    position: Optional[str] = None
    participants: List[str] = []
    notes: str = ""

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    notes: Optional[str] = None
    transcript: Optional[str] = None
    status: Optional[str] = None

class GenerateSummaryRequest(BaseModel):
    transcript: str
    meeting_type: str = "interview"
    additional_context: str = ""

# ============== AI Summarization ==============

async def generate_meeting_summary(
    transcript: str,
    meeting_type: str = "interview",
    company: str = "",
    position: str = ""
) -> Dict[str, Any]:
    """Generate AI summary from meeting transcript"""
    if not EMERGENT_LLM_KEY or LlmChat is None:
        return {
            "summary": "AI summarization unavailable. Please review transcript manually.",
            "key_points": [],
            "action_items": [],
            "sentiment": "neutral"
        }
    
    try:
        context = f"Company: {company}\nPosition: {position}\n" if company else ""
        
        system_message = "You are an expert meeting analyst. Extract actionable insights from meeting transcripts. Always respond with valid JSON only."
        
        prompt = f"""Analyze this {meeting_type} meeting transcript and provide a structured summary.

{context}
TRANSCRIPT:
{transcript}

Provide your response in the following JSON format:
{{
    "summary": "A concise 2-3 paragraph summary of the meeting",
    "key_points": ["List of 5-7 key points discussed"],
    "action_items": ["List of specific action items with owners if mentioned"],
    "questions_asked": ["Important questions that were asked"],
    "follow_up_topics": ["Topics that need follow-up"],
    "sentiment": "overall sentiment (positive/neutral/negative)",
    "confidence_indicators": ["Signs of confidence or areas of concern noted"],
    "next_steps": "Recommended next steps based on the meeting"
}}

Return ONLY valid JSON, no markdown or explanation."""

        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message=system_message
        ).with_model("openai", "gpt-4o-mini")

        response = await chat.send_message(prompt)
        
        # Parse JSON response
        try:
            # Clean response if needed
            response_text = response.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            # Return structured response from text
            return {
                "summary": response,
                "key_points": [],
                "action_items": [],
                "sentiment": "neutral"
            }
            
    except Exception as e:
        logger.error(f"Meeting summary generation error: {e}")
        return {
            "summary": f"Error generating summary: {str(e)}",
            "key_points": [],
            "action_items": [],
            "sentiment": "neutral"
        }


async def transcribe_meeting_audio(audio_data: bytes, format: str = "webm") -> Optional[str]:
    """Transcribe meeting audio using Whisper"""
    if not EMERGENT_LLM_KEY or OpenAISpeechToText is None:
        return None
    
    try:
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        try:
            stt = OpenAISpeechToText(api_key=EMERGENT_LLM_KEY)
            result = await stt.transcribe(
                file_path=temp_path,
                model="whisper-1",
                response_format="verbose_json"
            )
            
            if isinstance(result, dict):
                return result.get("text", "")
            return str(result) if result else ""
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Meeting transcription error: {e}")
        return None

# ============== Routes ==============

@router.get("/status")
async def get_service_status(request: Request):
    """Get meeting notes service status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "available": bool(EMERGENT_LLM_KEY),
        "features": {
            "transcription": OpenAISpeechToText is not None,
            "summarization": LlmChat is not None,
            "real_time": True,
            "action_items": True,
            "key_points": True
        },
        "supported_formats": ["webm", "wav", "mp3", "m4a", "ogg"],
        "max_duration_minutes": 120
    }


@router.post("/create")
async def create_meeting(meeting: MeetingCreate, request: Request):
    """Create a new meeting for notes"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    meeting_doc = {
        "id": f"meeting_{uuid.uuid4().hex[:12]}",
        "user_id": user["user_id"],
        "title": meeting.title,
        "meeting_type": meeting.meeting_type,
        "company": meeting.company,
        "position": meeting.position,
        "participants": meeting.participants,
        "notes": meeting.notes,
        "transcript": "",
        "summary": None,
        "key_points": [],
        "action_items": [],
        "status": "draft",  # draft, recording, processing, completed
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.meeting_notes.insert_one(meeting_doc)
    meeting_doc.pop("_id", None)
    
    return {"message": "Meeting created", "meeting": meeting_doc}


@router.get("/list")
async def list_meetings(
    request: Request,
    meeting_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20
):
    """List user's meetings"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    query = {"user_id": user["user_id"]}
    if meeting_type:
        query["meeting_type"] = meeting_type
    if status:
        query["status"] = status
    
    meetings = await db.meeting_notes.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).to_list(limit)
    
    return {
        "meetings": meetings,
        "total": len(meetings)
    }


@router.get("/{meeting_id}")
async def get_meeting(meeting_id: str, request: Request):
    """Get a specific meeting"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    meeting = await db.meeting_notes.find_one(
        {"id": meeting_id, "user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return meeting


@router.put("/{meeting_id}")
async def update_meeting(meeting_id: str, update: MeetingUpdate, request: Request):
    """Update a meeting"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if update.title:
        update_data["title"] = update.title
    if update.notes is not None:
        update_data["notes"] = update.notes
    if update.transcript is not None:
        update_data["transcript"] = update.transcript
    if update.status:
        update_data["status"] = update.status
    
    result = await db.meeting_notes.update_one(
        {"id": meeting_id, "user_id": user["user_id"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return {"message": "Meeting updated"}


@router.delete("/{meeting_id}")
async def delete_meeting(meeting_id: str, request: Request):
    """Delete a meeting"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.meeting_notes.delete_one(
        {"id": meeting_id, "user_id": user["user_id"]}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return {"message": "Meeting deleted"}


@router.post("/{meeting_id}/transcribe")
async def transcribe_meeting(
    meeting_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and transcribe meeting audio"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Verify meeting exists
    meeting = await db.meeting_notes.find_one(
        {"id": meeting_id, "user_id": user["user_id"]}
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Get file extension
    filename = file.filename or "audio.webm"
    ext = filename.split(".")[-1].lower()
    if ext not in ["webm", "wav", "mp3", "m4a", "ogg"]:
        raise HTTPException(status_code=400, detail="Unsupported audio format")
    
    # Read audio data
    audio_data = await file.read()
    
    # Update status
    await db.meeting_notes.update_one(
        {"id": meeting_id},
        {"$set": {"status": "processing"}}
    )
    
    # Transcribe
    transcript = await transcribe_meeting_audio(audio_data, ext)
    
    if transcript:
        word_count = len(transcript.split())
        await db.meeting_notes.update_one(
            {"id": meeting_id},
            {"$set": {
                "transcript": transcript,
                "word_count": word_count,
                "status": "transcribed",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "success": True,
            "transcript": transcript,
            "word_count": word_count
        }
    
    await db.meeting_notes.update_one(
        {"id": meeting_id},
        {"$set": {"status": "error"}}
    )
    
    raise HTTPException(status_code=500, detail="Transcription failed")


@router.post("/{meeting_id}/append-transcript")
async def append_transcript(meeting_id: str, request: Request):
    """Append text to meeting transcript (for real-time transcription)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    body = await request.json()
    text = body.get("text", "")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text required")
    
    # Append to transcript
    result = await db.meeting_notes.update_one(
        {"id": meeting_id, "user_id": user["user_id"]},
        {
            "$set": {
                "status": "recording",
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            "$push": {"transcript_chunks": {
                "text": text,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }}
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return {"message": "Transcript appended"}


@router.post("/{meeting_id}/finalize-transcript")
async def finalize_transcript(meeting_id: str, request: Request):
    """Finalize transcript from chunks"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    meeting = await db.meeting_notes.find_one(
        {"id": meeting_id, "user_id": user["user_id"]}
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Combine chunks into final transcript
    chunks = meeting.get("transcript_chunks", [])
    if chunks:
        full_transcript = " ".join([c.get("text", "") for c in chunks])
        word_count = len(full_transcript.split())
        
        await db.meeting_notes.update_one(
            {"id": meeting_id},
            {
                "$set": {
                    "transcript": full_transcript,
                    "word_count": word_count,
                    "status": "transcribed",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                "$unset": {"transcript_chunks": ""}
            }
        )
        
        return {
            "success": True,
            "transcript": full_transcript,
            "word_count": word_count
        }
    
    return {"success": False, "message": "No transcript chunks found"}


@router.post("/{meeting_id}/generate-summary")
async def generate_summary(meeting_id: str, request: Request):
    """Generate AI summary for a meeting"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    meeting = await db.meeting_notes.find_one(
        {"id": meeting_id, "user_id": user["user_id"]}
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    transcript = meeting.get("transcript", "")
    if not transcript:
        raise HTTPException(status_code=400, detail="No transcript available")
    
    # Generate summary
    summary_data = await generate_meeting_summary(
        transcript=transcript,
        meeting_type=meeting.get("meeting_type", "interview"),
        company=meeting.get("company", ""),
        position=meeting.get("position", "")
    )
    
    # Update meeting with summary
    await db.meeting_notes.update_one(
        {"id": meeting_id},
        {"$set": {
            "summary": summary_data.get("summary", ""),
            "key_points": summary_data.get("key_points", []),
            "action_items": summary_data.get("action_items", []),
            "questions_asked": summary_data.get("questions_asked", []),
            "follow_up_topics": summary_data.get("follow_up_topics", []),
            "sentiment": summary_data.get("sentiment", "neutral"),
            "next_steps": summary_data.get("next_steps", ""),
            "status": "completed",
            "summary_generated_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "success": True,
        "summary": summary_data
    }


@router.post("/summarize-text")
async def summarize_text(summary_request: GenerateSummaryRequest, request: Request):
    """Generate summary from provided transcript text (without saving)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not summary_request.transcript:
        raise HTTPException(status_code=400, detail="Transcript required")
    
    summary_data = await generate_meeting_summary(
        transcript=summary_request.transcript,
        meeting_type=summary_request.meeting_type
    )
    
    return {
        "success": True,
        "summary": summary_data
    }


@router.get("/{meeting_id}/export")
async def export_meeting(meeting_id: str, request: Request, format: str = "markdown"):
    """Export meeting notes in various formats"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    meeting = await db.meeting_notes.find_one(
        {"id": meeting_id, "user_id": user["user_id"]},
        {"_id": 0}
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if format == "markdown":
        content = f"""# {meeting.get('title', 'Meeting Notes')}

**Date:** {meeting.get('created_at', '')}
**Type:** {meeting.get('meeting_type', '').title()}
"""
        if meeting.get('company'):
            content += f"**Company:** {meeting['company']}\n"
        if meeting.get('position'):
            content += f"**Position:** {meeting['position']}\n"
        
        if meeting.get('summary'):
            content += f"\n## Summary\n{meeting['summary']}\n"
        
        if meeting.get('key_points'):
            content += "\n## Key Points\n"
            for point in meeting['key_points']:
                content += f"- {point}\n"
        
        if meeting.get('action_items'):
            content += "\n## Action Items\n"
            for item in meeting['action_items']:
                content += f"- [ ] {item}\n"
        
        if meeting.get('questions_asked'):
            content += "\n## Questions Asked\n"
            for q in meeting['questions_asked']:
                content += f"- {q}\n"
        
        if meeting.get('next_steps'):
            content += f"\n## Next Steps\n{meeting['next_steps']}\n"
        
        if meeting.get('transcript'):
            content += f"\n## Full Transcript\n{meeting['transcript']}\n"
        
        return {
            "format": "markdown",
            "content": content,
            "filename": f"{meeting.get('title', 'meeting').replace(' ', '_')}.md"
        }
    
    elif format == "json":
        return {
            "format": "json",
            "content": meeting,
            "filename": f"{meeting.get('title', 'meeting').replace(' ', '_')}.json"
        }
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use 'markdown' or 'json'")


@router.get("/stats/overview")
async def get_meeting_stats(request: Request):
    """Get meeting notes statistics"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Count meetings by type
    pipeline = [
        {"$match": {"user_id": user["user_id"]}},
        {"$group": {
            "_id": "$meeting_type",
            "count": {"$sum": 1}
        }}
    ]
    
    type_counts = {}
    async for doc in db.meeting_notes.aggregate(pipeline):
        type_counts[doc["_id"]] = doc["count"]
    
    # Total meetings
    total = await db.meeting_notes.count_documents({"user_id": user["user_id"]})
    
    # Completed meetings (with summaries)
    completed = await db.meeting_notes.count_documents({
        "user_id": user["user_id"],
        "status": "completed"
    })
    
    # Total word count
    word_pipeline = [
        {"$match": {"user_id": user["user_id"]}},
        {"$group": {
            "_id": None,
            "total_words": {"$sum": "$word_count"}
        }}
    ]
    
    total_words = 0
    async for doc in db.meeting_notes.aggregate(word_pipeline):
        total_words = doc.get("total_words", 0)
    
    return {
        "total_meetings": total,
        "completed_meetings": completed,
        "total_words_transcribed": total_words,
        "meetings_by_type": type_counts
    }
